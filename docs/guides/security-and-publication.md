# Security, policy, and publication guide

**Status:** Approved guide; implementation pending.

## Secret handling

- Accept secret values only through runtime environment variables.
- Store only variable names and header/query mapping metadata in manifests, `.env.example`, generated source, and documentation.
- Never log request authorization headers, query values mapped as credentials, raw environment values, or downloaded private specs.
- Redact upstream errors before returning MCP content.

## Authentication mapping

The generator may map known OpenAPI security schemes or user-provided mappings, for example:

```text
ACME_API_TOKEN -> Authorization: Bearer ${ACME_API_TOKEN}
ACME_API_KEY   -> X-API-Key: ${ACME_API_KEY}
```

It may also map an environment value to an approved query parameter. It must reject mappings that overwrite a user-provided request parameter without an explicit precedence rule.

## Runtime execution policy

Every approved operation becomes a tool. Before an upstream call, generated code evaluates policy:

- Read methods (`GET`, `HEAD`, `OPTIONS`) are allowed unless explicitly denied.
- Mutating methods (`POST`, `PUT`, `PATCH`, `DELETE`) are generated but protected by default.
- Explicit runtime configuration can allow a protected operation/method.
- A denied operation returns a safe MCP error and sends no upstream request.

## Document-derived manifest approval

For Markdown/HTML intake, show the complete candidate manifest including confidence and citations. Wait for explicit approval before code generation, dependency install, upstream smoke test, GitHub creation, or push.

## GitHub publication confirmation

Immediately before publication, request confirmation of:

1. GitHub owner or organization
2. Repository name
3. Visibility (`public` or `private`)
4. Source branch to publish

Create/push only after the confirmation. Verify that the remote has no credential-bearing files before reporting success.
