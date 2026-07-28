"""Bounded, explicit local structured-spec intake for the bundled engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_SPEC_BYTES = 2 * 1024 * 1024


class IntakeError(ValueError):
    """A user-safe local source acquisition error."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Object-pairs hook for json.loads that fails closed on duplicate keys."""
    seen: set[str] = set()
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate JSON key: {key!r}")
        seen.add(key)
        result[key] = value
    return result


def _load_yaml_strict(text: str) -> Any:
    """Parse YAML with safe_load while rejecting duplicate mapping keys."""
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise IntakeError("YAML support requires PyYAML from the bundled skill requirements") from exc

    class _NoDuplicateKeyLoader(yaml.SafeLoader):
        pass

    def _check_duplicate_key(loader: yaml.SafeLoader, node: yaml.nodes.MappingNode) -> dict[str, Any]:
        loader.flatten_mapping(node)
        seen: set[str] = set()
        result: dict[str, Any] = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node)
            if not isinstance(key, str):
                raise yaml.YAMLError(f"mapping key must be a string, got {type(key).__name__}")
            if key in seen:
                raise yaml.YAMLError(f"duplicate YAML key: {key!r}")
            seen.add(key)
            result[key] = loader.construct_object(value_node)
        return result

    _NoDuplicateKeyLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        _check_duplicate_key,
    )
    return yaml.load(text, Loader=_NoDuplicateKeyLoader)  # noqa: S506 — custom SafeLoader subclass


def load_local_document(file_name: str) -> tuple[Path, dict[str, Any]]:
    """Read one explicit JSON/YAML file without following a remote descriptor."""
    path = Path(file_name)
    if not path.is_file():
        raise IntakeError("input must be an existing local file")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise IntakeError("unable to read input file") from exc
    if size > MAX_SPEC_BYTES:
        raise IntakeError(f"input exceeds {MAX_SPEC_BYTES} byte limit")

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise IntakeError("input must be UTF-8 text") from exc

    suffix = path.suffix.lower()
    try:
        if suffix == ".json":
            document = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
        elif suffix in {".yaml", ".yml"}:
            document = _load_yaml_strict(text)
        else:
            raise IntakeError("input must have a .json, .yaml, or .yml extension")
    except IntakeError:
        raise
    except Exception as exc:
        kind = "JSON" if suffix == ".json" else "YAML"
        raise IntakeError(f"invalid {kind} document: {exc}") from exc

    if not isinstance(document, dict):
        raise IntakeError("specification root must be an object")
    return path, document
