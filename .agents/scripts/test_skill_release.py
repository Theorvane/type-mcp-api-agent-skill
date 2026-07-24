#!/usr/bin/env python3
"""Contract tests for versioned skill release automation."""

from __future__ import annotations

import os
import re
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/api-to-typemcp/SKILL.md"
WORKFLOW = ROOT / ".github/workflows/skill-release.yml"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")


class SkillReleaseTests(unittest.TestCase):
    def test_skill_frontmatter_declares_a_semver_release_version(self) -> None:
        content = SKILL.read_text(encoding="utf-8")
        match = re.search(r"^version:\s*([^\s#]+)\s*$", content, re.MULTILINE)
        self.assertIsNotNone(match, "SKILL.md must declare a frontmatter version")
        assert match is not None
        self.assertRegex(match.group(1), SEMVER)

    def test_version_extraction_step_executes_and_writes_outputs(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        match = re.search(
            r"Read and validate the skill version\n\s+id: version\n\s+run: \|\n(?P<script>(?: {10}.*\n)+)",
            workflow,
        )
        self.assertIsNotNone(match, "workflow must include the version extraction step")
        assert match is not None
        python = re.search(
            r"python3 - <<'PY'\n(?P<body>.*?)^\s{10}PY$",
            workflow,
            re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(python, "version extraction must use an executable Python heredoc")
        assert python is not None
        script = textwrap.dedent(python.group("body"))

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "github-output"
            previous_output = os.environ.get("GITHUB_OUTPUT")
            previous_cwd = Path.cwd()
            try:
                os.environ["GITHUB_OUTPUT"] = str(output_path)
                os.chdir(ROOT)
                exec(script, {"__name__": "__main__"})
            finally:
                os.chdir(previous_cwd)
                if previous_output is None:
                    os.environ.pop("GITHUB_OUTPUT", None)
                else:
                    os.environ["GITHUB_OUTPUT"] = previous_output

            self.assertEqual(output_path.read_text(encoding="utf-8"), "skill_version=0.1.0\ntag=v0.1.0\n")

    def test_main_push_release_workflow_uses_the_skill_version_for_every_artifact(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("push:", workflow)
        self.assertIn("branches: [main]", workflow)
        self.assertIn("skills/api-to-typemcp/SKILL.md", workflow)
        self.assertIn("SKILL_VERSION", workflow)
        self.assertIn('tag=v{version}', workflow)
        self.assertIn("gh release create", workflow)
        self.assertIn('--target "$GITHUB_SHA"', workflow)
        self.assertIn("--version", workflow)
        self.assertIn('"$SKILL_VERSION"', workflow)

    def test_registry_token_is_required_before_tag_or_release_side_effects(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        token_check = workflow.index("CLAWHUB_TOKEN")
        release_mutation = workflow.index("gh release create")
        self.assertLess(token_check, release_mutation)
        self.assertIn("secrets.CLAWHUB_TOKEN", workflow)


if __name__ == "__main__":
    unittest.main()
