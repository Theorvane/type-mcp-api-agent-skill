---
name: api-to-typemcp
description: Use when a user wants to turn a supplied API specification or documentation into a standalone TypeMCP MCP project through the bundled api-to-typemcp skill engine.
version: 0.1.4
category: integration
license: MIT
metadata:
  hermes:
    tags: [mcp, api, openapi, swagger, code-generation, type-mcp]
    related_skills: []
---

# API to TypeMCP

## Overview

This released skill is the generator delivery unit. Its **bundled skill engine** will live under this skill's `scripts/` directory and use controlled `templates/` to produce a standalone TypeScript MCP project that depends on published `@theorvane/type-mcp`. It never copies the TypeMCP implementation into generated output.

## Current implementation boundary

Task 1 establishes the embedded-engine release, documentation, and CI boundary. The executable engine, templates, and generated-project E2E arrive in later planned tasks. Do not claim that generation commands or project output exist until those tasks provide them.

The safety workflow is nevertheless fixed: manifest-first review, bounded supplied-source intake, secret-free artifacts, explicit digest approval for document-derived operations, exact-ID protected-write authorization before request construction, contained verification, and final publication confirmation.

## When to use

Use this skill when the user provides or asks to use:

- an OpenAPI 3.x or Swagger 2.0 JSON/YAML file or explicit URL;
- a supplied Swagger UI URL;
- a supplied Markdown/HTML API reference;
- API documentation plus a request to produce a maintainable TypeMCP MCP project.

Do not use it to enumerate a bare base URL, guess endpoints, perform mutating calls by default, or publish a repository without separate final confirmation.

## Required workflow contract

1. **Inspect and manifest.** Treat the source as untrusted; sanitize provenance/evidence and show a secret-free canonical manifest before generation.
2. **Approval.** For document-derived manifests, obtain explicit confirmation of the current digest and an isolated, integrity-validated single-use receipt. A changed/stale/tampered manifest or receipt stops generation.
3. **Policy.** Derive `GET`/`HEAD`/`OPTIONS` as `read`, mutations as `protected-write`, and unknown methods as `deny`. `TYPE_MCP_ALLOW_PROTECTED_OPERATIONS` grants protected writes only for exact known operation IDs; the policy check occurs before URL, query, headers, body, authentication, or dispatch.
4. **Output.** Generate only into a confirmed empty target or an explicit replacement target. Never place secret values in output, logs, or Git metadata.
5. **Verification.** Copy output to a fresh temporary workspace with scrubbed environment; inspect dependency metadata and lockfile, run `npm ci --ignore-scripts`, then run contained lint/typecheck/test/build and a local-fixture official-SDK smoke test. Verify published `@theorvane/type-mcp`, never a `file:`, `git:`, local, or copied dependency.
6. **Publication.** Immediately before publication, record owner/org, repository name, visibility, and source branch. Before staging, committing, or pushing, resolve the actual checked-out/ref-to-publish branch and stop unless it exactly equals the recorded source branch.

## Authentication and error safety

- Use only environment-variable references and approved header/query mapping names.
- Do not store or echo token values.
- Return safe errors with no stacks, authorization values, response secrets, raw private URLs, or raw private specifications.
- If a source contains a likely credential, redact it and stop for user guidance.

## Verification checklist

- [ ] Manifest is secret-free, evidence-backed, and canonically digested
- [ ] Document-derived manifest has current explicit approval and a valid isolated receipt
- [ ] Protected-write and deny behavior is verified before request construction
- [ ] Generated output uses published `@theorvane/type-mcp` and passes contained checks
- [ ] Owner/name/visibility/branch is confirmed immediately before publication
- [ ] No secret or downloaded private specification is committed or published
