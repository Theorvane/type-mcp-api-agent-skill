"""Manifest contract tests exercise the script by absolute path, not package imports."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
ENTRYPOINT = SKILL_DIR / "scripts" / "api_to_typemcp.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def manifest_for(name: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(ENTRYPOINT), "manifest", "--file", str(FIXTURES / name), "--json"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def canonical_without_digest(manifest: dict[str, object]) -> bytes:
    value = dict(manifest)
    value.pop("digest", None)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class ManifestTests(unittest.TestCase):
    def test_openapi_manifest_is_normalized_deterministic_and_secret_free(self) -> None:
        first = manifest_for("petstore.openapi.json")
        second = manifest_for("petstore.openapi.json")

        self.assertEqual(first, second)
        self.assertEqual(first["schema"], "api-to-typemcp.manifest")
        self.assertEqual(first["version"], 1)
        self.assertEqual(first["protocol"], "http")
        self.assertEqual(first["source"]["kind"], "openapi")
        self.assertEqual(first["source"]["descriptor"], "petstore.openapi.json")
        self.assertEqual(first["baseUrl"], "https://api.example.test/v1")
        self.assertEqual(
            first["digest"],
            "sha256:" + hashlib.sha256(canonical_without_digest(first)).hexdigest(),
        )

        operations = {operation["operationId"]: operation for operation in first["operations"]}
        self.assertEqual(set(operations), {"getPet", "createPet"})
        self.assertEqual(operations["getPet"]["method"], "GET")
        self.assertEqual(operations["getPet"]["path"], "/pets/{petId}")
        self.assertEqual(operations["getPet"]["policy"], "read")
        self.assertEqual(operations["getPet"]["parameters"][0]["name"], "petId")
        self.assertEqual(operations["createPet"]["method"], "POST")
        self.assertEqual(operations["createPet"]["policy"], "protected-write")
        self.assertTrue(operations["createPet"]["requestBody"]["required"])
        self.assertEqual(operations["createPet"]["responses"][0]["status"], "201")

        rendered = json.dumps(first, sort_keys=True)
        self.assertNotIn("fixture-secret-query", rendered)
        self.assertNotIn(str(FIXTURES), rendered)
        self.assertNotIn("?api_key=", rendered)

    def test_swagger_yaml_normalizes_to_the_same_operation_contract(self) -> None:
        manifest = manifest_for("petstore.swagger.yaml")

        self.assertEqual(manifest["source"]["kind"], "swagger")
        self.assertEqual(manifest["baseUrl"], "https://api.example.test/v1")
        operations = {operation["operationId"]: operation for operation in manifest["operations"]}
        self.assertEqual(operations["getPet"]["policy"], "read")
        self.assertEqual(operations["createPet"]["policy"], "protected-write")
        self.assertEqual(operations["createPet"]["requestBody"]["contentType"], "application/json")

    def test_manifest_rejects_secret_bearing_or_unsafe_operation_values(self) -> None:
        unsafe = {
            "openapi": "3.0.0",
            "servers": [{"url": "https://api.example.test"}],
            "paths": {
                "/pets?token=source-secret": {
                    "get": {
                        "operationId": "getPet",
                        "responses": {"200": {"description": "response-secret"}},
                    }
                }
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsafe.json"
            path.write_text(json.dumps(unsafe), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ENTRYPOINT), "manifest", "--file", str(path), "--json"],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("source-secret", result.stderr)
        self.assertNotIn("response-secret", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
