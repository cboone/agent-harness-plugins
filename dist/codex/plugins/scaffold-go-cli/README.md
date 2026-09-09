# Scaffold Go CLI

Scaffold a complete Go CLI project with Cobra, GoReleaser, GitHub Actions, and Homebrew tap support.

**Type:** Skill
**Trigger:** `/scaffold-go-cli`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

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

## Recommended Permissions

This skill runs git, GitHub CLI, and Go commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git init*)", "Bash(git add *)", "Bash(git commit *)", "Bash(git config *)", "Bash(git remote *)", "Bash(gh api user*)", "Bash(gh repo view*)", "Bash(gh issue create *)", "Bash(go build*)", "Bash(go get *)", "Bash(go mod *)", "Bash(mktemp -u /tmp/gh-issue-body-*)", "Bash(rm -f /tmp/gh-issue-body-*)"]
  }
}
```

## See Also

- [Scaffold New Repo](../scaffold-new-repo/README.md): language-agnostic repo boilerplate (included automatically)
- [Write Go Code](../write-go-code/README.md): Go style guide for writing code in the new project
- [All plugins](../../../../README.md)
