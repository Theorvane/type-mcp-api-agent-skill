# Task brief: 29 — Identify public skills-hub.ai requests to the registry WAF

**Status:** in-progress
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/29
**Branch:** `fix/29-identify-skills-hub-requests`
**Owner:** Hermes Agent

## Goal

Release `api-to-typemcp` v0.1.3 after making the skills-hub.ai publisher WAF-compatible without weakening its authentication boundaries.

## Scope

### Included

- Explicit stable User-Agent on every skills-hub.ai HTTP request.
- Unauthenticated public category validation and ApiKey-protected skill operations.
- Shared SemVer bump from `0.1.2` to `0.1.3`.

### Excluded

- Retrying, modifying, or claiming a successful skills-hub.ai v0.1.2 publication.
- skills-hub.cc automation.

## Safety and contract notes

- Secrets: authorization remains an Actions secret and is never embedded in headers recorded by source or logs.
- Side effects: only `main` promotion runs registry writes.
- Compatibility: direct urllib reproduction showed default User-Agent received WAF `403/1010`; a fixed product User-Agent received HTTP 200 from the same public endpoint.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agents/scripts/test_skill_release.py` | Failed as expected: public request did not send the required User-Agent. |
| Green | `python3 .agents/scripts/test_skill_release.py` | Passed: 12 tests. |
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
