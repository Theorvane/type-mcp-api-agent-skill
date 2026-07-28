## Release-lineage synchronization

Closes #54

Synchronizes the current release-only `main` tip into `dev` before the embedded-generator release promotion.

### Why

`main` (`1bf5063`) was not an ancestor of `dev` (`c698a96`), so direct `dev` → `main` promotion did not meet the repository's ancestry safety rule.

### Candidate lineage

`208d8e0` is a real merge commit with:

- first parent: `c698a96` (`dev`)
- second parent: `1bf5063` (`main`)

Both parents are ancestors of the candidate.

### Verification

- docs contract: **8 OK**
- workspace: **3 OK**
- branch governance: **2 OK**
- release contract: **13 OK**
- engine fast suite: **94 OK**
- contained generated-project E2E: **6/6 OK**
- docs / branch governance / release-promotion validators, `py_compile`, and `git diff --check`: **OK**

### Merge requirement

Merge this synchronization PR using a **merge commit**, not squash, to preserve `main` ancestry in `dev`. No version bump or registry publication occurs in this PR.
