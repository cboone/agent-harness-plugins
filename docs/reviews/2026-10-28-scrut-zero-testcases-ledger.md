# Scrut summary validation ledger

## Scope and authority

- Issue: [Flag scrut documents that report zero testcases](https://github.com/cboone/agent-harness-plugins/issues/577).
- Go-ahead: Chris, Inbox, 2026-10-28 9:16 AM ET, “Tooling next batch”, pick 5. Build through a ready PR; TOOLING merges.
- Keep `bin/run-scrut-documents` changes local for the overlapping test-environment branch.
- Full local review order applies; this change exceeds the small-change limit.

## Reproduction and design

An unterminated scrut fence returned `Result: 0 document(s) with 0 testcase(s): 0 succeeded, 0 failed and 0 skipped`, exit 0, through the original runner.

Validate summaries after zero exits in both single and parallel execution. Preserve nonzero scrut statuses for single documents and aggregate parallel failures. Require one complete, consistent summary with one document and positive testcase count. Print all scrut output, including stderr. Buffer single-document output until scrut finishes. On interruption, print captured diagnostics before cleanup and stop its process group.

The local test target uses the runner. The update target verifies documents after rewriting snapshots. CI uses the same runner with the pinned `set-up-scrut` action, since the external reusable workflow exposes no runner input. The external workflow remains unchanged; its direct `scrut test` invocation needs equivalent validation or a runner input.

## Validation

- Corepack Yarn immutable installation: passed.
- Targeted runner document: 24 testcases passed.
- Final `make test-all`: exit 0, all 40 scrut documents passed; lint and validation passed.
- Focused review: clean at Important; structural review ended with behavior-preserving fixes.
- Semgrep: zero findings with TOOLING’s explicit exception for the sole special-parameter-default span, recorded below.
- Final version check: all 60 catalog entries/manifests valid; no plugin content-directory changes or version bumps needed.

## Planted defects

| Planted defect              | Instrument         | Observed result                  | Regression test                                           |
| --------------------------- | ------------------ | -------------------------------- | --------------------------------------------------------- |
| Accept zero testcases       | Runner scrut tests | 2 assertions failed; make exit 2 | Unterminated fence, empty document, single empty document |
| Accept missing summary      | Runner scrut tests | 2 assertions failed; make exit 2 | Missing summary in single and parallel execution          |
| Accept unrecognized summary | Runner scrut tests | 2 assertions failed; make exit 2 | Unrecognized summary                                      |
| Accept duplicate summary    | Runner scrut tests | 1 assertion failed; make exit 2  | Duplicate summary                                         |
| Accept inconsistent counts  | Runner scrut tests | 1 assertion failed; make exit 2  | Inconsistent summary                                      |
| Suppress parallel stderr    | Runner scrut tests | 1 assertion failed; make exit 2  | Preserve stderr                                           |

Each plant modified the real runner and restored it before the next. Logs: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/scrut-577-plants.gb_p2pp8`.

## Reviews

Structural Nit round: fresh read-only `codex exec`, `gpt-6.1-sol`, high effort, 872000-token window. Anti-patterns and report-only simplify ran in parallel. Both exited 0 with validated nonempty JSON. Scope unchanged after review; no lasting changes found. Base: `4b473c00e6ad3bb935f204eb7807aaa554b91c57` from `origin/main`.

| Finding                                             | Reviewer label | Impact severity                                  | Disposition                                                                             | Review again           |
| --------------------------------------------------- | -------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------- | ---------------------- |
| CI helper-registration guidance names removed input | nit            | Nit; directs registrations to a removed block    | Taken: update the scoped guides, development guide, shell guidance and Makefile comment | No; documentation only |
| Help reverses output and validation order           | nit            | Nit; inaccurate buffering description            | Taken: correct help and snapshot                                                        | No; help text only     |
| Combine nested summary-validation conditions        | suggestion     | Nit; equivalent control flow is easier to follow | Taken                                                                                   | No; preserves behavior |

Structural loop ended: fixes changed no behavior. Full focused Nit round completed. Types aspect excluded because no types or schemas changed. Review artifacts: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/scrut-577-review.BYoE7w`.

### Focused Nit round

Four fresh read-only Codex aspects (`code`, `errors`, `tests`, `comments`) ran with `gpt-6.1-sol`, high effort and an 872000-token window. Every aspect exited 0 with validated nonempty JSON. No lasting scope changes were found. Code found no defects.

| Finding                                      | Reviewer label | Impact severity                                                     | Disposition                                               | Review again          |
| -------------------------------------------- | -------------- | ------------------------------------------------------------------- | --------------------------------------------------------- | --------------------- |
| Cancellation discards buffered diagnostics   | important      | Important; interrupted CI and local runs lose tool diagnostics      | Taken: flush the named single-document log before cleanup | Yes; behavior changed |
| Cancellation coverage omits descendants      | suggestion     | Nit; the new process-group boundary needs a child-process assertion | Taken: record and check the fixture child PID             | No; tests only        |
| Help incorrectly claims foreground execution | suggestion     | Nit; the child actually runs in a separate background group         | Taken: describe buffering only                            | No; help text only    |

The output-order finding in the structural loop and the foreground wording finding concern distinct statements. Neither is a recurring behavior defect. Focused loop advances to Important round 1. Targeted regression: 24 testcases passed after fixes. Cancellation plants passed: suppressing the captured-log flush failed its diagnostic assertion; signaling only the parent PID left one child running in the single-document case and two workers running in the parallel case. Each plant was reverted. Logs: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/scrut-577-cancel-plants._nmiig7a`.

### Focused Important round 1

All four aspects exited 0 with valid nonempty JSON and no findings. The scope comparison found no lasting changes. End state: clean at Important. No further round is warranted.

### Trims

One comment round and one prose round ran through fresh read-only `codex exec` contexts (`gpt-6.1-sol`, low effort, 872000-token window). Both exited 0 and returned classified file lists and full proposals. Took the wording improvements and removed the redundant summary-check comment. Retained the fixture mode descriptions because they document its cross-file interface. Retained the Makefile-to-CI registration reminder while shortening its wording. No behavior changed.

### Remaining checks

The early full scrut run printed all 40 documents passed, then exited nonzero with a missing single-log error while the runner was being edited for review fixes and plants. That run is invalidated and is not counted as a pass. The later standalone final run passed, as recorded below. Historical stop decisions are superseded by TOOLING’s final exception and finish authorization. Tidy and PR checks remain pending.

## Stop: baseline semgrep partial parsing

The required scan ran in a disposable shared clone of commit `9a5c1086`, with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`:

```bash
semgrep scan --config auto \
  --baseline-commit 4b473c00e6ad3bb935f204eb7807aaa554b91c57
```

The invocation also requested JSON output for inspecting parser errors. It used no metrics override. Semgrep exited 0, ran 85 rules on 7 files, and returned zero findings, but recorded `PartialParsing` for `bin/run-scrut-documents` at line 78: unexpected `:-` in `local pgid="${WORKER_PGID:-${!:-}}"`. The expression is also present in the comparison base. Parsed coverage was approximately 99.9 percent. Semgrep skipped its baseline checkout because the current scan had zero findings; the requested baseline mode did run.

This is incomplete validation, not a clean scan. The brief explicitly requires stopping when changed code is partially parsed. No parser workaround or rescan was attempted. Captures: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/scrut-577-semgrep.crlZ8g/scan.log` and `result.json`.

Resume requires TOOLING’s direction on the parser limitation and a reopened worker gate. Pending: successful baseline semgrep without changed-file partial parsing, final `lint-and-fix --no-push`, final `make test-all`, final version confirmation, exact-tree tidy, push, ready PR closing the issue, green CI and final review précis. No push or PR exists. All local changes are committed; the worker stops here.

Version confirmation already completed against the actual `origin/main` merge base: no plugin content directories changed; all 60 plugins have catalog coverage, valid manifest-owned versions, and matching Codex manifests where present. Root plus scoped instruction files remain below 32 KiB (root 6118 bytes; largest changed scoped file 2375 bytes).

## TOOLING span acceptance check

TOOLING authorized accepting the partial scan only if no changed or added line falls inside the JSON error span, including its enclosing function, compared with `4b473c00`. The worker remains running; no restart was required for this check.

- JSON evidence: `errors[0].path` and `errors[0].spans[0].file` are `bin/run-scrut-documents`; start is line 78, column 33, offset 0; end is line 78, column 35, offset 2. The error type is `PartialParsing` and the unexpected token is `:-`.
- The exact JSON line span contains no added or changed lines.
- The enclosing `stop_workers` function spans current lines 76–96. Its existing fallback expression remains unchanged.
- `git diff --no-ext-diff --no-color --unified=0 4b473c00 -- bin/run-scrut-documents` includes hunk `@@ -84,0 +86,9 @@ function stop_workers() {`. Added lines 86–94 flush interrupted single-document diagnostics. All nine additions are inside the enclosing function.
- A script extracted the JSON span, located the enclosing top-level function, parsed the diff hunk ranges and intersected added lines with both ranges. Raw-span intersection: empty. Enclosing-function intersection: 86, 87, 88, 89, 90, 91, 92, 93, 94.

Acceptance condition failed. Per TOOLING’s explicit conditional stop, final lint, the fresh standalone `make test-all`, tidy, push and PR remain pending. No PR body exists to update. This evidence must accompany any eventual PR body, together with the external workflow requirement already recorded above. The unchanged fallback expression was left alone.

The disposable scan clone was removed after this check. Its sibling `result.json` and `scan.log` remain at the recorded scan capture path. Awaiting TOOLING’s direction; no restart is needed while this worker remains running.

## TOOLING syntax-only rewrite authorization

TOOLING authorized splitting the nested process-group default into plain steps, leaving behavior and Bash 3.2 compatibility intact, then repeating affected suites, interruption and cleanup plants, and the same baseline scan. No new review round is required. Any remaining partial parsing requires another stop. The earlier enclosing-function rejection remains recorded as the reason for this authorized rewrite.

The assignment now takes `WORKER_PGID` first and evaluates the original background-PID default only when empty. The rewrite is confined to that assignment and its conditional fallback. `bash -n`, ShellCheck and shfmt passed. Runner coverage passed 24 testcases and repository-tooling passed 22. The latter invocation emitted a `child setpgid: Operation not permitted` diagnostic before completing successfully; it is retained here rather than suppressed. A two-document parallel run passed under macOS Bash 3.2. Direct comparisons of old and split expressions matched under Bash 3.2 and Bash 5.3 with empty and populated `WORKER_PGID` and a recorded background PID. Plants and scan rerun are pending.

### Revalidation after the syntax rewrite

The interruption-diagnostics plant failed one assertion; the parent-only signaling plant failed two, including the single-document child-process check. Captures: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/scrut-577-cancel-plants.e61qybfk`. Disabling log-directory cleanup failed five assertions, including the normal and interrupted cleanup checks. Capture: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/scrut-577-cleanup-plant.pzxbgdk5/cleanup.log`. Each plant modified the real runner, completed, and restored it before the next run. The restored 24-case runner document passed again. No mutation ran concurrently with another runner invocation. The same baseline scan is next.

### Stop: standalone background-PID default still parses partially

The repeated baseline scan used the same baseline `4b473c00e6ad3bb935f204eb7807aaa554b91c57`, `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, `--config auto`, and no metrics override, in a fresh disposable shared clone of `7b1a754e`. Semgrep exited 0 with zero findings, 85 rules and 7 files, but again reported `PartialParsing` and approximately 99.9 percent parsed coverage.

The new JSON span is `bin/run-scrut-documents:80`, columns 14–16, offsets 0–2: `:-` is unexpected in the now-standalone `pgid="${!:-}"` fallback. That fallback line is added by the authorized syntax rewrite and lies inside `stop_workers`. The nested default was removed, so the remaining limitation is the standalone special-parameter default. The fallback retained the original default semantics; directly expanding `$!` under nounset can fail when no background PID exists, while the default can return empty under Bash 5.3.

Per TOOLING’s explicit “If anything still parses partially, stop and report” instruction, no additional rewrite or scan was attempted. No new review round ran, as directed. Final lint-and-fix, fresh standalone `make test-all`, tidy, push and ready PR remain pending. No push or PR exists.

Captures are retained outside the clone at `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/scrut-577-semgrep-rerun.AJroKs/result.json` and `scan.log`. The recorded disposable clone was removed after capture inspection. The worktree is committed for TOOLING’s next direction.

## Final TOOLING parser-exception decision

TOOLING authorized one cached-background-PID experiment and explicitly authorized proceeding with the current form if the experiment changed behavior or parsing remained partial. This supersedes the earlier stop gates; final checks and ready-PR publication are authorized, with no new review round.

A temporary candidate initialized `LAST_BACKGROUND_PID` empty, assigned `$!` immediately after each asynchronous launch, and used that variable as the fallback in `stop_workers`. A deterministic DEBUG-trap probe delivered SIGTERM immediately before the first PID-capture assignment. The probe used the actual `stop_workers` function from each form and recorded signal targets rather than sending them. Under both Bash 3.2 and 5.3, the current form selected the newly launched background PID for TERM and CONT; the cached form selected no PID because its first capture had not executed. Both exited 143. The candidate therefore fails the exact-PID-selection requirement in the launch window and was reverted completely. Capture: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/scrut-577-cache-probe.hflf5lr3`.

The restored runner passed 24 testcases. The three requested plants were repeated sequentially: suppressed interruption diagnostics failed one assertion, parent-only signaling failed two, and disabled log-directory cleanup failed three cleanup assertions. All plants were restored and the runner passed 24/24 again. Captures: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/scrut-577-cancel-plants.jdbzkzsy` and `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/scrut-577-cleanup-final.omcbqawg`.

TOOLING’s accepted rationale is that the remaining parser exception is one special-parameter default, which carries no command or additional data flow of its own. The implementation retains its existing runtime semantics and has targeted interruption, diagnostic and cleanup evidence. This is an authorized narrow parser exception, not a claim of completely error-free parsing. The repeated baseline scan and exact span will be recorded below and included in the PR body. No further stop is required for that same narrow span.

### Accepted final baseline scan

The final scan used baseline `4b473c00e6ad3bb935f204eb7807aaa554b91c57`, `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, `semgrep scan --config auto --baseline-commit ...`, JSON output and no metrics override, in a fresh shared clone of `714a885c`. Exit 0, zero findings, 85 rules on 7 files. The JSON contains exactly one error: `PartialParsing` at `bin/run-scrut-documents:80`, columns 14–16, offsets 0–2, on the standalone `${!:-}` default. No additional partial span appeared. Semgrep skipped its baseline checkout because the current scan had no findings, while retaining baseline-limited target selection.

The span is inside `stop_workers` and the fallback line is changed relative to `4b473c00`; acceptance relies on TOOLING’s explicit final exception, not the earlier unchanged-function condition. The cache alternative failed identical PID selection under both Bash versions, as recorded above. The retained special-parameter default introduces no additional command. Runtime semantics, interruption diagnostics and cleanup have direct test and plant evidence. Semgrep is accepted with this documented parser limitation, not described as fully parsed.

Captures remain at `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/scrut-577-semgrep-final.dk20Mc/result.json` and `scan.log`. The disposable clone was removed after verifying its sole error. The PR body must include the exact span, cache comparison, acceptance rationale, and external reusable-workflow follow-up.

## Final local validation and publication preparation

`lint-and-fix --no-push` completed successfully with no fixes or lint commit needed. Markdown/Prettier were checked rather than run through broad fixers because those commands reach protected scrut snapshots; ShellCheck, shfmt, actionlint, JSON and plugin validation all passed through `make lint validate`. No required check was skipped. Caller continuation: standalone final tests, tidy, push and ready PR.

The fresh `make test-all` ran alone after all runner edits and plants ended. It exited 0 and reported all 40 scrut documents passed, including the runner’s 24 testcases. No runner edits or concurrent test/review processes ran alongside it. This successful run supersedes the invalidated early suite. Output: `/tmp/577-test-all-final.log`.

The repository `check-versions` procedure was repeated after fetching `origin/main`: comparison merge base remains `4b473c00e6ad3bb935f204eb7807aaa554b91c57`. No plugin content directory changed. All 60 plugins have catalog coverage and valid manifest-owned versions, and every present Codex manifest matches. No bump is needed.

Tidy will use backup branch `fix/577-scrut-zero-testcases-pre-tidy`, rebuild from that merge base as signed implementation, test and documentation commits, then require an exact-tree comparison against the backup. The measured tidy result and PR/CI state will be reported outside this tree so the tidy preserves the linted and tested content. No additional code review round ran after the explicitly authorized syntax-only rewrite.

## Publication and base-update gate

Exact-tree tidy passed against `fix/577-scrut-zero-testcases-pre-tidy`. The published history contains three valid signed commits: `5ad91042` (implementation), `06b4cbd8` (tests), and `2c695270` (documentation). The worktree was clean and the pushed tree exactly matched the backup. The branch was pushed normally, with no history rewrite.

[Reject scrut documents without valid testcase summaries](https://github.com/cboone/agent-harness-plugins/pull/670) is open and ready for review. The stored body matches the prepared body, includes the accepted parser span and external-workflow follow-up, and GitHub recognizes its closing reference to the issue.

GitHub reports `CONFLICTING` / `DIRTY` against `main` at `fec4708b`, after the background-watch work in repository PR 668 merged. No PR CI run has started. A non-mutating `git merge-tree --write-tree HEAD origin/main` found one conflict, `.github/workflows/ci.yml`; Makefile auto-merges. The concrete resolution preserves the checked-runner CI job and adds the incoming `MONITOR_SKILL_FILE` and `WATCH_CHANGES_STUB_BIN` environment registrations. Prepared patch: `/tmp/577-ci-conflict-resolution.patch`. No runner or fallback change is required.

TOOLING received the base-update gate request through the worker mailbox. No merge or rebase has begun. Pending authorization: signed merge of `origin/main`, the two-entry CI resolution, affected/full checks and version confirmation, push and green CI. Pushed history must remain intact. This gate request concerns the base update, not the already accepted parser exception. TOOLING retains responsibility for merging the PR.
