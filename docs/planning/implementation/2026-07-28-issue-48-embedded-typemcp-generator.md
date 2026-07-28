# Embedded TypeMCP Generator Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Make the published `api-to-typemcp` skill itself generate verified stdio TypeMCP MCP projects from approved API documentation, without a separate `type-mcp-api-cli` package or release.

**Architecture:** Move deterministic intake, manifest, approval, policy, rendering, and static verification into Python modules bundled under `skills/api-to-typemcp/scripts/`. Render a standalone strict TypeScript project that imports the published `@theorvane/type-mcp@0.2.0` and uses its decorator/runtime APIs. Root Python regression tests exercise the bundled engine and a generated-project E2E fixture; release packaging publishes every required script/template/reference with `SKILL.md`.

**Tech Stack:** Python 3.12 stdlib plus a reviewed YAML parser strategy; TypeScript/Node 20+ in generated projects; `@theorvane/type-mcp@0.2.0`; `zod`; MCP SDK; unittest/Vitest as appropriate; GitHub Actions.

**Source design:** `docs/superpowers/specs/2026-07-28-embedded-typemcp-generator-design.md`

---

## Preconditions and implementation order

1. This plan deliberately removes the obsolete CLI package and all release-policy references before adding runtime functionality; no code may retain a fallback to `type-mcp-api-cli`.
2. Every production behavior begins with an observed failing focused test recorded in `.agents/task-briefs/48-embed-typemcp-generator.md`.
3. The delivery is one issue but four reviewable commits/PR checkpoints: migration boundary, structured engine, TypeMCP renderer/E2E, then bounded Swagger UI/document intake.
4. Generated code must be tested using the published npm package, never an adjacent TypeMCP checkout or a copied implementation.

## Task 1: Replace the obsolete workspace/CLI release boundary

