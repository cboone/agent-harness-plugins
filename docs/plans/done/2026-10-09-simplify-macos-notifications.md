# Simplify macOS notifications

## Context

A review of the last 100 delivered `notify` banners, read from Notification Center's database, found them hard to scan:

- 36 of 54 completion bodies opened with synthetic user turns: skill expansions (`Base directory for this skill: …`), `<task-notification>` blocks and cross-session messages.
- Every `AskUserQuestion` produced a Question banner and a redundant Permission banner whose body was just `AskUserQuestion`.
- Subtitles repeated the worktree slug, carried Claude Code's `✳` pane-title glyph or a shell's `user@host:path` title, and pushed the tool name off the end.
- Replies leaked Markdown, permission paths lost their file names to truncation, multiple questions ran together, and a Codex reply arrived as raw JSON.

Chris assessed live sample banners built from real session data and approved the format below.

## Format

- **Title** names the action: `Done`, `Approve <Tool>?`, `Question` or `N questions`, `Plan ready for review`, and `Error` for OpenCode. The per-harness icon identifies the agent.
- **Subtitle** is `<repo> · <task>`. The repo comes from git's shared repository directory, so worktrees report their repository rather than their folder. The task is the tmux pane title with leading status glyphs removed. Generic titles (shell names, harness names, `user@host:path`, the repo or folder name) fall back to the branch suffix.
- **Completion body** summarizes the final reply alone: Markdown, code blocks, tables and status lines (`▸ …` or several `·` fields) are removed, whole sentences are kept in order within 140 characters, and a sentence that no longer fits fills at least 40 remaining characters with a word-boundary cut. A JSON reply with a string `summary` uses that summary.
- **Permission body** shows paths relative to the repository root, truncated from the left so the file name survives. Bash previews drop a leading `cd` into the working directory.
- **Questions** show the first question and `(+N more)`.
- `AskUserQuestion` permission prompts post nothing. `ExitPlanMode` permission prompts post `Plan ready for review` with the plan's first heading.
- Compacting banners are removed from Claude Code, Codex and OpenCode.

## Steps

1. Rewrite the formatting in `plugins/notify/scripts/notify` and remove the `PreCompact` hooks from both manifests.
1. Port the same format to `plugins/notify/opencode/index.ts` and remove its compacting hook.
1. Update `tests/fixtures/check-notifications` and `tests/scrut/notifications.md` to cover the new titles, subtitles, summaries, permission handling and question counts.
1. Update the plugin README and the root README's Codex and OpenCode notes, bump `notify` to `2.4.0`, run `make build` and `make test-all`.
