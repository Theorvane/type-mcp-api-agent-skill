# Task brief: 15 — Release and publish versioned API-to-TypeMCP skill

**Status:** review
**Issue:** https://github.com/Theorvane/type-mcp-api-agent-skill/issues/15
**Branch:** `feat/15-skill-release-publication`
**Owner:** Hermes Agent

## Goal

A merged reviewed `dev` → `main` promotion creates a Git tag and GitHub Release whose version exactly matches `skills/api-to-typemcp/SKILL.md`, then registers that exact version in ClawHub.

## Source references

- Product: `docs/product/`
- Architecture/API: `docs/architecture/`, `docs/api/`
- External registry CLI contract: https://docs.openclaw.ai/clawhub/cli

## Scope

### Included

- SemVer skill-version validation.
- Immutable `v<version>` tag and GitHub Release creation on `main` pushes only.
- ClawHub registration of the same explicit version after release creation.
- A required `CLAWHUB_TOKEN` GitHub Actions secret that is never logged.
- Regression coverage and operator-facing release documentation.

### Excluded

- Publishing the separate private `type-mcp-api-cli` package.
- Automatic version bumping.
- Changing API-to-TypeMCP runtime/generation behavior.

## Safety and contract notes

- Source input: `SKILL.md` frontmatter version is parsed and validated as SemVer.
- Secrets: ClawHub token is consumed only from Actions secrets; it is not written to source, logs, tags, or release notes.
- Side effects: the `main` push workflow fails before tag/release mutation if the token or version prerequisites are absent.
- Compatibility: ClawHub explicit `--version` must equal the Git tag version and skill frontmatter version.

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `python3 .agents/scripts/test_skill_release.py` | Observed `FileNotFoundError` because `.github/workflows/skill-release.yml` did not exist. |
| Green | `python3 .agents/scripts/test_skill_release.py` | 3 tests passed after adding the workflow and contract. |
| Regression | root harness and CLI `npm run verify` | Root harness passed; CLI `npm run verify` and production audit passed. |

## Verification

- [ ] Root documentation and harness tests
- [ ] CLI package verification
- [ ] `git diff --check`
- [ ] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- Independent review on `9634b8a` found that the GitHub Actions version-extraction heredoc referenced `os.environ` without importing `os`. A new execution regression test observed the resulting `NameError`; the workflow now imports `os`, and the 4-test focused suite passes.
