# type-mcp-api-cli — Contributor Instructions

## Purpose

`type-mcp-api-cli` is the deterministic, directly usable CLI package at `packages/type-mcp-api-cli/` within the `type-mcp-api-agent-skill` workspace. It owns safe source intake, normalized manifest construction, manifest approval challenge/receipt support, and TypeMCP project generation. It does **not** create GitHub repositories, call live APIs during ordinary verification, or persist credentials.

## Source of truth

1. User-approved product decisions
2. `docs/product/` and `docs/architecture/`
3. `docs/api/` for public CLI and manifest contracts
4. `docs/planning/` for issue-scoped delivery plans
5. This file
6. README

When root orchestration and package documents disagree, stop and reconcile the documents before implementing behavior.

## Repository boundaries

- `src/`: strict TypeScript CLI and contract implementation.
- `schemas/`: versioned closed JSON Schemas published with the package.
- `test/`: Vitest behavior and CLI-contract tests.
- `docs/`: canonical product, architecture, API, security, and planning documentation.
- `.agent/`: task briefs/checklists only; never runtime imports.

## Non-negotiable rules

1. **TDD.** Add a focused failing Vitest test, observe its expected failure, then make the smallest safe implementation.
2. **Strict boundary.** Accept external sources and CLI JSON as `unknown`; validate before use. No `any`, `@ts-ignore`, unchecked casts, or implicit undefined behavior.
3. **No secrets.** Never put credentials, raw private URLs, raw redirects, private paths, request headers, or secret values in manifests, diagnostics, fixtures, logs, package output, or Git.
4. **No accidental side effects.** `inspect` and `manifest` never generate files or call upstream APIs. `generate` never creates GitHub repositories. Network and live smoke tests require explicit documented policy.
5. **Contracted document approval.** Document-derived generation accepts only a CLI-issued, MAC-validated, single-use receipt matching the current canonical digest/version/protocol.
6. **Policy before request construction.** Protected write authorization and deny policy are evaluated before URL, query, headers, body, or authentication construction.
7. **Keep the core standalone.** Do not import Hermes implementation code. The CLI works without a conversation layer.
8. **Small conventional commits.** One concern per commit.

## Bootstrap implementation

Only `metadata --json`, local structured-spec `inspect --file <path> --json`, the closed `schemas/api-manifest-1.schema.json` artifact, and side-effect-free manifest v1 validation/canonical-digest library APIs are implemented today. Do not claim manifest construction, remote inspection, document parsing, approval, or generation is implemented until an issue, test evidence, and documentation demonstrate it.

## Workflow after bootstrap

1. Inspect open issues/PRs and create or update one focused Issue.
2. Branch from current `origin/dev`: `<type>/<issue-number>-<description>`.
3. For multi-behavior work, create a task brief from `.agent/templates/task-brief.md`.
4. Record RED test evidence, implement minimally, and rerun focused/full checks.
5. Update docs for public behavior and contracts.
6. Run the verification baseline, review the diff, commit, push, and open a PR into `dev` with `Closes #<issue>`.
7. Obtain independent specification and code-quality review before squash merge. Promote reviewed `dev` to release-only `main` in a separate release PR.

## Verification baseline

```bash
npm ci
npm run lint
npm run typecheck
npm test
npm run build
npm run verify:package
git diff --check
git status --short --branch
```

## Definition of done

A change is done only when its intended behavior had an observed failing test before implementation, focused/full tests and typecheck/build pass, docs match actual implementation, and the committed diff is issue-scoped.
