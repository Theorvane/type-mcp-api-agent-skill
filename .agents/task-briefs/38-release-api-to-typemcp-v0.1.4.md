# Task brief: 38 — publish api-to-typemcp v0.1.4

**Status:** review
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/38
**Branch:** `release/38-api-to-typemcp-v0.1.4`
**Owner:** Hermes Agent

## Goal

Promote the reviewed pre-release CLI availability guidance as the public `api-to-typemcp` v0.1.4 skill release.

## Source references

- Release guide: `docs/guides/skill-release.md`
- Release checklist: `.agents/checklists/release-readiness.md`
- Skill contract: `skills/api-to-typemcp/SKILL.md`

## Scope

### Included

- Bump the public skill version and README GitHub Release link from `0.1.3` to `0.1.4`.
- Update release-harness expectations and mock registry reconciliation fixtures.
- Promote reviewed `dev` to `main` only after release PR CI and exact-head approval.

### Excluded

- Publishing a `type-mcp-api-cli` npm package.
- Changing the no-supported-CLI compatibility policy.

## Safety and contract notes

- Compatibility: the supported CLI table remains empty; this release only publishes orchestration guidance.
- Secrets: release credentials remain GitHub Actions secrets and are never tracked or logged.
- Side effects: GitHub Release, ClawHub, and skills-hub.ai publication occur only from the automated `main` push workflow.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agents/scripts/test_skill_release.py` | Failed: the release workflow extracted `0.1.3` while the v0.1.4 release expectation was introduced. |
| Green | `python3 .agents/scripts/test_skill_release.py` | Passed: 12 tests. |
| Regression | Root documentation/governance harness and CLI `npm run verify` | Passed: docs 13 tests, workspace 5 tests, branch governance 2 tests, CLI 18 tests. |

## Verification

- [x] Documentation harness and Python compilation
- [x] CLI package lint/typecheck/tests/build/package/install-bin verification
- [x] Production dependency audit
- [x] `git diff --check`
- [ ] Exact-head GitHub CI and independent review
- [ ] Reviewed `dev` → `main` release promotion
- [ ] GitHub Release, ClawHub, and skills-hub.ai provenance verification

## Review notes

- Pending independent review.
