# CI Workflow Template

Use this template for `.github/workflows/ci.yml`. Uses the `cboone/gh-actions` reusable workflow, which creates parallel jobs for test, vet, lint, format-check, and more.

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
      run-lint: true
      run-format-check: true
```

## Notes

- `paths-ignore` skips CI for documentation and agent configuration changes; remove `*.md` if Markdown is source code (e.g., Scrut CLI tests in `tests/scrut/` are nested and NOT ignored)
- Concurrency groups cancel in-progress runs when new commits are pushed to the same branch/PR
- `permissions: contents: read` follows the principle of least privilege
- The reusable workflow creates parallel jobs internally (test, vet, lint, format-check) using Makefile targets (`make test`, `make vet`, `make fmt`, etc.)
- `run-lint: true` enables golangci-lint with SHA-256 verification
- `run-format-check: true` enables the gofmt/goimports formatting check
- The reusable workflow uses `go-version-file: go.mod` to stay current automatically
