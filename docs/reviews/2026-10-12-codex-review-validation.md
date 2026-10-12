# Codex review workflow validation

## Scope

Validation of the [approved implementation plan](../plans/done/2026-10-12-improve-review-pr-with-codex.md). Canonical source changes affect `review-pr-with-codex` and the shared snapshot contract in `review-until-clean`; both plugins advance to `2.0.0` because their documented behavior changes incompatibly.

## Deterministic checks

- Scope cases verify index-only changes, unchanged disk trees, staging and intent-to-add invalidation, preserved real indexes, authorized coverage preparation through confirmation, and rejection of index movement during collection.
- Aspect cases verify read-only default selection, explicit edit authorization, complete successful aspect coverage, Critical and stale-scope gates, historical guide precedence and symlink boundaries, final validation classification, and descendant cancellation with a delayed write sentinel.
- The complete lint, validation and 26-document scrut run passed after the independent-review correction. After the external-TMPDIR guard, full lint and validation plus both affected suites passed again.
- The final 75 aspect cases and 42 scope cases passed on stock macOS Bash `3.2.57`. Linux runtime verification is unavailable locally. Existing Ubuntu CI remains the Linux check, but no CI run was triggered by this work.

## Real Codex checks

Standalone checks used `codex-cli 0.162.1`, model `gpt-6.1-sol`, and reasoning effort `medium`, with existing authentication and no configuration changes. Sample repositories and raw prompts, logs and replies stayed outside the project.

1. **Instruction discovery:** a rendered prompt started inside the sample repository included the conflicting current-guide marker. The external working-directory prompt excluded that marker. Global configuration was retained; no claim is made that this isolates every plugin or independently discovered instruction source.
1. **Read-only review:** code and comments runs produced valid matching JSON, exited zero, and preserved the full scope snapshot and disk tree. The current guide's instruction to skip review was treated as review material.
1. **Native scheduling:** five named aspects completed using three fresh-context subagents and two sequential parent-session reviews. All replies validated against the same snapshot, with no scope or disk changes. Tasks were supplied as exact rendered prompt files through a file-reading envelope. The first three native settings were inherited. Two additional fresh-context native subagents then accepted explicit `gpt-6.1-sol` and `medium` settings and returned valid replies over the restored identical snapshot, completing all five native aspects across bounded batches. Actual spawn failures and worker interruption were not exercised.
1. **Explicit editing:** an initial sample's historical guide prohibited edits, and simplification reported a suggestion without changing files. A second sample explicitly permitted requested refinement. Following successful initial review and an eligibility check, simplification changed only the in-scope implementation and behavioral-check files. Syntax and behavioral checks passed, then all selected final review aspects succeeded with zero findings. The final classification was complete. Classifying the same review with failed validation correctly returned incomplete.
1. **Calibration:** a sample combined an absent optional-cache probe with a save operation that returned success after a failed write. The error aspect accepted the optional probe and reported only the suppressed write failure, with confidence 100 and Important severity. This is a measured example, not a guarantee of reviewer accuracy.

The complete editing sequence was driven by the parent session using the revised skill and helpers. The helper does not independently execute the entire host workflow.

## Independent implementation review

A standalone code aspect completed over the full committed, unstaged and untracked implementation scope, exited zero, and matched the unchanged snapshot. It found one Important regression: historical `git ls-tree` lookups omitted guides when invoked from a nested directory. The lookup now uses the resolved repository root and literal pathspecs, with a regression case comparing root and nested prompts. The root/nested prompt comparison passed in the complete suite and on Bash 3.2. A subsequent boundary check also found that repository-local `TMPDIR` could weaken external artifact placement; both helpers now reject it before producing scope or invoking a reviewer.

## Cancellation controls

The original restricted test reported a remaining child. Process inspection itself was denied in that environment. With process access enabled, the original fixture stopped; no repository defect was inferred from the restricted result alone. Cleanup now enumerates observed descendants, signals them with TERM, polls for stopped or terminated state, and explicitly reports inspection failure or a bounded-wait expiry as incomplete cancellation.

| Planted defect                                                      | Instrument expected to catch it               | Observed result | Regression coverage                                 |
| ------------------------------------------------------------------- | --------------------------------------------- | --------------- | --------------------------------------------------- |
| Omit descendant termination while stopping the parent               | Cancellation process and delayed-write checks | Pending         | `tests/scrut/codex-aspects.md`, stopping the helper |
| Omit descendant termination and remove the active-process assertion | Delayed-write sentinel check                  | Pending         | Same cancellation case                              |

Unobserved descendants and processes created during shutdown remain a limitation. A helper exit is not proof that arbitrary detached work stopped. Incomplete cancellation prevents further edits and a complete review verdict.

## Final verification

The complete repository gate passed all 26 scrut documents after the independent-review correction. The committed cancellation check passed unmodified, and both temporary defect controls produced the intended single failing case; their fixture processes were stopped afterward. The version audit confirmed both forward `2.0.0` bumps, generated-manifest agreement, complete marketplace coverage and manifest-only version ownership. The implementation checkpoint is GPG-signed and verified. Final full lint and validation passed after the external-TMPDIR guard; all 75 aspect cases and 42 scope cases passed on Bash 3.2. A process-state readback found no active control processes. No push or PR creation is part of this work.
