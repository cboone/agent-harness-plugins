# Branch Review: feature/351-add-write-manual-verification-plan

Base: `main` (merge base: `340f3192`)
Commits: 7
Files changed: 20 (17 added, 3 modified, 0 deleted, 0 renamed)
Reviewed through: `03e0f89b`
Updated: 2026-09-15 (previous: 2026-09-14)

## Summary

This branch adds the `write-manual-verification-plan` writing skill, which produces persistent, numbered by-hand verification checklists with explicit success observations and controls that distinguish an intended absence from a broken instrument. It supplies four focused reference documents, catalog and README registration, and generated Codex and OpenCode mirrors. Result classification requires build and control evidence, automation candidates remain visible as deferred rows, and issue-based records are read back after writes. The completed plan is retained in `docs/plans/done/`.

## Changes by Area

### Skill and Reference Material

The new skill establishes a complete workflow: it first finds an existing record, separates checks that require a real environment from automated-test candidates, confirms the loaded build, scopes exclusive resources, persists the checklist, and records results as readings. Its references provide the fixed checklist schema, null-versus-broken controls, resumption rules, and worked examples across host, simulator, browser, device, and printer environments. Shared audio-thread markers require a safe non-blocking handoff. Unreported evidence leaves a result pending, and an invalid build or control makes it void. Examples label missing historical metadata as placeholders.

Files involved:

- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/SKILL.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/examples.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/null-vs-broken.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/resuming.md`
- `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/references/step-format.md`

### Plugin Documentation and Catalog

The branch adds a complete plugin manifest and README, registers version `1.0.0` in the Writing catalog, recalculates the catalog state to `catalog-M71-m103-p157-n58`, and adds the root README row plus its conditional `gh` requirement. The canonical description is consistent across the manifest, marketplace, plugin README, and root README. The plugin README includes optional permissions for issue-record commands and tmpfile management.

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

### Planning and Review Records

The implementation plan defines the artifact shape, references, catalog integration, verification expectations, and commit boundaries. Its inventory describes the shipped copy/symlink/copy control, loaded-build confirmation, evidence requirements, and optional permissions. The completed plan is archived under `docs/plans/done/`. This review is included in the branch's file inventory.

Files involved:

- `docs/plans/done/2026-09-14-new-skill-write-manual-verification-plan.md`
- `docs/reviews/2026-09-14-feature-351-add-write-manual-verification-plan.md`

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
- `docs/plans/done/2026-09-14-new-skill-write-manual-verification-plan.md`
- `docs/reviews/2026-09-14-feature-351-add-write-manual-verification-plan.md`
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
- Matching an installed file to a fresh build is paired with a host reload and loaded-path check, or an identity read from the running instance.
- The persisted record retains automation deferrals and verifies issue-comment contents before presenting a successful save.

## Plan Compliance

**Verdict: good compliance.** The branch implements the planned artifact, document structure, catalog registration, and generated mirrors. The plan records the `retired` status and the evidence and persistence corrections. Its reference inventory matches the delivered scope. Local Scrut verification has a separately tracked limitation, described below.

**Implementation progress: 14/14 items below complete.**

### Plugin Structure and Activation

- **Done:** The manifest provides the specified `1.0.0` version, skill location, MIT license, metadata, and keywords.
- **Done:** The skill frontmatter uses the requested folded description form and covers each of the six planned activation situations.
- **Done:** The body supplies the planned sections: When to Use, Core Principles, The Step, Workflow, reference navigation, related skills, and sources.

### Checklist Model and References

- **Done:** The skill defines Setup, Action, Expected, and Null vs broken, plus `Why by hand` and `Result`, stable numbering, a status vocabulary, and mandatory build confirmation.
- **Done:** `step-format.md` supplies the planned document template, consistent resource scope, status table, numbering rules, step-part guidance, loaded-build confirmation, and status meanings.
- **Done:** `null-vs-broken.md` documents same-run liveness, positive controls, conditions that permit failure, discriminating measurements, controlled cycles, and other controls called for by the plan.
- **Done:** `resuming.md` specifies a single living record, read-back verification and recovery, evidence-gated result handling, build changes, deferral, resource-based sessions, and closeout.
- **Done:** `examples.md` includes the planned rewritten failures, complete fosforo checklist, springer examples, and clearly labelled illustrative examples for the four other environments.

### Documentation, Registration, and Mirrors

- **Done:** The plugin README uses the catalog description verbatim as its opening paragraph, contains valid related-plugin links and optional command permissions, and explains when `gh` is required.
- **Done:** The marketplace object appears in alphabetical order with matching version and description; `bin/compute-catalog-state` returns the committed `catalog-M71-m103-p156-n58` value.
- **Done:** The root README table row and conditional external-tool bullet match the catalog and README language.
- **Done:** The Codex and OpenCode mirrors are committed and were accepted as current by plugin validation.

### Verification and Plan Maintenance

- **Done:** `bin/check-cross-references plugins/write-manual-verification-plan/skills/write-manual-verification-plan/SKILL.md` reports that all cross-references resolve.
- **Done:** `make validate` passes JSON and all plugin validation rules. `make lint` passes Markdown, Prettier, shell, and workflow checks.
- **Done:** The completed plan records the delivered status model, reference inventory, conditional `gh` usage, and optional permissions.

### Deviations

- **Additional commits:** The seven reviewed commits include the initial three-commit implementation, plan maintenance, a saved review with Scrut evidence, the evidence and persistence corrections, and completion of the plan record.
- **Status vocabulary refinement:** `retired` is added to the planned vocabulary. The plan was updated before review with a specific rationale and matching reference material, so this is a justified design refinement.

### Fidelity Concerns

None outstanding in the reviewed implementation. It follows the plan's stated approach, including four flat reference files, no bundled scripts, persistence in a plan or issue record, and machine-readable exclusive-resource scope. The inventory uses the shipped reversible scan-log control; it does not claim an unshipped NaN example.

## Code Quality Assessment

**Overall quality: the reviewed implementation corrections pass local lint and validation.** No blocking implementation finding remains in this reassessment. The changes are confined to the new skill, its mirrors, and branch documentation. CI completed successfully for `550ae026`, including Scrut; that is distinct from the earlier local Scrut failure recorded below. This assessment does not claim a fresh local Scrut pass or a CI result for the later commits.

### Strengths

- The core workflow is unusually concrete for a writing skill: it defines the persisted artifact, status transitions, result format, and closing conditions rather than offering only general guidance.
- The examples consistently distinguish expected observations from weak, non-discriminating checks. This makes the central null-versus-broken principle actionable across multiple environments.
- The README, manifest, marketplace entry, and generated mirrors agree on the name, version, description, metadata, and installation surface.
- The plan anticipates validation-specific hazards, and the delivered skill passes the cross-reference and generated-tree checks that protect those hazards.

### Issues to Address

- The earlier local `make test-scrut` run recorded 10 failures in `tests/scrut/launch-workmux.md`: 392 of 402 cases passed, but generated branch names were rejected by the launcher. The branch does not change those snapshots or scripts. [#435](https://github.com/cboone/agent-harness-plugins/issues/435) remains open as of this reassessment. The local suite was not rerun for these prose changes, so that local limitation is not reported as resolved.

## Verification Performed

- `bin/check-cross-references plugins/write-manual-verification-plan/skills/write-manual-verification-plan/SKILL.md` passed in the initial review; the refreshed `make validate` also passed rule 19 across the skill and its references.
- `bin/compute-catalog-state` returned `catalog-M71-m103-p156-n58`, matching the committed marketplace metadata.
- `make validate` passed.
- `make format`, `make build`, and `make lint` passed for the source corrections: Markdown lint, Prettier, ShellCheck, `shfmt`, and `actionlint` reported no findings. The completed plan passed targeted Markdown lint.
- The earlier local `make test-scrut` run completed with exit code 2: 392 of 402 cases passed and 10 launcher cases failed, as recorded in commit `550ae026` and tracked in [#435](https://github.com/cboone/agent-harness-plugins/issues/435).
- [CI run 35003754913](https://github.com/cboone/agent-harness-plugins/actions/runs/35003754913) completed both Lint and validate and Scrut tests successfully against `550ae026`, verified through the GitHub API on 2026-09-15.
- `git diff --check` reported no whitespace errors in the corrections.

## Changes Since Last Review

- `550ae026` saves the review and records the completed local Scrut failure instead of treating an invoked test as a pass.
- `717d1897` requires same-run evidence, safe marker synchronization, active-build confirmation, persistent deferrals, and verified issue-comment writes; it also completes commands, example metadata, resource scope, and permissions, with regenerated mirrors.
- `03e0f89b` aligns the plan's inventory with delivery and moves the completed plan to `docs/plans/done/`.
