#!/usr/bin/env python3
"""Validate the embedded-engine documentation contract without dependencies."""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_SOURCE_DOCS = (
    "AGENTS.md",
    "README.md",
    "docs/product/vision.md",
    "docs/product/mvp-scope.md",
    "docs/architecture/overview.md",
    "docs/api/manifest-contract.md",
    "docs/guides/security-and-publication.md",
    "docs/planning/README.md",
    "skills/api-to-typemcp/SKILL.md",
)
REQUIRED_FILES = (
    *ACTIVE_SOURCE_DOCS,
    "docs/superpowers/specs/2026-07-28-embedded-typemcp-generator-design.md",
    "skills/api-to-typemcp/SKILL.md",
    ".agents/templates/task-brief.md",
    ".agents/templates/review-report.md",
    ".agents/checklists/pre-commit.md",
    ".agents/checklists/release-readiness.md",
)
EMBEDDED_ENGINE_PHRASE = "bundled skill engine"
TYPE_MCP_RUNTIME = "@theorvane/type-mcp"


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        print("Missing required files:", *missing, sep="\n- ")
        return 1

    markdown_files = sorted(
        path
        for path in ROOT.rglob("*.md")
        if "node_modules" not in path.parts and ".git" not in path.parts
    )
    empty = [str(path.relative_to(ROOT)) for path in markdown_files if not path.read_text(encoding="utf-8").strip()]
    if empty:
        print("Empty Markdown files:", *empty, sep="\n- ")
        return 1

    missing_links: list[str] = []
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)(?:#[^)]+)?\)")
    for path in markdown_files:
        for target in link_pattern.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("https://", "http://")):
                continue
            if not (path.parent / target).resolve().is_file():
                missing_links.append(f"{path.relative_to(ROOT)} -> {target}")
    if missing_links:
        print("Missing local Markdown links:", *missing_links, sep="\n- ")
        return 1

    prohibited = ("type-mcp-api-cli", "cli compatibility")
    for relative_path in ACTIVE_SOURCE_DOCS:
        content = (ROOT / relative_path).read_text(encoding="utf-8").lower()
        for phrase in prohibited:
            if phrase in content:
                print(f"{relative_path} retains obsolete CLI boundary phrase: {phrase}")
                return 1

    stale_claims = ("`npm ci --ignore-scripts`", "approval challenge", "challenge ID", "RFC 8785/JCS canonical")
    for relative_path in ACTIVE_SOURCE_DOCS:
        content = (ROOT / relative_path).read_text(encoding="utf-8")
        for phrase in stale_claims:
            if phrase in content:
                print(f"{relative_path} retains stale implemented-engine claim: {phrase}")
                return 1

    contract_files = {
        "AGENTS.md": (EMBEDDED_ENGINE_PHRASE, TYPE_MCP_RUNTIME, "Manifest before generation", "before request construction"),
        "README.md": (EMBEDDED_ENGINE_PHRASE, TYPE_MCP_RUNTIME, "Manifest first", "Contained verification"),
        "docs/architecture/overview.md": (EMBEDDED_ENGINE_PHRASE, TYPE_MCP_RUNTIME, "single-use HMAC-validated receipt", "npm install --ignore-scripts"),
        "docs/api/manifest-contract.md": (EMBEDDED_ENGINE_PHRASE, TYPE_MCP_RUNTIME, "engine-specific deterministic encoding", "receipt is not an audit record"),
        "docs/guides/security-and-publication.md": (EMBEDDED_ENGINE_PHRASE, TYPE_MCP_RUNTIME, "before upstream request construction or dispatch", "npm install --ignore-scripts", "actual checked-out/ref-to-publish branch"),
        "docs/planning/README.md": (EMBEDDED_ENGINE_PHRASE, TYPE_MCP_RUNTIME, "protected-write authorization before request construction"),
        "skills/api-to-typemcp/SKILL.md": (EMBEDDED_ENGINE_PHRASE, TYPE_MCP_RUNTIME, "before URL, query, headers, body, authentication, or dispatch"),
        ".agents/checklists/release-readiness.md": (
            "No separate generator CLI is required",
            "Engine fixtures cover malformed source, manifest, receipt, and policy rejection",
            "contained temporary directory",
            "published `@theorvane/type-mcp` dependency",
        ),
    }
    for relative_path, required_phrases in contract_files.items():
        content = (ROOT / relative_path).read_text(encoding="utf-8")
        for required_phrase in required_phrases:
            if required_phrase not in content:
                print(f"{relative_path} missing required embedded-engine contract phrase: {required_phrase}")
                return 1

    publication_contracts = (
        "owner/org, repository name, visibility, and source branch",
        "actual checked-out/ref-to-publish branch",
        "stop unless it exactly equals the recorded source branch",
        "before staging, committing, or pushing",
    )
    security = (ROOT / "docs/guides/security-and-publication.md").read_text(encoding="utf-8").lower()
    for required_phrase in publication_contracts:
        if required_phrase not in security:
            print(f"docs/guides/security-and-publication.md missing required publication contract: {required_phrase}")
            return 1

    print(f"validated {len(markdown_files)} Markdown files and {len(REQUIRED_FILES)} required harness files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
