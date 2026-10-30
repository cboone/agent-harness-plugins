# Error output guard ledger

## Scope and design

The existing fixture guard owns the rule because its inventory and validation
wiring already reach `make test-all` and CI. No additional tool or dependency is
introduced. The shell and awk implementation retains Bash 3.2 compatibility.
The brief selects the full local review order.

The guard uses shfmt JSON ASTs for Bash files and Scrut shell blocks. It tracks
parsed descriptor destinations and requires reasoned comments for discards and
retained diagnostics. Default Scrut live forwarding can be asserted directly.
Parsing fails closed unless a named exception has a reason. Embedded operands
are inventoried, not reparsed. The tracking design has two explicitly accepted
stream-context limits listed in the plan and the final decision below. This is
a conservative maintenance check, not a security boundary. Later sections retain
the implementation and review history, including the abandoned strict policy.

## Initial redirect audit

Each exception has an inline reason at its occurrence. Existing cases fall
into presence predicates, platform fallbacks, optional hook metadata, expected
lock contention, cleanup races, contextual validation errors, and standalone
plugin replay protocols. There is no filename-wide exemption for the capture
helper: its own implementation redirects are marked explicitly.

Local fixes keep stderr live for JSON validation, version queries and scans,
fixture JSON queries, socket startup, and unsuccessful disposable-worktree
cleanup. Exit-status and output protocols otherwise remain unchanged.

### Follow-ups

- `manage-resource-claims`: `main_worktree_path` and live inventory use process
  substitution, which loses `git worktree list` producer status. Partial output
  can be treated as complete. The two exceptions name this deferred concern.
  TOOLING was notified because the resource-claims workstream owns overlapping
  changes. A producer-status fix needs coordination and its own behavior tests.
- Version-audit scripts still allow unavailable registry reads to become empty
  lookup results. Stderr is live after this change, but a complete-versus-partial
  report contract needs broader design and coverage. No silent-discard exception
  was added for those reads.

## Plants

| Planted defect                                   | Expected instrument   | Observed result                    | Regression coverage                    |
| ------------------------------------------------ | --------------------- | ---------------------------------- | -------------------------------------- |
| Bare stderr discard in actual shipped source     | Fixture guard         | Exit 1; restored control passed    | `error-output-guard.md`, discard cases |
| Retained capture bypass in actual shipped source | Fixture guard         | Exit 1; restored control passed    | `error-output-guard.md`, capture cases |
| Weaken discard rule                              | Scrut rejection cases | 8 tests failed; restored 18 passed | `error-output-guard.md`                |
| Weaken capture rule                              | Scrut rejection cases | 5 tests failed; restored 18 passed | `error-output-guard.md`                |

## Reviews and validation

### Structural review, Nit round incomplete

Both runs used fresh `codex exec` contexts, `gpt-6.1-sol`, high effort and an
872000-token context window, read-only sandbox, approval policy `never`, disabled
web search and closed stdin. They ran concurrently. No completed structural
review or clean threshold is claimed.

- [Anti-pattern output](2026-10-28-error-output-anti-incomplete.json): process
  exit 0, nonempty schema-valid JSON, but `status: failure`, `complete: false`.
  The reviewer stopped before the checklist walk because its 67-file,
  20,245-line non-generated scope exceeded its full-reading capacity. It
  proposed seven file batches. Empty findings are not a clean result.
- [Report-only simplify output](2026-10-28-error-output-simplify-invalidated.json):
  process exit 0, nonempty schema-valid JSON, with one suggestion to remove the
  `reason` and `capture_text` aliases from `check_output`. The snapshot check
  invalidated the result: `origin/main` advanced from `a2e56c53` to `04a4fd87`
  during the review. The content tree, index and HEAD stayed unchanged. No edit
  was taken from this invalidated review. Reviewer label: `suggestion`; our
  severity: unassessed because the snapshot is invalid; take or record: record
  as an unverified lead; review again: a valid structural review remains needed.
- Preparation error: the repository-local aspect helper correctly refused to
  render its own review prompt. The run launched with that incomplete simplify
  prompt was stopped by its recorded PID, 7989, and exited 143. The installed
  helper then rendered the actual prompt. The stopped run is incomplete evidence
  and does not count as a completed review.

The anti-pattern execution reference says: "Never try the Codex run a second
time" after a completion failure. The project fallback requires Opus read-only
subagents, which are unavailable in this session. TOOLING received a question
requesting seven scoped Codex batches instead, all within the same Nit round.
Future review scopes must pin a base commit rather than a moving remote-tracking
ref.

### Scoped structural review authorization

TOOLING authorized the seven reviewer-proposed scoped read-only Codex batches in
the worker conversation. This is the narrower scope requested by the reviewer,
not a second attempt at the failed full-scope run. The Opus fallback is
unavailable to this Codex worker. All seven batches belong to the same Nit
round, with `gpt-6.1-sol`, high effort and an 872000-token window. The round is
complete only when every batch produces valid, complete output. Any batch that
fails a completion check stops the round and is reported without a rerun.

The batches cover tooling, new guard tests and docs; other fixtures;
attention-log, notify and push-notification; dependabot, monitor-pr and
pin-everything; publish-report-board; review helpers; and workmux. Their range
use fixed base and head commits. All seven completed: process exit 0, one
nonempty schema-valid JSON result, `status: success`, `complete: true`, empty
`not_reviewed`, and the exact requested range. Head, content tree and working
tree stayed unchanged. No batch needed a rerun.

[Coverage manifest](2026-10-28-error-output-batch-coverage.json) records all 69
canonical files and the seven literal scopes. The new guard fixture appears in
both batches 1 and 2, as proposed by the reviewer. Range:
`a2e56c535ed6326cc8d531d945fbb6c627a9b335..220698b8a153e4f0ab559d1e3c67ce19258abea5`.

| Batch                                     | Scope                                      | Important | Nit | Completion |
| ----------------------------------------- | ------------------------------------------ | --------- | --- | ---------- |
| [1](2026-10-28-error-output-batch-1.json) | Tooling, guard samples, docs               | 3         | 0   | Complete   |
| [2](2026-10-28-error-output-batch-2.json) | Fixtures                                   | 0         | 0   | Complete   |
| [3](2026-10-28-error-output-batch-3.json) | Attention and notification helpers         | 0         | 2   | Complete   |
| [4](2026-10-28-error-output-batch-4.json) | Dependency, monitoring and version helpers | 2         | 0   | Complete   |
| [5](2026-10-28-error-output-batch-5.json) | Report-board helpers                       | 4         | 1   | Complete   |
| [6](2026-10-28-error-output-batch-6.json) | Review helpers                             | 0         | 2   | Complete   |
| [7](2026-10-28-error-output-batch-7.json) | Workmux helpers                            | 2         | 1   | Complete   |

The round is complete but not clean. Three Important findings concern the new
guard; five Nit findings concern newly added exception comments. Eight Important
findings and one Nit describe pre-existing behavior. Their severity is retained;
the brief permits recording larger follow-ups instead of expanding this guard
change. No reviewer label was downgraded.

#### Finding decisions

The source locations and complete evidence remain in each raw batch report.
Each row records the reviewer label, our severity, take-or-record decision and whether further behavior review is required.

| Finding                            | Reviewer label | Our severity and impact                                                     | Take or record                                     | Review again                |
| ---------------------------------- | -------------- | --------------------------------------------------------------------------- | -------------------------------------------------- | --------------------------- |
| B1: `>&file` spelling              | `important`    | Important: discard and capture bypass the guard                             | Taken; see fixes below                             | Yes, behavior               |
| B1: token-split continuation       | `important`    | Important: inserted whitespace hides redirects                              | Taken; see fixes below                             | Yes, behavior               |
| B1: skipped command boundary       | `important`    | Important: unrelated reasons exempt earlier commands                        | Taken; see fixes below                             | Yes, behavior               |
| B3: tmux lookup comment            | `nit`          | Nit: logging continues without name metadata                                | Taken; see fixes below                             | No, comment                 |
| B3: missing session-ID comment     | `nit`          | Nit: completion state still uses other key fields                           | Taken; see fixes below                             | No, comment                 |
| B4: unavailable version reads      | `important`    | Important: existing workflow can close a stale issue after incomplete reads | Record, pre-existing broader report contract       | Follow-up                   |
| B4: reply pagination mismatch      | `important`    | Important: existing resolver omits replies beyond its fetch limit           | Record, pre-existing independent resolver concern  | Follow-up                   |
| B5: symlink metadata               | `important`    | Important: existing identity and permission protections inspect the link    | Record, pre-existing file-write protection concern | Follow-up                   |
| B5: unavailable metadata           | `important`    | Important: existing fallback bypasses identity and mode protections         | Record, pre-existing file-write protection concern | Follow-up                   |
| B5: origin URL in diagnostic       | `important`    | Important: existing mismatch notice can reveal URL credentials              | Record, pre-existing diagnostic concern            | Follow-up                   |
| B5: dash-leading input paths       | `important`    | Important: existing readers interpret valid paths as jq options             | Record, pre-existing input-handling concern        | Follow-up                   |
| B5: lock failure diagnostic        | `nit`          | Nit: existing retry reports non-contention failures as contention           | Record, pre-existing diagnostic concern            | Follow-up                   |
| B6: process-query comment          | `nit`          | Nit: errors are retained, not replayed                                      | Taken; see fixes below                             | No, comment                 |
| B6: runner-log comment             | `nit`          | Nit: log is retained, not validated                                         | Taken; see fixes below                             | No, comment                 |
| B7: partial worktree inventory     | `important`    | Important: existing unchecked producer can release live claims              | Record, already deferred and reported to TOOLING   | Follow-up                   |
| B7: concatenated issue objects     | `important`    | Important: existing validator accepts a stream as one issue                 | Record, pre-existing composition concern           | Follow-up                   |
| B7: cleanup and discovery comments | `nit`          | Nit: replacement diagnostics are incorrectly promised                       | Taken; see fixes below                             | Decide from the actual edit |

