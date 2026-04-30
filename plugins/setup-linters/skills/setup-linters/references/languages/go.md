# Go

## Tools

- **golangci-lint**: Meta-linter that runs multiple Go linters in parallel. Uses v2 configuration format.
- **gofmt**: Built-in Go formatter. No install needed.
- **goimports**: Formats code and manages import statements. Part of `golang.org/x/tools`.

## Install

```bash
# Homebrew (recommended)
brew install golangci-lint

# Go install (alternative)
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.11.4
```

## Config

Create `.golangci.yml` in the project root. Replace `GITHUB-USERNAME` and `PROJECT-NAME` with the actual values:

```yaml
version: "2"

run:
  timeout: 5m

formatters:
  enable:
    - gofmt
    - goimports

  settings:
    goimports:
      local-prefixes:
        - github.com/GITHUB-USERNAME/PROJECT-NAME

linters:
  enable:
    # Quality
    - bodyclose
    - durationcheck
    - errcheck
    - gocritic
    - gocyclo
    - govet
    - ineffassign
    - misspell
    - nilerr
    - revive
    - staticcheck
    - unconvert
    - unparam
    - unused
    # Style
    - godot

  settings:
    gocritic:
      enabled-tags:
        - diagnostic
        - experimental
        - opinionated
        - performance
        - style

    gocyclo:
      min-complexity: 15

    godot:
      capital: false
      scope: declarations

    revive:
      rules:
        - name: blank-imports
        - name: context-as-argument
        - name: context-keys-type
        - name: dot-imports
        - name: error-naming
        - name: error-return
        - name: error-strings
        - name: exported
        - name: increment-decrement
        - name: indent-error-flow
        - name: package-comments
        - name: range
        - name: receiver-naming
        - name: time-naming
        - name: unexported-return
        - name: var-declaration
        - name: var-naming

issues:
  max-issues-per-linter: 0
  max-same-issues: 0
```

## Makefile Targets

```makefile
.PHONY: lint fmt vet

lint: ## Run golangci-lint
	golangci-lint run ./...

fmt: ## Format Go code
	golangci-lint fmt ./...

vet: ## Run go vet
	go vet ./...
```

## Notes

- Uses golangci-lint v2 configuration format (`version: "2"`).
- `goimports` local-prefixes ensures project imports are grouped separately from third-party imports.
- Quality linters catch real bugs: `errcheck` (unchecked errors), `nilerr` (nil error returns), `bodyclose` (unclosed HTTP bodies), `staticcheck` (comprehensive static analysis), `govet` (shadows, printf args), `unconvert` (unnecessary type conversions), `unparam` (unused parameters).
- `gocritic` is enabled with all five tag categories (diagnostic, experimental, opinionated, performance, style) for maximum coverage.
- `misspell` catches spelling mistakes in comments and strings.
- Style linters enforce consistency: `godot` (comment periods), `revive` (comprehensive style rules with 17 configured checks).
- `gocyclo` threshold of 15 is reasonable for most projects.
- `issues` block with `max-issues-per-linter: 0` and `max-same-issues: 0` ensures all findings are reported, not truncated.
- `goimports` is a superset of `gofmt` that also manages imports. In v2, both are configured under `formatters`.
- The `fmt` subcommand (`golangci-lint fmt`) and the `formatters` config section are golangci-lint v2 features. The CI action `golangci/golangci-lint-action@v9` natively supports v2.
