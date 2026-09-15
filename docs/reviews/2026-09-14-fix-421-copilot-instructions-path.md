# Branch Review: fix/421-copilot-instructions-path

Base: `main` (merge base: `f9aa167`)
Commits: 13
Files changed: 25 (2 added, 23 modified, 0 deleted, 0 renamed)
Reviewed through: `71d9ec89`
Updated: 2026-09-15 (previous: 2026-09-14)

## Summary

This branch corrects repository guidance for GitHub Copilot path-specific instruction files. It standardizes their location under `.github/instructions/`, updates audits and references to cover nested files, and corrects the supported `excludeAgent` values. It also versions the affected plugins, regenerates catalog mirrors, updates the completed plan and this review, and records the documented `excludeAgent` values in repository Copilot instructions.

## Changes by Area

### Copilot instruction guidance

`clean-up-agent-config` removes recommendations for flat instruction-file paths, identifies misplaced files as unread, repairs link guidance, and validates files recursively under `.github/instructions/`. `resolve-copilot-pr-feedback` checks instruction location, `applyTo`, and code-review applicability, and names the valid `excludeAgent` values. `write-lean-code` now points to the supported nested path. Repository Copilot instructions record that GitHub documents `"code-review"` and `"cloud-agent"` as the supported values.

Files involved:

- `.github/copilot-instructions.md`
- `plugins/clean-up-agent-config/skills/clean-up-agent-config/SKILL.md`
- `plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-config-files.md`
- `plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-instruction-files.md`
- `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`
- `plugins/write-lean-code/skills/write-lean-code/references/comprehensive/build-infrastructure.md`

### Recursive scaffolding checks

`refresh-project-scaffolding` now audits nested `.github/instructions/**/*.instructions.md` files and their `applyTo` frontmatter, so refresh checks match GitHub's supported directory structure.

Files involved:

- `plugins/refresh-project-scaffolding/skills/refresh-project-scaffolding/SKILL.md`

### Versions and generated files

The branch publishes `clean-up-agent-config` 1.3.0, `resolve-copilot-pr-feedback` 1.5.4, `refresh-project-scaffolding` 2.1.1, and `write-lean-code` 1.0.4. Marketplace entries and generated Codex mirrors reflect those sources. The catalog state is `catalog-M70-m106-p159-n57`.

### Plan and review records

The completed plan is kept under `docs/plans/done/`. This review now includes the full branch inventory and reassessment through `71d9ec89`.

## File Inventory

### New files

- `docs/plans/done/2026-09-14-fix-copilot-path-specific-instructions.md`
- `docs/reviews/2026-09-14-fix-421-copilot-instructions-path.md`

### Modified files

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `.github/copilot-instructions.md`
- `dist/codex/plugins/clean-up-agent-config/.claude-plugin/plugin.json`
- `dist/codex/plugins/clean-up-agent-config/skills/clean-up-agent-config/SKILL.md`
- `dist/codex/plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-config-files.md`
- `dist/codex/plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-instruction-files.md`
- `dist/codex/plugins/refresh-project-scaffolding/.claude-plugin/plugin.json`
- `dist/codex/plugins/refresh-project-scaffolding/skills/refresh-project-scaffolding/SKILL.md`
- `dist/codex/plugins/resolve-copilot-pr-feedback/.claude-plugin/plugin.json`
- `dist/codex/plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`
- `dist/codex/plugins/write-lean-code/.claude-plugin/plugin.json`
- `dist/codex/plugins/write-lean-code/skills/write-lean-code/references/comprehensive/build-infrastructure.md`
- `plugins/clean-up-agent-config/.claude-plugin/plugin.json`
- `plugins/clean-up-agent-config/skills/clean-up-agent-config/SKILL.md`
- `plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-config-files.md`
- `plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-instruction-files.md`
- `plugins/refresh-project-scaffolding/.claude-plugin/plugin.json`
- `plugins/refresh-project-scaffolding/skills/refresh-project-scaffolding/SKILL.md`
- `plugins/resolve-copilot-pr-feedback/.claude-plugin/plugin.json`
- `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`
- `plugins/write-lean-code/.claude-plugin/plugin.json`
- `plugins/write-lean-code/skills/write-lean-code/references/comprehensive/build-infrastructure.md`

