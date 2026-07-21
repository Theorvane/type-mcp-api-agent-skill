# Task brief: 7 — validate manifest v1 and canonical digest

**Status:** in-progress
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/7
**Branch:** `feat/7-manifest-validation`
**Owner:** Hermes Agent

## Goal

Expose a deterministic, side-effect-free manifest-contract API that validates an unknown v1 manifest through the exact closed schema, computes the contract digest with RFC 8785/JCS canonical JSON, and fails closed when the declared digest does not match.

## Source references

- Product: `packages/type-mcp-api-cli/docs/product/vision.md`
- API: `docs/api/manifest-contract.md`
- CLI contract: `packages/type-mcp-api-cli/docs/api/cli-contract.md`

## Scope

### Included

- Public `canonicalizeJson`, `computeManifestDigest`, and `validateManifestV1` APIs.
- Exact v1 schema validation, digest-payload exclusion rules, SHA-256 output, and safe error results.
- Tests for deterministic key ordering, digest exclusion/mismatch, schema rejection, and non-finite/lone-surrogate rejection.

### Excluded

- Source-to-manifest construction or a new `manifest` CLI command.
- Remote intake, approval/receipts, project generation, or published npm release.

## Safety and contract notes

- Input is `unknown` and schema/canonicalization failures return fixed safe codes/messages only.
- No file writes, network use, subprocesses, or source/secret logging occur in the contract API.
- Digest payload excludes top-level `manifestDigest` and `approval`, exactly as documented.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `npm test -- --run test/manifest-contract.test.ts` | Observed failure: `Cannot find module '../src/manifest.js'`. |
| Green | `npm test -- --run test/manifest-contract.test.ts` | Passed: 5 tests. |
| Regression | `npm run verify` | Passed: lint, strict typecheck, 15 tests, build, package dry-run, installed-bin E2E. |

## Verification

- [ ] Lint
- [ ] Typecheck
- [ ] Unit/integration tests
- [ ] Build/package validation
- [ ] `git diff --check`
- [ ] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded
