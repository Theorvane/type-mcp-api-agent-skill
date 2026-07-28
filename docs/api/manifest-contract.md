# API manifest and embedded-engine contract

**Status:** Executable bundled-engine contract implemented; release publication is separate.

The manifest is the **bundled skill engine** review boundary. It is versioned, JSON-serializable, secret-free, schema-validated, and canonically hashed. Persisted/displayed source identifiers and evidence are sanitized under `docs/guides/security-and-publication.md`; original URLs, redirects, local paths, credentials, and raw private diagnostics are never manifest fields.

The manifest is not an approval credential. A document-derived manifest becomes generation-eligible only with a separate engine-issued receipt held in isolated state and bound to the reviewed digest. The engine renders projects that use published `@theorvane/type-mcp`, never a local or copied TypeMCP implementation.

## Engine stages

| Stage | Input | Output | Side-effect rule |
| --- | --- | --- | --- |
| `inspect` | supplied source descriptor | sanitized provenance and safe diagnostics | no generated files or upstream API calls |
| `manifest` | inspected source | validated manifest and deterministic digest | no generated files |
| `approve` | engine state and exact digest | engine-issued isolated HMAC receipt | no generated files or upstream API calls |
| `generate` | eligible manifest, valid receipt if required, confirmed output path | rendered project and generation metadata | local output only; no GitHub publication |
| `verify` | generated project copy | contained static/install/test evidence | no live upstream without separate approval |

The entrypoint is `skills/api-to-typemcp/scripts/api_to_typemcp.py`. It exposes `inspect`, `manifest`, `approve`, and `generate` for supplied local sources. `manifest` emits canonical JSON including `digest`; `approve --manifest-digest <digest>` issues the single-use receipt; `generate --confirm-manifest-digest <digest> --output <existing-empty-dir>` consumes it and renders the stdio project. Markdown/HTML requires an explicit `--base-url`; supplied Swagger UI HTML is inspected in-memory only and its configured structured spec must then be supplied separately. These commands never fetch/crawl an origin or publish GitHub output.

## Implemented manifest and digest

The current manifest is a normalized JSON object with `schema`, `version`, `protocol`, `source`, `baseUrl`, `operations`, `authentication`, and `digest`. `warnings` may be present only when intake produces normalized warnings; it is not a required top-level field. Intake rejects duplicate JSON/YAML keys, non-finite numbers, malformed Unicode, unsafe nesting/aliases, and unsupported source shapes before construction.

`digest` is lowercase `sha256:<hex>` over deterministic compact UTF-8 JSON: sorted keys, no insignificant whitespace, `ensure_ascii=False`, and no non-finite numbers. It covers every manifest field except `digest` itself. This is an engine-specific deterministic encoding; it is **not** a claim of RFC 8785/JCS conformance.

## Implemented receipt gate

Every `generate` invocation requires its exact current digest in `--confirm-manifest-digest` and an approval receipt from `approve --manifest-digest <digest>`. The receipt is held in isolated process-owned state and contains only `manifest_digest`, `issued_at`, `expires_at`, `nonce`, and HMAC `hmac`.

Validation recomputes the HMAC over the digest, times, and nonce using the state-local secret; it requires the matching digest, a readable unexpired receipt, and valid integrity data. A successful generation removes the receipt, making it single-use. A copied or edited manifest cannot use a receipt bound to a different digest; a receipt is not an audit record, a challenge protocol, or a publication authorization.

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
