# Checked gate review ledger

The branch adds tree-bound check/action receipts and extracts the execution core.
Base: `ed2a0df956595873acf9476ea6f5000fabec9294` (`origin/main`). No activation,
hooks or global rule changes. TOOLING merges after the worker's ready PR.

## Structural loop

Round 1, Nit: standalone read-only Codex `gpt-6.1-sol`, high effort, 872000-token
window; anti-patterns and report-only simplify in parallel. Snapshot
`b1a09b2e377c335f8bc56b0a191b0fc16545d25e`; no lasting changes found.
Anti-patterns read all 16 canonical files. Its `complete: false` reports the
unstaged generated marketplace outside its committed range; that file is now
included in the commit. This round is not described as clean.

| Finding                         | Reviewer label | Severity and impact                                       | Take or record                                                                | Review again           |
| ------------------------------- | -------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------- | ---------------------- |
| Case-sensitive Bash detection   | important      | Important: a failed pipeline can authorize the action     | Take: resolve PATH/symlinks, normalize case and propagate strict Bash options | Yes: behavior changes  |
| Reader plants lost stat import  | important      | Important: partition 3 cannot reach its named red verdict | Take: make the injected stat lookup self-contained                            | No: test plumbing only |
| Conditional core-patch assembly | suggestion     | Nit: duplicated selection couples assignment and use      | Take: initialize the optional patch and branch on its data                    | No: test plumbing only |

Additional local corrections preserve the previously valid input filename
`core` by nesting module fingerprints under `runner`, check timeout bounds
before floating conversion, and parse each shipped AST independently.
Round 2, Important 1: both reviewers exited 0; scope unchanged and complete.
Anti-patterns found the recurring interpreter-classification defect (`tcsh`),
a reader exemption that accepted script-local duplicates, and refusal receipts
that rendering could not load. All were labeled important and assessed Important:
the first can authorize an action after a hidden failure; the others weaken the
reader guard and prevent reporting setup failures. All are taken. Behavior fixes
require another round; the reader fix alone changes tests only. Simplify found
no proposals. End state: stopped: recurring defect.

TOOLING's structural call (native message `20261104T093321Z`) removes interpreter
classification and option injection entirely. Single argv commands are opaque;
explicit staged pipelines are constructed and supervised by the runner. Each
stage exit is recorded and every stage must succeed. Separate checks express
logical steps. New plants guard this contract, duplicate-reader refusal and
setup-failure rendering. This is within the unshipped interface's scope. Counts
carry forward: next is Important 2; a third interpreter-classification recurrence
stops without another patch.

## Test hooks after extraction

TOOLING authorized these plumbing changes while preserving assertions, named
plants, expected exits and existing Scrut snapshots:

- Import the real sibling `checked_core.py`; redirect command/group mocks there.
- Parse each runner and the core separately for reader and cause guards.
- Select each mutation's real source file and declare both scripts and the core
  as copied plant inputs; compound mutations patch their actual modules.
- Keep reader mutations' mode lookup self-contained after import extraction.

## Validation and remaining steps

Before round-1 fixes, gate behavior, gate plants and checked-plant partition 1
Scrut documents each exited 0. Current-tree validation is pending. Full focused
review, trims, disposable-clone Semgrep baseline, lint, locked full suite,
version check, exact-tree signed tidy and PR publication remain pending.

## Structural Important 2 and receipt-shape closure

Round 3, Important 2: both reviewers exited 0, schema-valid; scope unchanged.
Anti-patterns reported two important findings, both assessed Important and taken:
downstream closure could discard capture, and timeout could lose observed stage
exits. Draining after closure retains bounded capture; each observed exit is now
published immediately. These change behavior and require the next round.

A local fault injection also reproduced a rendering recurrence: the supervisor's
valid unknown-exit result was emitted but rejected by the loader. Assessed
Important, taken after TOOLING's native structural call `20261104T095401Z`.
One constructor and schema now live in the core; typed states distinguish absent,
failed and unknown exits. Publication rejects rows created outside the constructor.
Loading validates every well-formed state; verification alone demands passing
execution. The table-driven failure contract and constructor guard are planted.
A third receipt-shape recurrence goes to TOOLING without another patch.

