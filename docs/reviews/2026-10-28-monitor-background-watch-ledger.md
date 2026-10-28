# Monitor background watch ledger

## Authorization and baseline

Chris's Inbox go-ahead, 2026-10-27 8:54 PM ET, pick 7 after milestone 2.
TOOLING brief authorizes build through a ready PR; TOOLING merges.
Base: origin/main at 78386666, including milestone 2 merge d6af0680.
Repository is cboone/agent-harness-plugins, not archived and not a fork.
Corepack immutable install passed. Full local review order applies.

## Design and sweep

Extend merge-flow's existing loop with watch-changes. Share polling, backoff,
lifetime, terminal lifecycle and failure handling. Separate read-axis gate
permits observation under a review pause without granting merge permission.
Frozen baseline includes snapshot and latest Copilot review metadata only.
Finite quiet-tick decisions retain a poll bound, so the new wait cannot suppress
review requests or escalation. Pending-read retries retain milestone 2's common
handler and fallback cadence.

The current skill, checkpoint and plugin README own active quiet waits and are
updated. ScheduleWakeup and scheduled-task instructions remain fallbacks.
Codex scheduler/foreground paths remain. Step 8 merge watch already uses a
background command and stays shared. Historical plans/reviews remain records.
Root README is a catalog, with no quiet-wait instructions. Generated mirrors
will be rebuilt from canonical sources.

## Validation and review

Initial validation: new Scrut suite 27/27 and existing merge-flow suite 47/47
passed. ShellCheck and Bash syntax passed. Zero-second lifetime remains an
immediate expiry for existing callers. New baseline parsing requires one JSON
value; whitespace is rejected before GitHub.

## Planted boundaries

Each plant changed the canonical helper after committing the tests. Every
behavior-changing plant caused the corresponding Scrut assertion to fail;
restored the helper after each. No live GitHub calls ran. The first queued/
running plant left the normalized representation unchanged and therefore
changed no behavior; the effective plant included the status in the comparison.

| Plant                                       | Instrument      | Observed | Regression case                          |
| ------------------------------------------- | --------------- | -------- | ---------------------------------------- |
| Suppress completed/failed check event       | New Scrut suite | Failed   | Check completes/fails and legacy context |
| Suppress current-head review event          | New Scrut suite | Failed   | Current-head Copilot review arrives      |
| Suppress head event                         | New Scrut suite | Failed   | Head changes                             |
| Change merged to closed                     | New Scrut suite | Failed   | PR merges                                |
| Change closed to merged                     | New Scrut suite | Failed   | PR closes                                |
| Treat UNKNOWN as material                   | New Scrut suite | Failed   | Running, queued and transient UNKNOWN    |
| Include queued/running status in comparison | New Scrut suite | Failed   | Running, queued and transient UNKNOWN    |
| Advance failure bound by one                | New Scrut suite | Failed   | Failed polls and review failures         |
| Omit successful failure reset               | New Scrut suite | Failed   | Success resets failures                  |
| Advance quiet bound by one                  | New Scrut suite | Failed   | Quiet-poll count and call count          |
| Ignore fixed interval                       | New Scrut suite | Failed   | Fixed cadence                            |
| Remove failure multiplier                   | New Scrut suite | Failed   | Backoff                                  |
| Lower backoff cap to 800                    | New Scrut suite | Failed   | Fifteen-minute cap                       |
| Invert once lifetime comparison             | New Scrut suite | Failed   | Once honors lifetime without a read      |
| Extend blocking lifetime by one             | New Scrut suite | Failed   | Blocking lifetime, second read observed  |
| Remove read-axis gate                       | New Scrut suite | Failed   | Blocked metadata refuses before call     |

Pending: structural review, focused review, trims, baseline Semgrep, lint,
test-all, version check, tidy and PR checks.

## Structural loop, Nit round 1

Snapshot: a9d81eaf945b0a8064284b3e430edae03bfd9ecc, head 339c59d8.
Anti-patterns and report-only simplify ran in parallel through fresh standalone
Codex read-only processes: gpt-6.1-sol, high, 872000-token window,
approval_policy never, web_search disabled, stdin closed. Both exited zero;
outputs passed their schema checks. Anti-patterns reported success, complete
coverage and no unread files. Scope comparison found no lasting changes and no
scope movement. No clean verdict: three Important findings require fixes.

