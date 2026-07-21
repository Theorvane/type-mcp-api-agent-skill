#!/usr/bin/env python3
"""Validate the docs-only bootstrap contract without external dependencies."""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
    "docs/product/vision.md",
    "docs/product/mvp-scope.md",
    "docs/architecture/overview.md",
    "docs/api/manifest-contract.md",
    "docs/guides/security-and-publication.md",
    "docs/superpowers/specs/2026-07-21-type-mcp-api-agent-design.md",
    "docs/planning/README.md",
    "skills/api-to-typemcp/SKILL.md",
    ".agent/templates/task-brief.md",
    ".agent/templates/review-report.md",
    ".agent/checklists/pre-commit.md",
    ".agent/checklists/release-readiness.md",
)


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        print("Missing required files:", *missing, sep="\n- ")
        return 1

    markdown_files = sorted(ROOT.rglob("*.md"))
    empty = [str(path.relative_to(ROOT)) for path in markdown_files if not path.read_text(encoding="utf-8").strip()]
    if empty:
        print("Empty Markdown files:", *empty, sep="\n- ")
        return 1

    missing_links: list[str] = []
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)(?:#[^)]+)?\)")
    for path in markdown_files:
        for target in link_pattern.findall(path.read_text(encoding="utf-8")):
            if not (path.parent / target).resolve().is_file():
                missing_links.append(f"{path.relative_to(ROOT)} -> {target}")
    if missing_links:
        print("Missing local Markdown links:", *missing_links, sep="\n- ")
        return 1

    skill = (ROOT / "skills/api-to-typemcp/SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n") or "\n---\n" not in skill[4:]:
        print("Skill must start with YAML frontmatter and a non-empty body")
        return 1
    for required_phrase in ("name: api-to-typemcp", "type-mcp-api-cli", "manifest approval"):
        if required_phrase not in skill:
            print(f"Skill missing required contract phrase: {required_phrase}")
            return 1

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for required_phrase in (
        "Manifest before generation",
        "CLI boundary, not generator implementation",
        "No direct main changes",
    ):
        if required_phrase not in agents:
            print(f"AGENTS.md missing required operating rule: {required_phrase}")
            return 1

    print(f"validated {len(markdown_files)} Markdown files and {len(REQUIRED_FILES)} required harness files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
