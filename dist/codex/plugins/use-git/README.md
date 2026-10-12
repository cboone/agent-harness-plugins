# Use Git

Apply git and GitHub CLI conventions for tmpfile bodies, signed commits and safe pushes, and create GitHub issues.

**Type:** Skill
**Trigger:** `/use-git` (also activates automatically)

## Installation

See the [marketplace install instructions](../../../../README.md#install).

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
- [Create Issue](#create-issue): create GitHub issues using the tmpfile pattern
- [All plugins](../../../../README.md)

## Create issue

Create GitHub issues using tmpfiles to avoid permission prompts from large multiline Bash arguments.

**Type:** Skill
**Trigger:** `/use-git:create-issue`

### Installation

See the [marketplace install instructions](../../../../README.md#install).

### What It Does

Creates GitHub issues by writing the issue body to a temporary file and passing it to `gh issue create --body-file`, instead of inlining large multiline strings as Bash arguments. This keeps the Bash command short and avoids triggering Claude Code's permission prompts for complex commands. Supports labels, assignees, milestones, projects, and cross-repo issue creation.

### Requirements

- [`gh`](https://cli.github.com/). Install via Homebrew: `brew install gh`

### Usage

Ask Claude to create an issue:

- "Create an issue for adding dark mode support"
- "File a bug report about the login timeout"
- "Open an issue on org/repo for the missing docs"

Or invoke directly with `/use-git:create-issue`.

### Recommended Permissions

This skill runs GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue create *)", "Bash(gh issue view *)", "Bash(gh issue edit *)", "Bash(mktemp -u \"${TMPDIR:-/tmp}/gh-issue-body-*\")", "Bash(rm -f *gh-issue-body-*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

### See Also

- [Address Issue in Worktree](../workmux/README.md#workmuxstart-issue): Start working on an existing issue in an isolated worktree
- [Suggest Next Issue](../suggest-next-issue/README.md): Get recommendations on which issue to tackle next
- [All plugins](../../../../README.md)
