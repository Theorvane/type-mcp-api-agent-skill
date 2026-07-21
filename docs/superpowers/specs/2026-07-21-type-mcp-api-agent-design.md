# type-mcp-api-agent Design

**Status:** Approved for documentation and planning; implementation requires issue-level plans.

## Goal

Build a standalone repository containing a Hermes skill and deterministic generator that turns supplied API specifications or documentation into independently runnable TypeMCP MCP repositories.

## Approved decisions

- Repository name: `type-mcp-api-agent`.
- Generated projects install and execute the published `type-mcp` package from npm; generator output must not vendor the library source.
- Intake supports OpenAPI/Swagger JSON/YAML URLs and files, Swagger UI URLs, and Markdown/HTML API documentation URLs.
- Swagger UI input discovers an underlying specification from the supplied page/configuration; failure asks for a specification URL rather than broad crawling.
- Markdown/HTML extraction yields an evidence-backed manifest and requires explicit user approval before code generation.
- Every approved endpoint is generated as a tool. Runtime policy, not endpoint omission, controls execution. Mutating calls are protected by default.
- Authentication supports environment variables and explicit header/query mappings. OAuth/OIDC automation is deferred.
- Verified generated projects are published to a newly created GitHub repository only after a final owner/name/visibility confirmation.

## Repository shape

```text
type-mcp-api-agent/
├── skills/api-to-typemcp/       # Hermes orchestration skill
├── packages/generator/          # deterministic TypeScript intake/generation CLI
├── templates/generated-mcp/     # source template for each generated project
├── docs/                        # canonical decisions and contracts
└── .agent/                      # tracked engineering harness
```

## Data flow

1. Receive source URL/file and source type.
2. Retrieve/parse bounded input and record secret-free provenance.
3. Normalize operations into the manifest contract.
4. Require explicit approval for document-derived candidates.
5. Render a standalone TypeScript MCP project with `type-mcp` from npm.
6. Run generated-project lint/typecheck/test/build and an official-transport smoke test.
7. After final publication confirmation, create and push the output repository.

## Out of scope

OAuth/OIDC acquisition, credential persistence, base-URL endpoint scanning, GraphQL/gRPC/SOAP/WebSocket intake, automatic destructive approval UX, and automatic publication without confirmation.

## Implementation decomposition

1. Bootstrap package/tooling and deterministic manifest schemas.
2. Implement OpenAPI/Swagger file and URL intake.
3. Implement Swagger UI source discovery.
4. Implement Markdown/HTML evidence extraction and approval artifact.
5. Build source templates and `type-mcp` npm installation verification.
6. Add policy/auth mapping and generated-project E2E tests.
7. Implement GitHub publication only after end-to-end safety gates.
