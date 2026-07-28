# Agent MCP Installation Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Let `api-to-typemcp` distinguish project-only generation from project-plus-agent-installation and, after explicit per-target confirmation, register a verified generated stdio MCP server with supported agent clients.

**Architecture:** Keep manifest approval and TypeScript rendering unchanged. Add a Python installation boundary after contained generated-project verification: a typed `McpServerSpec`, read-only client detectors, immutable/fingerprinted install plans, narrowly scoped format adapters, atomic backup-and-replace writes, and truthful per-target verification. The skill remains an orchestrator: it asks the user intent/selection/final-confirmation questions; the bundled CLI only performs deterministic detection, plan construction, portable export, and confirmation-token-gated installation.

**Tech Stack:** Python 3.12 stdlib (`argparse`, `json`, `tomllib`, `pathlib`, `hashlib`, `tempfile`, `os.replace`, `subprocess`); existing `unittest` engine suite; existing generated TypeScript stdio server; official documented client CLIs/configuration formats only.

**Source design:** `docs/superpowers/specs/2026-07-28-agent-mcp-installation-design.md`

---

## Non-negotiable delivery rules

1. Begin every executable behavior task with an observed failing test and record its command/output in `.agents/task-briefs/71-agent-mcp-installation.md`.
2. The conversational skill, not an unattended CLI default, asks `project-only` versus `generate-and-install`. The default is project-only.
3. `generate` must not inspect client configuration. Only an explicit install path may call `detect`.
4. No adapter may read `.env`, print environment values, expand secret placeholders, or merge a secret from an existing agent config.
5. Only configuration formats and verification commands captured in the shipped reference document are enabled. Unknown, malformed, unsupported, or changed formats fail closed and receive portable export instructions.
6. Never perform a live upstream API request to validate client installation. Verify the configuration and, where the official CLI provides it, local server discovery only.
7. Each adapter remains independently testable. A failure rolls back only the target being mutated; never claim all-target success from partial success.
8. Keep the existing protected-write `TYPE_MCP_ALLOW_PROTECTED_OPERATIONS` behavior unchanged and fail-closed.

## Task 1: Create the issue task brief and pin supported-client evidence

**Objective:** Turn the design decision into an auditable delivery record and ensure every enabled adapter has a current official format reference before any implementation.

**Files:**
- Create: `.agents/task-briefs/71-agent-mcp-installation.md`
- Create: `skills/api-to-typemcp/references/agent-mcp-installation.md`
- Modify: `docs/product/vision.md`
- Modify: `docs/architecture/overview.md`

**Step 1: Write failing documentation-contract assertions**

Create `skills/api-to-typemcp/tests/test_agent_installation_docs.py` asserting that the reference lists these client identifiers and a source URL/retrieval date for each: `hermes`, `claude-code`, `codex`, `cursor`, `vscode-copilot`, `gemini-cli`, and `opencode`. Assert it states that portable export never mutates an agent config and that values of secrets are prohibited.

```python
def test_reference_covers_all_enabled_adapters_and_secret_boundary() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    for client in REQUIRED_CLIENTS:
        self.assertIn(f"## {client}", text)
        self.assertIn("Official reference:", _section(text, client))
    self.assertIn("never reads `.env`", text)
    self.assertIn("Portable export does not modify", text)
```

**Step 2: Run test to verify failure**

Run:

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_agent_installation_docs.py -v
```

Expected: FAIL because the adapter reference and task brief do not exist.

**Step 3: Capture current official adapter contracts**

For each client, record only the documented supported path/scope, native schema, documented add/list/test or reload command, and known limitations:

- Hermes: document `hermes mcp add`, `hermes mcp list`, and `hermes mcp test` as the preferred mutation/verification path.
- Claude Code: document its official MCP add/list/remove commands and scope behavior; do not hand-edit a file if the official CLI provides an equivalent safe operation.
- Codex: document `codex mcp add`, `codex mcp get`, `codex mcp list`, and the TOML `mcp_servers` representation.
- Cursor: document the user/workspace `mcp.json` selection and `mcpServers` JSON shape.
- VS Code/Copilot: document workspace `.vscode/mcp.json` versus user profile selection and its `mcpServers` object.
- Gemini CLI: document global/project `settings.json` selection and `mcpServers` shape.
- OpenCode: document `opencode mcp add` if available and the documented `opencode.json` local server shape.

Do not store user-home paths as universal facts when vendor documentation expresses OS-dependent paths. Keep the exact source URL and retrieval date beside each adapter. Update the product/architecture docs to make “agent installation is opt-in after generation verification” canonical.

**Step 4: Run test to verify pass**

Run:

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_agent_installation_docs.py -v
python3 .agents/scripts/test_validate_docs.py
python3 .agents/scripts/validate_docs.py
```

