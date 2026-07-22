from pathlib import Path

workflow = Path(".github/workflows/release-promotion.yml").read_text(encoding="utf-8")
assert "branches: [main]" in workflow, "release gate must target main"
assert "HEAD_REF: ${{ github.head_ref }}" in workflow, "release gate must read the PR head"
assert 'test "$HEAD_REF" = "dev"' in workflow, "only dev may promote to main"
print("verified release promotion accepts only dev into main")
