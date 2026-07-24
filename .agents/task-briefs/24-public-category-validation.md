# Task brief: 24 — Publish skills-hub.ai after public category validation

**Status:** in-progress
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/24
**Branch:** `fix/24-public-category-validation`
**Owner:** Hermes Agent

## Goal

Release `api-to-typemcp` v0.1.2 to skills-hub.ai by validating the public category endpoint without an API-key header, while retaining API-key authentication for all protected registry operations.

## Source references

- Product: `AGENTS.md`
- Architecture/API: live `https://api.skills-hub.ai/api/v1/openapi.json`
- Release guide: `docs/guides/skill-release.md`

## Scope

### Included

- Unauthenticated `GET /categories/` validation.
- Authenticated skills-hub.ai skill lookup and mutation requests.
- Shared SemVer bump from `0.1.1` to `0.1.2`.

### Excluded

- Any retry or mutation of the immutable v0.1.1 skills-hub.ai publication.
- skills-hub.cc publication or automation.

## Safety and contract notes

- Source input: static frontmatter category validated against the public registry endpoint.
- Secrets: API key exists only as `SKILLS_HUB_AI_API_KEY` Actions secret and must not occur in artifacts or logs.
- Side effects: registry mutations run only after reviewed `dev` → `main` promotion.
- Compatibility: retain the repository-tested standard-library publisher rather than the unavailable upstream CLI dependency.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agents/scripts/test_skill_release.py` | Failed as expected: `request()` rejected the missing `public` request boundary. |
| Green | `python3 .agents/scripts/test_skill_release.py` | Passed: 12 tests, including no API-key header for public category validation. |
| Regression | root harness + CLI verification + actionlint | Pending. |

## Verification

- [ ] Lint
- [ ] Typecheck
- [ ] Unit/integration tests
- [ ] Build/package validation, when applicable
- [ ] `git diff --check`
- [ ] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- v0.1.1 skills-hub.ai failure occurred before any registry mutation: category validation incorrectly coupled a public endpoint to authenticated request behavior.
