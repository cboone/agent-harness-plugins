---
name: add-goreleaser-homebrew
description: >-
  Add GoReleaser configuration and a GitHub Actions release workflow to an
  existing Go CLI project with Homebrew tap publishing. Use when the user
  says "add goreleaser", "set up goreleaser", "add Homebrew tap publishing",
  "publish to Homebrew", "set up release workflow", "add release automation
  for Go", or wants a Go CLI to ship signed release artifacts and a Homebrew
  cask. Detects shell completions, man-page generation, and macOS-only
  constraints, then conditionally tailors the GoReleaser config. Pairs with
  setup-installers (alternative non-GoReleaser installer paths) and the
  release skill (cutting tagged releases).
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

Read `./references/goreleaser-base.md` for the base GoReleaser template and create `.goreleaser.yml` from it:

1. Replace `PROJECT-NAME`, `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the gathered values
1. Adjust the ldflags `-X` path based on step 5
1. Adjust the `main` path based on step 6
1. Apply conditional modifications from `./references/conditional-features.md`:
   - If completions detected: add completion generation to `before.hooks`, include in `archives.files`, and set the `completions:` field
   - If man pages detected: add `before.hooks`, archive `files` section, and set the `manpages:` field
   - If macOS-only: restrict `goos`/`goarch`, remove Windows format override
   - If multiple features detected: combine per the "Combining Features" section in `./references/conditional-features.md`

### 8. Generate Release Workflow

Read `./references/release-workflow.md` for the release workflow template and create `.github/workflows/release.yml` from it.

- If the project is macOS-only, use the macOS-only variant (`runs-on: macos-latest`)
- Otherwise, use the default (`runs-on: ubuntu-latest`)

Create the `.github/workflows/` directory if it does not exist.

### 9. Optionally Update Makefile

If a `Makefile` exists in the project root:

1. Check whether a `release-dry-run` target already exists
1. If not, offer to add it using the snippet in `./references/makefile-targets.md`
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

The release workflow requires a `HOMEBREW_TAP_TOKEN` repository secret to publish Homebrew casks. Read `./references/homebrew-tap-token.md` for the full setup steps.

Ask the user whether they want to set up the token now or defer it to later. If they defer, note in the summary that the token must be configured before the first release.

### 12. Summary

Print a summary of what was created and modified:

- List every file generated or modified
- Note which conditional features were applied (completions, man pages, macOS-only)
- Remind the user to:
  - Tag a release to trigger the workflow: `git tag v0.1.0 && git push origin v0.1.0`
  - Test locally first with `goreleaser release --snapshot --clean` (or `make release-dry-run` if the Makefile was updated)
- If `HOMEBREW_TAP_TOKEN` setup was deferred in step 11: remind the user to add it as a repository secret before the first release (see `./references/homebrew-tap-token.md`)

## Error Handling

- If `go.mod` does not exist, abort with a message that this skill requires an existing Go project
- If `.goreleaser.yml` already exists, ask before overwriting
- If `.github/workflows/release.yml` already exists, ask before overwriting
- If `goreleaser check` fails, show the error and attempt to fix the configuration
- If the user's GitHub username cannot be detected, ask for it explicitly
- If the module path in `go.mod` does not follow the `github.com/USER/REPO` pattern, ask the user for the homepage URL
- If no version variable is found in Go source files, use the default ldflags path and suggest adding `var version string` to `main.go`

## Reference Templates

- `./references/goreleaser-base.md` -- base `.goreleaser.yml` template
- `./references/release-workflow.md` -- `.github/workflows/release.yml`
- `./references/makefile-targets.md` -- `release-dry-run` Makefile snippet
- `./references/conditional-features.md` -- completions, man pages, and macOS-only modifications
- `./references/homebrew-tap-token.md` -- `HOMEBREW_TAP_TOKEN` repository-secret setup
- `./references/migration-guide.md` -- migrating from older GoReleaser configurations

## Refresh `cboone/gh-actions` SHAs before scaffolding

The `cboone/gh-actions` reusable-workflow refs in this skill's templates are SHA-pinned with a `# vX.Y.Z` comment that was current when the template was authored. New releases of `cboone/gh-actions` rot those SHAs. Before emitting a workflow into a user's repo, refresh both the SHA and the comment to current latest:

```bash
TAG="$(gh release view --repo cboone/gh-actions --json tagName --jq '.tagName')"
SHA="$(gh api "repos/cboone/gh-actions/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

Replace each `cboone/gh-actions/.../<workflow>.yml@<old-sha> # <old-tag>` in the emitted workflow with the new SHA and tag. Dependabot in the user's repo keeps them in sync afterwards.