The installed cache changed while the first launch was being prepared:
review-pr-with-codex 2.1.3 and review-anti-patterns 1.1.3 disappeared. Those
launches failed before review, with missing/empty schema errors. Refreshed to
installed 2.1.4 and 1.1.4; the completed reviews above count as round 1.

Each entry records the reviewer's label, severity, disposition and next review.

1. **Boundary arithmetic: the startup poll spends a quiet tick before any wait**
   - Reviewer: `important`.
   - Severity: Important. A remaining one-tick budget immediately requests a
     review without honoring the selected interval; a two-tick post-request
     budget expires after one interval.
   - Take: yes. Preserve immediate material-event detection, but only count an
     unchanged poll after an elapsed cadence interval.
   - Review again: yes, behavior changes. Structural Important round 1 next.
1. **Parallel paths: background quiet counts bypass Copilot's working-state check**
   - Reviewer: `important`.
   - Severity: Important. A queued/running Copilot workflow is working, not a
     quiet tick under step 7a. Imported background counts can cause a redundant
     request or repeated unchanged callbacks while the workflow remains active.
   - Take: yes, pending TOOLING's design call below.
   - Review again: yes, behavior changes. Structural Important round 1 next.
1. **Sibling input forms: leading-zero quiet bounds change arithmetic semantics**
   - Reviewer: `important`.
   - Severity: Important. `010` becomes eight and `08` produces interpreter
     diagnostics instead of enforcing the requested poll bound.
   - Take: yes. Normalize accepted decimal input across the related numeric
     parameters or reject noncanonical representations consistently.
   - Review again: yes, behavior changes. Structural Important round 1 next.
1. **Tests that cannot fail: baseline cases do not assert their no-call guarantee**
   - Reviewer: `nit`.
   - Severity: Nit. Baseline refusal is tested, but moving validation after a
     metadata request would still pass the test's stated absence guarantee.
   - Take: yes, add explicit empty offline-call-counter assertions and plant
     validation after a read.
   - Review again: no for this tests-only edit; the behavior fixes need review.
1. **Docs drift: the repair-loop budget description omits background expiry**
   - Reviewer: `nit`.
   - Severity: Nit. README's overview still describes rounds as the only budget,
     while its new background path has a lifetime bound.
   - Take: yes, qualify the existing overview by mechanism.
   - Review again: no for this docs-only edit.
1. **write-bash-scripts: Checked commands: Centralize failed-read bookkeeping.**
   - Reviewer: `suggestion`.
   - Severity: Nit. PR and review failures duplicate one counter policy.
   - Take: yes, a local helper preserving both early returns and success reset.
   - Review again: no, the refactor preserves behavior.
1. **write-bash-scripts: Naming: Separate review metadata from mergeability values.**
   - Reviewer: `suggestion`.
   - Severity: Nit. One local variable changes from a metadata object to a
     mergeability string.
   - Take: yes, rename the locals without changing comparisons.
   - Review again: no, names preserve behavior.

## Design gate and resume

Stopped before fixes, push or PR. The proposed structural fix extends the
existing watch-changes observation with step 7a's existing current-head Copilot
workflow-status query. Internal queued/in-progress observations reset quiet
counts and stay silent; only elapsed unchanged non-working polls spend the
remaining budget. Keep one shared polling/backoff/lifetime loop and read-axis
gate. Extend the committed offline stub and tests for working-to-quiet
transitions and startup pacing, then plant each new boundary.

TOOLING must decide whether that extension fits the brief or whether finite
review-decision waits should instead retain the fallback path. No fixes have
been applied from this round; all seven takes remain outstanding. The loop
count persists: structural Nit round 1 complete, Important rounds not started;
focused review and trims not started. No recurring-defect stop has occurred.

Additional sweep disposition: docs/reviews/codex-consumption.md records older
measured harness capabilities, not active waiting instructions. The manual
continuation verification plan names monitor-pr 1.4.0 and foreground/scheduler
fallback checks; its quiet ticks remain applicable to those fallback checks.
Neither document is an instruction to keep rearming the new background watch.

## TOOLING design call and fixes

