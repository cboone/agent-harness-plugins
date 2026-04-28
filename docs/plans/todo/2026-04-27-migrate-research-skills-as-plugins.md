# Migrate Research and Math Skills from `strength-model` into Plugins

> Plan author: Claude (Opus 4.7, 1M ctx). Started 2026-04-27.

## Context

The user has built up 11 skills under `~/Development/strength-model/skills/` while working on the `strength-model` Lean formalization project. Some are generic enough to live as plugins in `cboone-cc-plugins`; others are tightly coupled to that repo's specific scripts, directory layout, and conventions, and trying to genericize them would strip the value.

Migrating the generic ones gives:

- A single source of truth, versioned per plugin.
- Marketplace install across all the user's research projects.
- Automatic OpenCode export via `bin/build-opencode-mirror`.
- A clean separation between the project (`strength-model`) and the methodology (the skills).

After reading each skill end-to-end (2026-04-27), 4 skills are explicitly out of scope for plugin migration because they're inseparable from the strength-model repo:

- **`bootstrap-research-program`** (595 lines): hardcodes `papers/<id>-<slug>/` + `framework/` + `verso/correspondence/` directory roots, IEEE template path, `papers/submission-schedule.yaml` priority-code vocabulary, paper 6 / 7 exemplars, `proofs/StrengthModel/<CamelCase>.lean` Lean module convention. Genericization would gut its value.
- **`maintain-planning-structure`** (302 lines): inspects specific files (`papers/plan.md`, `papers/submission-ladder.md`, `framework/formalization-status.md`, `verso/correspondence/`) by exact name. The "5-10 worktrees concurrently" workflow assumption is project-specific.
- **`manage-bibliographies`** (275 lines): workflow wrapper for 8+ project-local Python scripts (`bin/extract-pdf-text.py`, `bin/build-cross-references.py`, etc.) and the Mathpix `/v3/pdf` integration. Without those scripts, the skill describes nothing.
- **`ingest-reference-paper`** (229 lines): judgment layer for the same scripts, plus failure-mode tables tied to this specific OCR corpus, plus references to `.github/copilot-instructions.md` and `strength-data/docs/design/ecosystem-artifact-contracts.md`.

These four stay in `~/Development/strength-model/skills/`. If the user starts a second research repo with the same layout, copying the skills directory is the right migration path; they're not generic enough to live in a marketplace.

The 7 in scope:

- **`write-math`** (~83 lines, already generic): mathematical writing/exposition guide based on Tao, Knuth, Halmos.
- **`write-latex`** (~72 lines, already generic): LaTeX typesetting guide based on AMS, IEEE, ISO 80000-2, Knuth.
- **`write-pandoc-markdown`** (~68 lines, already generic): Pandoc-flavored Markdown conventions for academic papers with LaTeX output.
- **`write-lean-code`** (~74 lines, mostly generic): Lean 4 style guide and Mathlib conventions.
- **`write-lean-tests`** (~185 lines, project-bound but salvageable): compile-time `example`-based Lean 4 API regression tests; needs sanitization of `proofs/StrengthModelTest/` references.
- **`write-formalization-roadmap`** (~116 lines, generic by design): document-structure guide for multi-milestone formalization roadmaps across Lean, Rocq, Isabelle.
- **`manage-repo-licensing`** (~350 lines, already generic): REUSE-style mixed-license coverage with SPDX headers, `LICENSES/`, `REUSE.toml`, `NOTICE` authoring.

Resolved decisions (from clarifying conversation, 2026-04-27):

1. **Granularity**: One plugin per source skill. Matches existing repo convention (every `write-X` skill is its own plugin).
2. **Genericization**: Sanitize project-specific content to placeholders. Keep `strength-model` references only as illustrative case studies in `Sources` sections where they help.
3. **Categorization** (introduces a new `writing` category):
   - `code-quality`: `write-latex`, `write-lean-code`, `write-lean-tests`. Code-style/typesetting/test-style guides — same shape as the existing `write-go-code`, `write-bash-scripts`, etc.
   - `writing` (**new category**): `write-pandoc-markdown`, `write-math`, `write-formalization-roadmap`. Plus **the existing `write-markdown` plugin gets recategorized** from `code-quality` into `writing`. The new category captures style/structure guides for prose and document artifacts (as opposed to code).
   - `productivity`: `manage-repo-licensing`. REUSE/SPDX is a generic repo utility, analogous to existing `productivity` siblings `add-community-files`, `scaffold-new-repo`, and `setup-installers`.

The `productivity` category is a known catchall (27 of 41 existing plugins live there, doing everything from `commit` to `notify` to `scaffold-go-cli`). Refactoring `productivity` into more granular subcategories is out of scope here; a follow-up GitHub issue (drafted at the bottom of this plan, filed at execution time) tracks that work.

