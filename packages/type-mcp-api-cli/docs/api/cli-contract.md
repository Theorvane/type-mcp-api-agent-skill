# CLI and manifest API contract

**Status:** Implemented for `metadata --json`, local structured-spec `inspect`, schema artifact publication, manifest v1 validation, and canonical-digest computation.

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

This inspection stage does not construct a manifest, resolve `$ref`, normalize endpoint parameters, extract authentication, or create a manifest/challenge/receipt. The exported manifest-contract API separately validates an already supplied v1 manifest and computes its digest.

## Manifest validation and canonical digest API

`schemas/api-manifest-1.schema.json` is a closed manifest v1 artifact. The package exports:

- `canonicalizeJson(value)` for side-effect-free RFC 8785/JCS-compatible canonical JSON serialization of JSON-representable values;
- `computeManifestDigest(value)` to validate an unknown v1 manifest and compute lowercase `sha256:<hex>` over exactly `manifestVersion`, `cliProtocolVersion`, `source`, `baseUrl`, `operations`, `authentication`, and `warnings`;
- `validateManifestV1(value)` to additionally require that top-level `manifestDigest` exactly matches the computed value.

All contract failures return a fixed safe code/message pair: `MANIFEST_SCHEMA_INVALID`, `MANIFEST_DIGEST_MISMATCH`, or `CANONICALIZATION_FAILED`. These library APIs do not persist data, issue challenges/receipts, construct a manifest from an API source, or generate files.

The staged CLI commands (`manifest`, `approve`, `generate`) remain approved design but are not implemented.
