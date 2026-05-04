# Makefile Template

Use this template for `Makefile`.

```makefile
MATHLIB_BUILD_DIR := .lake/packages/mathlib/.lake/build/lib/lean

build: _check-mathlib-cache ## Build the LEAN-NAMESPACE library
	lake build LEAN-NAMESPACE

bootstrap: ## Bootstrap worktree (lake update, cache get, build)
	bin/bootstrap-worktree

lean-lint: _check-mathlib-cache ## Run Lean linter (batteries)
	lake lint

test: _check-mathlib-cache ## Run Lean tests
	lake test

lint-markdown: ## Lint Markdown files
	markdownlint-cli2 "**/*.md"

lint-spelling: ## Check spelling with cspell
	cspell --no-progress .

lint: lint-markdown lint-spelling ## Run text linters

check: lint lean-lint build test ## Lint, build, and test

clean: ## Remove Lake build artifacts
	lake clean

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | \
		awk -F ':.*## ' '{printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

_check-mathlib-cache:
	@if [ ! -d "$(MATHLIB_BUILD_DIR)" ] || { [ ! -f "$(MATHLIB_BUILD_DIR)/Mathlib.olean" ] && [ -z "$$(find "$(MATHLIB_BUILD_DIR)/Mathlib" -name '*.olean' -print -quit 2>/dev/null)" ]; }; then \
		echo "Error: Mathlib prebuilt artifacts not found." >&2; \
		echo "Run 'make bootstrap' or 'bin/bootstrap-worktree' first." >&2; \
		exit 1; \
	fi

.PHONY: build bootstrap lean-lint test lint-markdown lint-spelling lint check clean help _check-mathlib-cache
```

## Notes

- Keep `lean-lint` separate from the text `lint` target so text checks do not require a Lake cache.
- Keep `_check-mathlib-cache` as the prerequisite for every target that invokes `lake build`, `lake test`, or `lake lint`.
- Do not replace `bootstrap` with a bare `lake build`.