## Approach

Follow the existing `/create-plugin` workflow at `plugins/create-plugin/skills/create-plugin/SKILL.md` for each plugin. The work is 7 mechanical migrations, plus catalog updates, plus introducing the new `writing` category, plus recategorizing one existing plugin.

Order the migrations bottom-up so cross-references between newly migrated skills resolve as each lands:

| Tier | Plugins | Why this tier |
| --- | --- | --- |
| 1 | `write-math`, `write-latex`, `write-pandoc-markdown` | No cross-skill deps; foundations. |
| 2 | `write-lean-code`, `write-lean-tests` | Bidirectional pair; land together. |
| 3 | `write-formalization-roadmap` | References Tier 1. |
| 4 | `manage-repo-licensing` | Standalone; can land anywhere. |

Each tier can be its own commit (or commits) for clean PR history. The category infrastructure changes (new `writing` category in references, recategorization of `write-markdown`) should land first as a "category prep" commit so subsequent tiers can use the new category cleanly.

## Per-plugin migration steps (apply 7 times)

For each plugin `<NAME>`:

1. **Create directory structure** — implicit on first Write:

   - `plugins/<NAME>/.claude-plugin/plugin.json`
   - `plugins/<NAME>/skills/<NAME>/SKILL.md`
   - `plugins/<NAME>/skills/<NAME>/references/...` (preserve source's `references/` subtree)
   - `plugins/<NAME>/README.md`

2. **Copy source files** from `~/Development/strength-model/skills/<NAME>/` into `plugins/<NAME>/skills/<NAME>/`. Use `cp -R` for directory subtrees, then re-Read each Markdown file and Edit it for genericization.

3. **Genericize SKILL.md and references** (see "Genericization rules" below).

4. **Write `plugin.json`** following the Skills Plugin Template at `plugins/create-plugin/skills/create-plugin/references/plugin-json.md`. Invariants:

   - Alphabetized fields.
   - `version`: `1.0.0` for new plugins.
   - `keywords`: lowercase, alphabetized, ~3-6 entries.
   - `skills`: `"./skills"`.
   - `name` matches the directory name.

5. **Write per-plugin `README.md`** following the "Template for Skills" at `plugins/create-plugin/skills/create-plugin/references/readme-updates.md`. Crib from `plugins/write-go-code/README.md` for tone (style-guide skills) or `plugins/handle-secrets/README.md` for workflow skills.

6. **Insert into `.claude-plugin/marketplace.json`** alphabetically by `name`. Match `plugin.json` for shared fields and add `category` and `source`.

7. **Update root `README.md`** — both the ToC entry and the H3 description section.

8. **Update root `CLAUDE.md`** — append the directory tree for the new plugin under `plugins/`, alphabetically.

## Genericization rules

Per-plugin notes (from end-to-end SKILL.md reads on 2026-04-27):

- **`write-math`** — Already generic. Migrate verbatim. (~83 lines.)
- **`write-latex`** — Already generic. Migrate verbatim. (~72 lines.)
- **`write-pandoc-markdown`** — Already generic. Migrate verbatim. (~68 lines.)
- **`write-formalization-roadmap`** — Generic by design (covers Lean, Rocq, Isabelle, HOL). Verify references don't name `strength-model` specifically; sanitize any leakage.
- **`manage-repo-licensing`** — Already generic (REUSE/SPDX workflow). Migrate as-is. The `references/NOTICE.template.md` should stay templated.
- **`write-lean-code`** — Mostly generic, but check `references/comprehensive/pfr-downstream.md` and `references/comprehensive/build-infrastructure.md` for project-specific paths and sanitize.
- **`write-lean-tests`** — Heavy `StrengthModel` / `proofs/StrengthModelTest/` references. Apply find-and-replace below; demote concrete fixture names to a `## Sources` section as illustrative.

Find-and-replace table (apply to all 7 SKILL.md files and references):

| Find (project-specific) | Replace with (generic) |
| --- | --- |
| `proofs/StrengthModelTest/` | `<Name>Test/` (or `proofs/<Name>Test/` when the host repo's proof root is implied) |
| `proofs/StrengthModel/` | `<Name>/` |
| `StrengthModel.X.Y` (Lean module path) | `<Name>.X.Y` |
| `proofs/lakefile.toml` | `lakefile.toml` (with note: "in this repo's case, `proofs/lakefile.toml`") |
| Concrete fixture names (`threeGuessAttacker`, `cheapHashVf`, `iphoneDefense`) | Keep as illustrative in a `Sources` section, marked "(example fixtures from `strength-model`)" |
| `strength-model` repo paths in workflow steps | Replace with role-based descriptions ("the host research repo") |

## New `writing` marketplace category

The current `marketplace-json.md` reference lists only `code-quality` and `productivity` as valid categories (`plugins/create-plugin/skills/create-plugin/references/marketplace-json.md` lines 52-56). Adding a third category requires:

1. Update `plugins/create-plugin/skills/create-plugin/references/marketplace-json.md` "Valid Categories" section to add `"writing"` with a one-line definition (e.g., "style and structure guides for prose, documentation, and document artifacts").
2. Update `plugins/create-plugin/skills/create-plugin/references/readme-updates.md` "Subcategory Guide" table to add a `Writing` row covering the new ToC subcategory.
3. Bump the `create-plugin` plugin version (patch bump in `plugins/create-plugin/.claude-plugin/plugin.json` and the marketplace entry — currently `1.2.0` → `1.2.1`) since its reference content changes.

## Recategorization of `write-markdown`

`write-markdown` currently lives in `code-quality` (a category-of-convenience inherited from when no `writing` category existed). Move it to `writing`:

1. Edit its entry in `.claude-plugin/marketplace.json` — change `"category": "code-quality"` to `"category": "writing"`. No other field changes.
2. `plugins/write-markdown/.claude-plugin/plugin.json` does **not** change (no `category` field there) and does **not** get a version bump (content unchanged).
3. README ToC: remove `Write Markdown` from the Code Quality subcategory line, insert it alphabetically into the new Writing subcategory line.
4. README description sections: remove the existing `### Write Markdown` H3 from under `## Code Quality`, place it (verbatim) under the new `## Writing` H2 in alphabetical order.

This single recategorization is not a marketplace `metadata.version` bump on its own (that field tracks plugin add/remove, not category churn).

## ToC and README structure changes

The new ToC subcategory under Skills (alphabetical within):

```markdown
<br>Writing:
[Write Formalization Roadmap](#write-formalization-roadmap)
∙ [Write Markdown](#write-markdown)
∙ [Write Math](#write-math)
∙ [Write Pandoc Markdown](#write-pandoc-markdown)
```

Insertion point: between `Code Quality` and `Scaffolding`.

The three new `code-quality` migrations (`write-latex`, `write-lean-code`, `write-lean-tests`) slot alphabetically into the existing Code Quality subcategory ToC line. `write-markdown` is **removed** from that line as part of the recategorization.

`manage-repo-licensing` slots into the existing Scaffolding subcategory ToC line alphabetically (after `Bootstrap Project`).

A matching `## Writing` H2 section in the README "Skills" section sits between Code Quality and Scaffolding, giving final H2 ordering: `### Git`, `### Issues and Worktrees`, `### Code Review`, `### Code Quality`, `### Writing` (new), `### Scaffolding`, `### Agents`. The existing `### Write Markdown` H3 moves into Writing; the four new H3 entries (`### Write Formalization Roadmap`, `### Write Math`, `### Write Pandoc Markdown` go in Writing; `### Write Latex`, `### Write Lean Code`, `### Write Lean Tests` go in Code Quality; `### Manage Repo Licensing` goes in Scaffolding) land alphabetically within their subsections.

## Marketplace metadata version bump

`metadata.version` in `.claude-plugin/marketplace.json` is currently `1.26.0`. Seven new plugins → bump minor seven times: `1.26.0` → `1.33.0`. (Convention at `CLAUDE.md` "Versioning" section is one minor bump per added/removed plugin.) The `write-markdown` recategorization does not contribute additional bumps (catalog membership unchanged).

## Critical files to modify

**Create (4 per plugin × 7 = 28 new top-level files, plus references subtrees copied wholesale):**

- `plugins/<NAME>/.claude-plugin/plugin.json`
- `plugins/<NAME>/skills/<NAME>/SKILL.md`
- `plugins/<NAME>/skills/<NAME>/references/...` (only where source has them; copy then sanitize)
- `plugins/<NAME>/README.md`

**Modify:**

- `.claude-plugin/marketplace.json` — 7 new plugin entries; recategorize `write-markdown` entry from `code-quality` to `writing`; bump `metadata.version` to `1.33.0`.
- `README.md` — new `## Writing` H2 with new Writing ToC subcategory; remove `Write Markdown` from Code Quality ToC and `### Write Markdown` H3 from `## Code Quality`; reinstate them under Writing; insert the three Code Quality additions and `manage-repo-licensing` (under Scaffolding) alphabetically; insert new H3 description blocks for all 7 migrations.
- `CLAUDE.md` — extend the directory tree under `plugins/` with 7 new entries, alphabetically.
- `plugins/create-plugin/skills/create-plugin/references/marketplace-json.md` — add `writing` to Valid Categories.
- `plugins/create-plugin/skills/create-plugin/references/readme-updates.md` — add Writing row to Subcategory Guide.
- `plugins/create-plugin/.claude-plugin/plugin.json` and matching marketplace entry — patch bump (`1.2.0` → `1.2.1`).

**Reuse (read, do not modify):**

- `plugins/create-plugin/skills/create-plugin/SKILL.md` — workflow guide.
- `plugins/create-plugin/skills/create-plugin/references/plugin-json.md` — field reference and templates.
- `plugins/create-plugin/skills/create-plugin/references/skill-md.md` — frontmatter and body conventions.
- `plugins/create-plugin/skills/create-plugin/references/marketplace-json.md` — entry format.
- `plugins/create-plugin/skills/create-plugin/references/readme-updates.md` — README and per-plugin README templates.
- Existing analogous plugins as cribs:
  - `plugins/write-go-code/` for "always-on" style-guide structure with `references/essential/` + `references/comprehensive/`.
  - `plugins/handle-secrets/` for a workflow skill with categorized references.
  - `plugins/write-markdown/` for the simplest case (no categorized references) — also serves as the recategorization template.

## Follow-up issue (filed)

Filed as [#245](https://github.com/cboone/cboone-cc-plugins/issues/245) on 2026-04-27, ahead of execution, so the migration PR can reference it. Tracks refactoring the `productivity` catchall into more granular marketplace categories aligned with the README ToC subcategories. Out of scope for this migration.

## Verification

After all 7 plugins land:

1. **JSON validity**

   ```bash
   python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
   for p in plugins/*/; do python3 -m json.tool "$p.claude-plugin/plugin.json" > /dev/null; done
   ```

2. **Field consistency**: spot-check one new plugin against `plugin.json` ↔ `marketplace.json` field equivalence (all shared fields match exactly). Confirm `write-markdown`'s marketplace entry now reads `"category": "writing"`.

3. **Run the `/check-versions` skill** (per `CLAUDE.md`'s versioning guidance): verifies plugin versions and marketplace.json are consistent.

4. **Run the `/lint-and-fix` skill** to catch markdownlint issues in the new SKILL.md and README.md files.

5. **OpenCode mirror** rebuild:

   ```bash
   bin/build-opencode-mirror
   git status dist/opencode  # 7 new mirrored skill directories should appear
   ```

   Confirm 7 new entries in `dist/opencode/` and that none reference `${CLAUDE_PLUGIN_ROOT}` (per the README "Known limitations" note, that pattern doesn't expand in OpenCode — the migrated skills shouldn't use it since the source skills don't either, but verify).

6. **Live activation test** (in a fresh Claude Code session in a side worktree):

   ```bash
   /plugin marketplace add cboone/cboone-cc-plugins  # if not already added
   /plugin install write-math@cboone-cc-plugins
   ```

   Then ask Claude something math-y and confirm `write-math` activates from the new plugin source rather than the user-global `~/Development/strength-model/skills/` source. Repeat for one workflow skill (`/manage-repo-licensing`).

7. **CI**: open a draft PR; existing CI should validate marketplace schema, OpenCode mirror drift, and markdown linting.

8. **Confirm follow-up issue is filed** and its number is referenced in the PR description.

## Out of scope (explicitly deferred)

- **Migrating the 4 repo-bound skills** (`bootstrap-research-program`, `maintain-planning-structure`, `manage-bibliographies`, `ingest-reference-paper`). They stay in `~/Development/strength-model/skills/`.
- **Refactoring the `productivity` catchall.** Tracked by the follow-up issue drafted above. Out of scope here to keep this PR focused.
- **Removing or symlinking the source skills** in `~/Development/strength-model/skills/` for the 7 migrated ones. Once the plugins are installed via marketplace, the user can manually retire the local copies. This plan does not modify anything outside `cboone-cc-plugins`.
- **Renaming source skill names**. We preserve every name as-is; these become the plugin names.
- **Editing CLAUDE.md prose** beyond the directory tree. The skill-list section in the user's global `~/.claude/CLAUDE.md` will need an update to reflect the new triggers, but that's a follow-up the user runs in their dotfiles repo.
- **Cross-linking between newly migrated skills** with `${CLAUDE_PLUGIN_ROOT}` patterns. Source skills already cross-reference each other via plain skill names (e.g., `bootstrap-research-program` mentions `write-math`); these references get preserved during sanitization but not converted to `${CLAUDE_PLUGIN_ROOT}` patterns, since that breaks the OpenCode mirror.
