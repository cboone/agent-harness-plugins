---
name: scaffold-go-cli
description: >-
  Scaffold a complete Go CLI project with Cobra, GoReleaser, GitHub Actions CI/CD,
  Homebrew tap, and Makefile, following cboone's established patterns. Use when the
  user says "scaffold go cli", "new go cli", "create go cli", "scaffold go project",
  "new go project", "start a go cli", or asks to generate boilerplate for a Go
  command-line tool.
---

# Scaffold Go CLI

Generate the full boilerplate for a new Go CLI project following cboone's conventions.

## Workflow

### 1. Gather Project Information

Ask the user for these parameters:

- **Project name** -- kebab-case, used as the binary name, module path, and directory name (e.g., `my-tool`)
- **Short description** -- one sentence, used in README, GoReleaser Homebrew formula, and the Cobra root command `Short` field
- **Include Viper?** -- whether to add Viper for config file management (adds `--config` flag and `~/.config/<name>/config.yaml` support)
- **Include Charmbracelet TUI?** -- whether to add bubbletea, lipgloss, and bubbles dependencies

If the user already provided some or all of these in their initial request, do not re-ask. Derive what you can from context.

### 2. Verify the Target Directory

The project should be scaffolded in a directory named after the project. If the current directory is already named after the project and is empty (or nearly empty), use it. Otherwise, create a subdirectory.

If the directory already contains Go files, warn the user before proceeding.

### 3. Initialize Git

Skip if already inside a git repository.

```bash
git init
```

### 4. Generate main.go

Create `main.go` using the template from `./references/main-go.md`.

- Replace `PROJECT-NAME` with the project name

### 5. Generate cmd/root.go

Choose the template based on the Viper parameter:

- **Without Viper**: use `./references/root-go.md`
- **With Viper**: use `./references/root-go-viper.md`

Replace in the chosen template:

- `PROJECT-NAME` with the project name
- `PROJECT-DESCRIPTION` with the short description

### 6. Initialize go.mod and Install Dependencies

Follow the instructions in `./references/go-mod.md`:

```bash
go mod init github.com/cboone/PROJECT-NAME
go get github.com/spf13/cobra@latest
```

If Viper was selected:

```bash
go get github.com/spf13/viper@latest
```

If Charmbracelet TUI was selected:

```bash
go get github.com/charmbracelet/bubbletea@latest
go get github.com/charmbracelet/lipgloss@latest
go get github.com/charmbracelet/bubbles@latest
```

Then tidy:

```bash
go mod tidy
```

### 7. Generate Makefile

Create `Makefile` using the template from `./references/makefile.md`.

- Replace `PROJECT-NAME` with the project name

### 8. Generate .gitignore

Create `.gitignore` using the template from `./references/gitignore.md`.

- Replace `PROJECT-NAME` with the project name

If a `.gitignore` already exists, merge the template entries into it rather than overwriting.

### 9. Generate .goreleaser.yml

Create `.goreleaser.yml` using the template from `./references/goreleaser.md`.

- Replace `PROJECT-NAME` with the project name
- Replace `PROJECT-DESCRIPTION` with the short description

### 10. Generate CI Workflow

Create `.github/workflows/ci.yml` using the template from `./references/ci-workflow.md`.

No replacements needed (the workflow is project-name-independent).

### 11. Generate Release Workflow

Create `.github/workflows/release.yml` using the template from `./references/release-workflow.md`.

No replacements needed.

### 12. Generate LICENSE

Create `LICENSE` using the template from `./references/license.md`.

- Replace `YEAR` with the current year (run `date +%Y` to get it)

### 13. Generate README.md

Create `README.md` using the template from `./references/readme.md`.

- Replace `PROJECT-NAME` with the project name (kebab-case)
- Replace `PROJECT-TITLE` with the project name in title case
- Replace `PROJECT-DESCRIPTION` with the short description

### 14. Create Directory Stubs

Create stub directories for the standard project layout:

```bash
# internal package stub
mkdir -p internal
touch internal/.gitkeep

# plans directory
mkdir -p docs/plans
touch docs/plans/.gitkeep

# tests directory
mkdir -p tests
touch tests/.gitkeep
```

### 15. Verify the Build

Run a quick build to confirm everything compiles:

```bash
go build ./...
```

If the build fails, diagnose and fix the issue before continuing.

### 16. Create Initial Commit

Stage all generated files and create the initial commit:

```bash
git add -A
git commit -S -m "feat: scaffold Go CLI project"
```

### 17. Summary

Print a summary of what was created:

- List every file and directory generated
- Note which optional features were included (Viper, Charmbracelet TUI)
- Remind the user to:
  - Add `HOMEBREW_TAP_TOKEN` as a repository secret for releases
  - Add subcommands under `cmd/` as the CLI grows
  - Run `make help` to see available Makefile targets

## Error Handling

- If `go mod init` fails, check that Go is installed and on the PATH
- If `go get` fails for any dependency, check network connectivity and retry once
- If the target directory already contains Go files, ask the user before overwriting
- If `git init` fails, continue generating files but warn the user
- If the build verification fails, show the error and attempt to fix it before continuing
