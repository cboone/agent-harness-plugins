# Release Workflow Template

Use this template for `.github/workflows/release.yml`. Uses the `cboone/gh-actions` reusable workflow, which handles Go setup, GoReleaser installation, and release execution internally.

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents: write

jobs:
  release:
    uses: cboone/gh-actions/.github/workflows/go-release.yml@e4e9f34f54041223e72f0d6241efede27a698fa1 # v1.0.0
    with:
      go-version-file: go.mod
    secrets:
      HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}
```

## Notes

- Triggers on version tags (`v*` matches `v1.0.0`, `v0.1.0-rc1`, etc.)
- Concurrency uses `cancel-in-progress: false` to avoid interrupting active releases
- The reusable workflow handles checkout with `fetch-depth: 0`, Go setup, GoReleaser installation, and the release command internally
- `GITHUB_TOKEN` is provided automatically by GitHub Actions and its permissions are controlled by the caller workflow's `permissions:` block
- `HOMEBREW_TAP_TOKEN` must be added as a repository secret (see "Reference: HOMEBREW_TAP_TOKEN Setup" for creation and configuration)
