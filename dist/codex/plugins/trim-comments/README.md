# Trim Comments

Trim and rewrite code comments so each leads with what the code does and the minimum why, cutting trivia, jargon, restatement, and details that go stale.

**Type:** Skill
**Trigger:** `/trim-comments` (also activates automatically)

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

This compatibility alias invokes [Trim Text](../trim-text/README.md) with its `code-comments` profile. Install both plugins. The shared standard and workflow live in `trim-text`; the comment profile retains test scaffolding, stylesheet rules, protected comments, ticketless TODO flags, worked examples and comment-only verification.

Existing calls and options keep their scope. No arguments means comments within or directly above changed code since the remote default branch's merge base, including staged, unstaged and untracked files. Explicit paths mean all comments in those files; a single named comment means only that comment. Prose files and symlinks are skipped. The target edits only comments, checks that code stays unchanged, runs relevant checks, commits only eligible files and never pushes. Report-only Codex proposals retain the read-only sandbox. If `trim-text` is unavailable, the alias reports that without editing files.

For one mixed prose/comment pass, use `trim-text branch`. `trim-text branch --profile code-comments` is the equivalent of the alias's no-argument scope.

## Requirements

- A Git repository. The [GitHub CLI](https://cli.github.com/) finds the base branch when it is available; otherwise the skill falls back to the remote's `HEAD` ref, and asks when neither is set.
- `realpath`, which the path safety filter uses. It ships with GNU coreutils and with macOS 13 and later.
- Optional: [`codex`](https://github.com/openai/codex), authenticated, for the Codex dry run.

## Usage

```text
/trim-comments
/trim-comments src/send.ts src/send.test.ts
/trim-comments --dry-run
/trim-comments --no-commit
```

`--dry-run` reports the proposed changes without editing or committing. `--no-commit` edits and verifies but leaves the edits uncommitted. `--no-codex` classifies the comments in the current session instead of through Codex. Paths put every comment in those files in scope, changed or not, after the same safety filter drops generated files, prose documents, secret-bearing paths, symlinks, and anything that is not a regular file.

When `codex` is installed, a path or default scope first gets a read-only Codex dry run (`codex exec` in a read-only sandbox with `approval_policy="never"` and `web_search="disabled"`, on `gpt-6.1-sol` at `low` effort with an 872k context window, set on the run so your own Codex settings never apply). The sandbox holds only with `approval_policy="never"`, which stops the run from asking to leave it. `web_search="disabled"` turns off Codex's web search, which the sandbox does not cover. Together they keep the run's commands and web search offline. MCP servers in your Codex configuration are not covered and can still reach the network. Started from a Codex session, the skill runs in that session instead, on that session's model and settings. The current session checks each proposal against the standard before applying it. When Codex is missing or its run fails a completion check, the session classifies the comments itself and says so.

## Recommended Permissions

This skill runs read-only Git and GitHub CLI commands to find its scope. To allow them without prompts, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh repo view *)", "Bash(git symbolic-ref *)", "Bash(git merge-base *)", "Bash(git diff *)", "Bash(git --no-pager diff *)", "Bash(git ls-files *)", "Bash(git status *)", "Bash(git hash-object *)", "Bash(git log -1 *)", "Bash(git rev-parse *)", "Bash(git remote)", "Bash(git config --get *)", "Bash(realpath *)", "Bash(test -f *)", "Bash(grep -Iq *)", "Bash(command -v codex)", "Bash(mktemp -d*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. The multi-line `codex exec` command matches no simple permission rule. Approve its prompt or pass `--no-codex`. The skill also runs the project's own linter, formatter, type checker, and tests, which depend on the project. Its commit is a `git commit` limited to the edited files. It prompts by default; to let it run unattended, also allow `Bash(git commit *)`.

## Examples

- "trim the comments on this branch": reviews every changed file
- "this comment is too long": rewrites that comment
- "trim the code comments before I open the PR": a pass over the diff, committed locally

## Credits

Originally written by Erica Oh ([@acire](https://github.com/acire)) and used with her permission. This version adapts it to this repository's conventions and adds the rules on staying true.

## See Also

- [Review Branch](../review-branch/README.md): a broader review of the branch's changes
- [All plugins](../../../../README.md)
