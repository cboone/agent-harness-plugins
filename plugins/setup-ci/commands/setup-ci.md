---
description: Set up GitHub Actions CI with test, lint, format, and vulnerability check jobs, plus matching Makefile targets.
disable-model-invocation: true
---

# Setup CI

Detect the project's language(s), create a GitHub Actions CI workflow with appropriate parallel jobs (test, lint, format, vulnerability check), and create matching Makefile targets for local development.

## Workflow

### 1. Detect Project Type

Scan for language and file-type markers using Glob. **Exclude `node_modules/`, `.yarn/`, `vendor/`, and other dependency directories from all searches** to avoid false positives from vendored code.

| Marker(s)                                                                                                     | Language              |
| ------------------------------------------------------------------------------------------------------------- | --------------------- |
| `go.mod`                                                                                                      | Go                    |
| `package.json` + source files (`*.js`, `*.ts`, `*.jsx`, `*.tsx`, `*.mjs`, `*.mts`, excluding `node_modules/`) | JavaScript/TypeScript |
| `pyproject.toml`, `setup.py`, `requirements.txt`                                                              | Python                |
| `Cargo.toml`                                                                                                  | Rust                  |
| `Gemfile`, `*.gemspec`                                                                                        | Ruby                  |
| `*.sh`, `bin/*`, `scripts/*`                                                                                  | Shell                 |

**Go sub-detection**: If `main.go` exists at the root or a `cmd/` directory exists, classify as **Go CLI**. Otherwise classify as **Go Library**.

**JS/TS sub-detection**: Determine the package manager from lockfiles:

- `package-lock.json` = npm
- `yarn.lock` or `.yarnrc.yml` = yarn
- `pnpm-lock.yaml` = pnpm
- `bun.lock` = bun
- Default to npm if no lockfile found.

**Source file verification**: When `package.json` is detected, verify that actual JavaScript or TypeScript source files exist (`*.js`, `*.ts`, `*.jsx`, `*.tsx`, `*.mjs`, `*.mts`, excluding `node_modules/` and config files like `eslint.config.js`). A `package.json` used only for devDependencies (e.g., markdownlint tooling) does not make the project a JavaScript project. If no source files are found, skip JavaScript/TypeScript CI.

If multiple languages are detected, create a multi-language workflow with one job group per language. Present the detected languages to the user and confirm before proceeding.

If no language is detected, offer a generic workflow with `make test` and `make lint` targets.

### 2. Check for Existing CI

Look for existing CI files:

```bash
ls .github/workflows/ci.yml
ls .github/workflows/ci.yaml
ls .github/workflows/*.yml
```

If a CI workflow exists, present its contents and ask the user:

1. **Overwrite**: Replace the existing CI workflow entirely
1. **Merge**: Add missing jobs to the existing workflow (keep existing jobs intact)
1. **Abort**: Stop without changes

### 3. Check for Existing Makefile

If a `Makefile` exists, scan for existing CI-relevant targets:

```bash
grep -E '^(test|lint|fmt|vet|vuln|build|cover|coverage|tidy|tools|all):' Makefile
```

Report which targets already exist and which will be added. Only add targets that do not already exist. Ask before modifying any existing target.

If no `Makefile` exists, offer to create one with the appropriate language-specific template from the Reference sections below. The Makefile provides standard targets for local development (`test`, `lint`, `fmt`, `vuln`, etc.) and is required by the Go CI reusable workflow (`go-ci.yml@v2`), which calls Makefile targets (`make test`, `make vet`, `make fmt`, etc.) directly. If the user declines, note that CI will fail for Go templates because the reusable workflow requires Makefile targets.

### 4. Create CI Workflow

Generate `.github/workflows/ci.yml` from the appropriate language template in the Reference sections below. Write the file using the Write tool. The `.github/workflows/` directory will be created automatically if it does not exist.

Go, Shell, and secret scanning templates use `cboone/gh-actions` reusable workflows that handle tool installation, caching, and execution internally. Other language templates use inline jobs.

All templates share:

- Triggers: push to `main`, pull requests targeting `main`
- `paths-ignore` for documentation and agent configuration changes
- Concurrency groups to cancel in-progress runs on the same branch/PR
- `permissions: contents: read`
- `actions/checkout@v6` (in inline jobs) or handled by reusable workflows

#### Runner Usage Notes

