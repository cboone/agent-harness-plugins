---
description: Scaffold a Go library project with GoReleaser changelog releases, golangci-lint, GitHub Actions CI/CD, and Makefile.
disable-model-invocation: true
---

# Scaffold Go Library

Generate the full boilerplate for a new Go library project.

## Workflow

### 1. Gather Project Information

Ask the user for these parameters:

- **Project name** -- kebab-case, used as the module path and directory name (e.g., `stipple`)
- **Short description** -- one sentence, used in README, GoReleaser release header, and doc.go
- **Minimum Go version** -- the oldest Go version to support in CI (default: `1.24`)
- **Include example tests?** -- whether to generate an `example_test.go` with a basic `Example()` function

If the user already provided some or all of these in their initial request, do not re-ask. Derive what you can from context.

### 2. Detect User Identity

Detect the user's GitHub username and full name for use in templates:

```bash
# GitHub username (for module paths, URLs)
gh api user -q .login
```

```bash
# Full name (for LICENSE copyright)
git config user.name
```

If either command fails or produces no output, ask the user to provide the value. Use the GitHub username wherever templates reference `GITHUB-USERNAME` and the full name wherever they reference `COPYRIGHT-HOLDER`.

### 3. Verify the Target Directory

The project should be scaffolded in a directory named after the project. If the current directory is already named after the project and is empty (or nearly empty), use it. Otherwise, create a subdirectory.

Derive `PACKAGE-NAME` from `PROJECT-NAME` by removing hyphens (e.g., `my-lib` becomes `mylib`). If the result looks awkward, confirm with the user.

If the directory already contains Go files, warn the user before proceeding.

### 4. Initialize Git

Skip if already inside a git repository.

```bash
git init
```

### 5. Initialize go.mod

Follow the instructions in the go.mod Template section below:

```bash
go mod init github.com/GITHUB-USERNAME/PROJECT-NAME
```

No dependencies to install -- Go libraries should start stdlib-only.

### 6. Generate Package File

Create `PACKAGE-NAME.go` using the template from the Package File Template section below.

- Replace `PACKAGE-NAME` with the derived package name

This file contains the `package` declaration and a `Version` constant. No doc comment here -- that lives in `doc.go`.

### 7. Generate doc.go

Create `doc.go` using the template from the doc.go Template section below.

- Replace `PACKAGE-NAME` with the derived package name
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username
- Replace `PROJECT-NAME` with the project name

This is the canonical location for the package-level doc comment.

### 8. Generate Example Tests (optional)

If the user requested example tests, create `example_test.go` with a basic `Example()` function. This file is not generated from a reference template -- write it contextually based on the package name and description. The file should:

- Use `package PACKAGE-NAME_test` (external test package)
- Import the package being tested
- Include a single `func Example()` with a basic usage demonstration
- Include an `// Output:` comment

### 9. Generate Makefile

Create `Makefile` using the template from the Makefile Template section below.

- Replace `PROJECT-NAME` with the project name

### 10. Generate .gitignore

Create `.gitignore` using the template from the .gitignore Template section below.

No replacements needed.

If a `.gitignore` already exists, merge the template entries into it rather than overwriting.

### 11. Generate .goreleaser.yml

Create `.goreleaser.yml` using the template from the .goreleaser.yml Template section below.

- Replace `PROJECT-NAME` with the project name
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username

### 12. Generate .golangci.yml

Create `.golangci.yml` using the template from the .golangci.yml Template section below.

- Replace `GITHUB-USERNAME` with the detected GitHub username
- Replace `PROJECT-NAME` with the project name

### 13. Generate .editorconfig

Create `.editorconfig` using the template from the .editorconfig Template section below.

No replacements needed.

### 14. Generate CI Workflow

Create `.github/workflows/ci.yml` using the template from the CI Workflow Template section below.

- Replace `MINIMUM-GO-VERSION` with the minimum Go version (from step 1)

### 15. Generate Release Workflow

Create `.github/workflows/release.yml` using the template from the Release Workflow Template section below.

No replacements needed.

### 16. Generate LICENSE

Create `LICENSE` using the template from the LICENSE Template section below.

- Replace `YEAR` with the current year (run `date +%Y` to get it)
- Replace `COPYRIGHT-HOLDER` with the detected full name

