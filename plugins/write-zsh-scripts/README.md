# Write Zsh Scripts

Zsh style conventions for creating and editing zsh scripts, configurations, and completions.

**Type:** Skill
**Trigger:** `/write-zsh-scripts` (also activates automatically)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Provides zsh coding conventions covering script structure, strict mode, quoting, parameter expansion, arrays, glob qualifiers, and the completion system. Activates automatically when creating, editing, or reviewing zsh scripts and configurations, ensuring consistent style across all zsh files.

Includes two reference guides:

- **ZSH.md**: comprehensive scripting conventions
- **completions.md**: completion function conventions drawn from the upstream zsh completion-style-guide

## Usage

```text
/write-zsh-scripts
```

The skill also activates automatically when Claude Code detects zsh script work.

## Examples

- Creating a new `.zsh` plugin file: the style guide activates automatically
- Writing a completion function (`_my-command`): activates automatically
- Editing `.zshrc` or `.zshenv`: activates automatically
- "/write-zsh-scripts": loads the full style guide explicitly

## See Also

- [Write Bash Scripts](../write-bash-scripts/README.md): Bash style conventions
- [Lint and Fix](../lint-and-fix/README.md): run linters and formatters across the project
- [All plugins](../../README.md)
