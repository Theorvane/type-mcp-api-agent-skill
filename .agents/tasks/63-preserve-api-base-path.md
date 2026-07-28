# Task brief: 63 — Preserve API base path when resolving endpoint paths

**Status:** review
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/63
**Branch:** `fix/63-preserve-api-base-path`
**Owner:** sjungwon03

## Goal

Generated API clients preserve a configured API base URL path prefix when resolving endpoint paths that begin with `/`.

## Source references

- Product: `docs/product/`
- Architecture/API: `skills/api-to-typemcp/templates/typescript-stdio/src/api-client.ts.tmpl`
- Approved design/manifest: GitHub issue #63

## Scope

### Included

- Regression coverage for generated API-client URL construction.
- Normalize leading-slash endpoint paths before resolving them relative to the configured base URL.

### Excluded

- Changes to generated operation descriptors, authentication, or request policy.
- Changes to the published TypeMCP runtime package.

## Safety and contract notes

- Source input: operation paths are manifest-derived and remain handled by the generated client.
- Secrets: no credentials or credential references are added or logged.
- Side effects: generated request URLs only; no live requests run in this repository test.
- Compatibility: both leading-slash and relative operation paths must resolve against the configured base URL.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 skills/api-to-typemcp/tests/test_render.py RenderTests.test_generated_api_client_preserves_base_path_for_leading_slash_paths -v` | Observed expected failure: generated client lacked `normalizedPath` and still called `new URL(path, this.baseUrl)`. |
| Green | `python3 skills/api-to-typemcp/tests/test_render.py RenderTests.test_generated_api_client_preserves_base_path_for_leading_slash_paths -v` | Passed: rendered client strips one leading slash and resolves the resulting path against `baseUrl + "/"`. |
| Regression | `python3 .agents/scripts/test_validate_docs.py && python3 .agents/scripts/validate_docs.py`; `python3 .agents/scripts/test_workspace.py && python3 .agents/scripts/test_skill_release.py`; `python3 -m unittest discover -s skills/api-to-typemcp/tests -v` | Passed: 8 documentation tests, 3 workspace tests, 14 release-contract tests, and 95 bundled-engine/generated-project tests. |

## Verification

- [ ] Lint
- [ ] Typecheck
- [ ] Unit/integration tests
- [ ] Generator or generated-project E2E test, when applicable
- [ ] Build/package validation, when applicable
- [ ] `git diff --check`
- [ ] Documentation updated (not required: generated behavior is covered by its template contract and issue)
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- No review findings yet.