[Isolated reproductions](2026-10-28-error-output-review-repros.json) confirm seven
syntax-valid guard bypass samples: shorthand discard and capture, two split
redirect tokens, blank and comment boundaries, and a trailing backslash in a
comment. Each passes `/bin/bash -n` and incorrectly receives exit 0 from the
unmodified guard. The samples were never executed.

The secret-handling checklist was applied to the origin-notice trace: the raw
remote URL is interpolated into a retained notice and replayed to stderr.
No credential files or real credentials were inspected. This defensive finding
needs a separately scoped fix, not credential rotation or live changes in this
workstream.

Main integration remains required before the PR. Integrate before applying the
guard fixes so overlapping combined-worktree changes are present, and report any
conflict without resolving it. Then take the branch-owned findings, regenerate
mirrors and add regression cases and judge weakenings for the guard changes.
Behavior fixes advance the structural loop to its first Important round; the
seven scoped batches together remain its single Nit round.

### Validation at the stop

- Corepack `yarn install --immutable`: passed.
- New guard document: 18 cases passed, including accepted controls.
- Actual-source plants: each rejected with exit 1; each restored control passed.
- Rule weakenings: 8 and 5 failures; final restored document passed all 18 cases.
- Full Scrut suite, `SCRUT_JOBS=4`: all 43 documents passed, zero failed or
  skipped documents. Every document completed with a nonempty valid summary.
- Initial `make test-all` stopped at Prettier on 12 edited manifests. Targeted
  formatting and mirror regeneration corrected that failure. Separate lint and
  validation then passed: Markdown, Prettier, ShellCheck, shfmt, actionlint, JSON,
  the fixture guard, plugin manifests, generated mirrors and cross-references.
- Main integration, completed structural review, focused aspect review, trims,
  baseline Semgrep, final `lint-and-fix --no-push`, final `make test-all`, version
  checks, tidy, push and PR remain pending. No merge was attempted and no PR is
  open. TOOLING merges after the finished PR; this worker never merges it.

## Merge integration and review fixes

TOOLING authorized resolving the merge in the worker conversation: preserve all
fixture rules, take main's two conflicting canonical review-plugin manifests
and bump their patches, take main's generated manifests and regenerate them.
The signed merge is `f48dbca8`, with main parent
`e8667c85610d10882e7c33078748c7113b1c4a8e`. Both `output_line` and
`shared_copy_table` resets remain; the literal-copy-table exclusion and every
Git reset, fixture namespace, Scrut wrapper and diagnostic rule remain present.
Review-plugin versions are 2.2.1 and 3.3.1.

Merged-tree lint passed. Validation initially found a newly merged intentional
collision probe whose diagnostics were already captured, checked and replayed
on mismatch. Adding a reason to that occurrence reconciled the rule without
weakening either side. Validation then passed, as did all 18 error-output cases
and all 47 environment-isolation cases. This includes main's copy-table guards.
The version audit also caught a shared workmux patch value; this branch advances
it from main's 1.1.2 to 1.1.3.

### Valid pinned simplify result

[Raw simplify result](2026-10-28-error-output-simplify-pinned.json) and
[verification metadata](2026-10-28-error-output-simplify-pinned-metadata.json)
replace the invalidated lead. TOOLING authorized the rerun in the same Nit
round. It used the same immutable base and reviewed head as the seven batches,
in a disposable shared clone, with the installed 2.2.0 helper and the same
read-only Codex settings. Process exit, single JSON value, schema, reviewed
snapshot and scope stability checks passed. No lasting changes were found in
the clone; the original unresolved merge state was also unchanged. The rerun did
not consume another round or duplicate any anti-pattern batch.

Reviewer label: `suggestion`. Our severity: Nit, redundant aliases affect
clarity only. Take: remove `reason` and `capture_text` and match against
`text` directly, included in the guard fix. Review again: no behavior change
from this cleanup alone; the guard fixes require the first Important round.

### Taken findings

- B1 shorthand redirects: recognize `>&word`, including numeric-leading file
  names and quoted filenames, while leaving numeric descriptor writes live.
- B1 continuation tokens: delete the backslash rather than adding whitespace,
  and count trailing backslashes so escaped backslashes do not merge commands.
- B1 command boundaries: process blank and comment lines before the Git-graph
  skip, end continuation groups at hash suffixes conservatively, and flush
  pending text at file boundaries and EOF. Literal hash suffixes also end a
  group; embedded command text remains a conservative text check, not a Bash
  parser. Every Git-consumer rule retains its prior ordering and behavior.
- B3 comments: tmux metadata may be unavailable while logging continues; an
  empty session ID still contributes the remaining completion-key fields.
- B6 comments: inspection failures retain artifacts and are treated as active;
  the runner checks process status and reply, while retaining the log.
- B7 comments: failed directory resolution skips optional pane discovery.
  Prompt cleanup now keeps rm stderr live instead of promising a nonexistent
  replacement diagnostic. This last edit changes error output, so it joins the
  guard fixes in the next behavior review.

Our severities remain as recorded above. These branch-owned takes are no longer
pending; their regression results and plants are recorded next. All eight
pre-existing Important findings and the pre-existing Nit remain deferred in this
ledger under TOOLING's explicit direction. No issue has been filed for them.

The next structural review is Important round 1, with both base and head pinned.
Its fixed base is `e8667c85610d10882e7c33078748c7113b1c4a8e`, never a moving
remote-tracking ref. No structural clean threshold is claimed before that run.

### Guard-fix validation and plants

The expanded error-output document passes all 31 cases. It adds the seven
previously passing bypasses, numeric-leading shorthand filenames, descriptor
and reasoned-shorthand controls, literal-hash text, even backslash counts and
pending text at EOF. Every static sample passes `/bin/bash -n`; samples are
never executed.

[Plant results](2026-10-28-error-output-fix-plants.json) record six independent
judge weakenings. Each uses the existing Scrut setup and its named regression
case projected into a disposable document; the source assertion is unchanged.
Every original control passed both cases, every weakened guard produced exactly
one success and one assertion failure, and the restored repository guard passed
after each mutation. No test stub or real external tool was substituted.

| Weakened rule                                        | Named regression    | Measured result                       |
| ---------------------------------------------------- | ------------------- | ------------------------------------- |
| Disable shorthand recognition                        | Shorthand discard   | Control passes; named assertion fails |
| Insert whitespace at continuation join               | Split discard token | Control passes; named assertion fails |
| Skip blank/comment lines before assembling output    | Blank boundary      | Control passes; named assertion fails |
| Ignore comment termination when continuing           | Comment backslash   | Control passes; named assertion fails |
| Treat every trailing backslash count as continuation | Even backslashes    | Control passes; named assertion fails |
| Remove pending-file flushes                          | Pending at eof      | Control passes; named assertion fails |

The check and tests were committed before these plants. Original bytes were
restored between mutations. ShellCheck/shfmt, Markdown/Prettier/actionlint and
repository validation pass on the guard-fix tree. The Important review remains
pending, with no clean threshold claimed.

## Structural Important round 1: stopped for recurrence

Pinned range:
`e8667c85610d10882e7c33078748c7113b1c4a8e..f81d64cf15426e811195818c2a2072ac0f1827b6`.
Batches 1–4 and report-only simplify completed with process exit 0, exactly one
nonempty schema-valid result and the expected range or snapshot. Every completed
anti-pattern batch reports success, complete coverage and no unread scoped files.
The before/after snapshot check found no lasting changes: scope_changed false,
changed and outside_scope empty. These checks preceded writing the review records.
Batches 5–7 were not started after the recurring finding was observed. No clean
result is claimed for the incomplete whole round.

| Run                                                                              | Result                                                   |
| -------------------------------------------------------------------------------- | -------------------------------------------------------- |
| [Tooling batch 1](2026-10-28-error-output-important1-batch-1.json)               | Two guard Important findings, one pre-existing Important |
| [Fixture batch 2](2026-10-28-error-output-important1-batch-2.json)               | No Important findings                                    |
| [Notification batch 3](2026-10-28-error-output-important1-batch-3.json)          | No Important findings                                    |
| [Dependency/monitoring batch 4](2026-10-28-error-output-important1-batch-4.json) | Two previously deferred Important findings               |
| [Report-only simplify](2026-10-28-error-output-important1-simplify.json)         | Optional descriptive classification values               |
| Batches 5–7                                                                      | Not started: recurrence stop                             |

### Finding decisions

- Quoted hash text before a split redirect still bypasses the guard. Reviewer
  label: `important`; our severity: Important, a valid Bash command discards
  diagnostics without a reason. Take or record: take, pending structural design.
  Review again: required after the fix. This is another instance of the
  token-split class fixed after the Nit round, so the recurrence rule applies.
- `2>&-` and `2<&-` close stderr without being flagged. Reviewer label:
  `important`; our severity: Important, the child loses its diagnostic channel.
  Take or record: take, pending the same design. Review again: required after
  the fix. This syntax was absent from the initial guard.
- `bin/version-audit` repeats the pre-existing unavailable-read false success
  already deferred for its template. Reviewer label: `important`; our severity:
  Important. Take or record: record as that follow-up's repository-tooling
  sibling, without expansion or filing. Review again: follow-up. Batch 4 also
  re-reports the template and reply-pagination concerns at unchanged Important
  severity; both remain deferred.
- Simplify proposes `discard`/`capture` instead of numeric return values.
  Reviewer label: `suggestion`; our severity: Nit, clarity only. Take or record:
  record pending the structural decision, which may replace the helper.
  Review again: no behavior review solely for this proposal. It is not applied
  because the loop is stopped.

