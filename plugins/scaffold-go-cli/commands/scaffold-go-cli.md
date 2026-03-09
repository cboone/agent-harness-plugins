---
description: Scaffold a complete Go CLI project with Cobra, GoReleaser, GitHub Actions CI/CD, Homebrew tap, and Makefile.
disable-model-invocation: true
---

# Scaffold Go CLI

Generate the full boilerplate for a new Go CLI project.

## Workflow

### 1. Gather Project Information

Ask the user for these parameters:

- **Project name** -- kebab-case, used as the binary name, module path, and directory name (e.g., `my-tool`)
- **Short description** -- one sentence, used in README, GoReleaser Homebrew cask, and the Cobra root command `Short` field
- **Include Viper?** -- whether to add Viper for config file management (adds `--config` flag and `~/.config/<name>/config.yaml` support)
- **Include Charmbracelet TUI?** -- whether to add bubbletea, lipgloss, and bubbles dependencies

If the user already provided some or all of these in their initial request, do not re-ask. Derive what you can from context.

### 2. Detect User Identity

Detect the user's GitHub username and full name for use in templates:

```bash
# GitHub username (for module paths, URLs, Homebrew tap)
gh api user -q .login
```

```bash
# Full name (for LICENSE copyright)
git config user.name
```

If either command fails or produces no output, ask the user to provide the value. Use the GitHub username wherever templates reference `GITHUB-USERNAME` and the full name wherever they reference `COPYRIGHT-HOLDER`.

### 3. Verify the Target Directory

The project should be scaffolded in a directory named after the project. If the current directory is already named after the project and is empty (or nearly empty), use it. Otherwise, create a subdirectory.

If the directory already contains Go files, warn the user before proceeding.

### 4. Initialize Git

Skip if already inside a git repository.

```bash
git init
```

### 5. Generate main.go

Create `main.go` using the template from the main.go Template section below.

- Replace `PROJECT-NAME` with the project name
- Replace `GITHUB-USERNAME` with the detected GitHub username

### 6. Generate cmd/root.go

Choose the template based on the Viper parameter:

- **Without Viper**: use the root.go Template (Without Viper) section below
- **With Viper**: use the root.go Template (With Viper) section below

Replace in the chosen template:

- `PROJECT-NAME` with the project name
- `PROJECT-DESCRIPTION` with the short description

### 7. Initialize go.mod and Install Dependencies

Follow the instructions in the go.mod Template section below:

```bash
go mod init github.com/GITHUB-USERNAME/PROJECT-NAME
go get github.com/spf13/cobra@latest
```

If Viper was selected:

```bash
go get github.com/spf13/viper@latest
```

If Charmbracelet TUI was selected:

```bash
go get charm.land/bubbletea/v2@latest
go get charm.land/lipgloss/v2@latest
go get charm.land/bubbles/v2@latest
```

Then tidy:

```bash
go mod tidy
```

### 8. Generate Makefile

Create `Makefile` using the template from the Makefile Template section below.

- Replace `PROJECT-NAME` with the project name

### 9. Generate .gitignore

Create `.gitignore` using the template from the .gitignore Template section below.

- Replace `PROJECT-NAME` with the project name

If a `.gitignore` already exists, merge the template entries into it rather than overwriting.

### 10. Generate .goreleaser.yml

Create `.goreleaser.yml` using the template from the .goreleaser.yml Template section below.

- Replace `PROJECT-NAME` with the project name
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username

### 11. Generate CI Workflow

Create `.github/workflows/ci.yml` using the template from the CI Workflow Template section below.

No replacements needed (the workflow is project-name-independent).

### 12. Generate Release Workflow

Create `.github/workflows/release.yml` using the template from the Release Workflow Template section below.

No replacements needed.

### 13. Generate LICENSE

Create `LICENSE` using the template from the LICENSE Template section below.

- Replace `YEAR` with the current year (run `date +%Y` to get it)
- Replace `COPYRIGHT-HOLDER` with the detected full name

### 14. Generate README.md

Create `README.md` using the template from the README Template section below.

- Replace `PROJECT-NAME` with the project name (kebab-case)
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username

### 15. Generate CHANGELOG.md

Create `CHANGELOG.md` with the initial changelog template:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
```

No replacements needed. The `release` skill will populate version sections and comparison links on the first release.

### 16. Create Directory Stubs

Create stub directories for the standard project layout:

```bash
# internal package stub
mkdir -p internal
touch internal/.gitkeep

