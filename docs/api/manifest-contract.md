# API manifest and embedded-engine contract

**Status:** Contract approved; bundled-engine implementation is staged.

The manifest is the **bundled skill engine** review boundary. It is versioned, JSON-serializable, secret-free, schema-validated, and canonically hashed. Persisted/displayed source identifiers and evidence are sanitized under `docs/guides/security-and-publication.md`; original URLs, redirects, local paths, credentials, and raw private diagnostics are never manifest fields.

The manifest is not an approval credential. A document-derived manifest becomes generation-eligible only with a separate engine-issued receipt held in isolated state and bound to the reviewed digest. The engine renders projects that use published `@theorvane/type-mcp`, never a local or copied TypeMCP implementation.

## Engine stages

| Stage | Input | Output | Side-effect rule |
| --- | --- | --- | --- |
| `inspect` | supplied source descriptor | sanitized provenance and safe diagnostics | no generated files or upstream API calls |
| `manifest` | inspected source | validated manifest plus approval challenge when required | no generated files |
| `approve` | engine state, challenge ID, exact digest, explicit confirmation | engine-issued isolated receipt | no generated files or upstream API calls |
| `generate` | eligible manifest, valid receipt if required, confirmed output path | rendered project and generation metadata | local output only; no GitHub publication |
| `verify` | generated project copy | contained static/install/test evidence | no live upstream without separate approval |

Exact commands are added with the executable engine in later tasks; these stages define its contract and do not claim a current implementation.

## Schema and canonical digest

The schema is closed (`additionalProperties: false`) at every contract object. Unknown fields, duplicate JSON members, non-finite numbers, invalid Unicode, and schema-invalid payloads are rejected before digesting or approval.

The canonical digest algorithm is fixed for a manifest version:

1. Validate the manifest against its exact closed schema.
2. Form the logical digest payload: `manifestVersion`, `engineProtocolVersion`, `source`, `baseUrl`, `operations`, `authentication`, and `warnings`.
3. Serialize with [RFC 8785 JSON Canonicalization Scheme (JCS)](https://www.rfc-editor.org/rfc/rfc8785).
4. Compute SHA-256 over those UTF-8 bytes as lowercase `sha256:<hex>`.
5. Store it as `manifestDigest`.

`manifestDigest`, `approval`, and receipt bytes/paths are excluded from the digest payload. A copied or edited manifest cannot forge a receipt.

## Required fields and approval

Top-level fields are `manifestVersion`, `engineProtocolVersion`, `manifestDigest`, `source`, `baseUrl`, `operations`, `authentication`, `warnings`, and `approval`. Source kind is exactly `openapi`, `swagger`, `swagger-ui`, `markdown`, or `html`. Markdown/HTML evidence makes a manifest document-derived.

Document-derived approval requires explicit confirmation of the exact current digest. The isolated engine receipt includes its contract version, challenge ID, digest, manifest/engine contract versions, issue/expiry times, confirmation method, and authenticated integrity value. Validation requires the matching state, valid integrity value, current digest/version, unexpired state, and unused receipt; successful generation consumes it.

## Normative execution policy

| HTTP method | Derived mode |
| --- | --- |
| `GET`, `HEAD`, `OPTIONS` | `read` |
| `POST`, `PUT`, `PATCH`, `DELETE` | `protected-write` |
| Other/unknown | `deny` |

`TYPE_MCP_ALLOW_PROTECTED_OPERATIONS` is the sole protected-write grant. Unset, empty, malformed, duplicate, wildcard, method-only, or unknown IDs grant nothing. An exact known operation ID is required, and policy is evaluated before constructing URL, query, headers, body, authentication, or dispatching an upstream request. Unknown methods cannot be overridden from `deny`.

## Acceptance and exclusion cases

- A valid bounded OpenAPI/Swagger source produces a normalized, secret-free manifest for review.
- Markdown/HTML candidates require exact-digest approval and an engine-issued receipt before generation.
- A credential in source text, URL, or diagnostic is redacted or stops processing; it never enters artifacts.
- Missing, stale, used, tampered, or digest-mismatched receipts reject generation.
- Unset/wildcard/unknown protected-write allowlists and unknown methods send no upstream request.
- Generated output depends on published `@theorvane/type-mcp` and is verified only in containment.
