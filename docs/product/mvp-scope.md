# MVP scope

**Status:** Approved scope; implementation pending.

## Product ownership

| Concern | `type-mcp-api-cli` | `type-mcp-api-agent` |
| --- | --- | --- |
| Parse, normalize, diagnose, render | Owns | Invokes only |
| CLI install/version compatibility | Publishes versioned contract | Resolves/verifies before invocation |
| API-source manifest | Produces | Displays, obtains approvals, stores approved artifact safely |
| Generated-project checks | Emits deterministic metadata | Runs independent verification gates |
| GitHub output repository creation/push | Does not perform | Performs only after explicit final confirmation |

## Included

| Capability | MVP boundary |
| --- | --- |
| CLI input | OpenAPI 3.x / Swagger 2.0 JSON/YAML URL or local file, Swagger UI URL, or Markdown/HTML documentation URL |
| CLI output | Versioned secret-free manifest, diagnostics, and a rendered standalone TypeScript project |
| Skill intake | Validate source choice, resolve compatible CLI, and call staged CLI commands |
| Swagger UI | CLI discovers an underlying JSON/YAML specification from supplied UI page/config or known spec references |
| Markdown/HTML docs | CLI extracts evidence-backed candidate operations from supplied documentation URLs |
| Approval | Skill requires explicit manifest approval before CLI generation from Markdown/HTML-derived operations |
| Code generation | CLI renders a standalone TypeScript project whose dependencies include the npm `type-mcp` package |
| Endpoint coverage | CLI generates a tool for every approved endpoint, including mutating methods |
| Execution policy | Generated runtime controls read/write endpoint execution, defaulting to protected mutations |
| Authentication | Environment-variable references plus explicit header/query mapping; no secret values in artifacts |
| Compatibility | Skill checks CLI name/version and manifest schema compatibility before generation |
| Validation | CLI tests plus skill fixture-contract test, generated-project install/lint/typecheck/build/MCP smoke test |
| Publication | Skill creates/pushes a separately named GitHub repository only after explicit final confirmation |

## Deferred

| Capability | Reason |
| --- | --- |
| OAuth/OIDC login and refresh | Requires callback, token lifecycle, storage, and threat-model decisions |
| Bare base URL scanning | Endpoint enumeration is unsafe and unreliable without supplied documentation |
| Persistent credential stores | Environment injection is the smallest safe first boundary |
| Automatic destructive-call approval UX | Runtime policy is explicit; interactive approval protocol needs its own contract |
| GraphQL, gRPC, WebSocket, SOAP | HTTP API intake must be proven before protocol-specific expansion |
| Duplicating CLI logic in root skill code | Breaks the package boundary and creates competing generation behavior |
| Auto-publication without a final confirmation | GitHub repository creation and push are external side effects |

## Change control

A deferred capability or cross-package protocol change requires an updated product/architecture decision, API behavior table, a failing test/fixture assertion, and a reviewed plan before implementation.
