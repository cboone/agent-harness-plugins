# Monitor PR client mode ledger

## Authority and scope

The supplied worker brief authorizes build, local review, push and a ready PR on
`feat/monitor-pr-client-mode`, profile `normal-max-default`. TOOLING merges.
Origin is `cboone/agent-harness-plugins`, unarchived and not a fork. The fixed
merge base is `41be42039adb83f0f509bfba15eb3ebf7d954e16`.

TOOLING granted the full-suite lock in mailbox sequence 000001, written
20261102T165354Z: take it after reviews, trims and Semgrep; run once with
`SCRUT_JOBS=2`; release and report. A `pmset -g therm` warning requires holding
the run and reporting to TOOLING. The lock has not yet been acquired.

## Structural loop

Round 1: Nit. Fresh read-only Codex contexts, `gpt-6.1-sol`, `high`, 872000-token
window. Anti-patterns and report-only simplify ran in parallel. Both completed
with nonempty JSON, exit zero and full canonical coverage; no lasting tree
changes. Simplify covered all four cleanup angles inline in its report-only run.
Raw results are in the adjacent structural-round-1 JSON.

| Finding                                    | Reviewer label | Assessed severity                                                                              | Take or record                                                                                              | Review again                         |
| ------------------------------------------ | -------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| Validate live authority for every mutation | important      | Important: a reply could publish after the approved head changed, or resolution after closure. | Take: fresh OPEN/head check immediately before reply and resolution, including between combined operations. | Yes, changes behavior.               |
| Isolate the saved-head mismatch test       | nit            | Nit: the test had independent invalid fields that obscured its intended boundary.              | Take: supply OPEN and an authorized review ID; plant removal of only the head comparison.                   | Tests only; no separate advancement. |
| Read resolution metadata in one projection | suggestion     | Nit: redundant parsing and process starts.                                                     | Take: shared checked target projection, reused by fix and live-context checks.                              | No, preserves behavior.              |
| Consolidate fixture state rewrites         | suggestion     | Nit: repeated file transport obscures test variants.                                           | Take: one checked fixture-local rewrite function.                                                           | No, preserves behavior.              |

Round 2: Important. Both reviewers completed with exit zero, full canonical
coverage, no findings and no lasting tree changes. No recurrence was reported.
The structural loop ended **clean at Important**. General Codex review, trims
and Semgrep follow under the same worker go-ahead.

## Tests and plants

Initial affected dispatch, merge-flow, watch, ancestry, summary and thread-helper
documents passed: 62, 48, 64, 12, 18 and 66 cases respectively. Error-output-guard
passed 102 cases. The initial environment-isolation invocation used `make -s`,
which suppressed nested command echoes and caused three snapshot mismatches;
the normal-command rerun passed all 51 cases. No snapshot was changed for that
invocation error. No full suite has run.

The expanded client document passes 23 cases, including positive reply-only,
resolve-only and combined operations; unapproved rounds; no-fix and pause;
missing fix proof; unrelated fixing commit; changed and closed PR context;
changes between reply and resolution; and wrong-review approval reuse. All gh
calls use committed stubs and verify PATH before execution.

| Plant in an isolated shared clone | Instrument            | Observed result                                                            | Regression case                   |
| --------------------------------- | --------------------- | -------------------------------------------------------------------------- | --------------------------------- |
| Remove fix-ancestry rejection     | Client Scrut document | Intended case failed and an unrelated commit was resolved; restore passed. | Fixing commit outside the PR head |
| Remove remote-head rejection      | Client Scrut document | Intended case failed and the stale operation wrote; restore passed.        | Remote head change                |
| Remove owner pause                | Client Scrut document | Intended case failed and body intake ran for cboone; restore passed.       | Independent cboone pause          |

These three plants ran against the initial committed implementation. Four more
plants against the reviewed fix removed reply validation, resolution validation,
the OPEN-state check and the saved-head comparison individually. Each failed its
intended Scrut case; the restored 23-case document passed. The saved-head plant
specifically proves the corrected test's sensitivity. Raw initial plant evidence remains in the recorded
`/tmp/monitor-client-plants-path` capture. No live client PR was read or changed.

## General Codex loop

Round 1: Nit, five aspects (`code`, `errors`, `tests`, `comments`, `types`), fresh
read-only Codex, `gpt-6.1-sol`, `high`, 872000-token window. All aspects passed
schema and completion checks, with no lasting tree changes. The repository copy
of codex-aspects refused to run before launching any aspect; the installed,
byte-identical helper then ran the review. No failed aspect was retried.

| Finding                                                 | Reviewer label                             | Assessed severity                                                                                       | Take or record                                                                                                                                                                              | Review again                                                   |
| ------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Bind each actual thread to approval                     | important, independently in code and types | Important: a saved authorized review could be paired with a different thread or PR.                     | Take: bind approval to repository; query the actual thread before every mutation and verify its repository, PR, review, unresolved state and Copilot opener alongside live OPEN/head state. | Yes, changes behavior.                                         |
| Cover automatic repair and synchronization restrictions | important, tests                           | Important: the new authority boundaries lacked regression evidence against unintended automatic writes. | Take: exercise DIRTY/BEHIND and failed-check candidates with and without round authority.                                                                                                   | Tests only.                                                    |
| Cover incomplete or mismatched approvals                | important, tests                           | Important: permission evidence and PR scope lacked isolated negative tests.                             | Take: missing/empty/blank authority and mismatched PR/repository cases, with zero authentication calls; reject whitespace-only authority.                                                   | Tests plus the whitespace validity correction change behavior. |

Code and types report the same mechanism and are deduplicated. Resource ownership
is distinct from the earlier structural finding about temporal freshness. No
reviewer label was downgraded. Errors and comments reported no findings.

