# Secret-scanning workflow caller names

These tests check the YAML emitted from the reference templates.
Tool-specific caller IDs give the reusable workflow's shared `Validate inputs`
job distinct check names when both scanners are enabled.

## Gitleaks caller

```scrut
$ awk '/^jobs:$/ { jobs = 1; next } jobs && /^  [[:alnum:]_-]+:$/ { print; exit }' "${REPO_ROOT}/plugins/set-up-secret-scanning/skills/set-up-secret-scanning/references/gitleaks-workflow.md"
  gitleaks:
```

## TruffleHog caller

```scrut
$ awk '/^jobs:$/ { jobs = 1; next } jobs && /^  [[:alnum:]_-]+:$/ { print; exit }' "${REPO_ROOT}/plugins/set-up-secret-scanning/skills/set-up-secret-scanning/references/trufflehog-workflow.md"
  trufflehog:
```
