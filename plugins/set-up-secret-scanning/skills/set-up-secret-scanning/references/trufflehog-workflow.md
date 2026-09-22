# TruffleHog GitHub Actions Workflow Template

A single template that works for all repository types. Uses the `cboone/gh-actions` reusable workflow.

## Template

```yaml
name: trufflehog

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
    uses: cboone/gh-actions/.github/workflows/scan-for-secrets.yml@bbe15187a1a8c60caded9295d1d2d90338a0bb93 # v4.1.0
    with:
      tool: trufflehog
```

## Notes

- The reusable workflow handles TruffleHog version pinning, checkout with `fetch-depth: 0`, and configuration internally.
- Runs on pushes to `main` (post-merge) and on every pull request, so verification-based scanning covers both merged code and proposed changes.
- `workflow_dispatch` allows manual triggering from the GitHub Actions UI, useful for re-running verification against live providers on demand.
