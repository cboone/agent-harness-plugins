# Branch Review: fix/334-markdown-table-alignment

Base: `main` (merge base: `340f319`)
Commits: 8
Files changed: 17 (2 added, 15 modified, 0 deleted, 0 renamed)
Reviewed through: `76bf7213`
Updated: 2026-09-15 (previous: 2026-09-14)

The counts and assessment describe `340f319..76bf7213`. The commit that saves this updated review is outside that range.

## Summary

This branch gives Prettier responsibility for table alignment in files it formats and retains manual alignment for other Markdown files. It updates both the `write-markdown` guidance and the `set-up-linters` configuration templates, including the Pandoc-academic exception. The validation workflow uses the same ownership decision when choosing command order and direct CLI fallbacks.

The branch also corrects the repository's MD060 comment, advances `write-markdown` to `1.2.4` and `set-up-linters` to `2.2.0`, synchronizes the catalogs and generated mirrors, and archives the completed plan.

## Changes by Area

### Markdown guidance and validation

The skill and reference guide identify Prettier through its configuration or a format script, while honoring `.prettierignore`. Where Prettier formats the file, authors write rows without manual padding, run lint fixes, and run Prettier last. If a project script is missing, the validation section calls the corresponding installed CLI directly on the edited files, including `prettier --write` when no formatting script exists.

For files Prettier does not format, manual table alignment must happen before every markdownlint fix command, including project-specific scripts. This ordering protects existing padding from MD060's default `any` style, which can compact a nearly aligned table. The reference retains the full manual alignment procedure.

### Markdownlint presets

The generic configuration disables MD060 where Prettier formats Markdown and requires `{ "style": "aligned" }` otherwise. The setup instructions, configuration fragments, customization table, and notes describe that same choice.

The Pandoc-academic preset explicitly keeps `MD060: false` regardless of Prettier, preserving its allowance for dense academic tables. The generic rule does not overwrite that preset. The repository's own `.markdownlint.jsonc` continues to disable MD060 and accurately distinguishes the missing aligned-style fixer from the compact-style fixer.

### Release metadata and generated mirrors

`write-markdown` advances from `1.2.3` to `1.2.4`, and `set-up-linters` advances from `2.1.0` to `2.2.0`. The catalog state changes from `catalog-M70-m103-p156-n57` to `catalog-M70-m104-p157-n57`. Source manifests, marketplace entries, and the generated Codex marketplace agree.

Both mirrors rebuild successfully. The changed Codex skill copies match their source files; OpenCode exposes these skills through existing symlinks and requires no changed file.

### Planning and review

The implementation plan is retained at `docs/plans/done/2026-09-14-write-markdown-table-alignment-ownership.md`. This review covers the complete branch scope through the recorded commit, including the linter setup work and formatter fallback corrections.

## File Inventory

### New files

- `docs/plans/done/2026-09-14-write-markdown-table-alignment-ownership.md`
- `docs/reviews/2026-09-14-fix-334-markdown-table-alignment.md`

### Modified files

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `.markdownlint.jsonc`
- `dist/codex/plugins/set-up-linters/.claude-plugin/plugin.json`
- `dist/codex/plugins/set-up-linters/skills/set-up-linters/SKILL.md`
- `dist/codex/plugins/set-up-linters/skills/set-up-linters/references/tools/markdownlint.md`
- `dist/codex/plugins/write-markdown/.claude-plugin/plugin.json`
- `dist/codex/plugins/write-markdown/skills/write-markdown/SKILL.md`
- `dist/codex/plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`
- `plugins/set-up-linters/.claude-plugin/plugin.json`
- `plugins/set-up-linters/skills/set-up-linters/SKILL.md`
- `plugins/set-up-linters/skills/set-up-linters/references/tools/markdownlint.md`
- `plugins/write-markdown/.claude-plugin/plugin.json`
- `plugins/write-markdown/skills/write-markdown/SKILL.md`
- `plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`

