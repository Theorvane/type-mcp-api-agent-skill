#!/usr/bin/env python3
"""Dependency-minimal local OpenAPI/Swagger inspection and manifest entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# This script is intentionally executable by absolute path from an installed skill.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from intake import IntakeError, load_local_document
from structured_specs import StructuredSpecError, build_manifest


def _emit(value: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    else:
        print(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="api_to_typemcp", add_help=True)
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "manifest"):
        command = subcommands.add_parser(name)
        command.add_argument("--file", required=True, help="explicit local .json/.yaml/.yml specification")
        command.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    try:
        path, document = load_local_document(args.file)
        manifest = build_manifest(document, path.name)
        if args.command == "inspect":
            _emit({"source": manifest["source"], "baseUrl": manifest["baseUrl"], "operationCount": len(manifest["operations"])}, args.json)
        else:
            _emit(manifest, args.json)
        return 0
    except (IntakeError, StructuredSpecError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
