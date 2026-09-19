# Branch Review: chore/434-m1-improve-codex-compatibility

Base: main (merge base: 046f1389)
Commits: 11
Files changed: 266 (1 added, 265 modified, 0 deleted, 0 renamed)
Reviewed through: 9331d3be

## Summary

This branch completes milestone 1 of the Codex compatibility roadmap (issue #434). Codex now gets the same `SKILL.md` routing descriptions as Claude Code and OpenCode. Previously, the generator overwrote them with catalog summaries. All 61 canonical descriptions are rewritten as short routing descriptions, so the full catalog fits Codex's discovery budget. Two new deterministic checks back the change: rule 16b checks that generated skills are byte-identical to their sources, and rule 17 models Codex's full inventory lines against its budget. The branch also documents a cross-harness adapter contract, declares skill dependencies and validates those declarations, corrects the Codex install and hook-trust guidance, and records a dated baseline and verification in the Codex consumption review.

## Changes by Area

**Codex distribution generator.** `bin/build-codex-marketplace` no longer rewrites skill descriptions. `rewrite_skill_description` and `plugin_description` are removed, and a header comment explains that skills are copied unchanged.

- `bin/build-codex-marketplace`

**Plugin validation.** The new rule 16b compares every generated `dist/codex` `SKILL.md` byte for byte with its canonical source and reports orphaned generated skills. Rule 17 is rewritten. It renders each skill as Codex's `- plugin:skill: description (file: path)` line, charges `ceil(bytes / 4)` tokens per line, and fails above 2 percent of the reference model's 272,000-token window less a 600-token system-skill reserve. When the context window is empty, it falls back to 8,000 characters. The old repository-invented 12,000-character limit is gone. Per-description checks run on canonical copies: empty name or description, the 1,024-character error, and a 150-character warning.

- `bin/validate-plugins`, `Makefile` (unsets the two new override variables for scrut)

**Skill dependency checking.** `bin/check-cross-references` now parses `## Skill dependencies` sections. Every "Invoke the `NAME` skill" in a `SKILL.md` or its references must be declared there. Each declaration must follow the documented form, resolve to a canonical skill, appear in one category only and exactly once, and be used outside the section. Ignore-comment guidance now appears only for errors an ignore comment can fix.

- `bin/check-cross-references`

**Tests and fixtures.** The cross-reference fixture gains a second skill so declarations can resolve. The validator fixture copies `docs/` and adds six scenarios: an oversized description, a long description, a rewriting generator, aggregate overflow, path overhead, and the fallback. Scrut coverage is added for each.

- `tests/fixtures/cross-reference-fixture`, `tests/fixtures/validate-plugin-fixture`, `tests/scrut/check-cross-references.md`, `tests/scrut/repo-tooling.md`

**Routing descriptions.** All 61 canonical `SKILL.md` descriptions are rewritten to 150 characters or fewer. Each opens with the primary action, keeps distinguishing trigger phrases, and adds a negative boundary where a neighboring skill would otherwise compete. Together they total 8,673 characters, down from 33,758.

- `plugins/*/skills/*/SKILL.md` (61 files)

**Skill dependency declarations.** Thirteen skills declare required and optional dependencies. Composition phrasing is normalized to "Invoke the `NAME` skill", and references to Claude's Skill tool are removed. `bootstrap-project` and `refresh-project-scaffolding` declare their selection-driven candidates as optional.

- `bootstrap-project`, `merge-main`, `monitor-pr`, `pin-everything`, `pr`, `rebase-onto-main`, `refresh-project-scaffolding`, `resolve-copilot-pr-feedback`, `review-dependabot-config`, `set-up-linters`, `triage-dependabot-prs`, `upgrade-everything`, `write-lean-code`

**Authoring guidance.** `docs/plugin-development.md` gains two sections:

- "Routing descriptions and catalog summaries" separates ownership of the two kinds of description.
- "Cross-harness workflow adapters" covers invocation, composition, dependencies, capabilities, authority, and continuation, each with copyable templates.

`create-plugin` teaches the same conventions. Copilot review instructions now tell Copilot not to lengthen routing descriptions.

- `docs/plugin-development.md`, `plugins/create-plugin/skills/create-plugin/SKILL.md`, `plugins/create-plugin/skills/create-plugin/references/skill-md.md`, `.github/copilot-instructions.md`

**User documentation.** The root README treats registering the marketplace and installing plugins as separate steps, adds selective installation, refresh, and troubleshooting guidance, replaces the removed `plugin_hooks` flag with `/hooks` review and trust, and rewrites the known limitations with links to later milestones. The `notify` README gets matching corrections.

- `README.md`, `plugins/notify/README.md`

**Evidence and planning.** The Codex consumption review gains a dated milestone 1 baseline. It labels each claim as observed, documented, or upstream source, and records the validation constants, the verification (smoke checks, hook trust, Claude Code and OpenCode checks), and each affected finding's disposition. The roadmap checks off milestone 1, and the implementation plan is committed directly in `docs/plans/done/`.

- `docs/reviews/codex-consumption.md`, `docs/plans/todo/2026-09-15-codex-consumption-improvements.md`, `docs/plans/done/2026-09-18-finish-codex-compatibility-milestone-1.md`

**Versions and generated mirrors.** All 62 plugins are bumped once relative to `main`. `create-plugin` takes a minor bump (1.2.13 to 1.3.0); every other plugin takes a patch bump, and `notify`'s Codex manifest stays in step at 2.3.1. `dist/codex` is regenerated (126 files).

## File Inventory

- **New files (1):** `docs/plans/done/2026-09-18-finish-codex-compatibility-milestone-1.md`
- **Modified files (265):** 14 repository files (`.github/copilot-instructions.md`, `Makefile`, `README.md`, 3 under `bin/`, 4 under `docs/`, 4 under `tests/`), 63 plugin manifests, 61 `SKILL.md` files, `create-plugin`'s `references/skill-md.md`, `plugins/notify/README.md`, and 126 generated files under `dist/codex/`
- **Deleted files:** none
- **Renamed files:** none

## Notable Changes

- **Codex routing behavior changes for every skill.** Codex consumers now route on different descriptions for all 61 skills. The version bumps signal this, but selection accuracy is unmeasured until milestone 2.
- **New validation gates.** Rule 16b and the rewritten rule 17 can fail CI for reasons that did not exist before: generator drift, and catalog size including names and paths. Rule 17 also prints a summary line on every run, and scrut snapshots now expect it.
- **New authoring contract.** Every future composing skill must carry a well-formed `## Skill dependencies` section, or `bin/check-cross-references` fails.
- **No dependency, CI workflow, or security-relevant changes.** CI needs no change for the new override variables, because the runner never sets them.

## Plan Compliance

Plan: `docs/plans/done/2026-09-18-finish-codex-compatibility-milestone-1.md`

**Compliance verdict: good compliance.** Every implementation step, validation step, and acceptance criterion has a matching change or recorded evidence. The deviations are small, evidence-driven, and documented where they happen. The remaining concerns are about how durable the result is, not about missing work.

**Overall progress:** 27/27 items done (100%).

### Step 1: Capture the supported baseline

- **Done:** Dated baseline in the review. It covers the commit, `codex --version`, plugin and marketplace help, the feature rows, documentation links, the upstream renderer revision, hook events and trust, the reference model and window, name and path forms, the framing and system skills, refresh behavior for Git and local-path marketplaces, the differences from the audit, and the limits of what was inspected.
- **Done:** Root README install, management, hook-trust, troubleshooting, and limitations rewrite. The `install`, `using-with-codex-cli`, and `codex-cli-known-limitations` anchors are preserved, and the new milestone links resolve to the roadmap headings.
- **Done:** `notify` README correction, with a patch bump and the Codex manifest in step.

### Step 2: Publish the adapter authoring contract

- **Done:** The "Cross-harness workflow adapters" section, with all five areas and every example the plan names, including the skipped selection-driven candidate and continuation status.
- **Done:** `create-plugin` reference, workflow step, and checklist updates, with the minor bump.

### Step 3: Declare and validate skill dependencies

- **Done:** A fresh composition search. It found compositions beyond the plan's inventory (`set-up-linters`, `write-lean-code`, `pin-everything`'s `manage-repo-licensing`, `upgrade-everything`'s `triage-dependabot-prs`, and `refresh-project-scaffolding`'s `clean-up-agent-config` and `optimize-runner-usage`) and normalized them to the canonical phrase.
- **Done:** Dependency blocks in 13 skills, with patch bumps.
- **Done:** Preflight and missing-dependency behavior in the adapter contract.
- **Done:** Checker extensions: resolution, both-category, undeclared, unused, form, and repeat checks. The prefilter is widened, and the cross-references section of the guide describes the new checks.
- **Done:** Fixture and scrut cases for missing, unused, repeated, unresolved, and malformed declarations, a selection-driven optional candidate, and exempt mentions. Caveat: the `duplicate-section` error has no scrut case (see Code Quality).

