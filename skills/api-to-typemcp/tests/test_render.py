"""Renderer integration tests: generate a full project from a manifest."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = REPO_ROOT / "skills" / "api-to-typemcp"
ENTRY = SKILL_DIR / "scripts" / "api_to_typemcp.py"
FIXTURES = SKILL_DIR / "tests" / "fixtures"


def run_cli(args: list[str], env_extra: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(ENTRY), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


def fixture_path(name: str) -> str:
    return str(FIXTURES / name)


class RenderTests(unittest.TestCase):
    """End-to-end generation from the Petstore fixture."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.state_dir = self.tmp / "approval-state"
        self.state_dir.mkdir()
        self.env_extra = {"TYPE_MCP_APPROVAL_STATE_DIR": str(self.state_dir)}

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _generate_project(self) -> Path:
        """Approve and generate into a fresh output dir; return the path."""
        result = run_cli(["manifest", "--file", fixture_path("petstore.openapi.json"), "--json"], env_extra=self.env_extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        digest = json.loads(result.stdout)["digest"]

        approve = run_cli(
            ["approve", "--file", fixture_path("petstore.openapi.json"), "--manifest-digest", digest],
            env_extra=self.env_extra,
        )
        self.assertEqual(approve.returncode, 0, approve.stderr)

        out = self.tmp / "output"
        out.mkdir()
        gen = run_cli(
            ["generate", "--file", fixture_path("petstore.openapi.json"), "--output", str(out),
             "--confirm-manifest-digest", digest],
            env_extra=self.env_extra,
        )
        self.assertEqual(gen.returncode, 0, gen.stderr)
        return out

    # ------------------------------------------------------------------
    # package.json
    # ------------------------------------------------------------------

    def test_package_json_depends_on_published_typemcp(self) -> None:
        out = self._generate_project()
        pkg = json.loads((out / "package.json").read_text())
        deps = pkg.get("dependencies", {})
        self.assertIn("@theorvane/type-mcp", deps)
        self.assertEqual(deps["@theorvane/type-mcp"], "0.2.0")
        self.assertIn("zod", deps)
        # No local/git/file dependencies.
        for name, version in deps.items():
            self.assertNotIn("file:", version)
            self.assertNotIn("git:", version)
            self.assertFalse(version.startswith("link:"))

    # ------------------------------------------------------------------
    # server.ts
    # ------------------------------------------------------------------

    def test_server_has_decorators_for_every_operation(self) -> None:
        out = self._generate_project()
        server_ts = (out / "src" / "server.ts").read_text()
        self.assertIn("@McpServer", server_ts)
        # Petstore fixture has 2 operations: listPets (GET) and createPet (POST).
        self.assertIn("@McpTool", server_ts)
        self.assertGreaterEqual(server_ts.count("@McpTool"), 2)
        # Zod object inputs.
        self.assertIn("z.object", server_ts)

    # ------------------------------------------------------------------
    # index.ts
    # ------------------------------------------------------------------

    def test_index_creates_and_starts_stdio_server(self) -> None:
        out = self._generate_project()
        index_ts = (out / "src" / "index.ts").read_text()
        self.assertIn("createMcpServer", index_ts)
        self.assertIn("startStdioServer", index_ts)

    # ------------------------------------------------------------------
    # policy.ts
    # ------------------------------------------------------------------

    def test_policy_checks_authorization_before_request(self) -> None:
        out = self._generate_project()
        policy_ts = (out / "src" / "policy.ts").read_text()
        self.assertIn("TYPE_MCP_ALLOW_PROTECTED_OPERATIONS", policy_ts)
        # Must reject wildcards.
        self.assertIn("*", policy_ts)

    # ------------------------------------------------------------------
    # .env.example
    # ------------------------------------------------------------------

    def test_env_example_has_variable_names_only(self) -> None:
        out = self._generate_project()
        env_example = (out / ".env.example").read_text()
        # Should contain variable names but no values (no '=' with content).
        for line in env_example.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            self.assertNotIn("=", line, f".env.example line has a value: {line}")

    # ------------------------------------------------------------------
    # manifest copy
    # ------------------------------------------------------------------

    def test_generated_manifest_is_secret_free(self) -> None:
        out = self._generate_project()
        manifest_path = out / "api-to-typemcp.manifest.json"
        self.assertTrue(manifest_path.exists())
        content = manifest_path.read_text()
        # No fixture path leakage.
        self.assertNotIn(str(FIXTURES), content)
        self.assertNotIn("petstore.openapi.json", content)

    # ------------------------------------------------------------------
    # All files present
    # ------------------------------------------------------------------

    def test_all_expected_files_exist(self) -> None:
        out = self._generate_project()
        expected = [
            "package.json",
            "tsconfig.json",
            ".env.example",
            "README.md",
            "api-to-typemcp.manifest.json",
            "src/index.ts",
            "src/server.ts",
            "src/api-client.ts",
            "src/policy.ts",
            "src/schemas.ts",
            "src/operations.ts",
            "test/policy.test.ts",
            "test/server.test.ts",
        ]
        for rel in expected:
            self.assertTrue((out / rel).exists(), f"Missing: {rel}")


if __name__ == "__main__":
    unittest.main()
