# Security, policy, CLI, verification, and publication guide

**Status:** Approved guide; implementation pending.

## CLI trust and version selection

The canonical compatibility and trusted-resolution policy is [`cli-compatibility.md`](cli-compatibility.md). It is the only source of truth for allowed package versions, protocol/schema values, npm integrity, and executable path expectations.

- No CLI release is currently supported. The skill fails closed and must not execute a candidate CLI until the compatibility policy enables an exact release.
- Self-reported CLI metadata is a post-resolution compatibility check, not proof of provenance.
- `PATH` lookup is prohibited. A local binary is untrusted unless the user explicitly approves its absolute path and SHA-256 for one run under the policy's containment conditions.

## Secret-safe provenance and evidence

The CLI and skill must sanitize external source identifiers **before displaying, hashing, storing, or using them as approval evidence**.

1. Parse remote sources as URLs, never opaque display strings.
2. Remove URL userinfo entirely.
3. Replace query values for all keys with `REDACTED`; never retain signed query values. The key names may remain only when needed for diagnosis and are lowercased/allowlisted.
4. Record only the original-origin host, normalized path, and a stable content hash; never persist redirect targets verbatim.
5. Sanitize local paths to a project-relative identifier or opaque source ID; do not publish user home paths.
6. Redact credentials from evidence snippets and diagnostics before they enter manifests, logs, task briefs, or approval displays.
7. Compute content hashes from fetched bytes in ephemeral memory, but use only sanitized source identifiers in the persisted manifest.

A source containing a likely credential produces a warning. A sanitization failure is fatal: no manifest, approval, generation, verification, or publication proceeds.

## Secret handling

- Accept secret values only through runtime environment variables.
- Store only variable names and header/query mapping metadata in manifests, `.env.example`, generated source, and documentation.
- Never log request authorization headers, credential query values, raw environment values, downloaded private specs, redirect URLs, or raw private diagnostics.
- The skill must not pass secrets to CLI arguments.
- A live authenticated smoke test is separately approved, process-local, and its values are never recorded.

## Authentication mapping

The CLI may map known OpenAPI security schemes or user-provided mappings, for example:

```text
ACME_API_TOKEN -> Authorization: Bearer ***
ACME_API_KEY   -> X-API-Key: ***
```

It may also map an environment value to an approved query parameter. It must reject mappings that overwrite a user-provided request parameter without an explicit precedence rule.

## Runtime execution policy

Every approved operation becomes a tool. Policy is derived and enforced as specified in `docs/api/manifest-contract.md` **before upstream request construction or dispatch**:

| Method | Default mode | Runtime behavior |
| --- | --- | --- |
| `GET`, `HEAD`, `OPTIONS` | `read` | allowed unless an explicit policy denies it |
| `POST`, `PUT`, `PATCH`, `DELETE` | `protected-write` | generated but denied unless exact operation ID is in `TYPE_MCP_ALLOW_PROTECTED_OPERATIONS` |
| any other or unknown method | `deny` | safe MCP error; no upstream request |

A source parser, operation name, or documentation prose cannot classify a mutating method as `read`. The sole protected-write grant is a parsed `TYPE_MCP_ALLOW_PROTECTED_OPERATIONS` comma-separated list of exact stable operation IDs: unset, empty, wildcard, duplicate, method-only, malformed, or unknown entries grant nothing. The runtime evaluates it before URL/header/body/authentication construction. An override requires a visible manifest edit with `origin: approved-override`, a reason, and the normal receipt flow when document-derived. A denied operation sends no upstream request.

## Document-derived manifest approval

The skill displays the complete CLI candidate manifest including sanitized source evidence, confidence, JCS-recomputed canonical `manifestDigest`, CLI protocol version, and approval challenge. For a document-derived manifest, it waits for explicit user confirmation of that exact digest and challenge, then invokes CLI `approve` to obtain a separate MAC-validated receipt. The CLI rejects missing, stale, used, or unbound receipts. The skill does not invoke CLI source generation, output dependency install, upstream smoke test, GitHub creation, or push until the receipt is valid.

## Contained generation and verification

Generation and verification execute untrusted generated code/dependencies, so they must run in a newly created temporary workspace, never the skill repository or user workspace.

1. Create a fresh directory owned by the current process; use it as the only CLI/output working directory.
2. Run CLI and package commands with a scrubbed environment: retain only required runtime basics (`PATH`, temp/home set to isolated paths, locale), remove credentials, git configuration, cloud variables, npm auth, proxies unless explicitly approved, and inherited API endpoints.
3. Default to no outbound network except the explicitly approved npm registry fetch needed for a pinned package. Do not make upstream API requests in normal verification.
4. Inspect the generated `package.json`, lockfile, and npm registry/integrity metadata first. Run `npm ci --ignore-scripts` before any lifecycle script.
5. Run static lint/typecheck and local tests only after inspection. Treat package scripts as untrusted; allow them only under the isolated environment and documented network policy.
6. The MCP smoke test uses an official SDK transport against a local fixture/mock upstream. It must verify that denied writes make no upstream request.
7. A smoke test against a live upstream, especially with authentication, requires separate explicit user approval naming the upstream and permitted operations.
8. Remove the temporary workspace on success/failure unless the user explicitly asks to retain a redacted diagnostic artifact.

## GitHub publication confirmation

The CLI never creates or pushes output repositories. Immediately before the skill publishes a verified project, request confirmation of:

1. GitHub owner or organization
2. Repository name
3. Visibility (`public` or `private`)
4. Source branch to publish

Create/push only after the confirmation. Scan staged/tracked files and remote content for credentials or private downloaded source artifacts before reporting success.