### 17. Generate README.md

Create `README.md` using the template from the README Template section below.

- Replace `PROJECT-NAME` with the project name (kebab-case)
- Replace `PROJECT-TITLE` with the project name in title case
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username
- Replace `PACKAGE-NAME` with the derived package name

### 18. Generate CHANGELOG.md

Create `CHANGELOG.md` with the initial changelog template:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
```

No replacements needed. The `release` skill will populate version sections and comparison links on the first release.

### 19. Create Directory Stubs

Create stub directories for the standard library layout:

```bash
# plans directory
mkdir -p docs/plans/todo docs/plans/done
touch docs/plans/todo/.gitkeep docs/plans/done/.gitkeep
```

Libraries keep tests alongside source files, so no `tests/` directory. No `internal/` directory -- add it when needed.

### 20. Tidy Modules

```bash
go mod tidy
```

### 21. Verify the Build

Run a quick build to confirm everything compiles:

```bash
go build ./...
```

If the build fails, diagnose and fix the issue before continuing.

### 22. Create Initial Commit

Stage all generated files and create the initial commit:

```bash
git add -A
git commit -S -m "feat: scaffold Go library project"
```

### 23. Update Copilot Instructions

If `.github/copilot-instructions.md` exists (created by `scaffold-new-repo` when running in the bootstrap flow, or already present in an existing repo), append the following entries to the PR review section. Before appending each entry, check whether the bold key text already exists in the file; skip entries that are already present.

To locate the PR review section: look for an existing heading whose text includes "PR Review" or "Code Review" (e.g., `## PR Review`, `## Code Review`, `## PR Review Checklist (CRITICAL)`). If no matching heading exists, append a new `## PR Review` section at the end of the file and place the entries there.

- **golangci-lint v2 config format is intentional**: This project uses golangci-lint v2 configuration which includes `formatters:` as a top-level key and supports `golangci-lint fmt` as a subcommand. These are correct v2 features. Do not suggest reverting to v1 config format.
- **golangci-lint-action handles its own caching**: The `golangci/golangci-lint-action` manages golangci-lint installation and caching automatically. Do not suggest adding manual cache steps or replacing it with a manual install.

If `.github/copilot-instructions.md` does not exist, skip this step.

### 24. Summary

Print a summary of what was created:

- List every file and directory generated
- Note whether example tests were included
- Remind the user to:
  - Run `make help` to see available Makefile targets
  - Tag releases with `git tag v0.1.0 && git push --tags` to trigger GoReleaser
  - Write tests alongside source files (e.g., `PACKAGE-NAME_test.go`)
  - Use `make coverage` to generate an HTML coverage report
  - Run `/add-community-files` to add CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and .github/PULL_REQUEST_TEMPLATE.md

## Error Handling

- If `go mod init` fails, check that Go is installed and on the PATH
- If the target directory already contains Go files, ask the user before overwriting
- If `git init` fails, continue generating files but warn the user
- If the build verification fails, show the error and attempt to fix it before continuing

---

## Reference: go.mod Template

Do not write `go.mod` manually. Initialize it with `go mod init`.

### Initialize

```bash
go mod init github.com/GITHUB-USERNAME/PROJECT-NAME
```

### Tidy

After all source files are written:

```bash
go mod tidy
```

### Notes

- The module path is always `github.com/GITHUB-USERNAME/PROJECT-NAME`
- Go libraries should start with no external dependencies (stdlib-only)
- Add dependencies only when the library genuinely needs them
- The Go version in `go.mod` is set automatically by `go mod init` based on the installed Go toolchain
- `go mod tidy` removes unused dependencies and adds missing ones

## Reference: Package File Template

Use this template for `PACKAGE-NAME.go`, the main package source file. Replace `PACKAGE-NAME` with the derived package name (project name with hyphens removed).

```go
package PACKAGE-NAME

// Version is the current version of PACKAGE-NAME.
const Version = "0.0.0-dev"
```

### Notes

- The `Version` constant provides a programmatic way to check the library version
- No doc comment on this file -- the canonical package doc lives in `doc.go`
- The initial version is `0.0.0-dev` to indicate pre-release status
- Users will add their library's exported API to this file (or additional files in the same package)

## Reference: doc.go Template

