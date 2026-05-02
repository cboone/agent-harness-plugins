---
name: scaffold-go-cli
description: >-
  Scaffold a complete Go CLI project with Cobra, GoReleaser, GitHub Actions, and
  Homebrew tap support.
---

# Scaffold Go CLI

Generate the full boilerplate for a new Go CLI project.

## Workflow

### 1. Gather Project Information

If the user provided a project name in their request, use it as the project name and skip asking for it. Still ask for the remaining parameters (description, Viper, Charmbracelet TUI) unless already provided in the user's initial request.

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

Read `./references/main-go.md` for the `main.go` template and create the file from it.

- Replace `PROJECT-NAME` with the project name
- Replace `GITHUB-USERNAME` with the detected GitHub username

### 6. Generate cmd/root.go

Choose the template based on the Viper parameter:

- **Without Viper**: read `./references/root-go-without-viper.md`
- **With Viper**: read `./references/root-go-with-viper.md`

Replace in the chosen template:

- `PROJECT-NAME` with the project name
- `PROJECT-DESCRIPTION` with the short description

### 7. Initialize go.mod and Install Dependencies

Read `./references/go-mod.md` for the canonical setup commands. The base sequence:

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

Read `./references/makefile.md` for the Makefile template and create `Makefile` from it.

- Replace `PROJECT-NAME` with the project name

### 9. Generate .gitignore

Read `./references/gitignore.md` for the `.gitignore` template and create `.gitignore` from it.

- Replace `PROJECT-NAME` with the project name

If a `.gitignore` already exists, merge the template entries into it rather than overwriting.

### 10. Generate .goreleaser.yml

Read `./references/goreleaser.md` for the GoReleaser template and create `.goreleaser.yml` from it.

- Replace `PROJECT-NAME` with the project name
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username

### 11. Generate CI Workflow

Read `./references/ci-workflow.md` for the CI workflow template and create `.github/workflows/ci.yml` from it.

No replacements needed (the workflow is project-name-independent).

### 12. Generate Release Workflow

Read `./references/release-workflow.md` for the release workflow template and create `.github/workflows/release.yml` from it.

No replacements needed.

### 13. Generate LICENSE

Read `./references/license.md` for the LICENSE template and create `LICENSE` from it.

- Replace `YEAR` with the current year (run `date +%Y` to get it)
- Replace `COPYRIGHT-HOLDER` with the detected full name

### 14. Generate README.md

Read `./references/readme.md` for the README template and create `README.md` from it.

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

The release workflow requires a `HOMEBREW_TAP_TOKEN` repository secret to publish Homebrew casks. Read `./references/homebrew-tap-token.md` for the full setup steps.

Ask the user whether they want to set up the token now or defer it to later. If they defer, note in the summary that the token must be configured before the first release.

Note: for brand-new projects that have not been pushed to GitHub yet, `gh secret` commands (including `gh secret set` and `gh secret list`) will not work until a GitHub remote exists. See the "No remote yet?" note in the reference.

### 21. Summary

Print a summary of what was created:

- List every file and directory generated
- Note which optional features were included (Viper, Charmbracelet TUI)
- Remind the user to:
  - Add subcommands under `cmd/` as the CLI grows
  - Run `make help` to see available Makefile targets
  - Run the add-community-files skill to add CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and .github/PULL_REQUEST_TEMPLATE.md
- If `HOMEBREW_TAP_TOKEN` setup was deferred in step 20: check whether a GitHub remote exists and is accessible before creating a follow-up issue:

  ```bash
  if git remote get-url origin >/dev/null 2>&1 && gh repo view >/dev/null 2>&1; then
    gh issue create \
      --title "Set up HOMEBREW_TAP_TOKEN repository secret" \
      --body "The release workflow needs a HOMEBREW_TAP_TOKEN secret so GoReleaser can push Homebrew cask updates to the tap repository.

  See the HOMEBREW_TAP_TOKEN Setup reference in the scaffold-go-cli skill documentation for step-by-step instructions."
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

## Reference Templates

- `./references/main-go.md` -- `main.go` template
- `./references/root-go-without-viper.md` -- `cmd/root.go` without Viper
- `./references/root-go-with-viper.md` -- `cmd/root.go` with Viper
- `./references/go-mod.md` -- `go mod init` and dependency setup
- `./references/makefile.md` -- Makefile template
- `./references/gitignore.md` -- `.gitignore` template
- `./references/goreleaser.md` -- `.goreleaser.yml` template
- `./references/ci-workflow.md` -- `.github/workflows/ci.yml`
- `./references/release-workflow.md` -- `.github/workflows/release.yml`
- `./references/license.md` -- MIT license template
- `./references/readme.md` -- README template
- `./references/homebrew-tap-token.md` -- `HOMEBREW_TAP_TOKEN` repository-secret setup

## Refresh `cboone/gh-actions` SHAs before scaffolding

The `cboone/gh-actions` reusable-workflow refs in this skill's templates are SHA-pinned with a `# vX.Y.Z` comment that was current when the template was authored. New releases of `cboone/gh-actions` rot those SHAs. Before emitting a workflow into a user's repo, refresh both the SHA and the comment to current latest:

```bash
TAG="$(gh release view --repo cboone/gh-actions --json tagName --jq '.tagName')"
SHA="$(gh api "repos/cboone/gh-actions/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

Replace each `cboone/gh-actions/.../<workflow>.yml@<old-sha> # <old-tag>` in the emitted workflow with the new SHA and tag. Dependabot in the user's repo keeps them in sync afterwards.
