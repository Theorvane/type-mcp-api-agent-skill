---
name: api-to-typemcp
description: Use when turning supplied API sources into a safe TypeMCP project.
version: 0.2.0
category: integration
license: MIT
metadata:
  hermes:
    tags: [mcp, api, openapi, swagger, code-generation, type-mcp]
    related_skills: []
---

# API to TypeMCP

## Overview

This released skill is a complete, bundled generator delivery unit. Its **bundled skill engine** is in `scripts/`, its controlled TypeScript output templates are in `templates/`, and its public TypeMCP runtime constraints are in [references/type-mcp-runtime.md](references/type-mcp-runtime.md).

Generated projects depend only on published `@theorvane/type-mcp@0.2.0`; they never copy TypeMCP source or use local, `file:`, `git:`, `link:`, or private runtime APIs.

## When to use

Use this skill with a **supplied local** OpenAPI 3.x / Swagger 2.0 JSON/YAML file, supplied Swagger UI HTML, or supplied Markdown/HTML API reference. Do not use it to crawl a bare origin, infer undocumented operations, make mutating calls by default, or publish without explicit final confirmation.

## Bundled engine workflow

Run the engine through its installed skill-relative path. Set `SKILL_DIR` to the directory containing this `SKILL.md`; create a **controlled temporary output directory** yourself and keep it empty.

```bash
SKILL_DIR="/absolute/path/to/api-to-typemcp"
SOURCE="/absolute/path/to/supplied-openapi.json"
OUTPUT="$(mktemp -d -t api-to-typemcp-output.XXXXXX)"
STATE="$(mktemp -d -t api-to-typemcp-state.XXXXXX)"
export TYPE_MCP_APPROVAL_STATE_DIR="$STATE"

# 1. Inspect and build the exact secret-free manifest.
python3 "$SKILL_DIR/scripts/api_to_typemcp.py" inspect --file "$SOURCE" --json
python3 "$SKILL_DIR/scripts/api_to_typemcp.py" manifest --file "$SOURCE" --json > manifest.json
DIGEST="$(python3 -c 'import json; print(json.load(open("manifest.json"))["digest"])')"

# 2. Review the manifest, then explicitly approve precisely that digest.
python3 "$SKILL_DIR/scripts/api_to_typemcp.py" approve \
  --file "$SOURCE" --manifest-digest "$DIGEST"

# 3. Render only after approval, with an exact digest confirmation.
python3 "$SKILL_DIR/scripts/api_to_typemcp.py" generate \
  --file "$SOURCE" --output "$OUTPUT" \
  --confirm-manifest-digest "$DIGEST"
```

For supplied Markdown or HTML, add an explicit origin; no page is fetched or crawled:

```bash
python3 "$SKILL_DIR/scripts/api_to_typemcp.py" manifest \
  --file "/absolute/path/to/reference.md" \
  --base-url "https://api.example.test" --json
```

Swagger UI discovery is performed by `inspect` in-memory and returns only an explicit configured spec reference. The user must separately supply that structured spec; do not fetch it automatically.

## Mandatory safety gates

1. **Manifest first.** Treat every source as untrusted. Review canonical secret-free manifest data before generation.
2. **Receipt gate.** `approve` issues a HMAC-protected, digest-bound, single-use receipt. A changed, expired, tampered, or already-consumed receipt stops `generate`.
3. **Output gate.** The output directory must already exist and be empty unless `--replace` is explicitly supplied. Symlinks and `..` traversal are rejected.
4. **Runtime policy.** `GET`/`HEAD`/`OPTIONS` are read operations. `POST`/`PUT`/`PATCH`/`DELETE` are protected writes and require exact known IDs in `TYPE_MCP_ALLOW_PROTECTED_OPERATIONS` **before URL, query, headers, body, authentication, or dispatch**. Unknown methods deny.
5. **Containment.** Verify generated projects in a scrubbed temporary workspace, with no inherited credentials, dependency inspection, no-lifecycle installation, typecheck, tests, build, and local MCP stdio smoke.
6. **Publication.** **Immediately before GitHub publication**, record owner/org, repository name, visibility, and source branch. Resolve the actual checked-out/ref-to-publish branch and stop unless it exactly equals the recorded source branch. Ask for explicit user confirmation before the publication action.

## Runtime compatibility

Read [references/type-mcp-runtime.md](references/type-mcp-runtime.md) before modifying generated TypeScript. Use only `McpServer`, `McpTool`, `createMcpServer`, `startStdioServer`, `zod`, and an explicit `InstanceResolver` from the public contract.

## Verification checklist

- [ ] Source is supplied explicitly; no origin crawling occurred.
- [ ] Manifest is secret-free, evidence-backed, and canonically digested.
- [ ] Digest approval and a valid single-use receipt precede generation.
- [ ] Output target passed the empty/replace and traversal/symlink safety gates.
- [ ] Protected writes are authorized before request construction.
- [ ] Generated project uses published `@theorvane/type-mcp@0.2.0` only.
- [ ] Contained install/typecheck/test/build/MCP smoke passes.
- [ ] Immediately before GitHub publication, user confirms owner/name/visibility/source branch and the resolved branch matches.
