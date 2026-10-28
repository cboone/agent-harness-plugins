# Fixture environment isolation ledger

## State

The Semgrep overlap condition passed, so TOOLING's validation call accepts the
scan as complete for this branch. General review is clean at Important and
final trims are applied. Hostile full-suite checks, caller checksums, final
lint/build and versions pass. This ledger freezes the pre-publication candidate;
the workstream report records the history tidy, PR and CI outcome.

Authorization: build through a ready PR, relayed by TOOLING from the Inbox
thread "Tooling next batch", 2026-10-28 at 9:16 AM ET. Workers never merge.

## Evidence

- Read the complete bodies and empty comment lists for
  [catalog signing](https://github.com/cboone/agent-harness-plugins/issues/540)
  and [validation budgets](https://github.com/cboone/agent-harness-plugins/issues/519).
  Both remain open and received the `in progress` label.
- Repository ownership check: `cboone/agent-harness-plugins`, active, not a fork.
- `corepack yarn install --immutable` passed.
- At reproduction, HEAD and `origin/main` were both `93f8427c`.
- A temporary global Git config enabled signing with an unusable signing key
  and `/usr/bin/false` as the signing program. Running the catalog fixture's
  `root-docs` case exited 128: GPG could not sign the first commit.
- `CODEX_REFERENCE_CONTEXT_WINDOW=1 make validate` exited 2. Plugin validation
  rejected 3674 inventory tokens against negative available capacity. Its log
  is `/tmp/540-budget-before.log`.
- Fetch subsequently advanced `origin/main` to `84b350ef`. No merge or rebase
  was performed; the hostile runs have not been repeated on that newer tree.

## Changes awaiting validation

- Clear current budget overrides at `make validate`; CI uses the same target.
- Clear ambient Git config in the catalog, corpus and notification fixtures.
- Reset budgets and generator path overrides before validator fixture cases
  apply their intentional scenario overrides.
- Add a registered hostile-environment fixture and six Scrut cases covering
  commit signing, tag signing, each current budget variable and fixture budgets.

## Development checks

The first scoped ShellCheck run exited 1 with SC2249 at line 26 of
`tests/fixtures/environment-isolation`: its nested case needs a default arm.
TOOLING clarified that fixable findings in new code are ordinary development,
authorized continuation, and requested stable signing snapshots. The default
arm is now present and the scoped ShellCheck run passes. Workflow tag stderr
is captured and replayed on failure, preserving the extracted workflow code.

The isolated Scrut document, running when lint failed, finished with exit 2:
four budget cases passed and two signing snapshots failed because the helper
combined successful Git push stderr with stdout. The signing operations completed. Log:
`/tmp/540-isolation-tests.log`. No background test process remains.

The corrected six-case document passed, with zero skipped cases. Two added
cases independently passed for command-config signing and corpus commit hooks.

## Inheritance sweep

| Surface                                                                                | Treatment                                                                                                           |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Catalog, corpus and notification fixture Git calls                                     | Ignore global, system and environment-injected config in each fixture.                                              |
| Inline Git histories in backlog, bugs, review-scope, codex-aspects and resource claims | Reset Git config in document setup, before Git operations.                                                          |
| Suite Git config                                                                       | Retain existing empty global/system files; clear command-config injection locally and set empty injection in CI.    |
| Validation gate                                                                        | Clear all three current budget overrides and the generator's ambient source catalog; CI calls the same Make target. |
| Validator fixture                                                                      | Clear budgets and generator paths before applying each scenario's deliberate overrides.                             |
| Generator tests                                                                        | Clear path overrides at suite entry; direct command-specific overrides remain intentional API coverage.             |
| Codex stub                                                                             | Clear ambient modes and result controls at suite entry; document setup clears modes before its first case.          |
| Other executable stubs                                                                 | Existing SCRUT_UNSET entries isolate their deliberate controls; each testcase supplies needed values.               |
| Corpus directory, TMPDIR, PATH and REPO_ROOT                                           | Intentional inputs identifying test trees, scratch storage and executable dependencies; retain them.                |
| Direct validator budget overrides                                                      | Intentional lower-level API for boundary cases; the repository gate removes ambient values.                         |

No real user configuration was changed. Only the explicitly requested locked
repository dependencies were installed.

## Structural review, Nit round

Fresh read-only Codex runs used `gpt-6.1-sol`, high effort and an 872000-token
window. The anti-pattern result passed its schema and completion checks. No
lasting changes were found between the before/after review snapshots.

| Reviewer label                                        | Our severity                                                      | Take or record                                                                                              | Review again                            |
| ----------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| important: GIT_CONFIG redirects fixture writes        | Important: fixture setup can modify a caller-selected config file | Take: clear all exported Git variables through one sourced fixture helper; add an unchanged-file regression | Yes, behavior changes                   |
| important: GIT_TEMPLATE_DIR supplies executable hooks | Important: fixture commits still depend on caller hook templates  | Take: the shared helper clears this input too; add a template-hook regression                               | Yes, behavior changes                   |
| suggestion: flatter validation branch                 | Nit: readability only                                             | Take: replace the nested conditional with elif                                                              | No additional round for this edit alone |

The shared helper resets exported Git variables before fixture-specific
identity and date settings. This closes the class rather than extending the
list of individual environment variables. Both added regression cases pass
under macOS `/bin/bash`.

The first simplify launch was incomplete after the repository helper correctly
refused self-review. The process was stopped by its recorded PID, 95850. The
installed helper rendered the corrected run, which passed output validation.
The incomplete launch has no clean result and consumed no review round.

## Structural review, Important round

The anti-pattern and report-only simplify runs completed with valid output.
Both used `gpt-6.1-sol`, high effort and an 872000-token window. The simplify
run found no further suggestions. Snapshot checks found no lasting changes.

| Reviewer label                                           | Our severity                                                                                                      | Take or record                                                                                                       | Review again                       |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| important: preserve deliberate budget inputs             | Important: existing one-percent, invalid-budget and full-catalog tests lose their explicit controls               | Take pending continuation: use explicit fixture arguments for intentional overrides and preserve existing assertions | Yes, behavior changes              |
| important: reset the corpus caller's Git environment too | Important: a caller's GIT_DIR survives fixture child isolation and redirects or prevents caller-side corpus reads | Take pending TOOLING's structural decision; this repeats the inherited-Git-input class                               | Yes, after the recurrence decision |

Independent confirmation: the existing `empty-context-window` case with both
deliberately invalid overrides produced one error instead of its expected
three. Evidence is in
`/tmp/540-deliberate-overrides-before.log`. No correction followed the stop.

Proposed structural fix: isolate every testcase's caller before Git consumers,
including the environment regression helper and review-corpus document, rather
than relying on fixture subprocesses to change their parents. Sweep creation
and consumption paths together. Add a hostile caller-side `GIT_DIR` regression
with its own disposable repository and verify that repository stays unchanged.
For budget tests, expose explicit fixture arguments and update the existing
intentional callers without loosening any expected output.

End state: **stopped: recurring defect**. Counts remain one Nit and one
Important round in the combined structural loop. The next round, if authorized
after behavior fixes, is its second Important round. General review has not
started.

## Regression and plant results

The ten-case hostile-environment document passed with no failures or skips.
This does not cover the newly identified caller-side gap. Log:
`/tmp/540-ten-cases.log`.

Ten removal plants in a disposable clone each failed at the corresponding
helper invocation, and restoring each file left the clone unchanged:

| Plant                                        | Observed exit |
| -------------------------------------------- | ------------- |
| Remove shared reset: commit signing          | 128           |
| Remove shared reset: tag signing             | 128           |
| Remove shared reset: command-config signing  | 128           |
| Remove shared reset: configured corpus hooks | 1             |
| Remove shared reset: caller config file      | 1             |
| Remove shared reset: template hooks          | 1             |
| Remove gate context-window unset             | 2             |
| Remove gate enabled-percentage unset         | 2             |
| Remove gate reserve unset                    | 2             |
| Remove fixture budget reset                  | 1             |

Artifacts, reviewer JSON, logs and plant scripts are under
`/tmp/540-validation.k7vCzE/`. The second plant run is `plants-r2.log`.
All started reviewer and regression processes have finished.

## Remaining verification

TOOLING authorized entry-point isolation and a suite guard, plus explicit fixture
budget arguments. The shared reset now lives in `bin/lib/git-environment.bash`,
which repository tools and fixtures can both source. Git consumers and their
testcase callers reset independently at entry.

`bin/check-fixture-environments` scans script sources and Scrut command lines,
follows literal helper names and Makefile registrations, and requires a reset
as the first command after strict-mode setup. It is part of `make validate`
and has dedicated missing-reset, new-consumer and late-reset cases. The guard
passed after identifying the previously missed entry points.

The outer `GIT_DIR` regression checks the selected Git directory and compares
checksums for every file in a disposable caller repository. Removing the outer
entry reset failed with `corpus used the caller Git directory`, exit 1. A
deliberately changed caller file is a permanent negative control. Weakening the
comparison to compare its first input with itself made that negative control
exit 0 instead of its required 1, so the test rejects the weakened assertion.
The missing-reset guard plant is also a permanent negative testcase and exits 1.

Deliberate budget callers now pass fixture arguments. The empty-context-window
case again prints all three expected errors, with its assertions unchanged.
Evidence: `/tmp/540-deliberate-overrides-after.log`.

The expanded regression document passed all 17 cases, and the existing catalog
document passed all 14 cases, with zero failures or skips. Logs:
`/tmp/540-entry-stable.log` and `/tmp/540-catalog-options.log`.
An earlier run overlapped script edits and reported an unbound local after
successful validation; the stable-source rerun above passed. No pass is claimed
for the failed run.

## Structural review, second Important round

Both fresh read-only runs completed with valid outputs, using
`gpt-6.1-sol`, high effort and an 872000-token window. The anti-pattern review
read all 35 changed files and found no Important defect or inherited-input
recurrence. Before/after snapshots matched with no lasting changes.

The report-only simplify run suggested removing the guard's redundant
earliest-consumer scan. Our severity: Nit, redundant work without an incorrect
verdict. Take: removed the scan; requiring the reset first already enforces
ordering. Review again: no, behavior is unchanged; rerun positive guard and
missing/late-reset controls passed.

End state: **clean at Important**. Final structural count: one Nit and two
Important rounds. General review starts at its own Nit round. Trims, Semgrep,
full checks, versions, tidy and PR remain. Both issue labels remain set.

## General review, Nit round

The installed `codex-aspects` helper ran code, errors, tests and comments in
parallel, read-only, with `gpt-6.1-sol`, high effort and an 872000-token window.
All four process statuses and schema checks passed; before/after snapshots
matched. Types were omitted because no type or schema changed.

| Reviewer label                                                  | Our severity                                                                  | Take or record                                                                                                            | Review again                        |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| important, errors: failed fixtures discard captured diagnostics | Important: child failures produce blank test reports after cleanup            | Take: replay child diagnostics on stderr and preserve their exit status; committed failing fixture stub covers both paths | Yes, diagnostic behavior changes    |
| important, tests: generator-path isolation is untested          | Important: regressions could redirect or replace caller-selected output paths | Take: inject all path overrides after suite setup and check disposable sentinels plus successful validation               | No additional round for tests alone |
| suggestion, tests: indirect consumers lack negative controls    | Nit: the guard exists but transitive helper and registration paths need tests | Take: permanent negative controls cover literal helper calls and registered-variable callers                              | No additional round for tests alone |

An additional testcase pins all three explicit budget arguments against hostile
ambient values. The 23-case expanded document passed before strengthening the
alternate source-catalog input. That input now changes metadata, which the
validator checks; changing only its name let the source-path removal plant
remain green. The stronger positive control passes, and removing the source,
marketplace or distribution override reset makes its Scrut testcase fail.

All remaining plants completed in
`/tmp/540-validation.k7vCzE/general-plants`, using real Scrut assertions. Positive
controls passed. Each of four generator resets, three fixture arguments, two
indirect guard paths and two diagnostic replay paths failed its matching test
when removed or weakened. All planted files were restored. Log:
`/tmp/540-validation.k7vCzE/general-plants.log`.

## General review, Important round

The same four aspects completed with valid outputs and process statuses,
read-only with `gpt-6.1-sol`, high effort and an 872000-token window. None
reported a finding. Before/after snapshots matched, with no lasting changes.

End state: **clean at Important**. General count: one Nit and one Important
round. No additional inherited-input instance was reported. Trims, Semgrep,
lint, full checks, versions, tidy and PR remain.

## Trims

One report-only `trim-comments` run and one `trim-text` run completed read-only
with `gpt-6.1-sol`, low effort and an 872000-token window. File coverage and
reply shape checks passed. Applied two comment rewrites and three prose
rewrites, preserving directives, test contracts and evidence. No behavior
changed. No additional review round is required for these edits.

## Semgrep and lint

The requested baseline scan completed in a disposable `git clone --shared`
checkout, comparing with merge base `93f8427c25d71c67ba964ec7692bcbe79d144bde`.
The command used `semgrep scan --config auto --baseline-commit` with
`SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, without a metrics-off flag.
Result: 85 rules, 8 scanned files, 28 ignored files, zero findings and zero
errors. JSON and log: `/tmp/540-validation.k7vCzE/semgrep.json` and
`semgrep.log` in the same directory.

`make lint`, `make validate` and `make build` passed. Generation left the
worktree unchanged. The lint skill result was:

```text
Lint status: success
Commit: none
Unresolved or skipped: none
Check-only by project policy: Markdown and Prettier for protected Scrut files
Caller resume target: full checks, versions, tidy, push and ready PR
```

## Runtime recurrence and stop

`make test-all SCRUT_JOBS=4` ran with hostile signing config, a disposable
caller `GIT_DIR`, and all three budget variables set to hostile values. Lint
and validation passed. The Scrut run failed in backlog-gather, codex-aspects,
bugs-gather, merge-flow, manage-resource-claims, review-scope and review-corpus.
The 23-case environment-isolation document itself passed.

A two-case live Scrut reproduction proves the boundary: case one sources the
shared reset and sees `GIT_DIR` absent, but case two sees it present again.
Clearing an inherited variable in one testcase does not remove it from the
parent environment supplied to subsequent testcase shells. The static guard's
document-entry requirement therefore cannot establish runtime isolation.

Evidence: `/tmp/540-validation.k7vCzE/scrut-unset-repro.md` and
`scrut-unset-repro.log`. The targeted codex-aspects reproduction fails at
fixture creation with `fatal: a branch named 'base' already exists`, because
the inherited directory selects the caller repository instead of the fixture.
Log: `/tmp/540-validation.k7vCzE/codex-hostile-repro.log`.

Our severity: Important. The test run reached the disposable caller repository
and changed 117 file entries, including Git metadata; real caller repositories
must not be reachable through this input. No real user repository or config
was targeted. Before/after lists are under
`/tmp/540-validation.k7vCzE/full-caller/`.

| Reviewer label                                 | Our severity                                                                                 | Take or record                                                             | Review again                                                           |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| No reviewer label; live Scrut failure, exit 50 | Important: later cases inherit a caller repository selection and can modify its Git metadata | Take pending TOOLING's boundary decision; no fix after the recurrence stop | Yes, a fix changes runtime isolation; retain all existing round counts |

The runner was stopped with SIGTERM to its recorded PID, 39631. Its parent
make PID 81788 and wrapper PID 81654 exited as well; unified execution session
57075 completed. The full-suite result is failed/interrupted, with no complete
suite pass claimed. Log: `/tmp/540-validation.k7vCzE/test-all.log`.

Proposed next design boundary: sanitize Git inputs before Scrut launches each
testcase shell, reusing or extending the existing runner and shared reset.
Use the same shell wrapper through CI's existing `scrut-shell` input, so local
and CI have one contract. Retain per-consumer resets and add the two-case
parent-environment regression. No implementation followed discovery.

End state: **stopped: recurring defect**. Counts remain structural one Nit and
two Important rounds, and general one Nit and one Important round. This runtime
finding consumed no review round. Version checking, tidy, push and PR remain
unperformed. Both issue labels remain `in progress` pending TOOLING's decision.

## Scrut-startup boundary decision

TOOLING authorized one wrapper before Scrut startup, shared by Make and CI,
built from the existing reset policy. Per-consumer resets remain a second
layer. General review continues at Important round two; a further inherited-input
instance stops for TOOLING to take to Chris.

`bin/run-scrut` sources `bin/lib/git-environment.bash` and then executes Scrut.
The shared reset owns all exported `GIT_*` inputs and the three current budget
inputs. Removed those suite-level inputs from `SCRUT_UNSET`, removed the fixture's
duplicate budget reset, and retained deliberate fixture arguments. Both runner
paths and snapshot updates call the wrapper.

The reusable CI workflow had no pre-Scrut command hook. The CI document job now
uses the existing pinned Scrut setup action and calls `make test-scrut`; its
environment comes directly from `SCRUT_ENV`. Removed the duplicate CI list and
updated the test instructions to reflect one registration point. The changed
root-plus-tests instruction chain is 8484 bytes, below 32 KiB.

The guard checks the Make targets, CI routing, wrapper entry reset and direct
Scrut calls in scripts and workflows. It obtains test documents from the
runner's existing discovery instead of keeping a second format list. Negative
cases cover runner bypass, update bypass, direct CI calls, reusable CI bypass,
new direct callers and a missing wrapper reset.

The permanent two-case fixture first sources the reset, then checks a second
shell without sourcing it again. With hostile inputs, the real wrapper passes
both cases. Removing only the wrapper's source line leaves case one passing
and makes case two print `case 2 inherited`: Scrut exit 50, one success, one
failure, zero skips. Restoring the line passes both cases. Artifacts:
`/tmp/540-validation.k7vCzE/wrapper-check.PA6uDf/`. The local binary identifies
itself as `scrut 1772332969`; CI retains its existing pinned `0.4.3` dependency.

Hostile targeted results so far: Codex aspects passed 82 cases, and the runner
document passed 18 cases, both with zero skips. The expanded isolation document
passed all 31 cases with zero skips. Logs use the `wrapper-` prefix under
`/tmp/540-validation.k7vCzE/`.

One earlier expanded run had a cleanup race: Git maintenance changed lock and
bitmap files while the fixture removed its corpus. Installed Git 2.55.0
documentation confirms that automatic maintenance detaches by default. This
was a default background-process lifetime issue, with no inherited input found.
The shared fixture profile now pins `maintenance.autoDetach=false` and
`gc.autoDetach=false`, retaining maintenance in the foreground. Effective Git
configuration checks pass despite conflicting caller values; changing either
setting to true makes its real Scrut assertion fail. Both plants were restored.
Artifacts are in the `wrapper-check.PA6uDf` directory.

No additional review round has started yet; counts remain structural one Nit
plus two Important, and general one Nit plus one Important. The next run is
general Important round two, as TOOLING directed.

## Important round two attempt and current stop

All four read-only aspects completed with valid output objects and process
statuses, using `gpt-6.1-sol`, high effort and an 872000-token window through
installed helper version 2.1.4. However, snapshot validation failed:
`origin/main` advanced from `78386666` to `45b89f1c` during the run. HEAD,
index, tree and merge base remained identical. The actor was not identified.
The review has no valid clean result; the returned findings were treated as
untrusted until the independent confirmations below.

| Reviewer label                                                          | Our severity                                                                                                                     | Take or record                                                                                                                        | Review again                                                                            |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| important, code: Environment reset removes a required fixture input     | Important: the reset removes GIT_WORKTREE_STUB_BIN, so required launcher and resource-claim stub setup loses its executable path | Take pending continuation: rename the fixture input outside the reserved GIT_ namespace, with a guard against future collisions       | Yes, fixture setup behavior changes                                                     |
| important, errors: Maintenance probe failures discard their diagnostics | Important: a failed Git probe exits without its diagnostic after cleanup                                                         | Take pending TOOLING's structural decision: centralize captured-child execution and replay instead of adding another isolated handler | Yes, diagnostic behavior changes; this repeats the class fixed in the general Nit round |

A source-only probe confirms that `GIT_WORKTREE_STUB_BIN` is removed by the
shared reset. It is still registered in Make and used by launch-workmux,
launch-workmux-options and manage-resource-claims. The reset should continue
clearing Git inputs; fixture controls should use a different namespace, such
as `WORKTREE_GIT_STUB_BIN`.

For the diagnostic check, the committed failing-fixture stub was copied as
`git` and its resolution verified with `command -v` before execution. The
maintenance scenario exits 7 with a zero-byte output log, confirming the loss
independently of the invalid review. Evidence:
`/tmp/540-validation.k7vCzE/wrapper-check.PA6uDf/maintenance-failure-repro.log`.
No code fix followed discovery.

The proposed structural fix is one capture/replay helper for every captured
child call, plus negative controls for failures through the maintenance probe.
This is a diagnostic-loss recurrence; no additional surviving caller-input
leak was established. TOOLING received the distinction in the stop report.

Counts are preserved: structural one Nit plus two Important runs; general one
Nit and Important round one completed, plus this attempted Important round two
whose snapshot validation failed. No clean round or fresh budget is claimed.
For a continuation, derive the actual `origin/main` merge base once and pass
that immutable hash to both scope captures, avoiding shared remote-ref movement.

The separate maintenance lifetime fix was taken as an Important runtime
reliability finding: foreground maintenance replaces the default detached
process, with effective-config controls and plants. Its required review remains
unverified because this attempt was invalidated.

End state: **stopped: recurring defect**. All test and reviewer runs have
finished. The hostile full-suite pass with unchanged caller checksums, final
trims, renewed Semgrep/lint checks, versions, tidy and publication remain.

## Capture and namespace design continuation

TOOLING authorized one capture/replay helper for fixtures and validators, a
guard against captures outside it, and `WORKTREE_GIT_STUB_BIN` as the fixture
input. The invalid Important round two attempt does not count. The rerun uses
immutable base `93f8427c25d71c67ba964ec7692bcbe79d144bde`; every prior count stays.

`bin/lib/capture-child.bash` owns retained child diagnostics. It returns the
child's nonzero status and replays failures before cleanup. Result-variable,
separate-stdout, normalized-report and contextual-prefix modes preserve the
existing fixture and validator formats. Semantic validator branches still
count findings, but no caller keeps a capture/replay branch. Invalid writable
results fail rather than returning success, without replacing a failed child's
status.

Moved every retained diagnostic capture in the isolation fixture, catalog
fixture, notification fixture and both validators to this helper. Stdout-only
data queries keep stderr live; intentional `/dev/null` probes are not retained
diagnostic captures. The guard rejects retained captures in fixtures,
validators and shared libraries outside this one helper.

The active Make registration and launch/resource fixtures now use
`WORKTREE_GIT_STUB_BIN`. The guard rejects fixture-owned `GIT_*` registrations;
its old-name plant is a permanent negative case. Prior review evidence and the
completed historical plan retain the old name as recorded.

Targeted suites passed with original assertions unchanged: isolation 40 cases,
corpus 56, notifications 24, launcher options 16, resource claims 97 and catalog
validation 14. The corpus and notification formats were retained in the shared
helper instead of weakening their snapshots.

The committed failing stub resolves as the probe's Git executable and returns
7 with `deliberate fixture failure`. The real Scrut assertion passes. Removing
the common replay statement leaves status 7 but removes that diagnostic, making
the assertion fail with Scrut exit 50. The helper was restored. Artifacts:
`/tmp/540-validation.k7vCzE/capture-check.cpNrBn/`.

The namespace, direct-capture, stderr-file and second-library guard plants are
also permanent negative cases. No new diagnostic-loss instance was found after
centralization. General Important round two is next; full hostile validation
with an unchanged disposable caller repository remains required.

## Pinned general Important round two

All four aspects completed with valid output and zero process exit statuses,
using `gpt-6.1-sol`, high effort and an 872000-token window. Code, errors, tests
and comments reported no findings across the full scoped branch. Both scope
captures used immutable base `93f8427c25d71c67ba964ec7692bcbe79d144bde`; snapshots
matched with no lasting changes. Review artifacts use the
`general-important-2-pinned` prefix under `/tmp/540-validation.k7vCzE/`.

End state: **clean at Important**. General count: one Nit and two valid
Important rounds. The remote-ref-invalidated attempt did not count, as TOOLING
directed. Structural count stays one Nit and two Important rounds. No further
diagnostic-loss instance was found. Final comment/prose trims and validation of
the resulting tree remain before publication.

## Final trims after the runtime fixes

Fresh read-only comment and prose runs used `gpt-6.1-sol`, low effort and an
872000-token window. File coverage and reply checks passed. Applied three
comment rewrites and five prose rewrites, preserving instruction strength,
evidence and review counts. One comment proposal was adjusted to cover execution
diagnostics rather than attributing scratch-directory errors solely to yq.
No behavior changed. Final source validation now follows.

## Final baseline scan and validation stop

The renewed scan ran in `/tmp/540-validation.k7vCzE/semgrep-clone-final`, a fresh
shared clone of the trimmed branch. It used the requested `--config auto` and
`--baseline-commit 93f8427c25d71c67ba964ec7692bcbe79d144bde`, with the repository
slug set and no metrics-off flag. The process exited 0 and reported zero
findings, but its JSON contains two `PartialParsing` warnings/errors. Coverage
is incomplete, not clean: 85 rules, 12 scanned files, 33 ignored files and about
99.8 percent parsed lines.

| File                    | Parser limitation                                                       | Baseline comparison                                                             |
| ----------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| bin/run-scrut-documents | Nested default expansion `${WORKER_PGID:-${!:-}}`                       | Identical at baseline line 77 and current line 84                               |
| bin/validate-plugins    | Parenthesized arithmetic expansions for line and inventory token counts | Identical at baseline lines 746, 759 and 779 and current lines 749, 762 and 782 |

Both files pass macOS `/bin/bash -n`. No source rewrite, ignore rule, tool
upgrade or scan substitution was applied to work around the parser. The
limitations are present in unchanged code, but the requested baseline analysis
is still incomplete. TOOLING received the evidence for its validation decision.

Artifacts: `/tmp/540-validation.k7vCzE/semgrep-final.json` and
`semgrep-final.log`. This is a third-party scanner coverage issue, not a new
diagnostic-loss finding or a new model-review round. Review counts remain
structural one Nit plus two Important, and general one Nit plus two valid
Important rounds, both ending clean at Important.

No runs remain active. Final lint/build, the hostile full `make test-all` with
fresh unchanged caller checksums, version checking, exact-tree tidy, push and
ready PR with green checks remain unperformed after this scan stop. Both issue
labels remain `in progress` until TOOLING parks or continues the work.

## Semgrep span condition accepted

TOOLING authorized accepting the scan if no changed or added line intersects
the JSON spans, including their enclosing function or arithmetic expressions.
The check passed against `93f8427c25d71c67ba964ec7692bcbe79d144bde`.

The six raw spans are `bin/run-scrut-documents` 84:33–84:35 and
`bin/validate-plugins` 749:3–749:84, 762:3–763:4, 782:38–782:39,
782:79–782:102 and 782:103–782:104. The check conservatively expanded these to
the entire `stop_workers` function, lines 82–93, and the entire top-level
inventory-budget section, lines 513–795, including all affected expressions
and surrounding control flow.

Every expanded region matches a single unchanged baseline block and has
identical bytes. Git's zero-context diff reports no added or modified line in
any raw or expanded span. The checked files also match the scan clone's source
bytes. Protected baseline regions are 75–86 and 510–792, respectively.

Committed evidence:
`docs/reviews/2026-10-28-fixture-environment-semgrep-spans.json`. It records all
raw spans, changed-line ranges, expanded regions, source hashes and empty
intersections. The one-off checker is
`/tmp/540-validation.k7vCzE/check-semgrep-overlap.py`. The PR body must link
this evidence and retain the parser-limit explanation.

Under the validation call, changed code was fully scanned and the scan counts
as complete for this branch: zero findings, with two pre-existing parser
warnings outside changed code. The unchanged constructs were not rewritten.
Both owned scan clones were removed after the evidence was recorded; raw scan
JSON and logs remain. No model-review count changed.

## Final validation

The hostile full `make test-all SCRUT_JOBS=4` passed all 34 Scrut documents:
1450 testcase successes, zero failures and zero skips. The environment forced
commit/tag signing with an unusable key, selected a disposable caller through
`GIT_DIR`, and supplied hostile values for all three budget inputs.

The wrapper returned `make test-all exit=0; caller checksum comparison exit=0`.
Checksums cover every caller-repository file and its hostile config, both
unchanged. Evidence is under
`/tmp/540-validation.k7vCzE/full-caller-final.IvTAXk/` (`before` and `after`);
the full log is `/tmp/540-validation.k7vCzE/test-all-final.log`.

Final `make lint` and `make build` passed. Generation left the worktree clean.
Logs: `final-lint.log` and `final-build.log` under the validation directory.

```text
Status: no-op
Lint status: success
Commit: none
Unresolved or skipped: none
Check-only by project policy: Markdown and Prettier for protected Scrut files
Caller resume target: version check, tidy, push and ready PR
```

The repository check-versions workflow is all clear against merge base
`93f8427c25d71c67ba964ec7692bcbe79d144bde`: 60 manifests, two matching dual
manifests, complete marketplace coverage and manifest-only version ownership.
No plugin content changed, so no bump is required. Evidence:
`/tmp/540-validation.k7vCzE/version-check.json`.

Both review loops end **clean at Important**, each with one Nit and two valid
Important rounds. The invalid moving-ref attempt did not count. Publication
will include the verified Semgrep spans and committed evidence link in its body.

## Publication handoff

The authorized tidy groups implementation and tests together, with this ledger
and the span evidence in a separate documentation commit. The pre-tidy branch
retains the signed development history. Exact-tree comparison after rebuilding
is reported in the workstream mailbox, keeping this candidate tree unchanged.
The ready PR body carries the final checks and Semgrep evidence; TOOLING owns
merging. No Copilot review is requested or awaited.
