# Versioned skill release and registry publication

`skills/api-to-typemcp/SKILL.md` is a public, versioned artifact. Its frontmatter `version` is the single release version for the Git tag, GitHub Release, and ClawHub registry entry.

## Versioning rule

Update the skill's `version` using SemVer whenever its published behavior changes. A reviewed `dev` → `main` promotion releases exactly `v<version>`:

- GitHub tag: `v<version>`
- GitHub Release title: `api-to-typemcp v<version>`
- ClawHub skill version: `<version>`

The release workflow rejects a missing or non-SemVer version. It will not overwrite an existing tag: an existing tag is accepted only when its GitHub Release targets the same merged `main` commit. This makes a failed registry publication retryable without creating a second release.

## Required repository setup

Before the first production promotion, a ClawHub publisher with permission to publish `api-to-typemcp` must create an API token and add it to this repository as the Actions secret `CLAWHUB_TOKEN`.

The token is required before release creation. It is written only to a permissions-restricted temporary runner config and is never committed, printed, included in release notes, or uploaded as an artifact. Missing credentials fail the workflow before tag or release side effects.

## Automated release lifecycle

1. A PR from `dev` to release-only `main` passes `release-promotion`, independent review, and the required CI checks.
2. After the merge, `.github/workflows/skill-release.yml` runs on the resulting `main` push.
3. It reads and validates `skills/api-to-typemcp/SKILL.md` frontmatter `version`.
4. It creates—or verifies the target of—the corresponding immutable GitHub Release.
5. Only after GitHub Release success, it checks out the pinned official ClawHub CLI source and registers `skills/api-to-typemcp` with the same explicit version.

The workflow intentionally does not use `hermes skills publish --to clawhub`: Hermes v0.19.0 exposes that target but does not implement it. The pinned official ClawHub CLI supports explicit version publication, which prevents registry/GitHub version drift.

## Operator verification

After a successful production run, verify all three artifacts agree:

```bash
gh release view v<version> --repo Theorvane/type-mcp-api-agent-skill
clawhub inspect @<publisher>/api-to-typemcp --version <version>
```

If the GitHub Release exists but registry registration failed, correct the registry-side prerequisite and rerun the failed workflow. Do not manually create another tag or change its target.
