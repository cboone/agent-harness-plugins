# Zig Makefile

```makefile
.PHONY: test lint fmt fmt-check build run clean release help

test: ## Run tests
	zig build test

lint: fmt-check build ## Check formatting and build (Zig has no separate linter)

fmt: ## Format code
	zig fmt src/ build.zig

fmt-check: ## Check formatting without modifying files
	zig fmt --check src/ build.zig

build: ## Build the project
	zig build

run: ## Build and run the project
	zig build run

clean: ## Remove build artifacts
	rm -rf .zig-cache/ zig-out/

release: ## Cross-compile release binaries for all targets
	@for target in x86_64-linux aarch64-linux x86_64-macos aarch64-macos x86_64-windows; do \
		echo "Building for $${target}..."; \
		zig build -Dtarget="$${target}" -Doptimize=ReleaseSafe; \
	done

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
```