[Static reproductions](2026-10-28-error-output-recurrence-repros.json) confirm
all three inputs pass `/bin/bash -n` and incorrectly receive guard exit 0.
The samples were never executed. The hash-boundary workaround does not close the
tokenization class; 31 passing tests and six successful judge weakenings do not
establish the intended absence claim.

The Review rounds rule at `~/Work/projects/CLAUDE.md` requires stopping when
another instance of an earlier fixed class appears, and gives the conductor the
structural choice. No further regex edit, later review phase or PR action began.

### Structural option for the conductor

shfmt is already required by repository lint and installed before CI validation.
Its installed `--to-json` mode was checked directly on the three reproductions.
[Parser evidence](2026-10-28-error-output-shfmt-probes.json) shows descriptor 2,
operator `>`, target `/dev/null` for the quoted-hash split, and descriptor 2
with `>&`/`<&`, target `-`, for the closures. All parse successfully. No
software was installed and no product parser change was made.

One structural option extends the existing checker with this already-required
Bash parser for real redirects and comment positions, while defining conservative
handling for embedded command strings and non-Bash fixtures. Another is a narrow
declared grammar that rejects unsupported constructs rather than accepting them.
Either must preserve all fixture rules, cover the complete redirect family and
measure fixture-suite runtime. No new tool or further regex patch is introduced
without the conductor's call.

**End state: stopped: recurring defect.** Counts remain structural Nit 1 and
Important 1 stopped; they do not restart on resume.

## AST design call and prerequisite stop

TOOLING chose shfmt's JSON AST inside the existing checker, replacing the regex
token handling. The call covers descriptor 2 redirects, including overwrite,
duplication, input duplication and closure; Bash files and Scrut shell blocks;
fail-closed parsing unless a named exception has a reason; and explicit,
reasoned scope exclusions for embedded strings and non-Bash fixtures. The three
escape cases must become regression tests, with the old regex path planted as
the weakening. Resume the existing Important round count, finish batches 5–7,
and review the new design against an immutable merge-base commit. No follow-up
issues are authorized.

The call first requires confirming that local test-all and CI already provide
the repository's pinned shfmt, stopping if an install or CI change is needed.
That prerequisite is not fully met:

- Local make test-all includes lint-shell, which requires shfmt on PATH.
  Installed shfmt is 3.14.1. No local install is needed.