Expected: PASS and no active docs imply automatic installation.

**Step 5: Commit**

```bash
git add .agents/task-briefs/71-agent-mcp-installation.md skills/api-to-typemcp/references/agent-mcp-installation.md docs/product docs/architecture skills/api-to-typemcp/tests/test_agent_installation_docs.py
git commit -m "docs: define guarded agent MCP installation contract"
```

## Task 2: Add typed server descriptors and read-only detection

**Objective:** Model a generated server once, detect eligible agents without mutation, and make detection results safe to display to a user.

**Files:**
- Create: `skills/api-to-typemcp/scripts/agent_clients.py`
- Create: `skills/api-to-typemcp/tests/test_agent_clients.py`
- Create: `skills/api-to-typemcp/tests/fixtures/agent-clients/`

**Step 1: Write failing unit tests**

Write fixtures that represent a fake home/config root and a fake PATH. Test that `detect_clients()` reports an adapter only when it has positive, explainable evidence; missing config is a candidate only if an official CLI executable was found and supports safe creation; no config file is created.

```python
def test_detect_is_read_only_and_reports_only_evidenced_clients(self) -> None:
    before = snapshot_tree(self.home)
    clients = detect_clients(home=self.home, which=self.which)
    self.assertEqual([c.id for c in clients], ["hermes", "codex"])
    self.assertTrue(all(c.evidence for c in clients))
    self.assertEqual(snapshot_tree(self.home), before)


def test_detection_does_not_read_env_file_values(self) -> None:
    (self.project / ".env").write_text("TYPE_MCP_API_KEY=secret-value\n")
    result = detect_clients(home=self.home, which=self.which)
    self.assertNotIn("secret-value", json.dumps([c.to_public_dict() for c in result]))
```

**Step 2: Run test to verify failure**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_agent_clients.py -v
```

Expected: FAIL because no model/detector module exists.

**Step 3: Implement the minimal read-only contract**

Create immutable dataclasses:

```python
@dataclass(frozen=True)
class McpServerSpec:
    name: str
    command: str
    args: tuple[str, ...]
    cwd: Path
    env_names: tuple[str, ...]

@dataclass(frozen=True)
class DetectedClient:
    id: str
    display_name: str
    config_candidates: tuple[Path, ...]
    evidence: tuple[str, ...]
    can_verify_runtime: bool
```

- Build `McpServerSpec` only from the verified generated output. Require an absolute canonical output path, `dist/index.js` below that path, a safe server name, and a fixed `node` command.
- Keep an adapter registry keyed by the seven documented client IDs plus `portable`.
- Inject `home`, `platform`, and `which` into detection for deterministic tests.
- Use metadata/stat checks only. Never read `.env`, invoke an arbitrary executable, create missing configuration, or follow a configuration symlink during detection.
- Return public dictionaries with env **names** only.

**Step 4: Run focused and static tests**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_agent_clients.py -v
python3 -m py_compile skills/api-to-typemcp/scripts/agent_clients.py
```

Expected: PASS.

**Step 5: Commit**

```bash
git add skills/api-to-typemcp/scripts/agent_clients.py skills/api-to-typemcp/tests/test_agent_clients.py skills/api-to-typemcp/tests/fixtures/agent-clients
git commit -m "feat: detect supported MCP agent clients read-only"
```

## Task 3: Build deterministic plans, confirmation receipts, and portable export

**Objective:** Convert selected detected clients into a reviewable immutable plan without changing client configuration.

**Files:**
- Create: `skills/api-to-typemcp/scripts/install_plan.py`
- Create: `skills/api-to-typemcp/templates/agent-install/mcpServers.json.tmpl`
- Create: `skills/api-to-typemcp/tests/test_install_plan.py`
- Modify: `skills/api-to-typemcp/scripts/render.py`
- Modify: `skills/api-to-typemcp/tests/test_render.py`

