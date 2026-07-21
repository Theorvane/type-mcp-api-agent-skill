# Task brief: 1 — separate API agent skill from CLI generator

**Status:** review
**Issue:** https://github.com/Theorvane/type-mcp-api-agent/issues/1
**Branch:** `docs/1-separate-skill-cli`
**Owner:** Hermes Agent

## Goal

Make the repository a reusable Hermes skill that invokes an independently installable API-to-TypeMCP CLI, while retaining the reviewed manifest and safety workflow.

## Source references

- Product: `docs/product/vision.md`, `docs/product/mvp-scope.md`
- Architecture/API: `docs/architecture/overview.md`, `docs/api/manifest-contract.md`
- Approved baseline: `docs/superpowers/specs/2026-07-21-type-mcp-api-agent-design.md`

## Scope

### Included

- Separate skill and planned CLI responsibilities in all canonical docs.
- Add an in-repository `skills/api-to-typemcp/SKILL.md` that calls the CLI rather than generating code itself.
- Add CLI compatibility, fixture, and verification rules to the agent harness.

### Excluded

- Creating the `type-mcp-api-cli` repository.
- Implementing/intalling a CLI package.
- Generating an MCP project or publishing any generated project.

## Safety and contract notes

- Source input: CLI receives untrusted API specs/docs and emits a review manifest.
- Secrets: only environment-variable references cross the skill/CLI boundary.
- Side effects: manifest approval precedes generation; final confirmation precedes GitHub publication.
- Compatibility: skill pins/validates a compatible released CLI version and verifies CLI provenance before invocation.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agent/scripts/validate_docs.py` after adding required split-repo assertions | Expected failure before documents/skill are updated |
| Green | `python3 .agent/scripts/validate_docs.py` | Pass: 18 Markdown files and 14 required harness files validated. |
| Regression | `python3 -m py_compile .agent/scripts/validate_docs.py && git diff --check` | Pass. |

## Verification

- [ ] Documentation validator
- [ ] Python syntax check
- [ ] Diff check
- [ ] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded
