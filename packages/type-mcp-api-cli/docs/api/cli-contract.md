# CLI and manifest API contract

**Status:** Implemented for `metadata --json`, local structured-spec `inspect`, and schema artifact publication.

## Metadata command

```text
type-mcp-api-cli metadata --json
```

It exits `0` and writes exactly one JSON object to stdout:

```json
{
  "packageName": "type-mcp-api-cli",
  "cliProtocolVersion": 1,
  "manifestVersions": [1],
  "commands": ["inspect", "metadata"]
}
```

## Local structured-spec inspection

```text
type-mcp-api-cli inspect --file <path> --json
```

The command accepts only local `.json`, `.yaml`, and `.yml` files. It parses and classifies either OpenAPI `3.x` (`kind: "openapi"`) or Swagger `2.0` (`kind: "swagger"`). The source is not uploaded, and the command does not make network requests or generate files.

A successful result exits `0` and writes exactly one secret-free JSON object with:

| Field | Meaning |
| --- | --- |
| `kind` | `openapi` or `swagger` |
| `declaredVersion` | The document's OpenAPI/Swagger version |
| `mediaType` | `application/json` or `application/yaml` |
| `contentHash` | Lowercase `sha256:<hex>` of local source bytes |
| `opaqueLocalId` | `local:sha256:<hex>` derived from the resolved local source identity; never the path itself |
| `operationCount` | Number of recognized HTTP operation keys in `paths` |

Malformed files exit `65` with `{ "ok": false, "error": { "code", "message" } }`. Supported stable codes are `SOURCE_UNREADABLE`, `SOURCE_PARSE_FAILED`, and `UNSUPPORTED_STRUCTURED_SPEC`. Errors do not contain the path, source body, credentials, or stack trace. Unsupported argument shapes exit `64` with a safe usage string.

This inspection stage does not validate an eventual manifest, resolve `$ref`, normalize endpoint parameters, extract authentication, or create a manifest/challenge/receipt.

## Published schema

`schemas/api-manifest-1.schema.json` is the closed manifest v1 artifact. Future implementations must validate an input manifest against the exact schema version before applying RFC 8785/JCS hashing, approval challenge creation, receipt issuance, or generation.

The staged contract (`manifest`, `approve`, `generate`) is approved design but not yet implemented.
