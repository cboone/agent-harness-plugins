# Explicit edit-mode review ledger

Base: `5205fada80635f7d9dd4a1967c94a256e60a99cb`, the branch's merge base with `origin/main`. This record covers local pre-push review. TOOLING merges; no live configuration changes.

## Structural loop

Fresh standalone Codex runs, `gpt-6.1-sol`, `high`, context window `872000`, read-only sandbox, approval policy `never`, web search disabled. Anti-patterns and report-only simplify ran in parallel. Both exited zero with nonempty output; the anti-pattern reply passed its JSON shape check. Generated mirrors were excluded. Simplify completed reuse, simplification, efficiency and altitude inline, with no delegation or edits.

| Round | Threshold | Anti-patterns                  | Simplify    | State                                   |
| ----- | --------- | ------------------------------ | ----------- | --------------------------------------- |
| 1     | Nit       | One Important                  | No findings | AP-1 taken                              |
| 2     | Important | One Important                  | No findings | AP-2 taken; next round second Important |
| 3     | Important | One Important, AP-2 recurrence | No findings | stopped: recurring defect               |
| 4     | Critical  | No findings                    | No findings | clean at Critical                       |

### Finding AP-1

- **Reviewer's label:** `important`, “Agent-prose control flow: dirty checkouts prevent explicit-range edit runs”. An unrelated local edit makes a range review incomplete, so the draft stopped before fixing the fully reviewed selected range.
- **Our severity:** Important. The completeness gate made the proposed dirty-checkout workflow unreachable.
- **Take or record:** Take. TOOLING's design call, mailbox sequence 000001, received 2026-10-30 at 18:16:32 ET: keep the completeness gate strict and require a clean worktree before edit mode starts. Refuse with commit-or-stash guidance, without doing either. The issue does not require dirty-checkout edits. Add refusal regression coverage and a plant. Also take the edit-only capture-base lookup correction for `--range`.
- **Review again:** Yes. The clean-worktree precondition changes behavior. Loop count retained; the next round is Important, with report-only simplify again.

### Finding AP-2

- **Reviewer's label:** `important`, “Validator gaps: the clean-worktree gate accepts edits hidden by assume-unchanged”. Porcelain status alone accepts an edited tracked file carrying that index flag.
- **Our severity:** Important. The edit workflow could start with local edits that its clean-worktree requirement promises to refuse. This is distinct from AP-1's incomplete range-review control flow, not a recurrence of that mechanism.
- **Take or record:** Take. TOOLING approved the ordinary-`H` allowlist and immediate post-capture precondition recheck in mailbox sequence 000002, received 2026-10-30 at 18:25:25 ET. Refuse every other or unverifiable entry without changing the index. Reproduced in a disposable repository: modified `tracked.txt` appeared as `h tracked.txt` to `git ls-files -v`, while the current precondition helper exited zero. No index flags were changed outside the fixture.
- **Review again:** Yes, after the behavior correction. Next structural round is round 3, the second Important round. Simplify round 2 completed with no Important findings.

AP-2 regression suite expanded to 23 cases. The first expanded run exposed a fixture setup error: combining Git's two clearing flags left skip-worktree set. A direct fixture reproduction showed `s` becoming `S`, rather than `H`; issuing the clearing operations separately restored `H`. The corrected suite passed all 23. This changed test setup only.

### Finding AP-3 and recurrence stop

- **Reviewer's label:** `important`, “Sibling input forms: initialized submodules bypass the hidden-index-flag refusal”. An initialized submodule can hide edited assume-unchanged content from parent status while the parent flag inventory contains only an ordinary `H` gitlink.
- **Our severity:** Important. The clean-worktree policy can accept hidden child edits. This repeats AP-2's mechanism across a child-index boundary.
- **Take or record:** Take. The loop stopped immediately. TOOLING then selected refusal of every gitlink, registered or embedded and initialized or not, in mailbox sequence 000003 received 2026-10-30 at 18:36:07 ET. Name the path, check before and after capture, and document the limit in the skill and PR body. Recursive child-index validation is outside scope. The implementation reads stage metadata in the same rooted flag inventory and refuses gitlinks before considering other dirt. Registered and embedded initialized-child regression cases reproduce parent status remaining empty despite hidden child edits. No child index is modified by the helper.
- **Review again:** Yes, only after the structural call and fix. Three structural rounds are consumed: Nit, Important, Important. The next threshold is Critical, with report-only simplify again. Counts do not restart.

