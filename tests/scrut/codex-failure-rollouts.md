# Codex rollout failure banners

Committed capture-only alert and terminal stubs prevent live delivery. JSONL samples combine measured Codex 0.165.0 rollout shapes with protocol-derived and malformed-metadata cases. Identities and message bodies use sample values.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

## Terminal errors

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" error
Error: MONITOR | atlas: w sample | API limit reached | Funk
```

## Typed policy refusals omit provider text

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" refusals
Refusal: MONITOR | atlas: w sample | Turn ended in a safeguard refusal. | Funk
Refusal: MONITOR | atlas: w sample | Turn ended in a safeguard refusal. | Funk
Refusal: MONITOR | atlas: w sample | Turn ended in a safeguard refusal. | Funk
```

## Recovery, approval waits, untyped errors and subagents

An ordinary error is a positive control for delivery after the excluded inputs.

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" quiet
Error: MONITOR | atlas: w sample | API limit reached | Funk
```

## Duplicate terminal records and restarts

Two distinct turns post twice; replaying both turns posts nothing further.

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" duplicates
Error: MONITOR | atlas: w sample | API limit reached | Funk
Error: MONITOR | atlas: w sample | API limit reached | Funk
```

## Same turn ID in distinct threads

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" threads
Error: MONITOR | atlas: w sample | API limit reached | Funk
Error: MONITOR | atlas: w sample | API limit reached | Funk
```

## Concurrent readers of the same thread

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" concurrent
Error: MONITOR | atlas: w sample | API limit reached | Funk
```

## Identity and missing-message fallbacks

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" identity
Error: thread-fallback | atlas: w fallback | Turn ended in an API error. | Funk
```

## Every notification tier

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" tiers
Error: MONITOR
Error: MONITOR
Error: MONITOR
Worker: Error: MONITOR
```

## Outside tmux with no supplied name

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" outside
Error: thread-sample | sample-repo · unknown | API limit reached | Funk
```

## Appended partial records and supervisor shutdown

Follow mode reaches EOF before appending a partial record, posts after its newline, skips historical failure records, and exits when the recorded supervisor stops.

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" follow
Error: MONITOR | atlas: w sample | Appended error | Funk
```

## Mismatched thread identity

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" mismatch 2>&1
watch-codex-failures: rollout does not match --thread-id
[1]
```

## Failure appended during startup catch-up

A byte-count stub pauses after capturing the initial size. The fixture appends a failure before the watcher reads history, including multibyte text, then releases it.

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" startup
Error: MONITOR | atlas: w sample | Appended during startup | Funk
```

## Supplied directory overrides inherited Claude context

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" directory
Error: MONITOR | atlas: w sample | API limit reached | Funk
```

## Final record appended between EOF and owner-exit observation

The capture-only owner check pauses after the initial EOF. The fixture appends the terminal record and stops the supervisor before allowing that check to finish.

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" shutdown
Error: MONITOR | atlas: w sample | Appended at shutdown | Funk
```

## Byte accounting preserves Unicode tier matching

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" unicode
Worker: Error: ÉQUIPE | atlas: w sample | API limit reached | Funk
```

## Missing backend does not consume a delivery claim

The unavailable-backend fixture shadows only the lookup. A repaired lookup delivers the same terminal record through the committed alerter stub.

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" preflight
watch-codex-failures: alerter is not executable (thread thread-sample, turn turn-sample)
Error: MONITOR | atlas: w sample | API limit reached | Funk
```

## Detached backend startup failures remain observable

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" backend-failure
fixture backend startup failed
notify: alerter exited with status 127 (thread thread-sample, turn turn-sample)
attempts: 1
```

## Failed dispatch followed by a restart

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" dispatch-failure
first status: 23
attempts: 1
```

## Error-object metadata boundaries

Missing, null and empty metadata remain silent. A typed object-valued connection error provides the positive control.

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" metadata
Error: MONITOR | atlas: w sample | Connection failed | Funk
```