**Step 1: Write failing tests**

Test the following before implementation:

```python
def test_plan_contains_no_env_values_and_binds_the_target_fingerprint(self) -> None:
    plan = build_plan(spec, selected=["codex"], environment=fixture_environment)
    self.assertEqual(plan.targets[0].action, "add")
    self.assertIn("TYPE_MCP_API_KEY", plan.to_public_json())
    self.assertNotIn("real-secret", plan.to_public_json())
    self.assertRegex(plan.targets[0].config_fingerprint, r"^sha256:[0-9a-f]{64}$")


def test_plan_rejects_duplicate_server_name_without_replace_selection(self) -> None:
    with self.assertRaises(InstallPlanError):
        build_plan(spec, selected=["cursor"], environment=duplicate_fixture)


def test_generated_project_includes_portable_export_without_client_config(self) -> None:
    out = self._generate_project()
    self.assertTrue((out / "agent-install/mcpServers.json").is_file())
    self.assertFalse((out / ".cursor/mcp.json").exists())
```

**Step 2: Run tests to verify failure**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_install_plan.py skills/api-to-typemcp/tests/test_render.py -v
```

Expected: FAIL because the plan/export types do not exist.

**Step 3: Implement plan construction**

- Add `InstallTarget` and `InstallPlan` frozen dataclasses. A plan includes selected adapter ID, canonical config path, `create|add|replace` action, a SHA-256 fingerprint of the bytes inspected, backup destination, redacted rendered entry, and declared verification method.
- Persist a plan confirmation receipt in `TYPE_MCP_APPROVAL_STATE_DIR`, HMAC-bound to the canonical plan digest and single-use, reusing the existing approval module’s constrained state root rather than putting state in a generated project.
- Generate a portable standard `agent-install/mcpServers.json` and an `agent-install/README.md`. It is an export only: rendering must not create any agent-specific config path.
- Preserve env variable names from `.env.example`; never emit a value or `${VALUE}` resolved from host environment.

**Step 4: Run tests to verify pass**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_install_plan.py skills/api-to-typemcp/tests/test_render.py -v
python3 .agents/scripts/test_validate_docs.py
```

Expected: PASS.

**Step 5: Commit**

```bash
git add skills/api-to-typemcp/scripts/install_plan.py skills/api-to-typemcp/templates/agent-install skills/api-to-typemcp/scripts/render.py skills/api-to-typemcp/tests
git commit -m "feat: plan MCP agent installation before mutation"
```

## Task 4: Implement safe JSON/JSONC configuration patching and rollback primitives

**Objective:** Create a single tested mutation primitive that preserves unrelated JSON-family configuration and rolls back its own target on failure.

**Files:**
- Create: `skills/api-to-typemcp/scripts/install_mcp.py`
- Create: `skills/api-to-typemcp/tests/test_install_mcp.py`
- Create: `skills/api-to-typemcp/tests/fixtures/agent-configs/json/`

**Step 1: Write failing safety tests**

```python
def test_apply_creates_same_directory_backup_and_atomically_adds_entry(self) -> None:
    receipt = issue_install_receipt(plan)
    result = apply_plan(plan, receipt=receipt)
    self.assertTrue(result.backup_path.is_file())
    self.assertEqual(json.loads(self.config.read_text())["mcpServers"]["petstore-mcp"]["command"], "node")


def test_apply_rejects_changed_fingerprint_without_writing(self) -> None:
    self.config.write_text('{"mcpServers":{"other":{}}}')
    with self.assertRaises(InstallError):
        apply_plan(plan, receipt=issue_install_receipt(plan))
    self.assertEqual(self.config.read_text(), '{"mcpServers":{"other":{}}}')


def test_apply_rolls_back_current_target_when_verification_fails(self) -> None:
    with self.assertRaises(InstallError):
        apply_plan(plan, receipt=issue_install_receipt(plan), verifier=always_fail)
    self.assertEqual(self.config.read_bytes(), self.original_bytes)
```

Also cover configuration symlinks, parse failure, parent traversal, duplicate name, single-use receipt reuse, restrictive backup mode, and no secret value in result diagnostics.