Simplify's two suggestions were assessed Nit and taken as local structural
cleanup: one shared row constructor replaces duplicate defaults; stage rows'
start timestamps replace the parallel timestamp list. No independent design
change. Structural loop count carries forward: next is Critical-only. The focused
review loop has not started.

## Structural Critical 1 and monotonic stage evidence

Round 4, Critical 1: anti-patterns and simplify exited 0, complete and schema-valid;
scope unchanged. Simplify had no findings. Anti-patterns labeled capture-read
failure losing observed exits important; assessed Important, taken. This repeats
the stage-evidence-loss class. End state: stopped: recurring defect.

TOOLING's native call `20261104T102249Z` approved monotonic stage observations:
record every available start, exit and duration before reading any capture, then
handle each stream independently. Separate EOF, loaded-data and failure facts
survive later failures. Missing responses produce explicitly unknown evidence.
The pipeline fault matrix covers capture reads, absent/corrupt/partial responses,
missing stream metadata, missing durations, setup, spawn and timeout. It checks
that every available execution fact survives and that every failure renders but
verification refuses it. Assembly order and the monotonic helper are planted.
A third stage-evidence recurrence goes to TOOLING without another patch. Counts
carry; TOOLING named structural Critical 2 as the next round.

Local input-contract corrections also allow empty argument values and integer
expected process return codes, and include index status flags in its semantic
fingerprint. These preserve the brief's generic argv, expected-exit and declared
index contracts. Each boundary has a real case and a source plant.

The input contract also verifies an action's resulting HEAD when its recorded
commit tree equals the checked tree. Non-finite JSON constants are rejected so
failure receipts remain standard JSON. Matching-head, argument, index-flag and
JSON boundaries are included in source plants.

## Structural Critical 2: third-instance stop

Round 5, Critical 2: both reviewers exited 0; outputs schema-valid and complete,
with no lasting scope changes. The current 25 behavior cases and 25 checked source
plants exited 0, but omit the sibling failures below. These passes do not close
the findings.

| Finding                                               | Reviewer label | Severity and impact                                                                                                                    | Take or record                                                       | Review again          |
| ----------------------------------------------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | --------------------- |
| Invalid completion envelope drops stage records       | important      | Important: valid starts, exits and durations become unknown                                                                            | Take pending structural decision; no patch under third-instance rule | Yes: behavior changes |
| Supervisor spool reads erase completed execution      | important      | Important: a read error after wait loses exit and pipeline facts; the underlying code predates extraction, but new consumers expose it | Take pending structural decision; no patch under third-instance rule | Yes: behavior changes |
| Exponent overflow emits an unreadable failure receipt | important      | Important: `1e309` bypasses `parse_constant`, becomes infinity and serializes as `Infinity`, which the loader rejects                  | Take pending structural decision; no patch under third-instance rule | Yes: behavior changes |
| Replace manual test restoration with scoped patches   | suggestion     | Nit: test-plumbing cleanup with no behavior impact                                                                                     | Record below threshold; further edits stopped                        | No                    |

The first two findings recur in lost stage evidence; the third recurs in
incompatible emitted/read failure receipts. TOOLING's standing calls require a
third instance in either class to be reported without another patch. Stop report
`000007-20261104T105759Z-stop.md` was sent to TOOLING. No patch followed.

**End state: stopped: recurring defect.** The focused review loop, trims, Semgrep
baseline, lint-and-fix, full suite, version check, tidy, push and ready PR remain
unrun. No activation, hooks or global instructions changed. Work waits for
TOOLING's design and restart decision.

## Approved fact journal and strict codec correction

TOOLING relayed the restart and design go-ahead in native message
`ba199809-a44d-4ac0-b9d9-d857f00258e3` (`20261104T121001Z`), following the
Inbox decision in Today’s plan, Nov 4, at 7:08 AM ET, record `76e05dc5`.
This supersedes the preceding stop, without resetting review counts.

Every execution observation now appends a fact to an owned journal. Starts,
exits, bounded bytes, EOF, cleanup, reap and failures are recorded as observed;
the receipt is exclusively a fold of those facts. Worker response validation
adds failures without replacing observed stage facts. Supervisor spool-read
failures retain the bytes and exits recorded before that read. Publication and
loading compare the receipt against its folded journal. Status rendering still
uses only the published receipt.