### Step 4: Replace the compatibility budget check

- **Done:** Rule 17 refactor, removal of `CODEX_SKILL_DESCRIPTION_BUDGET`, and a rewritten header comment.
- **Done:** Name and description checks, the 1,024-character error, the warning threshold, primary and fallback gates, and diagnostics that report the total, budget, reserve, largest entries, and remedy. Caveat: the new empty-name check has no scrut case.
- **Done:** The five scenarios the plan names, all exercised through overrides. The path-overhead case asserts its own premise instead of hard-coding totals.

### Step 5: Tighten canonical routing descriptions

- **Done:** All 61 descriptions are at or under 150 characters, and the catalog costs 4,689 of 4,840 tokens.

### Step 6: Preserve routing descriptions in the Codex distribution

- **Done:** The generator copies skills unchanged.
- **Done:** Rule 16b byte-identity check, plus an orphan check the plan did not require.
- **Done:** Bumps, README, guide, and `create-plugin` wording corrections, and regenerated mirrors. `make build` leaves the tree clean.

### Step 7: Close milestone 1 with evidence

- **Done:** Roadmap checklist.
- **Done:** Dispositions for all 13 named findings (1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 17, and 20), each marked resolved, contract established with adoption pending, or deferred.
- **Done:** Issue #434. The public issue shows milestone 1 checked, and its document links point to `main`.
- **Done:** Plan moved to `docs/plans/done/`.

