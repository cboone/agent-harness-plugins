---
description: Add GoReleaser configuration and a GitHub Actions release workflow to an existing Go CLI project with Homebrew tap publishing.
disable-model-invocation: true
---

# Add GoReleaser Homebrew

Add GoReleaser configuration and a GitHub Actions release workflow to an existing Go CLI project with Homebrew tap publishing.

## Workflow

### 1. Verify the Project

Confirm the current directory is a Go CLI project:

- Check that `go.mod` exists (required; abort if missing)
- Read `go.mod` to extract the module path (needed for ldflags and URLs)
- Check for an existing `.goreleaser.yml` or `.goreleaser.yaml`; if present, warn and ask whether to overwrite or abort
- Check for an existing `.github/workflows/release.yml`; if present, warn and ask whether to overwrite or abort

### 2. Detect User Identity

Detect the user's GitHub username for use in templates:

```bash
gh api user -q .login
```

If the command fails or produces no output, ask the user to provide their GitHub username. Use it wherever templates reference `GITHUB-USERNAME`.

### 3. Gather Project Information

Collect the following, inferring from existing files where possible:

- **Project name**: derive from the binary name in the Makefile, the last segment of the module path in `go.mod`, or the git remote URL (run `git remote get-url origin`, strip trailing `.git`, take the last path segment). Do not derive from the directory or branch name, which are often misleading.
- **Short description**: check the README for a one-line description; if not found, ask the user
- **Homebrew dependencies**: ask whether the tool has any runtime dependencies to declare in the formula (e.g., `gh`, `docker`)

If the user already provided some or all of these in their initial request, do not re-ask.

### 4. Detect Project Features

Check for three conditional features. For each, use the detection steps described in the Conditional Features section below:

**Shell completions:**

1. Look for `cmd/completion.go`
1. Grep Go files for cobra completion command registration
1. Try `go run . completion --help`

**Man page generation:**

1. Look for `cmd/man.go`
1. Grep Go files for `cobra/doc` or `mango` imports
1. Try `go run . man --help`

**macOS-only constraints:**

1. Check for `//go:build darwin` build constraints
1. Check the Makefile for `GOOS=darwin`
1. If inconclusive, ask the user

Present all detected features to the user and let them confirm or override before proceeding.

### 5. Determine ldflags Target

Find where the version variable is declared:

1. Grep for `var version` in Go files (commonly in `main.go` or `cmd/root.go`)
1. If found in `main.go` or package `main`, use `-X main.version={{.Version}}`
1. If found in a `cmd` package, use `-X MODULE-PATH/cmd.version={{.Version}}`
1. If not found, default to `-X main.version={{.Version}}` and note that the user should add a `var version string` declaration

### 6. Determine Build Entry Point

Check where `func main()` is defined:

1. If `main.go` exists in the repository root, use `main: .`
1. If `main.go` exists in a subdirectory (e.g., `cmd/PROJECT-NAME/main.go`), use `main: ./cmd/PROJECT-NAME`
1. If unclear, default to `main: .`

### 7. Generate .goreleaser.yml

Create `.goreleaser.yml` using the base template from the .goreleaser.yml Template section below:

1. Replace `PROJECT-NAME`, `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the gathered values
1. Adjust the ldflags `-X` path based on step 5
1. Adjust the `main` path based on step 6
1. Apply conditional modifications from the Conditional Features section below:
   - If completions detected: add custom `install` block with `generate_completions_from_executable`
   - If man pages detected: add `before.hooks`, archive `files` section, and `man1.install` in the brew formula
   - If macOS-only: restrict `goos`/`goarch`, remove Windows format override, add `depends_on :macos`
   - If multiple features detected: combine per the "Combining Features" section in the Conditional Features section below

### 8. Generate Release Workflow

Create `.github/workflows/release.yml` using the template from the Release Workflow Template section below.

- If the project is macOS-only, use the macOS-only variant (`runs-on: macos-latest`)
- Otherwise, use the default (`runs-on: ubuntu-latest`)

Create the `.github/workflows/` directory if it does not exist.

### 9. Optionally Update Makefile

If a `Makefile` exists in the project root:

1. Check whether a `release-dry-run` target already exists
1. If not, offer to add it using the snippet from the Makefile Target section below
1. Append `release-dry-run` to the `.PHONY` declaration
1. Add the target block

If no Makefile exists, skip this step.

### 10. Verify Configuration

If `goreleaser` is installed locally, validate the generated config:

```bash
goreleaser check
```

If the check fails, review the error and fix the configuration.

If `goreleaser` is not installed, skip validation and note that the user can install it with `brew install goreleaser` to validate locally.

### 11. Summary

Print a summary of what was created and modified:

- List every file generated or modified
- Note which conditional features were applied (completions, man pages, macOS-only)
- Remind the user to:
  - Add `HOMEBREW_TAP_TOKEN` as a repository secret in Settings > Secrets and variables > Actions (a PAT with repo scope on the `homebrew-tap` repository)
  - Tag a release to trigger the workflow: `git tag v0.1.0 && git push origin v0.1.0`
  - Test locally first with `goreleaser release --snapshot --clean` (or `make release-dry-run` if the Makefile was updated)

## Error Handling

- If `go.mod` does not exist, abort with a message that this command requires an existing Go project
- If `.goreleaser.yml` already exists, ask before overwriting
- If `.github/workflows/release.yml` already exists, ask before overwriting
- If `goreleaser check` fails, show the error and attempt to fix the configuration
- If the user's GitHub username cannot be detected, ask for it explicitly
- If the module path in `go.mod` does not follow the `github.com/USER/REPO` pattern, ask the user for the homepage URL
- If no version variable is found in Go source files, use the default ldflags path and suggest adding `var version string` to `main.go`

---

## Reference: .goreleaser.yml Template

Use this template for GoReleaser configuration when adding release automation to an existing Go CLI project. Replace `PROJECT-NAME`, `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the actual values.

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
  groups:
    - title: Features
      regexp: '^.*?feat(\(.+\))?\!?:.+$'
      order: 0
    - title: Bug Fixes
      regexp: '^.*?fix(\(.+\))?\!?:.+$'
      order: 1
    - title: Performance
      regexp: '^.*?perf(\(.+\))?\!?:.+$'
      order: 2
    - title: Refactoring
      regexp: '^.*?refactor(\(.+\))?\!?:.+$'
      order: 3
    - title: Documentation
      regexp: '^.*?docs(\(.+\))?\!?:.+$'
      order: 4
    - title: Build
      regexp: '^.*?(build|ci)(\(.+\))?\!?:.+$'
      order: 5
    - title: Other
      order: 999
  filters:
    exclude:
      - "^chore:"
      - "^test:"
      - "^style:"

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
- `-X main.version={{.Version}}` injects the release version at build time; adjust the path if the version variable lives in a different package (e.g., `-X github.com/USER/REPO/cmd.version={{.Version}}`)
- Builds for Linux, macOS, and Windows on both amd64 and arm64 by default; see `conditional-features.md` for macOS-only projects
- Windows archives use zip; everything else uses tar.gz
- `prerelease: auto` marks pre-release tags (e.g., `v1.0.0-rc1`) correctly on GitHub
- Changelog uses **conventional commit grouping** instead of simple sort-and-filter, organizing entries under headings (Features, Bug Fixes, Refactoring, etc.) for clearer release notes
- The `Other` group with `order: 999` acts as a catch-all for commits that do not match any specific type
- Commits prefixed with `chore:`, `test:`, or `style:` are excluded from the changelog entirely
- Homebrew tap publishes to `GITHUB-USERNAME/homebrew-tap` using `HOMEBREW_TAP_TOKEN` (a PAT with repo scope on the homebrew-tap repository)
- The `{{` and `}}` delimiters are GoReleaser template syntax, not Go templates

