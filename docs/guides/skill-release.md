# Versioned skill release and registry publication

`skills/api-to-typemcp/SKILL.md` is a public, versioned artifact. Its frontmatter `version` is the single release version for the Git tag, GitHub Release, ClawHub registry entry, and skills-hub.ai publication.

## Versioning rule

Update the skill's `version` using SemVer whenever its published behavior changes. A reviewed `dev` → `main` promotion releases exactly `v<version>`:

- GitHub tag: `v<version>`
- GitHub Release title: `api-to-typemcp v<version>`
- ClawHub skill version: `<version>`
- skills-hub.ai skill version: `<version>`

A GitHub Release is retry-safe: an existing tag is accepted only when its GitHub Release targets the same merged `main` commit. ClawHub versions are immutable as well: after a registry-side failure, inspect the exact publisher/skill/version before retrying. If that exact version is already present, verify its provenance and complete the release record rather than attempting a duplicate publication.

## Required repository setup

Before the first production promotion, authorized publishers must add these repository Actions secrets:

- `CLAWHUB_TOKEN` — permission to publish `api-to-typemcp` on ClawHub.
- `SKILLS_HUB_AI_API_KEY` — permission to create and version the public `api-to-typemcp` entry on skills-hub.ai.

Both credentials are required before release creation. They are only sent in HTTPS authorization headers or a permissions-restricted temporary ClawHub runner config; neither is committed, printed, included in release notes, nor uploaded as an artifact. Missing credentials fail the workflow before tag or release side effects.

## Automated release lifecycle

1. A PR from `dev` to release-only `main` passes `release-promotion`, independent review, and the required CI checks.
2. After the merge, `.github/workflows/skill-release.yml` runs on the resulting `main` push.
3. It reads and validates `skills/api-to-typemcp/SKILL.md` frontmatter `version`.
4. It creates—or verifies the target of—the corresponding immutable GitHub Release.
5. Only after GitHub Release success, it checks out the pinned official ClawHub CLI source and registers `skills/api-to-typemcp` with the same explicit version.
6. In parallel with ClawHub registration, it invokes the repository-tested skills-hub.ai publisher against the live OpenAPI 3.1 contract. The public category lookup is deliberately unauthenticated; every registry request carries a stable product User-Agent required by the registry WAF, while protected skill reads and mutations authenticate with the API-key `Authorization: ApiKey <key>` scheme. The publisher retries transient transport/429/5xx failures with bounded backoff, reconciles existing immutable versions, and fails closed if the registry returns `PENDING_REVIEW` rather than `PUBLISHED`. The SKILL.md `category: integration` is validated by skills-hub.ai's public category endpoint.

The workflow intentionally does not use `hermes skills publish --to clawhub`: Hermes v0.19.0 exposes that target but does not implement it. The pinned official ClawHub CLI supports explicit version publication, which prevents registry/GitHub version drift.

## Operator verification

After a successful production run, verify all four artifacts agree:

```bash
gh release view v<version> --repo Theorvane/type-mcp-api-agent-skill
clawhub inspect @<publisher>/api-to-typemcp --version <version>
# Browse https://skills-hub.ai/skills/api-to-typemcp and verify v<version>.
```

If the GitHub Release exists but registry registration failed, correct the registry-side prerequisite and inspect `@<publisher>/api-to-typemcp --version <version>` before retrying. If the same artifact is already registered, verify its provenance; do not publish a duplicate, create another tag, or change the tag target.
