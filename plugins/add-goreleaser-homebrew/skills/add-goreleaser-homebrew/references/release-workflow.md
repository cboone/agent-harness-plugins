# Release Workflow Template

Use this template for `.github/workflows/release.yml`. Uses the `cboone/gh-actions` reusable workflow, which handles Go setup, GoReleaser installation, and release execution internally. No placeholder replacements are needed; the workflow is project-name-independent.

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
    uses: cboone/gh-actions/.github/workflows/release-go-binaries.yml@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0
    with:
      go-version-file: go.mod
    secrets:
      HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}
```

## macOS-Only Variant

For projects that only target macOS, add the `runs-on` input:

```yaml
jobs:
  release:
    uses: cboone/gh-actions/.github/workflows/release-go-binaries.yml@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0
    with:
      go-version-file: go.mod
      runs-on: macos-latest
    secrets:
      HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}
```

This ensures the build environment matches the target platform, which matters for projects that depend on macOS-specific APIs or frameworks.

## Notes

- Concurrency uses `cancel-in-progress: false` to avoid interrupting active releases
- Triggers on version tags (`v*` matches `v1.0.0`, `v0.1.0-rc1`, etc.)
- The reusable workflow handles checkout with `fetch-depth: 0`, Go setup, GoReleaser installation, and the release command internally
- `go-version-file: go.mod` reads the Go version from `go.mod` rather than hardcoding it
- `HOMEBREW_TAP_TOKEN` must be added as a repository secret (see "Reference: HOMEBREW_TAP_TOKEN Setup" for creation and configuration)
- `GITHUB_TOKEN` is provided automatically by GitHub Actions and its permissions are controlled by the caller workflow's `permissions:` block
