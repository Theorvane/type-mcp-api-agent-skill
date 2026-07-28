# Security, policy, verification, and publication guide

**Status:** Approved embedded-engine contract; implementation is staged.

## Bounded source intake and secret-safe evidence

The `api-to-typemcp` **bundled skill engine** treats supplied specifications and documents as untrusted input. It does not enumerate a bare API origin, crawl unrelated pages, or persist raw private source data.

1. Parse remote sources as URLs, never opaque display strings.
2. Remove URL userinfo entirely.
3. Replace query values with `REDACTED`; retain only allowlisted key names when necessary for diagnosis.
4. Persist only sanitized origin host, normalized path or opaque local ID, and a stable content hash; never raw redirect targets.
5. Sanitize local paths to a project-relative identifier or opaque source ID.
6. Redact credentials from evidence snippets and diagnostics before they enter manifests, logs, task briefs, or approval displays.
7. Hash fetched bytes only in ephemeral memory and never persist credential-bearing source text.

A sanitization failure is fatal: no manifest, approval, generation, verification, or publication proceeds.

## Secret handling

- Accept secret values only through runtime environment variables.
- Store variable names and header/query mapping metadata only in manifests, `.env.example`, generated source, and documentation.
- Never log authorization headers, credential query values, raw environment values, downloaded private specs, redirect URLs, or raw private diagnostics.
- The engine never receives secrets through command arguments.
- A live authenticated smoke test is separately approved, process-local, and its values are never recorded.

## Runtime execution policy

Every approved operation becomes a tool. The bundled skill engine derives and generated runtime enforces policy **before upstream request construction or dispatch**:

| Method | Default mode | Runtime behavior |
| --- | --- | --- |
| `GET`, `HEAD`, `OPTIONS` | `read` | may send a request unless explicitly denied |
| `POST`, `PUT`, `PATCH`, `DELETE` | `protected-write` | denied unless its exact known ID is in `TYPE_MCP_ALLOW_PROTECTED_OPERATIONS` |
| Other/unknown | `deny` | safe MCP error and no upstream request |

A source parser, operation name, or documentation prose cannot classify a mutating method as `read`. The sole protected-write grant is a comma-separated list of exact stable operation IDs: unset, empty, wildcard, duplicate, method-only, malformed, or unknown entries grant nothing. The runtime validates this list before URL, query, headers, body, authentication, or dispatch. A denied operation sends no upstream request.

## Manifest approval

The engine displays the complete candidate manifest with sanitized source evidence, confidence, RFC 8785/JCS canonical `manifestDigest`, contract version, and approval challenge. For document-derived manifests, it waits for explicit user confirmation of that exact digest, then writes a separate integrity-validated receipt in process-owned isolated state. The receipt is bound to exact digest/version, expires, and is single-use. Missing, stale, used, tampered, or unbound receipts stop generation. The engine never installs dependencies, calls an upstream API, creates a GitHub repository, or pushes output before these gates are valid.

## Contained generation and verification

Generation and verification execute untrusted generated code/dependencies, so they run in a newly created temporary workspace, never the skill repository or user workspace.

1. Create a fresh directory owned by the current process as the only engine/output working directory.
2. Use a scrubbed environment: retain only required basics (`PATH`, isolated temp/home, locale); remove credentials, git configuration, cloud variables, npm auth, proxies unless explicitly approved, and inherited API endpoints.
3. Default to no outbound network except an explicitly approved pinned npm registry fetch. Do not make upstream API requests in normal verification.
4. Inspect generated `package.json`, lockfile, and registry/integrity metadata. The project must declare published `@theorvane/type-mcp`, never a file/git/local dependency. Run `npm ci --ignore-scripts` before any lifecycle script.
5. Run lint, typecheck, tests, and build only inside containment after inspection.
6. Use an official SDK transport and local fixture/mock upstream for the MCP smoke test; prove denied writes make no upstream request.
7. A live authenticated upstream smoke test requires separate explicit user approval naming the upstream and permitted operations.
8. Remove the temporary workspace on success/failure unless a user requests a redacted diagnostic artifact.

## GitHub publication confirmation

Immediately before the skill publishes a verified project, record user confirmation of **owner/org, repository name, visibility, and source branch**.

Before staging, committing, or pushing, resolve the actual checked-out/ref-to-publish branch and stop unless it exactly equals the recorded source branch. Create or push only after this ref verification. Scan staged/tracked files and remote content for credentials or private downloaded source artifacts before reporting success.
