# Load-tolerant plant runner supervision

## Authority and current gate

Corrective work for tooling Queue 0f+, issue cboone/agent-harness-plugins#733.
CONDUCTOR record 6f62aceb opens this run on Codex normal-max-default.
Build through a ready PR; TOOLING holds merging for CONDUCTOR's version check.
Reviews are pinned to merge base
`302c0d91a77097f1ae66e39bd996253e4bbb17d8` while the review-scope stop holds.

TOOLING native000035 keeps verdict reading identical to main and moves its
redesign to the structured-result follow-up, cboone/agent-harness-plugins#739.
Native000037 and native000038 reopen test-only work after the final-5 restart
failed in bounded-capture. Production allocations and the document cap stay
unchanged. The approved detector wait, cleanup allowance and check limit are
recorded in the detector-margin section below. No additional structural round
is required for this correction.

Implementation is committed; final evidence is produced outside the source
tree. The required current-head default-parallel restart, complete plant replay
and survivor observations must finish before publication. No ready PR or merge
is claimed here. Earlier attempts below are historical evidence, not proof for
the final committed tree.

## Earlier preflight record

**Building under the reopened gate:** preflight found the propagated TERM-phase
inspection deadline could become too
small for `ps`. The 0.012164791580289602-second timeout bypassed final KILL
verification and retained stale PID evidence. Measured preflight:
`test_term_ignoring_group_is_stopped`, exit 1, 3.813 seconds. The command exited 0
and was reaped; cleanup retained PID 32424 and a `TimeoutExpired` cause.
Mailbox stop 000005 recorded it. TOOLING approved the phase-transition correction
on 6f62aceb and classified it as an implementation issue caught before review,
not another review recurrence. TERM exhaustion now advances to the KILL budget
reserved up front; only verified final state permits success. Phase expirations
are retained separately from cleanup errors and EPERM. Controlled tests and
plants cover transition, unknown final state and reservation ordering.
No worker-owned process remains running.

The structural implementation and checks form one checkpoint commit. The
centralized-I/O oracle recognizes the implementation behind the public command
wrapper. Further validation remains pending.
No full restart check, ready PR or merge claim exists.

## Structural calls and deadline survey

Initial source/check commits: f95bd971, b6aece3f and 61f393d0. Plant-defects is
bumped from 1.2.1 to 1.3.0 for the approved optional `git_timeout` capability.
Extend the existing execution core and regression suite; no new plugin or
watcher is proposed.

TOOLING's first structural call, on 6f62aceb, closes timeout-budget propagation:
one declared cleanup margin, absolute deadlines passed to supervision waits,
a syntax guard against independent literal limits, named detectors isolated per
mutation, and enforced per-document bounds. The approved policy is a 15-second
cleanup margin, counted wherever spent. An expired execution budget still
reserves cleanup. The document driver requests 285 seconds. Its 300-second root allocation
allows at most 255 seconds execution, 30 seconds child cleanup and 15 seconds
enclosing cleanup. Guard documents account for three phases times each declared
check budget plus its cleanup margin, without multiplying nested waits again.

| Site                                  | Previous limit                 | Current implementation, pending validation                                                                      |
| ------------------------------------- | ------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| Journal flock                         | 0.25 s                         | Enclosing active deadline; root journal operation uses the cleanup margin                                       |
| Process inspection                    | 0.25 s                         | Remaining absolute phase deadline                                                                               |
| Group TERM/KILL observation           | 0.2 s per signal               | Child deadlines partition the remaining group budget; TERM exhaustion advances to the reserved KILL observation |
| Leader reap                           | 1 s                            | Remaining reserved cleanup budget, with retained cause                                                          |
| Pipeline TERM/KILL reap               | 0.2 / 0.5 s                    | Remaining worker cleanup budget, partitioned across signals and thread join                                     |
| Pipeline thread join                  | 0.3 s                          | Remaining shared worker cleanup deadline                                                                        |
| Pipeline supervisor allowance         | 2 s                            | Worker cleanup reserve followed by supervisor cleanup reserve                                                   |
| checked-plant commands, setup and Git | Manifest timeout, default 60 s | Execution budgets retained, cleanup reserve separate                                                            |
| Detached-stdio detector               | 0.5 s assumption               | Readiness after flushed output; enclosing declared detector budget and reserved cleanup                         |
| Other test subprocess supervision     | Literal 2 / 3 / 5 s            | Remaining declared testcase budget                                                                              |
| Partial-pipeline oracle               | Literal 2 s                    | Deadline passed in the worker request                                                                           |
| Behavior and guard document drivers   | Scrut's outer timeout only     | At most 255 s execution, 30 s child cleanup, 15 s enclosing cleanup                                             |

