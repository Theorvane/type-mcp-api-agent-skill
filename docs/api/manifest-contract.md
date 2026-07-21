# API manifest contract

**Status:** Approved contract; implementation pending.

The manifest is the generation boundary and review artifact. It is JSON-serializable, versioned, and secret-free.

## Required top-level fields

| Field | Meaning |
| --- | --- |
| `manifestVersion` | Version of this contract |
| `source` | Kind, URL/path identifier, media type, retrieval time, and SHA-256 content hash |
| `baseUrl` | Resolved API base URL or an explicit unresolved state |
| `operations` | Candidate/approved operations |
| `authentication` | Secret-free environment-variable mapping hints |
| `warnings` | Ambiguities, unsupported constructs, and safety concerns |

## Operation fields

| Field | Meaning |
| --- | --- |
| `id` | Stable generated tool/operation identifier |
| `method` | HTTP method in uppercase |
| `path` | Relative endpoint path |
| `summary` | Human-readable name/description |
| `input` | Parameters/request-body schema and required fields |
| `responses` | Known response shapes or documented examples |
| `policy` | `read`, `protected-write`, or explicit deny/allow override |
| `evidence` | Source URL plus exact source location/snippet reference |
| `confidence` | `high`, `medium`, or `low` with a reason |
| `status` | `candidate`, `approved`, `excluded`, or `unsupported` |

## Acceptance / Error / Exclusion cases

| Case | Expected behavior |
| --- | --- |
| A: valid OpenAPI operation | Normalize method/path/input/auth evidence with `high` confidence |
| A: Markdown endpoint and request example | Add a candidate with document citation and stated confidence |
| E: conflicting method/path evidence | Record warning and require manifest correction; do not generate until approved |
| E: malformed JSON/YAML | Report safe parse failure and retain no partial executable operation |
| X: credential appears in source text | Redact the value from manifest/log output and emit a warning |
| X: no reliable endpoint evidence | Do not invent an operation or crawl a bare base URL |

## Approval rules

- Markdown/HTML-derived candidate operations cannot be generated until a user explicitly approves the reviewed manifest.
- Users may exclude operations, edit names/policy/auth mapping, or request another intake pass before approval.
- Any manifest change after approval invalidates approval until re-reviewed.
