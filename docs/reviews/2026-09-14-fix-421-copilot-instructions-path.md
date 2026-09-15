# Branch Review: fix/421-copilot-instructions-path

Base: `main` (merge base: `340f319`)
Commits: 5
Files changed: 17 (1 added, 16 modified, 0 deleted, 0 renamed)
Reviewed through: `a48764b6`

## Summary

This branch corrects published guidance for GitHub Copilot path-specific instruction files. It removes the invalid flat `.github/<scope>.instructions.md` layout from relevant skills and references, teaches the required `.github/instructions/` location and valid `excludeAgent` values, and rebuilds the Codex marketplace mirror. It also records the intended work in a committed plan and updates catalog versions consistently.

## Changes by Area

### Copilot instruction guidance

`clean-up-agent-config` now treats a path-specific instruction directly under `.github/` as unread, keeps the required nested location throughout its target layout, audit, examples, checks, and reference material, and describes the corrective move and link updates. `resolve-copilot-pr-feedback` adds a read-location, glob, and agent applicability check; corrects valid `excludeAgent` values; and grounds its length guidance in GitHub documentation.

Files involved:

- `plugins/clean-up-agent-config/skills/clean-up-agent-config/SKILL.md`
- `plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-config-files.md`
- `plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-instruction-files.md`
- `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`
- `plugins/write-lean-code/skills/write-lean-code/references/comprehensive/build-infrastructure.md`

### Plugin metadata and generated mirror

`clean-up-agent-config` receives a minor bump from `1.2.4` to `1.3.0` for its changed audit behavior, while `write-lean-code` receives a patch bump from `1.0.3` to `1.0.4`. Marketplace entries, the catalog-state tag, and the generated Codex mirror reflect the canonical sources.

Files involved:

- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `plugins/clean-up-agent-config/.claude-plugin/plugin.json`
- `plugins/write-lean-code/.claude-plugin/plugin.json`
- `dist/codex/plugins/clean-up-agent-config/`
- `dist/codex/plugins/resolve-copilot-pr-feedback/`
- `dist/codex/plugins/write-lean-code/`

### Planning

The branch adds a plan that defines the scope, explains the documentation facts behind the correction, distinguishes the retained baseline work, and specifies validation criteria.

Files involved:

- `docs/plans/todo/2026-09-14-fix-copilot-path-specific-instructions.md`

## File Inventory

### New files

- `docs/plans/todo/2026-09-14-fix-copilot-path-specific-instructions.md`

### Modified files

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `dist/codex/plugins/clean-up-agent-config/.claude-plugin/plugin.json`
- `dist/codex/plugins/clean-up-agent-config/skills/clean-up-agent-config/SKILL.md`
- `dist/codex/plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-config-files.md`
- `dist/codex/plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-instruction-files.md`
- `dist/codex/plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`
- `dist/codex/plugins/write-lean-code/.claude-plugin/plugin.json`
- `dist/codex/plugins/write-lean-code/skills/write-lean-code/references/comprehensive/build-infrastructure.md`
- `plugins/clean-up-agent-config/.claude-plugin/plugin.json`
- `plugins/clean-up-agent-config/skills/clean-up-agent-config/SKILL.md`
- `plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-config-files.md`
- `plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-instruction-files.md`
- `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`
- `plugins/write-lean-code/.claude-plugin/plugin.json`
- `plugins/write-lean-code/skills/write-lean-code/references/comprehensive/build-infrastructure.md`

### Deleted files

None.

### Renamed files

None.

## Notable Changes

- The catalog-state tag changes to `catalog-M70-m104-p153-n57`, matching the recomputed value.
- Generated Codex files track the canonical source changes, and plugin validation confirms the mirrors are current.
- The implementation intentionally retains an example of a flat instruction path only to explain that Copilot does not read it. The residual scan found no recommendation to use the invalid layout.

## Plan Compliance

### Verdict

Good compliance. All four planned change groups are implemented with the prescribed location, `applyTo`, and `excludeAgent` guidance, and the branch-wide generated metadata is synchronized. The only verification result not conclusively observed in this review environment is the terminal completion line for the full scrut suite.

### Overall Progress

4/4 items done (100%).

### Done Items

1. **`resolve-copilot-pr-feedback` correction:** Implemented the three-part readability check, documented the head-branch behavior, corrected `excludeAgent` values, attributed length guidance, updated the repo-wide path spelling, and updated success criteria. The retained `1.5.2` version matches the plan's explicit baseline decision.
1. **`clean-up-agent-config` correction:** Removed the flat layout, makes misplaced files an explicit unread condition in the audit, updates scoped examples and cross-references, corrects agent guidance, and updates both reference documents. The minor `1.3.0` bump appropriately reflects changed audit behavior.
1. **`write-lean-code` correction:** Updated the sole stale Copilot path and bumped the plugin from `1.0.3` to `1.0.4`.
1. **Plan:** Added the plan under `docs/plans/todo/` as required by the repository convention.

### Deviations

None. The branch follows the plan's intended approach. The residual scan reports the two canonical and mirrored explanatory mentions of `.github/lean.instructions.md`; these are documented exceptions, not actionable stale guidance.

### Fidelity Concerns

None in the implementation. Cross-reference validation, plugin validation, catalog-state computation, and version synchronization all support the stated design.

## Code Quality Assessment

### Overall Quality

Ready to merge. The documentation changes are internally consistent, scoped to the identified defect, and accompanied by the appropriate version and generated-mirror updates.

### Strengths

- The corrective rule is stated in both proactive configuration guidance and reactive review-feedback guidance, reducing the chance that a later workflow reintroduces the invalid layout.
- The audit now identifies the failure mode and describes a concrete remediation, including moving the file and repairing its references.
- The branch distinguishes an invalid path from an intentional example that explains why it is invalid, avoiding an overly broad residual scan rule.
- Version and marketplace consistency were directly verified: canonical plugin versions match their catalog entries, and the stored catalog state is `catalog-M70-m104-p153-n57`, which equals `bin/compute-catalog-state` output.

### Issues to Address

None.

### Suggestions

- Obtain a completed `make test-scrut` result before merging. The review environment reached the scrut invocation without a failure message, but did not return its completion status before the command boundary.

## Verification Evidence

- `bin/check-cross-references`: passed.
- `bin/compute-catalog-state`: matched `.claude-plugin/marketplace.json`.
- `bin/validate-plugins`: passed.
- `make lint`: passed, including Markdown linting and formatting, ShellCheck, `shfmt`, and `actionlint`.
- `make test-all`: completed lint and validation stages successfully and reached `scrut`; the full scrut completion status was not observed.