**Step 2: Run test to verify failure**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_install_mcp.py -v
```

Expected: FAIL because the mutator does not exist.

**Step 3: Implement atomic primitives**

- Canonicalize/contain the configuration path before reading. Reject a target symlink and missing parent directory unless the official client CLI is the adapter’s mutation path.
- Parse JSON strictly; JSONC is permitted only after a dedicated comment-preserving parser strategy is reviewed and fixture-tested. Do not strip comments with regex.
- Write a `0600` timestamped same-directory backup, render a temp file in the same directory, `fsync`, and use `os.replace`.
- Re-read the target and compare the saved fingerprint immediately before mutation.
- Do not replace a duplicate MCP name by default. A separately selected `replace` action must be represented in a fresh plan/receipt.
- On apply or verification failure, restore only the backup created by this invocation and report its result.

**Step 4: Run test to verify pass**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_install_mcp.py -v
python3 -m py_compile skills/api-to-typemcp/scripts/install_mcp.py
```

Expected: PASS.

**Step 5: Commit**

```bash
git add skills/api-to-typemcp/scripts/install_mcp.py skills/api-to-typemcp/tests/test_install_mcp.py skills/api-to-typemcp/tests/fixtures/agent-configs/json
git commit -m "feat: atomically install MCP configuration entries"
```

## Task 5: Add TOML and JSONC adapter codecs with preservation contracts

**Objective:** Support Codex TOML and documented JSONC clients without guessing or corrupting unrelated configuration.

**Files:**
- Create: `skills/api-to-typemcp/scripts/config_codecs.py`
- Create: `skills/api-to-typemcp/tests/test_config_codecs.py`
- Create: `skills/api-to-typemcp/tests/fixtures/agent-configs/toml/`
- Create: `skills/api-to-typemcp/tests/fixtures/agent-configs/jsonc/`

**Step 1: Write failing codec tests**

Assert exact preservation requirements per documented format: unrelated JSON/JSONC/TOML keys remain semantically unchanged, native MCP entry lands at the documented key, parse errors do not yield a write payload, and unsupported syntax yields `UnsupportedConfigFormat`.

```python
def test_codex_toml_adds_one_mcp_server_without_removing_profiles(self) -> None:
    rendered = render_codex_toml(FIXTURE.read_text(), spec)
    self.assertIn('[mcp_servers.petstore_mcp]', rendered)
    self.assertIn('[profiles.safe]', rendered)


def test_jsonc_comment_preservation_is_proven_or_adapter_is_disabled(self) -> None:
    outcome = patch_jsonc(FIXTURE.read_text(), spec)
    self.assertEqual(outcome.status, "supported")
    self.assertIn("// user-owned comment", outcome.content)
```

**Step 2: Run test to verify failure**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_config_codecs.py -v
```

Expected: FAIL because no format codec exists.

**Step 3: Implement only proven codecs**

- Use `tomllib` for TOML parse validation. Because it has no writer, add a narrow table-aware append-only renderer only for a config that is already valid and lacks the target table; otherwise reject and offer CLI/portable flow. Never serialize the whole TOML file with a lossy writer.
- Enable JSONC direct patching only if a reviewed parser/writer preserves comments and exact unrelated structure in fixture tests. If that guarantee cannot be made with a bundled/reviewed dependency, mark that adapter `manual-export-only`; do not perform heuristic comment stripping.
- Record the enabled/disabled state in `agent-mcp-installation.md` so the support matrix remains truthful.

**Step 4: Run tests to verify pass**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_config_codecs.py -v
python3 -m unittest skills/api-to-typemcp/tests/test_install_mcp.py -v
```

Expected: PASS; unsupported formats remain no-write failures.

**Step 5: Commit**

```bash
git add skills/api-to-typemcp/scripts/config_codecs.py skills/api-to-typemcp/tests/test_config_codecs.py skills/api-to-typemcp/tests/fixtures/agent-configs skills/api-to-typemcp/references/agent-mcp-installation.md
git commit -m "feat: add guarded native MCP configuration codecs"
```

## Task 6: Add one adapter at a time with fixture contracts

**Objective:** Implement all requested agent targets using the common planner/mutator and each target’s official format/CLI evidence.

