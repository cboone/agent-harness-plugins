# CI Workflow Template

Use this template for `.github/workflows/ci.yml`.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - name: Run tests
        run: make test

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - name: Run vet
        run: make vet

      - name: Check formatting
        run: make fmt
```

## Notes

- Triggers on pushes to main and on pull requests targeting main
- Uses `go-version-file: go.mod` instead of pinning a Go version (stays current automatically)
- Test and lint are separate jobs so they run in parallel
- The lint job runs `vet` and `fmt` (both are fast and catch different issues)
- `golangci-lint` is not included in CI by default; add it when the project is ready for stricter linting
