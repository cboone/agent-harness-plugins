# CI Workflow Template

Use this template for `.github/workflows/ci.yml`. Replace `MINIMUM-GO-VERSION` with the minimum Go version specified by the user (e.g., `1.24`).

The Go version matrix should include the minimum version and `stable` (the latest release).

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
    name: Test (Go ${{ matrix.go-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        go-version: ["MINIMUM-GO-VERSION", "stable"]
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: ${{ matrix.go-version }}

      - name: Run tests
        run: go test -race -v ./...

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "MINIMUM-GO-VERSION"

      - name: Run golangci-lint
        uses: golangci/golangci-lint-action@v9

  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "MINIMUM-GO-VERSION"

      - name: Build
        run: go build ./...

  format:
    name: Format
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "MINIMUM-GO-VERSION"

      - name: Check formatting
        run: |
          if [ -n "$(gofmt -l .)" ]; then
            echo "The following files are not formatted:"
            gofmt -l .
            exit 1
          fi

  vulncheck:
    name: Vulnerability check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "MINIMUM-GO-VERSION"

      - name: Install govulncheck
        run: go install golang.org/x/vuln/cmd/govulncheck@latest

      - name: Run govulncheck
        run: govulncheck ./...
```

## Notes

- Five parallel jobs: test, lint, build, format, vulncheck
- The test job uses a Go version matrix (`MINIMUM-GO-VERSION` + `stable`) to verify compatibility across versions
- The lint job uses the official golangci-lint GitHub Action for consistent results
- The format job checks that all files pass `gofmt` (fails CI if not)
- The vulncheck job uses `govulncheck` from the Go team to detect known vulnerabilities in dependencies
- `permissions: contents: read` follows the principle of least privilege
- Libraries benefit from multi-version testing more than CLIs because consumers may use older Go versions
