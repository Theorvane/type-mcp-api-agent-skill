"""Contract checks for safe `dev`/release-branch promotion into `main`."""

from pathlib import Path

workflow = Path(".github/workflows/release-promotion.yml").read_text(encoding="utf-8")

assert "branches: [main]" in workflow, "release gate must target main"
assert "HEAD_REF: ${{ github.head_ref }}" in workflow, "release gate must read the PR head"
assert 'test "$HEAD_REF" = "dev"' not in workflow, "release branches must not be rejected by a dev-only guard"
assert '[[ "$HEAD_REF" = "dev" || "$HEAD_REF" =~ ^release/[1-9][0-9]*-[a-z0-9]+(-[a-z0-9]+)*$ ]]' in workflow, (
    "promotion may accept only dev or a strict positive-issue release branch"
)
assert "actions/checkout@11d5960a326750d5838078e36cf38b85af677262" in workflow, "lineage guard needs a pinned checkout"
assert "fetch-depth: 0" in workflow, "lineage guard needs complete history"
assert 'git merge-base --is-ancestor origin/main HEAD' in workflow, "candidate must retain main ancestry"
assert 'git merge-base --is-ancestor origin/dev HEAD' in workflow, "candidate must retain dev ancestry"
assert 'test "$(git rev-list --parents -n 1 HEAD | awk' in workflow, "release branch must use a two-parent merge commit"
print("verified release promotion accepts dev or a strict lineage-preserving release branch into main")
