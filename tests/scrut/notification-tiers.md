# Session tiers

Each scenario runs the notifier under `/bin/bash` with a fixture `XDG_CONFIG_HOME`. The tmux stub reports the pane as window `w 42-fix-parser` of session `atlas` unless a scenario names another. Policy scenarios print each event's alert as `title | subtitle | sound`, or `none`; rule scenarios print `notify explain`.

## Worker posts only permission, plan and elicitation prompts

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-worker
stop: none
permission: Worker: Approve Bash? | atlas: w 42-fix-parser | Funk
plan: Worker: Plan ready for review | atlas: w 42-fix-parser | Tink
question: none
elicit: Worker: Question | atlas: w 42-fix-parser | Tink
codex-question: none
codex-stop: none
```

## Lead posts completions, permission and elicitation prompts

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-lead
stop: Done | atlas: conductor | Glass
permission: Approve Bash? | atlas: conductor | Funk
plan: none
question: none
elicit: Question | atlas: conductor | Tink
codex-question: none
codex-stop: Done | atlas: conductor | Glass
```

## Top posts what a lead posts

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-top
stop: Done | hub: coordinator | Glass
permission: Approve Bash? | hub: coordinator | Funk
plan: none
question: none
elicit: Question | hub: coordinator | Tink
codex-question: none
codex-stop: Done | hub: coordinator | Glass
```

## Session matching no rule stays untiered

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-unmatched
stop: Done | sample-repo · Sample task | Glass
permission: Approve Bash? | sample-repo · Sample task | Funk
plan: Plan ready for review | sample-repo · Sample task | Tink
question: Question | sample-repo · Sample task | Tink
elicit: Question | sample-repo · Sample task | Tink
codex-question: Question | sample-repo · Sample task | Tink
codex-stop: Done | sample-repo · Sample task | Glass
```

## Lead completion after an answered question or plan

A question the person rejected counts as answered; one that failed before reaching them does not, and neither does an ordinary tool call. Only Claude Code turns are checked: a Codex lead posts its Done even after an answered question.

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-answered
question: none
plan: none
rejected: none
failed: Done | atlas: conductor | Glass
tool: Done | atlas: conductor | Glass
earlier: Done | atlas: conductor | Glass
codex: Done | atlas: conductor | Glass
untiered: Done | sample-repo · Sample task | Glass
```

## First valid rule wins

Comments, blank lines, unknown tiers and fields, and a pattern bash cannot compile are skipped.

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-rules-order
tier: worker
rule: line 6: worker window ^w[ ]
name: none
subtitle: atlas: w 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
```

## Rule on the tmux session

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-rules-session
tier: lead
rule: line 1: lead session ^atlas$
name: none
subtitle: atlas: w 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
```

## Rule on the tmux server

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-rules-server
tier: lead
rule: line 1: lead server ^notify-test-server$
name: none
subtitle: atlas: w 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
```

## Rule on the session name, skipping a quoted record

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-rules-name
tier: lead
rule: line 1: lead name ^[[:upper:]]+$
name: MONITOR
subtitle: atlas: w 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
```

## Session name from a rename

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-rules-custom-title
tier: lead
rule: line 1: lead name ^Sample[ ]
name: Sample Title
subtitle: atlas: w 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
```

## The newest session name wins

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-rules-renamed
tier: lead
rule: line 2: lead name ^Renamed
name: Renamed Title
subtitle: atlas: w 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
```

## Rule on the working directory, then the project directory

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-rules-dir
tier: top
rule: line 1: top dir /sample-repo$
name: none
subtitle: atlas: w 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
tier: worker
rule: line 2: worker dir /worktrees/
name: none
subtitle: atlas: w 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
```

## NOTIFY_TIER wins, and an invalid value is ignored

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-rules-env
tier: top
rule: NOTIFY_TIER=top
name: none
subtitle: atlas: w 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
tier: worker
rule: line 1: worker window ^w[ ]
name: none
subtitle: atlas: w 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
```

## No matching rule, and no session name to match

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-rules-none
tier: untiered
rule: none
name: none
subtitle: sample-repo · Sample task
sounds: stop Glass, permission Funk, attention Tink
```

## No tiers file

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-rules-missing
tier: untiered
rule: none
name: none
subtitle: sample-repo · Sample task
sounds: stop Glass, permission Funk, attention Tink
```

## Multibyte window names in the default and C locales

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-rules-multibyte
tier: worker
rule: line 2: worker window ^λ[ ]
name: none
subtitle: atlas: λ 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
tier: worker
rule: line 2: worker window ^λ[ ]
name: none
subtitle: atlas: λ 42-fix-parser
sounds: stop Glass, permission Funk, attention Tink
```

## Icon-font window names give way to the session name

A window named only with a private-use glyph shows the session name, or the tmux session alone without one. Text next to a glyph stays.

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-place-glyph
tier: lead
rule: NOTIFY_TIER=lead
name: MONITOR
subtitle: hub: MONITOR
sounds: stop Glass, permission Funk, attention Tink
tier: lead
rule: NOTIFY_TIER=lead
name: none
subtitle: hub
sounds: stop Glass, permission Funk, attention Tink
tier: lead
rule: NOTIFY_TIER=lead
name: none
subtitle: hub: BOARDS
sounds: stop Glass, permission Funk, attention Tink
```

## Tiered session outside tmux keeps the repository subtitle

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-place-outside-tmux
tier: lead
rule: NOTIFY_TIER=lead
name: none
subtitle: sample-repo · sample-branch
sounds: stop Glass, permission Funk, attention Tink
```

## Name rules apply in the hooks

The hook reads the session name from its payload's transcript, for the rule and for a window named only with a glyph.

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-name-hook
permission: Approve Bash? | atlas: ATLAS | Funk
question: none
```

## Explain finds the session's transcript

From `$CLAUDE_CODE_SESSION_ID`, under `$CLAUDE_CONFIG_DIR`, then under `~/.claude`.

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-explain-lookup
tier: lead
name: LOOKUP
tier: lead
name: LOOKUP
```

## Explain fails on what it cannot read

Unlike the hooks, `explain` fails for a missing transcript, a session ID that is invalid or has a missing or unreadable transcript, and a tiers file that is not a readable file.

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-explain-errors
Error: cannot read the transcript <dir>/missing.jsonl.
exit 1
Error: found no readable transcript for session absent in <dir>/claude/projects.
exit 1
Error: found no readable transcript for session unreadable in <dir>/claude/projects.
exit 1
Error: found no readable transcript for session bad/../id in <dir>/claude/projects.
exit 1
Error: cannot read the tiers file <dir>/config/agent-harness-notify/tiers; check that it is a readable file.
exit 1
```

## POSIX checksum vectors for the place and the repository

```scrut
$ for name in 'atlas: w 42-fix-parser' sample-repo; do printf '%s' "${name}" | cksum; done
1698745888 22
419135404 11
```

## Tier sound subsets and their fallbacks

A worker takes its subset, hashed on the place. A lead without a subset takes the plain set, hashed on the place, and an untiered session hashes the repository. A subset missing index 0 falls back for that role, and without a sound set every tier keeps the built-in sounds.

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-sounds
sounds: stop Chord-worker-stop-3, permission Chord-worker-permission-3, attention Chord-worker-attention-3
sounds: stop Chord-stop-3, permission Chord-permission-3, attention Chord-attention-3
sounds: stop Chord-stop-4, permission Chord-permission-4, attention Chord-attention-4
sounds: stop Chord-stop-3, permission Chord-worker-permission-3, attention Chord-worker-attention-3
sounds: stop Glass, permission Funk, attention Tink
```
