# type-mcp-api-agent — Agent & Contributor Instructions

## Purpose

`type-mcp-api-agent-skill` ships one executable `api-to-typemcp` skill. Its **bundled skill engine**—under `skills/api-to-typemcp/`—owns deterministic intake, manifest construction, approval state, policy, rendering, and contained verification. Generated projects use the published `@theorvane/type-mcp` npm package and never copy TypeMCP source.

## Source-of-truth hierarchy

1. Explicit user request and approved manifest
2. `docs/product/` and `docs/architecture/`
3. `docs/api/` and `docs/guides/`
4. `docs/planning/` for executable work order
5. This file for operating rules
6. README and examples

When sources conflict, stop and update the lower-priority source before implementation.

## Repository boundaries

- `skills/api-to-typemcp/`: released skill, bundled engine modules, controlled templates, and runtime references. Engine behavior belongs here; its release artifact must include every required runtime file.
- `docs/`: canonical product, architecture, API, safety, and planning documents.
- `.agents/`: task briefs, checklists, fixtures, and deterministic root harness scripts.
- `.github/`: documentation/harness and bundled-engine CI.
- Generated projects, credentials, downloaded specs, engine state, caches, build output, coverage, and `node_modules/` are not committed.

## Non-negotiable rules

1. **Manifest before generation.** Normalize supplied input into a secret-free manifest before source generation. Document-derived operations require an engine-issued isolated-state receipt bound to the exact canonical digest, with integrity and single-use validation.
2. **Embedded engine boundary.** Do not restore a separate generator package, release, or compatibility-resolution path. Deterministic parsing and rendering belong in the bundled skill engine.
3. **Published npm runtime, not source copying.** Generated `package.json` must depend on reviewed `@theorvane/type-mcp`; prohibit `file:`, `git:`, local checkout, or copied TypeMCP implementations.
4. **All tools, controlled execution.** Generate every approved endpoint tool. `protected-write` operations require exact known IDs in `TYPE_MCP_ALLOW_PROTECTED_OPERATIONS`; unset, malformed, wildcard, duplicate, or unknown entries fail closed **before request construction**.
5. **Secrets never enter artifacts.** Sanitize source descriptors, redirect targets, evidence URLs/snippets, diagnostics, and local paths before display, hashing, or persistence. Store environment-variable references and mapping names only.
6. **No unbounded discovery.** Inspect supplied Swagger UI documents/configuration and explicit specs only. Markdown/HTML extraction uses supplied documents only. A bare base URL is never endpoint enumeration permission.
7. **Contained execution.** Generation and generated-project verification run in a fresh temporary workspace with a scrubbed environment and explicit network policy. Inspect `package.json`, then run `npm install --ignore-scripts` before any lifecycle script. Generated projects currently ship no lockfile, so do not claim lockfile-pinned `npm ci` reproducibility. Live authenticated smoke tests require separate explicit approval.
8. **Test first.** Every behavior change starts with one focused failing test and records the observed failure in its task brief.
9. **Safe generated errors.** Generated tools return safe client-facing errors and never expose stacks, credentials, response secrets, or raw upstream diagnostics.
10. **Final publication confirmation.** Immediately before a generated repository is created or pushed, record owner/org, repository name, visibility, and source branch. Verify the actual checked-out/ref-to-publish branch and stop unless it exactly equals the recorded source branch.
11. **Protected branch flow after bootstrap.** Every change uses a focused GitHub Issue, issue-numbered branch from `dev`, PR into `dev`, CI, independent specification/code-quality review, and squash merge. `main` is release-only.

## Required workflow

1. Read the linked issue, applicable docs, and `.agents/templates/task-brief.md`.
2. Create or update a task brief for multi-file behavior changes.
3. Write and run a focused failing test or deterministic harness assertion.
4. Implement the smallest safe change.
5. Run focused tests, documentation validation, release-contract checks when their inputs change, and `git diff --check`.
6. Update affected product/API/safety/planning documentation.
7. Complete `.agents/checklists/pre-commit.md`, commit one intent, and obtain the required reviews before protected delivery.

## Verification baseline

```bash
python3 .agents/scripts/test_validate_docs.py
python3 .agents/scripts/test_workspace.py
python3 .agents/scripts/validate_docs.py
python3 .agents/scripts/test_skill_release.py
python3 -m py_compile .agents/scripts/*.py
git diff --check
git status --short --branch
```

The Task 1–5 chronology is historical. The bundled engine, renderer templates, and contained generated-project E2E are now implemented; do not describe them as deferred. New transport or registry-release behavior still requires its own reviewed task.
