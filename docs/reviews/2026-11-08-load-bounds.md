# Notification and bugs-gather load bounds

The candidate moves notification fixture observations after owned detached
completion, advances grace ticks after backend readiness, and drains every
bugs-gather prefix reader. Production timing and hook files remain unchanged.
All validation is pending unless a checked receipt below states otherwise.

## Mechanisms and scope

The original backend fixture starts `jq` before logging delivery. The production
notifier gives that process two real seconds, so load can consume its opportunity
to log. Independent three-second log polls, six-second process-name polls and a
0.2-second absence sleep add scheduler-dependent observations. The private test
copy now loads a fixture clock before its entry point and joins recorded children
on exit. The backend declaration is renamed in the private copy; production functions and assets on disk remain unchanged.

The startup barrier holds a backend until the injected clock releases it. A
restored real grace clock cannot release that barrier. No synthetic CPU load is
needed. Unavoidable readiness uses a 120-second liveness bound; Python subprocess calls and individual lifecycle waits use 180-second timeouts.
Registration, completion and cleanup have separate budgets. These are containment
limits, not timing contract assertions.

`head` closes a bugs-gather pipeline before its subject finishes reporting errors.
A draining `sed` prefix reader preserves the subject's status. The synthetic regression writer continues past pipe capacity and receives SIGPIPE with an early reader, without relying on a scheduling delay. Help, cache, warning and usage
siblings are included.

Prior art: `launch-sleep-stub` already synchronizes a timeout tick to a fixture
marker, `watch-changes-stub` already records fake cadence, and `capture_child`
already retains child diagnostics. The candidate extends fixture control rather
than adding a production clock setting or changing the notifier's grace period.

## Whole-tree audit

[The site inventory](2026-11-08-load-bounds-timing-audit.json) records source lines,
hashes and dispositions from the entire test tree, including data-only matches.
The companion prefix-reader inventory also records unchanged early consumers across the test tree and distinguishes already captured subject output from live producers. Those potential producer-status races remain explicitly unproved outside bugs-gather.
It records existing rollout watcher polls, watcher lifetime checks, attention-log
scheduling assumptions, process cleanup observations and checked-runner timing
contracts. Those sites remain unchanged and are not claimed load-proof. The
restart evidence for this branch covers the notification fixtures and draining
readers; it does not lift another workstream's stop.

## Contract-only plant judges

Assertions in `NotificationLoadTests` observe specified subprocess exits, output
and the helper contract that prerequisite errors remain errors. File reads, regex inventory construction, temporary files, process
launch and timeout are prerequisites and raise ordinary exceptions. A missing or ambiguous snapshot subject raises `RuntimeError`.
Reader commands are extracted from those stable subjects, independently of
`head` or `sed` option spelling. No `setUp` assertion or
traceback filtering turns a prerequisite error into plant credit. The preflight
copies declared inputs, sources the loaded Bash libraries, parses the Python
judge, checks executed fixtures for prohibited instrumentation and runs the
unchanged judge before the plant gate. Missing or malformed backend observations use exit 2,
which the Python judge classifies as an ERROR. The observer records a missing
termination request as a complete negative observation, cleans up and reaps the
owned child, and leaves the delivery contract to reject that observation.
Captured compatibility rows are required
before the final gate.

## Claim-to-check map

| Claim                                                 | Contract                                                                 | Plant                                              |
| ----------------------------------------------------- | ------------------------------------------------------------------------ | -------------------------------------------------- |
| Delayed startup cannot consume grace                  | `test_blocked_startup`, `test_reported_deliveries_after_blocked_startup` | `real-grace-clock`                                 |
| Default and leading-zero fallback use two ticks       | `test_grace_ticks`                                                       | `short-grace`                                      |
| Grace expiry preserves the delivered banner           | `test_grace_ticks`                                                       | `term-banner`                                      |
| Detached failures retain their cause                  | `test_join_retains_failure`                                              | `lost-detached-status`                             |
| Backend shutdown is observed before reporting success | `test_grace_ticks`                                                       | `missing-backend-stop`                             |
| Prerequisite failure cannot become plant credit       | `test_prerequisite_error`, `test_join_retains_prerequisite_error`        | `prerequisite-verdict`, `lost-prerequisite-status` |
| A changed notifier entry point is refused             | `test_entrypoint_guard`                                                  | `entrypoint-guard`                                 |
| Explicit fixture failures print diagnostics           | `test_failure_diagnostic`                                                | `silent-fixture-failure`                           |
| Absence follows completed dispatch                    | `test_no_alert_after_dispatch`                                           | `visible-dispatch`                                 |
| Each prefix reader drains its writer                  | `test_draining_snapshot_readers`                                         | Each `early-reader` variant                        |