Polling intervals remain scheduling yields. Intentional short command execution
budgets remain supported. There are 15 plant guard documents with 29 mutations;
the extra mutation verifies normally exiting group cleanup. A membership test
requires every original detector, 31 total, to appear as a named check. Sibling
assertions remain with each mutation that depends on them. Changed gate
runner/plant documents also use the enclosing document driver.

## Reviews and findings

The first structural Nit review overlapped the plant-fixture commit. Its
findings were retained; the subsequent Important round covered all committed
fixtures at 61f393d0. The structural loop used anti-patterns plus report-only
simplify; all four simplify angles ran inline in fresh read-only contexts.
The focused Nit round covered code, errors, tests and comments. Types did not
apply because the initial diff added no data definitions.

Review outputs remain in the owned evidence directory. The first focused launch
failed its working-directory preflight before launching reviewers; the corrected
invocation ran four aspects. Counts are preserved: structural Nit and Important 1;
focused Nit. Further review has not run on the structural implementation.

| Finding                                                                 | Reviewer label | Our severity | Take or record                                                | Review again                                 |
| ----------------------------------------------------------------------- | -------------- | ------------ | ------------------------------------------------------------- | -------------------------------------------- |
| Detached detector exceeded enclosing plant budget and could raise ERROR | important      | Important    | Taken in 61f393d0                                             | Behavior changed; structural Important 1 ran |
| Standalone reap timeout lost its named cause                            | nit            | Nit          | Taken in 61f393d0                                             | Behavior changed; structural Important 1 ran |
| Seven-variant guard documents exceeded CI runtime target                | important      | Important    | Taken under TOOLING structural call; validation pending       | Recurrence stop; focused count preserved     |
| Delayed pipeline cleanup lacked coverage                                | important      | Important    | Integration regression and two source plants prepared         | Included in resumed review                   |
| Readiness failure hid early runner diagnostics                          | suggestion     | Nit          | Early exit now reports code, stderr and available result JSON | Test-only change                             |

No finding was downgraded. The first recurrence stop was reported in mailbox
000002; TOOLING's structural decision and refinements arrived on 6f62aceb.
Mailbox 000005 recorded the preflight issue and reopened on TOOLING's decision.
The focused loop continues from Nit. Its previous stop was **stopped: recurring
defect**; no new review round has run yet.

## Evidence and remaining work

Owned evidence root:
`/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/733-load-timeouts-8m1mh8s_`.
Helper snapshots contain the complete plugin bundle plus separate SHA-256/mode
manifests; helpers run only after verification. `structural-2` holds the current
core snapshot used by preflight. Earlier plant receipts are superseded by these
source changes and do not establish the full restart check.

The original queued default-parallel suite was canceled at the first recurrence
stop by its recorded owned PID 42261: exit 143, before acquiring the heavy lock.
The suite did not run, and there is no receipt. Initial uncommitted preflight
runs are not final plant evidence and must be rerun after committing the checks.
The behavior-document preflight exited 2 at the outer command; captured output
reports unittest exit 1 with two failures, and make reported Error 50. Its
42 cases expose the centralized-I/O oracle mismatch and the TERM-phase boundary.
The dedicated measured TERM case exited 1 and retained the exact timeout above.

Before the ready PR: validate the approved phase handling and oracle correction;
rebuild mirrors and regenerate patches;
run every plant through checked-plant inside checked-gate; finish the required
reviews and trims, baseline Semgrep, lint-and-fix, versions and exact-tree tidy;
run the default-parallel full suite under the heavy lock; publish tree-bound
receipts and the JSON claim registry. Other full suites use SCRUT_JOBS=2.
The PR body must list the new CI documents, and its precis must compare CI job
count and observed wall time with main, naming incomplete measurements.

## Structural Important 2 and root-plan correction

Anti-patterns found two Important findings on 9ce65bed: nested commands and
pipelines replace enclosing deadlines, leaving their separate groups unreachable
when the document driver stops the test parent; and the budget model counts
three checks but omits Git init, patch validation and application. Their labels
and our severity are Important. Take both; behavior changes require the next
structural round at Critical. This is the recurring budget-overrun class,
reported in mailbox 000007. Focused remains at Nit.

Simplify reported duplicated supplementary detector declarations as Nit. Our
severity is Important because a separately hardcoded inventory can falsely
validate coverage after execution drops a supplementary detector. Take: one
mapping drives inventory and execution, retaining an independent expected-31
oracle, plus a planted omission. No reviewer label was downgraded.

