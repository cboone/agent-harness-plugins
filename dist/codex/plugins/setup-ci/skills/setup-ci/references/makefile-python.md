# Python Makefile

```makefile
.PHONY: test lint fmt clean help

test: ## Run tests
	uv run pytest

lint: ## Run ruff lint
	uvx ruff check .

fmt: ## Check formatting
	uvx ruff format --check .

clean: ## Remove build artifacts
	rm -rf dist .pytest_cache .ruff_cache __pycache__

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
```
