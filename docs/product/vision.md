# Product vision

**Status:** Approved embedded-engine target; implementation is staged.

## Problem

Creating a trustworthy MCP server for an external API requires interpreting heterogeneous documentation, translating request shapes into tool schemas, keeping credentials external, controlling writes, and validating a runnable server. Teams supply OpenAPI, Swagger UI, Markdown, and HTML references—not only one schema format.

## Product statement

`api-to-typemcp` is a versioned Hermes skill that ships one **bundled skill engine**. The engine owns deterministic intake, manifest normalization, approval state, policy derivation, rendering, and contained generated-project verification. It renders standalone TypeScript MCP projects using the published `@theorvane/type-mcp` npm dependency; it never copies TypeMCP source into output.

## User outcomes

- A user supplies an OpenAPI/Swagger source, supplied Swagger UI page, or supplied Markdown/HTML document.
- The bundled skill engine presents a secret-free, evidence-backed manifest before generation.
- After the required approval and output-target confirmation, it renders every approved endpoint as a TypeMCP tool.
- The generated server uses published `@theorvane/type-mcp`, exposes an exact-ID protected-write gate, and is verified in containment.
- Only after explicit final confirmation can the skill create or push an output repository.

## Product principles

- **One shipping unit.** The released skill includes the engine, templates, and references required for generation.
- **Manifest first.** Reviewable evidence and endpoint policy precede source output.
- **Generated code is owned code.** Output is a normal editable TypeScript project.
- **Published runtime dependency.** Generated output depends on `@theorvane/type-mcp`, never a local checkout or copied implementation.
- **All approved operations are visible.** Runtime policy gates execution rather than silently omitting endpoints.
- **Credentials stay external.** Runtime environment mappings describe secrets without containing them.
- **Ambiguity is explicit.** Bounded document extraction records evidence and confidence; it cannot invent an API contract.
