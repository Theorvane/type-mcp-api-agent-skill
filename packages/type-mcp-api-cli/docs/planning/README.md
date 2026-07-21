# Planning

Implementation is issue-scoped after the bootstrap commit.

Completed:

1. Metadata/schema bootstrap.
2. Local OpenAPI 3.x / Swagger 2.0 JSON/YAML safe inspection (`inspect --file <path> --json`).
3. Closed manifest v1 validation and RFC 8785/JCS-compatible canonical-digest library APIs.

Next recommended issues:

1. Construct a secret-free manifest from a local inspected structured specification.
2. Implement bounded remote source intake and Swagger UI spec discovery.
3. Implement Markdown/HTML evidence extraction plus CLI challenge/receipt lifecycle.
4. Render a TypeMCP project that consumes the published npm `type-mcp` package, then verify it in an isolated fixture environment.

Each issue needs an observed RED test before implementation, safe A/E/X cases, and an update to public contract documentation.