GitHub schema introspection confirmed the query fields before implementation:
`PullRequestReviewThread` exposes `pullRequest` and `comments`; a comment exposes
`pullRequestReview`; the review exposes `fullDatabaseId` as BigInt. The helper
aliases that field to `reviewId` and accepts its string or numeric representation.
Only public schema metadata was read; no client PR was accessed. GraphQL and
transport errors preserve diagnostics and block mutation.

The expanded client document passes 34 cases. In addition to earlier boundaries,
it covers actual thread repository/PR/review mismatch, human or resolved threads,
missing or wrong node identity/type, BigInt representations, the Actions opener,
API errors, repair/sync restrictions and incomplete approval records. A no-fix
reply is allowed under authority while the thread stays open. Each mutation uses
one frozen, validated watch-state snapshot; resolution proof and the live target
check use that same head. Combined operations check proof before the reply and
again before resolution. Round 2
will run at Important because round 1 changed behavior. Trims, final baseline
Semgrep and the full suite remain pending.

Round 2: Important. All five aspects completed with schema-valid, nonempty
results, zero process exits and no lasting tree changes. Code, errors, tests and
types reported no findings. Comments reported one `suggestion`, assessed Nit:
`write-bash-scripts: Function comments: Document the new reply-validation arguments.`
Take: document the new validation-kind and resolution-reason arguments, which
belong to the change's own behavior. Comment-only; no further round. The general
loop ended **clean at Important**, with no recurring defect reported.

## Final defect sensitivity

Sixteen source plants and two assertion-weakening checks passed on the final
runtime implementation. Each source plant failed the intended Scrut case; valid
positive controls remained passing, and no syntax or parse error substituted for
a behavioral failure. The restored 34-case document passed. The adjacent plants
JSON records each instrument and result. These supersede the earlier plants for
runtime coverage while preserving their historical evidence.

The source plants covered actual review, PR, repository, author, unresolved state,
node ID, live head and OPEN state; fix ancestry; approval source, PR, repository
and saved head; automatic repair/sync routes; and the cboone pause. Weakening the
target test's count assertions still left its diagnostic assertion effective,
and weakening its diagnostic assertion still left the count assertions effective.
Some approval-record plants were rejected by the later live-target guard after
the early validity check was removed; their tests correctly caught the loss of
pre-authentication rejection rather than claiming an external write occurred.

Pending: one comment/prose trim round, final baseline Semgrep, lint, the one full
suite under TOOLING's lock, versions, exact-tree tidy, push and ready PR.

## Trims and compatibility

One paired read-only trim round completed, `gpt-6.1-sol`, `low`, 872000-token
window. Both processes exited zero with nonempty file classifications and reports.
Comment trimming proposed no changes. Prose trimming proposed six changes; four
were accepted. The active-voice README rewrite was left because it lengthened an
already explicit subject. Removing “that” from fixing-commit evidence was left
because it generalized the claim. Client-ledger wording keeps its client-only
scope explicit. The adjacent trims JSON preserves the proposals and decisions.

Source code, fenced blocks, headings and frontmatter stayed unchanged. Scoped
Markdown lint and formatting passed; mirrors were rebuilt. The unchanged default
thread-helper and summary-contract documents passed 66 and 18 cases after the
last runtime edits. Structural and general loops remain clean at Important.

## Baseline Semgrep and final lint policy

The required baseline-mode scan ran in a disposable shared clone of a9d09239,
with SEMGREP_REPO_NAME=cboone/agent-harness-plugins, config auto, merge base
41be42039adb83f0f509bfba15eb3ebf7d954e16 and two jobs. Semgrep 1.180.0 exited
zero: 0 findings, 0 errors, 18 scanned targets and no PartialParsing result.
Semgrep limited targets to changes since the baseline and skipped its historical
comparison phase because there were no current findings. Registry include-pattern
deprecation warnings were retained; no warning or error was suppressed. The full
JSON is adjacent to this ledger. The working tree was untouched by the clone.

Final lint-and-fix runs with --no-push. Enforced tools are Markdownlint and
Prettier (package scripts and make lint-markdown), ShellCheck/shfmt (make
lint-shell), actionlint (make lint) and the make validate validators.
Broad Markdown write commands reach protected Scrut files, so their full-repo
modes are check-only by project policy. The verified check commands are the
project's make lint wrappers; scoped edits were already formatted. Shell checks
use the repository's tracked-script list and preserve generated exclusions.
The one make test-all run supplies the full lint/validate/Scrut verification.

## Final validation

The one full `SCRUT_JOBS=2 make test-all` run passed on
`44f6da761bca452efdfe2fa3a29e416131586761`. All 76 Scrut documents and 2214 cases passed,
with 0 failures and 0 skips. Lint and validation passed. The run held TOOLING's
assigned lock and released it on completion. `pmset -g therm` recorded no thermal
or performance warning. Raw outcomes and timestamps are in the validation JSON.

Lint-and-fix `--no-push`: success, check-only for broad Markdown writers by
project policy, no unresolved or skipped required checks, no code fixes needed.
Scoped formatting had already run. Check-versions passed: monitor-pr 3.5.0 to
3.6.0, a minor capability bump; all 61 source plugins are registered, versions
remain in manifests, and both existing Codex manifests match their sources.

Only review records are updated after the full run; runtime, generated plugin
content and tests remain identical to the tested tree. Record-only Markdown and
JSON receive scoped lint/format checks before the exact-tree tidy. Publication
is authorized by the worker brief; the ready PR and review précis go to TOOLING,
which owns the merge. No client PR was accessed or changed.

Non-blocking tool diagnostic: Semgrep's help renderer emitted a cmdliner escape
warning while displaying its options. The actual baseline scan completed with
zero JSON errors; no third-party issue was filed.
