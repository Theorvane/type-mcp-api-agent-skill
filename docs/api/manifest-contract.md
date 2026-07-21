# API manifest, approval receipt, and CLI contract

**Status:** Approved contract; CLI and skill implementation pending.

The manifest is the CLI-to-skill review boundary. It is versioned, JSON-serializable, secret-free, schema-validated, and canonically hashed. All persisted/displayed source identifiers and evidence are sanitized under `docs/guides/security-and-publication.md`; original URLs, redirects, local paths, credentials, and raw private diagnostics are never manifest fields.

The **manifest is not an approval credential**. A document-derived manifest becomes generation-eligible only with a separate, CLI-issued approval receipt that cryptographically binds the reviewed digest.

## Invocation stages

| Stage | Input | Output | Side-effect rule |
| --- | --- | --- | --- |
| `metadata` | CLI executable | package/protocol/schema metadata | read-only |
| `inspect` | source descriptor | sanitized provenance and safe diagnostics | no generated files, no upstream API calls |
| `manifest` | inspected source | validated manifest plus approval challenge when required | no generated files |
| `approve` | CLI state directory, challenge ID, exact digest, explicit confirmation signal | CLI-issued approval receipt | no generated files or upstream API calls |
| `generate` | eligible manifest, verified receipt if required, empty output path | rendered project and generation metadata | no GitHub publication |

Exact flags are defined in the CLI repository. The skill does not invent stages or bypass them.

## Schema and canonical digest

The CLI publishes a versioned JSON Schema at `schemas/api-manifest-<manifestVersion>.schema.json`; the schema is closed (`additionalProperties: false`) at every contract object. Unknown fields, duplicate JSON object member names, non-finite numbers, invalid Unicode, and schema-invalid payloads are rejected before digesting or approval.

The canonical digest algorithm is fixed for a manifest version:

