"""Strict OpenAPI 3.x and Swagger 2.0 normalization for local supplied files."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from manifest import MANIFEST_SCHEMA, MANIFEST_VERSION, add_digest
from policy import classify_method


class StructuredSpecError(ValueError):
    """A user-safe unsupported or malformed structured specification error."""


_METHOD_ORDER = ("get", "head", "options", "post", "put", "patch", "delete")
_OPERATION_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")


def _reject_references(value: Any) -> None:
    if isinstance(value, dict):
        if "$ref" in value:
            raise StructuredSpecError("$ref is not supported for local normalization")
        for nested in value.values():
            _reject_references(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_references(nested)


def _safe_base_url(raw: object) -> str:
    if not isinstance(raw, str) or not raw:
        return ""
    try:
        parsed = urlsplit(raw)
        port = parsed.port
    except ValueError as exc:
        raise StructuredSpecError("base URL is malformed") from exc
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise StructuredSpecError("base URL must be an http(s) URL without credentials")
    netloc = parsed.hostname
    if port:
        netloc += f":{port}"
    path = parsed.path.rstrip("/")
    return urlunsplit((parsed.scheme, netloc, path, "", ""))


def _swagger_base_url(document: dict[str, Any]) -> str:
    host = document.get("host")
    if not isinstance(host, str) or not host or any(char in host for char in "@/?#"):
        raise StructuredSpecError("Swagger host must be a hostname")
    schemes = document.get("schemes", ["https"])
    if not isinstance(schemes, list) or not schemes or schemes[0] not in {"http", "https"}:
        raise StructuredSpecError("Swagger schemes must begin with http or https")
    base_path = document.get("basePath", "")
    if not isinstance(base_path, str) or (base_path and not base_path.startswith("/")):
        raise StructuredSpecError("Swagger basePath must be an absolute path")
    return _safe_base_url(f"{schemes[0]}://{host}{base_path}")


def _parameters(values: object, swagger: bool) -> list[dict[str, Any]]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise StructuredSpecError("parameters must be an array")
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for parameter in values:
        if not isinstance(parameter, dict):
            raise StructuredSpecError("parameter must be an object")
        name, location = parameter.get("name"), parameter.get("in")
        if not isinstance(name, str) or not name or not isinstance(location, str) or location not in {"path", "query", "header", "cookie", "body"}:
            raise StructuredSpecError("parameter name or location is invalid")
        if (name, location) in seen:
            raise StructuredSpecError("duplicate parameter")
        seen.add((name, location))
        if location == "body":
            continue
        schema = parameter.get("schema", {}) if not swagger else {"type": parameter.get("type", "string")}
        if not isinstance(schema, dict):
            raise StructuredSpecError("parameter schema must be an object")
        item = {"name": name, "in": location, "required": bool(parameter.get("required", False)), "type": schema.get("type", "string")}
        normalized.append(item)
    return sorted(normalized, key=lambda item: (item["in"], item["name"]))


def _request_body(operation: dict[str, Any], swagger: bool) -> dict[str, Any] | None:
    if swagger:
        bodies = [item for item in operation.get("parameters", []) if isinstance(item, dict) and item.get("in") == "body"]
        if not bodies:
            return None
        if len(bodies) != 1:
            raise StructuredSpecError("operation has multiple body parameters")
        schema = bodies[0].get("schema")
        if not isinstance(schema, dict):
            raise StructuredSpecError("body parameter schema must be an object")
        return {"required": bool(bodies[0].get("required", False)), "contentType": "application/json", "type": schema.get("type", "object")}
    body = operation.get("requestBody")
    if body is None:
        return None
    if not isinstance(body, dict) or not isinstance(body.get("content"), dict) or not body["content"]:
        raise StructuredSpecError("requestBody must have content")
    content_type = sorted(body["content"])[0]
    media = body["content"][content_type]
    if not isinstance(media, dict) or not isinstance(media.get("schema", {}), dict):
        raise StructuredSpecError("requestBody media schema must be an object")
    return {"required": bool(body.get("required", False)), "contentType": content_type, "type": media.get("schema", {}).get("type", "object")}


def _responses(values: object) -> list[dict[str, str]]:
    if not isinstance(values, dict) or not values:
        raise StructuredSpecError("operation responses must be an object")
    result: list[dict[str, str]] = []
    for status, response in values.items():
        if not isinstance(status, str) or not isinstance(response, dict):
            raise StructuredSpecError("response is invalid")
        description = response.get("description", "")
        if not isinstance(description, str):
            raise StructuredSpecError("response description must be a string")
        result.append({"status": status, "description": description})
    return sorted(result, key=lambda response: response["status"])


def build_manifest(document: dict[str, Any], descriptor: str) -> dict[str, Any]:
    """Validate and normalize one OpenAPI 3.x or Swagger 2.0 document."""
    _reject_references(document)
    if isinstance(document.get("openapi"), str) and document["openapi"].startswith("3."):
        kind, swagger = "openapi", False
        servers = document.get("servers", [])
        if not isinstance(servers, list) or not servers or not isinstance(servers[0], dict):
            raise StructuredSpecError("OpenAPI document must declare a server")
        base_url = _safe_base_url(servers[0].get("url"))
    elif document.get("swagger") == "2.0":
        kind, swagger = "swagger", True
        base_url = _swagger_base_url(document)
    else:
        raise StructuredSpecError("only OpenAPI 3.x and Swagger 2.0 are supported")

    paths = document.get("paths")
    if not isinstance(paths, dict) or not paths:
        raise StructuredSpecError("specification paths must be a non-empty object")
    operations: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for path in sorted(paths):
        item = paths[path]
        if not isinstance(path, str) or not path.startswith("/") or not isinstance(item, dict):
            raise StructuredSpecError("path item is invalid")
        common_parameters = item.get("parameters", [])
        for method in _METHOD_ORDER:
            operation = item.get(method)
            if operation is None:
                continue
            if not isinstance(operation, dict):
                raise StructuredSpecError("operation must be an object")
            operation_id = operation.get("operationId")
            if not isinstance(operation_id, str) or not _OPERATION_ID.fullmatch(operation_id) or operation_id in seen_ids:
                raise StructuredSpecError("operationId must be unique and stable")
            seen_ids.add(operation_id)
            operation_parameters = operation.get("parameters", [])
            if not isinstance(common_parameters, list) or not isinstance(operation_parameters, list):
                raise StructuredSpecError("parameters must be an array")
            parameters = _parameters(common_parameters + operation_parameters, swagger)
            item_value: dict[str, Any] = {
                "operationId": operation_id,
                "method": method.upper(),
                "path": path,
                "parameters": parameters,
                "requestBody": _request_body(operation, swagger),
                "responses": _responses(operation.get("responses")),
                "evidence": {"source": "structured-spec"},
                "status": "ready",
                "policy": classify_method(method),
            }
            operations.append(item_value)
    if not operations:
        raise StructuredSpecError("specification contains no supported operations")
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "version": MANIFEST_VERSION,
        "protocol": "http",
        "source": {"kind": kind, "descriptor": descriptor},
        "baseUrl": base_url,
        "operations": operations,
    }
    return add_digest(manifest)