TOOLING relayed the go-ahead in this session: extend watch-changes with the
existing step 7a current-head workflow query under read-axis; no duplicate query
implementation or poller. Queued/in-progress resets the quiet counter silently;
only elapsed non-working quiet polls spend its budget. Continue at structural
Important round 1, retaining the Nit round count.

All seven takes implemented. `copilot-status` and `watch-changes --review-wait`
share `read_copilot_status`; step 7a now invokes that helper. The background
counter is restored with `--quiet-count`, uses the full `--quiet-polls`
threshold, and replaces rather than adds to the retained counter on callback.
The startup poll detects material events but never spends a quiet tick.
Workflow errors other than a missing Copilot workflow count as failed reads.
Accepted numeric spellings are canonical decimals; leading zeros are rejected
across quiet bounds and sibling parameters. Invalid-baseline tests assert an
empty call counter. README names the background lifetime. Failure accounting
is centralized and review/mergeability local variables have distinct names.

Validation after fixes: watch-changes 40/40, existing merge-flow 47/47,
ShellCheck and /bin/bash syntax passed. Mirrors rebuilt. New boundary plants
and structural Important round 1 are next. No push or PR yet.

## Fix-boundary plants and Important round 1 input

All 17 new plants failed their targeted Scrut checks, with the canonical helper
restored after each. Startup counting failed the elapsed-wait assertion;
classifying queued or in-progress as quiet and retaining a working counter
failed the working-to-quiet count assertions. Accepting leading-zero spelling
separately for quiet-polls, quiet-count, failures, merged-reads, started,
interval, failure limit and lifetime failed the rejection tests. Moving a PR
read before baseline validation failed the empty-call-counter assertions.
Widening the integer size limit failed oversized-input rejection. Multiplying
before backoff clamping produced a negative wait and failed the 900-second
assertion. Replacing empty workflow/review output with empty arrays failed the
respective unavailable-read assertions. These tests are committed in
watch-changes.md; plants changed the real helper, not a replica.

Numeric validation also caps canonical bounds at 15 digits, keeping accepted
counters exact in jq and signed Bash arithmetic. Backoff checks the cap before
multiplication. Metadata projections require one JSON value, including empty
successful command output. These close the numeric and read-validation classes
before the next round, without changing the approved workflow design.

Restored validation: new suite 44/44 and merge-flow 47/47 passed; ShellCheck and
Bash syntax passed. Refreshed origin/main to 45b89f1c; the branch merge base is
still 78386666. Structural Important round 1 is next; no review counts reset.

## Structural loop result

Important round 1 completed on snapshot
514d529313a666e1d7639bc66cc7d6c232361644: anti-patterns success, complete coverage,
no unread files and no findings; report-only simplify valid, no findings or
further suggestions. Both standalone read-only Codex runs exited zero and
passed their result checks. Scope/tree comparison was unchanged. Same explicit
model/effort/window as Nit round 1. Mechanical and live integration checks that
read-only reviewers did not run remain caller validation obligations.

Structural loop: one Nit round with seven takes, then one Important round.
End state: clean at Important. No recurrence, downgrade or outstanding take.
Focused review begins at its own Nit round; all five review aspects apply:
code, errors, tests, comments and types (baseline/event/counter invariants).

## Focused loop, Nit round 1

All five aspects ran on the same unchanged scope, in batches of three and two
read-only Codex processes: gpt-6.1-sol/high/872000, explicit CLAUDE.md fallback,
approval_policy never, web_search disabled. Both helper runs exited zero; every
aspect status is valid/ok. The scope comparison found no lasting changes.
Comments reported no findings. Four findings were taken:

1. **write-markdown: Retry handling: Workflow failures never reach the retry limit.**
   - Reviewer: `important`; severity: Important, accepted as labelled.
   - A successful latest-review dispatch reset the shared counter before the
     later workflow error incremented it. Repeated workflow failures could
     therefore keep the fallback alive indefinitely.
   - Take: collect the required workflow result before dispatch and combine it
     with the latest-review result into exactly one review-metadata observation.
     Step 7a consumes that retained result, without a second read/dispatch.
   - Review again: yes, orchestration behavior changes; focused Important round 1.
