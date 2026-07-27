# CLI compatibility and trusted resolution policy

**Status:** Approved policy; no CLI release is supported yet.

This document is the canonical source of truth for whether `api-to-typemcp` may invoke a `type-mcp-api-cli` executable. `AGENTS.md`, the Hermes skill, fixtures, and future code must defer to this policy.

## Current compatibility state

| Field | Current value |
| --- | --- |
| Expected npm package | `type-mcp-api-cli` |
| Expected executable | `type-mcp-api-cli` |
| Supported CLI package versions | **none** — no release exists yet |
| Supported CLI protocol versions | **none** |
| Supported manifest schema versions | **none** |
| Default action | Fail closed; do not invoke a CLI or generate output |

Until this table is changed in a reviewed release, the skill may inspect a user-provided source only as documentation; it must not run a candidate CLI, install a package, generate a project, execute generated code, or publish output.

The skill itself can still be installed and used for orchestration guidance during this pre-release state. Its user-facing outcome must make clear that project generation is intentionally blocked, no CLI was installed or executed, and the compatibility policy is the release gate.

## Enabling a CLI release

Update the compatibility table only after a reviewed CLI npm release exists and its release evidence is available. A CLI release becomes supported only through one focused cross-repository change that updates this table with all of:

1. Exact npm package name and a bounded semver range, preferably an exact version for the first release.
2. Allowed CLI protocol and manifest schema versions.
3. npm registry dist integrity (`sha512-...`) for each supported exact package version.
4. The expected package `bin` mapping and executable relative path.
5. Fixture tests covering compatible, incompatible, tampered, and missing metadata cases.
6. Linked release/verification evidence from `packages/type-mcp-api-cli/` and its package release record.

If package, protocol, schema, or integrity changes, compatibility must be updated first. A broad range does not waive integrity verification: every resolved exact version needs a documented expected integrity.

## Trusted resolution flow

The skill must use this flow before *executing* a CLI:

1. Resolve an exact supported npm version from this document; reject an unpinned range at runtime.
2. Fetch/install it in a newly created isolated temporary directory using the npm registry and a generated lockfile.
3. Compare the resolved package integrity from the lockfile/package-manager metadata to this policy's expected integrity.
4. Resolve the `bin` entry to an absolute path under that isolated installation; reject a path outside it, symlinks escaping it, unexpected owner/mode, or an unexpected package name.
5. Record only the exact version, expected/observed integrity, absolute binary path, protocol/schema metadata, and non-secret timestamps in a task artifact.
6. Invoke the absolute path with a scrubbed environment and a controlled working directory.
7. Treat CLI metadata as a compatibility assertion *after* artifact integrity has been established, not as provenance proof.

A user-provided local binary or path is untrusted by default. The skill may execute it only after the user explicitly approves its SHA-256 digest and absolute path for that one run, with the same scrubbed environment and containment rules. `PATH` lookup alone is prohibited.

## Precedence and updates

1. This policy is authoritative for supported package/version/integrity/protocol/schema values.
2. A user may choose among versions explicitly listed here, but cannot override an unsupported value through chat alone.
3. A manifest's declared protocol/schema must satisfy this policy and the selected CLI's metadata; disagreement fails closed.
4. Future executable configuration must reference this file rather than duplicate compatibility values in a skill or source file.
