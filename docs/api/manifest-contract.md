# API manifest and CLI contract

**Status:** Approved contract; CLI and skill implementation pending.

The manifest is the CLI-to-skill generation boundary and review artifact. It is JSON-serializable, versioned, and secret-free.

## Invocation stages

The CLI contract exposes four conceptual stages. Names/flags will be fixed in the CLI repository before implementation; the skill must not infer them ad hoc.

| Stage | Input | Output | Side-effect rule |
| --- | --- | --- | --- |
| `inspect` | source descriptor | source provenance and safe diagnostics | no generated files, no upstream API calls |
| `manifest` | inspected source | validated versioned manifest | no generated files |
| `generate` | approved manifest + empty output path | rendered project and generation metadata | no GitHub publication |
| `metadata` | CLI executable | CLI/protocol/schema compatibility data | read-only |

## Required top-level manifest fields

| Field | Meaning |
| --- | --- |
| `manifestVersion` | Version of this contract |
| `cliProtocolVersion` | CLI request/output protocol compatibility value |
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
| A: compatible CLI and valid OpenAPI operation | CLI normalizes method/path/input/auth evidence with `high` confidence |
| A: Markdown endpoint and request example | CLI adds a candidate with document citation and stated confidence; skill requests approval |
| E: incompatible CLI/protocol/schema version | Skill stops before manifest review/generation and reports a safe compatibility error |
| E: conflicting method/path evidence | CLI records warning and requires manifest correction; skill does not generate until approved |
| E: malformed JSON/YAML | CLI reports safe parse failure and retains no partial executable operation |
| X: credential appears in source text | CLI redacts the value from manifest/log output and emits a warning |
| X: no reliable endpoint evidence | CLI does not invent an operation or crawl a bare base URL |
| X: unapproved document-derived manifest | Skill does not invoke `generate`, install output dependencies, smoke-test, or publish |

## Approval rules

- Markdown/HTML-derived candidate operations cannot be generated until a user explicitly approves the reviewed manifest.
- Users may exclude operations, edit names/policy/auth mapping, or request another intake pass before approval.
- Any manifest change after approval invalidates approval until re-reviewed.
- The skill records the approved manifest hash, CLI version, manifest version, and protocol version together.