1. **write-scrut-tests: Behavioral coverage leaves the workflow query scope unchecked.**
   - Reviewer: `important`; severity: Important, accepted as labelled.
   - The old fixture ignored query arguments, allowing a missing Copilot filter
     to pass tests while another workflow masks an active Copilot run.
   - Take: validate repository, branch, workflow, limit and JSON fields in the
     committed fixture. Register/unset the new fixture environment consistently.
   - Review again: no for this tests-only change; other takes require a round.
1. **write-bash-scripts: Checked commands: Baseline validation rejects the documented no-review representation.**
   - Reviewer: `important`; severity: Important, accepted as labelled.
   - The documented projection emitted an all-null object rather than the
     baseline's explicit null representation for an absent review.
   - Take: emit/store null consistently. Test executes the actual documented
     projection against the offline gh fixture and passes it into watch-changes.
   - Review again: yes, executable protocol changes; focused Important round 1.
1. **write-bash-scripts: Checked commands: Preserve the baseline-loading diagnostic.**
   - Reviewer: `suggestion`; severity: Nit. Safe refusal lacked its path/cause.
   - Take: capture jq's stderr and include the baseline path and diagnostic.
     Tests retain the filename and actual missing-file/parse cause.
   - Review again: no additional round for this diagnostic improvement; the
     Important fixes already require the next round.

The new combined-observation test executes the literal documented jq combiner
with successful review metadata and a failed workflow result, then passes the
real dispatcher's counters across two ticks. It verifies the executable
combination contract; live model tool ordering remains a host-integration
obligation, not a claim made by this offline test.

Validation after these fixes: new suite 47/47, ShellCheck passed, mirrors rebuilt.
No severity downgrade, recurring defect or new design gate. New plants and
focused Important round 1 remain next; structural loop stays clean at Important.

## Focused fix plants

All eight new plants failed their intended Scrut assertions: omit repository,
omit branch, select another workflow, change the limit, omit status from JSON,
restore the all-null no-review object, discard the workflow failure in the
literal documented combiner, and discard the baseline-loading cause. Script
plants passed Bash syntax before execution. Original files were restored after
each. Source commands in the skill are executed directly by the projection and
combiner tests, avoiding a duplicate expression in the tests.

Restored validation: watch-changes 47/47 and existing merge-flow 47/47 passed.
Focused Important round 1 is next, with all five aspects retained. The ledger
counts remain structural Nit plus Important 1, focused Nit 1; no recurrence or
downgrade has occurred. There have been 41 effective boundary plants in total.

## Focused Important round 1: recurrence stop

Code, errors and tests completed with valid/ok helper statuses and exit zero.
The scope comparison found no lasting changes or movement. Comments and types
were not launched: the first batch reached the mandatory recurrence stop, so
this round has incomplete aspect coverage and is not a clean result. Settings
remain gpt-6.1-sol/high/872000, read-only, with explicit CLAUDE.md fallback.

1. **write-scrut-tests: Behavioral coverage leaves PR and review query contracts unchecked.**
   - Reviewer: `important`; severity: Important, accepted as labelled.
   - Workflow arguments are now checked, but the same fixture returns the full
     snapshot and paginated review data regardless of PR fields, identity,
     endpoint or pagination flags. Removing statusCheckRollup or --slurp can
     therefore leave tests green while real responses fail or miss reviews.
   - Take: yes, pending TOOLING's structural decision. This is another instance
     of the query-contract defect class taken in focused Nit round 1.
   - Review again: yes after the fixture correction. Stop now for recurrence;
     no fix was applied and no further aspect or round was started.
1. **write-bash-scripts: Polling cadence: Explicit review waits use the idle interval.**
   - Reviewer: `important`; severity: Important, accepted as labelled.
   - A current-head notice is still a current-head review in the cadence test,
     so --review-wait uses 1200 seconds instead of the documented 300 seconds
     while awaiting its replacement, unless checks are running or overridden.
   - Take: yes, pending the recurrence decision. Give explicit review_wait the
     300-second cadence after the 120-second running-check condition, while
     retaining the fixed override. Add a current-head-notice case and plant it.
   - Review again: yes, behavior changes. No fix was applied at this stop.

