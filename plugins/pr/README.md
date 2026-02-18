# PR

Commit all changes, push to remote, and create a GitHub pull request in one automated step.

**Type:** Skill
**Trigger:** `/pr`
**Requires:** [`gh`](https://cli.github.com/)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **PR** from the available plugins.

## What It Does

Stages everything, generates a conventional commit message from the diff, pushes the branch, and opens a PR with an auto-generated title and summary. Detects connected GitHub issues from branch names and commit messages, and adds closing references automatically. Handles branches with no upstream, skips the commit step when the working tree is clean, and detects when a PR already exists.

## Usage

```text
/pr
```

No options. The skill makes opinionated decisions at every step with no prompts.

## Examples

- "pr": commits, pushes, and creates a pull request
- "create a pr": same behavior
- "push and create pr": same behavior

## See Also

- [Commit](../commit/README.md): commit without creating a PR
- [Review Branch](../review-branch/README.md): summarize branch work before opening a PR
- [All plugins](../../README.md)
