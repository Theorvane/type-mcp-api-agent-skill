# type-mcp-api-cli

Deterministic CLI for local structured API-specification inspection.

> **Current status:** machine-readable `metadata --json`, local OpenAPI 3.x / Swagger 2.0 JSON/YAML `inspect --file <path> --json`, and the closed versioned manifest schema are implemented. Manifest construction, remote intake, Swagger UI discovery, Markdown/HTML extraction, approval receipts, and project generation are planned—not available in this version.

## Product boundary

| Product | Responsibility |
| --- | --- |
| `type-mcp-api-cli` (`packages/type-mcp-api-cli/`) | Implemented local JSON/YAML structured-spec classification through `metadata` and `inspect`; manifest/approval/project-generation commands remain planned. |
| `api-to-typemcp` (`../../skills/api-to-typemcp/`) | Optional Hermes skill that resolves a trusted CLI release, presents manifests for approval, verifies generated output, and asks before GitHub publication. |

The CLI never creates GitHub repositories or persists credentials.

## Implemented commands

```bash
npm install type-mcp-api-cli
npx type-mcp-api-cli metadata --json
npx type-mcp-api-cli inspect --file ./openapi.yaml --json
```

`metadata --json` prints package/protocol/schema metadata and the supported command list. `inspect` reads a local structured spec only and prints a secret-free classification summary; it never prints the supplied file path or source text.

## Contract

- [`docs/api/cli-contract.md`](docs/api/cli-contract.md) is the canonical CLI contract.
- `schemas/api-manifest-1.schema.json` is a closed JSON Schema for manifest version `1`.
- Current protocol version: `1`.
- Future commands are additive only through tested, documented releases.

## Development

```bash
npm ci
npm run lint
npm run typecheck
npm test
npm run build
npm run verify:package
npm run verify:installed-bin
```

## Security

- Accept external API sources as untrusted data.
- Never store credentials or pass them as CLI arguments.
- No network access, local source storage, code generation, or live API calls occur in the bootstrap implementation. Local `inspect` parses one supplied JSON/YAML file in memory and returns only a sanitized summary.
- Publishing a generated repository belongs to the agent workflow and always needs a final user confirmation.

## License

MIT
