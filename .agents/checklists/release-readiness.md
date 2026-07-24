# Release readiness checklist

## Artifact integrity

- [ ] Release commit is on `main` after required reviews/CI.
- [ ] Repository documentation matches implemented behavior; planned features remain marked planned.
- [ ] No credential, downloaded private API document, generated customer project, CLI binary/cache, or local artifact is tracked.
- [ ] The repository contains skill/harness code only, not a copied CLI engine.

## Skill/CLI contract

- [ ] The supported CLI package/version range and manifest/protocol schema versions are documented.
- [ ] Fixture tests cover compatible CLI, incompatible CLI, malformed manifest, and unsafe-side-effect rejection.
- [ ] Document-derived code generation requires manifest approval.
- [ ] Generated output installs `type-mcp` from the npm registry in a clean temporary directory.
- [ ] Generated MCP smoke test uses an official MCP SDK transport.
- [ ] Write-policy and auth mapping tests prove no upstream request occurs when denied.

## Publication

- [ ] GitHub repository creation/push confirmation fields are documented and tested.
- [ ] Release notes identify any new external side effect, policy behavior, or supported CLI compatibility range.
- [ ] `skills/api-to-typemcp/SKILL.md` has an intentional SemVer version.
- [ ] `CLAWHUB_TOKEN` is configured as a repository Actions secret and never appears in tracked files or logs.
- [ ] GitHub tag, GitHub Release, and ClawHub entry use the identical skill version.
- [ ] Remote `main` matches the intended release commit.
