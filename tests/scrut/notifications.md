# Notification delivery

## Parses under the system bash

On macOS, `/bin/bash` is bash 3.2, which `env bash` finds without Homebrew on `PATH`. A parse failure exits 2, which Claude Code treats as blocking. CI runs on Linux, where `/bin/bash` is bash 5, so this case guards bash 3.2 only in local macOS runs.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
$ /bin/bash -n "${NOTIFY_BIN}" && echo "Parses"
Parses
```

## Every manifest subcommand dispatches

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" manifests
Every manifest subcommand dispatches
```

## Completion sound

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" completion
Done
sample-repo · Sample task
Completed sample
Glass
codex.png
```

## Claude Code completion

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" claude-completion
Done
sample-repo · Sample task
Completed sample
Glass
claude-code.png
```

## Reply summary without Markdown or status lines

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" summary
Done
sample-repo · Sample task
PR #12: ready. Checks pass on abc123, see the run. Copilot left one note
Glass
claude-code.png
```

## Status lines when nothing else remains

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" status-only
Done
sample-repo · Sample task
572 · checks 20/20. waiting on review
Glass
codex.png
```

## Table without leading pipes is dropped

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" pipeless-table
Done
sample-repo · Sample task
Results: All good.
Glass
codex.png
```

## First code line when nothing else remains

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" code-only
Done
sample-repo · Sample task
make test
Glass
codex.png
```

## Unclosed fence read as prose

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" unclosed-fence
Done
sample-repo · Sample task
Here is the fix: make test
Glass
codex.png
```

## Long reply cut at a word boundary

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" long-summary
Done
sample-repo · Sample task
The overnight throttle is on. I stopped the previous watcher and started a new one that checks the pull request hourly until the morning,…
Glass
codex.png
```

## Sentence dropped when little room remains

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" short-room
Done
sample-repo · Sample task
word word word word word word word word word word word word word word word word word word word word word word ends here.
Glass
codex.png
```

## JSON reply summary

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" json-summary
Done
sample-repo · Sample task
Do not implement this plan unchanged.
Glass
codex.png
```

## Long JSON reply summarized from its field

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" long-json-summary
Done
sample-repo · Sample task
Short JSON summary.
Glass
codex.png
```

## Empty reply does not borrow other text

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" stop-empty
Done
sample-repo · Sample task
Task completed
Glass
claude-code.png
```

## Missing reply read from the current turn

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" stop-transcript
Done
sample-repo · Sample task
Current turn reply.
Glass
claude-code.png
```

## Tool-only turn does not borrow an earlier reply

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" stop-tool-only
Done
sample-repo · Sample task
Task completed
Glass
claude-code.png
```

## Shell default pane title

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" generic-title
Done
sample-repo · sample-branch
Completed sample
Glass
codex.png
```

## Worktree names its repository

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" worktree
Done
sample-repo · worktree-branch
Completed sample
Glass
codex.png
```

## Claude question

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" claude-question
Question
sample-repo · Sample task
Choose a branch?
Tink
claude-code.png
```

## Elicitation dialog

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" elicit
Question
sample-repo · Sample task
Sign in to the sample server
Tink
claude-code.png
```

## Several questions

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" questions
3 questions
sample-repo · Sample task
Choose a branch? (+2 more)
Tink
claude-code.png
```

## Long first question keeps its count

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" long-question
3 questions
sample-repo · Sample task
Which very very very very very very very very very very very very very very very very very very very very very very very very ver… (+2 more)
Tink
claude-code.png
```

## Unexpected question input

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" question-shape
Question
sample-repo · Sample task
Needs input
Tink
claude-code.png
```

## Permission path keeps its file name

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-write
Approve Write?
sample-repo · Sample task
…-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-.md
Funk
claude-code.png
```

## Permission path under a symlinked working directory

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-symlink
Approve Write?
sample-repo · Sample task
docs/a.md
Funk
claude-code.png
```

## Permission command without its working-directory cd

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-bash
Approve Bash?
sample-repo · Sample task
make test
Funk
claude-code.png
```

## MCP permission prompt

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-mcp
Approve create_issue?
sample-repo · Sample task
github MCP tool
Funk
claude-code.png
```

## Answered question does not hide a permission prompt

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-stale-question
Approve Bash?
sample-repo · Sample task
Claude needs your permission to use Bash
Funk
claude-code.png
```

## Parallel tool calls pick the prompted tool

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-parallel
Approve Bash?
sample-repo · Sample task
ls -la
Funk
claude-code.png
```

## Answered calls are not pending

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-answered
Approve Bash?
sample-repo · Sample task
make deploy
Funk
claude-code.png
```

## Interactive prompt picks the oldest pending call

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-interactive
Approve Bash?
sample-repo · Sample task
echo first
Funk
claude-code.png
```

## Prompt that names no tool call

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-sandbox
Needs approval
sample-repo · Sample task
A sandboxed command needs network access
Funk
claude-code.png
```

## Permission prompt without a matching tool call

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-fallback
Approve TodoWrite?
sample-repo · Sample task
Claude needs your permission to use TodoWrite
Funk
claude-code.png
```

## Question permission prompt

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-question
No alert
```

## Plan permission prompt

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" plan
Plan ready for review
sample-repo · Sample task
Add a sample skill
Tink
claude-code.png
```

## Plan approval message

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" plan-message
Plan ready for review
sample-repo · Sample task
Sample plan
Tink
claude-code.png
```

