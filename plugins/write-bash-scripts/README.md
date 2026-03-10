# Write Bash Scripts

Bash style conventions for creating and editing Bash scripts.

**Type:** Skill
**Trigger:** `/write-bash-scripts` (also activates automatically)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Write Bash Scripts** from the available plugins.

## What It Does

Provides Bash coding conventions covering script structure, strict mode, quoting, error handling, and portability. Activates automatically when creating, editing, or reviewing Bash scripts, ensuring consistent style across all Bash files.

Includes a reference guide covering all conventions with ShellCheck rule identifiers.

## Usage

```text
/write-bash-scripts
```

The skill also activates automatically when Claude Code detects Bash script work.

## Examples

- Creating a new Bash script: the style guide activates automatically
- Editing a script in `bin/`: activates automatically
- "/write-bash-scripts": loads the full style guide explicitly

## See Also

- [Lint and Fix](../lint-and-fix/README.md): run ShellCheck and shfmt across the project
- [All plugins](../../README.md)
