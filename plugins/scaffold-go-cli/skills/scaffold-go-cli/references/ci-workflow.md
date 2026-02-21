# CI Workflow Template

Use this template for `.github/workflows/ci.yml`.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - name: Run tests
        run: make test

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - name: Run vet
        run: make vet

      - name: Check formatting
        run: make fmt

  vulncheck:
    name: Vulnerability check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - name: Install govulncheck
        run: go install golang.org/x/vuln/cmd/govulncheck@latest

      - name: Run govulncheck
        run: govulncheck ./...
```

## Notes

- Triggers on pushes to main and on pull requests targeting main
- `permissions: contents: read` follows the principle of least privilege
- Uses `go-version-file: go.mod` instead of pinning a Go version (stays current automatically)
- Test, lint, and vulncheck are separate jobs so they run in parallel
- The lint job runs `vet` and `fmt` (both are fast and catch different issues)
- The vulncheck job uses `govulncheck` from the Go team to detect known vulnerabilities in dependencies
- `golangci-lint` is not included in CI by default; add it when the project is ready for stricter linting