## Local review

Structural Nit round reviewed frozen `6187577c`, with anti-patterns and all four
read-only cleanup aspects. Execution receipt:
`/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/structural-1/gate/receipt.json`.
The editing `simplify` aspect was excluded. This snapshot had Important findings;
it is not a clean review of the current candidate.

| Finding                                                     | Reviewer label | Severity and impact                                                   | Take or record                                                             | Review again                              |
| ----------------------------------------------------------- | -------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------- | ----------------------------------------- |
| Backend stop was no longer observed                         | important      | Important: a no-op termination could still report successful shutdown | Take: observer records signal and reaped backend status; no-op plant       | Yes: fixture behavior changed             |
| Reader inventory omitted `head -n N`                        | important      | Important: an equivalent early reader silently lost its test          | Take: identify sites by subject; plant both option forms at every site     | Yes: detector behavior changed            |
| Forwarding wait alias duplicated immediate count assertions | suggestion     | Nit: name implied synchronization that no longer occurred             | Take: call the count predicate directly                                    | No additional round for this cleanup      |
| Writer issued one syscall per row                           | suggestion     | Nit: unnecessary fixture I/O under load                               | Take: bounded batches retain row order, partial-write handling and SIGPIPE | No additional round for test-only cleanup |

Cleanup simplification and altitude reported the same alias mechanism, counted as one finding. No reviewer Important label was downgraded. The completed structural continuation is recorded below.

Historical structural execution verification: exit 0 against the immutable frozen snapshot; receipt above. Current candidate validation remains pending.

