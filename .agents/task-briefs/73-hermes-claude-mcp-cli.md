# Task brief: 73 — Register generated MCPs with Hermes and Claude Code CLIs

**Status:** in-progress
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/73
**Branch:** `feat/73-hermes-claude-mcp-cli`
**Owner:** sjungwon03

## Goal

A user who explicitly selects Hermes or Claude Code after generated-project verification can register the generated stdio MCP server through that client’s official CLI and receive CLI-based discovery verification.

## Source references

- Product: `docs/product/vision.md`
- Architecture/API: `docs/architecture/overview.md`
- Existing installation contract: `skills/api-to-typemcp/references/agent-mcp-installation.md`
- Hermes CLI: `hermes mcp add --help`, inspected 2026-07-29
- Claude Code CLI: https://docs.anthropic.com/en/docs/claude-code/mcp, retrieved 2026-07-29

## Scope

### Included

- CLI-managed plan targets for Hermes and Claude Code.
- Official CLI `add`, verification, and compensating `remove` on a failed verification.
- Receipt-bound, secret-free installation plan and tests.
- Accurate support-matrix and user workflow documentation.

### Excluded

- Direct edits to Hermes or Claude Code settings.
- Runtime upstream API invocation.
- Implicit install, configuration creation, or secret value propagation.

## Safety and contract notes

- Source input: generated project must keep its existing contained entrypoint checks.
- Secrets: commands never receive `.env` data or environment values; only plan-visible environment variable names remain.
- Side effects: CLI registration happens only after the existing plan receipt is issued and consumed.
- Compatibility: use `hermes mcp add/test/remove`; use `claude mcp add --transport stdio <name> -- node <entry>`, `claude mcp list`, and `claude mcp remove`.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 -m unittest skills/api-to-typemcp/tests/test_cli_agent_adapters.py -v` | Failed: Hermes and Claude Code were rejected as unsupported native plan targets. |
| Green | `python3 -m unittest skills/api-to-typemcp/tests/test_cli_agent_adapters.py -v` | Passed: 4 tests, including receipt gating, official Hermes/Claude CLI arguments, unhealthy Claude discovery rollback, and failed Hermes verification rollback. |
| Regression | `python3 -m unittest discover -s skills/api-to-typemcp/tests -p 'test_*.py' -q` | Passed: 137 tests. |

## Verification

- [ ] Unit/integration tests
- [ ] Generator or generated-project E2E test, when applicable
- [ ] `git diff --check`
- [ ] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- Pending.
