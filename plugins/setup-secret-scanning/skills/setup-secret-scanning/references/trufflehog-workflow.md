# TruffleHog GitHub Actions Workflow Template

A single template that works for all repository types. Uses the `cboone/gh-actions` reusable workflow.

## Template

```yaml
name: trufflehog

on:
  push:
    branches: [main]
  workflow_dispatch:
  schedule:
    - cron: "0 4 * * 6"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  scan:
    uses: cboone/gh-actions/.github/workflows/secret-scan.yml@e4e9f34f54041223e72f0d6241efede27a698fa1 # v1.0.0
    with:
      tool: trufflehog
```

## Notes

- The reusable workflow handles TruffleHog version pinning, checkout with `fetch-depth: 0`, and configuration internally.
- The `schedule` trigger runs a weekly scan on Saturdays at 4 AM UTC, complementing gitleaks' daily scans.
- `workflow_dispatch` allows manual triggering from the GitHub Actions UI.
- Runs on pushes to `main` only (post-merge), since gitleaks already covers per-push and per-PR pattern matching.
