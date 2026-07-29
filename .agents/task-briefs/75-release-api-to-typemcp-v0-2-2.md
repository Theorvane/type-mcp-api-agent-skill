# Task brief: 75 — reconcile and publish api-to-typemcp v0.2.2

**Status:** in-progress
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/75
**Branch:** `chore/75-release-api-to-typemcp-v0-2-2`
**Owner:** sjungwon03

## Goal

Publish the reviewed Hermes and Claude Code MCP-registration capability as public `api-to-typemcp` version `0.2.2` through the protected `dev` → `main` release path.

## Source references

- Release contract: `docs/guides/skill-release.md`
- Release checklist: `.agents/checklists/release-readiness.md`
- Reviewed feature PR: https://github.com/Theorvane/type-mcp-api-agent-skill/pull/74

## Scope

### Included

- Preserve the divergent `main` release automation history by merging it into the current `dev` lineage with a no-fast-forward reconciliation commit.
- Bump the skill frontmatter version from `0.2.1` to `0.2.2`.
- Update the release-contract expected output and verify the bundled skill, generated-project E2E, and public release artifacts.

### Excluded

- New MCP engine behavior beyond reviewed `dev` content.
- Manual GitHub release, tag, ClawHub, or skills-hub.ai mutation.

## Safety and contract notes

- Source input: release promotion starts only from the current reviewed `dev` branch and preserves both release histories.
- Secrets: registry credentials remain GitHub Actions secrets only; no credential is read, printed, or committed.
- Side effects: GitHub Release and registry publication occur only after a reviewed `dev` → `main` merge.
- Compatibility: this is a backward-compatible feature release; generated projects continue to use the reviewed public TypeMCP runtime contract.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agents/scripts/test_skill_release.py` | Failed as expected after the contract expected `0.2.2` while `SKILL.md` remained `0.2.1`. |
| Green | `python3 .agents/scripts/test_skill_release.py` | Passed: 15 tests after the frontmatter and release-publisher fixture version were updated to `0.2.2`. |
| Regression | repository verification baseline plus generated-project E2E | Passed: 140 engine tests, 8 documentation tests, 3 workspace tests, 15 release-contract tests, documentation validation, Python compile, and `git diff --check`. |

## Verification

- [ ] Unit/integration tests
- [ ] Generator or generated-project E2E test
- [ ] Build/package validation
- [ ] `git diff --check`
- [ ] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- Pending exact-head independent review after PR creation.