## Structural Important round 1

Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/structural-2/gate/receipt.json`.
The frozen review was `885886d6`; anti-patterns reported no findings, all four
cleanup reviewers completed, and the scope comparison found no lasting changes.
End state: **clean at Important**.

| Finding                                             | Reviewer label | Severity and impact                                          | Take or record                                                                                                          | Review again                                |
| --------------------------------------------------- | -------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| Reset scenarios reread the same completed log count | suggestion     | Nit: repeated I/O and duplicated assertion                   | Take: retain the predicate and remove the inline repetition                                                             | No: same completed observation and contract |
| Observer computes the private stop predicate        | suggestion     | Nit: proposed separation of observation and assertion policy | Record below threshold: moving the predicate changes the private protocol; current complete-result contract is explicit | No                                          |

The former cleanup removed a misleading wait abstraction; the inline reread is a
different redundant observation. No Important or Critical class recurred.
The self-audit compiles the synthetic Python writer before launch, with a malformed-input contract and a parser-removal plant. This preserves
ERROR classification for fixture compilation failures without traceback filters.
Runtime checks and focused review of the resulting candidate remain pending.

## Focused Nit round: lifecycle recurrence stop

Frozen review: `61e98553`. Execution receipt:
`/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/focused-1/gate/receipt.json`.
Code, errors, tests, comments and types completed on the same snapshot. No
remaining review aspect was omitted. This is not a clean review.

| Finding                                                  | Reviewer label                  | Severity and impact                                                                 | Take or record                                                | Review again                      |
| -------------------------------------------------------- | ------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------- | --------------------------------- |
| Readiness failure bypasses owned backend cleanup         | important, from code and errors | Important: errexit can leave a held fixture backend running after its wrapper exits | Take pending the conductor's lifecycle class call             | Yes: failure behavior changes     |
| Function copy uses `eval`                                | important                       | Important: violates the repository's Important No eval rule                         | Take pending a checked declaration rename in the private copy | Yes: fixture construction changes |
| Clock diagnostics disappear through detached redirection | suggestion                      | Nit: the explicit cause is missing from the branch's own failure path               | Take with the lifecycle fix, using owned diagnostic capture   | Yes: diagnostic output changes    |
| Comment orders publication before reaping                | suggestion                      | Nit: implementation reaps before publishing                                         | Take after restart                                            | No                                |
| Pipe explanation ambiguously names the SIGPIPE recipient | suggestion                      | Nit: the writer receives SIGPIPE                                                    | Take after restart                                            | No                                |
| Ledger still calls a completed round next                | suggestion                      | Nit: contradictory current status                                                   | Take after restart                                            | No                                |

The lifecycle finding recurs after the structural loop fixed normal-return
backend shutdown observation. The mechanism is backend ownership not finalized
on every exit, including errors during readiness and observation. Source changes paused until TOOLING approved the structural class
and its audit. The proposed audit covers every ownership, completion, signal,
reaping, diagnostic and private-copy construction site in the diff and every
touched file, with a plant at each changed behavioral site and every prose claim
mapped to a contract or plant. The No eval finding is accepted without downgrade.

**End state: stopped: recurring defect.** Focused Important round 1 follows the
approved corrective work; counts do not reset. Trims, baseline Semgrep, final
lint/discovery/version checks, tidy, push, ready PR and CI remain unrun. The
already-started development run against an immutable candidate may finish; its
result cannot close this stop or certify the next candidate.

## Approved lifecycle correction

TOOLING approved “backend ownership not finalized on every exit” in mailbox
message `fe76520d`, recorded at `2026-11-08T12:53:36Z`. Restart covers the full
class audit, private-copy declaration rename, diagnostic capture and comment
corrections. Focused Important round 1 is next; the prior Nit round counts.

The fixture records the first backend PID and installs an owner EXIT finalizer.
Success, readiness failure, observation failure, HUP and TERM cancellation, and
cancellation deferred until PID registration all pass through owned cleanup and
reaping. Publication follows cleanup and reports separate requested-signal,
observed-exit and cleanup-exit fields. Cleanup cannot convert an observation of
an unexpectedly running backend into successful production shutdown. An original
error or cancellation status survives a later publication error. Per-invocation
readiness paths avoid reuse between dispatches. An owned diagnostic descriptor
captures detached errors; the joining parent replays them on failure.

The private copy requires exactly one literal backend declaration before a
literal rename. No function body is evaluated. Production hook entries and
hook-invoked scripts have no changes. The existing asynchronous Bash SIGINT
behavior is retained; cancellation contracts use HUP and TERM. Local controls
in `evidence/bash-async-int.txt` and `evidence/bash-async-int-prefork.txt` are
unverified observations, not checked-suite claims.

[The lifecycle inventory](2026-11-08-load-bounds-lifecycle-audit.json) records every
touched file and the ownership, wait, cancellation, cleanup and diagnostic sites
searched within it. Runtime validation of this correction remains pending.

| Claim                                                             | Contract                                                  | Plant                                                                       |
| ----------------------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------- |
| Every registered backend is stopped and reaped on readiness error | `test_readiness_error_cleanup`                            | `owner-finalizer-disabled`, `owner-cleanup-disabled`, `owner-reap-disabled` |
| Publication failure follows cleanup                               | `test_observation_error_cleanup`                          | `owner-cleanup-disabled`                                                    |
| HUP and TERM retain status and finalize ownership                 | `test_cancellation_cleanup`                               | `hup-status`, `term-status`, `owner-finalizer-disabled`                     |
| Cancellation before registration is retained and propagated       | `test_deferred_cancellation_cleanup`                      | `deferred-signal-forgotten`, `pending-signal-not-propagated`                |
| Publication error preserves cancellation status                   | `test_cancellation_status_survives_observation_error`     | `owner-status-overwritten`                                                  |
| Detached causes reach the caller                                  | `test_readiness_error_cleanup`                            | `diagnostic-replay-disabled`                                                |
| Backend failure retains exit and cause                            | `test_backend_error_diagnostic`                           | `backend-status-hidden`                                                     |
| Private declaration rename is exact and guarded                   | `test_copy_declaration`, `test_backend_declaration_guard` | `declaration-rename`, `declaration-guard`                                   |
| Writer compilation is a prerequisite                              | `test_writer_prerequisite`                                | `writer-prerequisite`                                                       |

The former below-threshold protocol suggestion is taken within this approved
correction: publication supplies raw observations and the grace scenario judges
the expected signal and statuses. Both TERM and INT banner mutations are plants.

## Focused Important round 1: diagnostic recurrence stop

Frozen snapshot: `de28a47c`. Checked execution receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/focused-2/gate/receipt.json`. Verification against the frozen current tree completed in the same strict call as this record. Scope comparison records no lasting changes.

