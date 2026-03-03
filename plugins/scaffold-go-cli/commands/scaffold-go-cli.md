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
- **Short description** -- one sentence, used in README, GoReleaser Homebrew formula, and the Cobra root command `Short` field
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
- Replace `PROJECT-TITLE` with the project name in title case
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

### 19. Set Up HOMEBREW_TAP_TOKEN

The release workflow requires a `HOMEBREW_TAP_TOKEN` repository secret to publish Homebrew formulas. Follow the steps in the "Reference: HOMEBREW_TAP_TOKEN Setup" section at the bottom of this file.

Ask the user whether they want to set up the token now or defer it to later. If they defer, note in the summary that the token must be configured before the first release.

Note: for brand-new projects that have not been pushed to GitHub yet, `gh secret` commands (including `gh secret set` and `gh secret list`) will not work until a GitHub remote exists. See the "No remote yet?" note in the reference section.

### 20. Summary

Print a summary of what was created:

- List every file and directory generated
- Note which optional features were included (Viper, Charmbracelet TUI)
- Remind the user to:
  - Add subcommands under `cmd/` as the CLI grows
  - Run `make help` to see available Makefile targets
  - Run `/add-community-files` to add CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and .github/PULL_REQUEST_TEMPLATE.md
- If `HOMEBREW_TAP_TOKEN` setup was deferred in step 19: remind the user to add it as a repository secret before the first release (see "Reference: HOMEBREW_TAP_TOKEN Setup")

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

test: ## Run tests
	go test ./...

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

brews:
  - repository:
      owner: GITHUB-USERNAME
      name: homebrew-tap
      token: "{{ .Env.HOMEBREW_TAP_TOKEN }}"
    directory: Formula
    homepage: "https://github.com/GITHUB-USERNAME/PROJECT-NAME"
    description: "PROJECT-DESCRIPTION"
    license: MIT
    test: |
      assert_match version.to_s, shell_output("#{bin}/PROJECT-NAME --version")
```

### Notes

- Uses GoReleaser v2 config format (`version: 2`)
- `CGO_ENABLED=0` produces static binaries (no C library dependency)
- `-s -w` in ldflags strips debug info and symbol tables (smaller binary)
- `-X main.version={{.Version}}` injects the release version at build time
- Builds for Linux, macOS, and Windows on both amd64 and arm64
- Windows archives use zip; everything else uses tar.gz
- Homebrew tap publishes to `GITHUB-USERNAME/homebrew-tap` using `HOMEBREW_TAP_TOKEN` (see "Reference: HOMEBREW_TAP_TOKEN Setup" for creation and configuration)
- `prerelease: auto` marks pre-release tags (e.g., `v1.0.0-rc1`) correctly on GitHub
- The `{{` and `}}` delimiters are GoReleaser template syntax, not Go templates

## Reference: CI Workflow Template

Use this template for `.github/workflows/ci.yml`.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - name: Run tests
        run: make test

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - name: Run vet
        run: make vet

      - name: Check formatting
        run: make fmt

  vulncheck:
    name: Vulnerability check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - name: Install govulncheck
        run: go install golang.org/x/vuln/cmd/govulncheck@latest

      - name: Run govulncheck
        run: govulncheck ./...
```

### Notes

- Triggers on pushes to main and on pull requests targeting main
- `permissions: contents: read` follows the principle of least privilege
- Uses `go-version-file: go.mod` instead of pinning a Go version (stays current automatically)
- Test, lint, and vulncheck are separate jobs so they run in parallel
- The lint job runs `vet` and `fmt` (both are fast and catch different issues)
- The vulncheck job uses `govulncheck` from the Go team to detect known vulnerabilities in dependencies
- `golangci-lint` is not included in CI by default; add it when the project is ready for stricter linting

## Reference: Release Workflow Template

Use this template for `.github/workflows/release.yml`.

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write

jobs:
  goreleaser:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - uses: goreleaser/goreleaser-action@v6
        with:
          version: "~> v2"
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}
```

### Notes

- Triggers on version tags (`v*` matches `v1.0.0`, `v0.1.0-rc1`, etc.)
- `fetch-depth: 0` fetches full git history (required for GoReleaser changelog generation)
- `version: "~> v2"` uses the latest GoReleaser v2.x release
- `GITHUB_TOKEN` is provided automatically by GitHub Actions
- `HOMEBREW_TAP_TOKEN` must be added as a repository secret (see "Reference: HOMEBREW_TAP_TOKEN Setup" for creation and configuration)
- `--clean` removes previous build artifacts before releasing

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

Use this template for the project `README.md`. Replace `PROJECT-NAME` (kebab-case), `PROJECT-TITLE` (title case), `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the actual values.

````markdown
# PROJECT-TITLE

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

- The heading uses the project name in title case (e.g., "Right Round", "Maze War++")
- The one-liner description matches what was provided for `go.mod` and GoReleaser
- Installation section covers all four install methods: Homebrew, `go install`, release binary, and local build
- Usage section is a placeholder for the user to fill in
- License section uses the standard MIT license wording

---

## Reference: HOMEBREW_TAP_TOKEN Setup

<!-- sync: this section is duplicated in plugins/add-goreleaser-homebrew/commands/add-goreleaser-homebrew.md -->

The release workflow needs a `HOMEBREW_TAP_TOKEN` repository secret so GoReleaser can push formula updates to the Homebrew tap repository. This section walks through creating the token and setting the secret.

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

Explain that this token allows GoReleaser to push formula updates to the tap repository during releases. The fine-grained PAT is preferred because it limits access to a single repository with minimal permissions.

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
