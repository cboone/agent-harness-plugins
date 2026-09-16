# Notification delivery

## Completion sound

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" completion
Codex · Done
Completed sample
Glass
```

## Duplicate completion

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" claude-completion
Claude Code · Done
Completed sample
Glass
```

## Claude question

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" claude-question
Claude Code · Question
Choose a branch?
Tink
```

## Claude compaction

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" claude-compact
Claude Code · Compacting
Auto-compacting context
Pop
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
Codex · Done
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
Codex · Done
Completed sample
Glass
```

## Question content

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" question
Codex · Question
Choose a branch?
Tink
```

## Serialized question input

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" question-string
Codex · Question
Choose a branch?
Tink
```

## Automatic compaction

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" compact
Codex · Compacting
Auto-compacting context
Pop
```

## Click routing

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" click
Click targets captured session, window and pane on originating server
```
