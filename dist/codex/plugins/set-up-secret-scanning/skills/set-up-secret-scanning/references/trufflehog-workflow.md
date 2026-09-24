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
- A scan that reports a verified or unknown result now fails the job. The workflow passes `--fail`, so TruffleHog exits 183 rather than succeeding. Before v4 it reported findings and still exited 0, so a repository moving from an older pin can see this job go red for the first time on findings that were always there. Read the first failure as a backlog, not a regression.
- `--no-update` keeps the checksum-verified version the workflow installed. Without it TruffleHog replaces itself mid-scan with whatever upstream has published, which defeats both the pin and its checksum.
- To keep a reviewed credential-shaped string, such as a test fixture in a commit that must not be rewritten, pass `trufflehog-allowlist` with a JSON file of reviewed findings. An entry matches only when `commit`, `path`, `line` and `detector` all agree, so moving the file or changing any one field fails the scan again. A verified finding is never allowlisted, and an unused entry warns rather than fails.
