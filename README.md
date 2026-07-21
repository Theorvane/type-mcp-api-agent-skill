# type-mcp-api-agent

A Hermes skill and tested generator harness for creating standalone TypeMCP MCP server repositories from an API source.

## Status

The repository currently contains the approved product specification and engineering harness. The generator implementation starts only from the approved design and issue plan.

## Intended workflow

1. Provide an OpenAPI/Swagger JSON or YAML URL/file, a Swagger UI URL, or a Markdown/HTML API documentation URL.
2. Discover and normalize API operations into a reviewable manifest.
3. For document-derived operations, present the manifest and wait for explicit approval.
4. Generate a standalone TypeScript MCP project that installs `type-mcp` from npm.
5. Verify the generated project, then create and push its own GitHub repository after confirming the target name, owner, and visibility.

## Product boundaries

- Every discovered endpoint can become a tool; execution is controlled by generated runtime policy.
- API secrets are supplied only at runtime through environment variables and approved header/query mappings.
- OAuth/OIDC token acquisition, credential persistence, endpoint guessing from a bare base URL, and unapproved publishing are out of scope for the initial release.

## Canonical documentation

- Product scope: `docs/product/`
- Architecture and manifest contract: `docs/architecture/`, `docs/api/`
- Safety and approval workflow: `docs/guides/`
- Executable task plans: `docs/planning/`
- Approved design history: `docs/superpowers/specs/`
- Agent workflow and quality gates: `AGENTS.md`, `.agent/`

## Development status

Read `AGENTS.md` before changing this repository. Do not represent planned generator behavior as implemented behavior.
