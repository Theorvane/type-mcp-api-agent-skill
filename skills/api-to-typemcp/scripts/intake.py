"""Bounded, explicit local structured-spec intake for the bundled engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_SPEC_BYTES = 2 * 1024 * 1024


class IntakeError(ValueError):
    """A user-safe local source acquisition error."""


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
            document = json.loads(text)
        elif suffix in {".yaml", ".yml"}:
            # PyYAML 6 is available in the supported runtime. safe_load never
            # constructs Python objects and is intentionally the only YAML API used.
            import yaml  # type: ignore[import-not-found]

            document = yaml.safe_load(text)
        else:
            raise IntakeError("input must have a .json, .yaml, or .yml extension")
    except IntakeError:
        raise
    except Exception as exc:
        kind = "JSON" if suffix == ".json" else "YAML"
        raise IntakeError(f"invalid {kind} document") from exc

    if not isinstance(document, dict):
        raise IntakeError("specification root must be an object")
    return path, document
