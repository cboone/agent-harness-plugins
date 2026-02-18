# Makefile Template

Use this template for `Makefile`. Replace `PROJECT-NAME` with the project name.

```makefile
# PROJECT-NAME Makefile

.DEFAULT_GOAL := all

# Run all checks
.PHONY: all
all: fmt vet lint test build

# Build all packages
.PHONY: build
build:
	go build ./...

# Remove build artifacts
.PHONY: clean
clean:
	rm -rf dist/
	rm -f coverage.html coverage.out

# Generate HTML coverage report
.PHONY: coverage
coverage:
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"

# Format code
.PHONY: fmt
fmt:
	go fmt ./...

# Show available targets
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all          Run fmt, vet, lint, test, build (default)"
	@echo "  build        Build all packages"
	@echo "  clean        Remove build artifacts"
	@echo "  coverage     Generate HTML coverage report"
	@echo "  fmt          Format code"
	@echo "  help         Show this help message"
	@echo "  lint         Run golangci-lint"
	@echo "  test         Run tests with race detector"
	@echo "  tools        Install development tools"
	@echo "  vet          Run go vet"

# Run golangci-lint
.PHONY: lint
lint:
	golangci-lint run ./...

# Run tests with race detector
.PHONY: test
test:
	go test -race ./...

# Install development tools
.PHONY: tools
tools:
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	go install github.com/goreleaser/goreleaser/v2@latest

# Run go vet
.PHONY: vet
vet:
	go vet ./...
```

## Notes

- No `VERSION` or `BINARY` variables -- libraries have no binary output
- The `all` target runs the full quality pipeline: format, vet, lint, test, build
- The `coverage` target generates an HTML report for reviewing test coverage
- The `tools` target installs golangci-lint and goreleaser for local development
- Targets are listed alphabetically for easy scanning
- No `demo` or `test-visual` targets -- add project-specific targets as needed
