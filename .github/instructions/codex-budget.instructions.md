---
applyTo: "bin/validate-plugins,tests/scrut/validate-plugins-catalog.md,tests/fixtures/validate-plugin-fixture"
---

# Codex budget review instructions

These rule 17 patterns are intentional and have been checked:

- **Rule 17 charges a share of listed skills, after withholding**: A skill withheld from implicit invocation is excluded before the enabled share is taken, because Codex never lists it. Taking the share over the remaining listed skills is intentional; do not flag it as double counting or as under-charging withheld skills. The withheld-skill scrut case forces `CODEX_ENABLED_SKILL_PERCENT=100` on purpose, so another skill cannot replace the withheld one among the counted share.
- **Piped scrut cases still assert exit status**: A case written as `{ COMMAND; echo "exit ${?}"; } | awk ...` records the fixture's own exit status as an `exit N` output line, which the expected output pins. The pipeline itself exits 0, so the block correctly has no `[N]` line. Do not flag it as dropping the exit status.
