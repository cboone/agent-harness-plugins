# Branch Review: fix/390-write-bash-scripts-bash-3.2

Base: `main` (merge base: `340f3192`)
Commits: 3
Files changed: 9 (1 added, 8 modified, 0 deleted, 0 renamed)
Reviewed through: `9e9c5f1b`

## Summary

This branch makes the `write-bash-scripts` guidance safe for macOS's bundled Bash 3.2 when strict mode is enabled. It corrects examples that mishandle empty argument and array lists, identifies Bash 3.2-incompatible features and replacements, and separately fixes examples that fail under strict mode on current Bash. The plugin patch version and catalog state are updated, with the generated Codex mirror refreshed.

## Changes by Area

### Bash compatibility guidance

The canonical guide now prescribes unbraced `"$@"` and `"$*"` for argument lists, guards empty arrays under `set -u`, and replaces or labels features unavailable in Bash 3.2. It also adds a version guard for scripts that require Bash 4 and documents portable approaches for line collection, associative lookups, casing, namerefs, variable tests, negative indices, globbing, and combined pipes or redirections.

Files: `plugins/write-bash-scripts/skills/write-bash-scripts/SKILL.md`, `plugins/write-bash-scripts/skills/write-bash-scripts/references/BASH.md`

### Strict-mode examples

The guide now gives `TRACE` an empty default before testing it, recommends `((i += 1))` instead of a post-increment statement that evaluates to zero, and uses that form in the subprocess-scope example. These changes prevent `set -u`, `set -e`, and `pipefail` from making the examples exit unexpectedly.

Files: `plugins/write-bash-scripts/skills/write-bash-scripts/references/BASH.md`

### Release metadata and distribution

`write-bash-scripts` moves from `2.0.3` to `2.0.4`, and both marketplace files report the recomputed `catalog-M70-m103-p157-n57` state. The committed Codex mirror contains the same plugin metadata and guide content as the canonical source.

