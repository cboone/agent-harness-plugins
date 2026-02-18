# Write Go Code

Go code style guide based on Google Go Style Guide, Effective Go, and Code Review Comments.

**Type:** Skill
**Trigger:** `/write-go-code` (also activates automatically)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Write Go Code** from the available plugins.

## What It Does

Provides Go style conventions covering naming, error handling, concurrency, testing, data types, functions, interfaces, and code organization. Activates automatically when writing, reviewing, or refactoring Go code, so you get consistent style guidance without needing to invoke it manually.

Organized into an essential checklist for quick reviews and comprehensive references by topic.

## Usage

```text
/write-go-code
```

The skill also activates automatically when Claude Code detects Go code work.

## Examples

- Writing a new Go function: the style guide activates automatically
- "review this Go code for style": activates automatically
- "/write-go-code": loads the full style guide explicitly

## See Also

- [Lint and Fix](../lint-and-fix/README.md): run linters and formatters across the project
- [Scaffold Go CLI](../scaffold-go-cli/README.md): scaffold a full Go CLI project
- [All plugins](../../README.md)
