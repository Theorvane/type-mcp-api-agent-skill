# Task brief: 48 — embed a TypeMCP project generator in api-to-typemcp

**Status:** Tasks 1–6 complete; Tasks 7–8 pending
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/48
**Branch:** `feat/48-task6-bounded-intake`
**Owner:** sjungwon03

## Goal

Ship the executable API-to-TypeMCP generator as part of the published `api-to-typemcp` skill, so agents can build standalone MCP servers that use `@theorvane/type-mcp` without any separate generator package or npm release.

## Source references

- Product: `docs/product/mvp-scope.md`
- Architecture/API: `docs/architecture/overview.md`, `docs/api/manifest-contract.md`
- Approved design: `docs/superpowers/specs/2026-07-28-embedded-typemcp-generator-design.md`
- Implementation plan: `docs/planning/implementation/2026-07-28-issue-48-embedded-typemcp-generator.md`

## Scope

### Included

- Bundled executable engine, templates, and skill workflow.
- OpenAPI 3.x / Swagger 2.0 input, bounded Swagger UI discovery, and supplied Markdown/HTML extraction.
- Versioned secret-free manifests, approvals, policy gates, TypeMCP stdio output, and contained verification.
- Migration away from external generator-release resolution.

### Excluded

- A separate generator repository or npm publication.
- Copied TypeMCP source in generated projects.
- Bare-origin crawling, persistent credentials, OAuth/OIDC, and automatic public publication.
- Streamable HTTP in the first stdio-generator increment.

## Safety and contract notes

- Source input: all documents/specifications are untrusted and bounded to user-supplied sources.
- Secrets: artifacts may contain environment-variable mapping names only; never values.
- Side effects: document-derived generation requires digest approval; live calls and GitHub publication require separate final confirmation.
- Runtime: generated projects consume published npm `@theorvane/type-mcp`; the skill ships the generator.

## Task 1 — workspace/release boundary migration

The separate generator workspace, package metadata, package lockfile, package tests, schemas, package documentation, compatibility guide, and CI job were removed. The shipping boundary is now `skills/api-to-typemcp/` with tracked structural `scripts/` and `templates/` directories.

Task 1 deliberately does **not** add `scripts/api_to_typemcp.py`, engine behavior, or TypeScript template files. The workspace test asserts that distinction: directories must exist, while the Task 2 entry point and Task 4 template tree must not yet exist. This prevents a structural migration from falsely claiming implementation that belongs to later tasks.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agents/scripts/test_workspace.py` | Observed exit 1: three failures because `bundled-engine:` was absent, `packages/type-mcp-api-cli` existed, and `skills/api-to-typemcp/scripts` did not exist. |
| Red | `python3 .agents/scripts/test_validate_docs.py` | Observed exit 1: 13 failures because active documents retained the obsolete generator boundary and did not contain the bundled-engine/published-runtime contract. |
| Green | `python3 .agents/scripts/test_workspace.py` | Observed exit 0: 3 tests passed. |
| Green | `python3 .agents/scripts/test_validate_docs.py` | Observed exit 0: 5 tests passed. |
| Green | `python3 .agents/scripts/validate_docs.py` | Observed exit 0: validated 32 Markdown files and 15 required harness files. |
| Regression | `python3 .agents/scripts/test_skill_release.py` | Observed exit 0: 12 tests passed. |
| Regression | `python3 -m py_compile .agents/scripts/*.py && git diff --check` | Observed exit 0. |
| Red (Task 2) | `python3 -m unittest discover -s skills/api-to-typemcp/tests -v` | Observed exit 1: four CLI/manifest failures because `scripts/api_to_typemcp.py` did not exist, plus one policy import error because `scripts/policy.py` did not exist. |
| Green (Task 2) | `python3 -m unittest discover -s skills/api-to-typemcp/tests -v` | Observed exit 0: 6 tests passed for local JSON/YAML intake, deterministic secret-free manifests, malformed/unsupported rejection, and fail-closed policy gates. |
| Regression (Task 2) | `python3 .agents/scripts/test_validate_docs.py` | Observed exit 0: 7 tests passed. |
| Regression (Task 2) | `python3 .agents/scripts/validate_docs.py` | Observed exit 0: validated 32 Markdown files and 15 required harness files. |
| Regression (Task 2) | `python3 .agents/scripts/test_workspace.py` | Observed exit 0: 3 tests passed after updating the structural assertion to require the Task 2 engine entry point/modules while deferring Task 4 templates. |
| Red (Task 2 security hardening) | `python3 -m unittest discover -s skills/api-to-typemcp/tests -v` | Observed exit 1: unsafe endpoint path containing `?token=source-secret` was accepted into the manifest. |
| Green (Task 2 security hardening) | `python3 -m unittest discover -s skills/api-to-typemcp/tests -v` | Observed exit 0: 7 tests passed after rejecting unsafe paths/schema values and excluding untrusted response descriptions from manifest artifacts. |
| Red (Task 2 YAML hardening) | `python3 -m unittest skills/api-to-typemcp/tests/test_engine_cli.py -v` | Observed exit 1: mixed YAML keys caused an uncaught `TypeError` and alias fan-out exceeded the two-second test timeout. |
| Green (Task 2 YAML hardening) | `python3 -m unittest discover -s skills/api-to-typemcp/tests -v` | Observed exit 0: 9 tests passed after bounded, identity-aware structure validation rejects non-string keys and alias fan-out without a traceback. |
| Red (Task 2 manifest contract hardening) | `python3 -m unittest skills/api-to-typemcp/tests/test_manifest.py -v` | Observed exit 1: a query-bearing filename leaked into the descriptor, string `required` values were coerced, and response summaries were omitted. |
| Green (Task 2 manifest contract hardening) | `python3 -m unittest discover -s skills/api-to-typemcp/tests -v` | Observed exit 0: 12 tests passed after descriptor sanitization, strict boolean validation, and generated status-based response summaries. |

## Verification

- [x] Focused documentation-contract tests
- [x] Workspace-boundary test
- [x] Documentation validator
- [x] Skill release-contract test
- [x] Python harness compilation
- [x] `git diff --check`
- [x] Documentation updated
- [x] Engine unit/integration tests (Task 2)
- [x] Generated-project E2E (Task 5)
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded
