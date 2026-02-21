# Go

## Tools

- **golangci-lint**: Meta-linter that runs multiple Go linters in parallel (govet, errcheck, staticcheck, unused, gosimple, and more).
- **gofmt**: Built-in Go formatter. No install needed.
- **goimports**: Formats code and manages import statements. Part of `golang.org/x/tools`.

## Install

```bash
# Homebrew (recommended)
brew install golangci-lint

# Go install (alternative)
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# goimports
go install golang.org/x/tools/cmd/goimports@latest
```

## Config

Create `.golangci.yml` in the project root:

```yaml
linters:
  enable:
    - errcheck
    - govet
    - gosimple
    - ineffassign
    - staticcheck
    - unused

linters-settings:
  errcheck:
    check-type-assertions: true

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
	gofmt -w .
	goimports -w .

vet: ## Run go vet
	go vet ./...
```

## Notes

- `gofmt` enforces tabs for indentation. This is non-negotiable in Go.
- `golangci-lint` replaces running individual linters manually. It handles caching and parallel execution.
- The config above enables the default set of linters. Add more as needed (e.g., `gocritic`, `revive`, `misspell`).
- `goimports` is a superset of `gofmt` that also manages imports.