## Plan without a heading

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" plan-no-heading
Plan ready for review
sample-repo · Sample task
Rename the sample helper.
Tink
claude-code.png
```

## Slash-command turn does not borrow an earlier reply

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" stop-slash-command
Done
sample-repo · Sample task
Task completed
Glass
claude-code.png
```

## Status line marked only by separators

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" status-dots
Done
sample-repo · Sample task
Ready to merge.
Glass
codex.png
```

## Interactive prompt skips older question and plan calls

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-skip-interactive
Approve Bash?
sample-repo · Sample task
make test
Funk
claude-code.png
```

## Meta records do not end the turn

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-meta
Approve Bash?
sample-repo · Sample task
make test
Funk
claude-code.png
```

## MCP display name matched by tool name

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-mcp-display
Approve create_issue?
sample-repo · Sample task
github MCP tool
Funk
claude-code.png
```

## Plan approval before the plan is in the transcript

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" plan-pending
Plan ready for review
sample-repo · Sample task
Review the proposed plan
Tink
claude-code.png
```

## New Claude Code prompt

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" claude-reset
Next user prompt allows another completion
```

## Plan heading inside a code fence is skipped

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" plan-fenced
Plan ready for review
sample-repo · Sample task
Real heading
Tink
claude-code.png
```

## Empty plan

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" plan-empty
Plan ready for review
sample-repo · Sample task
Review the proposed plan
Tink
claude-code.png
```

## Repeated completion

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" duplicate
One completion alert per turn
```

## New user prompt

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" reset
Next user prompt allows another completion
```

## Separate sessions

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" groups
Separate sessions retain separate banners
```

## Visible originating pane

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" visible
No alert
```

## Visible pane when tmux names itself the terminal

tmux 3.2 and later set `TERM_PROGRAM=tmux` in every pane, so the terminal comes from `__CFBundleIdentifier`.

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-visible-tmux-bundle
No alert
```

## Visible pane with the terminal from the tmux server

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-visible-tmux-global
No alert
```

## Unknown terminal under tmux

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tmux-unknown-terminal
Done
sample-repo · Sample task
Completed sample
Glass
codex.png
```

## Active terminal with another pane visible

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" other-pane
Done
sample-repo · Sample task
Completed sample
Glass
codex.png
```

## Subagent completion

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" subagent
No alert
```

## Interactive Codex session completion

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" codex-cli
Done
sample-repo · Sample task
Completed sample
Glass
codex.png
```

## Codex exec completion

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-codex-exec
No alert
```

## Codex subagent completion

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-codex-subagent
No alert
```

## Codex exec resuming an interactive session

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-codex-exec-resume
No alert
```

## Codex exec through its alias

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-codex-exec-alias
No alert
```

## Codex exec after an option value with a space

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-codex-spaced-value
No alert
```

## Codex exec without a transcript

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-codex-exec-ephemeral
No alert
```

## Codex review

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-codex-review
No alert
```

## Interactive Codex with an option value that ends in a command

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" codex-spaced-value-terminal
Done
sample-repo · Sample task
Completed sample
Glass
codex.png
```

## Codex exec in a terminal

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-codex-exec-terminal
No alert
```

## Interactive Codex started with a prompt

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" codex-terminal-prompt
Done
sample-repo · Sample task
Completed sample
Glass
codex.png
```

## Interactive Codex resuming an exec session

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" codex-interactive-resume
Done
sample-repo · Sample task
Completed sample
Glass
codex.png
```

## Codex option value that looks like a command

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" codex-option-value
Done
sample-repo · Sample task
Completed sample
Glass
codex.png
```

## Turn started by the user

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" turn-human
Done
sample-repo · Sample task
Completed sample
Glass
claude-code.png
```

## Turn started by the user in an older transcript

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" turn-human-legacy
Done
sample-repo · Sample task
Completed sample
Glass
claude-code.png
```

## Turn without an origin

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" turn-untagged
Done
sample-repo · Sample task
Completed sample
Glass
claude-code.png
```

## Turn without a promptId after one with a promptId

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" turn-without-prompt-id
Done
sample-repo · Sample task
Completed sample
Glass
claude-code.png
```

## Turn started by a background task

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-turn-task
No alert
```

## Turn started by another session

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-turn-peer
No alert
```

## Turn started by a scheduled wake

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-turn-scheduled
No alert
```

## Turn started through the SDK

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-turn-sdk
No alert
```

## Turn started by a background task in an older transcript

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-turn-legacy
No alert
```

## Turn with only meta prompts

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-turn-meta
No alert
```

## Compaction summary in a meta turn

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-turn-compacted
No alert
```

## Background turn after the user's turn

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" quiet-turn-after-human
No alert
```

## Background window in the active terminal

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" other-window
Done
sample-repo · Sample task
Completed sample
Glass
codex.png
```

## Question content

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" question
Question
sample-repo · Sample task
Choose a branch?
Tink
codex.png
```

## Serialized question input

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" question-string
Question
sample-repo · Sample task
Choose a branch?
Tink
codex.png
```

## Alerter stops after the grace period

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" delivery
Alerter stops after the grace period without SIGTERM
```

## Leading-zero wait limit keeps the default

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" delivery-leading-zero
Alerter stops after the grace period without SIGTERM
```
