# Trim Comments

Trim and rewrite code comments so each leads with what the code does and the minimum why, cutting trivia, jargon, restatement, and details that go stale.

**Type:** Skill
**Trigger:** `/trim-comments` (also activates automatically)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

The skill reviews the comments in a branch's changed code and keeps, rewrites, or deletes each one. It flags ticketless `TODO` comments and comments whose meaning is unclear instead of changing them. Its standard is one line by default: what the code is doing, then the minimum reason. A comment earns its place when someone would otherwise "fix" the code and break it, when deliberate code looks wrong, when an external constraint drives it, or when the reader cannot follow the code without a pointer to another file.

It cuts runtime trivia, consequence chains, arguments for decisions the code has already made, mock comments that narrate the author's thinking, CSS comments that restate the declaration, and jargon. It also favors wording that stays true: no line numbers, no counts or "currently", and comments anchored to the code beside them rather than to code elsewhere.

The scope defaults to comments in or directly above code changed since the base branch, including uncommitted and untracked files. The skill edits only comments, leaves directive and pragma comments alone, checks the edited files with the project's formatter and linter in check mode, its type checker, and its tests, and reports a before-and-after table. It then commits its edits locally and never pushes. A file that already held your uncommitted work stays uncommitted, so the commit never carries your own changes. It does not commit on a detached HEAD, on the default branch, or when it cannot tell which branch is the default. The report also covers which checks ran, the commit's branch, and any change a commit hook made.

## Requirements

- A Git repository. The [GitHub CLI](https://cli.github.com/) finds the base branch when it is available; otherwise the skill falls back to the remote's `HEAD` ref, and asks when neither is set.
- `realpath`, which the path safety filter uses. It ships with GNU coreutils and with macOS 13 and later.

## Usage

```text
/trim-comments
/trim-comments src/send.ts src/send.test.ts
/trim-comments --dry-run
/trim-comments --no-commit
```

`--dry-run` reports the proposed changes without editing or committing. `--no-commit` edits and verifies but leaves the edits uncommitted. Paths put every comment in those files in scope, changed or not, after the same safety filter drops generated files, prose documents, secret-bearing paths, symlinks, and anything that is not a regular file.

## Recommended Permissions

This skill runs read-only Git and GitHub CLI commands to find its scope. To allow them without prompts, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh repo view *)", "Bash(git symbolic-ref *)", "Bash(git merge-base *)", "Bash(git diff *)", "Bash(git --no-pager diff *)", "Bash(git ls-files *)", "Bash(git status *)", "Bash(git hash-object *)", "Bash(git log -1 *)", "Bash(git rev-parse *)", "Bash(git remote)", "Bash(git config --get *)", "Bash(realpath *)", "Bash(test -f *)", "Bash(grep -Iq *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. The skill also runs the project's own linter, formatter, type checker, and tests, which depend on the project. Its commit is a `git commit` limited to the edited files; leave it to prompt unless you want the commit to run unattended.

## Examples

- "trim the comments on this branch": reviews every changed file
- "this comment is too long": rewrites that comment
- "trim the code comments before I open the PR": a pass over the diff, committed locally

## Credits

Originally written by Erica Oh ([@acire](https://github.com/acire)) and used with her permission. This version adapts it to this repository's conventions and adds the rules on staying true.

## See Also

- [Review Branch](../review-branch/README.md): a broader review of the branch's changes
- [All plugins](../../README.md)
