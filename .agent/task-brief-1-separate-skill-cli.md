# Task brief: 1 — separate API agent skill from CLI generator

**Status:** review
**Issue:** https://github.com/Theorvane/type-mcp-api-agent/issues/1
**Branch:** `docs/1-separate-skill-cli`
**Owner:** Hermes Agent

## Goal

Make the repository a reusable Hermes skill that invokes an independently installable API-to-TypeMCP CLI, while retaining a mechanically enforceable manifest approval and safety workflow.

## Source references

- Product: `docs/product/vision.md`, `docs/product/mvp-scope.md`
- Architecture/API: `docs/architecture/overview.md`, `docs/api/manifest-contract.md`
- Approved baseline: `docs/superpowers/specs/2026-07-21-type-mcp-api-agent-design.md`
- Initial independent bootstrap review: `deleg_bec3e5d8`

## Scope

### Included

- Separate skill and planned CLI responsibilities in all canonical docs.
- Add an in-repository `skills/api-to-typemcp/SKILL.md` that calls the CLI rather than generating code itself.
- Define CLI compatibility, fixture, and verification rules in the agent harness.
- Define digest-bound document approval and normative method-policy defaults.

### Excluded

- Creating the `type-mcp-api-cli` repository.
- Implementing/installing a CLI package.
- Generating an MCP project or publishing any generated project.

## Safety and contract notes

- Source input: CLI receives untrusted API specs/docs and emits a review manifest.
- Secrets: only environment-variable references cross the skill/CLI boundary.
- Approval: document-derived generation needs `approval.state: approved` bound to the current canonical digest, manifest version, and protocol version.
- Policy: `GET`/`HEAD`/`OPTIONS` derive `read`; common mutations derive `protected-write`; unknown methods derive `deny` before upstream dispatch.
- Side effects: manifest approval precedes generation; final confirmation precedes GitHub publication.
- Compatibility: skill pins/validates a compatible released CLI version and verifies CLI provenance before invocation.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agent/scripts/validate_docs.py` after adding required split-repo skill assertion | Failed before `skills/api-to-typemcp/SKILL.md` existed: missing required file. |
| Green | `python3 .agent/scripts/validate_docs.py` | Pass after split-repo docs, skill contract, and approval/policy assertions are present. |
| Regression | `python3 -m py_compile .agent/scripts/validate_docs.py && git diff --check` | Pass. |

## Review remediation

Initial independent bootstrap review identified these important gaps, all addressed in this PR:

1. Document approval is now a canonical-digest/version/protocol-bound approval object that blocks stale or unbound generation.
2. Method policy is now normative: read methods, protected mutations, denied unknown methods, and visible reasoned overrides only.
3. Current bootstrap status and the separate CLI boundary are explicit; the repository does not claim a local generator implementation.
4. The validator asserts the non-negotiable approval/policy/bootstrap phrases instead of only structural Markdown properties.

## Verification

- [x] Documentation validator
- [x] Python syntax check
- [x] Diff check
- [x] Secret-pattern scan
- [x] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded
