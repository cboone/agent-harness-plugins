# Use Git

Git and GitHub CLI conventions for Claude Code.

**Type:** Skill
**Trigger:** `/use-git` (also activates automatically)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Provides conventions for running git and `gh` CLI commands in Claude Code. Covers when to use tmpfiles vs HEREDOCs for passing content, GPG signing, safe push practices, secret file exclusion, parallel tool call patterns, and clean diff output formatting.

The core problem: long string arguments in Bash commands (PR bodies, issue bodies, review replies) trigger Claude Code permission prompts. This skill standardizes the patterns that avoid those prompts while keeping operations safe.

Organized into a quick-reference decision table and deep-dive references by topic.

## Usage

```text
/use-git
```

The skill also activates automatically when Claude Code detects work involving git or `gh` CLI commands.

## Examples

- Running `gh pr create` with a long body: the skill directs to the tmpfile + `--body-file` pattern
- Committing changes: the skill provides the HEREDOC pattern with GPG signing
- Pushing code: the skill covers upstream fallback and safe push practices
- "review this git workflow": checks against the safety rules and conventions

## See Also

- [Commit](../commit/README.md): smart git commits with conventional commit messages
- [PR](../pr/README.md): commit, push, and create a pull request in one step
- [Create Issue](../create-issue/README.md): create GitHub issues using the tmpfile pattern
- [All plugins](../../README.md)
