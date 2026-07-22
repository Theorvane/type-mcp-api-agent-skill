# Task brief: 3 — inspect local structured API specifications

**Status:** in-progress
**Issue:** https://github.com/Theorvane/type-mcp-api-cli/issues/3
**Branch:** `feat/3-inspect-local-spec`

## Goal

Add a deterministic, local-only `inspect --file <path> --json` command for OpenAPI 3.x and Swagger 2.0 JSON/YAML sources.

## Boundaries

- Input is a local file only; no network requests.
- Output contains no raw path, source text, stack trace, or credential value.
- No manifest, approval, generation, or output-file creation.
- Unsupported/malformed input returns a stable safe error.

## Acceptance cases

| Case | Expected result |
| --- | --- |
| OpenAPI 3.x JSON | `openapi` classification, version, JSON media type, SHA-256 content hash, opaque local ID, and operation count |
| Swagger 2.0 YAML | `swagger` classification, version, YAML media type, SHA-256 content hash, opaque local ID, and operation count |
| malformed or unsupported input | stable safe error without path/body content |

## RED evidence

| local structured spec | `npm test -- --run test/inspect.test.ts test/cli.test.ts` | RED: missing `src/inspect.ts`, then unsupported CLI invocation exited `64`; GREEN: 5 focused tests passed. |