TOOLING reopened 6f62aceb with a root-owned deadline and execution-derived step
plan: all supervised calls require the active or inherited deadline; runtime
records prove every step is inside its parent reserve; accounting consumes the
same plan as execution, Git steps included. The next structural round is
Critical-only. TOOLING selected cooperative TERM unwinding with durable metadata-only group
records. Session-per-command containment and held-leader signaling remain.
Lost supervisors and unknown group states stay red; no registry-driven signal
is permitted. The question is resolved on gate 6f62aceb.

The two structural processes, schema validation and unchanged-scope checks each
exited 0. Findings remain open; the round ended **stopped: recurring defect**.

## Checkpoint evidence on the earlier tree

Preflight and plant receipts were verified against the clean 9ce65bed tree in
the same strict tool call that wrote this record. These are historical after
this record commit or later source changes, not final merge evidence.

Preflight: budget guards, behavior42 and bounded-capture guard document each
exit 0; action exit 0. Plant gate: run exit 0, render exit 0, action exit 0.

Receipt root: /var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/733-load-timeouts-8m1mh8s_/checkpoint-1. Files:
preflight/receipt.json and plants-gate/receipt.json.

Checked tree: 5d097b7b88038f7aab333c7f1d517a32d6054601.

Complete owned plant-defects 1.2.2 bundle: /var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/733-load-timeouts-8m1mh8s_/checkpoint-1/plant-defects.
Separate SHA-256/mode manifest: /var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/733-load-timeouts-8m1mh8s_/checkpoint-1/plant-defects.json.
Manifest SHA-256: a6ff8046796e19789224c1e49609d2affdd90b0668ae2c5887517f7d1273724b.

<!-- checked-plants:start -->

## Verified plants and controls

plant old-ps-limit: named assertion reached; red exit 1; restored; green exit 0.

plant suppressed-eperm: named assertion reached; red exit 1; restored; green exit 0.

plant old-pipeline-allowance: named assertion reached; red exit 1; restored; green exit 0.

plant old-pipeline-grace: named assertion reached; red exit 1; restored; green exit 0.

plant literal-supervision-limit: named assertion reached; red exit 1; restored; green exit 0.

plant oversized-document-budget: named assertion reached; red exit 1; restored; green exit 0.

plant unenforced-driver-budget: named assertion reached; red exit 1; restored; green exit 0.

plant term-expiry-skips-kill: named assertion reached; red exit 1; restored; green exit 0.

plant unknown-final-state-accepted: named assertion reached; red exit 1; restored; green exit 0.

plant kill-reserve-consumed: named assertion reached; red exit 1; restored; green exit 0.

control longer-delay-control: green control verified; control exit 0; restored; green exit 0.

