# Task brief: 48 — embed a TypeMCP project generator in api-to-typemcp

**Status:** design-review
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/48
**Branch:** `feat/48-embed-typemcp-generator`
**Owner:** sjungwon03

## Goal

Ship the executable API-to-TypeMCP generator as part of the published `api-to-typemcp` skill, so agents can build standalone MCP servers that use `@theorvane/type-mcp` without any `type-mcp-api-cli` release.

## Source references

- Product: `docs/product/mvp-scope.md`
- Architecture/API: `docs/architecture/overview.md`, `docs/api/manifest-contract.md`
- Approved design: `docs/superpowers/specs/2026-07-28-embedded-typemcp-generator-design.md`

## Scope

### Included

- Bundled executable engine, templates, and skill workflow.
- OpenAPI 3.x / Swagger 2.0 input, bounded Swagger UI discovery, and supplied Markdown/HTML extraction.
- Versioned secret-free manifests, approvals, policy gates, TypeMCP stdio output, and contained verification.
- Migration away from external `type-mcp-api-cli` release resolution.

### Excluded

- A separate `type-mcp-api-cli` repository or npm publication.
- Copied TypeMCP source in generated projects.
- Bare-origin crawling, persistent credentials, OAuth/OIDC, and automatic public publication.
- Streamable HTTP in the first stdio-generator increment.

## Safety and contract notes

- Source input: all documents/specifications are untrusted and bounded to user-supplied sources.
- Secrets: artifacts may contain environment-variable mapping names only; never values.
- Side effects: document-derived generation requires digest approval; live calls and GitHub publication require separate final confirmation.
- Compatibility: generated project consumes reviewed npm `@theorvane/type-mcp`; the skill itself ships the generator.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | Pending implementation plan | Must fail because the bundled engine and template do not yet exist. |
| Green | Pending implementation plan | Must pass for a structured OpenAPI fixture and a generated TypeMCP project. |
| Regression | Pending implementation plan | Root harness, generated-project verification, and documentation validation must pass. |

## Verification

- [ ] Lint
- [ ] Typecheck
- [ ] Unit/integration tests
- [ ] Generator or generated-project E2E test
- [ ] Build/package validation
- [ ] `git diff --check`
- [ ] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- Design review is required before writing an issue-scoped implementation plan or production code.
