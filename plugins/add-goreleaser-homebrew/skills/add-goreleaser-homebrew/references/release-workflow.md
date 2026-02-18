# Release Workflow Template

Use this template for `.github/workflows/release.yml`. No placeholder replacements are needed; the workflow is project-name-independent.

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write

jobs:
  goreleaser:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - uses: goreleaser/goreleaser-action@v6
        with:
          version: "~> v2"
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}
```

## macOS-Only Variant

For projects that only target macOS, change the runner:

```yaml
jobs:
  goreleaser:
    runs-on: macos-latest
```

This ensures the build environment matches the target platform, which matters for projects that depend on macOS-specific APIs or frameworks.

## Notes

- Triggers on version tags (`v*` matches `v1.0.0`, `v0.1.0-rc1`, etc.)
- `fetch-depth: 0` fetches full git history (required for GoReleaser changelog generation)
- `go-version-file: go.mod` reads the Go version from `go.mod` rather than hardcoding it, so the workflow stays in sync with the project automatically
- `version: "~> v2"` uses the latest GoReleaser v2.x release
- `GITHUB_TOKEN` is provided automatically by GitHub Actions
- `HOMEBREW_TAP_TOKEN` must be added as a repository secret (a PAT with repo scope on the user's `homebrew-tap` repository)
- `--clean` removes previous build artifacts before releasing
