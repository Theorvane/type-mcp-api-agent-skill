"""Black-box tests for the bundled local structured-spec entry point."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
ENTRYPOINT = SKILL_DIR / "scripts" / "api_to_typemcp.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def run_engine(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ENTRYPOINT), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class EngineCliTests(unittest.TestCase):
    def test_inspect_accepts_explicit_local_openapi_file(self) -> None:
        result = run_engine("inspect", "--file", str(FIXTURES / "petstore.openapi.json"), "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["source"]["kind"], "openapi")
        self.assertEqual(payload["operationCount"], 2)
        self.assertNotIn(str(FIXTURES), result.stdout)
        self.assertNotIn("fixture-secret-query", result.stdout)

    def test_rejects_malformed_and_unsupported_local_documents_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            malformed = Path(directory) / "bad.json"
            malformed.write_text("{not json", encoding="utf-8")
            unsupported = Path(directory) / "unsupported.json"
            unsupported.write_text('{"openapi":"3.1.0","paths":{}}', encoding="utf-8")
            malformed_base_url = Path(directory) / "malformed-base-url.json"
            malformed_base_url.write_text(
                '{"openapi":"3.0.0","servers":[{"url":"https://api.example.test:bad"}],"paths":{}}',
                encoding="utf-8",
            )

            for path in (malformed, unsupported, malformed_base_url):
                result = run_engine("inspect", "--file", str(path), "--json")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("error:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