One strict codec now handles manifests, worker responses, journal facts and
receipts. It rejects non-finite constants and exponent overflow on input and
non-finite values on output. A source guard rejects JSON decoding or encoding
outside that codec. Tests and source plants cover both constructor bypasses.

The three Important findings from Critical 2 are taken under this approved
structural design. Behavior changes require the next structural round, Critical
3; the focused loop has not started. The original 25 gate behavior cases and
four additional cases exited 0 (`/tmp/checked-gate-journal29.log`). Plants and
checked-plant compatibility remain pending at this checkpoint.

## Structural Critical 3 and journal validation

Round 6, Critical 3: anti-patterns and report-only simplify both exited 0 with
complete, schema-valid replies. The anti-pattern review read all 17 canonical
files, found no Important finding and identified no recurrence. Simplify
completed its four cleanup angles inline and proposed removing the unused
`load_rows` helper and import. Reviewer label suggestion; assessed Nit, a trivial
local cleanup to take after the design gate below; no behavior change or further
round required. The simplify sandbox could not repeat GitHub metadata lookup;
the parent independently confirmed the active, owned, non-fork repository.
Scope comparison exited 0 with `scope_changed: false` and no lasting changes.
Structural loop end: **clean at Critical**.

Validation completed on the journal implementation:

- 29 gate behavior cases: exit 0, `/tmp/checked-gate-journal29.log`.
- 30 checked source plants: runner exit 0, every named assertion red exit 1,
  restored green exit 0, `/tmp/checked-gate-journal-plants-final.log`.
- Original checked-plant suite, 43 cases: exit 0,
  `/tmp/checked-plant-journal-compat.log`; guard partitions 2 through 4 remain
  pending the full suite.
- Build, diff check and version/catalog validation: each exit 0; plant-defects
  advances from 1.1.0 to 1.2.0, with manifest-only version ownership.

The initial journal plant run had one surviving mutant: the completion-envelope
edit left a sibling type check intact. The corrected plant removes the complete
envelope condition. It and the other 29 plants passed on the committed test
checkpoint. The initial plant run preceded its source checkpoint; the final run
used signed commit `91cef6de` and restored green after every variant.

## Check-boundary fingerprint design gate

A local reproduction after the structural review found a separate Important
boundary defect. Three checks all declare `tree`: the first changes a tracked
file, the second checks that changed content, and the third restores the original
content. Recorded check exits were `[0, 0, 0]`, the action exited 0, and initial
and final fingerprints matched. The middle check inspected another tree, yet
the receipt passed. The reproduction exited 0 in an owned disposable fixture;
no source patch was applied.

Reviewer label: local observation. Severity: Important, because a passing receipt
can attribute checks to a tree they did not inspect. Take pending design call.
Review again: yes, behavior changes. Proposed correction records fingerprints at
each check boundary, still attempts every check, and refuses the action for any
different or unknown boundary, including a later restored tree. Add a regression
and checked plant. This is distinct from the recurring receipt-shape and
stage-evidence classes.

Question `000009-20261104T130837Z-question.md` went to TOOLING for the required
design call. The focused loop, trims, Semgrep, locked full suite, final lint,
tidy, push and ready PR remain unrun. No activation, hooks or global rules changed.

TOOLING approved the check-boundary correction in native message
`5d0282ff-0707-4318-b015-6895e3937939` (`20261104T130853Z`), on the existing
start record `76e05dc5`. Each check now records start and end fingerprints as
append-only facts folded into its row. All declared checks still run; a shared
boundary predicate gates the action, folded success and verification. Missing,
failed, duplicate or different boundary observations cannot pass. A regression
covers restoration by a later check, missing facts and a failed fingerprint
read, with a source plant of the shared predicate. The unused-loader Nit is
also taken: the obsolete loader and import are removed without behavior change.
Counts carry forward to the focused loop as TOOLING directed.

## Focused Nit round

All five aspects ran in fresh read-only Codex `gpt-6.1-sol`, high effort,
872000-token windows, with `CLAUDE.md` fallback guidance explicitly supplied.
Code, errors and tests ran first, then comments and types. Every process and
completion/schema check exited 0. The post-review scope comparison exited 0,
with `scope_changed: false`, no lasting changes and no outside-scope paths.
Code and errors reported no findings.

