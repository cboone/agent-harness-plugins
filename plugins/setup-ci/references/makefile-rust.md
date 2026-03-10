# Rust Makefile

```makefile
.PHONY: test lint fmt build clean help

test: ## Run tests
	cargo test

lint: ## Run clippy
	cargo clippy -- -D warnings

fmt: ## Check formatting
	cargo fmt -- --check

build: ## Build the project
	cargo build

clean: ## Remove build artifacts
	cargo clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
```