**Files:**
- Modify: `skills/api-to-typemcp/scripts/agent_clients.py`
- Modify: `skills/api-to-typemcp/scripts/install_plan.py`
- Modify: `skills/api-to-typemcp/scripts/install_mcp.py`
- Modify: `skills/api-to-typemcp/tests/test_agent_clients.py`
- Create: `skills/api-to-typemcp/tests/test_agent_adapters.py`
- Create: `skills/api-to-typemcp/tests/fixtures/agent-configs/{hermes,claude-code,codex,cursor,vscode-copilot,gemini-cli,opencode}/`

**Step 1: Write failing adapter tests in this exact sequence**

Implement in small commits in the following order; each adapter’s test must prove detection, rendered native entry, plan redaction, duplicate rejection, no mutation without receipt, successful apply or documented official CLI invocation, and per-client verification result:

1. Hermes — fake `hermes` executable transcript proves `mcp add`, `mcp list`, `mcp test` arguments; test no direct profile config edit when CLI is available.
2. Codex — TOML fixture proves the documented `mcp_servers` entry and fake `codex mcp get/list` verification transcript.
3. Claude Code — fake official CLI transcript proves scoped add/list behavior; fallback is portable only unless the exact client format is source-backed and preservation-tested.
4. Cursor — `mcpServers` fixture and selected user/workspace scope.
5. VS Code/GitHub Copilot — `.vscode/mcp.json` fixture and user/workspace scope; secret values must never enter workspace configuration.
6. Gemini CLI — `settings.json` fixture with selected project/global scope.
7. OpenCode — documented `mcp` local-server object or official CLI path.

Example test shape:

```python
def test_hermes_adapter_uses_documented_cli_and_verifies_same_server(self) -> None:
    plan = build_plan(spec, selected=["hermes"], environment=self.env)
    result = apply_plan(plan, receipt=issue_install_receipt(plan), runner=self.fake_runner)
    self.assertEqual(self.fake_runner.calls[0][:3], ["hermes", "mcp", "add"])
    self.assertIn(["hermes", "mcp", "test", spec.name], self.fake_runner.calls)
    self.assertEqual(result.targets[0].status, "verified")
```

**Step 2: Run each target’s test first**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_agent_adapters.py -v
```

Expected: each new target initially FAILS for its missing registry entry or adapter renderer; previously completed targets stay green.

**Step 3: Implement the smallest adapter**

- Prefer official client CLI commands when they offer add/list/test because they are less likely to damage vendor-owned config formats.
- File adapters must use the common codec/mutator only, never bespoke write code.
- Add no target-specific secret handling. Every adapter uses `McpServerSpec.env_names` or the generated launcher; values remain outside the configured payload.
- If a target’s verified format cannot satisfy preservation/secret requirements, register it as `manual-export-only` with a specific reason and portable path rather than pretending it is installed.

**Step 4: Run the full adapter suite after every client**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_agent_clients.py skills/api-to-typemcp/tests/test_agent_adapters.py skills/api-to-typemcp/tests/test_install_plan.py skills/api-to-typemcp/tests/test_install_mcp.py -v
```

Expected: PASS. Add one commit per client (`feat: add <client> MCP installation adapter`) rather than a single opaque bulk commit.

**Step 5: Commit each enabled adapter**

```bash
git add skills/api-to-typemcp/scripts skills/api-to-typemcp/tests skills/api-to-typemcp/references/agent-mcp-installation.md
git commit -m "feat: add <client> MCP installation adapter"
```

## Task 7: Wire deterministic CLI stages and the human-facing skill flow

**Objective:** Expose safe engine operations while ensuring the model asks for intent, target selection, and final confirmation rather than letting a default CLI invocation install anything.

**Files:**
- Modify: `skills/api-to-typemcp/scripts/api_to_typemcp.py`
- Create: `skills/api-to-typemcp/tests/test_agent_install_cli.py`
- Modify: `skills/api-to-typemcp/SKILL.md`
- Modify: `skills/api-to-typemcp/tests/test_documents.py`

**Step 1: Write failing CLI and documentation tests**

