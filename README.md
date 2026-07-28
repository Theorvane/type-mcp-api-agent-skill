# type-mcp-api-agent-skill

The published `api-to-typemcp` Hermes skill is the single delivery unit for API-to-TypeMCP generation. Its **bundled skill engine** will turn approved API documentation into standalone TypeScript MCP projects that depend on the published [`@theorvane/type-mcp`](https://www.npmjs.com/package/@theorvane/type-mcp) package.

## Status

The repository has migrated to the embedded-engine boundary. The executable engine and TypeScript templates are intentionally deferred to the next implementation tasks; this Task 1 change establishes the documentation, CI, and release boundary and does not claim generation is already implemented.

## Safety contract

- **Manifest first:** normalize and review a secret-free manifest before generation.
- **Bounded sources:** accept supplied OpenAPI/Swagger files or explicit documentation only; never enumerate a bare API origin.
- **Secrets stay external:** artifacts may contain environment-variable names and mappings, never values.
- **Protected writes fail closed:** `TYPE_MCP_ALLOW_PROTECTED_OPERATIONS` must authorize an exact known operation ID before request construction.
- **Contained verification:** inspect generated dependencies, use `npm ci --ignore-scripts`, and verify only in a fresh scrubbed workspace.
- **Publication is separate:** immediately before publication, confirm owner/org, repository name, visibility, and source branch; verify the actual checked-out/ref-to-publish branch and stop unless it exactly equals the recorded source branch.

## Install the released skill

- [ClawHub (`@sjungwon03/api-to-typemcp`)](https://clawhub.ai/sjungwon03/api-to-typemcp)
- [skills-hub.ai (`api-to-typemcp`)](https://skills-hub.ai/skills/api-to-typemcp)
- [GitHub Release v0.1.4](https://github.com/Theorvane/type-mcp-api-agent-skill/releases/tag/v0.1.4)

## Layout

```text
.
├── skills/api-to-typemcp/       # published skill and future bundled engine
│   ├── scripts/                 # Task 2 engine modules
│   └── templates/               # Task 4 controlled TypeScript templates
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

Read `AGENTS.md` before changing the embedded engine. Do not represent planned engine behavior as implemented behavior.
