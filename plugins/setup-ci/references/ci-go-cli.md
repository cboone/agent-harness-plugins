# Go CLI CI Workflow

Use this template for Go CLI projects (projects with `main.go` or a `cmd/` directory). Uses the `cboone/gh-actions` reusable workflow, which creates parallel jobs for test, vet, format-check, and optionally lint and build.

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
  ci:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v2
    with:
      go-version-file: go.mod
      run-lint: false
      run-format-check: true
```

## Notes

- Uses `go-version-file: go.mod` instead of pinning a Go version (stays current automatically)
- The reusable workflow creates parallel jobs internally (test, vet, format-check, and optionally lint and build) using Makefile targets
- `run-lint: false` because golangci-lint is not included by default for Go CLI projects; set to `true` when the project is ready for stricter linting
- `run-format-check: true` enables the gofmt/goimports formatting check
