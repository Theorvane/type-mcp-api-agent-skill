# Release readiness checklist

## Artifact integrity

- [ ] Release commit is on `main` after required reviews and CI.
- [ ] Repository documentation describes implemented behavior; planned features remain marked planned.
- [ ] No credential, downloaded private API document, generated customer project, engine cache, or local artifact is tracked.
- [ ] The release artifact contains the `api-to-typemcp` skill instructions plus its reviewed bundled scripts, templates, and references.
- [ ] No separate generator CLI is required by the installed skill or generated-project workflow.

## Bundled engine and generated-project contract

- [ ] Engine fixtures cover malformed source, manifest, receipt, and policy rejection.
- [ ] Manifest-first approval is enforced; document-derived generation requires a current single-use integrity-validated receipt.
- [ ] Structured input, Swagger UI discovery, and document extraction remain bounded to explicit user-provided sources.
- [ ] Authentication mappings and generated artifacts contain environment-variable names only, never values.
- [ ] Protected-write and deny policy tests prove authorization occurs before request construction and a denied operation makes no upstream request.
- [ ] Generated output installs the published `@theorvane/type-mcp` dependency from npm; it does not use a file, git, local, or copied TypeMCP implementation.
- [ ] Generated project installation, lifecycle checks, and MCP smoke test run in a scrubbed contained temporary directory.
- [ ] Generated MCP smoke test uses an official MCP SDK transport and local fixture upstream by default.

## Publication

- [ ] GitHub repository creation/push confirmation fields are documented and tested.
- [ ] Release notes identify new engine behavior, supported API-source inputs, policy changes, and any external side effect.
- [ ] `skills/api-to-typemcp/SKILL.md` has an intentional SemVer version.
- [ ] `CLAWHUB_TOKEN` is configured as a repository Actions secret and never appears in tracked files or logs.
- [ ] GitHub tag, GitHub Release, ClawHub entry, and skills-hub.ai entry use the identical skill version.
- [ ] Remote `main` matches the intended release commit.
