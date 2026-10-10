# Notification delivery

## Completion sound

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" completion
Done
sample-repo · Sample task
Completed sample
Glass
```

## Duplicate completion

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" claude-completion
Done
sample-repo · Sample task
Completed sample
Glass
```

## Reply summary without Markdown or status lines

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" summary
Done
sample-repo · Sample task
PR #12: ready. Checks pass on abc123, see the run. Copilot left one note.
Glass
```

## Long reply cut at a word boundary

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" long-summary
Done
sample-repo · Sample task
The overnight throttle is on. I stopped the previous watcher and started a new one that checks the pull request hourly until the morning,…
Glass
```

## JSON reply summary

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" json-summary
Done
sample-repo · Sample task
Do not implement this plan unchanged.
Glass
```

## Shell default pane title

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" generic-title
Done
sample-repo · sample-branch
Completed sample
Glass
```

## Worktree names its repository

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" worktree
Done
sample-repo · worktree-branch
Completed sample
Glass
```

## Claude question

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" claude-question
Question
sample-repo · Sample task
Choose a branch?
Tink
```

## Several questions

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" questions
3 questions
sample-repo · Sample task
Choose a branch? (+2 more)
Tink
```

## Permission path keeps its file name

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-write
Approve Write?
sample-repo · Sample task
…-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-long-name-.md
Funk
```

## Permission command without its working-directory cd

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" permission-bash
Approve Bash?
sample-repo · Sample task
make test
Funk
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
```

## Question content

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" question
Question
sample-repo · Sample task
Choose a branch?
Tink
```

## Serialized question input

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" question-string
Question
sample-repo · Sample task
Choose a branch?
Tink
```

## Click routing

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" click
Click targets captured session, window and pane on originating server
```