Errors returned no findings. There is no severity downgrade. End state:
stopped: recurring defect. Focused counts persist: Nit round 1 completed;
Important round 1 stopped after three of five aspects. Following behavior
fixes, the next full focused round is Important round 2, without resetting the
budget. Structural remains clean at Important.

## Proposed structural fixture correction

Replace permissive per-command response matching with one request-contract
validation/response-shaping layer for every supported offline gh operation.
Validate repository/PR identity, endpoint, supported flags and flag values for
pr view, api reviews and run list before selecting a fixture response. Honor
pr view's requested JSON fields, reject unsupported input, and require or
faithfully shape review pagination/slurp responses. Add two-page review input
with the current-head review on the later page. Test and plant missing/wrong
fields, identities, endpoints and pagination flags across all supported calls,
not only the workflow query. Keep the current offline refusal guard.

This extends the committed fixture rather than adding another helper or live
GitHub path. Combine it with the accepted notice-cadence correction, then run
the remaining local process from the persisted round count. TOOLING's decision
is required by the project's recurrence rule before those edits.

At this stop, last restored tests are watch-changes 47/47 and merge-flow 47/47;
41 effective plants are recorded. Trims, baseline Semgrep, final lint/test-all,
version check, tidy, push, PR and CI remain unrun. No background process remains.

## TOOLING recurrence decision and whole-contract correction

TOOLING relayed the go-ahead in this session for both fixes: one strict
request-validation/response-shaping layer for every supported gh call in the
existing fixture, plus the explicit review-wait cadence correction. The next
review is focused Important round 2, all five aspects, with counts retained.
A further query-contract instance remains a mandatory stop.

The fixture now parses every supported request before response selection,
validates PR/repository identity, workflow selection, endpoint, flags and JSON
field names, refuses duplicate/unknown input, and projects only requested PR
or workflow fields. Review responses require both paginate and slurp. Fault
responses remain intentional data for malformed/failed-read cases. All gh
requests are counted separately from the PR response-sequence index, so no-call
assertions cover API/workflow requests too. Direct API/workflow calls can start
at the first fixture row without a preceding PR view.

Coverage adds later-page current-head reviews, partial-field response shaping,
merge commits, merge-watch decisions, invalid request matrices for every
supported operation and unsupported operations. Notice review waits now select
300 seconds after the running-check 120-second priority; explicit interval
overrides still win, with assertions for all three paths.

Before plants: watch-changes 59/59, ShellCheck passed. New plants will run
against actual committed source in disposable shared clones, not a separate
implementation. No real GitHub path or new poller was added.

## Whole-contract and cadence plants

Three disposable shared clones of the committed source each passed the full
59-case positive control before planting. Across them, all 36 plants produced
Scrut assertion failures, not syntax failures. Each cloned script/fixture was
restored; git diff --quiet confirmed restoration in every clone. Canonical
source was unchanged throughout. Artifacts are in
/tmp/637-contract-plants.EV9fbQ, with one named log per plant and three result
lists. The effective plant total is now 77.

Planted each requested PR field omission (state, decision, head, merge commit,
checks, mergeability and merge status), omitted JSON output, an unsupported
field, wrong PR number and repository. Planted review endpoint/repository/PR
changes and missing paginate/slurp. Planted workflow repository/branch omissions,
wrong workflow/limit/field and omissions of headSha, status or JSON output.
Fixture plants weakened field projection, PR/workflow/review identity validation,
unsupported-option rejection, duplicate value/pagination/field rejection and
unsupported-field rejection. All were detected by the direct contract matrices
or consumer behavior assertions. Cadence plants removed explicit review pacing,
running-check priority and interval-override priority; each corresponding
assertion failed. The merge-commit omission specifically failed the commit
value assertion; field-projection weakening failed both partial-response cases;
missing slurp failed the later-page review case among its affected assertions.

Initial mutation attempts were interrupted because the large-number backoff
probe retained too many possible failures under metadata omission. A proposed
test lifetime changed its expected wait by clamping it and failed the clone
controls. The final test instead allows two failures above its initial count,
preserving the 900-second backoff assertion while bounding planted failures.
The invalid/interrupted attempts are not counted as passing plants.