- The CI lint/validation job already uses
  [the SHA-pinned setup action](https://github.com/cboone/gh-actions/blob/3c9adb5a8b166444d3c0e3fe606d55f0dc7ac726/actions/set-up-shfmt/action.yml).
  Its default is shfmt 3.14.1 with committed platform SHA-256 checksums, verified
  by reading that exact action revision through the GitHub API.
- The separate test-scrut matrix job in .github/workflows/ci.yml has no shfmt
  setup step. Its
  [pinned Scrut action](https://github.com/cboone/gh-actions/blob/3c9adb5a8b166444d3c0e3fe606d55f0dc7ac726/actions/set-up-scrut/action.yml)
  installs Scrut 0.4.3, not shfmt. That exact action was also inspected.
  The matrix runs error-output-guard and environment-isolation, which invoke the
  checker. Setup in the separate lint job does not configure this job.

Relying on incidental tools from the moving ubuntu-latest image would not
provide the repository's pinned version. The AST implementation therefore needs
a CI change to add the existing pinned shfmt setup to the Scrut matrix job.
TOOLING explicitly required stopping rather than making such a change.

No AST implementation, CI edit, software installation or new review run has
started. The prior recurrence findings remain unresolved. Round counts are
unchanged. The prerequisite result is reported to TOOLING for direction.

## Authorized AST implementation

TOOLING cleared the prerequisite stop by explicitly authorizing the existing
SHA-pinned shfmt setup step in the test-scrut matrix. The added step uses
`cboone/gh-actions/actions/set-up-shfmt@3c9adb5a8b166444d3c0e3fe606d55f0dc7ac726`,
the same v5.0.0 action, default shfmt 3.14.1 and committed checksum source as the
lint job. No other CI settings, permissions or triggers changed. The PR must
mention this prerequisite addition. No software was installed locally.

The existing checker now delegates redirect classification to shfmt JSON ASTs,
with Bash 3.2-compatible orchestration and jq traversal. All pre-existing graph,
namespace, reset and fixture-copy rules remain. Batch boundaries are validated;
parse failures and malformed AST boundaries fail closed. Exceptions require exact
unit names and reasons and are rejected when stale. The scope inventory names
all excluded non-Bash files with language-specific reasons and embedded operand
spans with a reason each. Embedded text is never regex-scanned as shell code.
Parsed substitutions inside words and heredocs are still inspected.

The AST follows descriptor operations in order, including duplication, moves,
closure, combined redirects and implicit stderr pipelines. Only actual parsed
comments grant line exceptions. Default Scrut live forwarding is distinguished
from local captures, functions, pipeline-left commands and configured streams.
The real tree has fourteen named non-Bash exclusions and no parse exceptions.

The seed audit removed 134 stderr suppressions in twenty Scrut documents while
preserving stdout suppression and quoted trap text. It added 172 assertion-specific
capture reasons plus eight manually placed annotations. The 176 annotated blocks
have identical comment- and position-free ASTs to their post-discard versions;
assertions were not removed. Broader producer-status findings remain deferred in
this ledger without changing severity or filing issues.

The guard document passes all 65 cases, including all three required escapes in
scripts and Scrut blocks, descriptor moves and leading zeros, nested substitutions,
real versus quoted markers, parser exceptions, named non-Bash input and cross-block
boundary failures. Environment isolation passes all 47 cases. The full checker
passes, and make validate passes. Final test-all remains outstanding. Removing
only AST position metadata from traversal reduced the measured full-tree checker
runtime from 12.21 to 6.17 seconds. The isolated guard document completed in 65.45
seconds; the environment document completed in 196.75 seconds.

Two pinned-parser limitations are explicit: a backslash-newline split before an
ampersand may be refused despite valid Bash syntax, and a backslash-ended comment
may produce an unsafe multiline comment AST. Both fail closed; named parse
exceptions can document unsupported static inputs. There is no regex fallback.

Important round 1 retains completed batches 1–4 and simplify. Batches 5–7 and the
fresh new-design review remain outstanding; no count reset or failed-run retry is
being taken. Old-regex regression plants will be recorded after the implementation
and tests are committed.

### Old-regex regression plants

After signed implementation commit `a8d22799`, the actual checker was replaced
with its old regex implementation from `87e96f6e`, one measured case at a time.
The allowed-probe control passed for both implementations. Each AST regression
returned the named discard error and status 1 before and after restoration.
Each planted old-regex case returned the normal success message and status 0,
so the corresponding regression assertion fails, rather than a neighboring
parse or fixture rule rejecting the plant. Source bytes were restored exactly;
the working tree remained clean outside the evidence records.

| Planted defect                   | Instrument              | Measured result                  | Regression                                          |
| -------------------------------- | ----------------------- | -------------------------------- | --------------------------------------------------- |
| Old regex with quoted-hash split | Guard discard assertion | Old checker accepts; AST rejects | Quoted hash token split, script and Scrut cases     |
| Old regex with output closure    | Guard discard assertion | Old checker accepts; AST rejects | Descriptor 2 output closure, script and Scrut cases |
| Old regex with input closure     | Guard discard assertion | Old checker accepts; AST rejects | Descriptor 2 input closure, script and Scrut cases  |

[Raw before, planted and restored results](2026-10-28-error-output-old-regex-plants.json)
retain all twelve statuses and outputs. No sample program was executed and no
external tool stub was introduced.

## Structural Important round 1 completed after resumption

The remaining historical batches used a disposable shared clone checked out at
`f81d64cf15426e811195818c2a2072ac0f1827b6`, with immutable base
`e8667c85610d10882e7c33078748c7113b1c4a8e`. All three ran read-only through
Codex `gpt-6.1-sol`, high effort, window 872000, approval never, web disabled,
stdin closed and ephemeral sessions. Each exited 0 with one nonempty schema-valid
JSON reply, success status, complete coverage, no unread files and the exact
requested range. Logs progressed beyond startup; no lasting clone changes were
found. No run was retried.

[Batch 5](2026-10-28-error-output-important1-batch-5.json) repeats four recorded
Important findings: symlink metadata, unavailable metadata, raw origin diagnostics
and dash-leading input paths. [Batch 6](2026-10-28-error-output-important1-batch-6.json)
has no Important findings. [Batch 7](2026-10-28-error-output-important1-batch-7.json)
repeats partial worktree inventory and concatenated issue-object validation.
For each repeated finding: reviewer label is important, our severity remains
Important for the previously recorded impact, decision remains record as an
independent pre-existing concern under TOOLING's direction, and no further
behavior review is caused by recording it. No follow-up issue was filed.

This completes Important round 1 without resetting its count. Its branch-owned
recurring redirect defects were taken through the authorized AST replacement,
which changes behavior and therefore advances the structural loop to Important
round 2. That fresh review includes all changed Scrut documents and report-only
simplify. The checker also passed directly under macOS Bash 3.2.57.

## Structural Important round 2 completion stop

The fresh review is pinned to base `e8667c85610d10882e7c33078748c7113b1c4a8e`
and head `dd43f040`, in a disposable shared clone. The coverage manifest includes
all changed Scrut documents, canonical source and the current ledger; generated
mirrors and historical raw review evidence are excluded with reasons.

Report-only simplify failed process completion with exit 1 before review began:
“Not inside a trusted directory and --skip-git-repo-check was not specified.”
The launch incorrectly selected the external capture directory as Codex's working
directory rather than the disposable Git clone. Settings were explicitly
`gpt-6.1-sol`, high effort, window 872000, read-only sandbox, approval never,
web disabled, ephemeral and stdin closed. No skip flag, override, fallback or
retry was attempted. No finding or clean result can be inferred from this failure.
[Failure evidence](2026-10-28-error-output-important2-simplify-failed.json)
records the process status and complete log.

Per the explicit completion-check stop, no later review phase or PR action will
start. Anti-pattern batches 1–2 had already started concurrently and are being
collected; batches 3–7 were not started. The stop was posted to TOOLING through
mailbox-post message 000012. Direction is required before any replacement
simplify run or continuation. The existing counts remain Nit 1, Important 1
completed and Important 2 incomplete. No clean threshold is claimed.

### Drained results and final stopped state

The two already running batches have now completed, both exit 0 with exactly one
nonempty schema-valid success result, complete coverage, no unread files and the
exact pinned range. [Batch 2](2026-10-28-error-output-important2-batch-2.json)
reports no Important findings. [Batch 1](2026-10-28-error-output-important2-batch-1.json)
reports two. The before/after snapshot comparison found no lasting changes:
scope_changed false, changed and outside_scope empty. No reviewer remains active.
[The coverage manifest](2026-10-28-error-output-important2-coverage.json) records
the intended seven scopes and exclusions; only batches 1–2 completed.

| Finding                                | Reviewer label | Our severity and impact                                                      | Take or record                                                       | Review again       |
| -------------------------------------- | -------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------ |
| Inherited stdout redirect destinations | important      | Important: a new Scrut live-forward exception accepts discarded child stderr | Take, correction pending the completion stop and conductor direction | Yes, behavior      |
| Unavailable version lookup             | important      | Important: an existing incomplete audit can close a drift issue              | Record, unchanged pre-existing follow-up under prior direction       | No edit; follow-up |

The new finding is a concrete context-propagation gap in the AST design. In a
default stdout Scrut block, `{ some-command 2>&1; } 01>/dev/null` escapes because
the enclosing retention check compares the unnormalized descriptor with `1`.
The sibling `{ some-command 2>&1; } 1<>/dev/null` escapes because that operator
is absent from the retention list. The nested descriptor map is reset to live
stdout, and its stderr redirect is therefore exempted. The local redirect reducer
normalizes descriptor numbers, but the enclosing propagation check does not.
These are static source traces from a valid completed review, not executed
reproductions. No fix or new plant was attempted after the completion stop.
A correction should propagate actual descriptor destinations or conservatively
reject unsupported inherited destinations rather than granting a live exception.
The conductor receives the finding with the existing stop; no severity downgrade
or clean result is taken.

The full Scrut run exited 0: all 46 documents passed. This is test evidence, not a
substitute for the incomplete review or outstanding final make test-all. The
branch is committed, with no push or PR. Remaining batches, focused reviews,
trims, baseline Semgrep, final lint, version checks and tidy are outstanding.

## Authorized completion and Important round 2 decisions

TOOLING classified the simplify launch error as an invocation error, not a round
and not clean, and authorized exactly one replacement with `--cd` set to this
trusted worktree, the same settings and pinned base, and no skip flag. That run
completed successfully. Existing valid batches 1–2 were retained; batches 3–7 ran
at the same immutable `e8667c85..dd43f040` range. All remaining runs exited 0 with
one nonempty schema-valid reply, expected range or snapshot, complete coverage
and no unread scoped files. The before/after snapshot comparison found no lasting
changes. No failed review output was treated as clean, and no count was reset.

Batches 3 and 6 have no Important findings. Batch 4 repeats unavailable-version
and reply-pagination findings. Batch 5 repeats four report-board findings and adds
a pre-existing invalid-port validator finding. Batch 7 repeats inventory and
issue-stream findings and adds a pre-existing missing rejection-status assertion.
All ten pre-existing Important concerns keep that severity; none is downgraded.
TOOLING's requirement to distinguish branch-owned defects from independent
pre-existing behavior is applied individually below.

### Scope decisions for deferred Important findings

Each row has reviewer label `important`, our severity Important for its stated
impact, decision record because the defect lies outside this branch's changes or
the guard brief, and no behavior edit requiring review in this workstream.
[Executable AST comparison](2026-10-28-error-output-deferred-scope-audit.json)
confirms identical base and current function bodies for the six specifically
requested concerns after removing only comments and source positions.

| Finding                             | Existing impact                                                | Exact scope reason                                                                                                                                                                                                                                                                                                  |
| ----------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Symlink metadata                    | Existing render can replace input data or change access modes  | `report-board` write_output and cmd_render have identical executable ASTs at the pinned base and head; only exception comments changed. Following symlinks and file-write identity policy are independent of stderr retention.                                                                                      |
| Unavailable metadata                | Existing fallback can bypass identity and mode protections     | The same two functions retain their original stat fallback and write decisions byte-for-byte in executable AST form. This branch neither introduces nor broadens the fallback; metadata failure policy is outside the guard brief.                                                                                  |
| Origin URL diagnostic               | Existing mismatch notice can expose URL credentials            | `bugs-gather` cmd_gather has an identical executable AST, including notice capture and replay. This branch adds reason comments; URL redaction is an independent pre-existing diagnostic defect. No actual credentials were inspected.                                                                              |
| Dash-leading filenames              | Existing gather CLI rejects valid relative paths               | `backlog-gather` require_json_file and cmd_finish have identical executable ASTs; the sibling bugs-gather readers also retain their original operands. Normalizing CLI input paths is outside the stderr guard.                                                                                                     |
| Partial worktree inventory          | Existing partial producer output can release live claims       | Both manage-resource-claims inventory functions have identical executable ASTs. Only comments name the deferred producer-status defect, already coordinated with the resource-claims workstream. No inventory, liveness or takeover behavior changes here.                                                          |
| Concatenated issue objects          | Existing validator can produce a malformed single-issue prompt | compose-issue-prompt validate_json has an identical executable AST. Its single-object versus stream contract is pre-existing and independent of guard redirects.                                                                                                                                                    |
| Unavailable version reads           | Existing incomplete audit can close a drift issue              | This branch removes stderr suppression but preserves the original success conversion, empty-result checks and workflow output contract. Designing complete/partial reports is independent work; no new failed-read success path was introduced.                                                                     |
| Reply pagination mismatch           | Existing resolver omits some replies from its audit            | The 20-versus-100 comment fetch limits and audit consumers are unchanged at the pinned base. This branch changes only prerequisite and validation exception comments in that helper.                                                                                                                                |
| Invalid repository URL port         | Existing boards can render unusable links                      | The report-board URL validator near line 600 and its callers are unchanged; the file's edits are exception comments. Port-range validation is outside the new error-output guard.                                                                                                                                   |
| Missing rejection-status assertions | Existing CLI tests can accept error text with status 0         | The existing composer and malformed-claim cases retain their original pipeline and expected-output assertions; edits add only capture reasons. This is not missing coverage for new guard behavior, whose rejected cases explicitly require status 1. Changing unrelated CLI status contracts is outside the brief. |

No follow-up issue was filed. The existing lock-failure wording Nit remains a pre-existing diagnostic follow-up at its original severity.

### Taken branch-owned finding and simplify suggestions

The inherited descriptor finding retains reviewer label `important` and our
severity Important: default Scrut forwarding could accept discarded child stderr.
It is taken. The redirect reducer's existing descriptor map now flows into nested
command nodes, so every supported operator and normalized descriptor uses the
same destinations. Pipeline producers use captured stdout. Function and
substitution contexts retain conservative stream assumptions. Twelve added
static cases cover both reported escapes, inherited closure and alias destinations,
file capture, pipeline capture, live saved-stdout aliases and conservative
function/substitution boundaries. The sample commands are never executed.
This is a behavior correction and requires the next structural round at Critical.

Report-only simplify has two `suggestion` findings. Naming the repeated
live-forward condition is a Nit clarity improvement, taken locally. Shortening
the repeated attention-log reason is also taken as a comment-only improvement;
broader annotation wording is optional and remains for the final trim pass.
Neither comment change independently requires another behavior round. No files
were changed by the reviewers.

### Descriptor propagation validation and plants

Signed commit `3ca5ea15` contains the corrected descriptor propagation and twelve
regression cases. All 77 guard cases and make validate passed. The actual prior
AST evaluator from `dd43f040` was then planted in the source file. Both the
leading-zero and in/out enclosing-stdout regressions changed from the named
discard error and status 1 to the old success message and status 0. The allowed
probe passed throughout; exact bytes were restored between phases and the fixed
assertions passed again. [Nine measured rows](2026-10-28-error-output-inherited-map-plants.json)
retain before, planted and restored outputs. These are guard failures against
static programs; none of the sample commands executed.

A sibling audit also identified explicit shell stdout changes by `exec` between
commands in one Scrut block. Such a block now conservatively requires a reason
for stderr merges instead of assuming their destination is live. Direct exec,
builtin exec and command-prefixed exec have regression cases. The first full-tree
validation caught an assignment-only CallExpr with no Args array; the predicate
now accepts an empty argument list. Validation then passed, all 80 cases passed,
and a further assignment-only redirect positive control passed separately. The
final document contains 81 cases. No test or failed development check was used as
a substitute for the final full-tree checks.

The normal descriptor reducer and stdout-context predicate share descriptor
normalization. Function and substitution boundaries preserve conservative stream
assumptions instead of inheriting unproven aliases. The AST design and external
interfaces remain unchanged. The behavior fixes advance the structural loop to
its Critical threshold, with report-only simplify retained and the base fixed at
`e8667c85610d10882e7c33078748c7113b1c4a8e`.

After commit `a6f57706`, the actual evaluator from `3ca5ea15` was planted for the
three explicit exec variants. All three corrected assertions returned the named
capture error and status 1 before and after restoration; the prior evaluator
accepted each with status 0. The allowed probe passed in every phase. Exact
source bytes were restored. [Twelve measured rows](2026-10-28-error-output-exec-stream-plants.json)
retain the outputs. No sample program or external stub was executed.

## Structural Critical round 1: recurring stream-context stop

Both anti-pattern review and report-only simplify completed with exit 0,
nonempty schema-valid output and the exact pinned range or snapshot. Settings
were gpt-6.1-sol, high effort, window 872000, read-only, approval never, web
search disabled, ephemeral and stdin closed. The before/after snapshot comparison
found no lasting changes. Range:
`e8667c85610d10882e7c33078748c7113b1c4a8e..7ee035d2`.
The fix scope covers complete guard code, fixtures, static samples and docs;
the remaining branch code was already fully reviewed in Important round 2 and
had not changed. No failed output is counted as a review or clean result.

[Anti-pattern findings](2026-10-28-error-output-critical1-anti.json) identify two
more instances of the stream-context class corrected in Important round 2.
The original leading-zero and in/out enclosing-stdout cases are fixed, but the
new live-forwarding assumptions still admit these siblings:

- `{ exec 3>/dev/null; some-command 2>&3; } 3>&1` accepts the later stderr
  redirect using the stale inherited descriptor-3 destination. The exec check
  only marks mutations of descriptor 1 as uncertain; the local map does not
  retain the descriptor-3 change for the following statement.
- `command builtin exec 1>/dev/null; some-command 2>&1` accepts the later
  merge because the exec predicate recognizes only one builtin prefix. The
  composed prefix hides the persistent stdout change from that predicate.

These are concrete static source traces from a completed reviewer. They were not
executed and no new source plant or fix was attempted after the recurrence stop.
Each finding has reviewer label important, our severity Important because the
guard accepts discarded child stderr, decision take-required but blocked pending
the structural call, and review-again yes for any behavior correction. Neither
is downgraded or deferred as an independent pre-existing issue.

[Report-only simplify](2026-10-28-error-output-critical1-simplify.json) suggests
naming the repeated descriptor-duplication condition. Reviewer label suggestion,
our severity Nit for clarity, record as optional at this stop, no behavior edit
or independent review required. It has not been applied.

The Review rounds recurrence rule requires a design decision before more fixes,
review, trims or PR work. The conductor is being informed through mailbox-post.
A narrower acceptance policy is available within the existing AST checker:
require an explicit reason for every descriptor-2 redirection except proven
syntactic self-duplication, including Scrut merges and aliases inferred as live.
That removes acceptance decisions based on mutable inherited destinations and
prefix recognition. The conductor chooses whether to use that policy or a fuller
persistent descriptor model; no such change is being made without the call.

The updated environment-isolation document passed all 47 cases. The guard's
80-case run and the 81st assignment control passed before this review, and make
validate passed. These do not establish absence of the newly reported defects.
No focused review, trims, baseline Semgrep, final lint, final test-all, tidy,
push or PR has started. Counts remain structural Nit 1, Important 1, Important 2,
and Critical 1 stopped; the failed simplify invocation consumed no round.

**End state: stopped: recurring defect.**

### Earlier-stop instructions and the current gate

TOOLING subsequently clarified that the relayed instructions answer the earlier
4:53 AM stop and apply together with the preceding message. Those tasks are
complete: inherited-descriptor correction and plants, valid replacement simplify,
remaining Important round 2 batches on the fixed base, individual deferred-scope
reasons, and a further structural round after the behavior change. The later
Critical round 1 recurrence remains unresolved. Its two own Important findings
are take-required, not deferred as pre-existing concerns.

A question has been sent to TOOLING identifying the distinct current gate and
requesting the structural choice already proposed above. No completed batch is
being repeated and no count is reset. Future simplify launches use a trusted
disposable Git clone under the latest instruction, without skip or override
flags. No patch, review or PR action starts before the recurrence call.

**End state: stopped: recurring defect.**

## Explicit-reason structural call and annotation-count gate

TOOLING selected the proposed closure: every descriptor-2 redirect requires a
recorded reason except syntactic self-duplication, including Scrut merges and
inferred live aliases. Alias and exec-prefix tracking must be removed. The call
also requires both new escape cases and earlier-implementation plants, followed
by Critical rounds continuing from the existing count. Before seeding reasons,
more than about twenty new annotations requires stopping with the count and a
sample.

The AST evaluator now classifies redirects syntactically, retaining normalized
descriptor numbers, combined redirects, descriptor-2 moves and closure checks.
The only duplication exemption is a literal numeric descriptor 2 duplicated onto
itself without a move. Alias maps, inherited-stream propagation, Scrut stream
acceptance exemptions, exec-prefix recognition and the live-forwarding report
field have been removed. Comment recognition, parsing, unit boundaries, scope
inventory and every fixture-environment graph rule remain.

The existing checker produced a complete AST scope inventory with no parse errors;
it exits 1 because the stricter policy finds unreasoned redirects. Before any new
reason annotation, the inventory identifies **412 redirects requiring 408
annotation sites in 35 existing Scrut documents**. Multiple redirects covered by
the same parsed outer-command end line count as one annotation site. Existing
valid reason markers have already been excluded. No shipped-script annotation
site was added to this count. [Count, per-file totals and twelve source samples](2026-10-28-error-output-explicit-reason-count.json)
record the measurement and the evaluator hash. All measured source lines are
unchanged; zero new annotations were added.

Representative sites:

- `tests/scrut/report-board.md:14`: the validation command merges stderr with
  stdout before the snapshot.
- `tests/scrut/copilot-rounds-report.md:174`: replay merges stderr before sending
  stdout to `/dev/null`.
- `tests/scrut/resolve-copilot-threads.md:102`: the invalid-review parser test
  merges stderr with stdout for its assertion.

The largest groups are report-board (98 sites), copilot-rounds-report (36) and
resolve-copilot-threads (22). The count exceeds the explicit budget gate, so the
worker stops before adding reasons. This is a measured policy migration, not a
passing full-tree guard or test result. Regression updates, the two new escape
cases and their plants, Critical round 2 and the rest of the local order remain
pending this gate. No new review round, push or PR started.

The design call is accepted and partially implemented; its annotation budget is
the current closed gate. TOOLING receives the count and sample for direction.

## Inbox decision: return to tracking and accept two known limits

TOOLING relayed the Inbox answer at 10:28 AM ET on 2026-10-29: “Go back to the
tracking design and record the two escapes”. The implementation and development
documentation are restored from `2a312d62` with a new signed commit. Earlier
commits and the annotation-count evidence remain in history; no commit is
rewritten and no force push is used. No branch has been pushed yet.

The plan now records both accepted limits: persistent mutations of a saved live
alias, and composed command/builtin prefixes hiding exec. Their exact examples
remain in the Critical round 1 report above. Each retains reviewer label important
and our severity Important. Decision: record as a known limit by the explicit
Inbox instruction, not as an independent pre-existing defect or a claimed fix.
Review-again: the return restores byte-identical tracking code already covered by
Critical round 1, so it does not create another behavior-fix round. The strict
annotation migration is abandoned and its budget gate no longer blocks this run.

Critical round 1 had valid complete results and no Critical findings. With the
two Important limits explicitly accepted and no further behavior correction to
that reviewed code, the structural loop ends **clean at Critical**, subject to
those recorded limits. Counts remain Nit 1, Important 1, Important 2 and Critical 1;
they do not restart. The full local order continues with the focused review loop.
Its conclusions must preserve these limits and distinguish any additional defects.

The ready-PR go-ahead remains in effect. Each loop's end state is reported to
TOOLING. A Codex update prompt receives Skip only. If a “Hooks need review” picker
appears, it is left unanswered, TOOLING is informed and the worker stops.

## Focused Nit round 1 and conductor recurrence call

All five applicable focused aspects completed with exit 0, one nonempty
schema-valid reply, the expected snapshot and no lasting changes. Settings were
gpt-6.1-sol, high effort, window 872000, read-only, approval never, web disabled,
ephemeral and stdin closed. Code, errors and tests ran first; comments and types
followed within three concurrent review slots. Types applies to the new JSON
policy and report data shapes. No hook-review picker appeared. The restored
81-case guard document and make validate both exited 0.

| Aspect                                                  | Reviewer label | Our severity and impact                                                                | Take or record                                        | Review again                  |
| ------------------------------------------------------- | -------------- | -------------------------------------------------------------------------------------- | ----------------------------------------------------- | ----------------------------- |
| Code: escaped exec command                              | important      | Important: another persistent stdout mutation can bypass the guard                     | Take required; recurrence call below controls the fix | Yes, behavior                 |
| Errors: unexpected parser failure under named exception | important      | Important: crash or I/O failure can become a successful exemption and lose diagnostics | Take; independent parser-status correction            | Yes, behavior                 |
| Tests: coprocess capture boundary                       | important      | Important: a separate captured stream is misclassified as live                         | Take with negative case and positive control          | Yes, behavior                 |
| Comments: two markers inside quoted jq programs         | suggestion     | Nit: inactive markers misleadingly duplicate real shell annotations                    | Take as comment-only cleanup, preserving real markers | No independent behavior round |
| Types                                                   | none           | No finding                                                                             | No edit                                               | No                            |

Raw reports are saved as `2026-10-29-error-output-focused-nit1-*.json`. The
escaped-exec example is additional to the two explicitly accepted cases. The
focused loop's reported end state at the recurrence is **stopped: recurring
defect**, with Nit round 1 counted and no reset. Remaining already-running
comments and types have now been collected; neither adds an Important finding.
No failed aspect or partial result is called clean.

TOOLING supplied a conductor-owned structural call through a peer message under
the delegated Review rounds procedure. It is a scoped design decision within the
existing brief, not new user authorization: fail closed when stdout or stderr
context cannot be resolved statically, including unresolved escaped/quoted
command names with stream effects, undecodable exec redirections, coprocesses
and other unsupported stream-changing constructs. A diagnostic must name the
construct, and the existing reason marker may exempt the site. The two accepted
limits stay recorded, with any incidental closure noted. Before building this
change, count newly failing existing sites; more than ten requires another stop
and examples because it reopens the abandoned migration.

The same call directs an independent correction for parse exceptions: accept
only recognized syntax/AST limitations, fail on crashes, termination and other
unexpected failures, and retain the parser diagnostic with its unit name. Add
escaped-exec and coprocess boundary tests and confirm fixes with plants. The
comments/types results are included above. The focused count continues from Nit 1.

### Independent parser-failure correction

The named-exception path now distinguishes expected syntax failure from parser
failure: status 1 also requires the pinned parser's source-position diagnostic.
Crashes, termination, I/O diagnostics and empty failure output fail with the unit
name and retained diagnostic. A successful parser must return the expected File
AST; only the recognized multiline-comment AST limitation can justify that
exception. Invalid output shapes and jq failures cannot become exemptions.

Five added cases simulate statuses 139 and 143, I/O and empty status-1 failures,
and status-0 invalid AST output. The committed shfmt stub only intercepts the
marked static exception input and forwards all other inputs to the actual parser.
The fixture and stub both refuse to run unless shfmt resolves to the copied
committed stub, and the actual parser executable must be distinct. Makefile
registration and ambient-variable resets apply equally to local tests and CI.
Existing native syntax and known-comment-limit positive cases remain covered.
All 86 guard cases and make validate pass. No static sample program is executed.

The two inactive markers inside quoted jq programs were removed as the comment
aspect proposed; the actual shell reason comments remain. Generated mirrors were
regenerated with make build. The existing patch versions already cover this
branch's comment changes. These comment edits change no behavior; the parser fix
does and will be reviewed in the next focused round after the stream preflight.

### Parser plants and fail-closed stream migration preflight

After signed parser-fix commit `efde1628`, the actual prior orchestration library
from `ca337297` was planted. Each of the five new parser-failure assertions returned
status 0 with the earlier implementation and status 1 with the named unexpected
failure diagnostic before and after restoration. Allowed-probe, native syntax
exception and known-comment-limit controls passed in every phase. Exact source
bytes were restored. [Twenty-four measured rows](2026-10-29-error-output-parser-exception-plants.json)
retain stdout, stderr and statuses. The committed stub simulates parser failures;
no static sample shell program is executed. The comment cleanup is signed in
`a9bf3f5d`. All 86 guard cases, validation and shell lint passed before preflight.

The stream policy has not been built. A disposable copy of the current checker
captured its native shfmt AST and unit metadata while scanning the unchanged
repository; its normal guard passed. A separate read-only query applies the
proposed fail-closed criteria and the existing actual-comment reason scopes.
It identifies unresolved command heads with non-stdin redirects, persistent exec
stream redirects and coprocess contexts. Literal quoted names are resolved when
the existing decoder can resolve them. Stdin-only redirects and assignment-only
calls are excluded. Multiple candidates covered by one parsed command-end line
count once; existing valid reason markers are excluded.

This conservative interpretation produces **409 newly failing command sites in
35 files**, covering 431 risk constructs: 429 unresolved-command redirections and
two persistent-exec sites. [Count, exact scope, file totals and source samples](2026-10-29-error-output-fail-closed-preflight.json)
record the measurement. Examples include the attention-log `exec > /dev/null`,
the two review-scope `"$@"` raw-output producers, and the guard fixture's
variable-named checker writing scope JSON. The interpretation also includes many
variable-named binary invocations with stderr merges. No new reason was added.

Separate static probes through that same query identify escaped exec, coproc and
both previously accepted cases. Thus the proposed policy would close both accepted
cases as well, subject to explicit site reasons. This is preflight evidence, not
an implemented fix or proof that the current guard detects them. The tracking
implementation and the accepted-limit documentation remain unchanged.

The count is above the conductor's ten-site threshold. The migration gate is
therefore closed and the count and examples have been sent to TOOLING. No stream
rule, new escaped-exec/coproc regression implementation, next review round, trim,
baseline Semgrep, final checks, tidy, push or PR follows without direction. The
independent parser correction and plants are complete and remain for review.
All five focused aspects completed validly; types had no finding and the comment
suggestion was taken. The loop count remains focused Nit 1, stopped: recurring
defect, with the selected structural correction now held at its migration gate.

## Narrowed rare-form call and implementation

TOOLING relayed the 2:44 PM ET Inbox answer: fail closed only on the rare forms,
including escaped or quoted exec, persistent exec redirects and coproc; ordinary
`"$@" > file` calls stay unchanged. The ten-site preflight gate remains. This
narrows the conductor's previous class-wide interpretation within the existing
brief; it does not authorize a general command-name migration.

A read-only query over the same native AST, with executable inputs verified
unchanged since capture, identifies **two** unreasoned sites: attention-log's
hook stdout suppression and ledger-concurrency's FIFO descriptor. The
[preflight record](2026-10-29-error-output-rare-preflight.json) includes both
sites and static probes for escaped/quoted exec, coproc, the two accepted
examples, ordinary variable commands and quoted non-exec calls. Both accepted
examples produce candidate diagnostics; ordinary controls do not. The count is
below ten, so the selected change proceeds without reopening the larger migration.

The evaluator now resolves literal command/builtin prefix structure recursively
and identifies persistent exec redirections and rare unresolved literal-only
command names that could dispatch exec. Dynamic variable command heads keep
their prior behavior. Coprocess contexts fail closed and their stdout is treated
as captured. The existing parsed comment marker can exempt each construct.
The diagnostic names the unresolved construct. Tracking for supported contexts
remains, with no general descriptor-2 annotation requirement.

The two existing sites now have actual reasons: hook stdout must remain silent
so it cannot be interpreted as a decision, and the owned FIFO descriptor stays
open for the reservation barrier. No other existing annotation was added.
Thirteen static cases cover the new failures, both accepted examples, explicit
reasons, named coprocesses, quote forms and unchanged ordinary controls. Their
shell programs never execute. All 99 cases and repository validation passed.

Before the next review, an additional parser-I/O boundary was hardened: the
parser diagnostic is cleared before invocation, and its stderr redirect opens
before stdin. A missing input cannot leave a stale source-position diagnostic
that grants an exception. The direct regression starts with a stale syntax
message and verifies the input-open diagnostic replaces it and is not a syntax
exception. All 100 cases pass. The pinned parser source also confirms reader
I/O errors are stored directly by
[Parser.fill](https://github.com/mvdan/sh/blob/v3.14.1/syntax/lexer.go), supporting
the distinction from position-bearing syntax diagnostics.

Both original accepted cases are now rejected by the unannotated rare-form gate;
the tracking limitations remain documented and no persistent-state proof is
claimed. Code and test findings from focused Nit 1 are taken, as is the independent
parser correction. Each retains Important severity and requires behavior review.
The comment-only cleanup needs no separate round; types had no finding. The
focused loop advances to Important round 1, with all earlier counts preserved.
Earlier-implementation plants will be recorded after this check-and-test commit.

### Rare-form and input-open plants

After signed commit `88014a87`, the actual earlier JQ evaluator from `a9bf3f5d`
was planted. Escaped exec, coproc, saved-alias mutation and composed-prefix
regressions all changed from the named stream-context error and status 1 to
success and status 0. Four controls, including ordinary variable commands and
explicitly reasoned rare forms, passed in every phase. Source bytes were restored.

The earlier parser wrapper from `a9bf3f5d` was then planted in the actual Bash
library. Its stale diagnostic caused the missing-input assertion to fail with
“missing input was accepted as a syntax exception”. The corrected wrapper passed
before and after restoration. No missing-helper or neighboring failure was used
as evidence. [Twenty-seven measured rows](2026-10-29-error-output-rare-plants.json)
retain the statuses and outputs. The static shell programs were never executed.

A read-only main-integration preview found conflicts with pinned main commit
`7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`. Canonical conflicts combine this
branch's annotations with main's owner-lock, notification-backend and launch
changes. Integration preserves main's logic and applies the existing annotation
policy; manifests take main plus a patch and generated mirrors are regenerated.
No pushed history exists or is rewritten. A behavior conflict that cannot be
reconciled still stops for TOOLING. The next review uses the resulting immutable
merge-base SHA, not a moving origin/main reference.

## Main integration and renewed rare-site migration gate

Main at `7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71` must be integrated for a
mergeable PR. Conflicts were resolved by preserving main's owner-lock,
notification-backend and launch logic, with existing reasons retained where
the same command remains. Removed or changed sites are logged for review.
Main's versions receive the branch's patch increment; generated mirrors were
taken from main and regenerated. No generated file was hand-merged. The checker
has no textual conflict and retains the fixture-environment graph and AST guard.
Three new jq helpers have explicit, language-specific non-Bash exclusions.

A complete native AST inventory of the resolved tree passes parsing and the
fixture graph, but returns 1 for unreasoned redirects. It identifies **13 new
rare-form instances**: four operations in the canonical workmux owner-lock helper,
repeated in its two generated plugin copies, and one rollout-reader descriptor.
These are **five canonical source sites plus eight generated instances**.
[The measured sites and kind totals](2026-10-29-error-output-main-integration-count.json)
retain their actual source. Owner-lock closes descriptors 8 and 9 and reserves
those same descriptors for identity retention; the rollout watcher opens
descriptor 3 to retain its reader. None received a new reason after this count.

Thirteen is above the explicit ten-site gate. TOOLING receives the physical and
canonical counts and examples before any exception is added. The worker does
not silently collapse the count or weaken the classifier around these auxiliary
descriptors. The merged guard also reports 56 ordinary unreasoned discard/capture
findings from new or changed main code. Those remain for individual review and
seeding under the original brief once this gate is resolved. No merged-tree
validation or test pass is claimed, and focused Important round 1 has not begun.

The merge is recorded as a signed commit with both parents retained. The next
review pins the exact resulting merge base, not a moving origin/main. Existing
loop counts and accepted-limit history remain. No pushed history was rewritten,
no force push or PR occurred, and no hook-review picker appeared. The rare and
input-open plants and the 100-case guard pass reported above precede integration;
they do not certify this merged tree. The current closed gate is the newly
measured rare-site budget.

### Main migration gate reopened by the Inbox answer

TOOLING relayed the Inbox answer from 5:02 PM ET on 2026-10-29: give the five
canonical source sites real reasons, regenerate their copies, and retain the
rare-forms rule. The four owner-lock operations now explain retained descriptors,
checked status and replayed diagnostics. The rollout reader explains its owned
input descriptor and live open errors. Generated owner-lock copies are rebuilt
from the canonical workmux source. Any further rare-form site beyond these five
still stops for TOOLING.

Each ordinary finding was reviewed individually, including generated repetitions.
[The site review](2026-10-29-error-output-main-site-review.json) records original
source and each reason or local fix. Two directory-creation failures in
attention-log suppressed useful errors before returning failure; their stderr is
now live. Retained owner-lock diagnostics already have explicit failure reports,
so those sites document that protocol. Test captures assert or replay their
retained output and status. Other annotations explain process predicates,
exclusive claims, optional metadata or transcript-refusal predicates. No new
follow-up issue was filed. The merged validation and focused Important round 1
remain pending, pinned to merge base
`7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`.

The post-merge AST inventory now returns zero findings, with no additional
rare-form site. Merged lint and repository validation pass. An initial validation
was started while mirror regeneration was still running; its missing generated
file result is invalid and retained only as invocation evidence. The completed
build was followed by a successful validation run. Initial lint identified seven
manifest formatting differences, corrected with the repository formatter.

The repository's check-versions skill was applied against the frozen main merge
base. Main had caught up with the branch's dependabot and monitor-pr patch
versions while their reason annotations still differed; both receive a forward
patch increment. [The resulting audit](2026-10-29-error-output-merged-versions.json)
finds all ten changed plugins forward-versioned, present Codex manifests matching,
and complete marketplace coverage with versions owned only by manifests.

The six explicitly requested pre-existing scope decisions were rechecked against
the new main merge base using normalized executable ASTs. All compared functions
remain identical, including the unavailable metadata, symlink, origin diagnostic,
filename, inventory and issue-stream paths. [The merged scope evidence](2026-10-29-error-output-merged-deferred-scope-audit.json)
retains each function and digest. These findings keep Important severity and the
individual outside-branch reasons above; no own-code defect is deferred by that
comparison.

Merged validation completed: all 53 Scrut documents passed, with 1923
testcases, zero failures and zero skipped cases. The dedicated guard run also
passed all 100 cases. Merged lint, make validate and the macOS Bash 3.2 checker
passed. These results precede focused Important round 1 and keep all prior
review counts.

## Focused Important round 1: required review tool unavailable

The five focused aspects were selected at immutable base `7a6997e7` and signed
head `aec2f845`, preserving the completed Nit round and all structural counts.
Code, errors and tests launched concurrently with `gpt-6.1-sol`, high effort,
872000 context window, read-only sandbox, approval policy never, web search
disabled, ephemeral sessions and closed stdin. Each printed its read-only review
intention, then the code-mode host negotiation timed out three times. No
repository read or review reply completed. This is a required-tool failure,
not evidence of zero findings.

The brief names a missing tool as a stop. All three owned reviewer processes
received TERM and were observed stopped with exit status -15; the controller
exited 1. Comments and types never launched. There was no rerun or fallback and
no hook-review picker. The before/after scope comparison found no lasting
changes, index movement or snapshot invalidation.
[The completion record](2026-10-29-error-output-focused-important1-tool-stop.json)
retains actual statuses and diagnostics. Full prompts, logs, PIDs, schema,
membership and snapshots are archived in the worker mailbox's
`artifacts/focused-important1-tool-stop` directory.

Focused Important round 1 remains incomplete. No clean threshold is claimed;
prior review counts are retained. Merged checks reported above remain passes,
but trims, Semgrep, final test-all, tidy, push and PR creation have not run.
TOOLING receives this stop and decides how the unavailable review capability is
restored before the brief continues.

### Repaired host and review-monitor invocation error

TOOLING reported the host repaired and directed resumption on 2026-10-29. The
five selected aspects resumed with the same model, effort, window, immutable base
and preserved counts, using Codex CLI 0.166.0. Code, errors and tests performed
repository reads successfully. During this step TOOLING temporarily directed a
hold after the current step, then confirmed restart authority under the Inbox
answer “Resume after the measurement” and the ramp rules' continuing-work clause.

The immediate-timeout monitor incorrectly matched historical diagnostic strings
printed as changed JSON evidence. It terminated the three active aspects before
any reply; comments and types never launched. There was no actual code-mode-host
timeout in this invocation. All three owned reviewers were observed stopped,
and the snapshot comparison found no lasting changes. This is a failed
invocation, not a review round or a clean result. The earlier actual-host-failure
launches likewise remain failed runs, not completed rounds.

[The invocation evidence](2026-10-29-error-output-review-monitor-invocation.json)
records statuses and the diagnostic comparison. The corrected external monitor
matches only timestamped router error records. It detects all three actual
errors in each old failing log and zero errors in each current reading log,
without treating quoted source as a live error. No replacement was launched.
The failed completion is reported to TOOLING before a replacement is attempted.
Focused Important round 1 remains pending, with all earlier counts preserved.

## Focused Important round 1 completed

TOOLING authorized one corrected launch, with continuing permission to correct
monitor-only invocation failures. The monitor uses timestamped router ERROR
records and leaves quoted diagnostics alone. The corrected invocation completed
all five aspects with Codex CLI 0.166.0, `gpt-6.1-sol`, high effort, 872000 window,
read-only sandbox, never approvals, disabled web search and closed stdin. Every
process exited 0 with a nonempty schema-valid reply at immutable base `7a6997e7`
and head `fd719462`. The snapshot comparison found no lasting changes or scope
movement. No host error or hook-review picker appeared. The earlier two failed
invocations remain failures, not rounds.

| Aspect                                                               | Findings                                  | Completion |
| -------------------------------------------------------------------- | ----------------------------------------- | ---------- |
| [Code](2026-10-29-error-output-focused-important1-code.json)         | None                                      | Valid      |
| [Errors](2026-10-29-error-output-focused-important1-errors.json)     | None                                      | Valid      |
| [Tests](2026-10-29-error-output-focused-important1-tests.json)       | One Important boundary-coverage finding   | Valid      |
| [Comments](2026-10-29-error-output-focused-important1-comments.json) | One suggestion about an inaccurate reason | Valid      |
| [Types](2026-10-29-error-output-focused-important1-types.json)       | None                                      | Valid      |

The tests finding keeps reviewer label `important` and Important severity:
existing exec-rejection cases could mask removal of the later-merge check.
Decision: take. A new static negative case reasons only the exec and requires
status 1 plus the capture diagnostic for the later merge. A positive control
reasons both operations on separate lines. The samples never execute. This adds
coverage for existing behavior, with no evaluator change or new design.

The comments finding keeps reviewer label `suggestion` and Nit severity:
the detached-launch reason incorrectly promised status before a timeout returns.
Decision: take as a trivial local wording correction. The reason now says status
is saved on completion and a timeout preserves the state directory. Generated
output is rebuilt from source. It changes no executable behavior.

| Measured plant                                             | Instrument                            | Measured result                                      | Committed regression                      |
| ---------------------------------------------------------- | ------------------------------------- | ---------------------------------------------------- | ----------------------------------------- |
| Remove block-wide stdout uncertainty from Scrut forwarding | Later unreasoned-merge rejection case | Three rejection judges fail; positive control passes | Allowed exec followed by unreasoned merge |

The new cases and their positive control are checked before the plant. This
round requires no successor for these test and comment changes; the final loop
end state will be recorded after validation and the measured plant.

### Allowed-exec boundary validation and plant

All 102 guard cases passed before signed test commit `c8c85be2`. The actual
JQ evaluator was then weakened to ignore block-wide exec stdout uncertainty,
while preserving rare-form checks. The reasoned exec no longer masked the
measurement: the later unreasoned merge changed from status 1 and its capture
diagnostic to status 0 and the success message. The positive control remained
successful. Scrut ran the two committed cases plus status-only and diagnostic-only
judges: the plant produced one pass and three failures, each on the named merge
contract. All four passed before and after exact source-byte restoration.
[The measured rows](2026-10-29-error-output-allowed-exec-plant.json) retain actual
statuses, diagnostics and the restored evaluator digest. Static samples never
executed. No stub was added.

The focused loop end state is **ended: fixes changed no behavior**. Its counts
are Nit 1 and Important 1; the two unavailable-host and monitor-error invocations
are failed launches, not rounds. The existing guard behavior is unchanged and
its missing boundary coverage is now explicit. The launch reason is corrected
and its generated mirror rebuilt. All five valid Important-round outputs and
full capture evidence are retained. The next local step is the single read-only
comment and prose trimming round.

## Comment and prose trim round

Both read-only Codex dry runs completed with `gpt-6.1-sol`, low effort, 872000
window, never approvals, disabled web search and closed stdin. The exact
classified file lists cover all 51 eligible comment files and 31 prose files.
Their before/after scope comparison found no lasting changes. The comment pass
proposed no edits. The prose pass proposed six rewrites, all taken after checking
meaning, requirements, recorded facts and unchanged links. Guard directives,
literal fixtures, raw review evidence and recorded decisions remain protected.
[The trim record](2026-10-29-error-output-trim-results.json) retains each complete
before/after proposal, file membership and exclusions. Prose formatting and
Markdown checks pass. No source behavior changed, no new review round is needed,
and no host error or hook-review picker appeared. Trim end state: **ended: fixes
changed no behavior**. Baseline Semgrep is the next local step.

## Baseline Semgrep

Semgrep 1.180.0 ran in an owned disposable `git clone --shared` of signed head
`14a64005`, with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins` and command
`semgrep scan --config auto --baseline-commit 7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71 --json`.
Metrics retained their default behavior. Exit status is 0, with zero findings,
138 rules and 117 changed targets scanned. The native baseline-aware scan
selected changed files from the pinned base; Semgrep omitted its second baseline
pass because the current pass had no findings. No full-scan substitute was used.

Coverage is approximately 87.7 percent of parsed lines, with 33 Bash targets,
78 JSON targets and one YAML target reported; 157 files matched ignore patterns.
Eleven Bash scripts have parser limitations: two Syntax error records and nine
PartialParsing records. No other language has a parser error. ShellCheck passed
on all eleven scripts. The standing 9:39 PM ET rule from 2026-10-28 therefore
applies, retaining the limitation rather than claiming complete Semgrep coverage.
[The baseline record](2026-10-29-error-output-semgrep-baseline.json) names every
unparsed or partly parsed file, spans, tool version, coverage and ShellCheck
result. Full output and the clone metadata are archived in the worker mailbox.
The next step is mandatory lint-and-fix with no push, followed by final test-all
and the repository version audit before exact-tree tidy.

## Final local checks

The mandatory `lint-and-fix --no-push` step used the documented `make format`
command and made no changes. Its verification ran all documented lint tools
through the `lint` prerequisite of `SCRUT_JOBS=4 make test-all`. Markdownlint,
Prettier, ShellCheck, shfmt and actionlint passed; no required work was skipped
or downgraded. No lint-fix commit was needed.

Final `make test-all` exited 0: all 53 documents and 1,925 tests passed, with zero
failures or skips. All 102 guard cases are included. The checker also passed
under macOS Bash 3.2.57. The repository check-versions skill then passed against
the frozen merge base: all ten changed plugins have forward patch versions,
present Codex manifests match current and baseline Claude manifests, and all
60 catalog plugins have complete coverage with versions owned only by manifests.
[The final validation record](2026-10-29-error-output-final-validation.json)
retains observed totals, versions, commands and tool output. Full logs are archived.
Only this validation metadata is added after the source checks; formatting,
Markdown and JSON validation cover that metadata before the signed tidy.

The branch has no remote head and no open PR. The next action preserves a local
backup, rebuilds the unpublished history as signed feature, test and documentation
commits, and verifies an identical stored tree before publication. No pushed
history is rewritten. The PR will close the discarded-error-output issue and
remain for TOOLING to merge.

## Published PR: incoming-main integration stop

The unpublished tidy created three signed commits and verified stored tree
`cbf9aee10eb0e71de11f617c2d2eccd0cb3f4cd8` identical to the pre-tidy backup.
Backup branch: `fix/672-guard-error-discards-pre-tidy-20261029191301`.
Published head `736147778a71db99d4c3774c2ec06b27f5e34361` is open ready for review
as [the error-output guard PR](https://github.com/cboone/agent-harness-plugins/pull/690).
No history was rewritten after publication.

GitHub reports CONFLICTING and DIRTY against the newer main; its opening snapshot
reports no checks. A read-only merge-tree preview against frozen incoming main
`5205fada80635f7d9dd4a1967c94a256e60a99cb` exits 1 with nine conflict paths.
[The integration record](2026-10-29-error-output-published-integration-stop.json)
retains the paths, preview tree, GitHub state and verified local checks.

Main adds a fixed review-fixture manifest check under `--review-paths` in the
same checker, changes fixture-operand handling and CI coverage, and deletes the
rollout mkdir stub this branch annotated. Reconciliation must preserve that
entry point, every fixture rule, the AST guard, new CI coverage and the guard's
unconditional shfmt dependency. Generated conflicts require regeneration.
These are reported to TOOLING before selecting an integration or review-base
continuation. No actual merge or source resolution has begun. The published
source remains unchanged; this local documentation records the stop without a
further push. The PR is not green or ready for the final review précis yet.

### Authorized integration: additional rare-site gate

TOOLING authorized one signed merge of incoming main, preserving both checker
modes, all rules, unconditional shfmt and new CI coverage, fixture hardening and
main's fixture deletion. The resolved tree keeps the exact incoming
`--review-paths` dispatch alongside the existing graph and AST guard. Generated
copies were regenerated; five plugin versions advance above main. The new jq
review-path contract has a named language-specific exclusion. Resolution
automation was corrected before any commit; original conflict inputs were
restored, the resolved Bash programs passed Bash 3.2 syntax checks and the build
completed. No published source was changed.

The complete native AST inventory finds four additional rare-form commands,
all in `tests/fixtures/check-codex-failures`: read/write FIFO opens on descriptors
4, 5 and 6, and a combined closure after both children are reaped. These are four
canonical and physical sites, with no generated repetitions. No new reasons
were added to them. The earlier instruction requires a stop for any additional
rare-form site beyond the five approved, so the signed merge is held pending
TOOLING's direction. [The gate record](2026-10-29-error-output-integration-rare-site-gate.json)
retains actual sites, proposed reasons and the eleven ordinary capture findings
still awaiting review and seeding. The rule was not weakened.

The merge remains in progress against `5205fada`, with all textual/index conflicts
resolved but no merge commit. This record stays uncommitted with that merge;
a partial documentation commit cannot preserve the requested single signed merge.
No focused review has started and no review count advances. The known upstream
lint-shell operand-contract failure is unchanged. TOOLING receives the new-site count before any
further exception or source change.

TOOLING approved the four FIFO reasons as proposed, without a classifier change.
The five previously approved source sites plus these four make nine; any further
rare-form site stops again. Each FIFO open and the closure now carries its own
written reason. Eleven ordinary captures were reviewed: two GNU-stat dialect
probes select a checked BSD fallback, seven native-Bash snapshots assert failure
diagnostics and status, and two mutation snapshots retain diagnostics while
asserting failure and empty stdout. Each receives its actual reason. The
review-scope copies remain byte-identical. These are annotations for existing
protocols, with no executable weakening or hidden follow-up.

The accepted AST inventory passes across 2,088 units with eighteen named
non-Bash exclusions and zero findings; the fixture graph passes too. Both
checker modes are preserved. Under Bash 3.2, the review-path mode passes all
eight other fixed-manifest files and reports only the known incoming-main
operand-contract failures in the unchanged review-submodule fixture at lines
132–134 and 254. This is the reported lint-shell failure, not a ShellCheck
parser failure. The upstream file is byte-identical to main and remains untouched.

The integration is recorded as one signed merge, without rebasing or rewriting
published history. Its focused review uses immutable base `5205fada` and the
existing Important-round count advances to round 2, as directed for this behavior
change. Full checks follow the review. No additional rare site appeared beyond
the nine approved.

## Focused Important round 2: incoming-main integration

The integration review used fixed base `5205fada` and signed merge
`54d3d451`, preserving the existing focused Nit 1 and Important 1 counts.
Code, errors and tests completed with valid output and no findings. The first
comments reply returned a different snapshot identifier, so validation failed;
types was cancelled without a reply. No invalid prose was used or repaired.
The unchanged snapshot allowed the three valid replies to be retained.

TOOLING authorized comments and types to complete the same round, with
`reviewed` bound to the required snapshot in the native schema. Both returned
valid output and no findings. All five successful replies name snapshot
`445aa43eee880cf6c8eb77f2b3212ec910d69c5d`; every process exited 0, with no
lasting source or scope changes. Settings remained `gpt-6.1-sol`, high effort,
872000 window, read-only sandbox, never approvals, disabled web search and closed
stdin. No actual host error or hook-review picker appeared.

[The completion record](2026-10-29-error-output-focused-important2-integration-status.json)
identifies retained and completed aspects. Raw successful replies and full
failed/completion captures are retained. The focused loop end state is
**clean at Important**, with counts Nit 1, Important 1 and Important 2.
No finding requires a further behavior round. Post-merge checks follow; the
known incoming-main operand-contract failure remains assigned elsewhere.

## Validation finding: mode-specific dependencies

The post-merge full run completed all 57 documents: 1,983 tests, with 1,981
passes and two failures in environment isolation. One is the known incoming-main
operand contract. The other is an Important integration defect: a public
review-path fixture intentionally copies only that mode's dependencies, but
unconditional AST-library imports prevented dispatch and lost its expected
source-line diagnostic. Reviewer label: testcase unexpected exit code; severity:
Important; decision: take; review again: behavior changes.

Signed fix 3db6289e moves the AST and capture-library imports after the early
review-path dispatch. No classifier, mode rule or upstream fixture changed.
The focused public regression now rejects the unprotected Scrut command at line
4 and accepts its protected control. The normal checker passes under Bash 3.2;
a bare-discard control still fails with the expected diagnostic.
[The fix record](2026-10-29-error-output-lazy-mode-fix.json) retains measured output.

TOOLING directed Critical round 1 for code, errors and tests, keeping the two
Important rounds already used. Its threshold is Critical-only: take Critical
findings and record lower findings. Comments and types are omitted because this
fix moves existing directive text and changes no data model. The fixed review
base remains 5205fada; full checks follow this confirmation. The incoming-main
operand defect remains assigned elsewhere.
