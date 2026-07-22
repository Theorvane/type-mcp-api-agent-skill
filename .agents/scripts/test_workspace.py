#!/usr/bin/env python3
"""Regression checks for the unified skill + CLI workspace layout."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "packages/type-mcp-api-cli"


class UnifiedWorkspaceTests(unittest.TestCase):
    def test_embeds_the_cli_as_an_independent_workspace_package(self) -> None:
        package = json.loads((CLI / "package.json").read_text(encoding="utf-8"))

        self.assertEqual(package["name"], "type-mcp-api-cli")
        self.assertEqual(package["description"], "Deterministic local structured-spec inspection CLI")
        self.assertEqual(package["bin"]["type-mcp-api-cli"], "./dist/cli.js")
        self.assertTrue((CLI / "src/cli.ts").is_file())
        self.assertTrue((CLI / "test/package-bin.mjs").is_file())

    def test_cli_product_vision_labels_unimplemented_capabilities_as_future(self) -> None:
        vision = (CLI / "docs/product/vision.md").read_text(encoding="utf-8")

        self.assertIn("Future product target", vision)
        self.assertNotIn("It accepts supported API inputs, produces a reviewable secret-free manifest", vision)

    def test_cli_readme_advertises_only_implemented_commands(self) -> None:
        readme = (CLI / "README.md").read_text(encoding="utf-8")

        self.assertIn("metadata --json", readme)
        self.assertIn("inspect --file <path> --json", readme)
        self.assertNotIn("npm install type-mcp-api-cli", readme)
        self.assertNotIn("npx type-mcp-api-cli", readme)
        self.assertNotIn("approval receipt, and project generation commands", readme)

    def test_docs_validator_skips_embedded_dependency_markdown(self) -> None:
        validator = (ROOT / ".agents/scripts/validate_docs.py").read_text(encoding="utf-8")

        self.assertIn('"node_modules" not in path.parts', validator)

    def test_ci_verifies_docs_harness_and_embedded_cli(self) -> None:
        workflow = (ROOT / ".github/workflows/verify.yml").read_text(encoding="utf-8")

        self.assertIn("cli-package", workflow)
        self.assertIn("working-directory: packages/type-mcp-api-cli", workflow)
        self.assertIn("npm run verify", workflow)
        self.assertIn("npm audit --omit=dev --audit-level=high", workflow)


if __name__ == "__main__":
    unittest.main()
