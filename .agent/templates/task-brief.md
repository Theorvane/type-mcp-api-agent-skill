# Task brief: <issue-number> — <title>

**Status:** draft | in-progress | review | complete
**Issue:** <GitHub URL>
**Branch:** `<type>/<issue-number>-<short-description>`
**Owner:** <name/agent>

## Goal

<One observable user outcome.>

## Source references

- Product: `<path>`
- Architecture/API: `<path>`
- Approved design/manifest: `<path or URL>`

## Scope

### Included

- <behavior>

### Excluded

- <non-goal>

## Safety and contract notes

- Source input: <untrusted boundary and validation>
- Secrets: <where values may appear; normally nowhere in artifacts>
- Side effects: <approval/policy/publish boundary>
- Compatibility: <npm/package/runtime concerns>

## Test-first evidence

| Stage | Command | Expected/observed result |
| --- | --- | --- |
| Red | `<focused test command>` | <failure proving missing behavior> |
| Green | `<focused test command>` | <passing behavior> |
| Regression | `<affected suite command>` | <result> |

## Verification

- [ ] Lint
- [ ] Typecheck
- [ ] Unit/integration tests
- [ ] Generator or generated-project E2E test, when applicable
- [ ] Build/package validation, when applicable
- [ ] `git diff --check`
- [ ] Documentation updated
- [ ] Independent specification review recorded
- [ ] Independent code-quality review recorded

## Review notes

- <finding / resolution>
