# write-markdown: split table alignment by who owns it (#334)

## Context

`write-markdown` loads automatically before every Markdown edit. It still tells agents to pad table cells by hand, and it cites MD060 as the rule that requires this. PR #325 moved table alignment to Prettier and set `MD060: false` in this repo, so the skill now contradicts the config. It also sends agents off computing column widths by hand for tables Prettier will rewrite anyway.

The guidance cannot simply be deleted. The skill also ships to repos that run markdownlint without Prettier, and there hand-alignment is the only option. So the fix splits the rule by who owns alignment:

- **Prettier formats Markdown:** Prettier aligns tables. Write the rows, run the format command, do not pad by hand, do not cite MD060.
- **No Prettier:** align by hand, as the current procedure describes.

## Finding: MD060 does have a fixer, and it compacts

The issue asks for MD060 to be checked by running it, not by reading its docs. I ran markdownlint 0.41.1 (the version `markdownlint-cli2` 0.23.2 resolves) in memory with `lint` plus `applyFixes`, with MD060 at its default settings:

| Case                                    | Reported against | `--fix` result                         |
| --------------------------------------- | ---------------- | -------------------------------------- |
| Aligned table, one cell edited          | `aligned`        | unchanged (no fix exists)              |
| Aligned table, two longer rows appended | `compact`        | padding stripped from the aligned rows |
| Mixed spacing                           | `compact`        | rewritten to compact                   |
| Any violation under `style: aligned`    | `aligned`        | unchanged                              |

The first two rows were then reproduced through the real CLI (`markdownlint-cli2` v0.23.2, markdownlint v0.41.1) on scratch files: the appended-rows table was compacted (3 fixes applied), and the edited-cell table came back byte-identical with 2 unfixable `aligned` errors remaining.

So "no fixer at any version" is wrong. The `aligned` style has no fixer. The `compact` and `tight` styles do, and under `any` a table that picked up a few unpadded rows can be compacted by `--fix`. The skill has to say this in the no-Prettier branch (align **before** running `--fix`), and this repo's `.markdownlint.jsonc` comment repeats the inaccurate claim.

## Changes

### 1. `plugins/write-markdown/skills/write-markdown/SKILL.md`

- **Common Mistakes intro:** reword "cause the most lint failures" so it no longer suggests that alignment is a lint failure everywhere.
- **Heading (line 17):** `### Tables: align all pipes vertically` becomes `### Tables: aligned pipes, from Prettier where it runs`.
- **Examples:** keep both. Relabel the first as the committed form and the second as "Ragged: fine as a draft only where Prettier will format it" (not "Wrong").
- **Line 37 procedure:** replace with two short branches:
  - **Prettier formats Markdown here:** Prettier owns alignment. Write rows without padding, including when adding a row to an existing table, and run the format command (`yarn format`, `yarn lint:fix`, `make format`, or the project's equivalent). Do not hand-pad; do not cite MD060, which such projects typically disable.
  - One-sentence detection rule: a Prettier config (`.prettierrc*`, `prettier.config.*`, or a `prettier` key in `package.json`) or a format script that runs Prettier, and `.prettierignore` does not exclude the file. The config filenames match the detection table in `plugins/lint-and-fix/skills/lint-and-fix/SKILL.md`.
  - **No Prettier:** nothing else aligns tables, so align by hand, before running `markdownlint-cli2 --fix`. MD060 cannot fix toward aligned, and with its default style a table with a few unpadded rows gets compacted. Then the existing procedure sentence, unchanged.
- **Key Conventions, Tables bullet (line 90):** drop `(MD060)`. The new bullet says to align pipes and pad delimiter hyphens, that Prettier's format command does this where it runs, and that elsewhere it is done by hand because markdownlint cannot.
- **Validation (lines 107 to 111):** stop claiming the lint-fix command "auto-corrects table alignment". Run the lint-fix command, then the format command, so Prettier has the last word on layout (the same order as this repo's `lint:fix`). Add `yarn format` to the list of example scripts. The `markdownlint-cli2 --fix` fallback gains a note to align tables by hand first.

### 2. `plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`

- **Heading (line 530):** `### Table column alignment (MD060)` becomes `### Table column alignment`. No anchors point at the old slug (checked with grep).
- **Line 532:** describe the committed form (aligned pipes, padded cells, filled delimiter) as Prettier's table formatting, which is also what MD060's `aligned` style accepts. MD060 becomes context, not the authority.
- **Examples:** relabel "Avoid" the same way as in SKILL.md.
- **New ownership paragraphs:**
  - **Where Prettier formats Markdown:** Prettier owns alignment. Rows go in unpadded and the format command aligns them. Such projects typically set `MD060: false`, because markdownlint cannot fix toward aligned and its default `any` style reports, and fixes, toward whichever style is closest. Includes the same detection rule as SKILL.md.
  - **Where Prettier is not configured:** align by hand, before `markdownlint-cli2 --fix`, with the compaction hazard stated. Keep the existing five-step procedure. Add one sentence: if Prettier is added later, hand-aligned tables do not change.
- **Line 560:** delete the "safety net ... write aligned tables from the start" sentence. It gets ownership backwards.

### 3. Version, catalog, mirrors

- `write-markdown` goes from `1.2.3` to `1.2.4`, a patch for a guidance fix, matching the convention in #421. Update `plugins/write-markdown/.claude-plugin/plugin.json` and the `.claude-plugin/marketplace.json` entry.
- Recompute `metadata.version` with `bin/compute-catalog-state`. It should come out as `catalog-M70-m103-p157-n57`.
- Rebuild with `bin/build-codex-marketplace` and `bin/build-opencode-mirror`. Never hand-edit `dist/` or `.agents/`.

### 4. `.markdownlint.jsonc` MD060 comment (beyond the issue's location list)

Correct "markdownlint has no fixer for this rule at any version". The new wording: markdownlint cannot fix toward the aligned style, and under the default `any` style `--fix` can strip padding from a table that picked up unpadded rows. `"MD060": false` stays. This is a separate commit so it can be dropped on its own.

## Commits

1. `fix: hand table alignment to Prettier in write-markdown (#334)`: sections 1 to 3, including mirrors. They must land together or CI's freshness check fails.
1. `docs: correct the MD060 fixer claim in markdownlint config (#334)`: section 4.
1. `docs: add plan for write-markdown table alignment (#334)`: this file, kept in `docs/plans/todo/` per the repo convention (the `pr` skill moves it to `done/`).

## Out of scope (follow-up to offer)

`plugins/set-up-linters/skills/set-up-linters/references/tools/markdownlint.md` generates a markdownlint config that leaves MD060 at its default. Downstream repos get the compacting fixer as a result. It could set `MD060: false` when Prettier is configured, or `{ "style": "aligned" }` when it is not. This belongs to a different plugin, so I will offer to file an issue rather than change it here.

## Verification

1. Repeat the MD060 experiment through the real CLI on scratchpad files, not just the library. Run `markdownlint-cli2 --fix` on (a) an aligned table with longer rows appended and (b) an aligned table with one cell edited, with MD060 at its default. Confirm that (a) is compacted and (b) is byte-identical (`cmp` against a copy). If the CLI behaves differently from the library, correct the wording before committing.
1. Run `bin/check-cross-references` on the edited skill.
1. Run `make build`, then confirm `git status` shows only the expected mirror files.
1. Run `make test-all` (lint, validate, scrut). Rule checks cover version agreement, catalog state, and mirror freshness.
1. Run the `check-versions` skill.
1. Reread both edited files in full. Check that the two branches never contradict each other, that no leftover sentence mandates padding unconditionally, and that there are no em dashes.
