# TypeMCP Runtime Contract

Generated projects use the reviewed public npm package:

```json
"@theorvane/type-mcp": "0.2.0"
```

## Allowed public API

Generated TypeScript uses only these public exports:

- `@McpServer`
- `@McpTool`
- `createMcpServer`
- `startStdioServer`
- `zod`
- an explicit `InstanceResolver`

`createMcpServer` and `startStdioServer` are asynchronous and must be awaited. The package uses TC39 standard decorators: generated `tsconfig.json` must not enable legacy `experimentalDecorators` or `emitDecoratorMetadata`.

`@McpTool` requires an `input` Zod object. Generated code pins Zod v4 (`^4.4.3`) because that is the compatible public runtime contract for `@theorvane/type-mcp@0.2.0`.

## Prohibited runtime boundaries

Never generate or publish any of the following:

- copied TypeMCP source code;
- `file:`, `git:`, `link:`, or `portal:` dependencies;
- imports from private, undocumented, or unavailable TypeMCP APIs;
- local TypeMCP checkouts as a generated-project dependency.

Before generated lifecycle scripts run, contained verification inspects dependency metadata and the generated `package-lock.json`, then runs `npm ci --ignore-scripts` in a fresh isolated workspace with inherited npm proxy configuration disabled. It then typechecks, tests, builds, and executes a local stdio smoke test against a mock upstream. Use a host container/VM/sandbox when the dependency graph is untrusted.
