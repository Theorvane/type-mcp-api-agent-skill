# type-mcp-api-agent — Agent & Contributor Instructions

## Purpose

`type-mcp-api-agent` is the standalone Hermes **skill/orchestration** repository for producing TypeMCP MCP projects from API sources. It invokes the separately versioned and installable `type-mcp-api-cli` CLI. The CLI owns deterministic intake, parsing, normalization, manifest serialization, and source rendering; this repository owns user interaction, manifest approval, CLI provenance/version checks, safety gates, generated-project verification, and confirmed publication.

Generated projects install and execute the published `type-mcp` npm package. No repository in this product family copies `type-mcp` source into generated output.

## Source-of-truth hierarchy

1. Explicit user request and approved manifest
2. `docs/product/` and `docs/architecture/`
3. `docs/api/` and `docs/guides/`
4. `docs/planning/` for executable work order
5. This file for operating rules
6. README and examples

When sources conflict, stop and update the lower-priority source before implementation.

## Repository boundaries

- `skills/`: Hermes skills that orchestrate the companion CLI. They may not duplicate CLI parsing/generation logic.
- `docs/`: canonical product, architecture, API, safety, compatibility, and planning documents for the skill.
- `.agent/`: tracked task briefs, checklists, review templates, fixtures, and deterministic harness scripts.
- `.github/`: issue/PR templates and skill/harness CI.
- `type-mcp-api-cli` is a **separate repository/package**, not a subdirectory, workspace package, git submodule, or copied source tree here.
- Generated user projects, credentials, downloaded specs, CLI binaries/caches, build output, coverage, and `node_modules/` are not committed here.

## Non-negotiable rules

1. **Manifest before generation.** Normalize every input through the CLI into the manifest contract. Markdown/HTML-derived operations require explicit user approval before source generation.
2. **CLI boundary, not generator implementation.** The skill invokes a compatible released `type-mcp-api-cli` executable. Do not add OpenAPI parsing, Swagger UI scraping, document extraction, manifest rendering, or TypeScript source-template logic to this repository.
3. **Trusted CLI resolution.** Follow `docs/guides/cli-compatibility.md` exactly. No CLI release is supported until that policy lists its exact version, protocol/schema, and npm integrity. Never execute a `PATH` binary, self-reported metadata-only artifact, or user-local binary without the policy's explicit digest/path approval flow.
4. **npm dependency, not source copying.** The CLI-generated `package.json` installs a verified `type-mcp` npm version. The skill verifies package exports and a generated-server smoke test only inside the contained verification boundary.
5. **All tools, controlled execution.** Generate every approved endpoint tool. Runtime policy controls execution by operation/method; mutating calls are protected by default and never silently execute because a documentation parser guessed them.
6. **Secrets never enter artifacts.** Sanitize source descriptors, redirect targets, evidence URLs/snippets, diagnostics, and local paths before displaying, hashing, or persisting them. Do not write tokens to source, manifests, lockfiles, examples, logs, commits, or GitHub issues. Only environment-variable references and mapping names are allowed.
7. **No unbounded discovery.** Swagger UI discovery may inspect its page/config and known spec URLs. Markdown/HTML extraction uses supplied documents only. A bare base URL is not endpoint enumeration permission.
8. **Contained execution.** CLI and generated-project verification run only in a fresh temporary workspace with a scrubbed environment, controlled working directory, and explicit network/upstream policy. Inspect the lockfile and run `npm ci --ignore-scripts` before any project lifecycle script. A live authenticated smoke test needs separate explicit user approval.
9. **Test first.** Every behavior change starts with one focused failing test and records the observed failure in its task brief.
10. **Safe generated errors.** Generated tools return safe client-facing errors; they never expose stacks, credentials, response secrets, or raw upstream diagnostics.
11. **No direct main changes after bootstrap.** Every change uses a focused GitHub Issue, issue-numbered branch, PR, CI, independent spec/code-quality review, and squash merge.

## Required workflow

1. Read the linked issue plus relevant docs and `.agent/templates/task-brief.md`.
2. Create a task brief for any change touching more than one behavior.
3. Write and run a focused failing test or deterministic harness assertion.
4. Implement the smallest safe change.
5. Run focused tests, the skill/CLI fixture contract test, documentation validator, and `git diff --check`.
6. Update affected product/API/safety/compatibility docs.
7. Complete `.agent/checklists/pre-commit.md`, commit one intent, push, and create/update a PR with `Closes #<issue>`.
8. Obtain independent specification and code-quality reviews before merge.

## Skill-to-CLI contract

The skill invokes the CLI in staged commands; exact flags are defined by the published CLI contract, not invented by the skill:

1. **Inspect:** validate input type and source provenance without generating code.
2. **Manifest:** request a secret-free normalized manifest and diagnostics.
3. **Generate:** only after required approval, render a project into a declared empty output directory.
4. **Verify:** ask the CLI or project harness for deterministic generation metadata; the skill independently runs the generated project's documented quality gates.

The skill must test against a controlled fixture CLI that emits known success, incompatibility, malformed-manifest, and unsafe-side-effect cases. This keeps the orchestration contract testable before the real CLI exists.

## Intake and approval contract

Supported sources through the CLI:

- OpenAPI 3.x or Swagger 2.0 JSON/YAML URL or local file
- Swagger UI URL, by discovering an underlying spec URL
- Markdown/HTML API documentation URL, extracted into evidence-backed candidate operations

For Markdown/HTML, show the CLI manifest with operation, method, URL, inputs, authentication hints, source evidence, and confidence. Do not invoke CLI generation, install dependencies, call the API, create a GitHub repository, or push until the user approves that manifest.

## Generated-project publication

Creating/pushing a generated repository is an external side effect. Immediately before that step, confirm its owner/org, name, visibility, and intended source branch with the user. Never publish credentials or a downloaded private specification.

## Verification baseline

The skill/harness must define deterministic checks equivalent to:

```bash
python3 .agent/scripts/validate_docs.py
python3 -m py_compile .agent/scripts/validate_docs.py
# once the skill has executable tests:
npm ci
npm run lint
npm run typecheck
npm test
npm run build
npm run verify:cli-contract
git diff --check
git status --short --branch
```

A cross-repository E2E test must use a released/fixture CLI to generate a temporary output project, install `type-mcp` from npm in that project, and exercise the MCP through an official SDK transport.

## Documentation locations

- Product intent and scope: `docs/product/`
- Architecture/ADRs and cross-repo compatibility: `docs/architecture/`
- Manifest and generated API contracts: `docs/api/`
- Safety, auth, and publication guides: `docs/guides/`
- Approved executable plans: `docs/planning/`
- Approved design specifications: `docs/superpowers/specs/`
- Skill behavior: `skills/api-to-typemcp/`

Use Korean or English consistently within each document. Never label a planned capability as implemented.

## Definition of done

A change is complete only when its focused assertion was observed failing before implementation, applicable quality gates pass, docs and fixtures are current, the pre-commit checklist is complete, independent review is recorded, and the PR is merged according to branch protection.
