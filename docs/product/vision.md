# Product vision

**Status:** Approved product target; not implemented yet.

## Problem

Creating an MCP server for an external API repeatedly requires developers to understand heterogeneous documentation, translate request shapes into tool schemas, handle credentials safely, enforce write policies, and validate a runnable server. Existing API descriptions are not limited to OpenAPI: teams often provide Swagger UI pages, Markdown guides, or HTML reference sites.

## Product statement

`type-mcp-api-agent` gives Hermes a disciplined workflow for producing a standalone MCP repository from an API source. The generated project installs `type-mcp` from npm and uses it to declare and run its MCP server. The agent produces a reviewable manifest before it produces code.

## Primary users

1. Developers who want a maintainable MCP facade for a third-party or internal HTTP API.
2. Platform teams that need reviewable generated code, explicit auth mappings, and runtime endpoint policy.
3. Agents that must transform API specifications into tested TypeMCP projects without copying framework source.

## User outcomes

- A user can provide an OpenAPI/Swagger file or URL, a Swagger UI URL, or a Markdown/HTML API document URL.
- The agent can identify candidate endpoints and present a normalized, evidence-backed manifest.
- After approval where required, the agent generates every approved endpoint as a TypeMCP tool.
- The generated server runs against the installed npm `type-mcp` package and exposes runtime controls for endpoint execution.
- The verified output can be committed and pushed to a newly created GitHub repository after an explicit publication confirmation.

## Product principles

- **Manifest first.** Human-readable evidence and endpoint policy precede code generation.
- **Generated code is owned code.** Output is a normal TypeScript project, reviewable and editable after generation.
- **The npm package is the runtime dependency.** The generator does not vendor `type-mcp` source.
- **All approved operations are visible.** Policy gates control execution rather than hiding supported endpoints.
- **Credentials stay external.** Runtime environment mappings describe secrets without containing them.
- **Ambiguity is explicit.** Document extraction records confidence and evidence; it cannot silently invent an API contract.
