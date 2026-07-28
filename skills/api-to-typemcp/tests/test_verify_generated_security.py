"""Security regression tests for contained generated-project verification."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import verify_generated  # noqa: E402


class GeneratedProjectVerificationSecurityTests(unittest.TestCase):
    def test_package_inspection_requires_a_lockfile(self) -> None:
        """Verification must fail before install when the dependency graph is unlocked."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / "package.json").write_text(json.dumps({"name": "demo"}))

            result = verify_generated.inspect_package(project)

        self.assertFalse(result["ok"])
        self.assertIn("package-lock.json is required", result["violations"])

    def test_smoke_transports_do_not_clone_the_parent_environment(self) -> None:
        """Generated smoke clients must receive an explicit minimal environment only."""
        self.assertNotIn("...process.env", verify_generated._SMOKE_READ_MJS)
        self.assertNotIn("...process.env", verify_generated._SMOKE_WRITE_DENY_MJS)
        self.assertIn(
            "env: { TYPE_MCP_BASE_URL: process.env.TYPE_MCP_BASE_URL, PATH: process.env.PATH }",
            verify_generated._SMOKE_READ_MJS,
        )

    def test_template_uses_patched_dependency_ranges(self) -> None:
        """Generated projects must not carry the ranges flagged by the security audit."""
        package_template = (SKILL_DIR / "templates" / "typescript-stdio" / "package.json.tmpl").read_text()
        self.assertIn('"@modelcontextprotocol/sdk": "^1.30.0"', package_template)
        self.assertIn('"vitest": "^4.1.10"', package_template)
        self.assertNotIn('"@modelcontextprotocol/sdk": "^1.0.0"', package_template)
        self.assertNotIn('"vitest": "^3.0.0"', package_template)
        self.assertIn('"@hono/node-server": "2.0.12"', package_template)


if __name__ == "__main__":
    unittest.main()
