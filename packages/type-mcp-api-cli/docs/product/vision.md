# CLI product vision

**Status:** `metadata --json`, the closed manifest-schema artifact, and local structured-spec `inspect --file <path> --json` are implemented.

## Future product target

`type-mcp-api-cli` is intended to become a standalone deterministic command-line tool that accepts supported API inputs, produces a reviewable secret-free manifest, issues/verifies document-approval receipts, and renders a standalone TypeMCP MCP project that consumes `type-mcp` as an npm dependency. Those manifest, receipt, and generation capabilities are not available in the current bootstrap.

## Current users

- Developers who need deterministic local OpenAPI 3.x / Swagger 2.0 JSON/YAML classification in terminal or CI.
- root `api-to-typemcp` orchestration, which remains fail-closed until a trusted CLI release is listed in its compatibility policy.

## Future users

- Developers who want a direct CLI for repeatable local/CI API-to-MCP generation.

## Non-goals

- GitHub repository creation/push.
- OAuth/OIDC token acquisition or refresh.
- Persistence of credentials or downloaded private specifications.
- Unbounded endpoint discovery from a bare API base URL.

## Initial delivery sequence

1. Metadata command and versioned schema publication — implemented.
2. Safe local structured-spec inspection for OpenAPI 3.x / Swagger 2.0 JSON/YAML — implemented.
3. Closed manifest validation and RFC 8785/JCS canonical-digest implementation — planned.
4. Bounded URL intake and Swagger UI spec URL discovery — planned.
5. Document evidence extraction plus approval challenge/receipt flow — planned.
6. TypeMCP project generation and isolated fixture verification — planned.