---

## Reference: Release Workflow Template

Use this template for `.github/workflows/release.yml`. No placeholder replacements are needed; the workflow is project-name-independent.

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

### macOS-Only Variant

For projects that only target macOS, change the runner:

```yaml
jobs:
  goreleaser:
    runs-on: macos-latest
```

This ensures the build environment matches the target platform, which matters for projects that depend on macOS-specific APIs or frameworks.

### Notes

- Triggers on version tags (`v*` matches `v1.0.0`, `v0.1.0-rc1`, etc.)
- `fetch-depth: 0` fetches full git history (required for GoReleaser changelog generation)
- `go-version-file: go.mod` reads the Go version from `go.mod` rather than hardcoding it, so the workflow stays in sync with the project automatically
- `version: "~> v2"` uses the latest GoReleaser v2.x release
- `GITHUB_TOKEN` is provided automatically by GitHub Actions
- `HOMEBREW_TAP_TOKEN` must be added as a repository secret (a PAT with repo scope on the user's `homebrew-tap` repository)
- `--clean` removes previous build artifacts before releasing

---

## Reference: Makefile Target

Add this target to an existing Makefile so developers can test the GoReleaser configuration locally without publishing.

```makefile
release-dry-run: ## Run GoReleaser in dry-run mode (no publish)
	goreleaser release --snapshot --clean
```

### How to Merge into an Existing Makefile

1. **Add to `.PHONY`**: Find the existing `.PHONY` line and append `release-dry-run`. For example:

   ```makefile
   .PHONY: build test lint vet fmt clean cover tidy help release-dry-run
   ```

1. **Append the target**: Add the `release-dry-run` target block at the end of the file, before the `help` target if one exists (so it appears in `make help` output).

1. **Verify the tab character**: The command line under `release-dry-run:` must use a literal tab, not spaces.

### Notes

- `--snapshot` builds the release artifacts locally without creating a GitHub release or publishing to Homebrew
- `--clean` removes any previous snapshot artifacts before building
- The `## ...` comment after the target name is a self-documenting Makefile convention that makes the target appear in `make help` output (when the Makefile includes a help target that greps for `##`)
- This target is optional; only add it if the project has a Makefile

---

## Reference: Conditional Features

Apply these modifications to the base `.goreleaser.yml` template and release workflow based on detected project features. Each section describes how to detect the feature and what to change.

### Shell Completions

#### Detection

Check for a `completion` subcommand in the project:

1. Look for `cmd/completion.go`
1. Grep Go files for cobra completion command registration (e.g., `"completion"` in `AddCommand` calls or `cobra.Command` literals)
1. Try running `go run . completion --help` to confirm the subcommand exists

If any of these succeed, the project has shell completions.

#### goreleaser.yml Modifications

Replace the basic `test` block in `brews` with a custom `install` block that generates completions:

```yaml
brews:
  - # ... (keep all other fields from the base template)
    install: |
      bin.install "PROJECT-NAME"

      generate_completions_from_executable(bin/"PROJECT-NAME", "completion")
    test: |
      assert_match version.to_s, shell_output("#{bin}/PROJECT-NAME --version")
```

The `generate_completions_from_executable` Homebrew helper automatically calls the binary's `completion` subcommand for bash, zsh, and fish, and installs the output files in the correct locations.

### Man Pages

#### Detection

Check for man page generation capability in the project:

1. Look for `cmd/man.go`
1. Grep Go files for `cobra/doc` or `mango` imports (common man page generators for Cobra CLIs)
1. Try running `go run . man --help` to confirm the subcommand exists

If any of these succeed, the project can generate man pages.

#### goreleaser.yml Modifications

**Add a `before` hook** to generate man pages during the build:

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p man/man1
    - go run . man man/man1
```

**Add man pages to the archive** by adding a `files` section to `archives`:

```yaml
archives:
  - formats:
      - tar.gz
    format_overrides:
      - goos: windows
        formats:
          - zip
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
    files:
      - src: man/man1/*
        dst: man/man1
```

**Add man page installation to the brew formula** in the `install` block:

```yaml
brews:
  - # ... (keep all other fields)
    install: |
      bin.install "PROJECT-NAME"
      man1.install Dir["man/man1/*"]
    test: |
      assert_match version.to_s, shell_output("#{bin}/PROJECT-NAME --version")
```

### macOS Only

#### Detection

Check whether the project targets macOS exclusively:

1. Look for `//go:build darwin` or `// +build darwin` build constraints in `.go` files
1. Check the Makefile for `GOOS=darwin` in build commands
1. Check for macOS-specific dependencies (e.g., `darwin` in `go.mod` comments, Objective-C bindings, or Apple framework imports)
1. If detection is inconclusive, ask the user

#### goreleaser.yml Modifications

**Restrict the build matrix** to macOS only:

```yaml
builds:
  - # ... (keep other fields)
    goos:
      - darwin
    goarch:
      - arm64
```

Note: Use `goarch: [arm64]` for Apple Silicon-only tools. Use `goarch: [amd64, arm64]` if the tool should also support Intel Macs.

**Remove the Windows format override** from archives (no longer needed):

```yaml
archives:
  - formats:
      - tar.gz
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
```

**Add a macOS requirement** to the brew formula using `custom_block`:

```yaml
brews:
  - # ... (keep other fields)
    custom_block: |
      depends_on :macos
```

#### .github/workflows/release.yml Modifications

Change the runner to `macos-latest`:

```yaml
jobs:
  goreleaser:
    runs-on: macos-latest
```

### Combining Features

When multiple conditional features are present, combine all applicable modifications into a single configuration. The most common combination is **completions + man pages** (as seen in bopca).

#### Example: Completions + Man Pages

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p man/man1
    - go run . man man/man1

archives:
  - formats:
      - tar.gz
    format_overrides:
      - goos: windows
        formats:
          - zip
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
    files:
      - src: man/man1/*
        dst: man/man1

brews:
  - # ... (keep all other fields)
    install: |
      bin.install "PROJECT-NAME"
      man1.install Dir["man/man1/*"]

      generate_completions_from_executable(bin/"PROJECT-NAME", "completion")
    test: |
      assert_match version.to_s, shell_output("#{bin}/PROJECT-NAME --version")
```

#### Example: Completions + Man Pages + macOS Only

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p man/man1
    - go run . man man/man1

builds:
  - main: .
    binary: PROJECT-NAME
    env:
      - CGO_ENABLED=0
    goos:
      - darwin
    goarch:
      - arm64
    ldflags:
      - -s -w
      - -X main.version={{.Version}}

archives:
  - formats:
      - tar.gz
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
    files:
      - src: man/man1/*
        dst: man/man1

brews:
  - # ... (keep all other fields)
    install: |
      bin.install "PROJECT-NAME"
      man1.install Dir["man/man1/*"]

      generate_completions_from_executable(bin/"PROJECT-NAME", "completion")
    custom_block: |
      depends_on :macos
    test: |
      assert_match version.to_s, shell_output("#{bin}/PROJECT-NAME --version")
```

Note: When macOS-only, remove the Windows format override from archives and change the release workflow runner to `macos-latest`.

### Notes

- The detection steps are heuristics; always present detected features to the user for confirmation before applying
- `generate_completions_from_executable` is a Homebrew helper that calls the binary's completion subcommand for each shell (bash, zsh, fish) and installs the output
- `man1.install Dir["man/man1/*"]` is a Homebrew helper that installs man pages into the correct system location
- The `before.hooks` section runs before each build; `go mod tidy` ensures dependencies are clean
- When combining man pages with macOS-only, the `files` section in archives still works (man pages are included in the macOS archives)