| Finding                                                   | Reviewer label | Severity and impact                                                                                                                     | Take or record                                                                                                                         | Review again   |
| --------------------------------------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| Action failure outcomes lack tests                        | important      | Important: action failure could be reported as success without a regression failing                                                     | Take: nonzero exit, spawn failure and timeout cases, with a checked outcome plant                                                      | No: tests only |
| Declared ignored-file fingerprints lack tests             | important      | Important: tree checks cannot detect lost content or mode enforcement for ignored inputs                                                | Take: unchanged-file success and separate content/mode refusals, each planted                                                          | No: tests only |
| Opaque argv reference overstates environment preservation | suggestion     | Nit: the shared supervisor sets Python cache variables                                                                                  | Take: name the cache variables and limit the no-injection promise to strict-mode options                                               | No: docs only  |
| Fold projections retain nested object references          | suggestion     | Nit design suggestion: mutating a returned argv also mutates its embedded journal, but current runner paths never perform this mutation | Record: optional internal API ownership change, with no demonstrated execution defect; unsigned JSON remains caller-editable by design | No: no edits   |

The types suggestion concerns direct mutation of an in-memory projection.
`run`, `execute`, `load`, `verify` and `render` do not relabel or mutate these
nested values. No new encapsulation contract or command-event validation was
added for that optional proposal.

The boundary plant run exited 1 because the new boundary predicate separately
rejected the verify-membership mutant. Its compound mutation now also weakens
that sibling guard. The tree plant likewise weakens both guards so its assertion
checks action refusal rather than only the refusal's wording. No production
behavior changed in these test corrections. The measured 334.774-second run
exceeded the document budget; the source plants now use three partitions, with
partition inputs cleared by the common test environment.

Focused loop end: **ended: fixes changed no behavior**. The two Important
findings are taken as tests with source plants; production behavior remains the
reviewed implementation. New test execution, trims, Semgrep, the locked full
suite, final lint, tidy, push and ready PR remain pending at this checkpoint.

## Focused fixes, plants and trims

The expanded behavior suite exited 0: 32 cases
(`/tmp/checked-gate-focused32.log`). All three named Scrut plant partitions
exited 0: 34 source plants, partitioned 12, 11 and 11. Each plant requires the
named assertion's red exit 1, restored green exit 0 and successful JSON-only
rendering. Logs: `/tmp/checked-gate-plants-part1.log`,
`/tmp/checked-gate-plants-part2.log`, `/tmp/checked-gate-plants-part3.log`.
The previously masked membership plant now reaches its intended assertion.

Comment and prose trims ran once each through fresh read-only Codex
`gpt-6.1-sol`, low effort, 872000-token windows. Both processes, nonempty replies
and report-prefix checks exited 0; all six source files and ten prose files
were classified in full. HEAD, tree and clean status remained unchanged during
the runs. Comment trim proposed no changes. Prose trim proposed two wording
changes in the gate reference; both are taken without meaning changes.
No proposals were declined, flagged or moved elsewhere. Required historical
review evidence and catalog descriptions remain intact. No executable source
changed, so unchanged-code verification is inapplicable to these edits.

## Full-suite artifact failure and focused continuation

Semgrep's baseline scan in an owned shared clone exited 0, with zero findings
and zero parser errors. The final scan used `98c5f843`, actual baseline
`ed2a0df956595873acf9476ea6f5000fabec9294`, `--config auto`, and clone-local
`diff.renames=true`. It scanned 14 targets with 1278 rules; default ignores
excluded generated mirrors and tests. Artifacts are under
`/tmp/checked-gate-semgrep.Xee6Hc/`.

The first locked `make test-all` exited 2 during validation, after all project
lint passed. A direct CLI import of the extracted core had created
`plugins/plant-defects/scripts/__pycache__/checked_core.cpython-313.pyc`, and
`make build` had copied it into the mirror. The validator rejected the generated
binary as a non-source file. Thermal inspection reported no warning; both suite
locks released. This is a failed full-suite result, not a validation pass.