## Notable Changes

- The `write-markdown` patch corrects published guidance. The `set-up-linters` minor version adds configuration selection based on the formatter.
- Generated content is rebuilt from canonical plugin sources.
- The changed behavior is in agent instructions and configuration examples; the branch adds no runtime dependency or executable helper.

## Plan Compliance

**Verdict: The planned implementation is complete, with a documented scope extension.**

| Plan area                | Assessment                                                                                               |
| ------------------------ | -------------------------------------------------------------------------------------------------------- |
| Markdown skill guidance  | Complete: ownership detection, draft examples, manual procedure, and conditional validation order agree. |
| Reference guide          | Complete: the ownership split, full manual procedure, and MD060 compaction behavior are documented.      |
| Versions and mirrors     | Complete: both changed plugins have forward version bumps; catalogs and mirrors pass validation.         |
| Repository MD060 comment | Complete: it distinguishes aligned-style limitations from the default fixer's compaction behavior.       |

### Scope and fidelity

The original plan listed `set-up-linters` as follow-up work. The branch includes that configuration capability, its minor version bump, and the Pandoc-academic exception. This extends the same alignment policy to newly configured projects and is consistent with the issue's purpose.

The plan's unconditional manual fallback and older expected catalog state are refined by the final implementation: direct fallback commands follow the same Prettier detection rule, and the catalog includes both plugin version changes. The completed plan remains a historical record.

### Verification evidence

| Check                                                 | Evidence and scope                                                                                                                                                                                                                                 |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Markdownlint, Prettier, ShellCheck, shfmt, actionlint | `make lint validate` passed locally at `76bf7213`; Markdownlint checked 493 files.                                                                                                                                                                 |
| JSON and plugin validation                            | The same command completed successfully, including catalog consistency, skill cross-references, and mirror freshness.                                                                                                                              |
| Formatting and mirror generation                      | `make format` and `make build` completed successfully for the source corrections.                                                                                                                                                                  |
| Version check                                         | `write-markdown` `1.2.3` to `1.2.4` and `set-up-linters` `2.1.0` to `2.2.0` are forward bumps; `bin/compute-catalog-state` matches `catalog-M70-m104-p157-n57`.                                                                                    |
| Whitespace                                            | `git diff --check` passed for the source corrections.                                                                                                                                                                                              |
| Scrut                                                 | [The CI Scrut job](https://github.com/cboone/agent-harness-plugins/actions/runs/35005552229/job/104504279741) passed at `167e5549`. It was not rerun locally for the subsequent prose-only corrections; this result does not certify a later head. |
| MD060 behavior experiments                            | The completed plan records the real-CLI appended-row and edited-cell experiments with markdownlint-cli2 `0.23.2` and markdownlint `0.41.1`. Those are historical evidence and were not repeated during this update.                                |

## Code Quality Assessment

**Assessment: No blocking source findings remain in the reviewed range.** The generic and Pandoc configuration paths are internally consistent, and the validation workflow preserves the ownership rule with or without project-specific scripts.

The published skill and reference guidance agree on Prettier detection and manual alignment order. Both plugin version bumps and the generated artifacts match the final content. The saved review now names the actual plugin scope, catalog state, plan location, and reviewed commit.

Merge readiness still requires CI and Copilot results for the PR's current head. The source assessment above is pinned to `76bf7213` and does not substitute for those checks.

## Changes Since Last Review

The preceding assessment covered three commits through `5b7836b`. The five additional commits through `76bf7213` add:

- Generic MD060 configuration selection in `set-up-linters`, its minor version bump, and synchronized catalogs and mirrors.
- The saved review and the completed plan's move into `docs/plans/done/`.
- Explicit preservation of the Pandoc-academic MD060 exception throughout the setup guidance.
- Conditional validation order and formatter-aware direct CLI fallbacks in `write-markdown`.
