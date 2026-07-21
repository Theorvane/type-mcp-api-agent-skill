# Security, policy, CLI, and publication guide

**Status:** Approved guide; implementation pending.

## CLI trust and version selection

The skill must invoke a deliberate CLI artifact, not whichever executable happens to be on `PATH`.

1. Prefer an explicit user-selected/project-pinned CLI version or path.
2. Query the CLI metadata stage and verify package/name, semantic version, generation protocol version, and manifest schema version against the skill's compatibility table.
3. Record only non-secret version/provenance values in the task artifact.
4. Stop on a missing, malformed, or incompatible CLI. Never fall back to copied generator code or an unverified alternate binary.

A direct CLI user is responsible for pinning the CLI in their own lockfile/CI; the skill makes that selection visible and verifies it before it performs side effects.

## Secret handling

- Accept secret values only through runtime environment variables.
- Store only variable names and header/query mapping metadata in manifests, `.env.example`, generated source, and documentation.
- Never log request authorization headers, query values mapped as credentials, raw environment values, or downloaded private specs.
- Redact upstream errors before returning MCP content.
- The skill must not pass secrets to CLI arguments. Environment values, if ever needed during a separately approved smoke test, remain process-local and are never recorded.

## Authentication mapping

The CLI may map known OpenAPI security schemes or user-provided mappings, for example:

```text
ACME_API_TOKEN -> Authorization: Bearer ${ACME_API_TOKEN}
ACME_API_KEY   -> X-API-Key: ${ACME_API_KEY}
```

It may also map an environment value to an approved query parameter. It must reject mappings that overwrite a user-provided request parameter without an explicit precedence rule.

## Runtime execution policy

Every approved operation becomes a tool. Policy is derived and enforced as specified in `docs/api/manifest-contract.md` **before upstream request construction or dispatch**:

| Method | Default mode | Runtime behavior |
| --- | --- | --- |
| `GET`, `HEAD`, `OPTIONS` | `read` | allowed unless an explicit policy denies it |
| `POST`, `PUT`, `PATCH`, `DELETE` | `protected-write` | generated but blocked until deliberate runtime configuration permits it |
| any other or unknown method | `deny` | safe MCP error; no upstream request |

A source parser, operation name, or documentation prose cannot classify a mutating method as `read`. An override requires a visible manifest edit with `origin: approved-override`, a reason, and the normal manifest-approval binding when document-derived. A denied operation sends no upstream request.

## Document-derived manifest approval

The skill displays the complete CLI candidate manifest including confidence, citations, canonical `manifestDigest`, CLI protocol version, and approval state. For a document-derived manifest, it waits for explicit user confirmation of that exact digest before recording the required `approval` object. The CLI rejects stale or unbound approval. The skill does not invoke CLI source generation, output dependency install, upstream smoke test, GitHub creation, or push until approval is valid.

## GitHub publication confirmation

The CLI never creates or pushes output repositories. Immediately before the skill publishes a verified project, request confirmation of:

1. GitHub owner or organization
2. Repository name
3. Visibility (`public` or `private`)
4. Source branch to publish

Create/push only after the confirmation. Verify that the remote has no credential-bearing files before reporting success.
