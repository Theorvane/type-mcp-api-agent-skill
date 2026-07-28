"""Bounded Swagger UI configuration discovery.

This module examines only user-supplied Swagger UI HTML in memory. It never
fetches a page, follows links, or enumerates an origin.
"""
from __future__ import annotations

import re
from typing import Any

MAX_SWAGGER_UI_BYTES = 2 * 1024 * 1024


class SwaggerUIError(ValueError):
    """User-safe error for invalid or oversized Swagger UI input."""


# Only inspect an explicit SwaggerUIBundle({...}) call. This intentionally does
# not recognise arbitrary `url` assignments elsewhere in a document.
_BUNDLE_RE = re.compile(r"SwaggerUIBundle\s*\(\s*\{(?P<config>.{0,65536}?)\}\s*\)", re.DOTALL)
_URL_RE = re.compile(r"(?:^|[,\n])\s*url\s*:\s*(['\"])(?P<url>[^'\"\s<>]{1,2048})\1")


def extract_spec_reference(html: str) -> dict[str, Any] | None:
    """Return one explicit spec reference from supplied Swagger UI HTML.

    No I/O is performed; callers must separately obtain and explicitly approve
    a structured specification before it reaches normal structured intake.
    """
    if not isinstance(html, str):
        raise SwaggerUIError("Swagger UI input must be text")
    if len(html.encode("utf-8")) > MAX_SWAGGER_UI_BYTES:
        raise SwaggerUIError(f"Swagger UI input exceeds {MAX_SWAGGER_UI_BYTES} byte limit")

    match = _BUNDLE_RE.search(html)
    if not match:
        return None
    url = _URL_RE.search(match.group("config"))
    if not url:
        return None
    return {"source_kind": "swagger-ui-config", "spec_url": url.group("url")}
