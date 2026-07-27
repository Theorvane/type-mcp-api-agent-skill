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
    "docs/guides/cli-compatibility.md",
    "docs/superpowers/specs/2026-07-21-type-mcp-api-agent-design.md",
    "docs/planning/README.md",
    "skills/api-to-typemcp/SKILL.md",
    ".agents/templates/task-brief.md",
    ".agents/templates/review-report.md",
    ".agents/checklists/pre-commit.md",
    ".agents/checklists/release-readiness.md",
)


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

    contract_files = {
        "docs/api/manifest-contract.md": (
            "CLI-issued approval receipt",
            "RFC 8785 JSON Canonicalization Scheme (JCS)",
            "closed (`additionalProperties: false`)",
            "separate, CLI-issued approval receipt",
            "TYPE_MCP_ALLOW_PROTECTED_OPERATIONS",
            "A copied/edited manifest cannot forge a receipt",
        ),
        "docs/guides/security-and-publication.md": (
            "before upstream request construction or dispatch",
            "A source parser, operation name, or documentation prose cannot classify a mutating method as `read`",
            "canonical `manifestDigest`",
            "MAC-validated receipt",
            "TYPE_MCP_ALLOW_PROTECTED_OPERATIONS",
            "unset, empty, wildcard, duplicate, method-only, malformed, or unknown entries grant nothing",
            "Contained generation and verification",
            "npm ci --ignore-scripts",
            "actual checked-out/ref-to-publish branch",
        ),
        "docs/guides/cli-compatibility.md": (
            "no CLI release is supported yet",
            "it must not run a candidate CLI, install a package, generate a project, execute generated code, or publish output",
            "The skill itself can still be installed and used for orchestration guidance",
            "Update the compatibility table only after a reviewed CLI npm release exists",
            "Trusted resolution flow",
            "npm registry dist integrity",
            "PATH` lookup alone is prohibited",
        ),
        "docs/architecture/overview.md": (
            "CLI-issued, unexpired, single-use MAC receipt",
            "TYPE_MCP_ALLOW_PROTECTED_OPERATIONS",
            "owner/org, name, visibility, and source-branch confirmation",
        ),
        "README.md": (
            "workspace repository",
            "packages/type-mcp-api-cli",
            "not published from this repository yet",
            "https://clawhub.ai/sjungwon03/api-to-typemcp",
            "https://skills-hub.ai/skills/api-to-typemcp",
            "https://github.com/Theorvane/type-mcp-api-agent-skill/releases/tag/v0.1.4",
        ),
    }
    for relative_path, required_phrases in contract_files.items():
        content = (ROOT / relative_path).read_text(encoding="utf-8")
        for required_phrase in required_phrases:
            if required_phrase not in content:
                print(f"{relative_path} missing required safety contract phrase: {required_phrase}")
                return 1

    publication_contracts = (
        "owner/org, repository name, visibility, and source branch",
        "actual checked-out/ref-to-publish branch",
        "stop unless it exactly equals the recorded source branch",
        "before staging, committing, or pushing",
    )
    for relative_path in (
        "docs/guides/security-and-publication.md",
        "skills/api-to-typemcp/SKILL.md",
    ):
        content = (ROOT / relative_path).read_text(encoding="utf-8").lower()
        for required_phrase in publication_contracts:
            if required_phrase not in content:
                print(f"{relative_path} missing required publication contract: {required_phrase}")
                return 1

    skill = (ROOT / "skills/api-to-typemcp/SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n") or "\n---\n" not in skill[4:]:
        print("Skill must start with YAML frontmatter and a non-empty body")
        return 1
    for required_phrase in (
        "name: api-to-typemcp",
        "type-mcp-api-cli",
        "manifest approval",
        "The skill is installed and its orchestration guidance is available",
        "Project generation is intentionally blocked by the compatibility policy; no CLI was installed or executed",
        "https://github.com/Theorvane/type-mcp-api-agent-skill/blob/dev/docs/guides/cli-compatibility.md",
        "actual checked-out/ref-to-publish branch",
    ):
        if required_phrase not in skill:
            print(f"Skill missing required contract phrase: {required_phrase}")
            return 1

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for required_phrase in (
        "Manifest before generation",
        "CLI boundary, not generator implementation",
        "Trusted CLI resolution",
        "Contained execution",
        "Protected branch flow after bootstrap",
    ):
        if required_phrase not in agents:
            print(f"AGENTS.md missing required operating rule: {required_phrase}")
            return 1

    print(f"validated {len(markdown_files)} Markdown files and {len(REQUIRED_FILES)} required harness files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
