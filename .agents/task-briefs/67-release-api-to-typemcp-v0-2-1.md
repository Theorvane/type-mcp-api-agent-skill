# Task brief: 67 — publish api-to-typemcp v0.2.1

**Status:** review
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/67
**Branch:** `chore/67-release-api-to-typemcp-v0-2-1`
**Owner:** Hermes Agent

## Goal

Release the reviewed security-hardened `api-to-typemcp` skill as public version 0.2.1 through the protected `dev` → `main` promotion and the main-push release workflow.

## Source references

- Release contract: `docs/guides/skill-release.md`
- Release checklist: `.agents/checklists/release-readiness.md`
- Security changes: #65
- ClawHub public-confirmation gate: #61

## Scope

### Included

- Bump the frontmatter release version from 0.2.0 to 0.2.1.
- Update release-contract expectations and public README release link.
- Verify the bundled artifact and a generated project before promotion.
- Promote and independently verify the public GitHub, ClawHub, and skills-hub.ai releases.

### Excluded

- New engine behavior or dependency changes beyond the reviewed `dev` content.
- Manual registry mutation or immutable-version retries.

## Safety and contract notes

- Source input: the reviewed `origin/dev` commit `a2225f5c8203c6d468d3419bf99c9a2c7a7d3ade`.
- Secrets: GitHub Actions secrets only; never read, print, or commit credentials.
- Side effects: registry publication only follows a reviewed `dev` → `main` merge and succeeds only for published registry state.
- Compatibility: generated projects retain the public `@theorvane/type-mcp@0.2.0` runtime contract.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agents/scripts/test_skill_release.py` | Expected to fail after changing the release-contract expectation to 0.2.1 while SKILL.md is 0.2.0. |
| Green | `python3 .agents/scripts/test_skill_release.py` | Passed: 15 tests. |
| Regression | full repository validation and generated-project verification | Passed: 98 engine tests; generated-project `npm ci`, build, Vitest, and audit (0 vulnerabilities). |

## Verification

- [x] Unit/integration tests
- [x] Generator or generated-project E2E test
- [x] Build/package validation
- [x] `git diff --check`
- [x] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- Pending exact-head independent review after PR creation.
