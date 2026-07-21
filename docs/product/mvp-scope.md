# MVP scope

**Status:** Approved scope; implementation pending.

## Included

| Capability | MVP boundary |
| --- | --- |
| OpenAPI 3.x | Parse JSON/YAML URLs and local files into the common manifest |
| Swagger 2.0 | Parse JSON/YAML URLs and local files, then normalize into the common manifest |
| Swagger UI | Discover an underlying JSON/YAML specification from the supplied UI page/config or known spec references |
| Markdown/HTML docs | Extract evidence-backed candidate operations from supplied documentation URLs |
| Manifest | Include endpoints, schemas, auth hints, evidence, confidence, and executable policy defaults |
| Approval | Require explicit manifest approval before generating from Markdown/HTML-derived operations |
| Code generation | Create a standalone TypeScript project whose dependencies include the npm `type-mcp` package |
| Endpoint coverage | Generate a tool for every approved endpoint, including mutating methods |
| Execution policy | Control read/write endpoint execution at runtime with environment/config policy, defaulting to protected mutations |
| Authentication | Environment-variable references plus explicit header/query mapping; no secret values in generated artifacts |
| Validation | Generator tests plus generated project install, lint, typecheck, build, and MCP smoke test |
| Publication | On explicit final confirmation, create and push a separately named GitHub repository |

## Deferred

| Capability | Reason |
| --- | --- |
| OAuth/OIDC login and refresh | Requires callback, token lifecycle, storage, and threat-model decisions |
| Bare base URL scanning | Endpoint enumeration is unsafe and unreliable without supplied documentation |
| Persistent credential stores | Environment injection is the smallest safe first boundary |
| Automatic destructive-call approval UX | Runtime policy is explicit; interactive approval protocol needs its own contract |
| GraphQL, gRPC, WebSocket, SOAP | HTTP API intake must be proven before protocol-specific expansion |
| OpenAPI custom extensions beyond recognized fields | Add only from real source requirements with tests |
| Auto-publication without a final confirmation | GitHub repository creation and push are external side effects |

## Change control

A deferred capability requires an updated product/architecture decision, API behavior table, a failing test, and a reviewed plan before implementation.
