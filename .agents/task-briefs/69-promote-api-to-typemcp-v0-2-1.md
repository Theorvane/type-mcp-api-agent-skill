# Task brief: 69 — promote api-to-typemcp v0.2.1 to main

**Status:** review
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/69
**Branch:** `release/69-api-to-typemcp-v0-2-1`
**Owner:** Hermes Agent

## Goal

Promote the reviewed `api-to-typemcp` v0.2.1 release candidate from `dev` to release-only `main`, preserving current release ancestry and publishing the same immutable version to GitHub, ClawHub, and skills-hub.ai.

## Source references

- Release policy: `docs/guides/skill-release.md`
- Release checklist: `.agents/checklists/release-readiness.md`
- Security hardening: #65
- ClawHub public-confirmation: #61
- Release preparation: #67

## Scope

### Included

- Merge current `origin/dev` into a branch created from `origin/main` with a two-parent merge commit.
- Run release-candidate verification on that exact merge commit.
- Deliver a `main` PR with exact-head approval and merge it with a merge commit.
- Verify resulting v0.2.1 release identity and all public registries.

### Excluded

- New feature/security implementation changes.
- Manual tags, releases, or registry mutations outside the guarded main-push workflow.

## Safety and contract notes

- Source input: `origin/main` `699638c08dba58eb99c1cc54f6c0e193af5237ed` and `origin/dev` `2274a105e701a0a93a90a636b7273f7d21b9cfa8`.
- Secrets: only repository Actions secrets; no credential read, output, or persistence.
- Side effects: GitHub release and registry publication occur only after reviewed main merge.
- Compatibility: generated projects remain bound to published `@theorvane/type-mcp@0.2.0` while the skill artifact is v0.2.1.

## Test-first / merge-candidate evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Candidate | `git show -s --format='%P' HEAD` | Exact release candidate has two parents: old main then reviewed dev. |
| Red | `python3 .agents/scripts/validate_release_promotion.py` | Failed at the obsolete dev-only guard, proving a lineage-preserving release branch could not be promoted. |
| Green | `python3 .agents/scripts/validate_release_promotion.py` | Passed after requiring strict `release/<positive-issue>-<kebab>` naming and main/dev ancestry. |
| Verification | full release and generated-project suite | Passed: release contract 15, docs 8, workspace 3, engine 98; generated project `npm ci`, build, Vitest, and audit (0 vulnerabilities). |
| Publication | guarded main-push workflow | Pending after reviewed merge. |

## Verification

- [x] Unit/integration tests
- [x] Generator or generated-project E2E test
- [x] Build/package validation
- [x] `git diff --check`
- [x] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- Main was not an ancestor of dev. The candidate merge commit is intentional lineage repair and must be merged into main using a merge commit, not squash or rebase.
- The former dev-only release guard rejected this candidate. It now accepts only `dev` or a strict `release/<positive-issue>-<kebab>` name and validates main/dev ancestry; arbitrary PR branches remain blocked.