Restored checks: watch-changes 59/59, merge-flow 47/47, ShellCheck and Bash
syntax passed. Focused Important round 2 is next, with code/errors/tests then
comments/types on one unchanged scope. Structural remains clean at Important;
focused counts remain Nit 1, Important 1 recurrence stop, then Important 2.

## Focused loop result

Important round 2 completed all five aspects on one unchanged scope. Both
helper batches exited zero with valid/ok results; final scope comparison found
no lasting changes. Code, errors, comments and types reported no findings.
Tests reported one below-threshold item:

- **write-scrut-tests: Behavioral coverage omits unchanged completed-check baselines.**
  Reviewer: `suggestion`; severity: Nit, a missing regression case rather than
  an observed implementation defect. Take: yes, required coverage for this
  change's own quiet boundary. Add completed CheckRun and legacy-context
  baselines, unchanged/reordered quiet results, and changed-conclusion events.
  Review again: no, tests only; product behavior remains unchanged.

Those three cases pass. Plants discarding the completed baseline, removing
ordering and ignoring conclusions each failed the intended new assertion.
Restored suite: 62/62. Effective plant total: 80. The test refusal-prefix check
now uses POSIX grep instead of introducing a new ripgrep dependency in CI.

Focused counts: Nit round 1 with four takes, Important round 1 stopped on the
query-contract recurrence, then Important round 2 with no Important/Critical
findings. TOOLING's structural decision was applied and validated; no further
query-contract instance was found. End state: clean at Important.
Structural end state also remains clean at Important.

Next: one trim-comments and trim-text dry run each, using fresh read-only Codex
at gpt-6.1-sol/low/872000. Then baseline Semgrep, final lint/test-all, versions,
tidy and the ready PR with green CI. No further approval gate is pending.

## Trims

One trim-comments and one trim-text dry run completed through fresh standalone
Codex: gpt-6.1-sol/low/872000, read-only, approval never and web search disabled.
Both exited zero and returned the required complete file lists and full proposal
tables. Scope comparison found no lasting changes from the dry runs.

Applied all four checked proposals: remove a redundant shared-caller comment,
state the fixture's purpose directly, shorten the no-double-count sentence,
and make checkpoint retention imperative. Commands, conditions, counters and
meaning are unchanged. Rebuilt mirrors. Scoped Prettier, Markdown lint,
ShellCheck, shfmt and the 62-case watch suite passed after applying the trims.
No additional review round is required for comment/prose-only changes.

Next: the required Semgrep auto baseline scan in a disposable shared clone,
without disabling metrics; then final lint and all project checks.

## Semgrep baseline gate

Stopped before final lint/test-all, version check, tidy, push or PR. Ran the
required command against head 1c2a19df in disposable shared clone
/tmp/637-semgrep.ihJdLW:

```bash
SEMGREP_REPO_NAME=cboone/agent-harness-plugins semgrep scan --config auto \
  --baseline-commit 78386666cdce00aa7efd09eff6cc9252335f034d --json
```

Metrics were not disabled. Semgrep 1.180.0 exited zero and reported 0 findings,
165 rules and 9 scanned targets, but its JSON contains one PartialParsing
warning with three spans in merge-flow: line 315's compact case statement,
line 488's division comparison, and line 496's nested elapsed-time arithmetic.
Parsed coverage was approximately 99.9 percent. This is incomplete validation,
not a clean scan. The committed report is
2026-10-28-monitor-background-watch-semgrep.json in this directory. Full logs,
status and raw JSON remain under /tmp/637-review.DKA6DN/semgrep*.

The project's local-review rule says a baseline scan that cannot run requires
a stop and decision. Partial parsing prevents that scan from validating all
changed code, so the gate remains closed; no error was suppressed and no tool
was installed or upgraded.

Proposed syntax-only correction: expand the one-line case into normal multiline
Bash and rerun the same baseline command. If the arithmetic spans persist, use
an equivalent [[ integer -gt "$((900 / failures))" ]] comparison and separate
elapsed = SECONDS - started from remaining = lifetime - elapsed. Preserve the
backoff/lifetime semantics and Bash 3.2 compatibility, rebuild mirrors, run
relevant checks/tests and rescan. No configuration or metrics override is
proposed. TOOLING's decision is needed before applying this parser-compatibility
correction or proceeding past the baseline gate.