Reviewer label: local validation failure. Severity: Important, because the new
sibling import adds an artifact that prevents repeated validation and can enter
a generated bundle. Take: both entry scripts disable bytecode writes before the
shared-core import. A disposable-copy CLI test clears inherited cache settings,
proves both programs ran and checks for cache artifacts; each entry's guard has
a source plant. Only the exact recorded source cache file and its empty directory
were removed; `make build` regenerated the mirror. No validator exclusion or
ambient environment workaround was added. Review again: yes, artifact behavior
changes, so the focused loop continues at Important 1, retaining its Nit count.

Mailbox status `000011-20261104T143604Z-status.md` records this failure and the
in-scope correction. Updated checks and the focused Important round remain
pending at this checkpoint; no publication occurred.

## Focused Important 1

All five aspects completed with process and schema checks exiting 0 on
`715f874b`; model, effort, window, sandbox and fallback guidance match the Nit
round. The post-review scope comparison exited 0 with no scope or lasting
content changes. Code, comments and types reported no findings.

| Finding                                                   | Reviewer label | Severity and impact                                                                                                                          | Take or record                                                                                                               | Review again                    |
| --------------------------------------------------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| Action and stage diagnostic causes omitted from rendering | important      | Important: the reporting interface hides the cause needed to distinguish spawn, timeout and stage capture failures, although JSON retains it | Take: render action argv and row cause separately from the run cause, and render each stage cause; add assertions and plants | Yes: rendering behavior changes |
| External manifest changes lack coverage                   | important      | Important: removing the stable-manifest guard could permit an action after its external manifest changed                                     | Take: mutation during a successful check, unchanged Git fingerprints, refusal and verification tests, with a guard plant     | No: tests only                  |
| Untracked file contributions lack coverage                | important      | Important: a tracked-only private index could authorize an action while omitting untracked source                                            | Take: unchanged untracked-file success, tree membership, creation/modification refusals and a tracked-only plant             | No: tests only                  |

These are separate paths from the earlier observations lost during capture IO:
all diagnostic values remain in the receipt. The rendering fix adds those
recorded fields to the human interface. The new coverage cases exercise the
external manifest comparison and private Git index, rather than the declared
ignored-file reader covered in the Nit round.

The bytecode correction's 33 behavior cases exited 0, followed by source
validation and artifact-absence checks exiting 0. Both actual `uv run --script`
entry points exited 0 for help without creating a source cache. The two affected
Scrut plant partitions, containing both new entry guards, exited 0.

The loop remains open: rendering changes require focused Important 2. Updated
behavior and plant checks are pending at this checkpoint.

## Focused Important 2: recurring partial-startup evidence loss

The 35-case behavior check exited 0 after Important 1's fixes. The expanded
source plant set has 40 cases, partitioned 14, 13 and 13. Partitions 1 and 2
exited 0; partition 3 was not started after this stop. These checks do not cover
the newly identified partial-startup failure.

Focused Important 2 completed code, errors and tests with process and schema
checks exiting 0. Code reported no findings. The post-review scope comparison
exited 0 with `scope_changed: false` and no lasting changes. Comments and types
were not started after the recurrence; this round is incomplete.

| Finding                                                         | Reviewer label | Severity and impact                                                                                                                                                                              | Take or record                                                                                                  | Review again                                           |
| --------------------------------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Later pipeline setup failure bypasses earlier stage observation | important      | Important: an earlier stage can emit diagnostics and exit before a later spawn fails, but the worker returns without capture threads or exit polling, leaving empty captures and an unknown exit | Take pending structural call; no patch under the recurrence rule                                                | Yes: lifecycle behavior must change                    |
| Journal persistence and partial-record recovery lack tests      | important      | Important: append/flush failures and torn records could lose the failure marker or permit an action without a regression failing                                                                 | Take pending structural call: transient-write and partial-record cases plus a checked journal-error guard plant | No for tests alone; the structural fix requires review |

The first finding recurs in the pipeline evidence-loss class. The journal
preserves facts once observed, but partial setup can bypass observation entirely.
The current fault matrix derives expected observations from that journal, so it
cannot prove that output or exits available outside it were collected. A stronger
regression needs independent evidence that the earlier stage emitted and exited
before the later spawn failure.

Stop `000012-20261104T150315Z-stop.md` went to TOOLING. No patch followed.
The proposed structural direction is one lifecycle that covers partial setup,
bounded output draining, stop/reap and journaling of already-started children,
while retaining the original spawn failure. TOOLING owns the design and restart
call; review counts carry.

