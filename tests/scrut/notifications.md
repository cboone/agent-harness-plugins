# Notification delivery

## Parses under the system bash

On macOS, `/bin/bash` is bash 3.2, which `env bash` finds without Homebrew on `PATH`. A parse failure exits 2, which Claude Code treats as blocking. CI runs on Linux, where `/bin/bash` is bash 5, so this case guards bash 3.2 only in local macOS runs.

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

## Click routing

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" click
Click targets captured session, window and pane on originating server
```
