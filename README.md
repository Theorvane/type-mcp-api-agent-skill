# type-mcp-api-agent-skill

A unified **workspace repository** for API-to-TypeMCP automation:

- root: the `api-to-typemcp` Hermes skill, approval/publication safety policy, and orchestration harness;
- `packages/type-mcp-api-cli/`: the deterministic TypeScript CLI package used directly in terminal/CI workflows and by the skill after trusted compatibility resolution.

## Status

The repository contains an implemented local-only CLI bootstrap (`metadata --json`, plus local OpenAPI 3.x / Swagger 2.0 `inspect --file <path> --json`) and the approved skill/orchestration contract. The CLI is intentionally a distinct package boundary inside this workspace. The CLI package is **not published from this repository yet** and remains `private`; the complete manifest/approval/generation workflow is also not implemented.

## Choose a usage mode

| Need | Use |
| --- | --- |
| Deterministic local structured-spec inspection in terminal/CI | `packages/type-mcp-api-cli/` directly |
| Guided source discovery, manifest approval, safety gates, verification, and confirmed GitHub publication | root `skills/api-to-typemcp/` Hermes skill |

The skill is an orchestrator. It invokes the CLI package; it does not duplicate parsing, normalization, manifest rendering, or project templates.

## Install the released skill

- [ClawHub (`@sjungwon03/api-to-typemcp`)](https://clawhub.ai/sjungwon03/api-to-typemcp)
- [skills-hub.ai (`api-to-typemcp`)](https://skills-hub.ai/skills/api-to-typemcp)
- [GitHub Release v0.1.3](https://github.com/Theorvane/type-mcp-api-agent-skill/releases/tag/v0.1.3)

The published skill is versioned independently from the private CLI package. See [the skill release guide](docs/guides/skill-release.md) for registry and release-lineage details.

## Workspace layout

```text
.
├── skills/api-to-typemcp/       # Hermes orchestration skill
├── docs/                        # product, architecture, contract, and safety policy
├── .agents/                     # root harness and documentation regression checks
└── packages/type-mcp-api-cli/   # standalone deterministic TypeScript CLI package
```

## Current CLI commands

```bash
cd packages/type-mcp-api-cli
npm ci
npm run build
node dist/cli.js metadata --json
node dist/cli.js inspect --file ./openapi.yaml --json
```

`inspect` reads only one local JSON/YAML source, produces a secret-free summary, and does not use the network or generate files. Remote intake, Swagger UI discovery, Markdown/HTML extraction, manifest creation, approval receipts, and project generation remain planned.

## Verification

```bash
# Root skill/docs harness
python3 .agents/scripts/test_validate_docs.py
python3 .agents/scripts/test_workspace.py
python3 .agents/scripts/validate_docs.py

# CLI package
npm --prefix packages/type-mcp-api-cli ci
npm --prefix packages/type-mcp-api-cli run verify
npm --prefix packages/type-mcp-api-cli audit --omit=dev --audit-level=high
```

## Canonical documentation

- Product scope: `docs/product/`
- Architecture and package boundary: `docs/architecture/`
- Manifest and generated API contracts: `docs/api/`
- Safety, auth, execution containment, and publication guides: `docs/guides/`
- Trusted CLI compatibility source of truth: `docs/guides/cli-compatibility.md`
- CLI implementation contract: `packages/type-mcp-api-cli/docs/api/cli-contract.md`
- Skill instructions: `skills/api-to-typemcp/SKILL.md`
- Skill release and registry publication: `docs/guides/skill-release.md`

Read `AGENTS.md` before changing either root orchestration or the CLI package. Do not represent planned CLI or generation behavior as implemented behavior.
