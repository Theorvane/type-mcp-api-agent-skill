#!/usr/bin/env python3
"""Regression checks for the embedded api-to-typemcp engine boundary."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/api-to-typemcp"
CLI = ROOT / "packages/type-mcp-api-cli"
WORKFLOW = ROOT / ".github/workflows/verify.yml"


class EmbeddedEngineWorkspaceTests(unittest.TestCase):
    def test_skill_declares_the_future_embedded_engine_layout(self) -> None:
        self.assertTrue(SKILL.is_dir())
        self.assertTrue((SKILL / "scripts").is_dir())
        self.assertTrue((SKILL / "templates").is_dir())

        # Task 1 establishes only the shipping boundary. Task 2 introduces the
        # executable entry point and structured-spec tests; Task 4 adds concrete
        # TypeScript templates. Do not claim those implementations exist yet.
        self.assertFalse((SKILL / "scripts/api_to_typemcp.py").exists())
        self.assertFalse((SKILL / "templates/typescript-stdio").exists())

    def test_obsolete_cli_workspace_is_removed(self) -> None:
        self.assertFalse(CLI.exists(), "the generator must not retain a CLI package workspace")

    def test_ci_uses_bundled_engine_boundary_not_cli_package(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("bundled-engine:", workflow)
        self.assertNotIn("cli-package:", workflow)
        self.assertNotIn("packages/type-mcp-api-cli", workflow)
        self.assertNotIn("package-lock.json", workflow)
        self.assertIn("test_workspace.py", workflow)
        self.assertIn("test_validate_docs.py", workflow)


if __name__ == "__main__":
    unittest.main()
