# Review-plan trailing issue ledger

Scope: issue 493, branch `fix/493-review-plan-trailing-issue`, merge base `5205fada80635f7d9dd4a1967c94a256e60a99cb`. Full local review order; no live configuration changes. TOOLING owns merge.

## Validation

- Focused Scrut suite: 28 cases passed before planting; implementation and tests committed at `8d83393f`.
- Plants: all five were detected by the named regression cases; restored helper also checked under system Bash 3.2.
- Structural reviews, focused aspects, trims, Semgrep, lint, full-suite observation and version checks completed. The known fixture baseline prevents an all-checks-green result; exact-tree tidy and the ready PR follow.

## Plants

Each plant changes the real helper after the tests have been committed. Restore it between runs. Scrut checks exact output, not just exit status.

| Planted defect                      | Instrument expected to catch it | Observed result                                         | Regression case                      |
| ----------------------------------- | ------------------------------- | ------------------------------------------------------- | ------------------------------------ |
| Remove suffix tolerance             | Focused Scrut suite             | Make exit 2; 8 of 28 cases failed, including named case | Trailing issue number                |
| Widen exact equality to a substring | Focused Scrut suite             | Make exit 2; 8 of 28 cases failed, including named case | Near miss with extra subject word    |
| Ignore retained issue identity      | Focused Scrut suite             | Make exit 2; 5 of 28 cases failed, including named case | Wrong trailing issue                 |
| Strip arbitrary trailing numbers    | Focused Scrut suite             | Make exit 2; 7 of 28 cases failed, including named case | Numeric subject without branch issue |
| Remove two trailing issue suffixes  | Focused Scrut suite             | Make exit 2; 1 of 28 cases failed, including named case | At most one trailing suffix          |

## Reviews

Structural Nit round: anti-pattern review and report-only simplify ran in parallel in fresh `codex exec` read-only sandboxes, `gpt-6.1-sol`, high effort, 872000-token window, approvals never and web search disabled. The project requires fresh Codex contexts, overriding the shared reference's default inline path for Codex callers. Both completed with no findings: clean at Nit. Simplify covered reuse, simplification, efficiency and altitude inline in its single reviewer. No editing stage ran. All eight canonical files were read, with generated mirrors excluded. No lasting changes found by scope comparison.

An earlier preliminary scope capture overlapped ledger edits and correctly refused an inconsistent tree. It was not used as review evidence; the subsequent structural before/after snapshots are identical (`13a52256d2925d742ed75eb0b3a3924a1fbbbe69`).

The first `make test-all` run stopped on MD012 in the new Scrut file. Removed its extra final blank line manually; this changes no behavior and costs no review round. `make validate` passed. The restored focused suite and the same 28 cases through a wrapper invoking `/bin/bash` 3.2 both passed.

Focused Nit round: `code`, `errors`, `tests` and `comments` ran in parallel through the installed `review-pr-with-codex` 2.3.1 helper, with the same read-only settings as structural review. All four returned exit 0 and schema-valid replies for snapshot `71b7c7894afde31fe528f7fbbbe5fe12567e6b4b`. Types were skipped because no types changed; simplify had already run report-only in step 1. Before/after scopes matched, with no lasting changes. The repository copy refused to run inside its own review target before launching any aspect; the installed copy was used as directed, with no bypass.

| Finding                                            | Reviewer's label | Assessed severity and impact                                                      | Take or record                                                                                             | Review again                                                |
| -------------------------------------------------- | ---------------- | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Code: recommended permissions omit required helper | `important`      | Important: users following the example can be blocked from running the comparator | Take: add a helper-specific Bash rule to the README and regenerate its mirror; no live permissions changed | No: documentation example only; matching behavior unchanged |

Focused loop end: ended: fixes changed no behavior. No other focused findings. No downgrade, recurrence or design stop.

One read-only Codex trim round covered comments and prose with `gpt-6.1-sol`, low effort, 872000-token window. Both completed, classified all eligible canonical files, and proposed no changes. Code fences, generated files and unchanged units were excluded. No flags or cut material.

Final `make test-all` passed Markdownlint, Prettier, ShellCheck and shfmt, then stopped at the known `tests/fixtures/review-submodule-fixture` operand-path lint failure (lines 132-134 and 254). The brief explicitly excludes that baseline defect; it was not edited. `make validate` passed separately, and the full `make test-scrut` run was observed separately because the aggregate stopped before it. This is a baseline limitation, not an all-checks-green claim.

