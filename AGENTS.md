# type-mcp-api-agent — Agent & Contributor Instructions

## Purpose

`type-mcp-api-agent` is a standalone Hermes skill and generator repository. It turns approved API sources into independently deployable TypeScript MCP projects that install and use the published `type-mcp` package from npm. It never copies `type-mcp` source into generated projects.

## Source-of-truth hierarchy

1. Explicit user request and approved manifest
2. `docs/product/` and `docs/architecture/`
3. `docs/api/` and `docs/guides/`
4. `docs/planning/` for executable work order
5. This file for operating rules
6. README and generated examples

When sources conflict, stop and update the lower-priority source before implementation.

## Repository boundaries

- `skills/`: Hermes skill instructions; orchestration only, no hidden business rules.
- `packages/generator/`: deterministic intake, normalization, rendering, and validation code.
- `templates/generated-mcp/`: audited source templates for generated projects.
- `docs/`: canonical product, architecture, API, safety, and planning documents.
- `.agent/`: tracked task briefs, checklists, review templates, and deterministic harness scripts.
- Generated user projects, credentials, downloaded specs, build output, coverage, and `node_modules/` are not committed here.

## Non-negotiable rules

1. **Manifest before generation.** Normalize every input into the manifest contract. Markdown/HTML-derived operations require explicit user approval before source generation.
2. **npm dependency, not source copying.** Generated `package.json` installs a verified `type-mcp` npm version. Verify package exports and run a generated-server smoke test.
3. **All tools, controlled execution.** Generate every approved endpoint tool. Runtime policy controls execution by operation/method; mutating calls are protected by default and never silently execute because a documentation parser guessed them.
4. **Secrets never enter artifacts.** Do not write tokens to source, manifests, lockfiles, examples, logs, commits, or GitHub issues. Only environment-variable references and mapping names are allowed.
5. **No unbounded discovery.** Swagger UI discovery may inspect its page/config and known spec URLs. Markdown/HTML extraction uses supplied documents only. A bare base URL is not endpoint enumeration permission.
6. **Strict TypeScript.** No `any`, unchecked external input, `@ts-ignore`, or implicit unsafe defaults. Parse all source content as `unknown` then validate.
7. **Test first.** Every behavior change starts with one focused failing test and records the observed failure in its task brief.
8. **Safe generated errors.** Generated tools return safe client-facing errors; they never expose stacks, credentials, response secrets, or raw upstream diagnostics.
9. **No direct main changes after bootstrap.** Every change uses a focused GitHub Issue, issue-numbered branch, PR, CI, independent spec/code-quality review, and squash merge.

## Required workflow

1. Read the linked issue plus relevant docs and `.agent/templates/task-brief.md`.
2. Create a task brief for any change touching more than one behavior.
3. Write and run a focused failing test.
4. Implement the smallest safe change.
5. Run focused tests, affected suites, typecheck, lint, build, package/generator integration tests, and `git diff --check`.
6. Update affected product/API/safety docs and generated-project documentation.
7. Complete `.agent/checklists/pre-commit.md`, commit one intent, push, and create/update a PR with `Closes #<issue>`.
8. Obtain independent specification and code-quality reviews before merge.

## Intake and approval contract

Supported sources:

- OpenAPI 3.x or Swagger 2.0 JSON/YAML URL or local file
- Swagger UI URL, by discovering an underlying spec URL
- Markdown/HTML API documentation URL, extracted into evidence-backed candidate operations

For Markdown/HTML, emit a manifest showing operation, method, URL, inputs, authentication hints, source evidence, and confidence. Do not generate code, install dependencies, call the API, create a GitHub repository, or push until the user approves that manifest.

## Generated-project publication

Creating/pushing a generated repository is an external side effect. Immediately before that step, confirm its owner/org, name, visibility, and intended source branch with the user. Never publish credentials or a downloaded private specification.

## Verification baseline

The implementation must define package scripts equivalent to:

```bash
npm ci
npm run lint
npm run typecheck
npm test
npm run build
npm run verify:generated
npm run verify:package
npm audit --omit=dev --audit-level=high
git diff --check
git status --short --branch
```

A generation E2E test must install `type-mcp` from npm in a temporary output project and exercise the generated MCP through an official SDK transport.

## Documentation locations

- Product intent and scope: `docs/product/`
- Architecture/ADRs: `docs/architecture/`
- Manifest and generated API contracts: `docs/api/`
- Safety, auth, and publication guides: `docs/guides/`
- Approved executable plans: `docs/planning/`
- Approved design specifications: `docs/superpowers/specs/`

Use Korean or English consistently within each document. Never label a planned capability as implemented.

## Definition of done

A change is complete only when its focused test was observed failing before implementation, all applicable quality gates pass, docs and generated examples are current, the pre-commit checklist is complete, independent review is recorded, and the PR is merged according to branch protection.