# plans directory
mkdir -p docs/plans/todo docs/plans/done
touch docs/plans/todo/.gitkeep docs/plans/done/.gitkeep

# tests directory
mkdir -p tests
touch tests/.gitkeep
```

### 17. Verify the Build

Run a quick build to confirm everything compiles:

```bash
go build ./...
```

If the build fails, diagnose and fix the issue before continuing.

### 18. Create Initial Commit

Stage all generated files and create the initial commit:

```bash
git add -A
git commit -S -m "feat: scaffold Go CLI project"
```

### 19. Update Copilot Instructions

If `.github/copilot-instructions.md` exists (created by `scaffold-new-repo` when running in the bootstrap flow, or already present in an existing repo), append the following entries to the PR review section. Before appending each entry, check whether the bold key text already exists in the file; skip entries that are already present.

To locate the PR review section: look for an existing heading whose text includes "PR Review" or "Code Review" (e.g., `## PR Review`, `## Code Review`, `## PR Review Checklist (CRITICAL)`). If no matching heading exists, append a new `## PR Review` section at the end of the file and place the entries there.

- **`cboone/gh-actions` reusable workflows manage tool versions internally**: The CI and release workflows use `cboone/gh-actions` reusable workflows that handle tool installation, version pinning, caching, and SHA-256 verification internally. Do not suggest replacing reusable workflow calls with inlined third-party actions.

If `.github/copilot-instructions.md` does not exist, skip this step.

### 20. Set Up HOMEBREW_TAP_TOKEN

The release workflow requires a `HOMEBREW_TAP_TOKEN` repository secret to publish Homebrew casks. Follow the steps in the "Reference: HOMEBREW_TAP_TOKEN Setup" section at the bottom of this file.

Ask the user whether they want to set up the token now or defer it to later. If they defer, note in the summary that the token must be configured before the first release.

Note: for brand-new projects that have not been pushed to GitHub yet, `gh secret` commands (including `gh secret set` and `gh secret list`) will not work until a GitHub remote exists. See the "No remote yet?" note in the reference section.

### 21. Summary

Print a summary of what was created:

- List every file and directory generated
- Note which optional features were included (Viper, Charmbracelet TUI)
- Remind the user to:
  - Add subcommands under `cmd/` as the CLI grows
  - Run `make help` to see available Makefile targets
  - Run `/add-community-files` to add CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and .github/PULL_REQUEST_TEMPLATE.md
- If `HOMEBREW_TAP_TOKEN` setup was deferred in step 20: check whether a GitHub remote exists and is accessible before creating a follow-up issue:

  ```bash
  if git remote get-url origin >/dev/null 2>&1 && gh repo view >/dev/null 2>&1; then
    gh issue create \
      --title "Set up HOMEBREW_TAP_TOKEN repository secret" \
      --body "The release workflow needs a HOMEBREW_TAP_TOKEN secret so GoReleaser can push Homebrew cask updates to the tap repository.

  See the HOMEBREW_TAP_TOKEN Setup reference in the scaffold-go-cli documentation for step-by-step instructions."
  fi
  ```

  If the issue was created successfully, report its URL in the summary.

  If no remote exists or the repo is not accessible via `gh`, print a reminder instead: the user should create the issue manually (or re-run the token setup) after pushing to GitHub for the first time.

## Error Handling

- If `go mod init` fails, check that Go is installed and on the PATH
- If `go get` fails for any dependency, check network connectivity and retry once
- If the target directory already contains Go files, ask the user before overwriting
- If `git init` fails, continue generating files but warn the user
- If the build verification fails, show the error and attempt to fix it before continuing

---

## Reference: main.go Template

Use this template for the root `main.go` file. Replace `PROJECT-NAME` with the actual project name and `GITHUB-USERNAME` with the user's GitHub username.

```go
package main

import (
	"fmt"
	"os"

	"github.com/GITHUB-USERNAME/PROJECT-NAME/cmd"
)

var version = "dev"

func main() {
	cmd.SetVersion(version)
	if err := cmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %s\n", err)
		os.Exit(1)
	}
}
```

### Notes

- The `version` variable is injected at build time via ldflags (`-X main.version=...`)
- The default value `"dev"` is used during local development
- `cmd.SetVersion()` passes the version to the Cobra root command
- Errors from `Execute()` are printed to stderr before exiting with code 1

## Reference: cmd/root.go Template (Without Viper)

Use this template when the user does **not** want Viper config management. Replace `PROJECT-NAME` and `PROJECT-DESCRIPTION` with the actual values.