Round 3 ended **stopped: recurring defect**. TOOLING's structural call permits the selected correction and continuation at Critical; the count is retained. Simplify round 3 exited zero with nonempty output and no Important cleanup findings, covering all four angles inline. The anti-pattern reply exited zero, reported `success` and `complete: true`, and passed the result-shape check; it is a completed review with a finding, not a clean result. All runs remained read-only.

### Structural completion

Round 4 completed after TOOLING's gitlink-refusal correction. Both subprocesses exited zero with nonempty output; the anti-pattern reply passed the shape check, had `status: success`, `complete: true` and no findings. Simplify completed all four angles inline and reported no Critical or concrete below-threshold findings. No lasting source changes were found. Structural loop end state: **clean at Critical**. No Critical label was downgraded; the existing anti-pattern schema's Important/Nit labels were retained and project impact severity assessed separately.

## General Codex loop

Round 1 at Nit used the installed `codex-aspects` helper, model `gpt-6.1-sol`, `high`, window `872000`, with `--guide-name CLAUDE.md` matching the configured fallback. Code, errors, tests and comments ran read-only in parallel; types was omitted because no types or schema changed. All four exited zero and passed the helper's schema, snapshot and membership checks. Code and errors reported no findings. GitHub metadata was unavailable inside the sandbox; the parent had independently verified the repository active and not a fork.

The first post-review scope capture was invalidated by the controller applying the jq documentation fix before that capture finished. That edit was made after all four reviewers had exited. Only the controller's two-line README edit was saved and restored to the reviewed version. A fresh capture and the helper's changes check then reported identical trees and snapshots, `scope_changed: false`, no changed or outside-scope paths. The saved documentation fix was reapplied after that check.

### Finding GC-1

- **Reviewer's label:** `important`, “write-scrut-tests: Behavioral coverage stops before fix verification runs.” The helper tests did not execute the full edit-to-verification handoff, especially a new untracked sibling outside an explicit range.
- **Our severity:** Important. A regression could verify the old committed range while omitting the fixes.
- **Take or record:** Take. Extend the existing opt-in `tests/evals/` convention with a disposable live edit evaluation, captured before/after trees, exact phase results and the final input manifest. Check a tracked sibling correction and a new untracked sibling, preserved assertions, HEAD, refs and index. The earlier ad hoc live run verified an unchanged sibling outside `--files`. The committed opt-in evaluation then passed with both `siblings.mjs` and new untracked `new-count.mjs` in the measured raw-tree diff and actual final input manifest. Phase JSON was shape-checked and complete; existing assertions, HEAD, refs and index stayed unchanged. The baseline failed on the intended 2-versus-3 endpoint assertion; post-fix Node tests passed. A fresh parent capture matched the reported final snapshot.
- **Review again:** No shipped behavior change: tests only. The positive live case and saved-artifact check passed. The live original-range plant failed exactly on incomplete final coverage; canonical instructions were restored. Finding resolved.

### Finding GC-2

- **Reviewer's label:** `important`, “write-markdown: Factual accuracy: edit mode requires jq despite its optional classification.”
- **Our severity:** Important. Following the requirements without jq leaves the requested edit workflow unavailable.
- **Take or record:** Take. Root README, plugin README and skill now explicitly require jq for edit mode; it remains optional for report-only fallback.
- **Review again:** No; documentation correction only. Finding resolved. General loop end state: **ended: fixes changed no behavior**. Only tests and dependency documentation changed; no further round is warranted by the advancement rule.

