# type-mcp-api-agent Design

**Status:** Approved for documentation and planning; implementation requires issue-level plans.

## Goal

Provide two selectable products for turning supplied API specifications or documentation into independently runnable TypeMCP MCP repositories:

1. `type-mcp-api-cli`: a standalone deterministic CLI, usable in terminals and CI.
2. `type-mcp-api-agent`: a Hermes skill repository that invokes the CLI for guided approval, verification, and confirmed publication.

## Approved decisions

- Skill repository name: `type-mcp-api-agent`.
- Companion CLI repository name: `type-mcp-api-cli` (planned; do not create it without an explicit repository-creation confirmation).
- The CLI is separately versioned, installed, and tested. It owns intake, parsing, manifest normalization, diagnostics, and project rendering.
- The skill owns CLI compatibility/provenance checks, user interaction, document-manifest approval, independent output verification, and confirmed GitHub publication.
- The skill must not duplicate or vendor CLI source, templates, parsers, or generators.
- Generated projects install and execute the published `type-mcp` package from npm; generator output must not vendor the library source.
- Intake supports OpenAPI/Swagger JSON/YAML URLs and files, Swagger UI URLs, and Markdown/HTML API documentation URLs.
- Swagger UI input discovers an underlying specification from the supplied page/configuration; failure asks for a specification URL rather than broad crawling.
- Markdown/HTML extraction yields an evidence-backed manifest and requires explicit user approval before CLI generation.
- Every approved endpoint is generated as a tool. Runtime policy, not endpoint omission, controls execution. Mutating calls are protected by default.
- Authentication supports environment variables and explicit header/query mappings. OAuth/OIDC automation is deferred.
- The CLI does not publish output. The skill publishes a verified generated project to a new GitHub repository only after final owner/name/visibility/source-branch confirmation and ref verification.

## Repository shape

```text
type-mcp-api-agent/                 # this repository
├── skills/api-to-typemcp/           # Hermes orchestration skill
├── docs/                            # skill/product/contract docs
└── .agent/                          # harness and fixture CLI contract tests

type-mcp-api-cli/                    # separate planned repository
├── src/                             # intake, normalize, render CLI engine
├── templates/generated-mcp/          # generated project template
├── tests/                            # CLI unit/integration/E2E tests
└── package.json                      # independently installable CLI package
```

## Cross-repository flow

1. A user invokes the CLI directly or invokes the Hermes skill.
2. The skill validates a chosen CLI package/binary/version before calling it.
3. CLI receives source URL/file and produces a secret-free manifest with provenance and diagnostics.
4. The skill requests approval for document-derived candidate operations.
5. The CLI renders a standalone TypeScript MCP project with `type-mcp` from npm.
6. The skill independently verifies the output project.
7. After final publication confirmation, the skill creates and pushes the output repository.

## Compatibility policy

The CLI publishes a semantic version plus protocol and manifest-schema versions. The skill declares the compatible ranges in its own documentation/configuration and fails closed outside them. Cross-repo changes require fixture contract tests in the skill and released CLI tests in the CLI repository.

## Out of scope

OAuth/OIDC acquisition, credential persistence, base-URL endpoint scanning, GraphQL/gRPC/SOAP/WebSocket intake, automatic destructive approval UX, automatic publication without confirmation, and copying CLI implementation into the skill repository.

## Implementation decomposition

### CLI repository

1. Bootstrap package/tooling and deterministic manifest schemas.
2. Implement OpenAPI/Swagger file and URL intake.
3. Implement Swagger UI source discovery.
4. Implement Markdown/HTML evidence extraction and approval artifact.
5. Build source templates and `type-mcp` npm installation verification.
6. Add policy/auth mapping and generated-project E2E tests.

### Skill repository

1. Implement CLI metadata/discovery and compatibility checks with fixture binaries.
2. Implement staged inspect/manifest/generate orchestration and manifest display.
3. Implement CLI-issued approval challenge/receipt handling and safe artifact recording.
4. Implement generated-project independent verification.
5. Implement final-confirmation GitHub publication orchestration.
