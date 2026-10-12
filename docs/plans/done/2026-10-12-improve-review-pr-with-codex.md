# Improve Review PR with Codex

## Goal and status

Make `review-pr-with-codex` read-only by default, bind results to everything the reviewers inspect, and make its Codex entry points reliable under instruction and concurrency constraints. Calibrate findings by impact and resolve the observed cancellation-test failure.

Status: implemented on 2026-10-12, including RP-1 and RP-2. Local validation and defect controls are recorded in [the validation report](../../reviews/2026-10-12-codex-review-validation.md). Linux runtime execution, actual native spawn failures and native interruption remain unverified; no push or CI run was authorized. The scope covers the five review concerns and the cancellation failure reported on 2026-10-12.

## Scope

Canonical changes belong in `plugins/review-pr-with-codex/`: the skill, aspect and invocation references, helper scripts, README, and manifests. Shared snapshot changes also belong in the byte-identical `plugins/review-until-clean/scripts/review-scope` copy and its affected consumers and documentation. Tests belong in the existing scrut suites and fixture helpers. Update catalog surfaces and regenerate mirrors only when those source changes require them.

Keep the existing review aspects, structured output, and failure reporting. No model-default changes, new plugins, global configuration edits, authentication changes, pushes, or PR creation are included.

## 1. Separate review from explicitly requested edits

- [x] Make omitted aspect arguments and `all` select applicable review aspects only. Require an explicit `simplify` argument to authorize edits. Define `all simplify` as review all applicable aspects, then simplify if eligible, and reject `simplify` alone with guidance to select review aspects too.
- [x] Retain the existing prerequisites for simplification: every selected review aspect succeeded, no Critical findings, and the reviewed scope remains valid. Do not interpret a request for review as permission to simplify.
- [x] After simplification, measure the actual changes and report out-of-scope edits and failures. Run relevant project formatting, linting, and tests, respecting the scope restriction. If a required command would modify unrelated files, use a scoped or check-only alternative, or report the limitation.
- [x] Rerun the selected review aspects against the final state after edits and any permitted formatting. Do not simplify again automatically. Distinguish the initial review, measured edits, validation, and final review in the report; a failed check or final aspect leaves the result incomplete.
- [x] Update options, examples, routing text, and README behavior consistently. Preserve the rule that nothing is staged, committed, or pushed by the skill.

## 2. Bind validity to the complete review scope

- [x] Keep `tree` as the working-tree content identifier used to measure edits. Strengthen `snapshot` to include HEAD, resolved base, working-tree content, index content, and the committed, staged, unstaged, and untracked bucket membership. Inspect existing snapshot consumers before changing the contract.
- [x] Represent index content deterministically, including executable modes and conflict stages. Do not rely on index timestamps or assume the index can always be written as a normal tree. Preserve existing explicit failures for unsupported repository states.
- [x] Bracket scope collection with checks for index content, HEAD, and base stability as well as disk content. Refuse a scope assembled from inconsistent reads.
- [x] Extend the comparison output to distinguish content changes from scope validity changes. Any snapshot mismatch invalidates the prior review, including index-only changes or base/HEAD movement with identical disk content. Block simplification and collect a fresh scope before rerunning review.
- [x] Update both `review-scope` copies together, their schema and affected consumers. Retain the documented limitations for ignored files, reverted edits, and Git normalization; describe those separately from validity checks.
- [x] Migrate `review-until-clean` explicitly: prepare authorized intent-to-add coverage before capturing the round snapshot, retain that preparation through review and validity checking, and restore it only after those checks or on failure/cancellation. Capture a fresh snapshot after any new preparation. Preserve pre-existing index entries and carry unchanged preparation through confirming rounds. Update the old staging-invariance assertions and documentation. Verify that an authorized preparation can complete a clean round and that unrelated index-content changes invalidate it (RP-1).

Validation must reproduce the reported case: replace the indexed version of a tracked file while leaving its disk content unchanged. The snapshot must change, the measured disk diff must remain empty, and the prior review must be invalidated. Also cover base/HEAD movement, bucket changes, unchanged-state stability, and preservation of the real index.

## 3. Make instruction handling match Codex behavior

- [x] Inspect supported CLI controls and local instruction discovery before choosing an isolation mechanism. Resolve trusted instructions from the base revision with Codex's precedence: `AGENTS.override.md`, `AGENTS.md`, then supported configured fallback names. Handle directory scope, empty files, and the repository's symlinked `CLAUDE.md` convention without treating symlink text as a complete guide.
- [x] For standalone runs, verify a supported way to prevent current-checkout instruction files from becoming active project guidance, then supply the resolved historical guidance as trusted review instructions. Preserve applicable global policy and authentication; do not edit user configuration or use sandbox bypasses.
- [x] For native subagents, use fresh task context when supported and document which instructions and permissions are inherited. If the harness cannot isolate current project guidance, report that limitation explicitly. Prefer the standalone entry point when verified isolation is required and available; otherwise report the unresolved limitation rather than claiming isolation.
- [x] Keep changed instruction files and reviewer output classified as review material. Match README and invocation claims to measured guarantees, including the distinction between sandbox-enforced read-only access and an instruction-only restriction.

