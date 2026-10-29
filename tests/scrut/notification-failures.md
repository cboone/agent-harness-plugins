# Terminal failure banners

Notification delivery and terminal inspection use committed fixture stubs. Each fixture refuses to run unless those commands resolve to its stubs. No live banners are posted.

## Errors, refusals and approval waits in every tier

Failure banners post even while the pane is visible and the turn began in the background. Structured refusal metadata cannot turn another error type into a refusal. Approval waits retain approval titles.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-failures
background: none
untiered-error: Error: MONITOR | atlas: w 42-fix-parser | Funk
untiered-refusal: Refusal: MONITOR | atlas: w 42-fix-parser | Funk
untiered-approval: Needs approval | sample-repo · Sample task | Funk
top-error: Error: MONITOR | atlas: w 42-fix-parser | Funk
top-refusal: Refusal: MONITOR | atlas: w 42-fix-parser | Funk
top-approval: Needs approval | atlas: w 42-fix-parser | Funk
lead-error: Error: MONITOR | atlas: w 42-fix-parser | Funk
lead-refusal: Refusal: MONITOR | atlas: w 42-fix-parser | Funk
lead-approval: Needs approval | atlas: w 42-fix-parser | Funk
worker-error: Worker: Error: MONITOR | atlas: w 42-fix-parser | Funk
worker-refusal: Worker: Refusal: MONITOR | atlas: w 42-fix-parser | Funk
worker-approval: Worker: Needs approval | atlas: w 42-fix-parser | Funk
API limit reached
Approve sample operation
Turn ended in a safeguard refusal.
```

## Refusal boundaries and missing fields

A new prompt or ordinary reply clears stale refusal metadata. Delayed persistence still identifies a refusal. Missing messages use a fixed fallback and missing names use the session ID. Subagents remain silent.

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-failure-boundaries
system: Refusal: thread-42 | atlas: w 42-fix-parser | Funk
metadata: Refusal: thread-42 | atlas: w 42-fix-parser | Funk
local-output: Refusal: thread-42 | atlas: w 42-fix-parser | Funk
new-turn: Error: thread-42 | atlas: w 42-fix-parser | Funk
new-reply: Error: thread-42 | atlas: w 42-fix-parser | Funk
delayed: Refusal: thread-42 | atlas: w 42-fix-parser | Funk
missing: Error: thread-42 | atlas: w 42-fix-parser | Funk
subagent: none
Turn ended in a safeguard refusal.
Turn ended in an API error.
```

## Untiered failures keep repository sound selection

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-failure-sounds
failure: Error: sample | atlas: w 42-fix-parser | Chord-permission-4
approval: Needs approval | sample-repo · Sample task | Chord-permission-4
```