Use this template for `doc.go`, the package-level documentation file. Replace `PACKAGE-NAME`, `PROJECT-DESCRIPTION`, `GITHUB-USERNAME`, and `PROJECT-NAME` with the actual values.

```go
// Package PACKAGE-NAME PROJECT-DESCRIPTION
//
// # Installation
//
//	go get github.com/GITHUB-USERNAME/PROJECT-NAME
package PACKAGE-NAME
```

### Notes

- This is the canonical location for the package-level doc comment (following Go convention)
- The first line follows the `// Package name ...` convention required by godoc
- The `PROJECT-DESCRIPTION` should start with a lowercase letter (it continues the "Package name" sentence)
- The `# Installation` section uses a godoc heading and an indented code block
- Keep doc.go focused on the package overview -- detailed API docs belong on exported symbols

## Reference: Makefile Template

Use this template for `Makefile`. Replace `PROJECT-NAME` with the project name.

```makefile
# PROJECT-NAME Makefile

.DEFAULT_GOAL := all

# Run all checks
.PHONY: all
all: fmt vet lint vuln test build

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
	@echo "  all          Run fmt, vet, lint, vuln, test, build (default)"
	@echo "  build        Build all packages"
	@echo "  clean        Remove build artifacts"
	@echo "  coverage     Generate HTML coverage report"
	@echo "  fmt          Format code"
	@echo "  help         Show this help message"
	@echo "  lint         Run golangci-lint"
	@echo "  test         Run tests with race detector"
	@echo "  tools        Install development tools"
	@echo "  vet          Run go vet"
	@echo "  vuln         Run govulncheck"

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
	go install golang.org/x/vuln/cmd/govulncheck@latest

# Run go vet
.PHONY: vet
vet:
	go vet ./...

# Run govulncheck
.PHONY: vuln
vuln:
	govulncheck ./...
```

### Notes

- No `VERSION` or `BINARY` variables -- libraries have no binary output
- The `all` target runs the full quality pipeline: format, vet, lint, vuln, test, build
- The `coverage` target generates an HTML report for reviewing test coverage
- The `tools` target installs golangci-lint, goreleaser, and govulncheck for local development
- Targets are listed alphabetically for easy scanning
- No `demo` or `test-visual` targets -- add project-specific targets as needed

## Reference: .gitignore Template

Use this template for `.gitignore`. No replacements needed.

```text
# If you prefer the allow list template instead of the deny list, see community template:
# https://github.com/github/gitignore/blob/main/community/Golang/Go.AllowList.gitignore
#
# Binaries for programs and plugins
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary, built with `go test -c`
*.test

# Code coverage profiles and other test artifacts
*.out
coverage.*
*.coverprofile
profile.cov

# Dependency directories (remove the comment below to include it)
# vendor/

# Go workspace file
go.work
go.work.sum

# goreleaser output
dist/

# env file
.env

# Editor/IDE
# .idea/
# .vscode/
```

### Notes

- No binary name entry -- libraries produce no binary
- No `bin/` directory -- libraries have no build output directory
- Coverage artifacts are ignored to keep the repo clean
- If a `.gitignore` already exists, merge these entries rather than overwriting

## Reference: .goreleaser.yml Template

