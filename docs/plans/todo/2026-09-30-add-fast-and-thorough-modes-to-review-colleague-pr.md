# Add fast and thorough modes to review-colleague-pr

## Context

`review-colleague-pr` currently runs one depth of review: it gathers every requirements source (issue comments, parent issues, sub-issues), reads every reviewable diff in full, reads parent-aware per-commit patches on re-reviews, and reports every section (follow-ups, conventions, pre-existing, done well). That is valuable when a PR deserves a full pass, but it is heavy for the common case where the user mainly wants to know whether anything significant is wrong.

This change adds two modes:

- **Fast** (the new default): reads less and reports only the most significant concerns. It skips nits, follow-up-level points and small details.
- **Thorough** (`--thorough`): today's behavior, essentially unchanged.

Decisions settled with the user:

- Fast is the default; `--thorough` opts into the full review. `--fast` is also accepted, for explicitness.
- Fast mode reads less as well as reporting less. Every safety and read-only rule is identical in both modes.

## Changes

### 1. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md`

**Options** (line 16 list): add

- `--fast` (default): focus on what would block merge or change the verdict.
- `--thorough`: the full review: every requirement source, every reviewable diff, attribution on re-reviews, and all report sections.
- If both are given, ask which one the user meant and stop (consistent with the existing Error Handling rule for questions).
- Clarify that `--full` is unrelated: it controls re-review scope (whole PR versus since the last review), not depth. The two combine freely.

**New `## Review Modes` section** after Options, before Review Principles. One short table or list stating, per stage, what fast changes. Everything not listed runs identically in both modes. State explicitly that the Ground Rules, secret exclusions, snapshot fetching, revalidation, restart limit and confirmation bar never relax in fast mode.

| Stage                     | Fast                                                                                                                                                                                                                                                                                | Thorough                         |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| Requirements (step 3)     | PR title/body, closing issues' bodies, user-supplied docs. Read issue comments, parent and sub-issues only when those sources do not state acceptance criteria. Name skipped sources under Requirements.                                                                            | All sources, as today.           |
| Prior discussion (step 4) | Unchanged (needed for the baseline and to avoid piling on).                                                                                                                                                                                                                         | Unchanged.                       |
| Reading (step 5)          | Read the full diff of source, tests, configuration, build, schema/migration and security-relevant files. Docs, fixtures, snapshots and other low-risk assets are listed in the header as not read in detail (existing step 5 disclosure mechanism, secret-path rule still applies). | Every reviewable diff, as today. |
| Re-review (step 5)        | Establish the rename chain (unchanged, it gates exclusions), read the baseline-to-head delta, skip per-commit parent-aware patches. Read them for a specific path only when a significant concern's attribution depends on it; otherwise make no attribution claims.                | As today.                        |
| CI (step 5)               | Unchanged.                                                                                                                                                                                                                                                                          | Unchanged.                       |

**Principle 4, "Proportion over coverage"** (line 34): add one sentence that fast mode applies this more strictly, per Review Modes.

**Step 3, 5 and 6** : add a one-line pointer at each affected point ("In fast mode, see Review Modes") rather than duplicating rules, so the thorough workflow text stays as it is.

**Step 6, Assess** (line 265): add a fast-mode paragraph:

- Assess **Before merge** in full, with the same confirmation bar.
- **Direction**: report only a concrete problem; omit when the direction is sound.
- **Requirements**: report only core requirements that are missing or partly met.
- **Questions for the author**: only ones whose answer could move an item into Before merge or change the verdict.
- **Prior discussion / Since your last review**: unchanged.
- Omit Could be follow-ups, Convention points, Pre-existing and Done well. Do not hunt for them.
- **Verdict**: "Needs a rethink", "Needs changes", or "No blockers found" ("Approve with follow-ups" and "Ready to approve" need the thorough pass, since follow-ups were not assessed).

**Step 7, Report** (line 281): the header line records the mode, for example `Fast review; --thorough adds follow-ups, pre-existing issues and strengths.` Add a short fast-mode example after the existing one (header, verdict, summary, Before merge, one question). Keep the existing example labeled as a thorough report.

### 2. `plugins/review-colleague-pr/README.md`

- "What It Does": one paragraph describing the two modes and that fast is the default; mark which report sections appear only in thorough mode.
- Usage block and options table: add `--fast` and `--thorough`, and note `--full` is about re-review scope, not depth.
- Keep the root-README/catalog description verbatim (it still holds for thorough mode, and the catalog wording does not claim depth). No change to `.claude-plugin/marketplace.json` or root `README.md`.

### 3. Version

`plugins/review-colleague-pr/.claude-plugin/plugin.json`: `1.0.1` to `1.1.0` (new capability). No invocation stops working, and `--thorough` restores the previous output, so this is treated as minor rather than major. There is no `.codex-plugin/plugin.json` for this plugin.

### 4. Generated mirrors and plan file

- Run `make build` to regenerate `dist/codex/plugins/review-colleague-pr/` (never hand-edit).
- Rename this plan to `docs/plans/todo/2026-09-30-add-fast-and-thorough-modes-to-review-colleague-pr.md` and commit it (a `cboone` repo, so plans are retained).

## Verification

1. `make build`, then confirm `git status` shows only the expected mirror updates.
2. `make lint` and `make validate` (catalog, manifests, mirrors, cross-references).
3. `make test-all`, observing the final result.
4. Run the `check-versions` skill.
5. Manual check: invoke `/review-colleague-pr <n>` on a real open PR in a `cboone` repository, once with no flag and once with `--thorough`. Confirm the fast run's header names its mode and any files not read in detail, it reports no follow-up, pre-existing or done-well sections, and the thorough run's output matches today's structure. Confirm nothing is posted to GitHub in either run.

Commits: GPG-signed Conventional Commits at logical boundaries (for example `feat: add fast and thorough modes to review-colleague-pr`, then `chore: regenerate mirrors`, then `docs: add plan`), consistent with recent history.