### Deleted files

None.

### Renamed files

None.

## Notable Changes

- The recursive audits now use the same nested instruction-file layout supported by GitHub.
- `excludeAgent` guidance follows [GitHub's repository instructions documentation](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions-in-your-ide/add-repository-instructions-in-your-ide), which shows a scalar `"code-review"` or `"cloud-agent"` value.
- The Codex mirrors and marketplace catalog state were regenerated from canonical sources.
- CI completed successfully for both `Lint and validate` and `Scrut tests / Scrut` on `62804c1f`.

## Plan Compliance

### Verdict

The planned guidance corrections are implemented, and the approved follow-up scope covers the same nested-file invariant in `refresh-project-scaffolding`. The plan's out-of-scope note said historical review documents would remain unchanged; the saved review was updated after Copilot identified that its inventory and version facts had become stale. The plan's initial version expectation for `resolve-copilot-pr-feedback` was also superseded by later fixes and is reflected as 1.5.4 in the final catalog.

### Overall Progress

4/4 planned items complete. The additional recursive scaffold audit, later version bumps, and updated review are complete as well.

### Completed Work

1. **`resolve-copilot-pr-feedback`:** Documents the supported instruction location, recursive file coverage, frontmatter and review-applicability checks, and GitHub-sourced length guidance. Its final version is 1.5.4.
1. **`clean-up-agent-config`:** Removes the invalid flat layout, marks misplaced files unread, updates examples and links, and checks nested files. Its final version is 1.3.0.
1. **`write-lean-code`:** Uses `.github/instructions/lean.instructions.md` and publishes version 1.0.4.
1. **Plan:** The completed plan is retained under `docs/plans/done/`.
1. **Approved follow-up:** `refresh-project-scaffolding` checks nested instruction files recursively and publishes version 2.1.1.
1. **Review and repository guidance:** This review reflects the complete inventory; repository Copilot instructions record GitHub's documented `excludeAgent` values.

## Code Quality Assessment

### Overall Quality

The changes are internally consistent across source skills, references, manifests, catalog entries, and generated mirrors. Recursive checks now align with the supported instruction-file location. Version metadata matches the catalog state.

### Prior findings addressed

- Nested instruction files are included in configuration and scaffolding audits and in resolver success criteria.
- The saved review now records the complete branch file inventory, plugin versions, and observed CI result.
- The PR description now names `resolve-copilot-pr-feedback` 1.5.4.
- Repository Copilot instructions clarify that GitHub documents a scalar `"cloud-agent"` value, not `"coding-agent"` or a list form, to exclude the cloud agent.

### Remaining concerns

None identified in the reviewed branch diff. GitHub's current documentation supports scalar `excludeAgent` values `"code-review"` and `"cloud-agent"`; the suggestion to replace `"cloud-agent"` with `"coding-agent"` conflicts with that documentation.

## Verification Evidence

- `make format`: passed.
- `make build`: passed and regenerated both mirrors.
- `make lint validate`: passed Markdown, formatting, shell, actionlint, JSON, plugin, catalog, cross-reference, and mirror checks.
- `bin/compute-catalog-state`: returned `catalog-M70-m106-p159-n57`, matching marketplace metadata.
- `make format`, `make lint validate`, and `git diff --check`: passed after the Copilot-instruction and review-document updates.
- CI on `62804c1f`: `Lint and validate` and `Scrut tests / Scrut` both passed.

## Changes Since Last Review

- Merged the updated `main` branch and synchronized the catalog state.
- Added recursive nested-file handling to `clean-up-agent-config`, `resolve-copilot-pr-feedback`, and `refresh-project-scaffolding`.
- Bumped `resolve-copilot-pr-feedback` to 1.5.4 and `refresh-project-scaffolding` to 2.1.1, then regenerated their mirrors.
- Updated repository Copilot instructions to reinforce GitHub's documented `excludeAgent` values.
- Updated this review's counts and inventory, and corrected the PR description's resolver version.
