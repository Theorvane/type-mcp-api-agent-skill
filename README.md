# type-mcp-api-agent-skill

The published `api-to-typemcp` Hermes skill is the single delivery unit for API-to-TypeMCP generation. Its **bundled skill engine** accepts bounded supplied sources, produces approved secret-free manifests, and renders standalone TypeScript MCP projects that depend on the published [`@theorvane/type-mcp`](https://www.npmjs.com/package/@theorvane/type-mcp) package.

## Status

Tasks 1–7 of embedded-engine delivery are implemented on `dev`: structured OpenAPI/Swagger intake, bounded Swagger UI and Markdown/HTML evidence intake, digest-bound approval, controlled TypeScript rendering, contained project E2E verification, and runtime/package-contract documentation. Skill version publication remains a separate release-preparation change after this implementation sequence.

## Safety contract

- **Manifest first:** normalize and review a secret-free manifest before generation.
- **Bounded sources:** accept supplied OpenAPI/Swagger files or explicit documentation only; never enumerate a bare API origin.
- **Secrets stay external:** artifacts may contain environment-variable names and mappings, never values.
- **Protected writes fail closed:** `TYPE_MCP_ALLOW_PROTECTED_OPERATIONS` must authorize an exact known operation ID before request construction.
- **Contained verification:** inspect generated `package.json`, use isolated `npm install --ignore-scripts`, and verify only in a fresh scrubbed workspace. Generated projects currently have no lockfile.
- **Publication is separate:** immediately before publication, confirm owner/org, repository name, visibility, and source branch; verify the actual checked-out/ref-to-publish branch and stop unless it exactly equals the recorded source branch.

## Install the released skill

- [ClawHub (`@sjungwon03/api-to-typemcp`)](https://clawhub.ai/sjungwon03/api-to-typemcp)
- [skills-hub.ai (`api-to-typemcp`)](https://skills-hub.ai/skills/api-to-typemcp)
- [GitHub Release v0.2.0](https://github.com/Theorvane/type-mcp-api-agent-skill/releases/tag/v0.2.0)

## Layout

```text
.
├── skills/api-to-typemcp/       # published skill and bundled engine
│   ├── scripts/                 # deterministic intake, approval, rendering, verification
│   ├── templates/               # controlled TypeScript templates
│   └── references/              # published TypeMCP runtime contract
├── docs/                        # product, architecture, contract, and safety policy
├── .agents/                     # harness and documentation regression checks
└── .github/workflows/           # documentation and bundled-engine CI
```

## Verification

```bash
python3 .agents/scripts/test_validate_docs.py
python3 .agents/scripts/test_workspace.py
python3 .agents/scripts/validate_docs.py
git diff --check
```

## Canonical documentation

- Product scope: `docs/product/`
- Embedded-engine architecture: `docs/architecture/`
- Manifest and generated API contracts: `docs/api/`
- Safety, execution containment, and publication: `docs/guides/`
- Approved plans: `docs/planning/`
- Skill instructions and release artifact: `skills/api-to-typemcp/SKILL.md`

Read `AGENTS.md` before changing the bundled engine. Do not represent planned HTTP transport or public registry publication as implemented behavior before their separate reviewed releases.