Use this template for `.goreleaser.yml`. Replace `PROJECT-NAME`, `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the actual values.

````yaml
# goreleaser configuration for PROJECT-NAME
# https://goreleaser.com

version: 2

# PROJECT-NAME is a library, not a binary
builds:
  - skip: true

changelog:
  sort: asc
  groups:
    - title: Features
      regexp: '^.*?feat(\([[:word:]]+\))??!?:.+$'
      order: 0
    - title: Bug Fixes
      regexp: '^.*?fix(\([[:word:]]+\))??!?:.+$'
      order: 1
    - title: Documentation
      regexp: '^.*?docs(\([[:word:]]+\))??!?:.+$'
      order: 2
    - title: Performance
      regexp: '^.*?perf(\([[:word:]]+\))??!?:.+$'
      order: 3
    - title: Refactoring
      regexp: '^.*?refactor(\([[:word:]]+\))??!?:.+$'
      order: 4
    - title: Tests
      regexp: '^.*?test(\([[:word:]]+\))??!?:.+$'
      order: 5
    - title: Build
      regexp: '^.*?(build|ci)(\([[:word:]]+\))??!?:.+$'
      order: 6
    - title: Other
      order: 999
  filters:
    exclude:
      - "^chore:"
      - "^style:"

release:
  header: |
    ## PROJECT-NAME {{ .Tag }}

    PROJECT-DESCRIPTION

    ### Installation

    ```bash
    go get github.com/GITHUB-USERNAME/PROJECT-NAME@{{ .Tag }}
    ```
  footer: |
    **Full Changelog**: https://github.com/GITHUB-USERNAME/PROJECT-NAME/compare/{{ .PreviousTag }}...{{ .Tag }}
````

### Notes

- `builds: [{skip: true}]` tells GoReleaser this is a library with no binary to compile
- The changelog groups commits by conventional commit type for organized release notes
- `chore:` and `style:` commits are excluded from the changelog
- The release header includes a `go get` installation command with the specific tag
- No Homebrew section -- libraries are installed via `go get`, not Homebrew
- The footer links to the full diff between tags on GitHub

## Reference: .golangci.yml Template

Use this template for `.golangci.yml`. Replace `GITHUB-USERNAME` and `PROJECT-NAME` with the actual values.

```yaml
# golangci-lint configuration for PROJECT-NAME
# https://golangci-lint.run/usage/configuration/

version: "2"

run:
  timeout: 5m

formatters:
  enable:
    - gofmt
    - goimports

  settings:
    goimports:
      local-prefixes:
        - github.com/GITHUB-USERNAME/PROJECT-NAME

linters:
  enable:
    # Quality
    - bodyclose
    - durationcheck
    - errcheck
    - gocritic
    - gocyclo
    - ineffassign
    - nilerr
    - revive
    - staticcheck
    - unused
    # Style
    - godot

  settings:
    gocyclo:
      min-complexity: 15

    godot:
      capital: false
      scope: declarations

    revive:
      rules:
        - name: blank-imports
        - name: context-as-argument
        - name: context-keys-type
        - name: dot-imports
        - name: error-naming
        - name: error-return
        - name: error-strings
        - name: exported
        - name: increment-decrement
        - name: indent-error-flow
        - name: package-comments
        - name: range
        - name: receiver-naming
        - name: time-naming
        - name: unexported-return
        - name: var-declaration
        - name: var-naming
```

### Notes

- Uses golangci-lint v2 configuration format (`version: "2"`)
- `goimports` local-prefixes ensures project imports are grouped separately
- Quality linters catch real bugs: `errcheck` (unchecked errors), `nilerr` (nil error returns), `bodyclose` (unclosed HTTP bodies), `staticcheck` (comprehensive static analysis), `unused` (dead code), `ineffassign` (ineffectual assignments)
- Style linters enforce consistency: `godot` (comment periods), `revive` (comprehensive style rules)
- `gocyclo` threshold of 15 is reasonable for library code -- lower than application code
- The revive rules list covers the most commonly accepted Go style conventions

## Reference: .editorconfig Template

Use this template for `.editorconfig`. No replacements needed.

```ini
# EditorConfig
# https://editorconfig.org

root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.go]
indent_style = tab

[*.{yml,yaml}]
indent_size = 2
indent_style = space

[*.md]
indent_size = 2
indent_style = space
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

### Notes

- Go files use tabs (gofmt enforces this)
- YAML and Markdown files use 2-space indentation
- Markdown has `trim_trailing_whitespace = false` because trailing spaces are meaningful in Markdown (they create line breaks)
- Makefile requires tabs for recipe lines (Make syntax requirement)
- `insert_final_newline = true` ensures POSIX-compliant text files
- The `root = true` directive stops editors from looking for parent .editorconfig files

## Reference: CI Workflow Template

Use this template for `.github/workflows/ci.yml`. Replace `MINIMUM-GO-VERSION` with the minimum Go version specified by the user (e.g., `1.24`).