**Objective:** Make repository governance, CI, docs, and release packaging describe one shipping unit: the executable skill.

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/product/vision.md`
- Modify: `docs/product/mvp-scope.md`
- Modify: `docs/architecture/overview.md`
- Modify: `docs/api/manifest-contract.md`
- Modify: `docs/guides/security-and-publication.md`
- Remove: `docs/guides/cli-compatibility.md`
- Modify: `docs/planning/README.md`
- Modify: `.github/workflows/verify.yml`
- Modify: `.agents/scripts/validate_docs.py`
- Modify: `.agents/scripts/test_validate_docs.py`
- Replace: `.agents/scripts/test_workspace.py`
- Remove: `packages/type-mcp-api-cli/`

**Step 1: Write focused failing migration tests**

Replace `test_workspace.py` with assertions that the bundled skill engine and template paths exist, `packages/type-mcp-api-cli` does not exist, and the verification workflow has an engine-generated-project job rather than a CLI-package job.

Add negative assertions in `test_validate_docs.py` that active source documents do not instruct users to resolve, install, execute, or wait for `type-mcp-api-cli`.

**Step 2: Run test to verify failure**

Run:

```bash
python3 .agents/scripts/test_workspace.py
python3 .agents/scripts/test_validate_docs.py
```

Expected: FAIL because the old CLI workspace, release gate, and CI job still exist.

**Step 3: Perform the boundary migration**

- Rewrite active source-of-truth docs to name the bundled engine as owner of deterministic intake/rendering.
- Keep the historical July 21 design labeled superseded; it may mention its historical CLI decision only in an explicitly historical section.
- Replace CLI receipt wording with **engine-issued receipt** only if cryptographic receipt implementation remains in scope; otherwise use a deterministic receipt record held in isolated state and document exact integrity/single-use behavior.
- Delete `docs/guides/cli-compatibility.md` and package-specific source/docs/tests/lockfiles.
- Replace the `cli-package` Actions job with a `bundled-engine` job that installs only its declared test dependencies and runs engine tests plus generated-project E2E.
- Update document validator required paths/phrases to the new contract. Do not merely weaken tests; assert the embedded-engine and published `@theorvane/type-mcp` invariants.

**Step 4: Run tests to verify pass**

Run:

```bash
python3 .agents/scripts/test_workspace.py
python3 .agents/scripts/test_validate_docs.py
python3 .agents/scripts/validate_docs.py
git diff --check
```

Expected: PASS; docs no longer create an external CLI runtime dependency.

**Step 5: Commit**

```bash
git add AGENTS.md README.md docs .github/workflows/verify.yml .agents/scripts
git rm -r packages/type-mcp-api-cli docs/guides/cli-compatibility.md
git commit -m "refactor: replace CLI package boundary with embedded skill engine"
```

## Task 2: Create the bundled engine contract and structured-spec fixture tests

**Objective:** Establish a safe, dependency-minimal engine API for file/URL descriptors, manifests, approval state, policy classification, and empty-target generation.

**Files:**
- Create: `skills/api-to-typemcp/scripts/api_to_typemcp.py`
- Create: `skills/api-to-typemcp/scripts/intake.py`
- Create: `skills/api-to-typemcp/scripts/manifest.py`
- Create: `skills/api-to-typemcp/scripts/policy.py`
- Create: `skills/api-to-typemcp/scripts/structured_specs.py`
- Create: `skills/api-to-typemcp/tests/test_engine_cli.py`
- Create: `skills/api-to-typemcp/tests/test_manifest.py`
- Create: `skills/api-to-typemcp/tests/test_policy.py`
- Create: `skills/api-to-typemcp/tests/fixtures/petstore.openapi.json`
- Create: `skills/api-to-typemcp/tests/fixtures/petstore.swagger.yaml`

**Step 1: Write the failing structured-manifest test**

Write a test that invokes `api_to_typemcp.py manifest --file <fixture> --json` and asserts:

- source kind and a secret-free source descriptor;
- stable operations from both `GET /pets/{petId}` and `POST /pets`;
- uppercase HTTP methods, unique stable operation IDs, normalized parameter descriptors, and exact policy modes;
- a deterministic SHA-256 canonical manifest digest;
- no temp path, query value, or fixture secret text in output.

**Step 2: Run test to verify failure**

Run:

```bash
python3 -m unittest skills.api-to-typemcp.tests.test_manifest -v
```

Expected: FAIL because the entry point/module does not exist.

**Step 3: Implement minimal structured input and manifest primitives**

- Accept only explicit local file descriptors first; leave remote URL acquisition behind `intake.py` with explicit scheme/host/redirect/size limits.
- Parse JSON and YAML only after validating document type and size; use a declared parser dependency only if the standard library cannot safely support YAML.
- Support OpenAPI 3.x and Swagger 2.0 only. Reject references/features that cannot be normalized safely rather than guessing.
- Canonicalize manifest JSON using a documented deterministic JSON encoding restricted to values representable by the contract; compute lowercase `sha256:<hex>` digest.
- Normalize paths, parameters, request bodies, response summaries, auth mapping *names*, warnings, evidence, and status.
- Never write a source or generated artifact during `inspect` or `manifest`.

**Step 4: Run focused tests to verify pass**

Run:

```bash
python3 -m unittest skills.api-to-typemcp.tests.test_manifest -v
python3 -m unittest skills.api-to-typemcp.tests.test_engine_cli -v
```

Expected: PASS for JSON/YAML valid fixtures and malformed/unsupported rejection cases.

**Step 5: Add and prove the execution-policy gate**

Write failing tests covering `GET` → `read`, `POST` → `protected-write`, unknown method → `deny`, wildcard/malformed/duplicate/unknown allowlist entries → no grant, and exact known ID → grant.

Run the focused test, implement `policy.py`, then rerun it:

```bash
python3 -m unittest skills.api-to-typemcp.tests.test_policy -v
```

Expected: initial FAIL, then PASS.

**Step 6: Commit**

```bash
git add skills/api-to-typemcp/scripts skills/api-to-typemcp/tests
git commit -m "feat: add embedded structured API manifest engine"
```

## Task 3: Add manifest approval state and safe generation preconditions

**Objective:** Ensure document-derived sources cannot generate without current-digest explicit approval, and no output target is altered accidentally.

**Files:**
- Modify: `skills/api-to-typemcp/scripts/api_to_typemcp.py`
- Modify: `skills/api-to-typemcp/scripts/manifest.py`
- Create: `skills/api-to-typemcp/scripts/approval.py`
- Modify: `skills/api-to-typemcp/tests/test_manifest.py`
- Create: `skills/api-to-typemcp/tests/test_approval.py`
- Create: `skills/api-to-typemcp/tests/test_output_safety.py`

**Step 1: Write failing approval tests**

Test that a document-derived manifest cannot pass `generate` unless an isolated-state receipt exactly matches its current digest and has not expired/been consumed. Test a manifest mutation invalidates a receipt.

Test that generation rejects a missing/non-empty target unless `--replace` is explicitly passed and that replacement cannot escape the declared target root.

**Step 2: Run tests to verify failure**

Run:

```bash
python3 -m unittest skills.api-to-typemcp.tests.test_approval skills.api-to-typemcp.tests.test_output_safety -v
```

Expected: FAIL because approval/output guards do not exist.

**Step 3: Implement the smallest safe approval/output flow**

- `approve` must require an explicit `--manifest-digest` matching current state and write a single-use receipt in a process-owned isolated directory.
- Do not place mutable approval state in the manifest.
- Use a per-state random secret/HMAC or an equivalent authenticated receipt format so edited receipt/manifest pairs cannot forge approval.
- Generate only after receipt validation for Markdown/HTML-derived input; structured specs remain reviewable and generate only with an explicit `--confirm-manifest-digest` command argument.
- Enforce empty output or exact explicit replace confirmation before rendering.

**Step 4: Run focused tests to verify pass**

Run the command from Step 2. Expected: PASS, including stale/tampered/used receipt and output-escape rejection cases.

**Step 5: Commit**

```bash
git add skills/api-to-typemcp/scripts skills/api-to-typemcp/tests
git commit -m "feat: gate embedded generation on manifest approval"
```

## Task 4: Add TypeMCP stdio project templates and renderer

**Objective:** Generate a strict TypeScript project that uses the published `@theorvane/type-mcp@0.2.0` API to expose every approved operation as a policy-gated MCP tool.

**Files:**
- Create: `skills/api-to-typemcp/scripts/render.py`
- Create: `skills/api-to-typemcp/templates/typescript-stdio/package.json.tmpl`
- Create: `skills/api-to-typemcp/templates/typescript-stdio/tsconfig.json.tmpl`
- Create: `skills/api-to-typemcp/templates/typescript-stdio/src/index.ts.tmpl`
- Create: `skills/api-to-typemcp/templates/typescript-stdio/src/api-client.ts.tmpl`
- Create: `skills/api-to-typemcp/templates/typescript-stdio/src/policy.ts.tmpl`
- Create: `skills/api-to-typemcp/templates/typescript-stdio/README.md.tmpl`
- Create: `skills/api-to-typemcp/templates/typescript-stdio/.env.example.tmpl`
- Modify: `skills/api-to-typemcp/scripts/api_to_typemcp.py`
- Create: `skills/api-to-typemcp/tests/test_render.py`
- Create: `skills/api-to-typemcp/tests/test_generated_project_static.py`

**Step 1: Write a failing renderer test**

Given the approved Petstore manifest, call `generate` into an empty temporary directory and assert:

- `package.json` depends exactly on `@theorvane/type-mcp: 0.2.0`, `zod`, and the MCP SDK; it has no `file:`, `git:`, or local TypeMCP dependency;
- generated `server.ts` has `@McpServer`, a distinct `@McpTool` for every approved operation, and Zod object inputs;
- generated `index.ts` imports and calls `createMcpServer()` and `startStdioServer()`;
- generated policy checks operation authorization before `api-client` request construction;
- `.env.example` contains variable names only;
- generated manifest is canonical and has no source secret/path leakage.

**Step 2: Run test to verify failure**

Run:

```bash
python3 -m unittest skills.api-to-typemcp.tests.test_render skills.api-to-typemcp.tests.test_generated_project_static -v
```

Expected: FAIL because renderer/templates do not exist.

**Step 3: Implement renderer and templates**

- Template fixed infrastructure files; render operation-specific `operations.ts`, `schemas.ts`, and `server.ts` programmatically with strict identifier escaping and collision handling.
- Use only documented TypeMCP 0.2.0 public APIs: decorators, `createMcpServer`, and `startStdioServer`.
- Emit a request client that puts path/query/header/body values only after policy validation. It must build authentication from optional environment-variable names without logging values.
- Ensure all upstream errors are mapped to safe client-facing errors.
- Generate every approved operation; do not silently omit protected writes or denied methods. Denied tools exist but always return a safe error without constructing a request.

**Step 4: Run renderer tests to verify pass**

Run the Step 2 command. Expected: PASS.

**Step 5: Commit**

```bash
git add skills/api-to-typemcp/scripts skills/api-to-typemcp/templates skills/api-to-typemcp/tests
git commit -m "feat: render TypeMCP stdio projects from approved manifests"
```

## Task 5: Add generated-project install, typecheck, test, build, and MCP smoke E2E

**Objective:** Prove a generated project uses the published TypeMCP package and runs through an official stdio MCP transport without calling a live upstream.

**Files:**
- Create: `skills/api-to-typemcp/scripts/verify_generated.py`
- Create: `skills/api-to-typemcp/tests/test_generated_project_e2e.py`
- Create: `skills/api-to-typemcp/tests/fixtures/mock_upstream.py`
- Modify: `.github/workflows/verify.yml`
- Modify: `.agents/scripts/test_workspace.py`

**Step 1: Write the failing E2E test**

The test must generate a project from the structured fixture into a fresh temporary directory, inspect its dependency declaration, install it with a scrubbed environment, and execute its generated quality commands. It then starts a local fixture upstream and uses the official MCP SDK stdio client to list/call a read tool.

A second case invokes a protected-write tool with no/malformed/wildcard/unknown allowlist and asserts the fixture upstream counter remains zero.

**Step 2: Run test to verify failure**

Run:

```bash
python3 -m unittest skills.api-to-typemcp.tests.test_generated_project_e2e -v
```

Expected: FAIL before verifier/fixtures and generated test scripts exist.

**Step 3: Implement contained verification**

- Copy only the generated output to a fresh temporary workspace; do not run against repository files.
- Scrub credentials, git config, cloud variables, npm auth, and inherited API endpoints. Use isolated HOME/TMP/npm cache directories.
- Inspect generated `package.json` and lockfile before lifecycle scripts; use `npm ci --ignore-scripts` first.
- Run lint, typecheck, test, and build using the generated scripts.
- Use local mock upstream and no live API calls in CI.
- Add CI setup for Node 20+ cache keyed to generated-project test metadata, not the deleted CLI lockfile.

**Step 4: Run E2E test to verify pass**

Run the Step 2 command. Expected: PASS with a published npm TypeMCP package resolution and denied-write zero-request evidence.

**Step 5: Commit**

```bash
git add skills/api-to-typemcp .github/workflows/verify.yml .agents/scripts/test_workspace.py
git commit -m "test: verify generated TypeMCP projects in containment"
```

## Task 6: Add bounded Swagger UI discovery and supplied-document extraction

**Objective:** Support all approved source categories without crawling unrelated pages or guessing operations beyond evidence.

**Files:**
- Create: `skills/api-to-typemcp/scripts/swagger_ui.py`
- Create: `skills/api-to-typemcp/scripts/documents.py`
- Create: `skills/api-to-typemcp/tests/test_swagger_ui.py`
- Create: `skills/api-to-typemcp/tests/test_documents.py`
- Create: `skills/api-to-typemcp/tests/fixtures/swagger-ui.html`
- Create: `skills/api-to-typemcp/tests/fixtures/api-reference.md`
- Create: `skills/api-to-typemcp/tests/fixtures/api-reference.html`
- Modify: `skills/api-to-typemcp/scripts/intake.py`
- Modify: `skills/api-to-typemcp/scripts/api_to_typemcp.py`

**Step 1: Write failing bounded-discovery tests**

- Swagger UI fixture exposes an explicit spec URL/config; engine returns that URL/source descriptor and then follows structured parsing.
- A fixture with no explicit spec reference fails safely; no additional host/page fetch is attempted.
- Markdown/HTML fixtures produce only operations with method/path/evidence snippets; every such manifest requires `explicit-user-confirmation` and valid receipt before generation.
- Ambiguous prose produces warnings and no guessed operation.

**Step 2: Run tests to verify failure**

Run:

```bash
python3 -m unittest skills.api-to-typemcp.tests.test_swagger_ui skills.api-to-typemcp.tests.test_documents -v
```

Expected: FAIL because bounded discovery/extraction modules do not exist.

**Step 3: Implement minimum bounded intake**

- Parse Swagger UI config/script data and explicit known spec references only; never crawl a base origin.
- Parse supplied Markdown/HTML in memory with size limits and redact evidence before digesting/persisting.
- Extract only clear HTTP method + relative/absolute path candidates, with source line/section evidence and confidence.
- Route every document-derived manifest through the approval receipt gate; do not downgrade it due to high confidence.

**Step 4: Run source tests to verify pass**

Run the Step 2 command. Expected: PASS for positive and no-discovery/no-evidence cases.

**Step 5: Commit**

```bash
git add skills/api-to-typemcp/scripts skills/api-to-typemcp/tests
git commit -m "feat: add bounded Swagger UI and document intake"
```

## Task 7: Update the skill, release package contract, and user-facing docs

**Objective:** Make installed agents use the bundled engine correctly and ensure ClawHub/skills-hub artifacts include all runtime files.

**Files:**
- Modify: `skills/api-to-typemcp/SKILL.md`
- Create: `skills/api-to-typemcp/references/type-mcp-runtime.md`
- Modify: `README.md`
- Modify: `docs/api/manifest-contract.md`
- Modify: `docs/guides/security-and-publication.md`
- Modify: `.github/workflows/skill-release.yml`
- Modify: `.agents/scripts/test_skill_release.py`
- Modify: `.agents/scripts/test_validate_docs.py`
- Modify: `.agents/task-briefs/48-embed-typemcp-generator.md`

**Step 1: Write failing distribution tests**

Assert the release workflow/ClawHub packaging includes `scripts/`, `templates/`, and `references/` beneath the skill path, and `SKILL.md` gives exact bundled-engine commands with mandatory manifest/approval/output/publish gates.

**Step 2: Run tests to verify failure**

Run:

```bash
python3 .agents/scripts/test_skill_release.py
python3 .agents/scripts/test_validate_docs.py
```

Expected: FAIL because release contract only verifies a guidance-only `SKILL.md`.

**Step 3: Update skill/runtime documentation**

- Replace “no supported CLI release” outcomes with exact built-in engine workflow.
- Document a concrete command sequence using absolute skill-relative script paths and a controlled temporary output directory.
- Reference the reviewed `@theorvane/type-mcp@0.2.0` public contract and prohibit unavailable/private APIs.
- Keep explicit user confirmation right before GitHub publication.
- Bump skill version only in a separate release-preparation PR after implementation has been merged to `dev`.

**Step 4: Run tests to verify pass**

Run the Step 2 command plus:

```bash
python3 .agents/scripts/validate_docs.py
git diff --check
```

Expected: PASS.

**Step 5: Commit**

```bash
git add skills/api-to-typemcp README.md docs .github/workflows .agents
git commit -m "docs: publish embedded TypeMCP generator workflow"
```

## Task 8: Full verification, reviews, and protected delivery

**Objective:** Demonstrate complete, reproducible behavior before PR delivery.

**Files:**
- Modify: `.agents/task-briefs/48-embed-typemcp-generator.md`
- No additional production files unless a failing verification exposes a scoped defect.

**Step 1: Run the complete repository verification suite**

Run:

```bash
python3 .agents/scripts/test_validate_docs.py
python3 .agents/scripts/test_workspace.py
python3 .agents/scripts/test_validate_branch_governance.py
python3 .agents/scripts/test_skill_release.py
python3 .agents/scripts/validate_docs.py
python3 .agents/scripts/validate_branch_governance.py
python3 .agents/scripts/validate_release_promotion.py
python3 -m py_compile .agents/scripts/*.py skills/api-to-typemcp/scripts/*.py
python3 -m unittest discover -s skills/api-to-typemcp/tests -v
git diff --check
git status --short --branch
```

Expected: all suites pass; no generated fixture output, credentials, caches, or deleted-CLI artifacts are tracked.

**Step 2: Request independent reviews**

- Request a specification review at the exact PR head: embedded engine, approval policy, source bounds, and TypeMCP API usage.
- Request a code-quality/security review at the exact PR head: parser bounds, secret hygiene, output containment, generated TypeScript, dependencies, and smoke tests.
- Resolve all threads with a new exact-head review after code changes.

**Step 3: Deliver via protected branch workflow**

```bash
git push -u origin feat/48-embed-typemcp-generator
gh pr create --base dev --head feat/48-embed-typemcp-generator --title "feat: embed TypeMCP generator in api-to-typemcp" --body "Closes #48"
```

Expected: PR author is `sjungwon03`; reviewer is `sjungwon03-ai`; merge only after exact-head approval, green CI, and zero unresolved threads. Use squash merge into `dev`.

## Release follow-up (separate issue/PR)

After #48 is merged and verified on `dev`, create a release issue to bump the skill version. Promote reviewed `dev` to `main`; only then does the existing release workflow create the GitHub release and publish the full executable skill artifact to ClawHub and skills-hub.ai. Verify public registry contents include `SKILL.md`, `scripts/`, `templates/`, and `references/` before reporting availability.
