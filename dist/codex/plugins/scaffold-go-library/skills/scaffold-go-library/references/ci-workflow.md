# CI Workflow Template

Use this template for `.github/workflows/ci.yml`. The minimum Go version is read from `go.mod` automatically. Uses two `cboone/gh-actions` reusable workflow calls: one for the minimum supported Go version (all checks, reads `go.mod`) and one for the latest stable Go release (tests only).

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
    uses: cboone/gh-actions/.github/workflows/run-go-ci.yml@bbe15187a1a8c60caded9295d1d2d90338a0bb93 # v4.1.0
    with:
      go-version-file: "go.mod"
      run-lint: true
      run-format-check: true
      run-build: true

  ci-stable:
    uses: cboone/gh-actions/.github/workflows/run-go-ci.yml@bbe15187a1a8c60caded9295d1d2d90338a0bb93 # v4.1.0
    with:
      go-version: "stable"
```

## Notes

- `paths-ignore` skips CI for documentation and agent configuration changes; remove `*.md` if Markdown is source code (e.g., Scrut CLI tests in `tests/scrut/` are nested and NOT ignored)
- Concurrency groups cancel in-progress runs when new commits are pushed to the same branch/PR
- Two reusable workflow calls implement the Go version matrix: `ci-minimum` reads the minimum version from `go.mod` and runs all checks; `ci-stable` runs tests against the latest stable Go release
- Each call creates its own set of parallel jobs internally using Makefile targets
- `run-lint: true` enables golangci-lint with SHA-256 verification
- `run-lint` installs golangci-lint 2.13.2, up from 2.11.4 before v4.1.0. A first run on the newer release can report findings the older one did not. Pin `golangci-lint-version` to a known release while working through them.
- `run-format-check: true` enables the gofmt/goimports formatting check
- `run-build: true` enables the `go build ./...` check
- `permissions: contents: read` follows the principle of least privilege
- Libraries benefit from multi-version testing more than CLIs because consumers may use older Go versions
- The stable call passes no `run-*` inputs, so it runs test, vet and lint: `run-lint` defaults to true, while `run-format-check` and `run-build` default to false. Formatting and build results do not vary by Go version, so leaving those two off is deliberate. Lint results do not vary either, so set `run-lint: false` on this call if the duplicate golangci-lint run is not worth the runner time
