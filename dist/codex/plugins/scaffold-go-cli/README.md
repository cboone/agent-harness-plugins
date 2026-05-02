# Scaffold Go CLI

Scaffold a complete Go CLI project with Cobra, GoReleaser, GitHub Actions CI/CD, and Homebrew tap support.

**Type:** Skill
**Trigger:** `/scaffold-go-cli`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Scaffold Go CLI** from the available plugins.

## What It Does

Generates the full boilerplate for a new Go CLI project: `main.go`, `cmd/root.go`, `go.mod`, `Makefile`, `.gitignore`, `.goreleaser.yml`, CI and release workflows, `LICENSE`, `README`, and directory stubs. Supports optional Viper config management and Charmbracelet TUI dependencies.

## Usage

```text
/scaffold-go-cli
```

The skill prompts for project name, module path, description, and optional features during setup.

## Examples

- "scaffold go cli": starts the interactive scaffolding process
- "new go cli": same behavior
- "start a go cli project": same behavior

## See Also

- [Scaffold New Repo](../scaffold-new-repo/README.md): language-agnostic repo boilerplate (included automatically)
- [Write Go Code](../write-go-code/README.md): Go style guide for writing code in the new project
- [All plugins](../../../../README.md)
