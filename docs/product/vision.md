# Product vision

**Status:** Approved product target; skill and CLI implementation pending.

## Problem

Creating an MCP server for an external API repeatedly requires developers to understand heterogeneous documentation, translate request shapes into tool schemas, handle credentials safely, enforce write policies, and validate a runnable server. Existing API descriptions are not limited to OpenAPI: teams often provide Swagger UI pages, Markdown guides, or HTML reference sites.

Different users also need different interfaces: a CI pipeline needs a deterministic CLI, while a Hermes user needs source discovery, evidence review, manifest approval, and publication safeguards.

## Product statement

The product is deliberately split into two independently usable repositories:

| Repository | Product role |
| --- | --- |
| `type-mcp-api-cli` | Deterministic API-source intake, manifest normalization, diagnostics, and TypeMCP project rendering CLI |
| `type-mcp-api-agent` | Hermes skill that invokes the CLI and manages approval, safety, verification, and confirmed GitHub publication |

The CLI is useful directly in a terminal or CI. The skill is useful when a user wants a guided and reviewable workflow. Both paths generate normal TypeScript MCP projects that install `type-mcp` from npm.

## Primary users

1. Developers who want a maintainable MCP facade for a third-party or internal HTTP API.
2. Platform teams that need reviewable generated code, explicit auth mappings, and runtime endpoint policy in CI.
3. Hermes users who want conversational source intake and safety/approval gates without reimplementing CLI behavior.

## User outcomes

- A developer can invoke the CLI with an OpenAPI/Swagger file or URL, Swagger UI URL, or Markdown/HTML API document URL.
- A Hermes user can invoke the skill, which calls the same CLI and presents a normalized, evidence-backed manifest.
- After approval where required, the CLI generates every approved endpoint as a TypeMCP tool.
- The generated server runs against the installed npm `type-mcp` package and exposes runtime controls for endpoint execution.
- The skill can verify the output and, after explicit final confirmation, create and push a newly named GitHub repository.

## Product principles

- **One deterministic engine, two entry points.** CLI and skill share a published contract rather than duplicate parsing/generation logic.
- **Manifest first.** Human-readable evidence and endpoint policy precede code generation.
- **Generated code is owned code.** Output is a normal TypeScript project, reviewable and editable after generation.
- **The npm package is the runtime dependency.** The CLI does not vendor `type-mcp` source.
- **All approved operations are visible.** Policy gates control execution rather than hiding supported endpoints.
- **Credentials stay external.** Runtime environment mappings describe secrets without containing them.
- **Ambiguity is explicit.** Document extraction records confidence and evidence; it cannot silently invent an API contract.
