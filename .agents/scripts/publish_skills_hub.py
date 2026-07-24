#!/usr/bin/env python3
"""Publish a versioned SKILL.md to skills-hub.ai without exposing credentials."""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})
MAX_ATTEMPTS = 3


def auth_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
        "X-Skills-Hub-Client": "github-actions",
    }


def retry_delay(status: int, retry_after: str | None, attempt: int) -> float:
    if status == 429 and retry_after is not None:
        try:
            return min(10.0, max(0.0, float(retry_after)))
        except ValueError:
            pass
    return min(10.0, float(2**attempt))


def version_exists(versions: object, version: str) -> bool:
    return isinstance(versions, list) and any(
        isinstance(item, dict) and item.get("version") == version for item in versions
    )


def publication_state(payload: object) -> str:
    return payload.get("status", "UNKNOWN") if isinstance(payload, dict) else "UNKNOWN"


def category_exists(payload: object, category: str) -> bool:
    if isinstance(payload, list):
        return any(category_exists(item, category) for item in payload)
    if isinstance(payload, dict):
        if payload.get("slug") == category:
            return True
        return any(category_exists(value, category) for value in payload.values())
    return False


def field(content: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:\s*([^\n#]+?)\s*$", content, re.MULTILINE)
    if match is None:
        raise SystemExit(f"SKILL.md frontmatter must declare {name}.")
    return match.group(1).strip().strip('"')


def request(
    api: str,
    token: str,
    path: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    retry: bool = True,
) -> tuple[int, object | None]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    for attempt in range(MAX_ATTEMPTS):
        req = Request(
            f"{api.rstrip('/')}{path}",
            data=data,
            method=method,
            headers=auth_headers(token),
        )
        try:
            with urlopen(req, timeout=30) as response:
                raw = response.read()
                return response.status, json.loads(raw) if raw else None
        except HTTPError as error:
            raw = error.read()
            try:
                body: object | None = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                body = None
            if not retry or error.code not in RETRYABLE_STATUSES or attempt == MAX_ATTEMPTS - 1:
                return error.code, body
            time.sleep(retry_delay(error.code, error.headers.get("Retry-After"), attempt))
        except URLError as error:
            if not retry or attempt == MAX_ATTEMPTS - 1:
                raise SystemExit(f"skills-hub.ai request failed: {error.reason}") from error
            time.sleep(retry_delay(503, None, attempt))
    raise AssertionError("retry loop exhausted without returning")


def require_published(skill: object, version: str) -> None:
    if publication_state(skill) != "PUBLISHED":
        raise SystemExit(
            f"skills-hub.ai submission is {publication_state(skill)}; refusing to claim a public release."
        )
    if not isinstance(skill, dict) or skill.get("latestVersion") != version:
        raise SystemExit("skills-hub.ai public skill does not expose the released version.")


def publish() -> None:
    token = os.environ.get("SKILLS_HUB_AI_API_KEY", "")
    if not token:
        raise SystemExit("Missing required repository secret SKILLS_HUB_AI_API_KEY.")
    api = os.environ.get("SKILLS_HUB_AI_API", "https://api.skills-hub.ai/api/v1")
    content = Path("skills/api-to-typemcp/SKILL.md").read_text(encoding="utf-8")
    name = field(content, "name")
    description = field(content, "description")
    version = field(content, "version")
    category = field(content, "category")
    if version != os.environ.get("SKILL_VERSION"):
        raise SystemExit("SKILL.md version does not match the release version.")

    status, categories = request(api, token, "/categories/")
    if status != 200 or not category_exists(categories, category):
        raise SystemExit("skills-hub.ai does not recognize the SKILL.md category.")

    status, skill = request(api, token, f"/skills/{name}")
    if status == 404:
        status, created = request(
            api,
            token,
            "/skills",
            "POST",
            {
                "name": name,
                "description": description,
                "version": version,
                "categorySlug": category,
                "platforms": ["CLAUDE_CODE"],
                "instructions": content.split("---", 2)[-1].strip(),
                "visibility": "PUBLIC",
                "tags": ["mcp", "api", "openapi", "swagger", "type-mcp"],
                "githubRepoUrl": f"https://github.com/{os.environ['GITHUB_REPOSITORY']}",
            },
            retry=False,
        )
        if status in RETRYABLE_STATUSES:
            status, created = request(api, token, f"/skills/{name}")
        if status not in (200, 201) or not isinstance(created, dict) or not isinstance(created.get("slug"), str):
            raise SystemExit(f"skills-hub.ai skill creation failed (HTTP {status}).")
        name = created["slug"]
        status, published = request(api, token, f"/skills/{name}/publish", "POST", {}, retry=False)
        if status in RETRYABLE_STATUSES:
            status, published = request(api, token, f"/skills/{name}")
        if status not in (200, 201):
            raise SystemExit(f"skills-hub.ai skill publication failed (HTTP {status}).")
        require_published(published, version)
    elif status == 200:
        status, versions = request(api, token, f"/skills/{name}/versions")
        if status != 200:
            raise SystemExit(f"skills-hub.ai version lookup failed (HTTP {status}).")
        if not version_exists(versions, version):
            status, _ = request(
                api,
                token,
                f"/skills/{name}/versions",
                "POST",
                {
                    "version": version,
                    "instructions": content.split("---", 2)[-1].strip(),
                    "changelog": f"Released from GitHub {os.environ['GITHUB_SHA']}.",
                },
                retry=False,
            )
            if status in RETRYABLE_STATUSES:
                status, recovered_versions = request(api, token, f"/skills/{name}/versions")
                if status == 200 and version_exists(recovered_versions, version):
                    status = 200
            if status not in (200, 201):
                raise SystemExit(f"skills-hub.ai version publication failed (HTTP {status}).")
    else:
        raise SystemExit(f"skills-hub.ai skill lookup failed (HTTP {status}).")

    status, public_skill = request(api, token, f"/skills/{name}")
    if status != 200:
        raise SystemExit(f"skills-hub.ai public verification failed (HTTP {status}).")
    require_published(public_skill, version)
    print(f"Published {name} v{version} to skills-hub.ai.")


if __name__ == "__main__":
    publish()
