# Branch Review: fix/334-markdown-table-alignment

Base: `main` (merge base: `340f319`)
Commits: 3
Files changed: 10 (1 added, 9 modified, 0 deleted, 0 renamed)
Reviewed through: `5b7836b`

## Summary

This branch corrects `write-markdown` so table alignment is owned by Prettier where Prettier formats Markdown, while retaining explicit hand-alignment guidance for projects without Prettier. It also corrects the inaccurate claim that markdownlint has no MD060 fixer, updates the related configuration rationale, bumps `write-markdown` to `1.2.4`, and refreshes the generated Codex marketplace mirror. The resulting guidance explains the actual MD060 behavior and gives agents a tooling-aware procedure that avoids unnecessary formatting churn.

## Changes by Area

### Markdown guidance

The `write-markdown` skill and its reference guide now distinguish projects where Prettier formats Markdown from those where it does not. In Prettier-managed projects, authors write table rows normally and use the formatter; without Prettier, they align tables before running `markdownlint-cli2 --fix` because MD060 can compact tables instead of creating aligned padding.

Files: `plugins/write-markdown/skills/write-markdown/SKILL.md`, `plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`, `dist/codex/plugins/write-markdown/skills/write-markdown/SKILL.md`, `dist/codex/plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`

### Markdownlint configuration

The MD060 configuration comment now accurately describes the absence of an aligned-style fix and the default `any` style's compaction behavior. The rule remains disabled because this repository delegates table layout to Prettier.

Files: `.markdownlint.jsonc`

### Plugin release metadata and mirrors

The plugin version advances from `1.2.3` to `1.2.4`, and the marketplace catalog state advances from `catalog-M70-m103-p156-n57` to `catalog-M70-m103-p157-n57`. The source manifest, marketplace records, and Codex mirror agree; the OpenCode mirror remains fresh without a changed file because it symlinks this skill.

Files: `plugins/write-markdown/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `dist/codex/plugins/write-markdown/.claude-plugin/plugin.json`

### Planning

The branch adds the plan that documents the MD060 command-line findings, the split ownership model, release metadata changes, and verification requirements.

Files: `docs/plans/todo/2026-09-14-write-markdown-table-alignment-ownership.md`

## File Inventory

### New files

- `docs/plans/todo/2026-09-14-write-markdown-table-alignment-ownership.md`

### Modified files

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `.markdownlint.jsonc`
- `dist/codex/plugins/write-markdown/.claude-plugin/plugin.json`
- `dist/codex/plugins/write-markdown/skills/write-markdown/SKILL.md`
- `dist/codex/plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`
- `plugins/write-markdown/.claude-plugin/plugin.json`
- `plugins/write-markdown/skills/write-markdown/SKILL.md`
- `plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`

## Notable Changes

- The branch changes published guidance and increments `write-markdown` from `1.2.3` to `1.2.4`, which is the appropriate patch-level release for a documentation and behavior-guidance correction.
- The generated Codex mirror and marketplace catalog are updated from source. `bin/validate-plugins` and `make test-all` confirm mirror freshness and catalog consistency.
- No runtime dependencies, public APIs, credentials, schema changes, or security-sensitive code are added.

## Plan Compliance

**Verdict: Good compliance.** All four implementation areas and all six stated verification activities are satisfied by the branch or independently confirmed during this review. The final commit order differs from the plan's proposed order, but that does not affect the resulting source, generated artifacts, or validation coverage.

**Overall progress: 19/19 items done (100%).**

### Markdown skill guidance

- Done: The common-mistakes section, table examples, tooling detection rule, no-Prettier procedure, summary table convention, and validation instructions implement the planned ownership split.
- Done: The guidance correctly says Prettier performs alignment where configured and says manual alignment must precede `markdownlint-cli2 --fix` where it is absent.

### Reference guide

- Done: The table-alignment heading no longer presents MD060 as the authority, and the committed-table description identifies Prettier formatting plus MD060's aligned-style compatibility.
- Done: The reference guide has matching Prettier and no-Prettier branches, retains the manual procedure, documents the compaction hazard, and removes the former safety-net framing.

### Versioning and generated artifacts

- Done: `write-markdown` is `1.2.4` in the source manifest and marketplace entry. The computed catalog state is `catalog-M70-m103-p157-n57`, matching the stored value.
- Done: Codex mirror files match their source. The OpenCode mirror is fresh, confirmed by `bin/validate-plugins` and `make test-all`; no OpenCode file changed because it symlinks the skill.

### Markdownlint comment

- Done: The MD060 comment accurately limits the no-fix claim to aligned style and explains that default `any` can compact an otherwise aligned table after unpadded rows are added.

### Verification

- Done: The commit record documents the requested real-CLI MD060 experiments, including the compacted appended-row case and unchanged edited-cell case.
- Done: `bin/check-cross-references plugins/write-markdown/skills/write-markdown/SKILL.md` passed during this review.
- Done: Generated artifact freshness was verified with `bin/validate-plugins`, `git diff --exit-code HEAD -- .agents/plugins/marketplace.json dist/codex dist/opencode`, and the full test suite.
- Done: `make test-all` passed: Markdown linting and Prettier formatting, ShellCheck, `shfmt`, `actionlint`, JSON validation, plugin validation, and 402 scrut cases.
- Done: The version check confirmed the `1.2.3` to `1.2.4` patch bump and recomputed the expected catalog state.
- Done: The changed guidance was reviewed for contradictory branches, unfinished markers, whitespace errors, and em dashes. None were found.

### Deviations

- Non-blocking: The plan proposed commits in the order implementation, configuration comment, then plan. The actual history adds the plan first, then the configuration comment, then implementation. This only changes history organization; the final tree and validations satisfy the plan.

### Fidelity Concerns

No fidelity concerns found. The wording reflects the plan's central requirement: table alignment is delegated to Prettier when it is available, and manual alignment remains explicit where it is not.

## Code Quality Assessment

**Overall quality: Ready to merge.** The branch is narrowly scoped, internally consistent, and fully validated. It replaces an unconditional formatting instruction with a clear decision rule based on the project's actual formatter configuration, preserving a safe fallback for projects without Prettier.

### Strengths

- The new guidance identifies the formatter as the owner of layout where that ownership exists, eliminating redundant manual padding and inaccurate reliance on MD060.
- Both published skill surfaces use the same decision model and explain the same MD060 limitation, reducing the chance of contradictory instructions.
- The patch version, marketplace state, and generated mirror stay synchronized, and repository validation confirms the published artifacts are fresh.
- The change includes a precise explanation of the observed compaction edge case, which prevents a misleading fallback recommendation.

### Issues to Address

No blocking issues found.

### Review Resolution

- Resolved: `set-up-linters` now generates an MD060 setting based on whether Prettier formats Markdown. It disables MD060 when Prettier owns alignment and requires the `aligned` style otherwise, preventing markdownlint's `any` style from compacting a nearly aligned table during `--fix`.