| Finding                                                                       | Reviewer label | Our severity                                                                                               | Take or record                                                       | Review again                     |
| ----------------------------------------------------------------------------- | -------------- | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------- |
| Uncited: Process-probe redirection discards backend-registration diagnostics. | important      | Important: registration failures lose their cause, and deferred cancellation loses its asserted diagnostic | Take after conductor class approval                                  | Yes: diagnostic behavior changes |
| Uncited: Publication failures are tested only after another failure.          | suggestion     | Nit: missing boundary coverage for the new publication-error branch                                        | Take with a positive-completion publication-error contract and plant | No: tests only                   |
| Uncited: The documented 180-second bound applies to individual waits.         | suggestion     | Nit: the containment description overstates an invocation-wide limit                                       | Take: describe separate wait budgets                                 | No: prose only                   |

The errors finding repeats the earlier diagnostic-loss mechanism: fixture errors inherit intentionally suppressed probe streams. The first correction restored detached diagnostics, but a caller-level `kill -0` redirection still suppresses registration errors and deferred-cancellation messages before they enter the owned log. Source changes stop pending TOOLING’s class decision. The proposed structural audit covers every fixture emission beneath a redirected call, including registration I/O, deferred signals, readiness probes and the diagnostic replay boundary, with contract-only plants and a claim map. No Important label is downgraded.

**End state: stopped: recurring defect.** Focused Important round 2 follows approved corrective work; counts persist. The queued development gate remains on its immutable snapshot and cannot certify a correction. Trims, baseline Semgrep, final lint/discovery/version checks, tidy, push, ready PR and CI remain unrun.

## Approved diagnostic class correction

TOOLING approved “fixture diagnostics emitted under suppressed probe streams”
in native message `12b20a5e`, recorded at `2026-11-08T14:00:30Z`.
The audit covers every diagnostic emission beneath redirected fixture calls.
Backend registration writes install descriptor 7 as stderr before opening the
registration path, retaining open failures. Registration and deferred-signal
messages write directly to that descriptor. The owner EXIT trap also restores
that stream before cleanup; expected builtin existence-probe diagnostics alone
remain suppressed. Parent join diagnostics retain ordinary stderr because that
parent does not execute beneath a redirected probe and its standalone contract
has no diagnostic file. Source changes remain confined to test fixtures.

| Claim                                                                   | Contract                               | Plant                                |
| ----------------------------------------------------------------------- | -------------------------------------- | ------------------------------------ |
| Registration failures retain operation and destination                  | `test_registration_error_diagnostic`   | `registration-diagnostic-suppressed` |
| Deferred cancellation retains its explicit cause                        | `test_deferred_cancellation_cleanup`   | `deferred-diagnostic-suppressed`     |
| Publication failure after success returns prerequisite status and cause | `test_publication_error_after_success` | `publication-status-hidden`          |

The diagnostic site ledger is included in the lifecycle audit. The source audit
is complete; runtime evidence and focused Important round 2 remain pending.

## Focused Important round 2

