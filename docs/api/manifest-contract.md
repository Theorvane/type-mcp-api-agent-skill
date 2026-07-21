# API manifest and CLI contract

**Status:** Approved contract; CLI and skill implementation pending.

The manifest is the CLI-to-skill generation boundary and review artifact. It is JSON-serializable, versioned, secret-free, and canonicalized before hashing. All persisted/displayed source identifiers and evidence are sanitized under `docs/guides/security-and-publication.md`; original URLs, redirects, local paths, credentials, and raw private diagnostics are never manifest fields.

## Invocation stages

The CLI contract exposes four conceptual stages. Names/flags will be fixed in the CLI repository before implementation; the skill must not infer them ad hoc.

| Stage | Input | Output | Side-effect rule |
| --- | --- | --- | --- |
| `inspect` | source descriptor | source provenance and safe diagnostics | no generated files, no upstream API calls |
| `manifest` | inspected source | validated versioned manifest | no generated files |
| `generate` | eligible manifest + empty output path | rendered project and generation metadata | no GitHub publication |
| `metadata` | CLI executable | CLI/protocol/schema compatibility data | read-only |

## Required top-level manifest fields

| Field | Meaning |
| --- | --- |
| `manifestVersion` | Version of this contract |
| `cliProtocolVersion` | CLI request/output protocol compatibility value |
| `source` | Sanitized source kind, origin host, normalized path or opaque local ID, media type, retrieval time, and SHA-256 content hash |
| `baseUrl` | Sanitized resolved API base URL or an explicit unresolved state |
| `operations` | Candidate/approved/excluded operations |
| `authentication` | Secret-free environment-variable mapping hints |
| `warnings` | Ambiguities, unsupported constructs, and safety concerns |
| `approval` | Approval state bound to the exact canonical manifest digest |

`source.kind` is exactly one of `openapi`, `swagger`, `swagger-ui`, `markdown`, or `html`. A manifest is **document-derived** when `source.kind` is `markdown` or `html`, or when any operation's `evidence.kind` is `markdown` or `html`.

## Canonical digest and approval object

The CLI canonicalizes the manifest payload excluding the `approval` object, serializes it deterministically, and computes `manifestDigest` as `sha256:<hex>`. The digest is included in `approval.manifestDigest`; it cannot be supplied independently of the reviewed payload.

| Approval field | Meaning |
| --- | --- |
| `state` | Exactly `not-required`, `pending`, or `approved` |
| `manifestDigest` | Canonical digest of the manifest payload excluding `approval` |
| `manifestVersion` | Contract version reviewed by the user |
| `cliProtocolVersion` | CLI protocol version that produced the reviewed manifest |
| `approvedAt` | RFC 3339 timestamp; required only when state is `approved` |
| `approvalMethod` | `explicit-user-confirmation`; required only when state is `approved` |

Rules:

1. A structured-only manifest begins as `not-required`.
2. A document-derived manifest begins as `pending`, even if its operations are manually marked `approved`.
3. The skill may change a document-derived approval from `pending` to `approved` only after explicit user confirmation of that exact `manifestDigest`.
4. The CLI `generate` stage rejects every document-derived manifest unless `approval.state` is `approved` and all approval fields match the current manifest version, protocol version, and canonical digest.
5. Any content change recomputes the digest and resets `approval` to `pending` for document-derived manifests. A stale approval is invalid.

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

## Normative execution-policy derivation

`policy` has exactly `{ "mode": "read" | "protected-write" | "deny", "origin": "derived" | "approved-override", "reason": string }`.

| HTTP method | Derived mode |
| --- | --- |
| `GET`, `HEAD`, `OPTIONS` | `read` |
| `POST`, `PUT`, `PATCH`, `DELETE` | `protected-write` |
| Any other/unknown method | `deny` |

The CLI must derive this table before source semantics, operation names, or documentation prose are considered. A parser must never derive a mutating method as `read`.

Changing the derived mode requires a visible manifest edit with `origin: approved-override`, a non-empty reason, and the same document-derived approval flow when applicable. The generated runtime evaluates policy before constructing or dispatching an upstream request. `deny` returns a safe MCP error and sends no upstream request.

## Acceptance / Error / Exclusion cases

| Case | Expected behavior |
| --- | --- |
| A: compatible CLI and valid OpenAPI operation | CLI normalizes method/path/input/auth evidence with `high` confidence and derives normative policy |
| A: Markdown endpoint and request example | CLI adds a `candidate` with document evidence and sets approval to `pending` |
| A: explicit approval of current document manifest | Skill records `approved` binding to the exact digest/version/protocol; CLI may generate |
| E: incompatible CLI/protocol/schema version | Skill stops before manifest review/generation and reports a safe compatibility error |
| E: conflicting method/path evidence | CLI records warning and requires manifest correction; skill does not generate until eligible |
| E: malformed JSON/YAML | CLI reports safe parse failure and retains no partial executable operation |
| X: credential appears in source text | CLI redacts the value from manifest/log output and emits a warning |
| X: no reliable endpoint evidence | CLI does not invent an operation or crawl a bare base URL |
| X: stale/unbound document approval | CLI rejects generation; skill requests review of the current digest |
| X: unknown HTTP method | CLI derives `deny`; generated runtime sends no upstream request |
