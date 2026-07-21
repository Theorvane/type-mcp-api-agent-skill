# Agent harness

This directory is versioned engineering infrastructure for `type-mcp-api-agent`, the Hermes skill/orchestration repository.

## Files

- `templates/task-brief.md`: required context and RED/GREEN evidence for multi-behavior changes
- `templates/review-report.md`: independent spec and quality review record
- `checklists/pre-commit.md`: change-level quality gate
- `checklists/release-readiness.md`: publication/release gate
- `scripts/validate_docs.py`: deterministic repository-document and skill-contract validation
- `fixtures/cli/` (future): controlled fake CLI fixtures for success, incompatibility, malformed-manifest, and side-effect-denial tests

## Operating model

1. Product/architecture/API docs establish the cross-repository decision.
2. A GitHub Issue narrows one implementation intent in either the skill or CLI repository.
3. The branch task brief records scope, assumptions, test-first evidence, and verification.
4. Skill behavior is tested against controlled CLI fixtures and later against released CLI artifacts.
5. A separate reviewer records specification and code-quality findings.
6. The PR is opened only after the checklist passes.

The harness is not CLI/generator runtime code. The skill repository must not host a copied CLI implementation, generated project, downloaded spec, or credential.
