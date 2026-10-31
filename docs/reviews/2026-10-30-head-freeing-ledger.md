# Head freeing counts review ledger

## Scope and reproduction

Issue: [companion-aware head freeing counts](https://github.com/cboone/agent-harness-plugins/issues/457).
Base: `5205fada80635f7d9dd4a1967c94a256e60a99cb` (`origin/main`).

The original payload requires schema-v2 metadata on current main. Metadata-only adaptation validates as three issues in one lane and reproduces `freedAfter: 1` with `then one more` while companion 4 remains queued. The fixed template reports zero and omits the promise; existing row states are unchanged.

## Plants and execution

The five-case Scrut document passes on the fixed tree. Tests were committed before plants. Canonical template plants were applied separately and restored from the recorded fixed file; mirrors were not edited.

| Plant                                                        | Instrument                  | Observed result                                                                   | Regression                                          |
| ------------------------------------------------------------ | --------------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------- |
| Restore successor-root-only soft ordering                    | Head freeing Scrut          | Two expected failures: external ordering and blocked head companion; three passes | Companion ordering and blocked head companion cases |
| Admit every head companion to freeing unit                   | Head freeing Scrut          | Blocked head companion expected failure; four passes                              | Blocked head companion case                         |
| Skip hard-blocked successor companions                       | Expanded head freeing Scrut | Combined hard/soft case fails; six pass                                           | Hard-blocked companion ordering case                |
| Force count observation to zero against original template    | Snapshot equality           | Rejected through rendered wording                                                 | External companion ordering case                    |
| Force wording observation to false against original template | Snapshot equality           | Rejected through computed count                                                   | External companion ordering case                    |

No syntax failure substituted for an assertion failure. Both plants changed the computed count and rendered wording from zero/false to one/true.

## Structural loop

Fresh read-only `codex exec`, `gpt-6.1-sol`, high effort, context 872000. Anti-patterns and report-only simplify ran in parallel. Both completed with exit zero and nonempty reports; anti-patterns JSON passed its bundled schema check. Simplify covered all four cleanup angles inline, report only, as required by the project.

- Nit round: anti-patterns found `Tests that cannot fail: write-scrut-tests: Critical setup lacks fail-fast`. Reviewer and assessed severity: Nit; setup failure produced dependent failures, not a false pass. Taken: add fail-fast to the two shared setup blocks.
- Simplify: no findings.
- Review again: no; changes affect test failure handling only.
- End state: ended: fixes changed no behavior.

Read-only reviewers could not reach GitHub. Repository ownership, fork and archive status were verified by the worker before changes. Their deliberately unrun runtime checks are covered by the worker's execution and subsequent validation.

## Final validation

Baseline Semgrep, lint-and-fix, versions, the assigned full suite and affected rechecks are recorded below. The mailbox handoff records the final tidy comparison and head. Copilot is paused. TOOLING merges; no live configuration changes.

## Focused review loop

Nit round, same read-only model, effort and context as structural review. Installed `codex-aspects` ran code, errors, tests, comments and types in parallel against snapshot `7510cf651f5335571205f3c0d20b89bd7dd24acb`, HEAD `f32a898c`. All five exited zero, returned schema-valid nonempty replies and reported complete membership. Code, comments and types found no findings.

| Reviewer label                                                              | Our severity and impact                               | Take or record                                                          | Review again                   |
| --------------------------------------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------ |
| errors: suggestion, relevant render error output discarded                  | Nit: failing tests still fail, but discard the cause  | Take: retain renderer failure diagnostics and status in shared setup    | No production behavior changes |
| tests: suggestion, hard-blocked successor companion ordering lacks coverage | Nit: implementation is correct; missing test boundary | Take: retain external soft ordering while adding companion hard blocker | Test-only change               |

End state: ended: fixes changed no behavior. No Important or Critical finding or downgrade. No recurrence of the fail-fast finding. The test gap is a separate companion-filtering defect class, not a repeated implementation finding. The proposed missing boundary receives its own canonical-template plant.

The repository-local aspect helper refused to run before launching because it is inside the reviewed repository. The installed helper was then used, as instructed. An initial scope capture was invalidated by worker edits and rejected; a settled capture supplied the actual review. These were pre-launch scope/setup failures, not completed reviewer rounds.

The expanded document passes all seven testcases (setup plus six execution cases). Skipping hard-blocked successor companions in the canonical freeing predicate fails exactly the added combined hard/soft case, with six passes. The plant was restored. Weakening either the count observation or the wording observation independently still rejects the original defect through the other observation. Focused review's closing scope comparison reported `scope_changed: false`, identical content trees and no lasting changes found.

## Trims

Fresh read-only Codex runs, gpt-6.1-sol low effort, context 872000, both exit zero with complete nonempty reports. trim-comments proposed no changes. trim-text proposed two wording reductions in the ledger and Scrut introduction; both taken. No production edits.

## Semgrep and lint

Native baseline Semgrep ran in `/tmp/head-freeing-457/semgrep-repo`, a disposable shared clone at `95f50da3540cd6ecc0fb8866ad05ac848b6854d5`. `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, config `auto`, baseline `5205fada80635f7d9dd4a1967c94a256e60a99cb`. Exit zero, 66 rules over five scanned files, zero findings, no parser errors, approximately 100 percent parsed coverage. Test fixtures were outside the scan target set. Semgrep skipped baseline-side execution because current findings were empty; native baseline selection was supplied. The real worktree was not checked out by the scanner.

`lint-and-fix --no-push`: scoped Markdown fix and Prettier passes changed nothing. Full `make -k lint` passed Markdown, Prettier, ShellCheck and shfmt, then failed only the known fixture-operand validator on `tests/fixtures/review-submodule-fixture` at lines 132–134 and 254. These pre-existing failures are explicitly outside the brief. Actionlint passed separately because make did not reach its recipe after the prerequisite failure. Lint status: failure, known baseline only; no fixes or lint commit needed. No failing check is reported as clean.

Version check: publish-report-board advances from 1.3.4 to 1.3.5, appropriate for this bug fix. Generated manifest agrees; all 60 catalog entries are registered and versions belong to manifests, with present Codex hook manifests matching. Default branch main and actual origin/main merge base were verified live.

## Single full suite and affected rechecks

TOOLING assigned the slot at `2026-10-31T02:39:13Z`. The atomic lock held owner `457-head-freeing-counts`; the EXIT trap released it after the single `make -k test-all SCRUT_JOBS=2` run. Keep-going allowed Scrut to run despite known lint failure; no silent make option was used.

The full run exited 2: 56 of 57 documents passed, including all seven new cases. Across 1,888 cases, 1,865 passed and 23 failed, all in environment-isolation.md. Lint reported the known fixture operand failures. Validation also caught an omission in the new document: its setup had not sourced the required Git-environment reset. That omission caused the other environment-isolation failures to cascade.

Added the established reset to the new document setup. The existing guard detected the omission before the fix. Subsequent affected checks: the seven-case document passed; `make validate` passed JSON, fixture environments and every plugin validation; environment-isolation.md passed 50 of 51 cases, with only its known review-submodule-fixture operand assertion failing. No second full suite or lock acquisition occurred. The correction changes test setup only, so no further behavioral review round is required.

Known baseline failures remain outside scope and are not described as passes. No production code changed after its review or scan.
