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
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
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
    - ineffassign
    - nilerr
    - revive
    - staticcheck
    - unused
    # Style
    - godot

  settings:
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
- Quality linters catch real bugs: `errcheck` (unchecked errors), `nilerr` (nil error returns), `bodyclose` (unclosed HTTP bodies), `staticcheck` (comprehensive static analysis).
- Style linters enforce consistency: `godot` (comment periods), `revive` (comprehensive style rules).
- `gocyclo` threshold of 15 is reasonable for most projects.
- `goimports` is a superset of `gofmt` that also manages imports. In v2, both are configured under `formatters`.
