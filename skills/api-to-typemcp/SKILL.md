---
name: api-to-typemcp
description: Use when a user wants to turn an API URL, OpenAPI/Swagger file or link, Swagger UI, or Markdown/HTML API documentation into a standalone TypeMCP MCP project through the type-mcp-api-cli.
version: 0.1.0
license: MIT
metadata:
  hermes:
    tags: [mcp, api, openapi, swagger, code-generation, type-mcp]
    related_skills: []
---

# API to TypeMCP

## Overview

This skill orchestrates the separately installed `type-mcp-api-cli`. It does not parse specifications, extract endpoints, create TypeScript templates, or substitute its own generator. The CLI is the deterministic engine; this skill is the approval, safety, verification, and publication layer.

The target is a normal standalone TypeScript MCP repository whose runtime dependency is npm `type-mcp`.

## When to use

Use this skill when the user provides or asks to use:

- an OpenAPI 3.x or Swagger 2.0 JSON/YAML URL or file;
- a Swagger UI URL;
- a Markdown/HTML API reference URL;
- an API documentation URL plus a request to produce a maintainable TypeMCP MCP project.

Do not use it for a bare base URL with no supplied API documentation. Do not use it to guess endpoints, execute mutating calls by default, or publish a repository without final confirmation.

## Required user inputs

Collect or infer only what is needed for the requested stage:

| Stage | Required inputs |
| --- | --- |
| Inspect/manifest | API source URL/file and optionally desired CLI version/path |
| Generate | An approved manifest plus an empty local output directory |
| Publish | Confirmed GitHub owner/org, repository name, visibility, and source branch |

For Markdown/HTML documents, manifest approval is mandatory. Do not proceed from candidate manifest to generation based on an implied or stale approval.

## Workflow

### 1. Establish the source and CLI

1. Identify the source type: structured specification, Swagger UI, or supplied Markdown/HTML documentation.
2. Resolve the CLI from an explicit user choice, project pin, or documented compatible release.
3. Invoke the CLI metadata command and validate its package/name, semantic version, generation protocol version, and manifest schema version.
4. Stop on incompatibility or an untrusted executable; report the missing requirement rather than reimplementing CLI behavior.

**Completion criterion:** the selected CLI and source descriptor are recorded without any secret value.

### 2. Inspect and obtain a manifest

1. Invoke the CLI inspect stage on the supplied source.
2. Invoke the manifest stage and receive a secret-free, versioned manifest plus safe diagnostics.
3. Verify that the manifest has source provenance, content hash, operations, auth mapping names, confidence, evidence, and warnings.
4. Present the operation table and warnings to the user.

**Completion criterion:** there is one complete manifest artifact whose hash, CLI version, and schema/protocol versions are known.

### 3. Apply approval and policy gates

1. If any operation derives from Markdown/HTML evidence, ask for explicit approval of the manifest.
2. Let the user remove operations or adjust tool names, auth mapping names, and policy before approval.
3. Mark `POST`, `PUT`, `PATCH`, and `DELETE` as generated-but-protected unless the approved runtime policy says otherwise.
4. If the manifest changes, invalidate approval and repeat review.

**Completion criterion:** every operation to generate is explicitly approved and write behavior is policy-gated.

### 4. Generate through the CLI

1. Confirm the local output directory is empty or user-approved for replacement.
2. Invoke the CLI generation stage with the approved manifest and selected output directory.
3. Do not inject secrets into CLI arguments, generated files, logs, or Git metadata.
4. Confirm generated `package.json` declares npm `type-mcp`, not a path/file/git copy of its source.

**Completion criterion:** the CLI reports generation metadata and all generated paths are under the approved output directory.

### 5. Independently verify generated output

Run the generated project’s documented checks in its own directory:

```bash
npm ci
npm run lint
npm run typecheck
npm test
npm run build
npm run verify:package
npm audit --omit=dev --audit-level=high
git diff --check
```

Also run an MCP smoke test through an official SDK transport. Verify a denied write-policy operation sends no upstream request. Treat failures as generator/manifest defects; do not patch generated source invisibly.

**Completion criterion:** fresh tool output demonstrates the generated project uses installed npm `type-mcp` and passes its applicable checks.

### 6. Publish only with final confirmation

Immediately before GitHub creation/push, ask for and record confirmation of owner/org, repository name, visibility, and source branch. Then create, commit, push, and read back the remote URL/default branch. Scan staged/tracked files for secrets before reporting success.

**Completion criterion:** the user-confirmed repository exists remotely and contains the verified generated project with no credential-bearing artifact.

## Authentication and error safety

- Use only environment-variable references plus approved header/query mappings.
- Do not store or echo token values.
- Return safe summaries of CLI/upstream errors; no stacks, authorization values, response secrets, or raw private specs.
- If a source includes a likely credential, redact it from the review artifact and stop for user guidance.

## Common pitfalls

1. **Duplicating CLI behavior in the skill.** Fix or extend `type-mcp-api-cli`; do not add parser/template logic here.
2. **Treating a documentation URL as an approved contract.** Markdown/HTML candidates always need explicit manifest approval.
3. **Installing an arbitrary globally available CLI.** Validate package/version/protocol/schema before calling it.
4. **Skipping generated-project verification.** A generated directory is not a deliverable until it installs npm `type-mcp` and runs through an official MCP transport.
5. **Publishing too early.** GitHub repository creation/push has a separate final confirmation gate even after manifest approval.

## Verification checklist

- [ ] CLI provenance/version and manifest schema/protocol compatibility verified
- [ ] Manifest is secret-free and evidence-backed
- [ ] Document-derived operations explicitly approved
- [ ] Every approved operation generated; mutating operations protected by policy
- [ ] Generated project installs npm `type-mcp` and passes applicable checks
- [ ] Official-transport MCP smoke test passes
- [ ] GitHub owner/name/visibility/branch confirmed immediately before publication
- [ ] No secret or downloaded private specification is committed or published
