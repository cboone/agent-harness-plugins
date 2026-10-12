# Write Zsh Scripts

Zsh scripting conventions for syntax, types, expansion, scope and completions, with a workflow for syntax checks, compilation, linting and formatting.

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

## Additional workflows

For "check zsh", "lint zsh" or "validate zsh", follow `skills/write-zsh-scripts/references/lint/workflow.md`. It uses zsh syntax and compilation checks, ShellCheck, shfmt and optional checkbashisms and shellharden, reporting unsupported or unavailable checks.