Use deterministic discovery tests and a controlled Codex smoke test with conflicting base and checkout instructions. Record the CLI version, active instruction sources, and observed result. Stub tests alone cannot establish instruction isolation.

## 4. Schedule native aspects within available capacity

- [x] Replace the requirement to spawn every aspect before waiting with bounded scheduling. Account for parent and existing-agent occupancy; use available slots and launch remaining aspects as capacity becomes available.
- [x] Handle partial spawn failures without discarding successful results. Use sequential execution for remaining aspects when the harness cannot provide more workers, while retaining each aspect's exact prompt and output validation.
- [x] Specify fresh-context requirements for model and effort overrides where the spawn interface requires them. Report actual settings when overrides are unsupported, including the sequential fallback.
- [x] Define completion and cancellation handling for every launched aspect. Stop and observe active workers before the final measurement; release completed workers where the interface supports it. Report incomplete cancellation explicitly.

Verify the five-aspect case with only three available child slots, plus zero capacity, occupied slots, partial spawn failure, and unsupported model overrides. Use a native-harness smoke test for behavior the CLI stub cannot exercise.

## 5. Calibrate findings consistently

- [x] Establish a common confidence and impact standard for all review aspects. Require a concrete introduced problem, a supported scenario, and confidence of at least 80 for a reported defect. Keep severity separate from confidence and aspect-specific ratings.
- [x] Reserve Critical for merge-blocking consequences supported by the evidence or explicit project rules. A factual documentation error, broad catch, or fallback is not automatically Critical.
- [x] Allow documented best-effort operations, expected negative results, optional probes, and intentional fallback behavior when failures remain appropriately observable. Require findings to explain the unexpected failure and its effect.
- [x] Retain tests and types ratings as explanatory metadata. Treat optional design improvements and simplification suggestions as suggestions, with the preservation-of-behavior requirement intact.

Verify prompts with contrasting examples: harmless documentation inaccuracies versus unsafe operational instructions, and justified optional probes versus suppressed failures that lose data. Check exact prompt contracts deterministically; assess model calibration with controlled examples without claiming stub tests prove reviewer quality.

## 6. Diagnose cancellation before changing it

The helper suite passed 55 of 56 cases on two runs. The cancellation case reported `child still running` after TERM. This establishes a failed check, but does not yet distinguish a running process from a terminated process awaiting collection.

- [x] Reproduce with process-state evidence and verify whether the remaining child is running, awaiting collection, or outside the cleanup mechanism. Inspect both test synchronization and helper cleanup before assigning the cause.
- [x] If cleanup is defective, stop the relevant process tree reliably and observe completion before returning. If the assertion is defective, update it to distinguish active execution from terminated state while retaining the guarantee that cancelled simplification cannot continue editing.
- [x] Cover delayed shutdown and a descendant process capable of writing a sentinel after cancellation. Prove the check detects continued execution. Use finite test synchronization and avoid leaving fixture processes running.
- [x] Verify stock Bash 3.2 and the installed Bash on macOS, and keep cancellation failure visible in the aspect report. Linux runtime execution is unavailable locally and remains an explicit validation limit for existing Ubuntu CI.

## Integration and acceptance

- [x] Add behavioral coverage to `tests/scrut/codex-aspects.md`, `tests/scrut/review-scope.md`, the shared-copy check in `tests/scrut/repo-tooling.md`, and affected fixtures as needed. Read scoped test instructions before edits. Add model smoke-test evidence separately from deterministic test results.
- [x] Validate the complete review/edit workflow (RP-2): omitted arguments and `all` never edit; `all simplify` runs gated edits, validation and final review; `simplify` alone is rejected; failed aspects, Critical findings and scope movement prevent edits; failed validation or final review leaves the result incomplete. Bind actionable findings to the final snapshot and mark superseded initial findings. Extract deterministic selection and eligibility decisions into the helper where useful, then exercise host-controlled sequencing in controlled smoke tests.
- [x] Determine version bumps from the final contract. The default edit policy changes existing behavior, so evaluate a major bump for `review-pr-with-codex`; choose the shared consumer's bump based on its resulting compatibility. Mirror manifest versions and update catalog descriptions only when their wording changes.
- [x] Run `make build`, then relevant checks and `make test-all`. Confirm generated mirrors, cross-references, shared-helper identity, and the final observed test results. Use `check-versions` before a PR.
- [x] Update this plan as implementation proceeds and create signed commits at logical boundaries.

Acceptance requires read-only default invocation, explicit authorization for simplification, validation and review of final edits, invalidation on index or scope movement, accurate instruction guarantees, completion within native worker limits, impact-based findings, and a cancellation check that reliably detects continued execution.

## Completion record

Implementation and local validation completed on 2026-10-12. The complete repository gate passed all 26 scrut documents after the independent-review correction. Final external-TMPDIR guard checks passed full lint and validation, 75 aspect cases and 42 scope cases on Bash 3.2. Both cancellation defect controls failed the intended case, and no active control processes remained. Version ownership, generated mirrors and signed commits were verified. External and native-harness verification limits remain documented in the validation report.
