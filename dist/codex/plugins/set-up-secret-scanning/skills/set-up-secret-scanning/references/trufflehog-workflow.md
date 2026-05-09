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
    uses: cboone/gh-actions/.github/workflows/scan-for-secrets.yml@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0
    with:
      tool: trufflehog
```

## Notes

- The reusable workflow handles TruffleHog version pinning, checkout with `fetch-depth: 0`, and configuration internally.
- Runs on pushes to `main` (post-merge) and on every pull request, so verification-based scanning covers both merged code and proposed changes.
- `workflow_dispatch` allows manual triggering from the GitHub Actions UI, useful for re-running verification against live providers on demand.
