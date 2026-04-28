---
name: scaffold-go-library
description: >-
  Scaffold a Go library project with GoReleaser changelog releases,
  golangci-lint, GitHub Actions CI/CD (multi-version Go matrix), and Makefile.
  Use when the user says "scaffold a Go library", "new Go library", "create a
  Go package", "start a Go library", "bootstrap a Go library", or starts a Go
  module that exposes a library API rather than a CLI binary. For Go CLIs
  (have main.go) use scaffold-go-cli instead. For language-agnostic
  boilerplate alone, use scaffold-new-repo.
---

# Scaffold Go Library

Generate the full boilerplate for a new Go library project.

## Workflow

### 1. Gather Project Information

If the user provided a project name in their request, use it as the project name and skip asking for it. Still ask for the remaining parameters (description, minimum Go version, example tests) unless already provided in the user's initial request.

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

Read `./references/go-mod.md` for the canonical `go mod init` invocation.

```bash
go mod init github.com/GITHUB-USERNAME/PROJECT-NAME
```

No dependencies to install -- Go libraries should start stdlib-only.

### 6. Generate Package File

Read `./references/package-file.md` for the package-file template and create `PACKAGE-NAME.go` from it.

- Replace `PACKAGE-NAME` with the derived package name

This file contains the `package` declaration and a `Version` constant. No doc comment here -- that lives in `doc.go`.

### 7. Generate doc.go

Read `./references/doc-go.md` for the `doc.go` template and create `doc.go` from it.

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

Read `./references/makefile.md` for the Makefile template and create `Makefile` from it.

- Replace `PROJECT-NAME` with the project name

### 10. Generate .gitignore

Read `./references/gitignore.md` for the `.gitignore` template and create `.gitignore` from it.

No replacements needed.

If a `.gitignore` already exists, merge the template entries into it rather than overwriting.

### 11. Generate .goreleaser.yml

Read `./references/goreleaser.md` for the GoReleaser template and create `.goreleaser.yml` from it.

- Replace `PROJECT-NAME` with the project name
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username

### 12. Generate .golangci.yml

Read `./references/golangci.md` for the golangci-lint template and create `.golangci.yml` from it.

- Replace `GITHUB-USERNAME` with the detected GitHub username
- Replace `PROJECT-NAME` with the project name

### 13. Generate .editorconfig

Read `./references/editorconfig.md` for the `.editorconfig` template and create `.editorconfig` from it.

No replacements needed.

### 14. Generate CI Workflow

Read `./references/ci-workflow.md` for the CI workflow template and create `.github/workflows/ci.yml` from it.

- Replace `MINIMUM-GO-VERSION` with the minimum Go version (from step 1)

### 15. Generate Release Workflow

Read `./references/release-workflow.md` for the release workflow template and create `.github/workflows/release.yml` from it.

No replacements needed.

### 16. Generate LICENSE

Read `./references/license.md` for the LICENSE template and create `LICENSE` from it.

- Replace `YEAR` with the current year (run `date +%Y` to get it)
- Replace `COPYRIGHT-HOLDER` with the detected full name

### 17. Generate README.md

Read `./references/readme.md` for the README template and create `README.md` from it.

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

If `.github/copilot-instructions.md` exists (created by the scaffold-new-repo skill when running in the bootstrap flow, or already present in an existing repo), append the following entries to the PR review section. Before appending each entry, check whether the bold key text already exists in the file; skip entries that are already present.

To locate the PR review section: look for an existing heading whose text includes "PR Review" or "Code Review" (e.g., `## PR Review`, `## Code Review`, `## PR Review Checklist (CRITICAL)`). If no matching heading exists, append a new `## PR Review` section at the end of the file and place the entries there.

- **golangci-lint v2 config format is intentional**: This project uses golangci-lint v2 configuration which includes `formatters:` as a top-level key and supports `golangci-lint fmt` as a subcommand. These are correct v2 features. Do not suggest reverting to v1 config format.
- **`cboone/gh-actions` reusable workflows manage tool versions internally**: The CI and release workflows use `cboone/gh-actions` reusable workflows that handle tool installation, version pinning, caching, and SHA-256 verification internally. Do not suggest replacing reusable workflow calls with inlined third-party actions.

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
  - Run the add-community-files skill to add CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and .github/PULL_REQUEST_TEMPLATE.md

## Error Handling

- If `go mod init` fails, check that Go is installed and on the PATH
- If the target directory already contains Go files, ask the user before overwriting
- If `git init` fails, continue generating files but warn the user
- If the build verification fails, show the error and attempt to fix it before continuing

## Reference Templates

- `./references/go-mod.md` -- `go mod init` setup
- `./references/package-file.md` -- top-level package source file
- `./references/doc-go.md` -- `doc.go` package doc comment
- `./references/makefile.md` -- Makefile template
- `./references/gitignore.md` -- `.gitignore` template
- `./references/goreleaser.md` -- `.goreleaser.yml` template
- `./references/golangci.md` -- `.golangci.yml` template
- `./references/editorconfig.md` -- `.editorconfig` template
- `./references/ci-workflow.md` -- `.github/workflows/ci.yml`
- `./references/release-workflow.md` -- `.github/workflows/release.yml`
- `./references/license.md` -- MIT license template
- `./references/readme.md` -- README template