The `paths-ignore` patterns skip CI for changes that do not affect build or test outcomes:

- `*.md` matches root-level Markdown only (README, CONTRIBUTING, etc.). Nested `.md` files such as Scrut CLI tests in `tests/scrut/` are NOT ignored, so CI still runs when test files change.
- `docs/**` skips documentation directory changes.
- `.claude/**`, `**/CLAUDE.md`, `**/AGENTS.md` skip AI agent configuration files.
- `LICENSE` and `.editorconfig` skip non-code metadata.

**When to adjust**: Remove `*.md` from `paths-ignore` if your project treats Markdown files as source code (e.g., documentation-focused projects where Markdown linting is a CI step). Remove `docs/**` if your docs directory contains generated API references that should trigger CI.

The concurrency group cancels in-progress CI runs when new commits are pushed to the same branch or PR. This prevents wasted minutes on superseded commits.

For multi-language projects, combine language-specific jobs into a single workflow file using the multi-language pattern from the Reference section.

### 5. Create or Update Makefile Targets

Add missing targets from the appropriate Makefile template in the Reference sections below. Include both targets that the CI workflow references directly (e.g., `make test`, `make vet`) and standard local-development targets (`test`, `lint`, `fmt`, `vuln`, etc.) even when the CI workflow runs equivalent commands directly rather than via `make`.

Rules:

- Only add targets that do not already exist in the Makefile
- Ask before modifying existing targets
- If creating a new Makefile, include a `help` target
- Preserve any existing Makefile content (append new targets at the end)

### 6. Summary

Print a summary of what was created or modified:

- List every file created or modified
- Suggest complementary plugins:
  - `/setup-secret-scanning` for secret scanning
  - `/setup-linters` for linter configuration (if no linter configs detected)
  - `/add-scrut-cli-tests` for CLI snapshot testing (if CLI project detected)
  - `/add-goreleaser-homebrew` for release automation (if Go project detected)

## Error Handling

- **Not a git repo**: Warn the user, suggest `git init`, then continue (CI workflow files do not require a git repo to create, but will not trigger without one)
- **No language detected**: Offer a generic workflow with checkout + `make test` / `make lint` targets
- **Existing CI**: Ask before overwriting (covered in step 2)
- **Missing Makefile**: Offer to create one; if the user declines, note that CI may fail for language templates whose workflows reference `make` targets

---

## Reference: Go CLI CI Workflow

Use this template for Go CLI projects (projects with `main.go` or a `cmd/` directory). Uses the `cboone/gh-actions` reusable workflow, which creates parallel jobs for test, vet, format-check, and optionally lint and build.

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  ci:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v2
    with:
      go-version-file: go.mod
      run-lint: false
      run-format-check: true
```

### Notes

- Uses `go-version-file: go.mod` instead of pinning a Go version (stays current automatically)
- The reusable workflow creates parallel jobs internally (test, vet, format-check, and optionally lint and build) using Makefile targets
- `run-lint: false` because golangci-lint is not included by default for Go CLI projects; set to `true` when the project is ready for stricter linting
- `run-format-check: true` enables the gofmt/goimports formatting check

---

## Reference: Go Library CI Workflow

Use this template for Go library projects (no `main.go` at root, no `cmd/` directory). Replace `MINIMUM-GO-VERSION` with the minimum Go version from `go.mod` (e.g., `1.24`). Uses two `cboone/gh-actions` reusable workflow calls: one for the minimum Go version (all checks) and one for stable (tests only).

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  ci-minimum:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v2
    with:
      go-version: "MINIMUM-GO-VERSION"
      run-lint: true
      run-format-check: true
      run-build: true

  ci-stable:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v2
    with:
      go-version: "stable"
```

### Notes

- Two reusable workflow calls implement the Go version matrix: one for the minimum supported version (all checks) and one for stable (tests only)
- Each call creates its own set of parallel jobs internally
- Libraries benefit from multi-version testing more than CLIs because consumers may use older Go versions
- `run-lint: true` enables golangci-lint with SHA-256 verification
- `run-format-check: true` enables the gofmt/goimports formatting check
- `run-build: true` enables the `go build ./...` check
- The stable call uses defaults (test only) since lint, format, and build results do not vary by Go version

---

## Reference: JavaScript/TypeScript CI Workflow

