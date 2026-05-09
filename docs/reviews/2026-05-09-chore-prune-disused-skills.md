# Branch Review: chore/prune-disused-skills

Base: `origin/main` (merge base: `54746d4`)
Commits: 3
Files changed: 28 (1 added, 7 modified, 20 deleted, 0 renamed)
Reviewed through: `f7a9219`

## Summary

This branch removes the unused `update-docs-reminder` hook plugin and the unused `update-review` skill plugin from the canonical source tree, the Claude and Codex marketplaces, and the generated Codex and OpenCode mirrors. It also updates root README guidance and `create-plugin` reference examples so current user-facing documentation no longer advertises either removed plugin.

The implementation is mostly complete and follows the plan closely. The main issue is Markdown table formatting: `yarn lint:md` currently fails on a touched `create-plugin` reference table and its mirrored paths.

## Changes by Area

### Plugin Catalog And Mirrors

The Claude marketplace and Codex marketplace mirror both drop the `update-docs-reminder` and `update-review` entries, and `metadata.version` changes from `catalog-M61-m108-p156-n53` to `catalog-M59-m106-p153-n51`. `bin/compute-catalog-state` returns the same new value.

Files involved:

- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `dist/codex/plugins/update-docs-reminder/`
- `dist/codex/plugins/update-review/`
- `dist/opencode/plugins/update-docs-reminder.ts`
- `dist/opencode/skills/update-review`

### Canonical Plugin Sources

Both removed plugins are deleted from `plugins/`, including manifests, README files, hook or skill payloads, and helper scripts. This matches the planned pruning scope and avoids leaving orphan source directories behind.

Files involved:

- `plugins/update-docs-reminder/`
- `plugins/update-review/`

### Documentation And Guidance

The root README no longer lists `Update Review` in Code Review, no longer lists `Update Docs Reminder` under Hooks, and no longer documents the hook-specific `jq` dependency. Codex CLI hook guidance now names only `notify`.

The `create-plugin` reference examples now use only `notify` as the workflow hook example, with matching generated Codex mirror updates.

Files involved:

- `README.md`
- `plugins/create-plugin/skills/create-plugin/references/marketplace-json.md`
- `plugins/create-plugin/skills/create-plugin/references/readme-updates.md`
- `dist/codex/plugins/create-plugin/skills/create-plugin/references/marketplace-json.md`
- `dist/codex/plugins/create-plugin/skills/create-plugin/references/readme-updates.md`

### Planning

A scoped plan was added for pruning exactly these two plugins, including explicit out-of-scope handling for archived plan history.

Files involved:

- `docs/plans/done/2026-05-09-prune-update-docs-reminder-and-update-review.md`

## File Inventory

### New Files

- `docs/plans/done/2026-05-09-prune-update-docs-reminder-and-update-review.md`

### Modified Files

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `README.md`
- `dist/codex/plugins/create-plugin/skills/create-plugin/references/marketplace-json.md`
- `dist/codex/plugins/create-plugin/skills/create-plugin/references/readme-updates.md`
- `plugins/create-plugin/skills/create-plugin/references/marketplace-json.md`
- `plugins/create-plugin/skills/create-plugin/references/readme-updates.md`

### Deleted Files

- `dist/codex/plugins/update-docs-reminder/.claude-plugin/plugin.json`
- `dist/codex/plugins/update-docs-reminder/.codex-plugin/plugin.json`
- `dist/codex/plugins/update-docs-reminder/README.md`
- `dist/codex/plugins/update-docs-reminder/hooks/hooks.json`
- `dist/codex/plugins/update-docs-reminder/opencode/index.ts`
- `dist/codex/plugins/update-docs-reminder/scripts/check-docs`
- `dist/codex/plugins/update-review/.claude-plugin/plugin.json`
- `dist/codex/plugins/update-review/README.md`
- `dist/codex/plugins/update-review/skills/update-review/SKILL.md`
- `dist/opencode/plugins/update-docs-reminder.ts`
- `dist/opencode/skills/update-review`
- `plugins/update-docs-reminder/.claude-plugin/plugin.json`
- `plugins/update-docs-reminder/.codex-plugin/plugin.json`
- `plugins/update-docs-reminder/README.md`
- `plugins/update-docs-reminder/hooks/hooks.json`
- `plugins/update-docs-reminder/opencode/index.ts`
- `plugins/update-docs-reminder/scripts/check-docs`
- `plugins/update-review/.claude-plugin/plugin.json`
- `plugins/update-review/README.md`
- `plugins/update-review/skills/update-review/SKILL.md`

### Renamed Files

None.

## Notable Changes

- Marketplace plugin count drops from 53 to 51.
- The computed catalog state changes to `catalog-M59-m106-p153-n51`.
- The `update-docs-reminder` Bash script and its `jq` dependency are removed from the shipped plugin surface.
- `update-review` is removed while `review-branch` and `address-review` remain available.
- The branch intentionally preserves references under `docs/plans/done/` as historical records.

## Plan Compliance

Plan reviewed: `docs/plans/done/2026-05-09-prune-update-docs-reminder-and-update-review.md`

Compliance verdict: good compliance with one formatting issue outside the plan's explicit validation list. The functional pruning work is complete, the generated mirrors and catalog metadata are consistent, and the commits are split along the planned logical boundaries. The remaining issue is Markdown lint failure in a touched table.

Overall progress: 8/8 plan steps done (100%).

### Done Items

