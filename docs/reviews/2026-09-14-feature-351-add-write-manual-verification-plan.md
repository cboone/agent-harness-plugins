# Branch Review: feature/351-add-write-manual-verification-plan

Base: `main` (merge base: `340f3192`)
Commits: 4
Files changed: 19 (16 added, 3 modified, 0 deleted, 0 renamed)
Reviewed through: `86b71222`

## Summary

This branch adds the `write-manual-verification-plan` writing skill, which produces persistent, numbered by-hand verification checklists with explicit success observations and controls that distinguish an intended absence from a broken instrument. It supplies four focused reference documents, catalog and README registration, and generated Codex and OpenCode mirrors. The active plan is retained in `docs/plans/todo/`, which is appropriate for this repository's plan convention.

## Changes by Area

### Skill and Reference Material

The new skill establishes a complete workflow: it first finds an existing record, separates checks that require a real environment from automated-test candidates, confirms the installed build, scopes exclusive resources, persists the checklist, and records results as readings. Its references provide the fixed checklist schema, null-versus-broken controls, resumption rules, and worked examples across host, simulator, browser, device, and printer environments.

Files involved:

- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/SKILL.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/examples.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/null-vs-broken.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/resuming.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/step-format.md`

### Plugin Documentation and Catalog

The branch adds a complete plugin manifest and README, registers version `1.0.0` in the Writing catalog, recalculates the catalog state to `catalog-M71-m103-p156-n58`, and adds the root README row plus its conditional `gh` requirement. The canonical description is consistent across the manifest, marketplace, plugin README, and root README.

Files involved:

- `plugins/write-manual-verification-plan/.claude-plugin/plugin.json`
- `plugins/write-manual-verification-plan/README.md`
- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `README.md`

### Generated Mirrors

The Codex copy contains the plugin manifest, README, skill, and all four reference files. The OpenCode mirror adds the expected symlink to the canonical skill directory.

Files involved:

- `dist/codex/plugins/write-manual-verification-plan/`
- `dist/opencode/skills/write-manual-verification-plan`

### Planning Record

The implementation plan defines the artifact shape, references, catalog integration, verification expectations, and commit boundaries. Its final branch update adds the `retired` status and documents the conditional `gh` catalog bullet, keeping the plan aligned with the shipped design.

Files involved:

- `docs/plans/todo/2026-09-14-new-skill-write-manual-verification-plan.md`

## File Inventory

### New Files

- `dist/codex/plugins/write-manual-verification-plan/.claude-plugin/plugin.json`
- `dist/codex/plugins/write-manual-verification-plan/README.md`
- `dist/codex/plugins/write-manual-verification-plan/skills/write-manual-verification-plan/SKILL.md`
- `dist/codex/plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/examples.md`
- `dist/codex/plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/null-vs-broken.md`
- `dist/codex/plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/resuming.md`
- `dist/codex/plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/step-format.md`
- `dist/opencode/skills/write-manual-verification-plan`
- `docs/plans/todo/2026-09-14-new-skill-write-manual-verification-plan.md`
- `plugins/write-manual-verification-plan/.claude-plugin/plugin.json`
- `plugins/write-manual-verification-plan/README.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/SKILL.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/examples.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/null-vs-broken.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/resuming.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/step-format.md`

### Modified Files

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `README.md`

## Notable Changes

- The new `retired` status gives a precise terminal state for a verification step that cannot establish the intended claim, rather than conflating it with a deferred or unavailable check.
- The workflow requires step 0, confirmation of the build under test, at the beginning of every session. This directly protects against results from an installed artifact produced by another worktree.
- The skill uses `### Exclusive resources` intentionally, so the resource-claim and issue-suggestion skills can consume the checklist's declared scope.
- No runtime dependency or executable script is added. The conditional `gh` requirement applies only when the checklist record is stored in an issue comment.

## Plan Compliance

**Verdict: good compliance.** The branch implements the plan's artifact, document structure, catalog registration, generated mirrors, and verification requirements. The only implementation addition beyond the earlier plan text, the `retired` status, was explicitly recorded in the plan before review and is a well-justified refinement of its status model.

**Overall progress: 13/13 items done (100%).**

### Plugin Structure and Activation

- **Done:** The manifest provides the specified `1.0.0` version, skill location, MIT license, metadata, and keywords.
- **Done:** The skill frontmatter uses the requested folded description form and covers each of the six planned activation situations.
- **Done:** The body supplies the planned sections: When to Use, Core Principles, The Step, Workflow, reference navigation, related skills, and sources.

