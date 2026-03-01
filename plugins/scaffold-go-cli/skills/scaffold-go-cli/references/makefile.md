# Makefile Template

Use this template for the project Makefile. Replace `PROJECT-NAME` with the actual binary name.

```makefile
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
BINARY  := PROJECT-NAME
OUTDIR  := bin

LDFLAGS := -ldflags "-X main.version=$(VERSION)"

.DEFAULT_GOAL := all

.PHONY: all build test lint vet fmt vuln clean cover tidy help

all: fmt vet lint vuln test build ## Run all checks and build

build: ## Build the binary
	mkdir -p $(OUTDIR)
	go build $(LDFLAGS) -o $(OUTDIR)/$(BINARY) .

test: ## Run tests
	go test ./...

lint: ## Run golangci-lint
	golangci-lint run ./...

vet: ## Run go vet
	go vet ./...

fmt: ## Check formatting (exits non-zero if files need formatting)
	@test -z "$$(gofmt -l .)" || { gofmt -l . && exit 1; }

vuln: ## Run govulncheck
	govulncheck ./...

clean: ## Remove build artifacts
	rm -rf $(OUTDIR) dist coverage.out

cover: ## Run tests with coverage
	go test -coverprofile=coverage.out ./...
	go tool cover -func=coverage.out

tidy: ## Tidy go.mod
	go mod tidy

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
```

## Notes

- The `all` target is the default goal and runs the full quality pipeline: format, vet, lint, vuln, test, build
- Self-documenting: each target has a `## Comment` that `make help` displays
- Version is derived from git tags, falling back to `"dev"`
- Binary output goes to `bin/` to keep the project root clean
- `fmt` target checks formatting without modifying files (CI-friendly)
- `lint` assumes `golangci-lint` is installed (`brew install golangci-lint`)
- `vuln` assumes `govulncheck` is installed (`go install golang.org/x/vuln/cmd/govulncheck@latest`)
