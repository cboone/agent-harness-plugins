# Shell Makefile

Replace `SCRIPT-DIR` with the directory containing shell scripts (e.g., `scripts`, `bin`, or `.`).

```makefile
.PHONY: lint fmt help

lint: ## Run ShellCheck
	shellcheck SCRIPT-DIR/*.sh

fmt: ## Check formatting
	shfmt -d SCRIPT-DIR/

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
```
