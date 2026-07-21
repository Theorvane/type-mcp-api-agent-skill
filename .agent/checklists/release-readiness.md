# Release readiness checklist

## Artifact integrity

- [ ] Release commit is on `main` after required reviews/CI.
- [ ] Repository documentation matches implemented behavior; planned features remain marked planned.
- [ ] No credential, downloaded private API document, generated customer project, or local artifact is tracked.
- [ ] Package lock and dependency audit are current when packages exist.

## Generator safety

- [ ] OpenAPI/Swagger, Swagger UI, and document-derived behavior has current tests where implemented.
- [ ] Document-derived code generation requires manifest approval.
- [ ] Generated output installs `type-mcp` from the npm registry in a clean temporary directory.
- [ ] Generated MCP smoke test uses an official MCP SDK transport.
- [ ] Write-policy and auth mapping tests prove no upstream request occurs when denied.

## Publication

- [ ] GitHub repository creation/push confirmation fields are documented and tested.
- [ ] Release notes identify any new external side effect or policy behavior.
- [ ] Remote `main` matches the intended release commit.