The Go version matrix should include the minimum version and `stable` (the latest release).

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
    name: Test (Go ${{ matrix.go-version }})
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      matrix:
        go-version: ["MINIMUM-GO-VERSION", "stable"]
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: ${{ matrix.go-version }}

      - name: Run tests
        run: go test -race -v ./...

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "MINIMUM-GO-VERSION"

      - name: Run golangci-lint
        uses: golangci/golangci-lint-action@v9

  build:
    name: Build
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "MINIMUM-GO-VERSION"

      - name: Build
        run: go build ./...

  format:
    name: Format
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "MINIMUM-GO-VERSION"

      - name: Check formatting
        run: |
          if [ -n "$(gofmt -l .)" ]; then
            echo "The following files are not formatted:"
            gofmt -l .
            exit 1
          fi

  vulncheck:
    name: Vulnerability check
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "MINIMUM-GO-VERSION"

      - name: Install govulncheck
        run: go install golang.org/x/vuln/cmd/govulncheck@latest

      - name: Run govulncheck
        run: govulncheck ./...
```

### Notes

- `paths-ignore` skips CI for documentation and agent configuration changes; remove `*.md` if Markdown is source code (e.g., Scrut CLI tests in `tests/scrut/` are nested and NOT ignored)
- Concurrency groups cancel in-progress runs when new commits are pushed to the same branch/PR
- Five parallel jobs: test, lint, build, format, vulncheck
- The test job uses a Go version matrix (`MINIMUM-GO-VERSION` + `stable`) to verify compatibility across versions
- The lint job uses the official golangci-lint GitHub Action for consistent results
- The format job checks that all files pass `gofmt` (fails CI if not)
- The vulncheck job uses `govulncheck` from the Go team to detect known vulnerabilities in dependencies
- `permissions: contents: read` follows the principle of least privilege
- Libraries benefit from multi-version testing more than CLIs because consumers may use older Go versions

## Reference: Release Workflow Template

Use this template for `.github/workflows/release.yml`. No replacements needed.

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents: write

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - name: Checkout code
        uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: stable

      - name: Run GoReleaser
        uses: goreleaser/goreleaser-action@v6
        with:
          distribution: goreleaser
          version: latest
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Notes

- Triggers on version tags (e.g., `v0.1.0`, `v1.0.0`)
- Concurrency uses `cancel-in-progress: false` to avoid interrupting active releases
- Uses `fetch-depth: 0` to get full git history for changelog generation
- Only needs `GITHUB_TOKEN` (no `HOMEBREW_TAP_TOKEN` since libraries have no Homebrew formula)
- `permissions: contents: write` is required for GoReleaser to create the GitHub release
- GoReleaser will skip the build step (configured in `.goreleaser.yml`) and only generate the changelog and release
- Uses `go-version: stable` since the release workflow only needs to run GoReleaser, not compile code

## Reference: LICENSE Template

Use this exact template. Replace `YEAR` with the current year (from `date +%Y`) and `COPYRIGHT-HOLDER` with the user's full name.

```text
MIT License

Copyright (c) YEAR COPYRIGHT-HOLDER

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Notes

- Replace `COPYRIGHT-HOLDER` with the user's full name (from `git config user.name`)
- The year is always the current year at the time of generation
- This is the standard MIT license text with no modifications

## Reference: README Template

Use this template for the project `README.md`. Replace `PROJECT-NAME` (kebab-case), `PROJECT-TITLE` (title case), `PROJECT-DESCRIPTION`, `GITHUB-USERNAME`, and `PACKAGE-NAME` with the actual values.

````markdown
# PROJECT-TITLE

PROJECT-DESCRIPTION

## Installation

```sh
go get github.com/GITHUB-USERNAME/PROJECT-NAME
```

## Usage

```go
package main

import (
	"fmt"

	"github.com/GITHUB-USERNAME/PROJECT-NAME"
)

func main() {
	fmt.Println(PACKAGE-NAME.Version)
}
```

## Development

```sh
git clone https://github.com/GITHUB-USERNAME/PROJECT-NAME.git
cd PROJECT-NAME
make all
```

Run `make help` to see all available targets.

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
````

### Notes

- The heading uses the project name in title case (e.g., "Stipple", "My Lib")
- Installation uses `go get` (the standard way to add a Go library dependency)
- The usage example shows a minimal import and usage of the package
- The development section covers cloning and running the full quality pipeline
- Replace `PACKAGE-NAME` in the usage example with the actual package name (hyphens removed)
- License section uses the standard MIT license wording
