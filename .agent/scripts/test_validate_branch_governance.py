#!/usr/bin/env python3
"""Regression tests for the branch-governance validator."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ".agent/scripts/validate_branch_governance.py"
WORKFLOW = ".github/workflows/verify.yml"


class BranchGovernanceValidatorTests(unittest.TestCase):
    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", VALIDATOR],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_accepts_dev_integration_and_main_release_coverage(self) -> None:
        result = self.run_validator(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_workflow_without_dev_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied_root = Path(directory) / "repo"
            shutil.copytree(ROOT, copied_root, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
            workflow = copied_root / WORKFLOW
            content = workflow.read_text(encoding="utf-8")
            self.assertIn("branches: [dev, main]", content)
            workflow.write_text(
                content.replace("branches: [dev, main]", "branches: [main]"),
                encoding="utf-8",
            )
            result = self.run_validator(copied_root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
