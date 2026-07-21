# Planning

Implementation plans are canonical, issue-scoped documents. Store them as `YYYY-MM-DD-issue-<number>-<topic>.md`.

Every plan must link its issue, list exact files/commands, define acceptance/error/exclusion cases, describe a focused TDD cycle for each behavior, and identify documentation changes.

## Cross-repository planning rule

Plans must identify their target boundary (`root skill/docs` or `packages/type-mcp-api-cli`) and may not smuggle CLI behavior into root skill code or skill orchestration behavior into the CLI package.

- CLI engine, parsers, templates, manifest schema production, and source rendering live in `packages/type-mcp-api-cli`.
- Hermes UX, CLI compatibility, approvals, independent verification, and confirmed publication live at the repository root.
- Any shared protocol change needs a linked issue/plan identifying both root and CLI-package impact, plus a version/fixture compatibility test.

No implementation starts without a plan derived from `docs/superpowers/specs/2026-07-21-type-mcp-api-agent-design.md`.
