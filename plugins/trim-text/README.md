# Trim Text

Trim and rewrite prose, such as PR and issue bodies and agent instructions, so it leads with what the reader needs and the minimum why, without changing what it says.

**Type:** Skill
**Trigger:** `/trim-text` (also activates automatically)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

The skill applies the standard from [Trim Comments](../trim-comments/README.md) to prose. It leads with what the reader needs, then the minimum reason, and cuts the rest: narration of how the author got there, consequence chains, arguments for decisions already made, hedges, jargon, and facts that go stale. Text stays when a reader would otherwise do the wrong thing, when something deliberate looks wrong, or when an external constraint drives it.

A profile adapts the standard to each kind of text:

- **PR and issue bodies:** the change or the problem first, without restating the title, the diff, or the commit list.
- **Agent instructions:** `AGENTS.md`, `CLAUDE.md`, skills, Copilot instructions, and global instructions. This profile leans toward keeping and flagging, because a rule that looks redundant is often the fix for a past failure.
- **None:** pasted text and commit message bodies get the shared standard alone.

Every rewrite must preserve meaning: no claim added, no "must" turned into "should", and every condition and exception kept. Deleted text is limited to what the standard cuts, and the only statement of a requirement is never deleted. A claim that is no longer true is corrected when you run the skill directly, and flagged when another skill calls it. The skill leaves quotations, legal text, generated files, code blocks, and text that must match another file verbatim alone.

How it applies the result depends on the input:

- **Files:** edits them in place, checks them with the project's linters in check mode, and commits the edits locally when on a working branch, never pushing. It does not commit on the base branch or a detached HEAD, and files that already held your uncommitted work stay uncommitted.
- **A PR or issue:** shows a before-and-after diff and asks before updating the body on GitHub.
- **Pasted text or a draft from another skill:** returns the rewrite and edits nothing.

[PR](../pr/README.md) and [Commit](../commit/README.md) use it on their drafts when it is installed.

## Requirements

- The [GitHub CLI](https://cli.github.com/), authenticated, for PR and issue bodies and current-branch PR lookups.
- A Git repository for file paths.
- `realpath` (GNU coreutils, or macOS 13 and later) for a symlinked instruction file such as `CLAUDE.md`.
- Optional: [`codex`](https://github.com/openai/codex), authenticated, for the Codex dry run on file paths.

## Usage

```text
/trim-text
/trim-text branch
/trim-text branch --base origin/main
/trim-text pr 42
/trim-text issue 17 --dry-run
/trim-text AGENTS.md plugins/*/skills/*/SKILL.md
/trim-text docs/guide.md --profile none --no-commit
```

With no scope argument, a branch with an open PR offers its body (default) or branch changes. Without a PR, default to branch changes. Explicit `branch` selects changed prose, including local on-disk changes and untracked prose, compared with the merge base of the PR's remote base or the verified remote default branch. `--base` selects another comparison ref. Unchanged prose and unrelated edits remain untouched; the existing file verification and commit rules apply.

`--profile` overrides the profile detected from the input. `--dry-run` reports the proposed changes without editing anything. `--no-commit` edits files and verifies them but leaves the edits uncommitted. `--no-codex` classifies file paths in the current session instead of through Codex.

When `codex` is installed, file paths first get a read-only Codex dry run (`codex exec` in a read-only sandbox with `approval_policy="never"` and `web_search="disabled"`, on `gpt-6.1-sol` at `low` effort with an 872k context window, set on the run so your own Codex settings never apply). The sandbox holds only with `approval_policy="never"`, which stops the run from asking to leave it. `web_search="disabled"` turns off Codex's web search, which the sandbox does not cover. Together they keep the run's commands and web search offline. MCP servers in your Codex configuration are not covered and can still reach the network. Started from a Codex session, the skill runs in that session instead, on that session's model and settings. The current session checks each proposal against the standard and the profile before applying it. PR and issue bodies and pasted text always run in the current session. When Codex is missing or its run fails a completion check, the session classifies the text itself and says so.

## Recommended Permissions

This skill reads PR and issue bodies with the GitHub CLI and runs read-only Git commands to find and check its files. To allow them without prompts, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh pr view *)", "Bash(gh pr list *)", "Bash(gh issue view *)", "Bash(gh repo view *)", "Bash(git ls-files *)", "Bash(git rev-parse *)", "Bash(git status *)", "Bash(git --no-pager diff *)", "Bash(git show *)", "Bash(git cat-file -e *)", "Bash(git symbolic-ref *)", "Bash(git config --get *)", "Bash(git remote)", "Bash(git branch --show-current)", "Bash(git hash-object *)", "Bash(git log -1 *)", "Bash(grep -Iq *)", "Bash(mktemp -u *)", "Bash(rm -f */gh-body-*)", "Bash(realpath *)", "Bash(command -v codex)", "Bash(mktemp -d*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. The multi-line `codex exec` command matches no simple permission rule. Approve its prompt or pass `--no-codex`. The skill also runs the project's own linters and formatters in check mode, which depend on the project. Its writes prompt by default: `gh pr edit` and `gh issue edit` update a body after you approve the diff in the conversation, and `git commit` commits edited files. To let them run without a second prompt, also allow:

```json
{
  "permissions": {
    "allow": ["Bash(gh pr edit *)", "Bash(gh issue edit *)", "Bash(git commit *)"]
  }
}
```

## Examples

- "tighten the PR body": trims the open PR's description, after you approve the diff
- "this instruction is too long": rewrites the instruction in place
- "trim this" with pasted text: returns a shorter version

## See Also

- [Trim Comments](../trim-comments/README.md): the same standard for code comments
- [Write Markdown](../write-markdown/README.md): Markdown formatting conventions
- [All plugins](../../README.md)
