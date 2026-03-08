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

- **Project name**: determine in this precedence order:
  1. If a Makefile defines a binary name (for example via a `BINARY`/`TOOL_BIN` variable or the target passed to `go build -o`), use that name.
  1. Otherwise, use the last segment of the module path in `go.mod`.
  1. Otherwise, try `git remote get-url origin`: strip any trailing `.git` from the URL and take the last path segment. If the command exits non-zero, returns empty output, or the URL cannot be parsed into a repo name, treat this as "no remote" and continue to step 4.
  1. If none of the above yield a name, ask the user for the project name.

  Do not derive the project name from the directory or branch name, which are often misleading.

- **Short description**: check the README for a one-line description; if not found, ask the user

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
   - If completions detected: add completion generation to `before.hooks`, include in `archives.files`, and set the `completions:` field
   - If man pages detected: add `before.hooks`, archive `files` section, and set the `manpages:` field
   - If macOS-only: restrict `goos`/`goarch`, remove Windows format override
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

### 11. Set Up HOMEBREW_TAP_TOKEN

The release workflow requires a `HOMEBREW_TAP_TOKEN` repository secret to publish Homebrew casks. Follow the steps in the "Reference: HOMEBREW_TAP_TOKEN Setup" section at the bottom of this file.

Ask the user whether they want to set up the token now or defer it to later. If they defer, note in the summary that the token must be configured before the first release.

### 12. Summary

Print a summary of what was created and modified:

- List every file generated or modified
- Note which conditional features were applied (completions, man pages, macOS-only)
- Remind the user to:
  - Tag a release to trigger the workflow: `git tag v0.1.0 && git push origin v0.1.0`
  - Test locally first with `goreleaser release --snapshot --clean` (or `make release-dry-run` if the Makefile was updated)
- If `HOMEBREW_TAP_TOKEN` setup was deferred in step 11: remind the user to add it as a repository secret before the first release (see "Reference: HOMEBREW_TAP_TOKEN Setup")

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
- `-X main.version={{.Version}}` injects the release version at build time; adjust the path if the version variable lives in a different package (e.g., `-X github.com/USER/REPO/cmd.version={{.Version}}`)
- Builds for Linux, macOS, and Windows on both amd64 and arm64 by default; see the Conditional Features section for macOS-only projects
- Windows archives use zip; everything else uses tar.gz
- `prerelease: auto` marks pre-release tags (e.g., `v1.0.0-rc1`) correctly on GitHub
- Changelog uses **conventional commit grouping** instead of simple sort-and-filter, organizing entries under headings (Features, Bug Fixes, Refactoring, etc.) for clearer release notes
- The `Other` group with `order: 999` acts as a catch-all for commits that do not match any specific type
- Commits prefixed with `chore:`, `test:`, or `style:` are excluded from the changelog entirely
- Uses `homebrew_casks:` (GoReleaser v2.10+) instead of the deprecated `brews:`. Casks are the correct artifact type for pre-compiled binaries distributed via GoReleaser
- The `directory` field defaults to `Casks` and is omitted; do not set it to `Formula`
- `binaries:` lists binary names to install, replacing the formula `install:` block
- Casks do not support `test:` blocks; version testing is handled differently in the Homebrew cask ecosystem
- The quarantine removal hook prevents "App is damaged" Gatekeeper errors on macOS for unsigned binaries. The `hooks.post.install` field is a string (not a list)
- Homebrew tap publishes to `GITHUB-USERNAME/homebrew-tap` using `HOMEBREW_TAP_TOKEN` (see "Reference: HOMEBREW_TAP_TOKEN Setup" for creation and configuration)
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

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents: write

jobs:
  goreleaser:
    runs-on: ubuntu-latest
    timeout-minutes: 30
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
    # macOS runner required for platform-specific builds
    runs-on: macos-latest
```

This ensures the build environment matches the target platform, which matters for projects that depend on macOS-specific APIs or frameworks.

### Notes

- Concurrency uses `cancel-in-progress: false` to avoid interrupting active releases
- Triggers on version tags (`v*` matches `v1.0.0`, `v0.1.0-rc1`, etc.)
- `fetch-depth: 0` fetches full git history (required for GoReleaser changelog generation)
- `go-version-file: go.mod` reads the Go version from `go.mod` rather than hardcoding it, so the workflow stays in sync with the project automatically
- `version: "~> v2"` uses the latest GoReleaser v2.x release
- `GITHUB_TOKEN` is provided automatically by GitHub Actions
- `HOMEBREW_TAP_TOKEN` must be added as a repository secret (see "Reference: HOMEBREW_TAP_TOKEN Setup" for creation and configuration)
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

**Note:** All `before.hooks` examples below use `go run .`, which assumes the main package is at the repository root. If `builds.main` is a subdirectory (e.g., `./cmd/PROJECT-NAME`), replace `go run .` with `go run ./cmd/PROJECT-NAME` in all hook commands.

### Shell Completions

#### Detection

Check for a `completion` subcommand in the project:

1. Look for `cmd/completion.go`
1. Grep Go files for cobra completion command registration (e.g., `"completion"` in `AddCommand` calls or `cobra.Command` literals)
1. Try running `go run . completion --help` to confirm the subcommand exists

If any of these succeed, the project has shell completions.

#### goreleaser.yml Modifications

**Add a `before` hook** to generate completion files during the build:

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p completions
    - go run . completion bash > completions/PROJECT-NAME.bash
    - go run . completion zsh > completions/PROJECT-NAME.zsh
    - go run . completion fish > completions/PROJECT-NAME.fish
```

