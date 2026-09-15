# Branch Review: fix/413-prompt-footer

- Base: `main` (merge base: `340f3192`)
- Commits: 4
- Files changed: 31 (2 added, 29 modified, 0 deleted, 0 renamed)
- Reviewed through: `827c9ab4`
- Review date: 2026-09-15
- Working tree was clean when the review began.

## Summary

This branch addresses [issue #413](https://github.com/cboone/agent-harness-plugins/issues/413) by generating branch names in the invoking skill before composing the destination prompt. Both worktree launchers accept an explicit generated candidate and no longer start a separate naming process with issue content and the chain-command footer. Issue branch reuse, normalization, explicit names, and destination-agent launch behavior remain covered.

## Changes by Area

### Branch selection and launch

Both bundled `scripts/launch-workmux` files replace `--auto-name` with `--generated-name <candidate>`. They reject missing, empty, repeated, conflicting, and invalid candidates; validate issue numbers; retain branch reuse and issue-number insertion; and give migration guidance for obsolete calls. The naming subprocess, dry-run output parser, and naming capture files are removed.

Files: the launchers under `plugins/create-worktree/` and `plugins/address-issue-in-worktree/`, plus their Codex copies.

### Skill instructions and documentation

Both worktree skills now generate semantic candidates from task data, with imperative descriptions, default type prefixes, and repository naming overrides. Their READMEs remove the separate naming-command dependency and naming-specific workmux version requirement. The `pr` and `use-git` text attributes branch prefixes to repository conventions and explicit names.

Files: both worktree `SKILL.md` files and READMEs, `plugins/pr/skills/pr/SKILL.md`, `plugins/use-git/skills/use-git/references/common-operations.md`, and corresponding Codex copies.

### Regression coverage

Naming snapshots now supply candidates directly. New cases cover argument rejection and a composed issue containing separators, template delimiters, shell-like text, and a chain footer. The workmux stub rejects naming calls and repeated launch calls; the Makefile removes unused naming-stub environment variables.

Files: `tests/scrut/launch-workmux.md`, `tests/data/worktree-naming-issue.json`, `tests/fixtures/workmux-stub`, and `Makefile`.

### Packaging and delivery records

The four affected plugin versions and both catalog files are synchronized. Generated Codex content is updated; OpenCode symlinks resolve to the changed sources without requiring changed symlink entries. The committed plan records implementation and validation evidence.

Files: four source manifests, their Codex copies, both marketplace files, and `docs/plans/done/2026-09-15-inline-worktree-branch-naming.md`.

## File Inventory

### New files (2)

- `docs/plans/done/2026-09-15-inline-worktree-branch-naming.md`
- `tests/data/worktree-naming-issue.json`

### Modified files (29)

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `Makefile`
- `dist/codex/plugins/address-issue-in-worktree/.claude-plugin/plugin.json`
- `dist/codex/plugins/address-issue-in-worktree/README.md`
- `dist/codex/plugins/address-issue-in-worktree/scripts/launch-workmux`
- `dist/codex/plugins/address-issue-in-worktree/skills/address-issue-in-worktree/SKILL.md`
- `dist/codex/plugins/create-worktree/.claude-plugin/plugin.json`
- `dist/codex/plugins/create-worktree/README.md`
- `dist/codex/plugins/create-worktree/scripts/launch-workmux`
- `dist/codex/plugins/create-worktree/skills/create-worktree/SKILL.md`
- `dist/codex/plugins/pr/.claude-plugin/plugin.json`
- `dist/codex/plugins/pr/skills/pr/SKILL.md`
- `dist/codex/plugins/use-git/.claude-plugin/plugin.json`
- `dist/codex/plugins/use-git/skills/use-git/references/common-operations.md`
- `plugins/address-issue-in-worktree/.claude-plugin/plugin.json`
- `plugins/address-issue-in-worktree/README.md`
- `plugins/address-issue-in-worktree/scripts/launch-workmux`
- `plugins/address-issue-in-worktree/skills/address-issue-in-worktree/SKILL.md`
- `plugins/create-worktree/.claude-plugin/plugin.json`
- `plugins/create-worktree/README.md`
- `plugins/create-worktree/scripts/launch-workmux`
- `plugins/create-worktree/skills/create-worktree/SKILL.md`
- `plugins/pr/.claude-plugin/plugin.json`
- `plugins/pr/skills/pr/SKILL.md`
- `plugins/use-git/.claude-plugin/plugin.json`
- `plugins/use-git/skills/use-git/references/common-operations.md`
- `tests/fixtures/workmux-stub`
- `tests/scrut/launch-workmux.md`

There are no deleted or renamed files. The saved review itself is outside the reviewed commit range.

## Notable Changes

- The bundled launcher interface changes: callers using `--auto-name` must generate a candidate and pass `--generated-name`. Both shipped skills migrate together, and obsolete calls receive explicit guidance.
- Removing the naming subprocess removes the route by which the composed footer reached a separate tool-capable naming agent. The invoking skill explicitly treats issue text as data while naming.
- The configured destination agent still starts through workmux. Naming behavior no longer comes from workmux's naming configuration.
- Versions: `create-worktree` 1.6.0, `address-issue-in-worktree` 2.3.0, `use-git` 1.2.4, and `pr` 1.8.5. Catalog state: `catalog-M70-m105-p158-n57`.
- No dependency lockfile, workflow, or workmux configuration changes.

## Plan Compliance

Plan: [Inline worktree branch naming](../plans/done/2026-09-15-inline-worktree-branch-naming.md). It identifies issue #413 explicitly and was introduced by this branch.

**Verdict: good compliance, 10/10 items done (100%).** The approved design and all implementation, verification, and delivery items are satisfied by the branch and the completed review checks.

The count below uses the five implementation bullets, four verification bullets, and one delivery/boundaries item.

### Implementation

1. **Done: replace the naming interface.** Both launchers implement supplied candidates, optional issue/base arguments, positional exact names, conflict validation, and migration errors.
2. **Done: preserve branch selection semantics.** Existing normalization and reuse logic remains, including ambiguity errors, meaningful numbers, case, nested paths, and selected-branch reporting.
3. **Done: remove the naming subprocess.** The generator, dry-run parser, and naming capture files are removed. Prompt escaping, detached launch, and existing-pane delivery are retained. The bundled launchers are byte-identical.
4. **Done: update both skills and related documentation.** Naming rules and examples match across the two skills. Requirements and prefix attribution are updated in the planned documentation surfaces.
5. **Done: version and regenerate packaging.** Versions match the approved targets. Plugin validation confirms catalog consistency and generated-tree freshness.

### Verification

1. **Done: convert naming snapshots.** Candidate-based tests retain normalization, branch reuse, ambiguous matches, and repository tooling parity coverage.
2. **Done: argument and cleanup coverage.** Tests cover missing/empty/whitespace/repeated candidates, obsolete calls, invalid issues, mixed modes, invalid Git names, and empty prompt cleanup. The stub rejects naming and duplicate launch invocations.
3. **Done: literal prompt regression.** Both launchers are exercised with the fixture containing separators, template delimiters, shell-like content, and the appended footer. Tests inspect the escaped workmux input and check that the shell-like text did not execute.
4. **Done: semantic examples and project checks.** Examples cover semantic naming, maintenance/documentation prefixes, meaningful numbers, bare slugs, and repository-specific prefixes. Lint, format, cross-reference validation, catalog validation, mirror freshness, and whitespace checks pass. The full review run completed with all 408 Scrut cases passing.

### Delivery and boundaries

1. **Done.** Four focused conventional commits reference #413, and all four commit objects contain PGP signatures. Signature presence was checked directly; cryptographic trust was not assessed. Workmux configuration and timeout/signal-cleanup behavior remain outside the changes.

### Deviations and fidelity

The implementation follows the approved design. The issue originally listed several possible remedies, but the committed plan selects inline semantic naming, which the code implements. Updates to `pr` and `use-git` are planned consistency changes.

The plan records intermittent detached-output failures under [issue #439](https://github.com/cboone/agent-harness-plugins/issues/439), which remains open. Keeping that behavior outside this naming fix is consistent with the scope boundary. The review's full suite passed, so the recorded earlier failures do not leave this review without a successful full run. One passing run does not establish that the intermittent issue is resolved.

The prompt regression verifies the launcher's output boundary through a stub. It does not execute real MiniJinja rendering or observe a real destination agent, and deterministic snapshots cannot prove an invoking model will always follow naming instructions. These are validation limits, not evidence of a new defect.

## Code Quality Assessment

### Verdict

**Ready to merge.** No new actionable correctness, security, or maintainability defect was found. The change implements the approved design, and the full validation command completed successfully. The existing intermittent detached-output problem remains tracked separately.

### Strengths

- Removes the problematic execution path instead of parsing or stripping user-controlled prompt delimiters.
- Validates generated candidates before allocating the prompt file, including on issue-reuse calls.
- Preserves established normalization and explicit-branch handling, with focused regression cases for boundary conditions.
- Keeps both bundled launcher copies identical and generated distributions consistent.
- States naming responsibilities clearly and preserves repository overrides.
- Adds no dependencies and leaves unrelated launch mechanics unchanged.

### Issues to address

No new actionable defect was found in the reviewed changes.

The existing fixed-wait log collection at `plugins/create-worktree/scripts/launch-workmux:509` remains subject to the intermittent output omission documented in issue #439. That code is unchanged by this branch, and the issue did not reproduce in this review's full run. Keep the follow-up open; this is not a new branch finding.

### Suggestions

An integration check with real workmux could supplement the stub assertions by confirming the rendered destination prompt matches the original composed text. It would strengthen evidence for template rendering and delivery without changing the naming design.

## Validation

- Passed: Markdown lint, Prettier, ShellCheck, shfmt, actionlint, JSON validation, plugin validation including cross-references and mirror freshness.
- Passed: `git diff --check 340f319..HEAD`.
- Passed: direct comparison of both bundled launchers.
- Confirmed: all four branch commits contain PGP signature blocks.
- Passed: full Scrut suite, **408 succeeded, 0 failed, 0 skipped**, across 8 documents. The encompassing `make test-all` process exited 0.
- Validation command: `DEVELOPER_DIR=/Library/Developer/CommandLineTools make test-all`.
- The developer-directory override uses the installed Command Line Tools Git for the fixture's `/usr/bin/git` invocation.
- Suite output is retained locally at `/tmp/413-review-checks.log`.

## Follow-up

To process this review, run:

```text
/address-review docs/reviews/2026-09-15-fix-413-prompt-footer.md
```
