# Makefile Template

Create `Makefile` in the project root with the following content.

Replace `PROJECT-NAME` with the project name.

Recipe lines must be indented with literal tabs, not spaces.

```makefile
.PHONY: build test fmt format lint check run clean release test-scrut test-scrut-update test-all lint-md format-md lint-actions help

BIN := $(CURDIR)/zig-out/bin/PROJECT-NAME

build: ## Build the project
	zig build

test: ## Run unit tests
	zig build test

fmt: ## Check formatting without modifying files
	zig build fmt-check

format: ## Format code in place
	zig build fmt

lint: fmt build ## Check formatting and build (Zig has no separate linter)

check: fmt build test ## Run the full local gate before pushing
	@echo "check: formatting, build and tests all clean"

run: ## Build and run the project
	zig build run

clean: ## Remove build artifacts
	rm -rf .zig-cache/ zig-out/ release/

release: ## Cross-compile release binaries for all targets
	@set -e; rm -rf release; for target in x86_64-linux-gnu aarch64-linux-gnu x86_64-macos aarch64-macos x86_64-windows-gnu; do \
		printf 'Building for %s...\n' "$$target"; \
		zig build --prefix "release/$$target" -Dtarget="$$target" -Doptimize=ReleaseSafe; \
	done

test-scrut: build ## Run scrut CLI tests
	@command -v scrut > /dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	BIN="$(BIN)" scrut test tests/scrut/

test-scrut-update: build ## Update scrut test expectations
	@command -v scrut > /dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	BIN="$(BIN)" scrut update --replace --assume-yes tests/scrut/

test-all: test test-scrut ## Run all tests (unit + scrut)

lint-md: ## Lint Markdown files
	yarn lint

format-md: ## Format Markdown and other non-Zig files
	yarn lint:fix

lint-actions: ## Lint GitHub Actions workflows
	actionlint

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'
```

## Notes

- `check` is the whole point of this file. It runs the format check, the build and the tests in one command, so there is a single thing to run before pushing instead of a hand-spelled `zig fmt --check ... && zig build && zig build test` that comes out slightly different every time.
- `fmt` checks and `format` writes, matching `set-up-ci`'s Zig Makefile. This is the opposite of the more common `fmt`-writes convention, so read the target before running it in an unfamiliar Zig project.
- `fmt` and `format` delegate to the `fmt-check` and `fmt` steps in `build.zig` rather than calling `zig fmt` directly. That keeps one list of paths in the build script, and it is what makes `build.zig.zon` actually get checked: the usual `zig fmt --check src/ build.zig` silently skips the manifest.
- `lint` is `fmt` plus `build` because Zig has no separate linter. The compiler catches most of what a linter would, so a debug build is the closest equivalent.
- `release` writes per-target directories under `release/`, which the `.gitignore` template excludes. Zig cross-compiles all five targets from one machine with no extra toolchains.
- `release` installs each target straight into its own prefix with `zig build --prefix`, and clears `release/` first. Building into the default `zig-out/` and copying from it instead puts every target's leftovers in every directory: `zig build` does not clear the install prefix between runs, so a Windows build leaves a `.exe` and a `.pdb` behind that the next target's copy picks up.
- The scrut targets are a starting point; run the add-scrut-cli-tests skill to wire up the test files and the binary variable properly.
- `lint-md`, `format-md` and `lint-actions` cover the non-Zig files. They need the tooling that `set-up-linters` installs, so they fail until that skill has run.
