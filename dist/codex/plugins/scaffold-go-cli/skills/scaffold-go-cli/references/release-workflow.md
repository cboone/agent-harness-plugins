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
    uses: cboone/gh-actions/.github/workflows/release-go-binaries.yml@bbe15187a1a8c60caded9295d1d2d90338a0bb93 # v4.1.0
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