Use this template for JavaScript or TypeScript projects. Replace `PACKAGE-MANAGER`, `INSTALL-COMMAND`, and `RUN-PREFIX` with the values from the table below.

| Package Manager | `INSTALL-COMMAND`                | `RUN-PREFIX` |
| --------------- | -------------------------------- | ------------ |
| npm             | `npm ci`                         | `npx`        |
| yarn            | `yarn install --immutable`       | `yarn`       |
| pnpm            | `pnpm install --frozen-lockfile` | `pnpm exec`  |
| bun             | `bun install --frozen-lockfile`  | `bunx`       |

If the project has a `tsconfig.json`, include the optional typecheck job.

**Package manager setup variations:**

- **npm**: Use `actions/setup-node@v4` with `cache: "npm"`. No extra setup needed.
- **yarn** (detected via `.yarnrc.yml` or `yarn.lock`): Add a `run: corepack enable` step before `actions/setup-node@v4`. Use `cache: "yarn"`.
- **pnpm** (detected via `pnpm-lock.yaml`): Add a `run: corepack enable` step before `actions/setup-node@v4`. Use `cache: "pnpm"`.
- **bun** (detected via `bun.lock`): Replace the `actions/setup-node@v4` step entirely with `oven-sh/setup-bun@v2` (omit the `cache` and `node-version` parameters; Bun manages its own caching). The `actions/setup-node` `cache` option does not support Bun.

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "PACKAGE-MANAGER"

      - name: Install dependencies
        run: INSTALL-COMMAND

      - name: Run tests
        run: RUN-PREFIX jest

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "PACKAGE-MANAGER"

      - name: Install dependencies
        run: INSTALL-COMMAND

      - name: Run ESLint
        run: RUN-PREFIX eslint .

  format:
    name: Format
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "PACKAGE-MANAGER"

      - name: Install dependencies
        run: INSTALL-COMMAND

      - name: Check formatting
        run: RUN-PREFIX prettier --check .

  # Include this job only if tsconfig.json exists
  typecheck:
    name: Type check
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "PACKAGE-MANAGER"

      - name: Install dependencies
        run: INSTALL-COMMAND

      - name: Run type check
        run: RUN-PREFIX tsc --noEmit
```

### Notes

- Detect the test runner from `package.json` scripts (jest, vitest, mocha, etc.) and adjust the test command accordingly
- If `package.json` has a `test` script, use `npm test` (or equivalent) instead of calling the runner directly
- If `package.json` has `lint` or `format` scripts, prefer those over direct tool invocation
- Only include the typecheck job if `tsconfig.json` exists
- The template above shows the npm setup; see "Package manager setup variations" above for yarn, pnpm, and bun differences
- For **yarn** and **pnpm**: add `run: corepack enable` as a step before `actions/setup-node` so the correct package manager shim is available for caching and installation
- For **bun**: replace `actions/setup-node@v4` with `oven-sh/setup-bun@v2` and remove `node-version` and `cache` parameters

---

## Reference: Python CI Workflow

Use this template for Python projects. Uses `uv` for dependency management and `ruff` for linting and formatting.

3 parallel jobs: test, lint, format.

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up uv
        uses: astral-sh/setup-uv@v5

      - name: Run tests
        run: uv run pytest

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up uv
        uses: astral-sh/setup-uv@v5

      - name: Run ruff lint
        run: uvx ruff check .

  format:
    name: Format
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up uv
        uses: astral-sh/setup-uv@v5

      - name: Check formatting
        run: uvx ruff format --check .
```

### Notes

- Uses `astral-sh/setup-uv@v5` for fast Python tooling
- `uvx ruff` runs ruff without installing it into the project
- `uv run pytest` uses the project's virtual environment for testing
- If the project uses a different test runner, adjust accordingly

---

## Reference: Rust CI Workflow

Use this template for Rust projects.

4 parallel jobs: test, lint, format, build.

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Cache dependencies
        uses: Swatinem/rust-cache@v2

      - name: Run tests
        run: cargo test

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy

      - name: Cache dependencies
        uses: Swatinem/rust-cache@v2

      - name: Run clippy
        run: cargo clippy -- -D warnings

  format:
    name: Format
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt

      - name: Check formatting
        run: cargo fmt -- --check

  build:
    name: Build
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Cache dependencies
        uses: Swatinem/rust-cache@v2

      - name: Build
        run: cargo build
