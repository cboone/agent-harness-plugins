# Release Workflow Template

Use this template for `.github/workflows/release.yml`. No replacements needed.

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: stable

      - name: Run GoReleaser
        uses: goreleaser/goreleaser-action@v6
        with:
          distribution: goreleaser
          version: latest
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Notes

- Triggers on version tags (e.g., `v0.1.0`, `v1.0.0`)
- Uses `fetch-depth: 0` to get full git history for changelog generation
- Only needs `GITHUB_TOKEN` (no `HOMEBREW_TAP_TOKEN` since libraries have no Homebrew formula)
- `permissions: contents: write` is required for GoReleaser to create the GitHub release
- GoReleaser will skip the build step (configured in `.goreleaser.yml`) and only generate the changelog and release
- Uses `go-version: stable` since the release workflow only needs to run GoReleaser, not compile code