Frozen snapshot: `2014c525`. Checked execution receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/focused-3/gate/receipt.json`, verified against the frozen current tree in the same strict call as this record. All selected aspects completed with no findings; launched prompts match the preflight-pinned inputs. The scope comparison records no lasting changes.

**End state: clean at Important.** The loop ends because this round took no finding at its threshold. Runtime validation, plant compatibility registration, trims, baseline Semgrep, final lint/discovery/version checks, tidy, push, ready PR and CI remain pending.

## Development gate setup failure

Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/development-3/receipt.json`. The captured cause is `ValueError: timeout must be in (0, 3600]`. Every declared check and the plant action is recorded as not-run with no exit status. No runtime or plant result earns credit. The outer lock released. New queue entries stop pending a validated manifest/closure/dry-run check and TOOLING’s restart decision. The automatic failure post exceeded the mailbox limit; its compact replacement links to the retained receipt.

## Final prose and comment trim

Read-only Codex proposals reviewed frozen `5058333f`, using `gpt-6.1-sol`, low effort and window `872000`. Execution receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/trims-1/gate/receipt.json`, verified against the frozen current tree before these edits in the same strict call. Both replies completed with the required file classification and proposal table. All proposals were taken; none were declined. The stale backend comment described polling removed by the fixture clock and join. Other edits shorten the plan and ledger while retaining the review history and contract map. No runtime behavior changed. Formatting and fixture validation follow; tests remain subject to the queued development receipt and final discovery.

## Baseline Semgrep setup stop

Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/semgrep-1/gate/receipt.json`. The captured process exit is `2`; the CLI refused automatic configuration with metrics disabled before scanning. No scan output or clean verdict exists. The required baseline scan remains unrun. TOOLING receives the explicit-ruleset proposal; another baseline invocation waits for that decision.

## Baseline Semgrep completed

TOOLING approved `p/ci` with metrics disabled in native message `80121af5`. The first explicit-ruleset invocation omitted test paths through default target filtering and receives no clean coverage claim. The corrected invocation supplies the changed test files explicitly alongside the tree, preserving `--baseline-commit` at the actual merge base in the same disposable shared clone. No override flag or full-scan substitute was used.

Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/semgrep-3/gate/receipt.json`, verified against frozen `fe55f5be` before this record in the same strict call. Scan findings: `0`; scan errors: `0`; skipped rules: `0`. The checked coverage assertion requires every changed test source and Scrut document in the scan target set.

## Version check

The repository `check-versions` skill compared this branch with `origin/main` at `5406e6c6ac46bbfd8cedf278760f607c1a32152a`. Changed plugins: `[]`; version bumps required: `False`. The repository plugin validator accepted current versions, mirrors and marketplace coverage. Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/versions-1/gate/receipt.json`, verified against the current tree before this record in the same strict call. No manifest or catalog edits were needed.

## Trim verification and final preflight

The source trim was committed before its parser comparison finished. That comparison now verifies an unchanged shell AST and the exact single eligible comment deletion, alongside unchanged remaining runtime sources. Shellcheck, shfmt and fixture-environment checks also completed. Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/trim-validation-1/gate/receipt.json`, verified against the current tree before this record. Runtime tests remain pending.

The installed make executes the outer recipe containing `$(MAKE)` even under `--dry-run`, demonstrated by an owned fixture without a heavy wrapper. The final preflight therefore verifies the canonical wrapper and dependency headers, then dry-runs its inner goals. Runtime discovery retains exactly `["make", "test-all"]`; preflight uses `["make", "--dry-run", "lint", "validate", "test-scrut"]`. Invalid timeout and missing-script copies remain refused. Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/final-prequeue-mechanism/gate/receipt.json`, verified against the current tree before this record in the same strict call. No heavy queue entry was created by the proof.

## Lifecycle prerequisite correction