### Validation

- **Done:** `make test-all`. Reproduced for this review: lint and `make validate` pass, and scrut passes 458 of 458 cases.
- **Done:** `make build` with a clean `git status`. Reproduced.
- **Done:** Isolated Codex smoke checks, recorded with redacted paths and no copied credentials.
- **Done:** One explicit `$commit` invocation and one natural-language activation, both recorded as informational.
- **Done:** Claude Code loading and OpenCode mirror checks, recorded.
- **Done:** `check-versions`, recorded. An independent check for this review agrees: 62 of 62 changed plugins are bumped exactly once.

### Deviations

- **CLI `0.155.1` instead of the anticipated `0.155.0`.** Reasonable. The baseline records the discrepancy, and the support policy targets current stable rather than a fixed version.
- **The reserve covers bundled system skills only, not usage-instruction framing.** Reasonable. The upstream renderer shows framing is outside the budget, and the validation constants table records this as "None".
- **Extra commits.** `6e630013` (a validator fixture fix) and `9331d3be` (a stale comment count) fall outside the seven planned boundaries. The `6e630013` message says the fixture needed `docs/` because of the `create-plugin` references added in `ac7a4b8d`. So `ac7a4b8d` probably does not pass the scrut suite on its own, even though the plan asked for each commit to validate independently. This is minor, and it cannot be corrected without rewriting history, which repository policy forbids.
- **Scope additions.** These are the Copilot instruction bullet, the `Makefile` unset of the override variables, rule 16b's orphan check, and the troubleshooting list. All are justified and small.

### Fidelity concerns

- **The budget fits, but narrowly.** The plan's criterion ("passes the 2 percent budget") is met with 151 tokens to spare, about 3 percent of the available budget. Plugin lines average about 77 tokens, so roughly two more skills fit before rule 17 fails. The plan's intent that routing descriptions be preserved within budget holds today, but the next plugin addition will likely force tightening elsewhere (see Code Quality, issue 1).
- **Some optional classifications are not yet backed by the documented fallback.** `merge-main` and `rebase-onto-main` declare `commit` as optional, which is defensible because Stash and Abort remain available. Their bodies, though, still offer "Commit first" unconditionally, with no instruction for when `commit` is not installed. The adapter contract says an optional dependency "follows its documented fallback". The plan explicitly leaves workflow-body adoption to milestone 2, so this is a carry-forward item, not a milestone 1 gap. Milestone 2 should close it for the Git chain.