**Add completion files to the archive** by adding a `files` section to `archives`:

```yaml
archives:
  - # ... (keep all other fields)
    files:
      - src: completions/*
        dst: completions
```

**Add completions to the cask config**:

```yaml
homebrew_casks:
  - # ... (keep all other fields from the base template)
    completions:
      bash: completions/PROJECT-NAME.bash
      zsh: completions/PROJECT-NAME.zsh
      fish: completions/PROJECT-NAME.fish
```

Completion files are pre-generated during the build via `before.hooks`, included in the release archive via `archives.files`, and referenced in the cask via the `completions:` field. This replaces the formula approach of running `generate_completions_from_executable` at install time.

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

**Add man pages to the cask config**:

```yaml
homebrew_casks:
  - # ... (keep all other fields)
    manpages:
      - man/man1/PROJECT-NAME.1
```

Man page files are pre-generated during the build via `before.hooks`, included in the release archive via `archives.files`, and referenced in the cask via the `manpages:` field. For projects with multiple man pages (e.g., per-subcommand), add an entry for each file.

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
    - mkdir -p man/man1 completions
    - go run . man man/man1
    - go run . completion bash > completions/PROJECT-NAME.bash
    - go run . completion zsh > completions/PROJECT-NAME.zsh
    - go run . completion fish > completions/PROJECT-NAME.fish

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
      - src: completions/*
        dst: completions

homebrew_casks:
  - # ... (keep all other fields)
    manpages:
      - man/man1/PROJECT-NAME.1
    completions:
      bash: completions/PROJECT-NAME.bash
      zsh: completions/PROJECT-NAME.zsh
      fish: completions/PROJECT-NAME.fish
```

#### Example: Completions + Man Pages + macOS Only

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p man/man1 completions
    - go run . man man/man1
    - go run . completion bash > completions/PROJECT-NAME.bash
    - go run . completion zsh > completions/PROJECT-NAME.zsh
    - go run . completion fish > completions/PROJECT-NAME.fish

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
      - src: completions/*
        dst: completions

homebrew_casks:
  - # ... (keep all other fields)
    manpages:
      - man/man1/PROJECT-NAME.1
    completions:
      bash: completions/PROJECT-NAME.bash
      zsh: completions/PROJECT-NAME.zsh
      fish: completions/PROJECT-NAME.fish
```

Note: When macOS-only, remove the Windows format override from archives and change the release workflow runner to `macos-latest`.

### Notes

- The detection steps are heuristics; always present detected features to the user for confirmation before applying
- Completion files must be pre-generated during build time via `before.hooks` (unlike formulas, which could generate them at install time with `generate_completions_from_executable`)
- Man pages are referenced via the `manpages:` array, which lists file paths relative to the archive root
- The `binaries:` array replaces the formula `install:` block for listing binaries to install
- Casks do not support `test:` blocks; version testing works differently in the Homebrew cask ecosystem
- The `before.hooks` section runs before each build; `go mod tidy` ensures dependencies are clean
- When combining man pages with macOS-only, the `files` section in archives still works (man pages are included in the macOS archives)

---

## Reference: HOMEBREW_TAP_TOKEN Setup

<!-- sync: this section is duplicated in plugins/scaffold-go-cli/commands/scaffold-go-cli.md -->

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

---

## Reference: Migrating Existing Projects from Formula to Cask

For projects that previously used `brews:` in their `.goreleaser.yml` and want to migrate to `homebrew_casks:`, follow these steps:

### 1. Update `.goreleaser.yml`

Replace the `brews:` section with `homebrew_casks:` per the base template above. Key changes:

- `brews:` becomes `homebrew_casks:`
- Remove `directory: Formula` (casks default to `Casks/`)
- Remove the `test:` block (casks do not support it)
- Remove the `install:` block; add `binaries:` array instead
- Add the quarantine removal `hooks.post.install` (see the base template)
- If using completions: switch from `generate_completions_from_executable` to pre-generated files with `before.hooks`, `archives.files`, and `completions:` (see the Shell Completions section)
- If using man pages: switch from `man1.install` to `manpages:` array (see the Man Pages section)

**Important**: The `hooks.post.install` field must be a **string**, not a YAML list. Using a list causes `yaml: unmarshal errors` and release failures.

### 2. Create `tap_migrations.json`

In the root of the tap repository (e.g., `GITHUB-USERNAME/homebrew-tap`), create a `tap_migrations.json` file so existing formula users automatically migrate to the cask:

```json
{
  "PROJECT-NAME": "PROJECT-NAME"
}
```

This tells Homebrew to redirect `brew install GITHUB-USERNAME/tap/PROJECT-NAME` from the old formula to the new cask.

### 3. Clean Up the Old Formula

After the first release with `homebrew_casks:` succeeds and the cask is published to the tap repository:

1. Verify the cask works: `brew install GITHUB-USERNAME/tap/PROJECT-NAME`
1. Delete the old formula file from the tap repository (e.g., `Formula/PROJECT-NAME.rb`)
1. Keep `tap_migrations.json` permanently so users with the old formula installed can upgrade