```python
def test_detect_is_separate_from_generate_and_never_mutates_home(self) -> None:
    result = run_cli(["detect-agents", "--project", str(self.project)])
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(snapshot_tree(self.home), self.before)


def test_install_rejects_missing_or_wrong_plan_receipt(self) -> None:
    result = run_cli(["install-agents", "--plan", str(self.plan)])
    self.assertEqual(result.returncode, 2)
    self.assertIn("confirmation", result.stderr)


def test_skill_requires_two_explicit_questions_before_installation() -> None:
    text = SKILL.read_text(encoding="utf-8")
    self.assertIn("project only", text)
    self.assertIn("install into an agent", text)
    self.assertIn("final installation confirmation", text)
```

**Step 2: Run test to verify failure**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_agent_install_cli.py skills/api-to-typemcp/tests/test_documents.py -v
```

Expected: FAIL because the CLI stages and user-flow contract are absent.

**Step 3: Add CLI stages and instructions**

Add only these commands:

```text
api_to_typemcp detect-agents --project <verified-output> [--json]
api_to_typemcp plan-agent-install --project <verified-output> --targets <csv> --server-name <safe-name> --json
api_to_typemcp approve-agent-install --plan <plan.json> --plan-digest <digest>
api_to_typemcp install-agents --plan <plan.json> --confirmation-receipt <path> --json
```

- `generate` retains its current behavior and does not call detection.
- Plan JSON is secret-free and contains the config fingerprint/bound target list.
- `install-agents` requires the single-use plan receipt, revalidates every target fingerprint, and reports target-by-target outcome with an overall `partial` status where applicable.
- In `SKILL.md`, add a conversation sequence that explicitly asks the user: intent, selected detected targets, then final confirmation with displayed plan. Make project-only the default route and show portable export for unsupported/deselected clients.
- Update containment text: agent configuration writes are local side effects behind a final confirmation and do not prove a live upstream API call.

**Step 4: Run test to verify pass**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_agent_install_cli.py skills/api-to-typemcp/tests/test_documents.py -v
python3 -m py_compile skills/api-to-typemcp/scripts/*.py
```

Expected: PASS.

**Step 5: Commit**

```bash
git add skills/api-to-typemcp/scripts/api_to_typemcp.py skills/api-to-typemcp/SKILL.md skills/api-to-typemcp/tests
git commit -m "feat: add confirmed MCP agent installation workflow"
```

## Task 8: Prove generated launcher/project integration without a live API

**Objective:** Ensure every installation plan launches the built generated stdio server from its approved output directory and does not weaken policy containment.

**Files:**
- Modify: `skills/api-to-typemcp/scripts/render.py`
- Modify: `skills/api-to-typemcp/scripts/verify_generated.py`
- Modify: `skills/api-to-typemcp/tests/test_generated_project_e2e.py`
- Create: `skills/api-to-typemcp/tests/test_agent_install_e2e.py`

**Step 1: Write failing integration test**

Generate the Petstore fixture, build it through `verify_project`, create a portable plan, and use the plan’s `command`, `args`, and `cwd` to run the existing offline MCP list-tools smoke path. Assert no `TYPE_MCP_ALLOW_PROTECTED_OPERATIONS` value is introduced and no mock upstream request is made merely by discovery.

```python
def test_plan_launches_built_server_and_discovery_makes_no_upstream_call(self) -> None:
    project = _generate_and_verify_petstore(self.tmp)
    plan = build_plan(server_spec_from_project(project), selected=["portable"], environment=self.env)
    tools = run_mcp_list_tools(plan.portable_entry)
    self.assertIn("listPets", tools)
    self.assertEqual(self.upstream.stats(), {})
```

