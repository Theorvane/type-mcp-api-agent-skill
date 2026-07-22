from pathlib import Path

workflow = Path(".github/workflows/verify.yml").read_text(encoding="utf-8")
assert "branches: [dev, main]" in workflow, "verify workflow must cover dev and main"
print("verified dev integration and main release workflow coverage")
