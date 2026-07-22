# Task brief: 3 — unify CLI workspace with skill repository

**Status:** in-progress
**Issue:** https://github.com/Theorvane/type-mcp-api-agent/issues/3
**Branch:** `feat/3-unify-cli-workspace`

## Goal

Move the deterministic `type-mcp-api-cli` package into the root skill repository without moving parser/generator behavior into root skill code. Keep the package independently installable and verified, then rename the canonical repository to `type-mcp-api-agent-skill` and archive the migrated legacy CLI repository.

## Boundaries

- Root owns the Hermes skill, publication safety policy, and root harness.
- `packages/type-mcp-api-cli/` owns CLI source, schema, package lock, package tests, and package documentation.
- No npm release is enabled by this migration; trusted executable policy remains fail-closed.

## TDD evidence

| Behavior | Command | Evidence |
| --- | --- | --- |
| unified CI package job | `python3 .agents/scripts/test_workspace.py` | RED: `cli-package` job absent; GREEN after root workflow added package verification. |
| docs validator ignores dependency docs | `python3 .agents/scripts/validate_docs.py` | RED: installed nested `node_modules` Markdown links failed; GREEN after excluding `node_modules`/`.git` paths. |
| root harness | `python3 .agents/scripts/test_validate_docs.py && python3 .agents/scripts/test_workspace.py && python3 .agents/scripts/validate_docs.py` | GREEN. |
| relocated CLI package | `npm ci && npm run verify && npm audit --omit=dev --audit-level=high` from `packages/type-mcp-api-cli` | GREEN: 10 tests, package-bin E2E, 0 production vulnerabilities. |

## External operations after PR merge

1. Rename `Theorvane/type-mcp-api-agent` to `Theorvane/type-mcp-api-agent-skill`.
2. Read back repository metadata/default branch.
3. Archive `Theorvane/type-mcp-api-cli` after updating its repository description with the migration destination.
4. Read back archived legacy repository metadata.
