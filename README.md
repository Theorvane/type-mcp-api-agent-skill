# type-mcp-api-agent

A Hermes skill repository for turning supplied API sources into standalone TypeMCP MCP repositories **by invoking the separate `type-mcp-api-cli` CLI**.

## Status

This repository currently contains the approved skill contract, product specification, and engineering harness. Neither the skill runtime nor the companion CLI implementation is published from this repository yet.

## Choose a usage mode

| Need | Use |
| --- | --- |
| Deterministic intake, manifest creation, or project generation in a terminal/CI pipeline | `type-mcp-api-cli` (separate CLI repository/package; planned) |
| Guided API-source discovery, manifest approval, safety checks, verification, and confirmed GitHub publication | this repository's `api-to-typemcp` Hermes skill |

The skill is an orchestrator. It validates and invokes a compatible released CLI; it does not reimplement parsing, normalization, or source rendering.

## Intended skill workflow

1. Accept an OpenAPI/Swagger JSON or YAML URL/file, Swagger UI URL, or Markdown/HTML API documentation URL.
2. Resolve a verified CLI executable and create a secret-free review manifest.
3. Require explicit approval for Markdown/HTML-derived operations.
4. Invoke the CLI to generate a standalone TypeScript MCP project whose dependencies include `type-mcp` from npm.
5. Verify the generated project and only then, after final owner/name/visibility confirmation, create and push its own GitHub repository.

## Canonical documentation

- Product scope: `docs/product/`
- Architecture and cross-repository compatibility: `docs/architecture/`
- Manifest and generated API contracts: `docs/api/`
- Safety, auth, and publication guides: `docs/guides/`
- Executable task plans: `docs/planning/`
- Approved design history: `docs/superpowers/specs/`
- Hermes operating rules and quality gates: `AGENTS.md`, `.agent/`
- Skill instructions: `skills/api-to-typemcp/SKILL.md`

Read `AGENTS.md` before changing this repository. Do not represent planned CLI or generation behavior as implemented behavior.
