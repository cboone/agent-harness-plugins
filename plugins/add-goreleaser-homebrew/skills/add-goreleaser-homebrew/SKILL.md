---
name: add-goreleaser-homebrew
description: >-
  Add GoReleaser configuration and a GitHub Actions release workflow to an
  existing Go CLI project with Homebrew tap publishing. Use when the user says
  "add goreleaser", "add homebrew", "add release workflow", "set up goreleaser",
  "set up homebrew tap", "add goreleaser homebrew", "configure releases",
  "add release pipeline", or asks to add automated releases or Homebrew
  distribution to an existing Go project.
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

- **Project name**: derive from the binary name in the Makefile, the last segment of the module path in `go.mod`, or the git remote URL (not from the directory or branch name, which are often misleading)
- **Short description**: check the README for a one-line description; if not found, ask the user
- **Homebrew dependencies**: ask whether the tool has any runtime dependencies to declare in the formula (e.g., `gh`, `docker`)

If the user already provided some or all of these in their initial request, do not re-ask.

### 4. Detect Project Features

Check for three conditional features. For each, use the detection steps described in `./references/conditional-features.md`:

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

Create `.goreleaser.yml` using the base template from `./references/goreleaser.md`:

1. Replace `PROJECT-NAME`, `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the gathered values
1. Adjust the ldflags `-X` path based on step 5
1. Adjust the `main` path based on step 6
1. Apply conditional modifications from `./references/conditional-features.md`:
   - If completions detected: add custom `install` block with `generate_completions_from_executable`
   - If man pages detected: add `before.hooks`, archive `files` section, and `man1.install` in the brew formula
   - If macOS-only: restrict `goos`/`goarch`, remove Windows format override, add `depends_on :macos`
   - If multiple features detected: combine per the "Combining Features" section in `./references/conditional-features.md`

### 8. Generate Release Workflow

Create `.github/workflows/release.yml` using the template from `./references/release-workflow.md`.

- If the project is macOS-only, use the macOS-only variant (`runs-on: macos-latest`)
- Otherwise, use the default (`runs-on: ubuntu-latest`)

Create the `.github/workflows/` directory if it does not exist.

### 9. Optionally Update Makefile

If a `Makefile` exists in the project root:

1. Check whether a `release-dry-run` target already exists
1. If not, offer to add it using the snippet from `./references/makefile-target.md`
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

## Reference Navigation

- `./references/goreleaser.md`: base `.goreleaser.yml` template with conventional commit changelog grouping
- `./references/release-workflow.md`: GitHub Actions release workflow template with macOS-only variant
- `./references/makefile-target.md`: optional `release-dry-run` Makefile target snippet
- `./references/conditional-features.md`: detection logic and configuration modifications for completions, man pages, and macOS-only builds

## Error Handling

- If `go.mod` does not exist, abort with a message that this skill requires an existing Go project
- If `.goreleaser.yml` already exists, ask before overwriting
- If `.github/workflows/release.yml` already exists, ask before overwriting
- If `goreleaser check` fails, show the error and attempt to fix the configuration
- If the user's GitHub username cannot be detected, ask for it explicitly
- If the module path in `go.mod` does not follow the `github.com/USER/REPO` pattern, ask the user for the homepage URL
- If no version variable is found in Go source files, use the default ldflags path and suggest adding `var version string` to `main.go`