**Step 2: Run test to verify failure**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_agent_install_e2e.py -v
```

Expected: FAIL because plan-to-launch integration is absent.

**Step 3: Implement minimal project integration**

- Ensure `npm run build` produces the exact `dist/index.js` path required by `McpServerSpec`.
- If a launcher file is necessary for a documented client, generate it only in `agent-install/`, make it resolve its own project root safely, and test that it reads no secret value into artifacts/logs.
- Reuse the existing contained `verify_generated` scrubbed environment and local mock upstream. Do not introduce a network call to an API provider.

**Step 4: Run E2E and security regressions**

```bash
python3 -m unittest skills/api-to-typemcp/tests/test_agent_install_e2e.py skills/api-to-typemcp/tests/test_generated_project_e2e.py skills/api-to-typemcp/tests/test_verify_generated_security.py -v
```

Expected: PASS; generated project install/build/test/MCP smoke remain green and npm audit remains zero.

**Step 5: Commit**

```bash
git add skills/api-to-typemcp/scripts skills/api-to-typemcp/templates skills/api-to-typemcp/tests
git commit -m "test: verify generated MCP agent launch integration"
```

## Task 9: Update release contracts, documentation, and final regression checks

**Objective:** Ship the new adapter modules/templates/references in the released skill and make documentation/release checks prevent contract drift.

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `docs/guides/security-and-publication.md`
- Modify: `docs/api/manifest-contract.md`
- Modify: `.agents/scripts/validate_docs.py`
- Modify: `.agents/scripts/test_workspace.py`
- Modify: `.agents/scripts/test_skill_release.py`
- Modify: `.github/workflows/verify.yml` only if new deterministic test paths require explicit CI coverage
- Modify: `skills/api-to-typemcp/SKILL.md`

**Step 1: Write failing release/workspace assertions**

Add assertions that the release artifact contains `agent_clients.py`, `install_plan.py`, `install_mcp.py`, `config_codecs.py`, the portable template, and the agent-installation reference. Assert active docs say installation is opt-in, requires a final confirmation, and has portable/manual fallback. Assert there is no promise of automatic API credential import or live API verification.

**Step 2: Run test to verify failure**

```bash
python3 .agents/scripts/test_workspace.py
python3 .agents/scripts/test_skill_release.py
python3 .agents/scripts/test_validate_docs.py
```

Expected: FAIL until release/docs contracts contain the new paths and language.

**Step 3: Update release/docs contract**

- Update product/API/security docs with A/E/X behavior tables for: project-only request (A), install request with detected selected targets (A), absent/unsupported client (E), changed config fingerprint (X), duplicate server name (X), and one-target rollback/partial result (E).
- Update release package assertions without weakening existing containment, lockfile, or protected-write requirements.
- Bump the skill version only in a separately reviewed release-preparation issue after this feature PR is merged to `dev`; do not mix version/release mutations into issue #71.

**Step 4: Run full required verification**

```bash
python3 -m unittest discover -s skills/api-to-typemcp/tests -p 'test_*.py' -q
python3 .agents/scripts/test_validate_docs.py
python3 .agents/scripts/test_workspace.py
python3 .agents/scripts/validate_docs.py
python3 .agents/scripts/test_skill_release.py
python3 -m py_compile .agents/scripts/*.py skills/api-to-typemcp/scripts/*.py
git diff --check
git status --short --branch
```

Expected: all suites pass; no generated output, fake home, `.env`, cache, Node modules, or backup is tracked.

**Step 5: Commit**

```bash
git add README.md AGENTS.md docs .agents/scripts .github/workflows skills/api-to-typemcp
git commit -m "docs: document opt-in MCP agent installation"
```

## Task 10: Review-gated delivery

**Objective:** Deliver only a reviewable, exact-head implementation to protected `dev`.

**Files:**
- Modify: `.agents/task-briefs/71-agent-mcp-installation.md`

**Step 1: Complete evidence**

Record each red/green command, adapter matrix, runtime-verification capability, skipped/manual-only target reason, security regression result, and the exact final commit SHA in the task brief.

**Step 2: Request independent review**

Create a PR from `feat/71-agent-mcp-installation` to `dev`. Require an independent specification review (every enabled adapter matches the pinned official reference and design) and a code-quality/security review (fingerprint, backup, atomicity, secret hygiene, rollback, and no-live-upstream invariant).

**Step 3: Revalidate exact head after review**

```bash
gh pr checks <PR> --repo Theorvane/type-mcp-api-agent-skill --watch --interval 10
gh pr view <PR> --repo Theorvane/type-mcp-api-agent-skill --json headRefOid,reviews,reviewDecision,statusCheckRollup
```

Expected: approvals and checks apply to the exact current head. If the head changes after review, repeat review/verification.

**Step 4: Merge**

Squash-merge only after both reviews and every required check are green. Do not promote to `main` or publish from this feature issue.
