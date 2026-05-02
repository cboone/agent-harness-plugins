# Setup Linters

Detect project languages, recommend appropriate linters and formatters, install them, and generate config files.

**Type:** Skill
**Trigger:** `/setup-linters`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Setup Linters** from the available plugins.

## What It Does

Scans the project for language markers and file types, checks for existing linter configurations, and recommends the appropriate tool stack. Supports JavaScript/TypeScript, Go, Python, Rust, Ruby, Shell, Zig, Zsh, Swift, Lean, and cross-language tools. Installs selected tools, generates sensible default configs, creates an `.editorconfig`, and optionally wires up a CI lint workflow.

For Lean projects, no external linter is installed: `lake lint` is wired up via `lintDriver = "batteries/runLinter"` in `lakefile.toml`, plus a `lean-lint` Makefile target and a `lake lint` step in `leanprover/lean-action`-driven CI.

For paper-backed Lean/math projects, the Pandoc-academic preset generates coordinated markdownlint and cspell configs for Pandoc citations, LaTeX math, raw `{=latex}` blocks, YAML frontmatter titles, dense academic tables, and transcription trees treated as excluded reference material.

## Usage

```text
/setup-linters
```

## Examples

- "set up linters": detects project type and walks through setup
- "add linting to this project": same behavior
- "set up eslint and prettier": same behavior
- "add ruff to this project": same behavior

## See Also

- [Lint and Fix](../lint-and-fix/README.md): run existing linters with auto-fix (use after setup)
- [Setup Secret Scanning](../setup-secret-scanning/README.md): set up secret scanning
- [All plugins](../../../../README.md)
