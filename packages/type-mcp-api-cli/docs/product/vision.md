# CLI product vision

**Status:** Metadata/schema publication and local structured-spec inspection are implemented.

`type-mcp-api-cli` is a standalone deterministic command-line tool. It accepts supported API inputs, produces a reviewable secret-free manifest, issues/verifies document-approval receipts, and renders a standalone TypeMCP MCP project that consumes `type-mcp` as an npm dependency.

## Users

- Developers who want a direct CLI for repeatable local/CI API-to-MCP generation.
- `type-mcp-api-agent`, which orchestrates the CLI only after a trusted release has been listed in its compatibility policy.

## Non-goals

- GitHub repository creation/push.
- OAuth/OIDC token acquisition or refresh.
- Persistence of credentials or downloaded private specifications.
- Unbounded endpoint discovery from a bare API base URL.

## Initial delivery sequence

1. Metadata command and versioned schema publication — implemented.
2. Safe local structured-spec inspection for OpenAPI 3.x / Swagger 2.0 JSON/YAML — implemented.
3. Closed manifest validation and RFC 8785/JCS canonical-digest implementation.
4. Bounded URL intake and Swagger UI spec URL discovery.
5. Document evidence extraction plus approval challenge/receipt flow.
6. TypeMCP project generation and isolated fixture verification.
