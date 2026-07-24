# Task brief: 1 — harden installed CLI bin and manifest schema

**Status:** review
**Issue:** https://github.com/Theorvane/type-mcp-api-cli/issues/1
**Branch:** `fix/1-harden-cli-bin-schema`

## Goal

Make the only implemented CLI command work through a normal npm-installed `.bin` symlink, make manifest v1 structurally closed as documented, and correct the public contract link.

## Scope

- Symlink-safe executable entrypoint detection.
- Schema tests for unknown nested fields and invalid array items.
- Schema constraints for operations, authentication, warnings, and approval.
- README contract-link correction.

## Exclusions

- No API source intake, manifest command, approval receipt implementation, or generator.
- No `type-mcp` runtime dependency yet.

## RED evidence

| Behavior | Command | Observed result |
| --- | --- | --- |
| npm-installed bin | clean consumer tarball install + `.bin/type-mcp-api-cli metadata --json` | Exit 0 with **0 bytes** output. |
| symlink-safe guard | `npm test -- --run test/entrypoint.test.ts` | RED: `isCliEntrypoint` was missing, then GREEN after realpath-based guard. |
| nested schema rejection | `npm test -- --run test/schema.test.ts` | RED: approval/operation structural tests failed, then GREEN after closed nested definitions. |
| package bin | `npm run verify:installed-bin` | GREEN: clean consumer install printed metadata JSON. |

## Required checks

```bash
npm run lint
npm run typecheck
npm test
npm run build
npm run verify:package
npm audit --omit=dev --audit-level=high
git diff --check
```
