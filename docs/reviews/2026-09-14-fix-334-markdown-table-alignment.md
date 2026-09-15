# Branch Review: fix/334-markdown-table-alignment

Base: `main` (merge base: `f9aa1673`)
Commits: 13
Files changed: 21 (2 added, 19 modified, 0 deleted, 0 renamed)
Reviewed through: `e1dbc738`
Updated: 2026-09-15 (previous: 2026-09-15)

The counts and assessment describe `f9aa1673..e1dbc738`. The commit that saves this updated review is outside that range.

## Summary

This branch gives Prettier responsibility for table alignment in files its command actually formats and retains manual alignment for other Markdown files. It updates `write-markdown`, the generic and Pandoc-academic presets in `set-up-linters`, and Prettier configuration detection in `lint-and-fix`. Validation follows the same per-file decision and runs Prettier before lint fixes when an enabled MD060 rule could reject an unpadded table.

The branch also corrects the repository's MD060 comment, advances the three changed plugins, synchronizes catalogs and generated mirrors, and retains the completed plan. It includes the current `main` changes through `f9aa1673`.

## Changes by Area

### Markdown guidance and validation

The skill and reference guide verify that Prettier is available, inspect the chosen command's paths, globs, working directory, and options, and honor its effective ignore files. The default ignore files are `.gitignore` and `.prettierignore`; an explicit `--ignore-path` selects the files used instead. Configuration can live in `package.json`, but configuration presence alone does not establish coverage. A format command restricted to JavaScript does not own Markdown alignment.

Where Prettier formats a file, authors write table rows without manual padding. If MD060 is enabled or its effective setting is unknown, a standalone Prettier pass runs before any lint-fix chain. Lint fixes follow, and Prettier runs last. If MD060 is disabled, the initial formatter pass is unnecessary.

Direct CLI fallbacks resolve installed tools through the project's package manager and preserve the working directory, configuration arguments, ignore options, and edited paths. For files Prettier does not format, including ignored files, manual alignment happens before every markdownlint fix command. The reference retains the full manual alignment procedure.

### Markdownlint presets and configuration detection

The generic configuration disables MD060 only when the selected or existing formatter command covers every Markdown file governed by that configuration. It keeps `{ "style": "aligned" }` when coverage is absent or mixed. The Pandoc-academic preset explicitly keeps `MD060: false` regardless of Prettier, preserving its allowance for dense academic tables.

`set-up-linters` generates Prettier configuration only when the tool was selected and the corresponding configuration is missing. Both `set-up-linters` and `lint-and-fix` recognize an existing `prettier` key in `package.json`, including projects with no wrapper script. The repository's own `.markdownlint.jsonc` continues to disable MD060 and distinguishes the missing aligned-style fixer from the compact-style fixer.

### Release metadata and generated mirrors

| Plugin           | Base version | Branch version | Change                                                            |
| ---------------- | ------------ | -------------- | ----------------------------------------------------------------- |
| `lint-and-fix`   | `1.3.9`      | `1.3.10`       | Recognize Prettier configuration in `package.json`.               |
| `set-up-linters` | `2.1.0`      | `2.2.0`        | Select the generic MD060 setting from actual formatter coverage.  |
| `write-markdown` | `1.2.3`      | `1.2.4`        | Correct alignment ownership, validation order, and CLI fallbacks. |

The catalog state changes from `catalog-M70-m105-p159-n57` at the recorded base to `catalog-M70-m106-p161-n57`. Source manifests, marketplace entries, and the generated Codex marketplace agree.

Both mirrors rebuild successfully. Changed Codex skill copies match their source files; OpenCode exposes these skills through existing symlinks and requires no changed file.

### Planning and review

The implementation plan is retained at `docs/plans/done/2026-09-14-write-markdown-table-alignment-ownership.md`. This review covers the complete branch scope through the recorded commit, including the approved `lint-and-fix` expansion.

## File Inventory

### New files

- `docs/plans/done/2026-09-14-write-markdown-table-alignment-ownership.md`
- `docs/reviews/2026-09-14-fix-334-markdown-table-alignment.md`

### Modified files

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `.markdownlint.jsonc`
- `dist/codex/plugins/lint-and-fix/.claude-plugin/plugin.json`
- `dist/codex/plugins/lint-and-fix/skills/lint-and-fix/SKILL.md`
- `dist/codex/plugins/set-up-linters/.claude-plugin/plugin.json`
- `dist/codex/plugins/set-up-linters/skills/set-up-linters/SKILL.md`
- `dist/codex/plugins/set-up-linters/skills/set-up-linters/references/tools/markdownlint.md`
- `dist/codex/plugins/write-markdown/.claude-plugin/plugin.json`
- `dist/codex/plugins/write-markdown/skills/write-markdown/SKILL.md`
- `dist/codex/plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`
- `plugins/lint-and-fix/.claude-plugin/plugin.json`
- `plugins/lint-and-fix/skills/lint-and-fix/SKILL.md`
- `plugins/set-up-linters/.claude-plugin/plugin.json`
- `plugins/set-up-linters/skills/set-up-linters/SKILL.md`
- `plugins/set-up-linters/skills/set-up-linters/references/tools/markdownlint.md`
- `plugins/write-markdown/.claude-plugin/plugin.json`
- `plugins/write-markdown/skills/write-markdown/SKILL.md`
- `plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`