```go
package cmd

import "github.com/spf13/cobra"

var rootCmd = &cobra.Command{
	Use:           "PROJECT-NAME",
	Short:         "PROJECT-DESCRIPTION",
	SilenceUsage:  true,
	SilenceErrors: true,
}

// Execute runs the root command.
func Execute() error {
	return rootCmd.Execute()
}

// SetVersion sets the version string on the root command.
func SetVersion(v string) {
	rootCmd.Version = v
}
```

### Notes

- `SilenceUsage: true` prevents Cobra from printing usage on every error
- `SilenceErrors: true` prevents Cobra from printing errors (the caller handles that)
- `SetVersion` receives the version from `main.go` where it is injected via ldflags
- The `Use` field is the binary name (what the user types to run the command)

## Reference: cmd/root.go Template (With Viper)

Use this template when the user **does** want Viper config management. Replace `PROJECT-NAME` and `PROJECT-DESCRIPTION` with the actual values.

```go
package cmd

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	cfgFile string
	rootCmd = &cobra.Command{
		Use:           "PROJECT-NAME",
		Short:         "PROJECT-DESCRIPTION",
		SilenceUsage:  true,
		SilenceErrors: true,
	}
)

// Execute runs the root command.
func Execute() error {
	return rootCmd.Execute()
}

// SetVersion sets the version string on the root command.
func SetVersion(v string) {
	rootCmd.Version = v
}

func init() {
	cobra.OnInitialize(initConfig)
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default: ~/.config/PROJECT-NAME/config.yaml)")
}

func initConfig() {
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		home, err := os.UserHomeDir()
		if err == nil {
			viper.AddConfigPath(filepath.Join(home, ".config", "PROJECT-NAME"))
			viper.SetConfigName("config")
			viper.SetConfigType("yaml")
		}
	}

	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err != nil {
		// Missing config file is fine; surface unexpected errors (e.g., syntax).
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			fmt.Fprintf(os.Stderr, "Warning: config file error: %v\n", err)
		}
	}
}
```

### Notes

- Adds `--config` persistent flag for explicit config file path
- Default config location is `~/.config/PROJECT-NAME/config.yaml`
- `viper.AutomaticEnv()` binds environment variables automatically
- Missing config file is silently ignored (common for CLIs that work without config)
- The `PROJECT-NAME` in the config path and flag help should match the binary name

## Reference: go.mod Template

Do not write `go.mod` manually. Initialize it with `go mod init`, then add dependencies with `go get`.

### Initialize

```bash
go mod init github.com/GITHUB-USERNAME/PROJECT-NAME
```

### Add Core Dependencies

Always add Cobra:

```bash
go get github.com/spf13/cobra@latest
```

### Add Optional Dependencies

#### Viper (config management)

Only add if the user requested Viper:

```bash
go get github.com/spf13/viper@latest
```

#### Charmbracelet TUI

Only add if the user requested TUI dependencies:

```bash
go get charm.land/bubbletea/v2@latest
go get charm.land/lipgloss/v2@latest
go get charm.land/bubbles/v2@latest
```

### Tidy

After all dependencies are added:

```bash
go mod tidy
```

### Notes

- The module path is always `github.com/GITHUB-USERNAME/PROJECT-NAME`
- Use `@latest` to get the most recent stable version
- `go mod tidy` removes unused dependencies and adds missing ones
- The Go version in `go.mod` is set automatically by `go mod init` based on the installed Go toolchain

## Reference: Makefile Template

Use this template for the project Makefile. Replace `PROJECT-NAME` with the actual binary name.

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

### Notes

- Self-documenting: each target has a `## Comment` that `make help` displays
- Version is derived from git tags, falling back to `"dev"`
- Binary output goes to `bin/` to keep the project root clean
- `fmt` target checks formatting without modifying files (CI-friendly)
- `lint` assumes `golangci-lint` is installed (`brew install golangci-lint`)
- `vuln` assumes `govulncheck` is installed (`go install golang.org/x/vuln/cmd/govulncheck@latest`)

## Reference: .gitignore Template

Use this template for the project `.gitignore`. Replace `PROJECT-NAME` with the actual binary name.

```gitignore
# Binary
/PROJECT-NAME
/bin/
/dist/

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

# Go workspace files
go.work
go.work.sum

# Environment
.env

# Dependency directories
# vendor/
```

### Notes

