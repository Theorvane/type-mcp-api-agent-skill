#!/usr/bin/env python3
"""Regression tests for the embedded-engine documentation contract."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ".agents/scripts/validate_docs.py"
ACTIVE_SOURCE_DOCS = (
    "AGENTS.md",
    "README.md",
    "docs/product/vision.md",
    "docs/product/mvp-scope.md",
    "docs/architecture/overview.md",
    "docs/api/manifest-contract.md",
    "docs/guides/security-and-publication.md",
    "docs/planning/README.md",
    "skills/api-to-typemcp/SKILL.md",
)
EMBEDDED_ENGINE_PHRASE = "bundled skill engine"
TYPE_MCP_RUNTIME = "@theorvane/type-mcp"
PUBLICATION_CONFIRMATION = "owner/org, repository name, visibility, and source branch"
REF_VERIFICATION = "actual checked-out/ref-to-publish branch"
REF_EQUALITY_STOP = "stop unless it exactly equals the recorded source branch"


class EmbeddedEngineDocumentationValidatorTests(unittest.TestCase):
    def assert_validator_fails_after_removal(self, relative_path: str, phrase: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied_root = Path(directory) / "repo"
            shutil.copytree(ROOT, copied_root, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
            target = copied_root / relative_path
            content = target.read_text(encoding="utf-8")
            self.assertIn(phrase, content)
            baseline = subprocess.run(
                ["python3", VALIDATOR], cwd=copied_root, check=False, capture_output=True, text=True
            )
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
            target.write_text(content.replace(phrase, "REMOVED BY REGRESSION TEST"), encoding="utf-8")
            result = subprocess.run(
                ["python3", VALIDATOR], cwd=copied_root, check=False, capture_output=True, text=True
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_active_source_docs_do_not_direct_cli_resolution_or_installation(self) -> None:
        for relative_path in ACTIVE_SOURCE_DOCS:
            with self.subTest(path=relative_path):
                content = (ROOT / relative_path).read_text(encoding="utf-8").lower()
                self.assertNotIn("type-mcp-api-cli", content)
                self.assertNotIn("cli compatibility", content)

    def test_validator_enforces_embedded_engine_and_published_runtime(self) -> None:
        for relative_path in (
            "AGENTS.md",
            "README.md",
            "docs/architecture/overview.md",
            "docs/api/manifest-contract.md",
            "skills/api-to-typemcp/SKILL.md",
        ):
            with self.subTest(path=relative_path):
                content = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(EMBEDDED_ENGINE_PHRASE, content)
                self.assertIn(TYPE_MCP_RUNTIME, content)

    def test_validator_rejects_removed_embedded_engine_contract(self) -> None:
        self.assert_validator_fails_after_removal("docs/architecture/overview.md", EMBEDDED_ENGINE_PHRASE)

    def test_validator_rejects_removed_published_runtime_contract(self) -> None:
        self.assert_validator_fails_after_removal("docs/api/manifest-contract.md", TYPE_MCP_RUNTIME)

    def test_validator_preserves_publication_confirmation_gates(self) -> None:
        for relative_path, phrase in (
            ("docs/guides/security-and-publication.md", PUBLICATION_CONFIRMATION),
            ("docs/guides/security-and-publication.md", REF_VERIFICATION),
            ("docs/guides/security-and-publication.md", REF_EQUALITY_STOP),
        ):
            with self.subTest(path=relative_path, phrase=phrase):
                self.assert_validator_fails_after_removal(relative_path, phrase)


if __name__ == "__main__":
    unittest.main()