## Semgrep

Semgrep 1.180.0 completed with exit 0 in disposable shared clone `/tmp/review-plan-493.0WUgbC/semgrep-clone` at `5e410c3e`, against merge base `5205fada80635f7d9dd4a1967c94a256e60a99cb`. Command: `SEMGREP_REPO_NAME=cboone/agent-harness-plugins semgrep scan --config auto --baseline-commit 5205fada80635f7d9dd4a1967c94a256e60a99cb --json --output /tmp/review-plan-493.0WUgbC/semgrep-clone-result.json`. No metrics override. Result: 131 rules, 7 changed targets, approximately 100.0% parsed lines, zero findings, `errors: []`, no skipped rules; five generated or test paths excluded by ignore policy. The comparator was scanned. With no current findings, Semgrep skipped the comparison-side baseline scan while retaining baseline-limited target selection.

The first scan launch accidentally used the worktree directory. It was stopped by its recorded PID, 50664, and observed exit 143 before using its output. HEAD and the working tree were unchanged. Only the subsequent completed disposable-clone scan counts as evidence.

## Final lint

`lint-and-fix --no-push`, parent continuation: after checks, preserve the known baseline fixture failure from the brief, tidy the exact tree, then push and open a ready PR. No other unresolved check is waived.

| Tools                                                            | Recorded command | Mode and policy                                                                                                                                                                                                                                      |
| ---------------------------------------------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Markdownlint, Prettier, ShellCheck, shfmt, fixture operand check | `make lint`      | Check-only; global fixers would reach protected Scrut files or generated files. Scoped instructions say Scrut files are never reformatted and generated files are rebuilt. Changed prose and the helper were formatted in the earlier scoped passes. |
| Actionlint                                                       | `actionlint`     | Check-only; run separately because the known fixture failure stops `make lint` first                                                                                                                                                                 |
| JSON, fixture environment and plugin validators                  | `make validate`  | Check-only                                                                                                                                                                                                                                           |

These same commands are the recorded final verification commands. No whole-tree fixer is authorized to modify protected or unrelated files.

Final verification: `make lint` again passed Markdownlint, Prettier, ShellCheck and shfmt, then failed only on the six known fixture operand diagnostics. Separate `actionlint` and `make validate` both exited 0. No formatting fixes were needed. The fixture is byte-identical to the merge base. Lint status: failure due to the expressly excluded baseline; no skipped tool or additional unresolved lint finding. Check-only by project policy: Markdownlint, Prettier and shfmt. Continuation follows the brief's explicit baseline exclusion, without claiming lint success.

## Full-suite results

`make test-scrut` completed: 56 of 57 documents passed; only `environment-isolation.md` failed. Its 51 cases initially had two failures: the known fixture operand checker and a generated-mirror check that overlapped the README mirror rebuild. The generated-file diagnostics made that check unreliable. No further generator writes occurred during an isolated rerun of the entire document: 50 cases passed and only the same known fixture operand check failed. No testcase was skipped. The transient mirror failure is resolved by the stable rerun and final standalone validation, not counted as an initial pass. The new matching document's 28 cases passed in the full suite as well as in focused default-Bash and system-Bash-3.2 runs.

The baseline fixture error is the only remaining test limitation. Neither the aggregate nor the full Scrut run is reported as clean.

## Version and handoff

`check-versions`: `review-plan` advances from `1.1.0` to `1.1.1`, a patch fix to existing matching behavior. All 60 plugins have matching marketplace coverage, valid manifest-owned versions and matching Codex manifests where present; marketplace entries and metadata contain no version fields. The generated review-plan mirror was rebuilt. No other plugin version changes.

Completed plan moves to `docs/plans/done/`. Tidy preserves the exact checked tree in logical signed feature, test and process-document commits; its backup and equality result are reported in the mailbox handoff. Later changes after the Semgrep scan contain only process records and the plan's completed location; the shipped comparator, skill, README, manifests and generated plugin are unchanged from the scanned head. Push and ready PR are authorized by the brief. TOOLING owns merge. No live configuration, hook activation, credential or notification changes.
