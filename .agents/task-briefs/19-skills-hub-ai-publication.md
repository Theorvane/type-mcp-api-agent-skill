# Task brief: 19 — Publish released skill to skills-hub.ai

**Status:** in-progress
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/19
**Branch:** `feat/19-skills-hub-ai-publication`
**Owner:** Hermes Agent

## Goal

A reviewed `dev` → `main` promotion releases the same SemVer-tagged `api-to-typemcp` skill to GitHub, ClawHub, and skills-hub.ai, while excluding skills-hub.cc.

## Source references

- Product: `README.md`
- Release policy: `AGENTS.md`, `.agents/checklists/release-readiness.md`
- skills-hub.ai category API: `GET https://api.skills-hub.ai/api/v1/categories`
- Issue: #19

## Scope

### Included

- Add valid skills-hub.ai category metadata to the published skill.
- Require the repository secret `SKILLS_HUB_AI_API_KEY` before release side effects.
- Publish using skills-hub.ai’s documented `POST /api/v1/skills` and `POST /api/v1/skills/{slug}/publish` endpoints.
- Preserve least-privilege job permissions and avoid persistent checkout credentials.

### Excluded

- `skills-hub.cc` registration or credentials.
- Republishing existing v0.1.0 artifacts.

## Safety and contract notes

- Source input: static repository `SKILL.md` frontmatter; version and category are validated before use.
- Secrets: only GitHub Actions repository secrets; no values are committed, logged, or uploaded.
- Side effects: GitHub release, ClawHub, and skills-hub.ai publication only on `main` push after reviewed promotion.
- Compatibility: `@skills-hub-ai/cli@0.4.1` cannot be installed because its declared `@skills-hub-ai/installer@0.1.0` dependency is unavailable from npm. Issue #19 records the reviewed decision to use a repository-tested direct client against the live OpenAPI 3.1 contract instead.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agents/scripts/test_skill_release.py` | Fails because skills-hub.ai job, secret gate, and category metadata are absent. |
| Green | `python3 .agents/scripts/test_skill_release.py` | Passed: 11 contract and mocked state-machine tests, including category API validation, existing-unpublished recovery, capped retry delay, and 409 version reconciliation. |
| Regression | root harness + `npm run verify` + `actionlint` | Passed locally; `npm audit --omit=dev --audit-level=high` found 0 vulnerabilities. |

## Verification

- [ ] Lint
- [ ] Typecheck
- [ ] Unit/integration tests
- [ ] Build/package validation
- [ ] `git diff --check`
- [ ] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- skills-hub.cc is explicitly out of scope by user direction.