- The binary name at the top prevents accidentally committing a built binary in the project root
- `bin/` matches the Makefile output directory
- `dist/` is created by GoReleaser during release builds
- `go.work` and `go.work.sum` are workspace files for multi-module setups (not committed)
- `.env` prevents accidentally committing secrets

## Reference: .goreleaser.yml Template

Use this template for GoReleaser configuration. Replace `PROJECT-NAME`, `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the actual values.

```yaml
version: 2

builds:
  - main: .
    binary: PROJECT-NAME
    env:
      - CGO_ENABLED=0
    goos:
      - linux
      - darwin
      - windows
    goarch:
      - amd64
      - arm64
    ldflags:
      - -s -w
      - -X main.version={{.Version}}

archives:
  - formats:
      - tar.gz
    format_overrides:
      - goos: windows
        formats:
          - zip
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"

checksum:
  name_template: checksums.txt

release:
  prerelease: auto

changelog:
  sort: asc
  filters:
    exclude:
      - "^docs:"
      - "^test:"
      - "^chore:"

homebrew_casks:
  - binaries:
      - PROJECT-NAME
    repository:
      owner: GITHUB-USERNAME
      name: homebrew-tap
      token: "{{ .Env.HOMEBREW_TAP_TOKEN }}"
    homepage: "https://github.com/GITHUB-USERNAME/PROJECT-NAME"
    description: "PROJECT-DESCRIPTION"
    license: MIT
    hooks:
      post:
        install: |
          system_command "/usr/bin/xattr", args: ["-dr", "com.apple.quarantine", "#{staged_path}/PROJECT-NAME"]
```

### Notes

- Uses GoReleaser v2 config format (`version: 2`)
- `CGO_ENABLED=0` produces static binaries (no C library dependency)
- `-s -w` in ldflags strips debug info and symbol tables (smaller binary)
- `-X main.version={{.Version}}` injects the release version at build time
- Builds for Linux, macOS, and Windows on both amd64 and arm64
- Windows archives use zip; everything else uses tar.gz
- Uses `homebrew_casks:` (GoReleaser v2.10+) instead of the deprecated `brews:`. Casks are the correct artifact type for pre-compiled binaries distributed via GoReleaser
- The `directory` field defaults to `Casks` and is omitted; do not set it to `Formula`
- `binaries:` lists binary names to install, replacing the formula `install:` block
- Casks do not support `test:` blocks; version testing is handled differently in the Homebrew cask ecosystem
- The quarantine removal hook prevents "App is damaged" Gatekeeper errors on macOS for unsigned binaries. The `hooks.post.install` field is a string (not a list)
- Homebrew tap publishes to `GITHUB-USERNAME/homebrew-tap` using `HOMEBREW_TAP_TOKEN` (see "Reference: HOMEBREW_TAP_TOKEN Setup" for creation and configuration)
- `prerelease: auto` marks pre-release tags (e.g., `v1.0.0-rc1`) correctly on GitHub
- The `{{` and `}}` delimiters are GoReleaser template syntax, not Go templates

## Reference: CI Workflow Template

Use this template for `.github/workflows/ci.yml`. Uses the `cboone/gh-actions` reusable workflow, which creates parallel jobs for test, vet, lint, format-check, and more.

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
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v1
    with:
      go-version-file: go.mod
      use-makefile: true
      run-lint: true
      run-format-check: true
```

### Notes

- `paths-ignore` skips CI for documentation and agent configuration changes; remove `*.md` if Markdown is source code (e.g., Scrut CLI tests in `tests/scrut/` are nested and NOT ignored)
- Concurrency groups cancel in-progress runs when new commits are pushed to the same branch/PR
- `permissions: contents: read` follows the principle of least privilege
- The reusable workflow creates parallel jobs internally (test, vet, lint, format-check)
- `use-makefile: true` tells the reusable workflow to call Makefile targets (`make test`, `make vet`, `make fmt`) instead of running Go commands directly
- `run-lint: true` enables golangci-lint with SHA-256 verification
- `run-format-check: true` enables the gofmt/goimports formatting check
- The reusable workflow uses `go-version-file: go.mod` to stay current automatically

## Reference: Release Workflow Template

Use this template for `.github/workflows/release.yml`. Uses the `cboone/gh-actions` reusable workflow, which handles Go setup, GoReleaser installation, and release execution internally.

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
    uses: cboone/gh-actions/.github/workflows/go-release.yml@v1
    with:
      go-version-file: go.mod
    secrets:
      HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}