## Notable Changes

- `write-markdown` and `lint-and-fix` receive patch releases for prompt corrections. The `set-up-linters` minor release adds formatter-dependent configuration selection.
- Generated content is rebuilt from canonical plugin sources.
- The changes relative to the recorded base are agent instructions, configuration examples, metadata, and documentation. They add no runtime dependency or executable helper.

## Plan Compliance

**Verdict: The planned implementation is complete, with documented scope extensions.**

| Plan area                | Assessment                                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------------------------- |
| Markdown skill guidance  | Complete: per-file coverage, draft examples, manual procedure, and validation order agree.            |
| Reference guide          | Complete: ownership, manual alignment, and MD060 compaction behavior are documented.                  |
| Versions and mirrors     | Complete: all three changed plugins have forward version bumps; catalogs and mirrors pass validation. |
| Repository MD060 comment | Complete: it distinguishes aligned-style limitations from the default fixer's compaction behavior.    |

### Scope and fidelity

The original plan listed `set-up-linters` as follow-up work. The branch includes that configuration capability, its minor version bump, and the Pandoc-academic exception. The user also approved extending this PR to `lint-and-fix` so both shared detection tables recognize `package.json` configuration.

The final workflow refines the plan's formatter detection and unconditional fallback order through actual command coverage and the effective MD060 setting. The catalog includes all three plugin version changes and the merged base-branch updates. The completed plan remains a historical record.

### Verification evidence

| Check                                                 | Evidence and scope                                                                                                                                                                                                                         |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Markdownlint, Prettier, ShellCheck, shfmt, actionlint | `make lint validate` passed locally at `e1dbc738`, including the merged source.                                                                                                                                                            |
| JSON and plugin validation                            | The same command passed catalog consistency, skill cross-references, and generated-tree freshness checks.                                                                                                                                  |
| Formatting and mirror generation                      | `make format` passed for the source corrections, and `make build` rebuilt both mirrors after the base-branch merge.                                                                                                                        |
| Version check                                         | All three changed plugins have forward bumps, and `bin/compute-catalog-state` matches `catalog-M70-m106-p161-n57`.                                                                                                                         |
| Whitespace                                            | `git diff --check` passed for the source corrections and merge resolution.                                                                                                                                                                 |
| Scrut                                                 | [The CI Scrut job](https://github.com/cboone/agent-harness-plugins/actions/runs/35008141149/job/104512998264) passed at `01fafb4e`. It was not rerun locally for the subsequent prompt changes; this result does not certify a later head. |
| Formatter coverage probes                             | Prettier `3.9.6` recognized `package.json` configuration and independently honored `.gitignore` and `.prettierignore`. A JavaScript-only format check passed while the Markdown file remained unformatted.                                 |
| Validation order probe                                | With markdownlint-cli2 `0.23.2`, markdownlint `0.41.1`, and MD060 set to `aligned`, lint-fix failed on an unpadded table with three unfixable errors. A standalone Prettier pass aligned it, and the same lint-fix command then passed.    |

## Code Quality Assessment

**Assessment: No blocking source findings remain in the reviewed range.** Generic configuration selection preserves alignment enforcement when formatter coverage is incomplete, the Pandoc exception is explicit, and the validation order handles enabled MD060 rules without depending on a later step in a failing command chain.

The published skill and reference guidance agree on coverage, ignored files, manual alignment, and command order. The shared detection tables recognize `package.json` configuration. All three version bumps and the generated artifacts match the final content.

Merge readiness still requires CI and Copilot results for the PR's current head. This source assessment is pinned to `e1dbc738` and does not substitute for those checks.

## Changes Since Last Review

The preceding assessment covered `340f319..76bf7213`. Subsequent branch work adds:

- The approved `lint-and-fix` configuration detection correction, its patch version, and generated copies.
- Actual formatter coverage checks, effective ignore-file handling, and preservation of the generic aligned rule for mixed coverage.
- Package-manager CLI runners and a standalone formatter pass before lint fixes when MD060 is enabled or unknown.
- Explicit manual alignment for files excluded from Prettier.
- Merges of `main` through `f9aa1673`, recomputed catalog state, and this updated inventory and verification record.
