# Agent harness

This directory is versioned engineering infrastructure for `type-mcp-api-agent`.

## Files

- `templates/task-brief.md`: required context and RED/GREEN evidence for multi-behavior changes
- `templates/review-report.md`: independent spec and quality review record
- `checklists/pre-commit.md`: change-level quality gate
- `checklists/release-readiness.md`: publication/release gate
- `scripts/validate_docs.py`: deterministic repository-document validation

## Operating model

1. Product/architecture/API docs establish the decision.
2. A GitHub Issue narrows one implementation intent.
3. The branch task brief records scope, assumptions, test-first evidence, and verification.
4. A separate reviewer records specification and code-quality findings.
5. The PR is opened only after the checklist passes.

The harness is not runtime code. Do not import it from generated projects or the generator package.