## Code Quality Assessment

**Overall quality: ready to merge.** The tooling is careful and well tested, and its constants trace to recorded evidence. The documentation separates observation, documentation, and upstream source cleanly. Nothing found blocks merging. The items below are low to moderate and can land as follow-ups, or in this branch where noted.

### Strengths

- **Rule 16b turns generator drift into a hard failure.** The `rewriting-generator` scenario proves rule 16 alone would have passed, which is exactly the regression this milestone removes.
- **Rule 17 mirrors the upstream renderer closely.** It charges `ceil(bytes / 4)` per line including the newline, truncates to 1,021 characters plus `...`, uses a fixed-length home placeholder so results do not depend on the machine, and counts characters the same way under any locale by stripping UTF-8 continuation bytes. Every constant is explained next to its definition and in the review.
- **The tests stay stable as the catalog changes.** The path-overhead case computes its premise from the diagnostic and fails loudly if the premise stops holding. The inventory summary is matched by glob, so ordinary content changes do not churn snapshots.
- **The dependency parser is precise.** It skips frontmatter and fenced code, so documented examples do not count as declarations. It excludes the section from the "used" search and reports actionable, specific messages. Only reference errors get the ignore-comment notice, so dependency errors do not suggest a remedy that cannot work.
- **The generated tree stays consistent.** `make build` leaves the tree clean, and all 62 plugins carry exactly one bump at the correct level.

### Issues to address

1. **Budget headroom is thin, and the contributor path does not mention it (moderate).** At 4,689 of 4,840 tokens, adding about two average skills will fail rule 17. Each line also embeds the plugin version in its cache path, so a version that gains a digit (for example `1.9.9` to `1.10.0`) grows the line. That cannot tip the catalog over on its own at today's headroom, but it means the validation result depends on version numbers. The "Adding a plugin" section of `docs/plugin-development.md` never mentions the budget, so the first contributor to hit the failure meets it mid-change. At minimum, add a step there: read the rule 17 summary line, and if the catalog is over budget, tighten the largest routing descriptions. That is the remedy the diagnostic already prints.
2. **Two new error paths have no tests (low).** `check-cross-references`'s `duplicate-section` error ("has more than one ## Skill dependencies section") and `validate-plugins`' new empty-`name` check have no scrut cases. Add one case to each suite.
3. **A user-facing suggestion uses the composition phrase (low).** `plugins/optimize-runner-usage/skills/optimize-runner-usage/SKILL.md` lines 22 and 26 tell the user: "Invoke the set-up-ci skill to create a CI workflow…". The new guide says suggestions must not be phrased as "Invoke the … skill". The checker misses this only because the name is not backticked. `optimize-runner-usage` is already patch-bumped on this branch (1.2.3), so rewording to "Use the `set-up-ci` skill…" needs no additional bump.

### Suggestions

- **Catch near-miss composition phrasing.** The checker recognizes only the exact canonical phrase. `set-up-linters`' former "invoke `lint-and-fix`" would have escaped it, and this branch caught that one by manual search. A warning for "invoke `name`" forms that are not the canonical phrase would catch future drift without making the convention stricter.
- **Revisit the reserve when the system skills change.** The validation constants say to revisit only when the reference model changes. The 600-token reserve depends on Codex's bundled system skills (567 tokens observed), which can change in a CLI release without any model change. Name that as a second revisit trigger in the review and the rule 17 comment.
- **Track trigger coverage lost to shortening.** Some capabilities no longer appear in routing text. Examples: `suggest-next-issue`'s parallel-work and exclusive-resource questions, `monitor-pr`'s "watch the pr" and "keep an eye on the pr", and `create-worktree`'s "who has the DAW". This was the milestone's deliberate trade-off. Milestone 2's activation evaluation should include a few of these phrasings, so any lost routing is measured rather than assumed.
