# Trim Comments

Trim and rewrite code comments so each leads with what the code does and the minimum why, cutting trivia, jargon, restatement, and details that go stale.

**Type:** Skill
**Trigger:** `/trim-comments` (also activates automatically)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

The skill reviews the comments in a branch's changed code and keeps, rewrites, or deletes each one. Its standard is one line by default: what the code is doing, then the minimum reason. A comment earns its place when someone would otherwise "fix" the code and break it, when deliberate code looks wrong, when an external constraint drives it, or when the reader cannot follow the code without a pointer to another file.

It cuts runtime trivia, consequence chains, arguments for decisions the code has already made, mock comments that narrate the author's thinking, CSS comments that restate the declaration, and jargon. It also favors wording that stays true: no line numbers, no counts or "currently", and descriptions of the code beside the comment rather than code elsewhere.

The scope defaults to files changed since the base branch, including uncommitted and untracked files. The skill edits only comments, runs the project's formatter, linter, type checker, and tests, and reports a before-and-after table. It leaves the edits uncommitted for review.

## Usage

```text
/trim-comments
/trim-comments src/send.ts src/send.test.ts
/trim-comments --dry-run
```

`--dry-run` reports the proposed changes without editing. Paths limit the scope to those files.

## Requirements

- A Git repository. The [GitHub CLI](https://cli.github.com/) finds the base branch when it is available; otherwise the skill falls back to `origin/HEAD`.

## Examples

- "trim the comments on this branch": reviews every changed file
- "this comment is too long": rewrites the comments in the files you name
- "clean up the comments before I open the PR": a pass over the diff, left uncommitted for review

## Credits

Originally written by Erica Oh ([@acire](https://github.com/acire)) and used with her permission. This version adapts it to this repository's conventions and adds the rules on staying true.

## See Also

- [Commit](../commit/README.md): commits the trimmed comments once you have reviewed them
- [Review Branch](../review-branch/README.md): a broader review of the branch's changes
- [All plugins](../../README.md)