## Trims

One read-only Codex trim round used `gpt-6.1-sol`, `low`, window `872000`, approval policy `never`, web search disabled. Three independent runs covered code comments, agent instructions, and remaining changed prose. All exited zero with nonempty replies listing classified files and either full before/after proposals or no changes. Generated files and unchanged units were excluded.

`trim-comments` proposed nothing. `trim-text` proposed seven rewrites; six were applied after checking every condition, authority boundary, literal value and reference remained unchanged. The remaining repeated-subject-to-pronoun rewrite in the evaluation README was left alone because it added ambiguity without improving the instruction. No factual corrections or flags remained. Trims changed wording only; no new review round is required.

## Baseline Semgrep

Semgrep 1.180.0 exited zero in the disposable shared clone at `/tmp/624-local.x4TA5k/semgrep-clone`, whose HEAD was verified as `4e1816eb16fd6230059daa76ae6a59127b1f94f3`. The native baseline scan used merge base `5205fada80635f7d9dd4a1967c94a256e60a99cb`, `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, `p/default`, two jobs and metrics off. It ran 131 rules over 11 changed targets with zero findings, no parser errors and approximately 100 percent parsed lines among scanned targets. Eight paths matched configured ignore patterns, including evaluation/test paths; this is not a claim that Semgrep scanned those files. Summary diagnostics are in `2026-10-30-624-semgrep.json`. No baseline checkout touched the source worktree.

Third-party tool note: `semgrep scan --help` emitted a cmdliner escape-rendering warning while returning help and exit zero. The actual scan completed normally. No third-party issue was filed.

## Final lint, versions and full suite

`lint-and-fix --no-push` used check modes because repository-wide writers reach protected Scrut, generated and historical paths, and the brief excludes the known fixture defect. No lint fixes were needed in the branch's own changes. `make lint` passed Markdown lint over 806 files, Prettier, ShellCheck and shfmt, then failed only the six known rooted-operand findings in `tests/fixtures/review-submodule-fixture`. `actionlint` passed separately because the aggregate stopped before it. No formatter rewrote protected files. The plugin README's permission JSON was also parsed and now lists both edit helpers using the existing scope-helper convention; no live permission configuration changed.

The full-suite driver acquired `~/Work/projects/.locks/tooling-full-suite.d`, wrote this workstream's handle and released its lease on exit. One `SCRUT_JOBS=2 make test-all` invocation, without `make -s`, stopped at that baseline lint failure. Only the components not yet started were then run under the same lock: `make validate` passed, and the full Scrut run completed with **57 documents, 1,914 cases: 1,912 passed, 2 failed, 0 skipped**. The new refusal document passed all 33 cases.

Both failures exactly match the brief: `environment-isolation.md:39` expected the unchanged fixture's rooted-operand checker to pass, and `run-scrut-documents.md:254` received macOS `child setpgid ... Operation not permitted`. The fixture, checker, runner and affected old documents are unchanged against the merge base. No full-suite retry or unrelated fix ran. This is completed validation with known baseline failures, not an all-green suite.

`check-versions` verified the minor bump **1.1.4 to 1.2.0**, all 60 plugins registered, manifest-only version ownership and matching Codex manifests where present. A current GitHub main-file read confirmed 1.1.4 before publication. Origin fetch and push identities match the active, public, non-fork `github.com/cboone/agent-harness-plugins`; the brief explicitly selects `main`. No remote feature branch existed at the pre-publication check.

## Verification so far

- `make build`: passed; mirrors generated from canonical sources.
- `make validate`: passed with the gitlink refusal and regenerated mirrors.
- Focused `review-scope.md`: 48 cases passed.
- Focused `result-check.md`: 17 cases passed; schema unchanged.
- Focused `anti-pattern-edit-worktree.md`: 33 cases passed with gitlink refusal, initialized and uninitialized cases, and nested invocation coverage. Earlier plants were restored before this run.
- `shellcheck` and `shfmt`: passed for the refusal helper.
- Disposable scope fixture: stable recapture; measured selected, new-test and sibling files while the committed range was empty; staging alone changed the snapshot; capture preserved the real index.
- Ad hoc live edit execution: passed in a disposable committed-range fixture. Only the necessary existing sibling outside `--files` changed; node endpoint tests changed from red to green. Parent independently verified schema, complete success, no findings or gaps, unchanged HEAD/index and no other files changed. Source remained unchanged.
- Read-only behavioral walkthrough: twelve cases examined. This was interpretation of the prompt, not live edit execution. It found the edit-only capture-base lookup omission, now corrected. Its observation about the existing checker accepting failure objects is outside this change: the edit workflow explicitly stops on failed or unavailable phase results.

## Plants

| Planted defect                              | Instrument expected to catch it      | What actually happened                                                                                                     | Regression test                                                           |
| ------------------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Disable dirty-worktree refusal              | Focused edit-worktree Scrut document | Four expected failures; restored 13/13                                                                                     | Unstaged, staged and untracked refusal cases                              |
| Return success after printing dirty refusal | Exit-status assertions               | Four expected exit-code failures; restored 13/13                                                                           | The same four refusal cases                                               |
| Disable hidden-flag refusal                 | Hidden-flag regression cases         | Five expected failures; restored 23/23                                                                                     | Clean and edited assume-unchanged, skip-worktree and combined flags       |
| Disable ordinary refusal after capture      | Post-capture concurrent-edit case    | Five failures including the named post-capture case; restored 23/23                                                        | Change introduced after before-capture                                    |
| Disable gitlink refusal                     | Registered and embedded child cases  | Seven failures, including both hidden-child cases; restored 33/33                                                          | Initialized hidden-child cases, clean gitlinks and uninitialized gitlink  |
| Remove rooted inventory pathspec            | Nested-invocation cases              | Two expected exit-code failures; restored 33/33                                                                            | Hidden parent index entry and parent gitlink outside invocation directory |
| Reuse original range for final verification | Opt-in edit acceptance evaluation    | Exit 1: reply review incomplete; both fix paths listed in final not_reviewed                                               | Tracked and newly untracked sibling coverage                              |
| Optimize Python assertions away             | Evaluation runtime guard             | Post-commit optimized run exited 1 with the expected assertion-runtime diagnostic; normal saved positive case passed again | Refuse an optimized interpreter before evaluating results                 |

The post-capture plant measures the helper's ability to refuse an edit after capture. The workflow's requirement to invoke that helper after capture is agent prose, not an executable orchestration test. The gitlink plant compiled and ran; registered and embedded initialized-child assertions saw success instead of refusal. The hidden-parent-flag case also detected the wrong diagnostic.

The original-range plant changed the real canonical skill and edit reference temporarily, under an exact-path restoration trap. The live fixture made both functional corrections and passed its existing assertions, but its final input manifest contained only `range.mjs`. Aggregate JSON remained honest: `complete: false`, with `siblings.mjs` and `new-count.mjs` unreviewed. The evaluator failed on that completeness assertion, not a syntax or setup error. Both source files were restored and compared byte-for-byte with recorded backups. Positive, negative and ad hoc run evidence remains under `/tmp/624-local.x4TA5k`.

## Local handoff

Local implementation, reviews, source generation, focused regressions, live evaluations, plants, baseline scan and the locked full-suite attempt are complete. The brief's known baseline failures remain outside this change. Structural review ended **clean at Critical**; general review **ended: fixes changed no behavior** after taking its test and dependency-documentation findings. No reviewer Important or Critical label was downgraded.

Publication follows the project's signed logical-commit tidy and ready-PR procedure. The final tree comparison, commit IDs and PR URL are reported to TOOLING by mailbox. The local pre-tidy branch preserves the original review history; no pushed history is rewritten. TOOLING owns merging.
