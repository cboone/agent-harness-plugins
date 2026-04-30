# Gitleaks GitHub Actions Workflow Template

A single template that works for all repository types. Uses the `cboone/gh-actions` reusable workflow, which runs the gitleaks CLI directly (no license required).

## Template

```yaml
name: gitleaks

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  scan:
    uses: cboone/gh-actions/.github/workflows/secret-scan.yml@e4e9f34f54041223e72f0d6241efede27a698fa1 # v1.0.0
    with:
      tool: gitleaks
```

## Notes

- The reusable workflow uses the gitleaks CLI directly, not `gitleaks/gitleaks-action`. The CLI works without a license for both personal and organization repositories.
- Runs on pushes to `main` (post-merge) and on every pull request, so all merged code is scanned and proposed changes are scanned before merge.
- `workflow_dispatch` allows manual triggering from the GitHub Actions UI, useful for re-scanning history after a gitleaks rule update.
- The reusable workflow handles checkout with `fetch-depth: 0` and tool installation internally.
- `permissions: contents: read` grants the minimum access needed for scanning. Reusable workflows cannot elevate permissions beyond what the caller grants.
