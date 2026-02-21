# Create Tmux Plugin

Scaffold a tmux plugin with TPM Redux conventions: entry point, helpers, scripts directory, and README with install sections.

**Type:** Skill
**Trigger:** `/create-tmux-plugin`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Create Tmux Plugin** from the available plugins.

## What It Does

Generates the full boilerplate for a new tmux plugin: the entry point (`plugin-name.tmux`), a shared helpers script with `get_tmux_option`, the main script stub, LICENSE, and a README with TPM Redux, manual, and legacy TPM install sections. Supports optional scrut test skeleton, GitHub Actions CI, and workmux layout generation.

## Usage

```text
/create-tmux-plugin
```

The skill prompts for plugin name, description, and configurable options during setup.

## Examples

- "create tmux plugin": starts the interactive scaffolding process
- "new tmux plugin": same behavior
- "scaffold tmux plugin": same behavior

## See Also

- [Scaffold New Repo](../scaffold-new-repo/README.md): language-agnostic repo boilerplate
- [Write Shell Scripts](../write-shell-scripts/README.md): Bash style guide for writing plugin scripts
- [All plugins](../../README.md)
