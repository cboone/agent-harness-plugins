# JavaScript/TypeScript Makefile

Replace `INSTALL-COMMAND` and `RUN-PREFIX` with the detected package manager equivalents.

```makefile
.PHONY: test lint fmt typecheck clean help

test: ## Run tests
	RUN-PREFIX jest

lint: ## Run ESLint
	RUN-PREFIX eslint .

fmt: ## Check formatting
	RUN-PREFIX prettier --check .

typecheck: ## Run TypeScript type check
	RUN-PREFIX tsc --noEmit

clean: ## Remove build artifacts
	rm -rf dist node_modules/.cache

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
```

Adapt targets to match `package.json` scripts when they exist (e.g., if `package.json` has a `test` script, use `npm test` instead of `npx jest`).
