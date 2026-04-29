# Gitleaks GitHub Actions Workflow Template

A single template that works for all repository types. Uses the `cboone/gh-actions` reusable workflow, which runs the gitleaks CLI directly (no license required).

## Template

```yaml
name: gitleaks

on:
  push:
  pull_request:
  workflow_dispatch:
  schedule:
    - cron: "0 4 * * *"

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
- The `schedule` trigger runs a daily scan at 4 AM UTC to catch secrets introduced outside of PR workflows (e.g., direct pushes).
- `workflow_dispatch` allows manual triggering from the GitHub Actions UI.
- The reusable workflow handles checkout with `fetch-depth: 0` and tool installation internally.
- `permissions: contents: read` grants the minimum access needed for scanning. Reusable workflows cannot elevate permissions beyond what the caller grants.
