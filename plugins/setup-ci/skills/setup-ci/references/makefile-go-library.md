# Go Library Makefile

Adapted from the scaffold-go-library template.

```makefile
.DEFAULT_GOAL := all

.PHONY: all
all: fmt vet lint vuln test build ## Run all checks

.PHONY: build
build: ## Build all packages
	go build ./...

.PHONY: clean
clean: ## Remove build artifacts
	rm -rf dist/
	rm -f coverage.html coverage.out

.PHONY: coverage
coverage: ## Generate HTML coverage report
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"

.PHONY: fmt
fmt: ## Check formatting (exits non-zero if files need formatting)
	@test -z "$$(gofmt -l .)" || { gofmt -l . && exit 1; }

.PHONY: format
format: ## Format code (write mode)
	go fmt ./...

.PHONY: help
help: ## Show available targets
	@echo "Available targets:"
	@echo "  all          Run fmt, vet, lint, vuln, test, build (default)"
	@echo "  build        Build all packages"
	@echo "  clean        Remove build artifacts"
	@echo "  coverage     Generate HTML coverage report"
	@echo "  fmt          Check formatting"
	@echo "  format       Format code (write mode)"
	@echo "  help         Show this help message"
	@echo "  lint         Run golangci-lint"
	@echo "  test         Run tests with race detector"
	@echo "  tools        Install development tools"
	@echo "  vet          Run go vet"
	@echo "  vuln         Run govulncheck"

.PHONY: lint
lint: ## Run golangci-lint
	golangci-lint run ./...

.PHONY: test
test: ## Run tests with race detector
	go test -v -race ./...

.PHONY: tools
tools: ## Install development tools
	go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.11.4
	go install golang.org/x/vuln/cmd/govulncheck@v1.1.4

.PHONY: vet
vet: ## Run go vet
	go vet ./...

.PHONY: vuln
vuln: ## Run govulncheck
	govulncheck ./...
```
