# CI Workflow Template

Use this template for `.github/workflows/ci.yml`. Replace `MINIMUM-GO-VERSION` with the minimum Go version specified by the user (e.g., `1.24`). Uses two `cboone/gh-actions` reusable workflow calls: one for the minimum Go version (all checks) and one for stable (tests only).

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
      go-version: "MINIMUM-GO-VERSION"
      run-lint: true
      run-format-check: true
      run-build: true

  ci-stable:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@f69487c36f4e217afe28ea631de39edf17d35238 # v2.1.4
    with:
      go-version: "stable"
```

## Notes

- `paths-ignore` skips CI for documentation and agent configuration changes; remove `*.md` if Markdown is source code (e.g., Scrut CLI tests in `tests/scrut/` are nested and NOT ignored)
- Concurrency groups cancel in-progress runs when new commits are pushed to the same branch/PR
- Two reusable workflow calls implement the Go version matrix: one for the minimum supported version (all checks) and one for stable (tests only)
- Each call creates its own set of parallel jobs internally using Makefile targets
- `run-lint: true` enables golangci-lint with SHA-256 verification
- `run-format-check: true` enables the gofmt/goimports formatting check
- `run-build: true` enables the `go build ./...` check
- `permissions: contents: read` follows the principle of least privilege
- Libraries benefit from multi-version testing more than CLIs because consumers may use older Go versions
- The stable call uses defaults (test only) since lint, format, and build results do not vary by Go version
