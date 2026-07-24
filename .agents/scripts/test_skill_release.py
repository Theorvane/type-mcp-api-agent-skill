#!/usr/bin/env python3
"""Contract tests for versioned skill release automation."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import tempfile
import textwrap
import unittest
from email.message import Message
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/api-to-typemcp/SKILL.md"
WORKFLOW = ROOT / ".github/workflows/skill-release.yml"
PUBLISHER = ROOT / ".agents/scripts/publish_skills_hub.py"
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


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

            self.assertEqual(output_path.read_text(encoding="utf-8"), "skill_version=0.1.1\ntag=v0.1.1\n")

    def test_version_extraction_step_rejects_invalid_numeric_prerelease_identifiers(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        python = re.search(
            r"python3 - <<'PY'\n(?P<body>.*?)^\s{10}PY$",
            workflow,
            re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(python, "version extraction must use an executable Python heredoc")
        assert python is not None
        script = textwrap.dedent(python.group("body"))
        original = SKILL.read_text(encoding="utf-8")

        for invalid_version in ("0.1.0-01", "0.1.0-alpha.01"):
            with self.subTest(version=invalid_version), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                skill_path = root / "skills/api-to-typemcp/SKILL.md"
                skill_path.parent.mkdir(parents=True)
                skill_path.write_text(
                    original.replace("version: 0.1.1", f"version: {invalid_version}"),
                    encoding="utf-8",
                )
                previous_cwd = Path.cwd()
                previous_output = os.environ.get("GITHUB_OUTPUT")
                try:
                    os.environ["GITHUB_OUTPUT"] = str(root / "github-output")
                    os.chdir(root)
                    with self.assertRaises(SystemExit):
                        exec(script, {"__name__": "__main__"})
                finally:
                    os.chdir(previous_cwd)
                    if previous_output is None:
                        os.environ.pop("GITHUB_OUTPUT", None)
                    else:
                        os.environ["GITHUB_OUTPUT"] = previous_output

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

    def test_skills_hub_ai_publication_is_gated_and_uses_the_released_version(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        content = SKILL.read_text(encoding="utf-8")

        self.assertIsNotNone(
            re.search(r"^category:\s*integration\s*$", content, re.MULTILINE),
            "skills-hub.ai requires an approved category",
        )
        job = re.search(
            r"^  publish-skills-hub-ai:\n(?P<body>.*?)(?=^  \w|\Z)",
            workflow,
            re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(job, "release workflow must publish skills-hub.ai")
        assert job is not None
        body = job.group("body")
        self.assertIn("permissions:\n      contents: read", body)
        self.assertIn("SKILLS_HUB_AI_API_KEY: ${{ secrets.SKILLS_HUB_AI_API_KEY }}", body)
        self.assertTrue(PUBLISHER.is_file())
        self.assertIn("Missing required repository secret SKILLS_HUB_AI_API_KEY", PUBLISHER.read_text(encoding="utf-8"))
        self.assertIn("python3 .agents/scripts/publish_skills_hub.py", body)
        self.assertIn("persist-credentials: false", body)

        secret_gate = workflow.index("Missing required repository secret SKILLS_HUB_AI_API_KEY")
        release_mutation = workflow.index("gh release create")
        self.assertLess(secret_gate, release_mutation)

    def test_skills_hub_publisher_uses_api_key_auth_and_reconciles_versions(self) -> None:
        self.assertTrue(PUBLISHER.is_file(), "skills-hub.ai publisher must be an executable, tested script")
        spec = importlib.util.spec_from_file_location("publish_skills_hub", PUBLISHER)
        self.assertIsNotNone(spec)
        assert spec is not None and spec.loader is not None
        publisher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(publisher)

        self.assertEqual(publisher.auth_headers("test-key")["Authorization"], "ApiKey test-key")
        self.assertEqual(publisher.retry_delay(429, "2", 0), 2.0)
        self.assertEqual(publisher.retry_delay(429, "60", 0), 10.0)
        self.assertGreater(publisher.retry_delay(503, None, 0), 0)
        self.assertTrue(publisher.category_exists({"data": [{"slug": "integration"}]}, "integration"))
        self.assertFalse(publisher.category_exists({"data": [{"slug": "security"}]}, "integration"))
        self.assertTrue(publisher.version_exists([{"version": "0.1.1"}], "0.1.1"))
        self.assertFalse(publisher.version_exists([{"version": "0.1.0"}], "0.1.1"))
        self.assertEqual(publisher.publication_state({"status": "PUBLISHED"}), "PUBLISHED")
        self.assertEqual(publisher.publication_state({"status": "PENDING_REVIEW"}), "PENDING_REVIEW")

    def test_skills_hub_publisher_retries_a_transient_http_failure(self) -> None:
        spec = importlib.util.spec_from_file_location("publish_skills_hub", PUBLISHER)
        assert spec is not None and spec.loader is not None
        publisher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(publisher)

        headers = Message()
        transient = publisher.HTTPError("https://example.invalid", 503, "unavailable", headers, None)

        class Response:
            status = 200

            def read(self) -> bytes:
                return b'{"status":"PUBLISHED"}'

            def __enter__(self) -> "Response":
                return self

            def __exit__(self, *_: object) -> None:
                return None

        with patch.object(publisher, "urlopen", side_effect=[transient, Response()]) as urlopen, patch.object(
            publisher.time, "sleep"
        ) as sleep:
            status, payload = publisher.request("https://example.invalid", "test-key", "/skills/test")

        self.assertEqual(status, 200)
        self.assertEqual(payload, {"status": "PUBLISHED"})
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once()

    def test_only_the_release_job_receives_write_contents_permission(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertNotIn("permissions:\n  contents: write", workflow)
        release = re.search(r"^  release:\n(?P<body>.*?)(?=^  \w|\Z)", workflow, re.DOTALL | re.MULTILINE)
        publish = re.search(
            r"^  publish-clawhub:\n(?P<body>.*?)(?=^  \w|\Z)",
            workflow,
            re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(release)
        self.assertIsNotNone(publish)
        assert release is not None and publish is not None
        self.assertIn("permissions:\n      contents: write", release.group("body"))
        self.assertIn("permissions:\n      contents: read", publish.group("body"))
        self.assertEqual(publish.group("body").count("persist-credentials: false"), 2)


if __name__ == "__main__":
    unittest.main()