At the stop: structural and focused loops clean at Important, trims complete,
62/62 affected Scrut tests passed, 80 effective plants recorded. Final lint,
make test-all, versions, tidy, push, PR and CI remain unrun. No background
command remains; the scan clone and artifacts are retained for the decision.

## Parser-compatibility go-ahead and completed baseline

TOOLING authorized the syntax-only correction and continuation through the
remaining checks and ready PR, with no new review round. Expanding the case
statement cleared that span; the same scan still reported only the arithmetic
spans. Applied the conditionally authorized integer comparison and separate
elapsed/remaining arithmetic, preserving behavior and Bash 3.2 compatibility.
Rebuilt mirrors; Bash syntax and ShellCheck passed.

Added a delayed-read fixture assertion so lifetime arithmetic is tested after
nonzero polling time. The control suite passed 63/63. Six plants removed queued
or running detection, disabled or forced backoff clamping, reversed elapsed
arithmetic and added rather than deducted elapsed time. All failed the intended
assertions; originals restored. Affected suites then passed 63/63 and 47/47.
Effective plant total: 86. No behavior changed in the parser-compatible forms,
so review counts remain unchanged as TOOLING directed.

Final scan from committed head f2dd8c73 in a fresh disposable shared clone used
the same auto config, actual baseline 78386666 and repo-name environment. It
exited zero: 0 findings, 0 errors, 165 rules, 10 targets, approximately 100 percent
parsed. Metrics stayed enabled. The committed Semgrep JSON now holds this final
clean report; earlier partial reports and full scan logs remain in the external
review artifacts, and their diagnostic evidence is recorded above.

Removed all four recorded scan clones after their commands completed, as
TOOLING requested. No scan process remains. The baseline gate is satisfied.
Next: lint-and-fix --no-push, make test-all, versions, exact-tree signed tidy,
push, ready PR and green CI. No approval question remains open.

## Final lint and project validation

Invoked lint-and-fix --no-push with the project commands. Formatting had already
been applied to changed non-snapshot files; bulk Markdown writers stayed out of
protected Scrut snapshots. The required check commands ran, with no skipped or
unavailable tool. Two own-change issues were fixed manually: equivalent AWK
fence patterns avoid Prettier inflating Scrut fences, and the recurring-session
loop prohibition is plain text so cross-reference validation does not mistake
a harness command for a repository skill. Rebuilt the mirror.

Final verification ran `SCRUT_JOBS=4 make test-all` and exited zero: Markdown
lint, Prettier, ShellCheck, shfmt, actionlint, JSON/plugin validation and all
38 Scrut documents passed, including watch-changes 63/63 and merge-flow 47/47.
No product behavior changed in the lint fixes. Lint status: success; unresolved
or skipped: none. The fixes and this record are committed without pushing.

Version check: all clear against actual origin/main merge base 78386666.
Only monitor-pr changed: 3.3.0 to 3.4.0, appropriate for the new capability.
All 60 marketplace registrations match plugin directories; canonical versions,
present Codex manifests and generated versions match, with no marketplace
version duplication. No other plugin needs a bump.

PR destination is public cboone/agent-harness-plugins, not archived or a fork;
validated origin fetch/push identities are the same. Base is explicitly main.
Only issue 637 is in the closing list. User instructions select sentence-case
PR titles; no title-lint workflow was found. The branch has no remote head, so
the required tidy will not rewrite pushed history. Authorization through a
ready PR remains open; TOOLING merges and the worker will stop after green CI.

## Pre-publication handoff

All required local verification is complete: make test-all passed 38 documents,
1,551 cases, zero failures and zero skips. The new watch suite passed 63/63.
Both review loops ended clean at Important, trims ran once each, all 86 effective
plants were detected, Semgrep's baseline is complete with zero findings/errors,
and version/catalog verification is clear. No open finding or approval gate
remains for the authorized ready PR.

The implementation plan moves to done. The unpublished branch is rebuilt as
logical signed feature, test and documentation commits, retaining a pre-tidy
backup. Before push, the complete committed tree must compare equal to that
backup; the result and final PR/CI status are recorded in the workstream handoff.
No source or test behavior is changed by the tidy. TOOLING owns the merge.
