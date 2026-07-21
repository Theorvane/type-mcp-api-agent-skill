# Pre-commit checklist

Complete every applicable item before committing a non-bootstrap change.

## Scope and traceability

- [ ] A focused GitHub Issue exists and the branch name contains its number.
- [ ] The issue and task brief cite the relevant product/architecture/API documents.
- [ ] The diff contains one coherent intent only.
- [ ] Generated artifacts, downloaded specs, credentials, and build output are absent.

## Test-first and contracts

- [ ] A focused test was written before implementation and observed failing.
- [ ] The smallest implementation makes the focused test pass.
- [ ] External source data is parsed as `unknown` and validated.
- [ ] Public behavior and A/E/X cases are documented.
- [ ] Markdown/HTML extraction has a manifest approval gate.
- [ ] Generated projects use `type-mcp` from npm rather than copied source.

## Safety

- [ ] Secrets are represented only as environment-variable references.
- [ ] No source/output/log includes a credential or unsafe upstream error.
- [ ] Mutating endpoint behavior is runtime-policy-gated.
- [ ] GitHub create/push behavior is behind explicit final confirmation.

## Verification

- [ ] `python3 .agent/scripts/validate_docs.py`
- [ ] `npm run lint` (when package exists)
- [ ] `npm run typecheck` (when package exists)
- [ ] `npm test` (when package exists)
- [ ] `npm run build` (when package exists)
- [ ] generated-project E2E verification (when generator changes)
- [ ] `git diff --check`
- [ ] `git status --short --branch`
