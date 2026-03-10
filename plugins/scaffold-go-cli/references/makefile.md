# Makefile Template

Use this template for the project Makefile. Replace `PROJECT-NAME` with the actual binary name.

```makefile
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
BINARY  := PROJECT-NAME
OUTDIR  := bin

LDFLAGS := -ldflags "-X main.version=$(VERSION)"

.PHONY: build test lint vet fmt vuln clean cover tidy help

build: ## Build the binary
	mkdir -p $(OUTDIR)
	go build $(LDFLAGS) -o $(OUTDIR)/$(BINARY) .

test: ## Run tests with race detector
	go test -v -race ./...

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

- Self-documenting: each target has a `## Comment` that `make help` displays
- Version is derived from git tags, falling back to `"dev"`
- Binary output goes to `bin/` to keep the project root clean
- `fmt` target checks formatting without modifying files (CI-friendly); use `go fmt ./...` directly for write-mode formatting
- `lint` runs only `golangci-lint`; repos with broader linting should use a separate `lint-all` umbrella target
- `vuln` assumes `govulncheck` is installed (`go install golang.org/x/vuln/cmd/govulncheck@latest`)
- The five targets `vet`, `test`, `lint`, `build`, and `fmt` are required by `go-ci.yml@v2`, which calls them via Makefile
