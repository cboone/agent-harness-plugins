---
applyTo: ".claude-plugin/marketplace.json,.agents/plugins/marketplace.json,plugins/pr/skills/pr/SKILL.md"
---

# Catalog and PR Issue Review

- Verify catalog state arithmetic with `bin/compute-catalog-state` against the current canonical marketplace. Do not infer totals from a partial diff or generated catalog excerpt. Components are independent sums without carrying.
- In the PR skill, a closing candidate means an identity matching the PR target after follow-up removal. Other connected identities are related issues and do not satisfy the closing-candidate condition. Evaluate the Strategy 3 fallback against the closing list.
