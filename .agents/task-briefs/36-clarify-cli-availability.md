# Task brief: 36 — explain pre-release TypeMCP CLI availability

**Status:** in-progress
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/36
**Branch:** `fix/36-clarify-cli-availability`
**Owner:** Hermes Agent

## Goal

An installed `api-to-typemcp` skill clearly explains that its orchestration guidance is available while project generation remains blocked until a reviewed compatible CLI release is recorded in the canonical policy.

## Source references

- Product: `docs/product/mvp-scope.md`
- Architecture: `docs/architecture/overview.md`
- Compatibility policy: `docs/guides/cli-compatibility.md`
- Skill contract: `skills/api-to-typemcp/SKILL.md`

## Scope

### Included

- Clarify the no-supported-CLI user outcome without weakening fail-closed behavior.
- State the canonical policy update required after a reviewed npm release.
- Add regression coverage for the required guidance.

### Excluded

- Publishing `type-mcp-api-cli`.
- Adding parsing, manifest, or generation logic to the root skill.

## Safety and contract notes

- Source input: no source is executed while the compatibility table lists no supported CLI release.
- Secrets: no credentials, specifications, or values are added to artifacts.
- Side effects: no package installation, generation, execution, or publication is enabled.
- Compatibility: `docs/guides/cli-compatibility.md` remains the sole release allowlist.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agents/scripts/test_validate_docs.py` | Failed as intended: the required pre-release skill and release-unblock guidance were absent. |
| Green | `python3 .agents/scripts/test_validate_docs.py` | Passed: 13 tests, including the full pre-release denial contract, safe blocked outcome, and installed-skill canonical policy URL. |
| Regression | `python3 .agents/scripts/test_workspace.py`, `python3 .agents/scripts/validate_docs.py`, `npm --prefix packages/type-mcp-api-cli run verify` | Passed: 5 workspace tests; 38 Markdown files and 15 required harness files validated; CLI verification passed with 18 tests. |

## Verification

- [ ] Lint (not applicable: root is docs/Python harness only)
- [ ] Typecheck (not applicable: root is docs/Python harness only)
- [x] Unit/integration tests
- [x] Generator or generated-project E2E test (not applicable: no executable orchestration behavior changes)
- [x] Build/package validation (CLI package regression verification)
- [x] `git diff --check`
- [x] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- Independent review found that the installed-skill relative policy link would break after publication and that the added regressions did not protect the full pre-release denial contract. Resolved with a canonical GitHub policy URL, a validator that distinguishes external Markdown URLs from local paths, and regressions for the denial contract and safe blocked outcome.