Evidence: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/733-load-timeouts-8m1mh8s_/checkpoint-1/plant-run/results.json`.

<!-- checked-plants:end -->

## Root execution checkpoint

The shared runtime creates the root deadline once, adopts complete inherited
contexts and refuses supervised work without one. Allocations record parent
identity and deadlines, reserve cleanup before the parent deadline and validate
that record before starting a process. TERM defers interruption across spawn and
registration, then unwinds cleanup; cancellation prevents new supervised work.
Pipeline stages retain their worker's held group. Incremental audit reads preserve
nested group observations without repeatedly scanning the entire journal.

One execution plan supplies both budgets and real dispatch for checks, setup,
Git initialization, patch validation and patch application. Successful results
validate the observed steps against that plan. Guard manifests independently
check their recorded allocations against the parent reserve. The optional
`git_timeout` defaults to `timeout`, is finite and positive through 3600 seconds,
and is refused if it cannot fit its enclosing execution budget. Guard fixtures
use 10 seconds for Git and retain their named check budgets.

The detached launcher signals readiness after flushed output. Test-side waits
use the enclosing budget and cooperate with runner cleanup. The single detector
mapping drives both execution and inventory, with a separate expected-31 oracle.
New plants target missing parents, parent reserve escapes, lost-supervisor
acceptance, omitted detectors and ignored Git budgets alongside the original
inspection and phase-boundary plants. All checkpoint validation remains pending
for the completed committed tree. No current-tree pass or restart claim exists.

## Structural Critical round

Both read-only Codex processes and schema checks exited 0 at c3de2319, with
unchanged HEAD and working tree confirmed in the same strict call as this record.
Each read all 58 applicable files in full; seven generated mirrors were excluded.
Anti-patterns established no Critical defect. Simplify's two reviewer Nit
findings are also our Nit: duplicated pipeline plan bookkeeping and a redundant
locked audit read in finalization. Take both as trivial local simplifications
that preserve the approved design. They are below the active threshold, so this
loop ends **clean at Critical**. Focused remains at Nit pending Important 1.

Checkpoint-2 validation failed before any source mutation. BudgetTests counted
all inherited scopes in the shared journal rather than its own descendants.
The test-side scope filter needs correction. Plant run exit 1, render exit 1,
action unrun/refused. Preflight gate exit 1: budget check exit 1; behavior,
bounded-capture, gate behavior and post-group observation exits 0; action refused.
These failed receipts support no passing current-tree or restart claim. All
artifacts remain under checkpoint-2; no run is relabeled clean.

## Focused Important 1 and identity correction

Code, errors, tests, comments and types completed on 54ab3a98. Retained statuses
and all five schemas were verified in the same strict call as this historical
record; the original unchanged-scope check is in focused-important1/changes.json.
Current source fixes are subsequent work and have not yet been reviewed.

Code/errors duplicate one reviewer Important, also our Important: a first TERM
inside cleanup can interrupt KILL/reaping/records. Take by deferring interruption
through cleanup and propagating afterward, covering both commands and pipelines.
Errors adds reviewer Important, also our Important: root finalization can hide
captured document diagnostics. Take by publishing streams before finalization,
retaining its separate red cause. Both change behavior, so focused Important 2
is next. These are new interruption/diagnostic mechanisms in the root revision,
not another instance of the earlier budget arithmetic/propagation defects.
Tests and types returned no findings. Comments' suggestion is our Nit: the stale
285-second execution claim omits child reserves; take the 255/30/15 correction.
No reviewer Important or Critical finding was downgraded.

Report 000014 published completion status outside its verification call. Stop
000015 recorded the Check records violation and performed same-call
reverification against 54ab3a98. TOOLING accepted that evidence and reopened
6f62aceb: every future mailbox, ledger, precis or PR check claim requires a gate
action or same-call strict verification; otherwise it is marked unverified.

Checkpoint-3 was canceled at owned, command-verified Python PID 47690 and exited 143. Its plants are incomplete, not a restart pass. Post-observation exit 1 found
numeric PGID 29189 matching a live process. TOOLING's read-only observation
identified macOS Contacts contactsd, PPID 1, started November 5 at 18:22:51 EST,
after the run: identifier reuse, not surviving work. No signal was sent.
TOOLING approved recording leader start time and command at spawn. Different
start time is reused; same start and command is survivor; unreadable identity or
same start with a changed command is unknown/red, since exec preserves identity.
Only held leaders authorize signals. Tests cover all four cases; source plants
cover reuse and exec-changed-command classification. This is metadata observation
within the existing containment design. Final evidence remains pending.

## Focused Important 2

All five aspects, their statuses and schemas, and unchanged review scope at
fccf6f5f were verified in the same strict call as this record. Code, errors,
comments and types returned no findings. Tests returned one Important, also
our Important: pure classifier tests do not prove reconciliation retains live
survivors or unknown identities and refuses final success. Take controlled
reconciliation/finalization tests for absence, reuse, survivor and both unknown
forms, assert no signals, and plant its live-group acceptance guard. The take
changes tests and fixtures only; no further behavior round follows this take.
The loop will end **ended: fixes changed no behavior** after that correction.

Checkpoint-4's full plant attempt is superseded and canceled by its recorded,
command-verified owned Python PID. Its receipt is not a final restart claim.
The final full plant replay follows the remaining trims, baseline scan, lint and
tidy, so its receipt can bind the completed tree. The owned cancellation PID is
retained in checkpoint-4/canceled-owned-pid.json. The initial cancellation
matcher refused an ambiguous match before signaling; matching the executable
and exact argv identified the owned process without relaxing identity checks.

The reconciliation take is implemented without production behavior changes.
The nine-test budget/supervision preflight exited 0 in this same strict call
before this record and commit. It is a preliminary check, not merge evidence.
The controlled journal and process observations prove absence/reuse clear,
survivor and both unknown forms stay pending and refuse finalization, and no
signal is sent. The added source plant remains pending the final complete run.
Focused loop end state: **ended: fixes changed no behavior**.

## Trims

One read-only Codex round each for code comments and prose at 47dab981, using
low effort. Reply shape, every selected file's classification and unchanged
starting scope were checked in the same strict call as this record. Code
comments: 11 files, no proposals. Prose: 24 files, two accepted rewrites in
checked-runner's Git-budget and deferred-TERM instructions. Both retain every
condition and use direct instructions. No proposals declined or left unresolved.
Source files remained unchanged. Markdownlint and Prettier checks for the edited
reference each exited 0 before this record. These are preliminary checks; final
lint and restart receipts remain pending. Raw replies remain in the evidence
root as trim-comments.md and trim-prose.md.

## Baseline scan configuration stop

The first baseline attempt in the disposable shared clone of 8ff58c81 exited 2
before scanning or producing result JSON: `--config auto` rejects the added
`--metrics off` option in the installed tool. Raw log and captured exit are in
semgrep/initial.log and initial-status.json. That status capture defaulted counts
from missing JSON; initial-summary.json correctly marks findings and scanned
count unknown. This is unavailable coverage, not a zero-finding scan.

Mailbox stops/questions 000021 and 000022 ask TOOLING to choose continuation with
an explicit rule config, proposing `p/default` with metrics off and the same real
baseline SHA. No config change, tool install or replacement full scan occurred.
The initial mailbox post from the scratch clone refused the wrong directory;
the report was then sent from the owned project worktree. Lint, tidy, final
restart receipts, push and PR remain behind this baseline gate. Review counts
and end states persist. The earlier copy-record parser issue was not reached.

TOOLING reopened 6f62aceb with one fresh-clone retry using `p/default`, metrics
off and clone-local `diff.renames=true`. Only shell parse errors were allowed by
the standing rule; any other failure remained a stop. The real baseline retry at
8a450451 exited 0, scanned 43 targets, and returned zero findings and zero errors.
No partial parse exception was needed. Status, result JSON, clone HEAD and the
unchanged source HEAD/tree were checked in the same strict call as this record.
The result is retained in 733-load-timeouts/semgrep-baseline.json and the raw
semgrep/retry artifacts. No source/global Git configuration changed. Continue
to lint, versions, tidy and final tree-bound restart receipts; this historical
scan is not itself a final merge receipt.

## Lint and fix

Mandatory lint-and-fix used no push. Fixers targeted changed files outside the
protected Scrut documents, which stayed check-only. The initial `make lint`
completed before `make validate` exited 2 at the fixture environment rule; later
validation steps and the dependent record/commit did not run.

The Git delay fixture now uses Bash and sources the shared Git environment reset
before any consumer. Its reset library is an explicit plant input; the fixture
root is set by the test. The former Python-specific exemption was removed.
This is a test-fixture correction, with no production behavior change or new
review round. Source-plant patches and mirrors were regenerated.

After the correction, `make lint` and `make validate` each exited 0, and the
changed Git-budget detector exited 0, before this record in the same strict call.
Outputs are lint-final.log and validate-final.log in the evidence root. No
advisory-only tools were inferred. Policy downgrade: Scrut documents check-only.
Final tree-bound receipts, versions, tidy and the default-parallel suite remain
pending. Caller resumes version verification and tidy.

The fixture correction's commit was the lint gate's dependent action: project
lint, validation and the affected Git-budget test each exited 0, then the signed
commit action exited 0. The receipt at lint-gate/receipt.json was verified against
the clean committed tree in the same strict call as this record. An earlier
staging command refused the already-moved Python path; its existing staged
deletion was retained and only actual owned paths were staged, without overrides.

The repository check-versions workflow refreshed origin/main and verified its
actual merge base remains the fixed review SHA. Manifest direction, optional
Codex manifests, marketplace coverage and version ownership checks exited 0.
Only plant-defects changes: 1.2.1 to 1.3.0, the approved minor capability bump.
The repository remains non-fork and not archived. These verifications preceded
this record in the same strict call. Final receipt binding remains pending.

## Final restart handoff

Source and test work is complete; final evidence remains unrun at this record.
The local review order ends structural clean at Critical and focused ended:
fixes changed no behavior, followed by one comments trim and one prose trim.
The Bash fixture normalization is a test-only lint correction; its affected test
and full lint/validation were gate-checked before its dependent signed commit.

CI Scrut jobs grow from 87 to 100. The 13 added documents are guard partitions
1 and 5 through 15, plus checked-timeout-budgets.md. The final precis and PR list
them explicitly. Base wall time is unmeasured; final local suite wall time and
normal-load observations will be recorded externally, with CI timing distinct.

Final receipts, helper SHA-256/mode manifests, generated plant status and the
JSON claim registry live under the worker mailbox's artifacts/final-1 directory.
No check outcome is assumed here. The final full source-plant replay, baseline
verification for the changed Bash fixture, version check and default-parallel
make test-all must all produce current-tree receipts before the ready PR. The
heavy lock is acquired before the suite gate starts its supervision clock; the
suite's own exact suite-lock/make command reenters that validated ownership.
Post-run identity observations classify reuse, survivor and unknown without
signaling unheld leaders. TOOLING retains the plugin-version merge hold; this
worker stops at the ready PR and keeps its worktree.

## Corrective fixture restart

The final plant attempt failed its verdict because a TERM assertion diagnostic
contained the reserved exclusion token `skipped`. Both diagnostics now describe
interrupted confirmation or an unreaped stage without that token. The exclusion
predicates remain intact. An assertion-message guard covers the methods executed
by this plant contract. Follow-up outside this PR: verdict classification by free
assertion text can collide with ordinary wording; structured assertion verdicts
need a separate design.

The Git fixture rejected its own macOS path alias through literal comparison.
Inode identity preserves the PATH guard across aliases. A zero-delay Git version
probe, foreign-PATH rejection control and ready sentinel establish that the
three-second Git budget detector is armed before the five-second delay. Its check
budget is ten seconds. Each correction has a source plant. TOOLING authorized
this test-only restart on gate 6f62aceb; production behavior and review counts
are unchanged. Earlier final-1 evidence remains retained and incomplete.

Final evidence will use artifacts/final-2. Lint, static checks, the entire plant
contract and the default-parallel suite remain pending for the corrected tree.

## Assertion guard coverage correction

The initial assertion-message guard mapped six assertion forms and omitted an
existing assertIsNotNone diagnostic. No current excluded token was present there,
but that form escaped the requested guard. The correction derives message
positions from unittest signatures, including context-manager keyword messages,
and refuses unsupported forms, argument expansion and invalid call signatures.
A source plant targets the formerly omitted diagnostic. Positive signature
examples and unsupported-form controls exercise the guard itself.

TOOLING approved this test-only structural correction on gate 6f62aceb. Another
gap in this guard requires a recurrence stop rather than another local patch.
The final-2 replay remains diagnostic evidence only. Final-3 must repeat lint,
static checks, all 27 assertion variants and the control, then the required
normal-load default-parallel suite. All outcomes remain pending for that tree.

## Approved simpler timing design

TOOLING reopened corrective work on gate 6f62aceb after the Inbox decision
“Plant-runner timeouts”, q-5ae07a2c. The design removes shared cumulative timing
and elapsed-budget admission. Each fixed call limit includes cleanup. Outer
limits are summed statically against the document cap; nested limits are checked
individually against their declared parent, without summing fingerprint calls.
The implementation plan is [Simplify plant-runner timing](../plans/done/2026-11-06-733-simpler-timing.md).

The failed default-parallel receipt and diagnosis remain retained under
artifacts/final-3. They do not support the new tree. Containment and the 1.3.0
version remain in scope; all implementation checks, the focused structural round,
trims, baseline scan and final restart gates are pending for the replacement.
Another budget or deadline defect requires a stop and report.

### Inclusive-limit fixture conversion

TOOLING classified the first replacement preflight's cleanup failure as a fixture
constant tuned for the earlier execution-plus-cleanup model. The production
allocation remains unchanged. Both delayed pipeline fixtures declare their TERM
wait once and derive the inclusive limit with a threefold observation margin.
The old fixture limit is retained as a source plant. The manifest-cause mutation
now preserves the surrounding indentation and has a syntax-validity detector.

The replacement uses the existing document runner's two queues: other documents
finish in the parallel batch, then checked runners execute serially in the same
owned process group. Parallel overlap and checked non-overlap have independent
fixture controls. Gate mutations are declared individually in the document
policy; the static fit check covers those plans, runner plans and whole-module
documents. The old parent-reserve plant is retired because that cumulative
admission mechanism was removed; fixed-limit escape and nested-size plants
replace that boundary coverage.

Preliminary receipts are retained under artifacts/design-2; their checked posts
refer to the working-tree snapshots tested there. They are historical pointers
for the coming committed tree. Final structural review, trims, baseline scan,
lint, complete source-plant replay and default-parallel restart remain pending.

## Verdict and audit-lock recurrence corrections

The structural replacement round ended `stopped: recurring defect`. Its raw
reports remain under worker artifacts/review-fixed-2. The anti-patterns reviewer
reported Important audit publication and parent-state lock waits before deadline
activation. Three simplify Nits remain held: explicit lock-deadline branches,
execution-plan reuse and an unused AST read. No findings were taken at the stop.
The fixture replay separately reached the intended scheduler assertion but its
nested Scrut `0 skipped` diagnostic collided with the whole-capture exclusion.

The Inbox decisions q-982d027b and q-945d95dd authorize both behavior corrections
in this PR. Verdict exclusions now use recognized outer framework statuses and
summaries. The repository manifests use unittest and Bash validity-fixture
formats. Unrecognized formats and actual unittest skips or framework errors are
refused. The manifest schema and full-capture required markers remain unchanged.
The signature-based message guard remains hygiene, outside verdict correctness.

Each call activates its deadline for allocation publication and parent-state
reads. A final execution-deadline check precedes Popen. Pipeline request and
response IO share the pipeline's active inclusive limit. The held-lock probe has
its own audit because its expected journal failure must not invalidate the
caller's ownership evidence. Its holder stays in the caller's contained process
group and is reaped by its recorded PID. The spawn probe advances its clock only
after reservation rather than mutating an already-copied timestamp.

Unverified evidence pointers: artifacts/compatibility-1 contains legacy normal
outputs for each existing manifest and the capture receipts. The first action
was refused on repository drift; its replacement repeats every capture with a
frozen source. The committed compatibility fixture compares current decisions
with those captured legacy decisions. New plants cover nested diagnostic text,
real skip, unknown format, held lock, parent-state activation and expired spawn.
Focused structural round 3 and every subsequent final check remain pending.
Version 1.3.0 includes both corrections; the merge hold remains with TOOLING.

## One launch point and final summaries

Structural round 3 ended `stopped: recurring defect`. Both reviewers reported
Important nested stdout summaries affecting the outer unittest verdict; the
anti-patterns reviewer also reported Important pipeline stage launch after a
blocking journal append crossed the execution deadline. The severity calls agree
with the false rejection and consumed cleanup reserve. No finding was applied at
the stop. Four simplify Nits remain held. Raw reports are committed beside the
previous rounds.

The Inbox decisions q-2392ac4e and q-c02cc255 authorize the class corrections,
relayed by TOOLING as native000029 on gate 6f62aceb. All launches now use one
function. It prepares options and chooses Popen or synchronous run before a
shared active-deadline check, then dispatches immediately. Synchronous inspection
keeps the standard library's existing timeout cleanup. Pipeline stages use their
execution deadline after journal append. The AST guard rejects launch API
references outside the sole core boundary, covering direct calls and aliases.

Verdicts use only the final summary in the framework's own result stream,
stderr for unittest. Earlier and per-test output is ignored. The nine captured
legacy decisions remain the compatibility contract. The nested stdout case,
missing summary, wrong stream and contradictory summary have focused controls.
The pipeline fixture holds its stage-journal lock between the allocation's worker
execution and cleanup deadlines; the stage's started flag supplies the result.
It does not rely on a process winning a filesystem race before cleanup.

Version 1.3.0 documents these rules. All validation for this replacement remains
pending, including the source plants and structural round 4. Subsequent review
launches follow each skill's reference with stdin closed. Native000031 clarifies
native000030: caller-built Codex commands use the actual worktree without added
repository flags. The sanctioned codex-aspects runner retains its documented
internal snapshot directory and repository flag, launched from this worktree.
No helper or trust setting is changed. Another instance of either class
requires a stop. Building still ends at the ready PR with TOOLING's merge hold.

## Split result reading into its own follow-up

TOOLING native000035 relays the “Split it out” decision, q-3317daad. The two
result-reading designs and their tests, plants and product documentation are
removed. The matches and expectation functions are copied exactly from current
origin/main and compared against a captured source baseline. The nine legacy
verdicts remain the compatibility contract. Structured results are tracked in
[cboone/agent-harness-plugins#739](https://github.com/cboone/agent-harness-plugins/issues/739).
Historical review reports retain the attempted designs as evidence, not current
behavior. Round 4 ended stopped: recurring defect; no finding was downgraded.

All timing, containment, launch-boundary and static-fit work remains. Restart
assertion context messages now use scalar status metadata, retaining full captures in
the runner evidence. A forced scheduler failure verifies that nested summaries
never reach its outer assertion diagnostic; its source plant restores the raw
result representation. The original assertion-message guard remains hygiene.

Validation is pending for this scope. Structural round 5 continues prior counts.
After trims, baseline scan and lint, current main is merged with a signed merge
commit if needed. Tidy and every final check follow, including the complete plant
replay from its start, default-parallel heavy-lock suite and survivor inspection.
The ready PR records the structured-result follow-up and remains under TOOLING's
merge hold. A new timing or deadline defect requires a stop.

## Structural round 5 cleanup dispositions

The frozen round-5 review and completion artifacts are retained under the worker artifact directory `review-fixed-5`. Its raw suggestions and individual severity, take-or-record, and review-again calls are retained in `733-load-timeouts/cleanup-critical5-dispositions.json`. Five local cleanups simplify lock-limit selection, gate dispatch, manifest discovery and budget-test setup. They preserve behavior. The inherited audit-read optimization and declarative mutation-data refactor are recorded for separate work. No additional behavioral review round is triggered by these edits. Final trim, scan, lint, plant and suite evidence remains pending.

## Final trims

One read-only comments round and one prose round ran through `gpt-6.1-sol`, low effort, window 872000, against the fixed review base. Completion, reply shape, classified file coverage and real tool reads were checked before recording this entry. The comments run used Git diffs and direct text reads after sandbox restrictions blocked automated extraction. The single selected comment rewrite preserves both queue ownership and interruption meaning; exact removal of the old and new comment spans confirms unchanged code. No prose proposal was returned. Raw reports are retained beside the structural reviews. Formatting, lint, scan and final restart evidence remain pending.

## Final baseline and remaining restart evidence

The baseline scan at `/Users/ctm/.local/state/codex-mailboxes/tooling/733-plant-load-timeouts/worker/artifacts/final-5/static-pre-lint/receipt.json` was verified against its clean committed tree immediately before this record. Its captured result: 0 findings across 81 scanned targets, with 1 shell PartialParsing warning. The scan is partial, accepted under the approved shell-parser exception; it is not an error-free scan. The unchanged configuration uses `p/default`, metrics off and fixed merge base `302c0d91a77097f1ae66e39bd996253e4bbb17d8` in the disposable clone.

Structural round 5 ends `clean at Critical`: its anti-pattern report has no findings, and the cleanup suggestions are our Nits, with five equivalent local takes and two broader refactors recorded. Focused review remains `ended: fixes changed no behavior`. The final committed-tree plant replay, default-parallel suite, survivor observations and current-main ancestry remain required. Final results and the claim registry will be recorded in external worker receipts before the ready PR. TOOLING retains the merge hold.

## Detector wait margins after the final restart stop

The default-parallel restart on the frozen final-5 tree failed: make test-all exit 2, suite payload check exit 2, action not-run. The retained receipt is `/Users/ctm/.local/state/codex-mailboxes/tooling/733-plant-load-timeouts/worker/artifacts/final-5/suite/receipt.json`. The failed document was `checked-plant-guards-1.md`. Its bounded-capture check had an execution window shorter than the detector wait. Exact inner results were lost when the private fixture cleaned up; the outer diagnostic contained only absent scalar flags. The stop and environment evidence are retained in `/Users/ctm/.local/state/codex-mailboxes/tooling/733-plant-load-timeouts/worker/artifacts/final-5/stop-precis.json`.

TOOLING native000037 and native000038 reopen test-only work on gate 6f62aceb. Keep production allocations and the 300-second document cap. The selected detector wait is 30 seconds, with 15 seconds of cleanup and an unchanged 10-second inner call. The check receives 90 seconds inclusive, giving 60 seconds of execution. Its three checks plus Git fit exactly under the document cap.

The static guard inventories generated Runner/Gate plant checks and compatible manifest check scripts, follows local detector helpers, and reads their explicit waits. It compares each wait with the real allocation factory using a margin of at least two. Unknown wait expressions fail the guard. Inherited pipeline observation also has an explicit independent limit. Unexpected inner results are retained in unique files; assertion text exposes only metadata and the file path.

New source plants restore the old window/wait mismatch, accept an undeclared wait, and print retained output. They join the complete replay. No structural review round is added under the explicit test-only gate. Required focused checks, lint, baseline scan, full replay, exact-head default-parallel suite, load/thermal evidence, survivor observation and ready PR remain pending.

The implementation checklist is [Give plant detectors an explicit execution margin](../plans/done/2026-11-06-733-detector-margins.md). Final evidence will be retained outside the source tree.

## Detector-margin baseline scan

The current pre-lint baseline receipt was verified against its clean committed tree immediately before this record: `/Users/ctm/.local/state/codex-mailboxes/tooling/733-plant-load-timeouts/worker/artifacts/final-6/static-pre-lint/receipt.json`. Its captured result is 0 findings, 87 scanned targets and 1 shell PartialParsing warning. The scan is partial under the approved exception. Final committed-tree evidence remains required.

## Retention fixture metadata contract

The final-6 replay stopped in its first full batch: check exits [0, 1, 1, 0], action not-run. The failed receipt is `/Users/ctm/.local/state/codex-mailboxes/tooling/733-plant-load-timeouts/worker/artifacts/final-6/plants-1/receipt.json`. The older nested-output plant removed the returned metadata file path; the new retention test indexed that path before asserting it existed. Its red phase produced a KeyError alongside the intended failure. This was a test-contract error; its phase timeout flags were false. Later batches and the restart suite did not run. The checked stop report and retained data are in `/Users/ctm/.local/state/codex-mailboxes/tooling/733-plant-load-timeouts/worker/artifacts/final-6/fixture-stop-precis.json`.

Within the existing test-only gate, the retention test asserts the metadata and owned file contract before access. A regression invokes that test with missing metadata and requires an assertion failure without an exception. A new source plant removes the assertion. The older nested-output plant now requires both related named failures and still excludes errors. Targeted replay includes both this older plant and the new metadata plant before the complete fresh replay. Production allocations and verdict reading remain unchanged. Final committed-tree gates remain pending.
