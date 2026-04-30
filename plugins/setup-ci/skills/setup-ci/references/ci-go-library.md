# Go Library CI Workflow

Use this template for Go library projects (no `main.go` at root, no `cmd/` directory). The minimum Go version is read from `go.mod` automatically. Uses two `cboone/gh-actions` reusable workflow calls: one for the minimum supported Go version (all checks, reads `go.mod`) and one for the latest stable Go release (tests only).

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  ci-minimum:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@f69487c36f4e217afe28ea631de39edf17d35238 # v2.1.4
    with:
      go-version-file: "go.mod"
      run-lint: true
      run-format-check: true
      run-build: true

  ci-stable:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@f69487c36f4e217afe28ea631de39edf17d35238 # v2.1.4
    with:
      go-version: "stable"
```

## Notes

- Two reusable workflow calls implement the Go version matrix: `ci-minimum` reads the minimum version from `go.mod` and runs all checks; `ci-stable` runs tests against the latest stable Go release
- Each call creates its own set of parallel jobs internally
- Libraries benefit from multi-version testing more than CLIs because consumers may use older Go versions
- `run-lint: true` enables golangci-lint with SHA-256 verification
- `run-format-check: true` enables the gofmt/goimports formatting check
- `run-build: true` enables the `go build ./...` check
- The stable call uses defaults (test only) since lint, format, and build results do not vary by Go version