### Checklist Model and References

- **Done:** The skill defines Setup, Action, Expected, and Null vs broken, plus `Why by hand` and `Result`, stable numbering, a status vocabulary, and mandatory build confirmation.
- **Done:** `step-format.md` supplies the planned document template, status table, numbering rules, step-part guidance, build-confirmation detail, and status meanings.
- **Done:** `null-vs-broken.md` documents same-run liveness, positive controls, conditions that permit failure, discriminating measurements, controlled cycles, and other controls called for by the plan.
- **Done:** `resuming.md` specifies a single living record, reprinting from that record, free-text result handling, steps that remain unsettled, build changes, deferral, resource-based sessions, and closeout.
- **Done:** `examples.md` includes the planned rewritten failures, complete fosforo checklist, springer examples, and clearly labelled illustrative examples for the four other environments.

### Documentation, Registration, and Mirrors

- **Done:** The plugin README uses the catalog description verbatim as its opening paragraph, contains the intended sections and valid related-plugin links, and explains when `gh` is required.
- **Done:** The marketplace object appears in alphabetical order with matching version and description; `bin/compute-catalog-state` returns the committed `catalog-M71-m103-p156-n58` value.
- **Done:** The root README table row and conditional external-tool bullet match the catalog and README language.
- **Done:** The Codex and OpenCode mirrors are committed and were accepted as current by plugin validation.

### Verification and Plan Maintenance

- **Done:** `bin/check-cross-references plugins/write-manual-verification-plan/skills/write-manual-verification-plan/SKILL.md` reports that all cross-references resolve.
- **Done:** `make validate` passes JSON and all plugin validation rules. The lint portion of `make test-all` also passes with no Markdown, Prettier, shell, or workflow-lint findings.
- **Done:** The plan's final update records the added `retired` terminal status and corrects the root README requirement to include optional `gh` usage.

### Deviations

- **Additional commit:** The branch contains a fourth documentation commit after the plan's initial three-commit outline. It updates the plan to reflect the final `retired` status and conditional `gh` bullet. This is reasonable plan maintenance, not scope expansion.
- **Status vocabulary refinement:** `retired` is added to the planned vocabulary. The plan was updated before review with a specific rationale and matching reference material, so this is a justified design refinement.

### Fidelity Concerns

None. The implementation follows the plan's stated approach, including four flat reference files, no bundled scripts, persistence in a plan or issue record, and machine-readable exclusive-resource scope.

## Code Quality Assessment

**Overall quality: implementation ready, but the branch cannot yet pass the full test suite.** This is a prose-first skill plugin, and its behavior is clear, internally consistent, and guarded by the repository's catalog, generated-tree, and cross-reference validation. No implementation defect was found in the branch diff. However, `make test-scrut` currently fails in an unrelated launcher test area, tracked in [#435](https://github.com/cboone/agent-harness-plugins/issues/435).

### Strengths

- The core workflow is unusually concrete for a writing skill: it defines the persisted artifact, status transitions, result format, and closing conditions rather than offering only general guidance.
- The examples consistently distinguish expected observations from weak, non-discriminating checks. This makes the central null-versus-broken principle actionable across multiple environments.
- The README, manifest, marketplace entry, and generated mirrors agree on the name, version, description, metadata, and installation surface.
- The plan anticipates validation-specific hazards, and the delivered skill passes the cross-reference and generated-tree checks that protect those hazards.

### Issues to Address

- `make test-scrut` completes with 10 failures in `tests/scrut/launch-workmux.md`: 392 of 402 cases pass, but generated branch names are rejected by the launcher. The branch does not change the affected snapshots or launcher scripts, so this is not caused by the plugin change. The failure is tracked in [#435](https://github.com/cboone/agent-harness-plugins/issues/435).

## Verification Performed

- `bin/check-cross-references plugins/write-manual-verification-plan/skills/write-manual-verification-plan/SKILL.md` passed.
- `bin/compute-catalog-state` returned `catalog-M71-m103-p156-n58`, matching the committed marketplace metadata.
- `make validate` passed.
- The lint portion of `make test-all` passed: Markdown lint, Prettier, ShellCheck, `shfmt`, and `actionlint` all reported no findings.
- `make test-scrut` completed with exit code 2: 392 of 402 cases passed and 10 cases in `tests/scrut/launch-workmux.md` failed. The failure is tracked in [#435](https://github.com/cboone/agent-harness-plugins/issues/435).
- `git diff --check 340f3192..HEAD` reported no whitespace errors.
