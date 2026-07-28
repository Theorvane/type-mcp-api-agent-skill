# Task brief: 65 — harden generated-project verification and dependencies

**Status:** review
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/65
**Branch:** `fix/65-harden-generated-project-verification`
**Owner:** Hermes Agent

## Goal

Generated TypeMCP projects use reviewed dependency versions and are verified from a lockfile in a credential-scrubbed, proxy-free process environment.

## Source references

- Product: `skills/api-to-typemcp/SKILL.md`
- Architecture/API: `AGENTS.md`
- Audit: https://clawhub.ai/sjungwon03/skills/api-to-typemcp/security-audit

## Scope

### Included

- Replace audit-flagged SDK and Vitest ranges with current reviewed versions.
- Generate a `package-lock.json` from a controlled template and require it before verification.
- Use `npm ci --ignore-scripts` with explicit isolated npm paths and proxy-disabled configuration.
- Prevent MCP smoke subprocesses from inheriting the complete process environment.
- Declare OpenClaw runtime requirements and accurately document containment limits.

### Excluded

- Runtime policy changes, TypeMCP behavior changes, API mutation, and ClawHub publication.

## Safety and contract notes

- Source input: supplied API documents remain untrusted and are never crawled.
- Secrets: verification receives only an allowlisted environment; smoke child processes receive `PATH` and the local `TYPE_MCP_BASE_URL` only.
- Side effects: verification writes only a temporary workspace; npm registry access is needed for `npm ci`.
- Compatibility: `@theorvane/type-mcp@0.2.0` declares `@modelcontextprotocol/sdk@1.26.0`; the generated root pin is upgraded to the compatible current `^1.30.0`.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 -m unittest skills/api-to-typemcp/tests/test_verify_generated_security.py -v` | Failed as expected: no lockfile enforcement, smoke cloned `process.env`, and stale SDK/Vitest ranges. |
| Green | `python3 -m unittest skills/api-to-typemcp/tests/test_verify_generated_security.py -v` | Passed: 3 focused security regressions. |
| Regression | `python3 -m unittest discover -s skills/api-to-typemcp/tests -p 'test_*.py' -v` | Passed: 97 tests. |

## Verification

- [x] Unit/integration tests
- [x] Generator or generated-project E2E test
- [x] Build/package validation
- [x] `git diff --check`
- [x] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- Pending independent reviews after local verification.
