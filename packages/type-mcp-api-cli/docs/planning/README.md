# Planning

Implementation is issue-scoped after the bootstrap commit.

Completed:

1. Metadata/schema bootstrap.
2. Local OpenAPI 3.x / Swagger 2.0 JSON/YAML safe inspection (`inspect --file <path> --json`).

Next recommended issues:

1. Build a closed manifest v1 validator and RFC 8785/JCS canonical-digest implementation.
2. Implement bounded remote source intake and Swagger UI spec discovery.
3. Implement Markdown/HTML evidence extraction plus CLI challenge/receipt lifecycle.
4. Render a TypeMCP project that consumes the published npm `type-mcp` package, then verify it in an isolated fixture environment.

Each issue needs an observed RED test before implementation, safe A/E/X cases, and an update to public contract documentation.
