---
name: scaffold-go-library
description: >-
  Scaffold a Go library project with GoReleaser changelog releases, golangci-lint,
  GitHub Actions CI/CD, and Makefile. Use when the user says "scaffold go library",
  "new go library", "create go library", "scaffold go package", "new go package",
  "start a go library", or asks to generate boilerplate for a Go library or package.
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

Follow the instructions in `./references/go-mod.md`:

```bash
go mod init github.com/GITHUB-USERNAME/PROJECT-NAME
```

No dependencies to install -- Go libraries should start stdlib-only.

### 6. Generate Package File

Create `PACKAGE-NAME.go` using the template from `./references/package-go.md`.

- Replace `PACKAGE-NAME` with the derived package name

This file contains the `package` declaration and a `Version` constant. No doc comment here -- that lives in `doc.go`.

### 7. Generate doc.go

Create `doc.go` using the template from `./references/doc-go.md`.

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

Create `Makefile` using the template from `./references/makefile.md`.

- Replace `PROJECT-NAME` with the project name

### 10. Generate .gitignore

Create `.gitignore` using the template from `./references/gitignore.md`.

No replacements needed.

If a `.gitignore` already exists, merge the template entries into it rather than overwriting.

### 11. Generate .goreleaser.yml

Create `.goreleaser.yml` using the template from `./references/goreleaser.md`.

- Replace `PROJECT-NAME` with the project name
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username

### 12. Generate .golangci.yml

Create `.golangci.yml` using the template from `./references/golangci.md`.

- Replace `GITHUB-USERNAME` with the detected GitHub username
- Replace `PROJECT-NAME` with the project name

### 13. Generate .editorconfig

Create `.editorconfig` using the template from `./references/editorconfig.md`.

No replacements needed.

### 14. Generate CI Workflow

Create `.github/workflows/ci.yml` using the template from `./references/ci-workflow.md`.

- Replace `MINIMUM-GO-VERSION` with the minimum Go version (from step 1)

### 15. Generate Release Workflow

Create `.github/workflows/release.yml` using the template from `./references/release-workflow.md`.

No replacements needed.

### 16. Generate LICENSE

Create `LICENSE` using the template from `./references/license.md`.

- Replace `YEAR` with the current year (run `date +%Y` to get it)
- Replace `COPYRIGHT-HOLDER` with the detected full name

### 17. Generate README.md

Create `README.md` using the template from `./references/readme.md`.

- Replace `PROJECT-NAME` with the project name (kebab-case)
- Replace `PROJECT-TITLE` with the project name in title case
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username
- Replace `PACKAGE-NAME` with the derived package name

### 18. Create Directory Stubs

Create stub directories for the standard library layout:

```bash
# plans directory
mkdir -p docs/plans
touch docs/plans/.gitkeep
```

Libraries keep tests alongside source files, so no `tests/` directory. No `internal/` directory -- add it when needed.

### 19. Tidy Modules

```bash
go mod tidy
```

### 20. Verify the Build

Run a quick build to confirm everything compiles:

```bash
go build ./...
```

If the build fails, diagnose and fix the issue before continuing.

### 21. Create Initial Commit

Stage all generated files and create the initial commit:

```bash
git add -A
git commit -S -m "feat: scaffold Go library project"
```

### 22. Summary

Print a summary of what was created:

- List every file and directory generated
- Note whether example tests were included
- Remind the user to:
  - Run `make help` to see available Makefile targets
  - Tag releases with `git tag v0.1.0 && git push --tags` to trigger GoReleaser
  - Write tests alongside source files (e.g., `PACKAGE-NAME_test.go`)
  - Use `make coverage` to generate an HTML coverage report

## Error Handling

- If `go mod init` fails, check that Go is installed and on the PATH
- If the target directory already contains Go files, ask the user before overwriting
- If `git init` fails, continue generating files but warn the user
- If the build verification fails, show the error and attempt to fix it before continuing
