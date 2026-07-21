# Planning

Implementation plans are canonical, issue-scoped documents. Store them as `YYYY-MM-DD-issue-<number>-<topic>.md`.

Every plan must link its issue, list exact files/commands, define acceptance/error/exclusion cases, describe a focused TDD cycle for each behavior, and identify documentation changes.

## Cross-repository planning rule

Plans must identify their target repository and may not smuggle CLI behavior into the skill repository or skill orchestration behavior into the CLI repository.

- CLI engine, parsers, templates, manifest schema production, and source rendering are planned in `type-mcp-api-cli`.
- Hermes UX, CLI compatibility, approvals, independent verification, and confirmed publication are planned in `type-mcp-api-agent`.
- Any shared protocol change needs linked issues/plans in both repositories and a version/fixture compatibility test.

No implementation starts without a plan derived from `docs/superpowers/specs/2026-07-21-type-mcp-api-agent-design.md`.
