# Planning

Implementation plans are canonical, issue-scoped documents. Store them as `YYYY-MM-DD-issue-<number>-<topic>.md`.

Every plan must link its issue, list exact files and commands, define acceptance/error/exclusion cases, describe a focused TDD cycle for each behavior, and identify documentation changes.

## Embedded-engine planning rule

Plans target the published `skills/api-to-typemcp/` **bundled skill engine** and must preserve its single shipping boundary:

- Engine modules, parsers, manifest state, policy, templates, and generated-project verification live beneath `skills/api-to-typemcp/`.
- Generated projects use published `@theorvane/type-mcp`; plans must prohibit local/file/git TypeMCP dependencies and source copying.
- Plans must keep manifest-first review, bounded source intake, secret hygiene, protected-write authorization before request construction, contained verification, and final publication confirmation.
- New engine behavior requires a linked issue/plan, a focused observed failing test, and release-artifact coverage when files are added.

No implementation starts without a plan derived from `docs/superpowers/specs/2026-07-28-embedded-typemcp-generator-design.md`.
