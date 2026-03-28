# Rust Makefile

```makefile
.PHONY: test lint fmt build deny audit typos changelog clean help

test: ## Run tests (cargo nextest, falls back to cargo test)
	@command -v cargo-nextest >/dev/null 2>&1 && cargo nextest run || cargo test

lint: ## Run clippy
	cargo clippy -- -D warnings

fmt: ## Check formatting
	cargo fmt -- --check

build: ## Build the project
	cargo build

deny: ## Check dependencies with cargo-deny
	cargo deny check

audit: ## Audit dependencies for vulnerabilities
	cargo audit

typos: ## Check for typos
	typos

changelog: ## Generate changelog from conventional commits
	git cliff -o CHANGELOG.md

clean: ## Remove build artifacts
	cargo clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
```
