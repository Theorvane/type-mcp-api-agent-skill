# Task brief: 71 — offer generated MCP installation for supported agents

**Status:** in-progress
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/71
**Branch:** `feat/71-agent-mcp-installation`

## Goal

Keep project-only generation as default and add opt-in, secret-free agent MCP installation after generated-project verification.

## Safety

- `.env` values are never read or persisted.
- Detection is read-only; native config changes require a fresh plan and final confirmation.
- Symlinked project build/config paths are rejected; unsupported clients receive portable export.

## Test-first evidence

| Stage | Command | Result |
| --- | --- | --- |
| Red | `python3 -m unittest skills/api-to-typemcp/tests/test_agent_installation_docs.py -v` | Missing reference initially. |
| Green | `python3 -m unittest skills/api-to-typemcp/tests/test_agent_installation_docs.py skills/api-to-typemcp/tests/test_agent_clients.py -v` | Passed: 6 tests. |
| Security regression | same command | Passed: symlinked `dist/` and config-parent paths are rejected. |

## Review notes

- Task 1 specification and quality review approved before temporary checkout loss; changes were reconstructed from the recorded contract.
- Task 2 reviewer discovered intermediate symlink traversal; regression tests now cover it.