**End state: stopped: recurring defect.** The Semgrep rescan for subsequent code
changes, complete locked full suite, final lint, tidy, push and ready PR remain
unrun. The prior full-suite result remains exit 2. No activation, hooks or global
instructions changed, and no locks or background commands remain.

## Approved common pipeline lifecycle

TOOLING's structural call `592fa08b-e279-4092-8a5c-e74d3bbcad76`
(`20261104T150350Z`) resumes the existing journal design on start record
`76e05dc5`. Every started stage now enters the same capture and stop/reap path,
including partial spawn, capture-file setup and pump setup failures. Starts are
journaled before subsequent spawns. The original setup error remains the primary
cause; later observations and failures add facts. A worker execution deadline
leaves a bounded cleanup allowance before the outer process-group supervisor's
deadline. Existing checked-plant command behavior is unchanged.

The new regression uses an independent sentinel and exit observation outside the
journal, before the injected later failure. It covers missing/denied later spawn,
capture setup, a third-stage failure, a running first stage and pump setup. It
asserts original output, known exits and reap evidence for every started child,
renderable refusal and rejected verification. Separate plants weaken partial
capture setup and cleanup/reaping. Journal tests inject append acknowledgement
failure, queued-exit flush failure and a torn record, retaining known exits and
bytes after recovery; both the failure marker and action guard are planted.

The five existing pipeline smoke cases exited 0. The two new lifecycle and
journal-recovery methods exited 0. Expanded behavior, source plants and resumed
review remain pending. Important 2 is still incomplete; counts carry. TOOLING
requires another recurrence in pipeline evidence to stop for a decision about
omitting pipelines from the initial release, without another local patch.

## Resumed Important 2

All five aspects completed on `2201a7cd`, with process, schema and scope checks
exiting 0. No lasting scope changes were found. Code, errors, comments and types
reported no findings. The prior partial-startup finding is resolved by the common
lifecycle and independently observed regression. The expanded behavior suite
exited 0 with 37 cases; all three lifecycle plant partitions exited 0, covering
44 source plants. Shared reader and formatter guards also exited 0.

| Finding                                                      | Reviewer label | Severity and impact                                                                                               | Take or record                                                                                                                                          | Review again   |
| ------------------------------------------------------------ | -------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| Empty-check manifest rejection lacks direct coverage         | important      | Important: weakening the manifest guard could run an action with no checks                                        | Take: actual empty-check manifest, no action, renderable refusal and failed verification, with a guard plant                                            | No: tests only |
| Automatic shared-core fingerprint lacks independent coverage | important      | Important: explicitly declaring the core in existing plant fixtures can hide removal of its automatic fingerprint | Take: disposable plugin copy without a declared core input, changed content/mode refusals preserving records, and separate omission/content/mode plants | No: tests only |

The new tests exited 0 as part of the 39-case behavior suite. The child-reap plant
now removes signaling while retaining capture cancellation and descriptor
cleanup, isolating the intended failure rather than removing unrelated cleanup.
All source-plant targets are checked against the production scripts before use.

Focused loop end: **ended: fixes changed no behavior**. Counts remain one Nit,
Important 1 and Important 2, including the recorded stop and resumed snapshot.
The last fixes are tests only, so another focused round is not required. The
new source plants, final trim coverage for changes after the earlier trim,
Semgrep rescan, complete locked full suite, final lint, tidy and publication are
pending at this checkpoint.

## Final trim coverage and baseline scan

The final changed-unit trim coverage ran after implementation stabilized,
limited to comments and prose changed since `98c5f843`; the earlier trim's work
was not repeated. Both read-only Codex runs used `gpt-6.1-sol`, low effort and
872000-token windows, exited 0, and passed nonempty/report-shape checks. All four
source files and two prose files were classified. No changes, declined proposals,
flags or unresolved trim checks were reported. HEAD, tree and clean status stayed
unchanged. Source comments retain the cache, partial-startup lifecycle and
unfinished-thread descriptor constraints; audit facts and fenced test data stay
protected.

Semgrep's rescan of `d7a81f0b` in the same disposable clone exited 0 with zero
findings and zero parser errors. The actual merge-base baseline, auto rules,
repository slug and clone-local rename setting were unchanged. Results:
`/tmp/checked-gate-semgrep.Xee6Hc/reviewed-results.json` and
`reviewed-scan.log`. Subsequent edits here record results only.

