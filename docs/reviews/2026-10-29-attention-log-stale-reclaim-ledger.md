# Attention-log stale reclaim ledger

## Scope and design

Base: `origin/main`, merge base recorded before review. Issue:
[stale reclaim](https://github.com/cboone/agent-harness-plugins/issues/673).
The committed plan records the prior-art survey. Automatic stale removal is
replaced by reporting and fail-closed session updates or unrotated appends.
Stopping all writers is required before manual recovery. Shared helpers and
hook files are unchanged. Attention-log patch version: 1.0.2 to 1.0.3.

## Plants

| Planted defect                                 | Instrument                          | Actual result                       | Regression coverage                                                |
| ---------------------------------------------- | ----------------------------------- | ----------------------------------- | ------------------------------------------------------------------ |
| Original stopped-PID read/remove reclaim       | Successor handoff fixture, session  | Exit 1: successor ownership removed | Stale observers cannot remove a live successor                     |
| Original PID-less age/remove reclaim           | Successor handoff fixture, pidless  | Exit 1: successor ownership removed | Stale observers cannot remove a live successor                     |
| Original rotation age/remove reclaim           | Successor handoff fixture, rotation | Exit 1: successor ownership removed | Stale observers cannot remove a live successor                     |
| Restore ignored failure in `open_state`        | Opening guard case                  | Exit 1: markerless event            | Opening hooks skip a stale session                                 |
| Restore ignored notification failure           | Opening guard case                  | Exit 1: markerless event            | Opening hooks skip a stale session                                 |
| Suppress lock-directory preparation diagnostic | Preparation guard case              | Exit 1: missing diagnostic          | Lock-directory preparation failures explain skipped opening events |

## Validation and review

- Merge base: `7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`.
- System Bash 3.2.57: 64 attention-log cases passed, zero failures or skips.
- All three original reclaim plants failed at the ownership assertion. Removing
  that assertion while retaining each plant still failed at the protected-state
  or rotation assertion. Restoring production and fixture files passed all
  three direct handoffs. No plant remains in the tree.
- ShellCheck and shfmt passed on the changed script and committed fixture.
- `make build` passed. Locked dependencies restored with network/scripts off.

Review is pending. No clean review result is claimed before completion checks.
The full local review order applies. The brief requires stopping rather than
falling back on a Codex code-mode host-negotiation timeout.

## Stop: reviewer unavailable

The first structural Nit round is incomplete. Anti-patterns and report-only
simplify each started a fresh `codex exec` run using `gpt-6.1-sol`, `high`,
`872000`, read-only sandbox, approvals never and web search disabled. Simplify
was report-only with all four cleanup angles requested inline. Neither produced
validated review output or findings; neither is clean at any threshold.

Both logs contain `timed out negotiating with the code-mode host`, at
2026-10-29 17:44:57 EDT and 17:44:58 EDT respectively. The brief explicitly
requires stopping on this error without fallback. Both processes were
interrupted through their recorded exec sessions and observed exiting 1.
The scope comparison found no lasting changes: tree
`ebc52fcb0031e5120bdef60236a9f4ce6fa4492b` remained unchanged, with no changed or
outside-scope paths.

Before model startup, initial CLI invocations from the scratch directory were
refused because that directory was not trusted. Corrected the working directory
to the repository without a skip or override flag. Those refused invocations
produced no review and consumed no review round. Used installed helper copies
for prompt rendering after the repository copy correctly refused to review
itself.

Remaining: successful structural review, focused aspect review, trims,
baseline Semgrep in a disposable clone, final lint-and-fix, version validation,
`make test-all`, tidy, push and a ready PR. None of these is claimed complete.
No push, PR, merge, configuration change or software installation occurred.

Resume through TOOLING after the reviewer failure is cleared. Capture a fresh
scope; retain this failed first round rather than presenting it as clean.
The implementation and regression plants are preserved in signed commits.
Logs and captures are retained in `/tmp/attention-673.4rHce3/` for the handoff.

## Resume and structural Nit retry

TOOLING relayed the ramp restart go-ahead on 2026-10-30. Issue `in progress`
was restored. The Oct 29 failed round remains above. Both fresh read-only
`codex exec` reviewers used `gpt-6.1-sol`, `high`, `872000`, approvals never and
web search disabled. Both exited zero and passed schema/shape validation.
Simplify covered reuse, simplification, efficiency and altitude inline, with
no findings or edits. Anti-patterns covered all seven canonical changed files
and excluded only three generated mirror paths. The parent confirmed no PR
body applied. No lasting scope changes were found.

Findings, with separate disposition calls:

- Reviewer's label: `important`, "Parallel paths: state-opening hooks ignore
  the stale-lock failure". Own severity: Important; a stale owner can leave a
  newly logged request without a marker, making later clearing impossible.
  Take: state-opening paths with a usable session must return when acquisition
  fails; retain sessionless event recording. Review again: yes, behavior changes.
  Regression coverage includes request, prompt notification, API stop and refusal
  stop, with stopped-PID and aged PID-less owners, plus recovery and clearing.
- Reviewer's label: `nit`, "Docs drift: the README still promises automatic
  stale-lock recovery". Own severity: Nit; published recovery instructions
  contradict the changed policy. Take: update that one known-limits paragraph.
  TOOLING explicitly approved this scope extension at 15:42 EDT on 2026-10-30.
  Review again: no for this documentation edit alone.

The structural loop advances to Important after the behavior fix and plants.
The completed Nit round is not clean; the failed earlier attempt remains
incomplete. Fresh captures and reviewer outputs are retained under
`/tmp/attention-673-resume.xcJqj0/structural/`.

The fix passed all 66 attention-log cases on Bash 3.2.57. A focused document
extracted from the committed setup and opening-guard cases passed three cases.
Two independent production plants restored the old `open_state` failure
suppression and the old notification condition. Each focused run failed the
stale-opening case with exit 1 because a markerless event appeared; the other
two cases passed. The restored focused run passed all three. No plants remain.
These tests now guard the Important finding; they change behavior and justify
one structural Important round. The README-only edit consumes no extra round.

## Structural Important round

Anti-patterns and report-only simplify each exited zero, produced nonempty
validated JSON and found no findings. Anti-patterns reported complete coverage;
simplify completed all four cleanup angles inline. The unchanged-scope check
passed, including normalized and raw content identity. The structural loop ended
**clean at Important**, after the incomplete Oct 29 attempt and one completed
Nit round that took an Important fix and a Nit documentation correction.
No recurring defect was found. Settings remained read-only
`gpt-6.1-sol` / `high` / `872000`, approvals never, web search disabled.

A repository validator then reported the new fixture's direct retained stderr
capture. Replaced that test-only capture with `capture_child`, including the
background successor's exec-log and wait-log pairing. `bin/check-fixture-environments`
and ShellCheck passed after the change. This is test-harness cleanup, with no
production behavior edit and no additional structural round. The next focused
review includes the corrected fixture. Attention-log checks are rerun below.

After the capture cleanup, all 66 attention-log cases passed again. The three
original reclaim plants were rerun against the corrected fixture: all failed
with live-successor removal, and restored direct handoffs all passed. Fixture
validation, ShellCheck and formatting pass. Production code was restored exactly.

## Focused Nit round

Four parallel read-only `codex exec` aspects (`code`, `errors`, `tests`,
`comments`) used `gpt-6.1-sol` / `high` / `872000`, approvals never and web
search disabled. All exited zero and passed helper validation. Types was
inapplicable because no type or schema changed. Scope comparison found no
lasting changes. Code, tests and comments reported no findings.

- Reviewer's label: `important`, "write-bash-scripts: Errors to stderr:
  Opening hooks silently suppress lock-directory failures."
  Own severity: Important; the fail-closed guard can now discard an opening
  event without explaining that directory preparation failed. Take: retain
  fail-closed behavior and report preparation failure with its path, original
  filesystem error, skipped operation and permission/storage guidance. Tests
  cover request, notification and API-stop failures, then repair and recording.
  Review again: yes, diagnostics change behavior. This is a missing-diagnostic
  class, distinct from the markerless-event defect fixed in structural review.

The focused loop advances to its first Important round after the fix and plant.
The completed Nit round is not clean. Its results remain at
`/tmp/attention-673-resume.xcJqj0/focused/`.

The diagnostic fix passed all 67 attention-log cases on system Bash 3.2.57.
The extracted preparation-guard document passed both cases before the plant.
Restoring the old silent mkdir failure made its diagnostic assertion fail with
exit 1; the setup case passed. Restoring production code passed both cases again.
No plant remains. The behavior fix is committed at `8b76a2d7`.

## Focused first Important round and class closure

All four aspect runs exited zero and validated; code, tests and comments found
none. The unchanged-scope comparison passed. Errors reported:

- Reviewer's label: `important`, "write-bash-scripts: Errors to stderr:
  Opening hooks silently discard events after lock retries expire."
  Own severity: Important; a live holder can exhaust the wait budget and an
  opening hook then skips its event without a diagnostic. Take: yes, at the
  active threshold. Review again: yes, diagnostics change behavior.

The loop **stopped: recurring defect** because this is the same missing-diagnostic
class as the preparation failure. No further production edit occurred before
TOOLING's decision. At 16:00 EDT on 2026-10-30, TOOLING chose class closure:
every `lock_session` failure exit must explain the skipped update, with a
deterministic test and plant for each exit. Keep bounded waiting, fail-closed
returns and ownership rules; use the existing reporter, no helper or hook edits.
The focused loop resumes at its second Important round, retaining its count.

The failure-exit contract is now checked as a whole:

| Failure exit | Diagnostic source                                                | Deterministic scenario                |
| ------------ | ---------------------------------------------------------------- | ------------------------------------- |
| Preparation  | Session reporter with original filesystem error                  | Unwritable sessions parent            |
| Reservation  | Existing owner-file helper diagnostic                            | Unwritable prepared lock directory    |
| PID write    | Session reporter with original write error                       | Committed write-failure injection     |
| Stale owner  | Session reporter and offline recovery guidance                   | Stopped PID and aged PID-less owners  |
| Exhaustion   | Session reporter, attempts, observed owner and recovery guidance | Live parent PID, committed sleep stub |

PID-write diagnostics now include the owner path and skipped update explicitly.
The added exhaustion diagnostic leaves the 101 attempts and 100 sleeps intact.
No recovery, release, hook registration or configuration behavior changed.

Class-closure validation: all 68 attention-log cases passed on Bash 3.2.57.
The focused contract document passed both cases before planting and after
restoration. Each planted diagnostic omission failed the contract case with
exit 1. Repeating each plant after removing the generic diagnostic assertion,
then after removing the specific-explanation assertion, still failed. All 15
negative runs detected the planted omission. Every production mutation parsed
under system Bash before execution. No plant remains.

| Planted defect                     | Instrument            | Actual result                              | Regression coverage                                    |
| ---------------------------------- | --------------------- | ------------------------------------------ | ------------------------------------------------------ |
| Omit preparation diagnostic        | Failure-exit contract | Exit 1, also with either assertion removed | Every session-lock failure explains the skipped update |
| Suppress reservation helper stderr | Failure-exit contract | Exit 1, also with either assertion removed | Every session-lock failure explains the skipped update |
| Omit PID-write diagnostic          | Failure-exit contract | Exit 1, also with either assertion removed | Every session-lock failure explains the skipped update |
| Omit stale-owner diagnostic        | Failure-exit contract | Exit 1, also with either assertion removed | Every session-lock failure explains the skipped update |
| Omit exhaustion diagnostic         | Failure-exit contract | Exit 1, also with either assertion removed | Every session-lock failure explains the skipped update |

## Focused second Important round

Code, errors, tests and comments each exited zero, returned nonempty validated
JSON and reported no findings. The before/after scope comparison found no
lasting changes, including raw bytes. Settings remained four parallel read-only
`gpt-6.1-sol` / `high` / `872000` runs, approvals never and web search disabled.
Types remained inapplicable. No simplify editing stage ran.

The focused loop ended **clean at Important**: one Nit round, two Important
rounds, with the first Important round stopped for recurrence and resumed only
after TOOLING's recorded class-closure decision. Counts were retained. No further
correctness round is required because the second Important round took no finding.

## Trims

One read-only `trim-comments` run and one read-only `trim-text` run used
`gpt-6.1-sol` / `low` / `872000`, approvals never and web search disabled.
Both exited zero with complete classification lists and valid dry-run replies.
Comments proposed no changes. Text proposed two local rewrites: active voice
for aged rotation ownership in the README, and removal of design narration in
the plan. Both were accepted after checking meaning and changed-unit scope.
All other units were kept; no factual corrections or cut material were flagged.
No code or fixture behavior changed, so no correctness round was added.

## Baseline Semgrep and version check

Baseline scan ran at `21d2f9c3` in disposable shared clone
`/tmp/attention-673-resume.xcJqj0/semgrep-repo`, with
`SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, config `auto`, baseline
`7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71` and JSON output. Exit 0: 54 rules,
6 targets, 0 findings, approximately 35.4% parsed lines. It was a real baseline
scan restricted to changed files. Six changed paths were unscanned under ignore
patterns: four generated dist paths and the two test paths.

One parsing warning covers Bash in `plugins/attention-log/scripts/attention-log`,
lines 10 through 808. No non-shell parse error was reported. This is substantial
coverage loss, not a fully parsed or error-free scan. Under the brief's explicit
shell-only exception, this completed baseline scan counts with that limitation
recorded and passing ShellCheck on the production script and race fixture.
Results, log and coverage JSON are retained at the scratch root.

The `check-versions` workflow compared the branch with its actual origin/main
merge base. Only attention-log changed: 1.0.2 to 1.0.3, a patch bug fix. Claude
and Codex manifests match both at the base and current head. Marketplace coverage
and version ownership passed for all 60 registered plugins; metadata and catalog
entries carry no duplicated versions. Full repository validation follows.

## Final-check contract correction

The first `make test-all` completed all 52 documents and failed only the
owner-call contract's current-tree case: it expected nine literal calls and
found eight. All other cases, including attention-log and the known notify
rollout case, passed. Removing rotation's second acquire removed one legitimate
call; the count fixture still described the previous reclaim path.

The audit confirms eight checked, unredirected calls: attention-log has reserve
and release for rotation and for sessions (four), workmux resource claims has
one reserve and one release (two), and bugs-gather has one reserve and one
release (two). Updated only the test fixture's expected count and its Scrut
expectation. Added valid-Bash negative cases for an additional checked call and
a missing checked call: each is rejected by count alone, without relying on
an unchecked-call diagnostic. Existing redirect, capture and ignored-status
plants still fail their guards. All seven owner-call contract cases pass.

This is a test-only correction for the removed reclaim call, with no production
behavior change and no additional correctness review round. The full required
checks are rerun; the first failed run is not reported as a pass.

The disposable clone was refreshed to `6045336d` and the same baseline scan was
rerun after the test-contract correction. Exit 0: 54 rules, 6 targets, 0 findings,
approximately 37.6% parsed lines and 8 ignored changed paths (four dist mirrors
and four test paths). The sole parsing warning remains Bash lines 10 through 808
of attention-log. No non-shell parse error was reported. ShellCheck passes on
all changed Bash files, including the updated test-contract fixture. This is
the final baseline scan; its coverage limitation remains explicit.

Origin was fetched again before publication. The merge base remains
`7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`, and origin/main still has
attention-log 1.0.2, so the 1.0.3 patch remains forward and unconflicted in version.

## Final validation and publication handoff

The final `make test-all` exited zero: 52 documents, 1830 cases passed, zero
failures and zero skips. Markdownlint, Prettier, ShellCheck, shfmt, actionlint,
JSON, fixture-environment and plugin validation all passed. The final notify
rollout document passed locally; its known CI flake remains report-only.

`lint-and-fix --no-push` completed through the project commands. Scoped Prettier
and shfmt fixers made no code edits; Markdownlint stayed check-only because
Scrut files and generated mirrors cannot be rewritten by a broad fixer. All
required check commands ran. This docs-only final record receives Markdown
checks; production and test code remain exactly as the passing full run.

Publication uses the ready-PR go-ahead. The completed plan is under
`docs/plans/done/`. Tidy requires a pre-tidy backup, signed logical commits and
an exact-tree comparison before push. The resulting head, comparison result
and PR URL are reported to TOOLING. Merge stays with TOOLING and waits for
Chris (he/him)'s hook review because the plugin version bump republishes hooks.
No hook file, user configuration, software installation or activation changed.