Files: `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `plugins/write-bash-scripts/.claude-plugin/plugin.json`, `dist/codex/plugins/write-bash-scripts/.claude-plugin/plugin.json`, `dist/codex/plugins/write-bash-scripts/skills/write-bash-scripts/SKILL.md`, `dist/codex/plugins/write-bash-scripts/skills/write-bash-scripts/references/BASH.md`

### Planning and follow-up tracking

The branch adds its dated plan and the plan's separate repository-script audit is tracked by open issue [#433](https://github.com/cboone/agent-harness-plugins/issues/433). Keeping the plan committed follows this repository's `cboone` convention.

Files: `docs/plans/todo/2026-09-14-write-bash-scripts-bash-3-2-compatibility.md`

## File Inventory

### New files

- `docs/plans/todo/2026-09-14-write-bash-scripts-bash-3-2-compatibility.md`

### Modified files

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `dist/codex/plugins/write-bash-scripts/.claude-plugin/plugin.json`
- `dist/codex/plugins/write-bash-scripts/skills/write-bash-scripts/SKILL.md`
- `dist/codex/plugins/write-bash-scripts/skills/write-bash-scripts/references/BASH.md`
- `plugins/write-bash-scripts/.claude-plugin/plugin.json`
- `plugins/write-bash-scripts/skills/write-bash-scripts/SKILL.md`
- `plugins/write-bash-scripts/skills/write-bash-scripts/references/BASH.md`

## Notable Changes

- The patch fixes a portability defect in the published Bash authoring guidance. Empty `"${@}"`, `"${*}"`, and `"${array[@]}"` expansions are now handled accurately for Bash 3.2 under `set -u`.
- The plugin patch release is internally consistent. `bin/compute-catalog-state` reports the committed catalog state.
- Generated Codex content is current. The OpenCode build has no corresponding skill mirror, and `bin/validate-plugins` confirms all generated trees are fresh.
- The branch does not add executable regression coverage for Bash 3.2. The commits document direct cross-version execution of changed snippets, while issue #433 tracks broader repository coverage under `/bin/bash`.

## Plan Compliance

Verdict: good compliance. The branch completes the plan's implementation, release, verification, and follow-up tracking work without an approach deviation.

Overall progress: 25/25 items done (100%).

### Commit 1: Bash 3.2 guidance and release metadata

- Done: Main and dual-purpose examples use `"$@"`; the variable-expansion guidance explains why it is the documented exception to the braces rule.
- Done: Variadic and alias examples use the portable argument-list form, and the variadic declaration explicitly retains array type information.
- Done: Empty-array expansion is guarded with both the parameter-expansion and length-check approaches.
- Done: The process-substitution section provides a portable `while IFS= read -r` collection loop and limits `readarray` to Bash 4 and later.
- Done: The new Bash 3.2 section covers all planned unsupported features and replacements, including `|&` and `&>>`, plus the requested `BASH_VERSINFO` guard.
- Done: The skill summary reflects the corrected invocation, exception, array guard, and pointer to the reference section.
- Done: Version `2.0.4`, catalog state, and the generated mirror match the plan and validation output.

### Commit 2: Strict-mode examples

- Done: The debug-tracing example defaults an unset `TRACE` safely.
- Done: Arithmetic guidance explains the `set -e` post-increment failure and preserves the valid `for ((...))` header use.
- Done: The subprocess example uses `((count += 1))`, preventing the loop body from returning a failure status on its first iteration.
- Done: The Codex mirror includes these adjustments, and the full plugin validation confirms generated-tree freshness.

### Commit 3 and follow-up

- Done: The dated plan is committed at the planned path.
- Done: The required follow-up exists as open issue [#433](https://github.com/cboone/agent-harness-plugins/issues/433), linked to the scope identified by the plan.

### Verification

- Done: The commit messages record cross-version strict-mode execution of the changed examples and reproduction of the previous failures.
- Done: `bin/check-cross-references` succeeds for both changed skill files.
- Done: `make test-all` completes successfully, including Markdown linting and formatting checks, ShellCheck, `shfmt`, `actionlint`, JSON and plugin validation, and 402 passing `scrut` cases.
- Done: The review independently confirmed the catalog-state result, generated-tree validation, and cross-reference validation.

### Deviations and fidelity concerns

No implementation deviations were found. The planned direct Bash 3.2 example checks are recorded in commit messages rather than committed as automated tests. That is consistent with the plan's scratchpad approach, but it leaves future regression detection to the separate follow-up in issue #433.

## Code Quality Assessment

Overall quality: ready to merge. The change is focused, accurately scoped to Bash version behavior, and passes the complete repository suite.

### Strengths

- The explanation distinguishes portable syntax from ordinary variable expansion without weakening the general braces rule.
- The guide offers concrete, version-appropriate alternatives instead of only listing unsupported Bash features.
- The strict-mode corrections address real exit-status behavior and explain the underlying condition, which makes the guidance maintainable.
- Source metadata, catalog state, and generated content are synchronized and validated.

### Issues to Address

No blocking issues found.

### Suggestions

- The arithmetic table has two rows with the same preferred `((i += 1))` expression. Combining them into one row would reduce repetition, but it does not affect correctness.
- Consider converting the documented cross-version snippet checks into automated coverage when the Bash 3.2 follow-up in issue #433 is addressed.

## Verification Performed

- `make test-all`
- `make test-scrut` (402 succeeded, 0 failed, 0 skipped)
- `bin/check-cross-references plugins/write-bash-scripts/skills/write-bash-scripts/SKILL.md plugins/write-bash-scripts/skills/write-bash-scripts/references/BASH.md`
- `bin/compute-catalog-state` (`catalog-M70-m103-p157-n57`)
- `git diff --check 340f319211b8ebfd64b0d37abda7768886bbf165..HEAD`
