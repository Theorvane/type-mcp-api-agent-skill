# MVP scope

**Status:** Implemented bundled-engine scope; registry publication remains separate.

## Product ownership

| Concern | `api-to-typemcp` bundled skill engine |
| --- | --- |
| Parse, normalize, diagnose, and render | Owns as skill-shipped implementation |
| API-source manifest | Produces and presents for review |
| Approval state | Holds an isolated deterministic receipt record bound to the manifest digest |
| Generated-project checks | Runs independently in a contained temporary workspace |
| GitHub output repository creation/push | Runs only after explicit final confirmation |

## Included

| Capability | MVP boundary |
| --- | --- |
| Input | Supplied local OpenAPI 3.x / Swagger 2.0 JSON/YAML file; `inspect`-only supplied Swagger UI configuration; supplied local Markdown/HTML documentation with explicit `--base-url` |
| Engine output | Versioned secret-free manifest, diagnostics, and a rendered standalone TypeScript project |
| Approval | Explicit manifest-digest confirmation for document-derived sources; structured specs are shown before generation |
| Code generation | Controlled templates with exact published `@theorvane/type-mcp` dependency |
| Endpoint coverage | Every approved endpoint, including mutating methods |
| Execution policy | `GET`/`HEAD`/`OPTIONS` read; mutations protected; unknown methods deny before request construction |
| Authentication | Environment-variable references and explicit mappings only; no values in artifacts |
| Validation | Root harness, engine tests, and contained generated-project install/lint/typecheck/test/build/MCP smoke checks |
| Publication | Explicit final confirmation immediately before a separately named GitHub repository is created or pushed |

## Deferred

| Capability | Reason |
| --- | --- |
| OAuth/OIDC login and refresh | Requires lifecycle, callback, storage, and threat-model decisions |
| Bare base-URL scanning | Unsafe endpoint enumeration without supplied documentation |
| Persistent credential stores | Environment injection is the smallest safe boundary |
| Automatic destructive-call approval UX | Exact runtime policy remains explicit; an interactive protocol needs its own contract |
| GraphQL, gRPC, WebSocket, SOAP | HTTP API intake must be proven first |
| Streamable HTTP transport | The first generated transport is reliable stdio |
| Automatic publication without final confirmation | Repository creation and push are external side effects |

## Change control

A deferred capability or manifest protocol change requires an updated product/architecture decision, API behavior table, focused failing test/fixture assertion, and reviewed plan before implementation.