1. Validate the manifest against its exact versioned closed JSON Schema.
2. Form the **digest payload** with exactly these top-level properties, in this logical set: `manifestVersion`, `cliProtocolVersion`, `source`, `baseUrl`, `operations`, `authentication`, and `warnings`.
3. Serialize that payload using [RFC 8785 JSON Canonicalization Scheme (JCS)](https://www.rfc-editor.org/rfc/rfc8785): ECMAScript number serialization, lexicographically sorted object keys by UTF-16 code units, no insignificant whitespace, and UTF-8 encoding.
4. Compute SHA-256 over those exact UTF-8 bytes and encode as lowercase `sha256:<hex>`.
5. Store the result as the top-level `manifestDigest`.

`manifestDigest`, `approval`, and any receipt path/bytes are excluded from the digest payload. The skill may independently recompute the digest with the same schema/JCS algorithm before displaying it or asking for approval.

## Required top-level manifest fields

| Field | Meaning |
| --- | --- |
| `manifestVersion` | Exact manifest schema/contract version |
| `cliProtocolVersion` | Exact CLI request/output protocol version |
| `manifestDigest` | Digest of the defined canonical payload |
| `source` | Sanitized source kind, origin host, normalized path or opaque local ID, media type, retrieval time, and content hash |
| `baseUrl` | Sanitized resolved API base URL or an explicit unresolved state |
| `operations` | Candidate/approved/excluded operations |
| `authentication` | Secret-free environment-variable mapping hints |
| `warnings` | Ambiguities, unsupported constructs, and safety concerns |
| `approval` | Requirement/challenge metadata; never a mutable approval decision |

`source.kind` is exactly one of `openapi`, `swagger`, `swagger-ui`, `markdown`, or `html`. A manifest is **document-derived** when `source.kind` is `markdown` or `html`, or when any operation's `evidence.kind` is `markdown` or `html`.

## Approval challenge and receipt

### Manifest approval requirement

`approval` has exactly:

| Field | Meaning |
| --- | --- |
| `requirement` | `none` for structured-only input; `explicit-user-confirmation` for document-derived input |
| `challengeId` | Opaque, cryptographically random CLI state identifier; required only for explicit confirmation |
| `challengeExpiresAt` | RFC 3339 expiry; required only for explicit confirmation |
| `manifestDigest` | Must exactly equal the top-level digest |

The CLI state directory is process-owned (`0700`) and contains an unexported per-challenge signing key. The manifest does **not** contain an `approved` state, timestamp, or mutable attestation.

### CLI-issued receipt

After the skill displays the exact digest and receives explicit user confirmation, it invokes CLI `approve` using the isolated state directory, `challengeId`, and digest. The CLI issues a separate receipt containing:

| Field | Meaning |
| --- | --- |
| `receiptVersion` | Receipt contract version |
| `challengeId` | Matches unexpired CLI state |
| `manifestDigest` | Exact digest approved |
| `manifestVersion` | Exact reviewed manifest version |
| `cliProtocolVersion` | Exact reviewed protocol version |
| `issuedAt`, `expiresAt` | RFC 3339 validity window |
| `confirmationMethod` | Exactly `explicit-user-confirmation` |
| `mac` | CLI-generated HMAC over the preceding receipt fields, encoded `base64url` |

The HMAC key remains only in CLI state. `generate` accepts a document-derived manifest only when the receipt is supplied separately and its MAC, challenge state, expiry, digest, manifest version, and protocol version all validate. A copied/edited manifest cannot forge a receipt. The challenge is single-use: successful generation consumes it. Any digest-payload change creates a new challenge and invalidates all existing receipts.

## Operation fields

| Field | Meaning |
| --- | --- |
| `id` | Stable generated tool/operation identifier |
| `method` | HTTP method in uppercase |
| `path` | Relative endpoint path |
| `summary` | Human-readable name/description |
| `input` | Parameters/request-body schema and required fields |
| `responses` | Known response shapes or documented examples |
| `policy` | Normative runtime policy object described below |
| `evidence` | Sanitized source kind, origin/path or opaque ID, and exact redacted location/snippet reference |
| `confidence` | `high`, `medium`, or `low` with a reason |
| `status` | `candidate`, `approved`, `excluded`, or `unsupported` |

## Normative execution-policy derivation and runtime gate

`policy` has exactly `{ "mode": "read" | "protected-write" | "deny", "origin": "derived" | "approved-override", "reason": string }`.

| HTTP method | Derived mode |
| --- | --- |
| `GET`, `HEAD`, `OPTIONS` | `read` |
| `POST`, `PUT`, `PATCH`, `DELETE` | `protected-write` |
| Any other/unknown method | `deny` |

The CLI derives this table before source semantics, operation names, or documentation prose. A parser must never derive a mutating method as `read`.

Generated runtime configuration has one fail-closed allow mechanism:

```text
TYPE_MCP_ALLOW_PROTECTED_OPERATIONS=operation-id-1,operation-id-2
```

- Unset, empty, malformed, duplicate, wildcard (`*`), method-only, or unknown operation IDs grant **no** protected-write permission.
- A protected-write operation executes only when its exact stable `operation.id` occurs once in this parsed allowlist.
- `read` operations remain subject to explicit `deny`; `deny` operations cannot be enabled by environment configuration.
- The runtime validates the allowlist and evaluates policy **before constructing URL, query, headers, body, authentication injection, or dispatching an upstream request**.

Changing a derived mode requires a visible manifest edit with `origin: approved-override`, non-empty `reason`, and (for a document-derived manifest) a newly bound receipt. Overrides cannot convert unknown methods from `deny`.

## Acceptance / Error / Exclusion cases

| Case | Expected behavior |
| --- | --- |
| A: compatible CLI and valid OpenAPI operation | CLI normalizes method/path/input/auth evidence, validates schema/JCS digest, and derives normative policy |
| A: Markdown endpoint and request example | CLI adds a `candidate`, creates an explicit-confirmation challenge, and requires a receipt before generation |
| A: explicit approval of current document manifest | CLI issues a receipt bound to exact digest/version/protocol; CLI may generate once |
| E: incompatible CLI/protocol/schema version | Skill stops before manifest review/generation and reports a safe compatibility error |
| E: malformed or non-canonical manifest | CLI rejects before challenge, receipt, or generation |
| E: expired/used/tampered receipt | CLI rejects generation and requires a new manifest approval flow |
| X: credential appears in source text/URL/diagnostic | CLI sanitizes/redacts or stops; no secret enters manifest/log output |
| X: no reliable endpoint evidence | CLI does not invent an operation or crawl a bare base URL |
| X: unset/wildcard/unknown protected-write allowlist | Generated runtime sends no upstream request |
| X: unknown HTTP method | CLI derives `deny`; generated runtime sends no upstream request |