```

### Notes

- Uses `dtolnay/rust-toolchain@stable` for toolchain setup
- `Swatinem/rust-cache@v2` caches Cargo dependencies and build artifacts
- Clippy runs with `-D warnings` to fail on any warning
- The format job uses `cargo fmt -- --check` (check mode, no modifications)
- **Action pinning**: `dtolnay/rust-toolchain@stable` and `Swatinem/rust-cache@v2` follow this project's convention of pinning third-party actions to upstream-maintained tags and branch references rather than commit SHAs. Generated workflows should keep these references as shown.

---

## Reference: Ruby CI Workflow

Use this template for Ruby projects.

2 parallel jobs: test, lint.

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: "3.3"
          bundler-cache: true

      - name: Run tests
        run: bundle exec rake test

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: "3.3"
          bundler-cache: true

      - name: Run RuboCop
        run: bundle exec rubocop
```

### Notes

- Uses `ruby/setup-ruby@v1` with `bundler-cache: true` for automatic Bundler caching
- Detect the Ruby version from `.ruby-version` if it exists and use that instead of `"3.3"`
- If the project uses RSpec instead of Minitest, use `bundle exec rspec` for the test command
- If the project uses `standardrb` instead of RuboCop, adjust the lint command accordingly

---

## Reference: Shell CI Workflow

Use this template for shell script projects. Uses the `cboone/gh-actions` reusable workflow, which handles ShellCheck and shfmt installation and execution internally.

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  lint:
    uses: cboone/gh-actions/.github/workflows/shell-lint.yml@v1
```

### Notes

- The reusable workflow handles ShellCheck and shfmt installation, checkout, and execution internally
- ShellCheck and shfmt configuration (scan directories, formatting options) is managed by the reusable workflow

---

## Reference: Multi-Language CI Workflow

For projects with multiple detected languages, combine language-specific jobs into one workflow file. Go uses a reusable workflow call; other languages use inline jobs.

Example combining Go and JavaScript:

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  go-ci:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v2
    with:
      go-version-file: go.mod
      run-format-check: true

  js-test:
    name: "JS: Test"
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

  js-lint:
    name: "JS: Lint"
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npx eslint .
```

### Notes

- Go uses a reusable workflow call that creates its own parallel jobs internally
- Non-Go languages use inline jobs with language-prefixed IDs (e.g., `js-test`, `js-lint`)
- Prefix job display names with the language (e.g., `"JS: Test"`, `"JS: Lint"`)
- Only include jobs relevant to each detected language

---

## Reference: Makefile Templates

### Go CLI Makefile

Adapted from the scaffold-go-cli template. Replace `PROJECT-NAME` with the project name.

```makefile
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
BINARY  := PROJECT-NAME
OUTDIR  := bin

LDFLAGS := -ldflags "-X main.version=$(VERSION)"

.PHONY: build test lint vet fmt vuln clean cover tidy help

build: ## Build the binary
	mkdir -p $(OUTDIR)
	go build $(LDFLAGS) -o $(OUTDIR)/$(BINARY) .

test: ## Run tests with race detector
	go test -v -race ./...

lint: ## Run golangci-lint
	golangci-lint run ./...

vet: ## Run go vet
	go vet ./...

fmt: ## Check formatting (exits non-zero if files need formatting)
	@test -z "$$(gofmt -l .)" || { gofmt -l . && exit 1; }

vuln: ## Run govulncheck
	govulncheck ./...

clean: ## Remove build artifacts
	rm -rf $(OUTDIR) dist coverage.out

cover: ## Run tests with coverage
	go test -coverprofile=coverage.out ./...
	go tool cover -func=coverage.out

tidy: ## Tidy go.mod
	go mod tidy

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
```

### Go Library Makefile

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
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	go install golang.org/x/vuln/cmd/govulncheck@latest

.PHONY: vet
vet: ## Run go vet
	go vet ./...

.PHONY: vuln
vuln: ## Run govulncheck
	govulncheck ./...
```

### JavaScript/TypeScript Makefile

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

### Python Makefile

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

### Rust Makefile

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

### Ruby Makefile

```makefile
.PHONY: test lint clean help

test: ## Run tests
	bundle exec rake test

lint: ## Run RuboCop
	bundle exec rubocop

clean: ## Remove build artifacts
	rm -rf tmp coverage

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
```

### Shell Makefile

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
