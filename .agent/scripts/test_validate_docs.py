#!/usr/bin/env python3
"""Regression tests for the docs-contract validator."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ".agent/scripts/validate_docs.py"
PUBLICATION_CONFIRMATION = (
    "owner/org, repository name, visibility, and source branch"
)
REF_VERIFICATION = "actual checked-out/ref-to-publish branch"
REF_EQUALITY_STOP = "stop unless it exactly equals the recorded source branch"
BRANCH_GOVERNANCE = "Protected branch flow after bootstrap"


class PublicationContractValidatorTests(unittest.TestCase):
    def assert_validator_fails_after_removal(self, relative_path: str, phrase: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied_root = Path(directory) / "repo"
            shutil.copytree(ROOT, copied_root, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
            target = copied_root / relative_path
            content = target.read_text(encoding="utf-8")
            self.assertIn(phrase, content)
            baseline = subprocess.run(
                ["python3", VALIDATOR],
                cwd=copied_root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
            target.write_text(content.replace(phrase, "REMOVED BY REGRESSION TEST"), encoding="utf-8")
            result = subprocess.run(
                ["python3", VALIDATOR],
                cwd=copied_root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_security_guide_rejects_missing_publication_confirmation(self) -> None:
        self.assert_validator_fails_after_removal(
            "docs/guides/security-and-publication.md", PUBLICATION_CONFIRMATION
        )

    def test_security_guide_rejects_missing_ref_verification(self) -> None:
        self.assert_validator_fails_after_removal(
            "docs/guides/security-and-publication.md", REF_VERIFICATION
        )

    def test_skill_rejects_missing_publication_confirmation(self) -> None:
        self.assert_validator_fails_after_removal(
            "skills/api-to-typemcp/SKILL.md", PUBLICATION_CONFIRMATION
        )

    def test_skill_rejects_missing_ref_verification(self) -> None:
        self.assert_validator_fails_after_removal(
            "skills/api-to-typemcp/SKILL.md", REF_VERIFICATION
        )
    def test_security_guide_rejects_missing_ref_equality_stop(self) -> None:
        self.assert_validator_fails_after_removal(
            "docs/guides/security-and-publication.md", REF_EQUALITY_STOP
        )

    def test_skill_rejects_missing_ref_equality_stop(self) -> None:
        self.assert_validator_fails_after_removal(
            "skills/api-to-typemcp/SKILL.md", REF_EQUALITY_STOP
        )

    def test_agents_rejects_missing_branch_governance(self) -> None:
        self.assert_validator_fails_after_removal("AGENTS.md", BRANCH_GOVERNANCE)


if __name__ == "__main__":
    unittest.main()