```

### Notes

- Triggers on version tags (`v*` matches `v1.0.0`, `v0.1.0-rc1`, etc.)
- Concurrency uses `cancel-in-progress: false` to avoid interrupting active releases
- The reusable workflow handles checkout with `fetch-depth: 0`, Go setup, GoReleaser installation, and the release command internally
- `GITHUB_TOKEN` is provided automatically by GitHub Actions and its permissions are controlled by the caller workflow's `permissions:` block
- `HOMEBREW_TAP_TOKEN` must be added as a repository secret (see "Reference: HOMEBREW_TAP_TOKEN Setup" for creation and configuration)

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

Use this template for the project `README.md`. Replace `PROJECT-NAME` (kebab-case), `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the actual values.

````markdown
# PROJECT-NAME

PROJECT-DESCRIPTION

## Installation

### Homebrew

```sh
brew install GITHUB-USERNAME/tap/PROJECT-NAME
```

### From source

```sh
go install github.com/GITHUB-USERNAME/PROJECT-NAME@latest
```

### From release

Download a binary from the [releases page](https://github.com/GITHUB-USERNAME/PROJECT-NAME/releases).

### Build locally

```sh
git clone https://github.com/GITHUB-USERNAME/PROJECT-NAME.git
cd PROJECT-NAME
make build
./bin/PROJECT-NAME
```

## Usage

```sh
PROJECT-NAME
```

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
````

### Notes

- The heading uses the exact binary/repository name in kebab-case (e.g., `# gh-problemas`, `# my-tool`)
- The one-liner description matches what was provided for `go.mod` and GoReleaser
- Installation section covers all four install methods: Homebrew, `go install`, release binary, and local build
- Usage section is a placeholder for the user to fill in
- License section uses the standard MIT license wording

---

## Reference: HOMEBREW_TAP_TOKEN Setup

<!-- sync: this section is duplicated in plugins/add-goreleaser-homebrew/commands/add-goreleaser-homebrew.md -->

The release workflow needs a `HOMEBREW_TAP_TOKEN` repository secret so GoReleaser can push cask updates to the Homebrew tap repository. This section walks through creating the token and setting the secret.

### 1. Check for the Homebrew Tap Repository

Verify the tap repository exists:

```bash
gh repo view GITHUB-USERNAME/homebrew-tap
```

If the repository does not exist, offer to create it:

```bash
gh repo create GITHUB-USERNAME/homebrew-tap --public --description "Homebrew tap for GITHUB-USERNAME's tools"
```

Replace `GITHUB-USERNAME` with the user's actual GitHub username throughout this section.

### 2. Check for an Existing Secret

Check whether the secret is already configured:

```bash
gh secret list | grep HOMEBREW_TAP_TOKEN || true
```

If the secret already exists, skip to step 5 (Verify) to confirm it is still configured.

### 3. Create a Fine-Grained Personal Access Token

Direct the user to create a fine-grained PAT:

1. Open <https://github.com/settings/personal-access-tokens/new>
1. **Token name**: something descriptive, e.g., `homebrew-tap-token`
1. **Expiration**: choose an appropriate duration (90 days, 1 year, or custom)
1. **Repository access**: select "Only select repositories", then choose `GITHUB-USERNAME/homebrew-tap`
1. **Permissions**: under "Repository permissions", set **Contents** to **Read and write**; leave everything else at the defaults
1. Click "Generate token" and copy the token value

Explain that this token allows GoReleaser to push cask updates to the tap repository during releases. The fine-grained PAT is preferred because it limits access to a single repository with minimal permissions.

### 4. Set the Repository Secret

Offer to set the secret using the `gh` CLI:

```bash
gh secret set HOMEBREW_TAP_TOKEN
```

This command reads the token from stdin (no echo), so the user can paste the token value securely. The secret is set on the current repository.

### 5. Verify

Confirm the secret is configured:

```bash
gh secret list | grep HOMEBREW_TAP_TOKEN || true
```

If the secret appears in the output, the setup is complete. If not, re-run step 4.

### Notes

- **No remote yet?** If the repository has not been pushed to GitHub yet (common for brand-new projects), `gh secret` commands (`gh secret set`, `gh secret list`) will fail because there is no associated GitHub repository. In that case, note the token value securely and set/verify the secret after creating the GitHub remote and pushing for the first time.
- **Classic PATs also work.** A classic personal access token with `repo` scope can be used instead of a fine-grained PAT, but classic tokens grant broader access than necessary. Fine-grained PATs scoped to the single tap repository are the recommended approach.
