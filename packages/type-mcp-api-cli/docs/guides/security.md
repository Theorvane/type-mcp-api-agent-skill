# Security policy

## Implemented safety boundaries

`metadata --json` does not read API inputs, use the network, access environment secrets, create files, or invoke subprocesses.

`inspect --file <path> --json` reads one local JSON/YAML file. It does not use the network, generate files, call an upstream API, persist the supplied path/body, or print either one. Its output uses content hashes and an opaque local identifier; parse/read failures return fixed safe code/message pairs without source text, paths, or stacks.

## Rules for future commands

1. Treat source payloads as `unknown` and validate before use.
2. Sanitize URL userinfo, query values, redirect targets, private paths, snippets, and diagnostics before any display, hash artifact, or persistent output.
3. Do not accept secret values through CLI arguments. Use environment-variable names only in generated auth mappings.
4. Document-derived manifests require an isolated-state approval challenge and CLI-issued, MAC-validated, single-use receipt before generation.
5. Protected writes must require exact stable IDs in `TYPE_MCP_ALLOW_PROTECTED_OPERATIONS`; all malformed, wildcard, duplicate, method-only, and unknown entries fail closed before upstream request construction.
6. Generation never performs GitHub publication. The optional agent asks for final owner/name/visibility/source-branch confirmation and validates the ref before push.
