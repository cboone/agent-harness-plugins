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

A committed boundary fixture holds each reader at the exclusive file claim. The parent releases both through separate FIFOs after receiving both ready messages. Child-output capture waits for detached delivery diagnostics to close before the alert count is checked.

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" concurrent
Error: MONITOR | atlas: w sample | API limit reached | Funk
```

## Existing directory claims remain valid

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" legacy-claim
legacy directory preserved; no replay
```

## Missing concurrent reader reports arrivals and statuses

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" concurrent-timeout
readiness timeout identifies missing reader; both statuses retained
```

## Claim errors retain filesystem diagnostics

```scrut
$ LC_ALL=C "${CHECK_CODEX_FAILURES_BIN}" claim-error
claim failed with filesystem diagnostic; no delivery
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

The fixture waits for follower-start readiness before appending a partial record. Follow mode posts after its newline, skips historical failure records and exits when the recorded owner stops.

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

## Follow-mode launch budgets

The committed jq and sleep wrappers count watcher launches after startup on a
sample rollout with a long history. The idle window excludes fixture-controller
launches. Both wrappers must resolve to the committed test doubles.

```scrut
$ "${MEASURE_CODEX_FAILURE_LAUNCHES_BIN}" check
startup_jq=1 idle_seconds=3 idle_jq=0 idle_sleep=* idle_tail=0 (glob)
launch budgets satisfied
```

## Failure appended after startup byte capture

A byte-count stub pauses after capturing the initial size. The captured history contains multibyte text. Before following starts, the fixture appends a failure, then releases the stub.

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" startup
Error: MONITOR | atlas: w sample | Appended during startup | Funk
```

## Supplied directory overrides inherited Claude context

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" directory
Error: MONITOR | atlas: w sample | API limit reached | Funk
```

## Record appended during owner shutdown

The fixture pauses the supervisor's first follow-mode owner check, appends a terminal record and stops the owner before releasing the check. Delivery may occur through the follower or the final drain.

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

## Every supported failure shape while following

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" follow-shapes
Error: MONITOR | atlas: w sample | API limit reached | Funk
Error: MONITOR | atlas: w sample | Connection failed | Funk
Error: MONITOR | atlas: w sample | Turn ended in an API error. | Funk
Refusal: MONITOR | atlas: w sample | Turn ended in a safeguard refusal. | Funk
Refusal: MONITOR | atlas: w sample | Turn ended in a safeguard refusal. | Funk
Refusal: MONITOR | atlas: w sample | Turn ended in a safeguard refusal. | Funk
```

## Record already partial at startup

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" partial-startup
Error: MONITOR | atlas: w sample | Partial startup error | Funk
```

## Relative rollout with a different notification directory

```scrut
$ "${MEASURE_CODEX_FAILURE_LAUNCHES_BIN}" relative
startup_jq=1 idle_seconds=3 idle_jq=0 idle_sleep=* idle_tail=0 (glob)
launch budgets satisfied
relative rollout modes satisfied
```

## Extracted fields retain command-substitution compatibility

Trailing newlines in identity, turn and message fields are removed as before. Replaying the same normalized turn does not deliver twice.

```scrut
$ "${CHECK_CODEX_FAILURES_BIN}" escaped-fields
Error: MONITOR | atlas: w sample | API limit reached | Funk
```

## Supervisor timer failure propagates

```scrut
$ "${MEASURE_CODEX_FAILURE_LAUNCHES_BIN}" supervisor-error
timer failure propagated; watcher stopped with owner and rollout context
```

## Cancellation closes owned readers and timers

The fixture records the follower, supervisor and timer PIDs, plus the private
reader directory, before stopping the watcher while its owner remains running.
A real extended timer makes descendant cleanup observable.

```scrut
$ "${MEASURE_CODEX_FAILURE_LAUNCHES_BIN}" cancel
watcher canceled; descendants stopped; reader directory removed; owner preserved
```

## Failure appended after follower closure

A delivered prefix confirms consumption of multibyte data. After the persistent follower closes, the static reader pauses before opening the rollout. Only then does the fixture append the final terminal failure.

```scrut
$ "${MEASURE_CODEX_FAILURE_LAUNCHES_BIN}" final-drain
final drain delivered exactly the prefix and the post-follower failure
```

## Follower failure while the owner remains running

The fixture releases a failing follower after recording the running children and
reader directory. The owner remains running while the watcher reports failure.

```scrut
$ "${MEASURE_CODEX_FAILURE_LAUNCHES_BIN}" follower-error
follower-error propagated; diagnostics retained; descendants and reader directory removed
```

## Final-reader failure after owner shutdown

A controlled static-reader marker follows follower closure. The fixture records
that reader's PID before releasing its failure.

```scrut
$ "${MEASURE_CODEX_FAILURE_LAUNCHES_BIN}" final-reader-error
final-reader-error propagated; diagnostics retained; descendants and reader directory removed
```

## Exact TSV message round trip

```scrut
$ "${MEASURE_CODEX_FAILURE_LAUNCHES_BIN}" escaped-message
TSV message preserves literal backslashes and internal whitespace as exact JSON
```

## Startup history offset and partial-record retention

The history case waits for a newly appended failure before stopping the owner,
then checks that no historical banner was delivered. The partial case starts
with an unfinished record and appends only its suffix and newline.

```scrut
$ "${MEASURE_CODEX_FAILURE_LAUNCHES_BIN}" follow
startup history is skipped before appended delivery
```

```scrut
$ "${MEASURE_CODEX_FAILURE_LAUNCHES_BIN}" partial-startup
partial startup record is retained until newline
```
