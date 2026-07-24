# Task brief: 9 — dev-default branch governance

**Status:** in-progress
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/9
**Branch:** `ci/9-dev-default-branch`
**Owner:** Hermes Agent

## Goal

Use protected `dev` for integration while retaining protected `main` solely for release promotion.

## Scope

### Included

- CI push coverage for `dev` and `main`.
- A deterministic branch-governance validator executed by CI.
- Root and CLI contributor workflow documentation.

### Excluded

- CLI implementation or generated-project behavior.
- Publishing a release.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `test -f .agents/scripts/validate_branch_governance.py` | failed: validator was absent |
| Green | `python3 .agents/scripts/validate_branch_governance.py` | pending |
| Regression | docs harness and CLI verification baseline | pending |

## Verification

- [ ] Docs/harness validation
- [ ] CLI lint/typecheck/tests/build
- [ ] `git diff --check`
- [x] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- Protection rules require existing `docs-and-harness` and `cli-package` checks on both protected branches.