The 39-case behavior suite exited 0. The final source set has 48 plants; named
Scrut partitions 1 and 2 exited 0. The complete locked full suite will exercise
all three partitions, including the remaining standalone partition, and the
unchanged checked-plant suite and its guard partitions. Final full-suite and
publication results remain pending at this checkpoint.

## Linked-entry compatibility correction

A compatibility probe against the original monolithic runner found baseline
linked-entry exit 0 and current linked-entry exit 1. `uv run --script` preserves
the link path in `__file__`; the extracted dependency lookup therefore searched
beside the link instead of beside the resolved runner. The original runner
fingerprint already resolved its entry path. Reproduction artifacts are in
`/tmp/checked-gate-link-probe.b3Y0ap/`.

Reviewer label: local compatibility probe. Severity: Important, because a
previously working entry invocation fails after extraction. Take: resolve the
entry path before both sibling-core lookup and core-output protection. The
regression now exercises linked run/render, stale-core refusal and protection of
the actual module, with plants for both boundaries. Review again: yes, this
compatibility behavior fix continues the focused loop at Critical 1, retaining
all previous counts. It is not a pipeline-evidence recurrence.

The superseded full-suite supervisor PID `86203` was verified by exact command
and working directory before SIGTERM. It forwarded cancellation to its owned
child group, exited 143, and released both locks. The original checked-plant
suite and its three guard documents, all new gate documents and other completed
documents had individually passed, but the full suite was intentionally
cancelled and is not a pass. No source edits occurred before termination and
lock release were observed. The linked-entry regression check then exited 0.

Status `000013-20261104T163042Z-status.md` informed TOOLING. Updated review,
plants, baseline scan and complete full-suite validation remain pending at this
checkpoint. No activation, hooks, global instructions or publication changed.

## Final focused review and validation

Focused Critical 1 reviewed `de6a14af` in all five aspects with explicit
`gpt-6.1-sol`, high effort, 872000 context and read-only settings. Every process,
schema and completion check exited 0; the before/after scope comparison exited
0 with no scope change. Code, tests and types reported no findings. Artifacts:
`/tmp/checked-gate-review.7yhchO/focused-critical1/`.

- Reviewer label: suggestion. Rendered reports omit the original per-boundary
  fingerprint diagnostic. Severity: Nit, because the receipt retains the cause
  and the action is safely refused with a boundary failure. Record: a diagnostic
  enhancement below the Critical threshold, rather than missing behavior or
  boundary coverage. Review again: no edit taken.
- Reviewer label: suggestion. The first plant document overstates its partition's
  coverage. Severity: Nit, a heading correction. Take: name partition 1 and remove
  the claim that it exercises every boundary. Review again: no, wording only.

Focused review ends **clean at Critical** after four rounds: Nit, Important 1,
Important 2 (interrupted and resumed at the same count), and Critical 1.
Structural review retains its six-round **clean at Critical** result. The final
changed-unit comments and prose trims retained their complete no-change results.
No pipeline-evidence recurrence occurred after the last structural call.

The final baseline Semgrep rescan of `de6a14af` exited 0 with zero findings and
zero parser errors, using the recorded disposable clone and actual merge base.
Results: `/tmp/checked-gate-semgrep.Xee6Hc/final-results.json` and
`final-scan.log`. Both linked-entry plant partitions exited 0.

The complete full suite exited 0 at unchanged `de6a14af`: lint, validation and
all 85 Scrut documents passed. This includes 39 gate behavior cases, all 50 gate
plants through checked-plant, and the original checked-plant behavior and guard
documents. No tests were skipped. The tooling directory lock and heavy lock were
released; the canonical bytecode-cache directory remained absent. Thermal and
performance checks reported no warning. Evidence:
`/tmp/checked-gate-full-suite-final2.log` and its thermal log. Earlier failed and
cancelled runs remain recorded above and are not counted as passes.

The final version audit exited 0: plant-defects 1.1.0 to 1.2.0 is a minor
capability bump; marketplace coverage and manifest-only ownership match. Only
the accepted heading correction and these process records changed after the
full suite. Final lint, signed exact-tree tidy and publication follow.
