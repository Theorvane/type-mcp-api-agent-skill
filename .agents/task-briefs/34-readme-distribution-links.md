# Task brief: 34 — Add public skill distribution links to README

**Status:** review
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/34
**Branch:** `docs/34-readme-distribution-links`
**Owner:** Hermes Agent

## Goal

README visitors can open the released API-to-TypeMCP skill from its public ClawHub, skills-hub.ai, and GitHub Release pages.

## Source references

- Product: `docs/product/mvp-scope.md`
- Architecture/API: `docs/guides/skill-release.md`
- Approved issue: https://github.com/Theorvane/type-mcp-api-agent-skill/issues/34

## Scope

### Included

- A concise README distribution section with the three public release links.
- A documentation-validator regression test requiring those links.

### Excluded

- Changes to the skill, release workflow, registry credentials, or registry metadata.

## Safety and contract notes

- Source input: links are fixed public release/registry URLs verified from the release workflow and public registry pages.
- Secrets: none.
- Side effects: GitHub issue, branch, and PR only; no registry publication.
- Compatibility: documentation-only change.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agents/scripts/test_validate_docs.py` | Failed: README lacked the first required ClawHub URL. |
| Green | `python3 .agents/scripts/test_validate_docs.py` | Passed: 8 tests. |
| Regression | `python3 .agents/scripts/validate_docs.py` | Passed: 37 Markdown files and 15 required harness files validated. |

## Verification

- [ ] Lint (not applicable: no package source change)
- [ ] Typecheck (not applicable: no TypeScript change)
- [x] Unit/integration tests
- [ ] Generator or generated-project E2E test (not applicable)
- [ ] Build/package validation (not applicable)
- [x] `git diff --check`
- [x] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- Pending independent review.