- **Delete canonical plugin sources:** Done. Both `plugins/update-docs-reminder/` and `plugins/update-review/` are removed recursively.
- **Remove catalog entries and recompute metadata:** Done. Both marketplace entries are gone, and `bin/compute-catalog-state` returns `catalog-M59-m106-p153-n51`, matching the stored metadata.
- **Regenerate the Codex mirror:** Done. The Codex marketplace drops both plugins, both Codex plugin directories are removed, and generated `create-plugin` reference copies match the source edit.
- **Regenerate the OpenCode mirror:** Done. `dist/opencode/plugins/update-docs-reminder.ts` and `dist/opencode/skills/update-review` are removed.
- **Update root README:** Done. The planned rows, external-tool bullet, and Codex hook prose were updated.
- **Update cross-references in `create-plugin`:** Done. Both source reference files now use only `notify` as the hook example, and the Codex mirror copies were updated.
- **Validate:** Done for the planned validation commands that are branch-relevant. `bin/validate-json` passes, `bin/validate-plugins` passes, `bin/version-audit` exits 0 while reporting existing upstream pin drift, `git diff --check` passes, and `git status --short --branch` was clean before this review document was created.
- **Commit:** Done. The branch has three conventional commits. Commit objects include `gpgsig` headers; `git log --show-signature` found signatures but could not open the local GPG trustdb from the sandbox.

### Deviations

- The plan's spot-check expectation says remaining references should be only in `docs/plans/done/` and the active Codex-native plugin plan. The new pruning plan itself also contains references in `docs/plans/todo/`. That is a reasonable self-reference, but the written spot-check should account for it if used mechanically.
- The implementation keeps `docs/plans/todo/2026-05-02-codex-cli-native-plugins.md` unchanged, as the plan explicitly said. That preserves the requested narrow scope, but it leaves an active todo plan with references to a plugin that no longer exists.

### Fidelity Concerns

- The core implementation matches the plan's intent: remove two unused plugins without broadening the cleanup to other low-traffic skills or archived history.
- The completed pruning plan remains under `docs/plans/todo/`. Repository history shows completed plans are commonly moved to `docs/plans/done/`; leaving this implemented plan under `todo` may confuse future plan discovery.

## Code Quality Assessment

Overall quality: not ready to merge until the Markdown lint issue is fixed. The functional deletion and marketplace consistency are good, but the branch currently fails a project lint command on files changed by the branch.

### Strengths

- The deletion is complete across canonical plugin sources, generated Codex output, generated OpenCode symlinks, and marketplace metadata.
- Catalog metadata is recomputed correctly rather than hand-guessed.
- The README updates are targeted and avoid rewriting unrelated sections.
- Archived historical plans are preserved, which matches the repository convention.
- Commit boundaries are clean and logical.

### Issues To Address

1. **Blocking: `yarn lint:md` fails on the touched `create-plugin` hook table.**

   The examples column was shortened from `notify, update-docs-reminder` to `notify`, but the table remains padded to the old width. The custom MD060A table-alignment rule reports errors for the source file, the generated Codex copy, and the OpenCode symlinked view:

   - `plugins/create-plugin/skills/create-plugin/references/readme-updates.md:65`
   - `plugins/create-plugin/skills/create-plugin/references/readme-updates.md:66`
   - `plugins/create-plugin/skills/create-plugin/references/readme-updates.md:67`
   - `dist/codex/plugins/create-plugin/skills/create-plugin/references/readme-updates.md:65`
   - `dist/codex/plugins/create-plugin/skills/create-plugin/references/readme-updates.md:66`
   - `dist/codex/plugins/create-plugin/skills/create-plugin/references/readme-updates.md:67`
   - `dist/opencode/skills/create-plugin/references/readme-updates.md:65`
   - `dist/opencode/skills/create-plugin/references/readme-updates.md:66`
   - `dist/opencode/skills/create-plugin/references/readme-updates.md:67`

   The OpenCode paths are symlinked through `dist/opencode/skills/create-plugin`, so fixing the source table and regenerating or updating the Codex mirror should clear the duplicated reports.

2. **Non-blocking documentation hygiene: the completed pruning plan is still in `docs/plans/todo/`.**

   The branch fully implements the plan. Existing repo history frequently moves completed plans to `docs/plans/done/`, so keeping this one under `todo` leaves a completed task in the active-plan directory.

3. **Non-blocking active-plan staleness: `docs/plans/todo/2026-05-02-codex-cli-native-plugins.md` still names `update-docs-reminder`.**

   This was explicitly out of scope in the pruning plan, so it is not a plan-compliance failure. It is still a future-reader risk because that plan remains under `todo` while describing a removed plugin as present and codex-compatible.

### Validation Run

Commands run during review:

```text
bin/validate-json
bin/validate-plugins
bin/version-audit
bin/compute-catalog-state
git diff --check 54746d4d877787a8705adbdaf91173b411935252..HEAD
yarn install --immutable
yarn lint:md
```

Results:

- `bin/validate-json`: passed.
- `bin/validate-plugins`: passed.
- `bin/version-audit`: exited 0 and reported upstream drift in unrelated tool pins (`knip`, `stylelint`, `golangci-lint`, `cargo-deny`, `typos-cli`, and `pkg`).
- `bin/compute-catalog-state`: returned `catalog-M59-m106-p153-n51`.
- `git diff --check`: passed.
- `yarn install --immutable`: completed with the existing peer-dependency warning for `markdownlint-rule-force-align-table-columns`.
- `yarn lint:md`: failed with 9 MD060A table-alignment errors listed above.