Development receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/development-4/receipt.json`. The gate failed on the unchanged lifecycle preflight; the plant action did not run. The failure was an ERROR, not a contract FAIL, and earns no plant credit.

The direct diagnostic captured a registration path with a doubled separator from
`TMPDIR`. Decoding through `Path.parent` normalized that spelling, while the
owner command retained the reported path. The backend happened to match through
its normalized icon argument; the owner did not. Registration decoding now uses
`os.path.dirname` to retain the reported spelling. All existing backend, owner
and cleanup comparisons consume that same key; unknown identities still raise
`RuntimeError` before any signal.

The class audit checks the raw registration producer, decoder, all process-key
consumers, and other path normalization in the touched files. `ROOT.resolve()`
locates test code and does not construct process identity. Absolute-path
validation does not replace the recorded string. The registration-only contract
covers canonical, repeated-separator and dot-component spellings. Its separate
manifest restores the old normalization and expects a named contract FAIL;
prerequisite failures in lifecycle controls cannot earn that plant credit.

| Claim                                                | Contract                          | Plant                          |
| ---------------------------------------------------- | --------------------------------- | ------------------------------ |
| Registration retains the reported directory spelling | `test_registration_path_spelling` | `normalized-registration-path` |

TOOLING authorized the direct diagnostic outside the lock in native message
`a7fa3907`. The corrected diagnostic completed, but receives no merge credit.
No additional review round is required under the tests-only rule: the edit
changes a test prerequisite and adds its contract, without changing fixture or
production behavior. Existing review counts and end states remain recorded.
The complete development gate must run again through fresh pre-queue checks.

## Merge claim closure preparation

The final admission checker now validates a preceding run for every plant render and refuses missing or orphan renders. Each final plant run and render is a separate checked-gate check, with explicit supporting inputs and `tree`, and outputs remain outside the checkout. The discovery check retains exactly `["make", "test-all"]`; its dry-run uses the verified inner goals. Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/751-load-bounds/evidence/merge-closure-proof/gate/receipt.json`, verified against the current tree before this record in the same strict call. This proves the planned closure only; fresh checks at the final head and actual runtime evidence remain required.

## Finalizer output contract and independent plant declarations

Development-5 failed. Captured gate action exit: `1`. The failing plant `owner-finalizer-disabled` has status `setup-error`: ValueError: plant did not satisfy its named assertion verdict. Its baseline exit is `0`, red exit `1`, and restored exit `0`. These captures are from the failed receipt, not a pass claim. The red contains `ERROR: test_readiness_error_cleanup`: missing finalizer output raised a prerequisite exception before the named assertion. No plant or aggregate merge credit is claimed.

TOOLING native message `73e99c42` authorized correcting the test gap and running every plant independently in one further development gate. The finalizer observation is subject output: its absence or wrong bytes now fails the exact output contract. Registration, process identity and filesystem errors other than absent output still raise non-assertion errors. The existing `owner-finalizer-disabled` plant guards this contract.

The pinned runner stops within a manifest after its first failed variant and provides no variant-selection flag. Task manifests therefore declare one variant each, retaining each existing selector and verdict. The development action invokes the trusted runner for every declaration, records every process status and fails after collecting the complete set. Runner, fixture and production behavior are unchanged. Test-only edits add no review round; prior counts and end states remain in force. Every new manifest still requires captured compatibility registration and final run/render checks before publication.

## Reduced validation scope

TOOLING native messages `53b82e37` and `f79bd14c` replace the every-site plant
requirement. The retained plants cover the mechanisms below. Other audited sites
remain checked by reading and by their ordinary regression tests, without a
per-site plant claim. Removed manifests and support files are recorded in the
owned evidence file `scope-cut-removed-files.json`; they were created on this
branch. No compatibility rows from removed manifests are registered.

| Mechanism                             | Kept plant                           | Contract                             |
| ------------------------------------- | ------------------------------------ | ------------------------------------ |
| Slowed-stub restart and clock barrier | `real-grace-clock`                   | `test_blocked_startup`               |
| Draining prefix reader                | `early-reader-1`                     | `test_draining_snapshot_readers`     |
| Bugs-gather no-state pipe             | `early-reader-5`                     | `test_draining_snapshot_readers`     |
| Backend ownership on exit             | `owner-finalizer-disabled`           | `test_readiness_error_cleanup`       |
| Diagnostics under redirected probes   | `registration-diagnostic-suppressed` | `test_registration_error_diagnostic` |

Development-6 was withdrawn while queued before runtime, using its recorded
owner-checked process group. It produced no runtime receipt, result or review
round. Heavy admission is closed until TOOLING confirms the dark-mode switch
passed. The remaining publication gate is discovery and these retained plants,
with captured compatibility rows and tree-bound run/render receipts. The cut
changes test data only and adds no review round.
