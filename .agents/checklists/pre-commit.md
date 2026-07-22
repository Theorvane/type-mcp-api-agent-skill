# Pre-commit checklist

Complete every applicable item before committing a non-bootstrap change.

## Scope and traceability

- [ ] A focused GitHub Issue exists and the branch name contains its number.
- [ ] The issue and task brief cite the relevant product/architecture/API documents.
- [ ] The diff contains one coherent intent only.
- [ ] Generator/CLI logic has not been added to this skill repository.
- [ ] Generated artifacts, downloaded specs, credentials, and build output are absent.

## Test-first and contracts

- [ ] A focused test/fixture assertion was written before implementation and observed failing.
- [ ] The smallest implementation makes the focused test pass.
- [ ] CLI command results and external source data are parsed as `unknown` and validated.
- [ ] CLI package/version, manifest schema, and protocol compatibility are verified.
- [ ] Public behavior and A/E/X cases are documented.
- [ ] Markdown/HTML extraction has a manifest approval gate.
- [ ] Generated projects use `type-mcp` from npm rather than copied source.

## Safety

- [ ] Secrets are represented only as environment-variable references.
- [ ] No source/output/log includes a credential or unsafe upstream error.
- [ ] Mutating endpoint behavior is runtime-policy-gated.
- [ ] GitHub create/push behavior is behind explicit final confirmation.
- [ ] The skill fails closed on unavailable/incompatible CLI rather than using a substitute.

## Verification

- [ ] `python3 .agents/scripts/validate_docs.py`
- [ ] `python3 -m py_compile .agents/scripts/validate_docs.py`
- [ ] skill-to-CLI fixture contract test, when executable behavior changes
- [ ] `npm run lint` / `npm run typecheck` / `npm test` / `npm run build`, when package exists
- [ ] generated-project E2E verification, when orchestration changes
- [ ] `git diff --check`
- [ ] `git status --short --branch`
