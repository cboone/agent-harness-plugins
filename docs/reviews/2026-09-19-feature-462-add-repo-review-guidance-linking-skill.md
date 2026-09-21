# Branch Review: feature/462-add-repo-review-guidance-linking-skill

Base: main (merge base: 136cf555)
Commits: 14
Files changed: 111 (48 added, 63 modified, 0 deleted, 0 renamed)
Reviewed through: e74e53fd

Line references are pinned to `e74e53fd`. `origin/main` was at `f68b9a3f` when this review was written.

## Summary

This branch adds `set-up-review-config`, a skill that detects a repository's file types and installs condensed style-guide review checklists for three automated reviewers: a Copilot `.github/skills/code-review/` skill, a `## Code Review Rules` block in `AGENTS.md` for Codex, and a `REVIEW.md` block for Claude Code Review. Seven style guides gain a hand-written `references/review-checklist.md`, which the new `bin/build-review-checklists` copies byte for byte into the new plugin during `make build`, and validator rule 20 keeps those copies current. `bootstrap-project`, `refresh-project-scaffolding`, `clean-up-agent-config` and `create-plugin` are updated to run, audit, preserve and document the new config. The Copilot layout was validated up front on a live test PR (cboone/gh-problemas#18), where Copilot cited checklist rules by name.

On its own merge base the branch is green: `make lint`, `make validate` and all 479 scrut testcases pass, and `make build` in a clean clone produces no drift. It is, however, behind `main` by PR #468 (Codex compatibility milestone 1). A trial merge conflicts in 24 files, and once resolved, `make validate` fails with two errors caused by this branch. See Issues to address.

## Changes by Area

### New plugin: `set-up-review-config`

The skill runs an eight-step workflow (check the repository, detect file types, detect CI checks and skip paths, resolve pinned links, present the plan, write, validate, report) with a `--dry-run` option that stops at the plan. `references/guides.md` holds per-guide detection and routing rules, including the shebang rule and Pandoc-academic exclusions. Three fenced templates define the entry skill, the `AGENTS.md` section and `REVIEW.md`. Managed content is marked with `BEGIN`/`END` HTML comment blocks or a managed first line on whole files.

- `plugins/set-up-review-config/.claude-plugin/plugin.json`
- `plugins/set-up-review-config/README.md`
- `plugins/set-up-review-config/skills/set-up-review-config/SKILL.md`
- `plugins/set-up-review-config/skills/set-up-review-config/references/{guides,code-review-skill,agents-md-section,review-md}.md`
- `plugins/set-up-review-config/skills/set-up-review-config/references/checklists/*.md` (7 generated copies)

### Style-guide review checklists

Each of the seven core guides gains a `references/review-checklist.md` with `## Important`, `## Nits` and `## Do not flag` sections, and every item has a bold, citable rule name. Each `SKILL.md` gains a `## Pull Request Review` pointer to it. All are minor version bumps.

- `plugins/write-{go-code,lean-code,lean-tests,bash-scripts,zsh-scripts,markdown,scrut-tests}/skills/*/references/review-checklist.md`
- The matching `SKILL.md` and `.claude-plugin/plugin.json` files

### Build, validation and CI

`bin/build-review-checklists` checks every source before writing: H1, section order, bold rule names, no relative links, no `./references/` paths, no plugin-root placeholder, no validator directives, no fences or tables, and a 5,000-byte cap. It then copies the checklists and removes orphaned copies. Rule 20 in `bin/validate-plugins` regenerates into a temporary directory and reports missing, stale, orphaned and unlisted copies. `make build` and CI's "Validate generated mirrors" step run the generator first.

- `bin/build-review-checklists`
- `bin/validate-plugins`
- `Makefile`
- `.github/workflows/ci.yml`

### Orchestrator and companion skills

`bootstrap-project` (1.5.0) adds the new skill to its infrastructure table, overlap rules, execution order, example plan and next steps. `refresh-project-scaffolding` (2.2.0) adds a signature, an update strategy and a "Review Config Checks" reference section, and it delegates content currency to `set-up-review-config --dry-run`. `clean-up-agent-config` (1.3.1) recognizes `REVIEW.md` and `.github/skills/code-review/` and never moves or deduplicates managed content. `create-plugin` (1.2.14) points its mirror step at `make build`.

- `plugins/bootstrap-project/**`
- `plugins/refresh-project-scaffolding/**`
- `plugins/clean-up-agent-config/**`
- `plugins/create-plugin/**`

### Tests

A new scrut suite covers the generator with 23 testcases against a throwaway plugin tree: copying, orphan removal, idempotence, the directory override, every validation error with its exit code, a failing run leaving copies untouched, and a non-vacuous check that the real repository's copies match. Four new validator-fixture scenarios cover stale, orphaned, unlisted and invalid checklists, each producing exactly the rule 20 error.

- `tests/scrut/build-review-checklists.md`
- `tests/fixtures/review-checklist-fixture`
- `tests/scrut/repo-tooling.md`
- `tests/fixtures/validate-plugin-fixture`

### Repository documentation and review guidance

The root `AGENTS.md`, `plugins/AGENTS.md` and `bin/AGENTS.md` gain the "never hand-edit the copies" constraint and the double-bump rule. `docs/plugin-development.md` gains a "Review checklists" section. A new Copilot instructions file covers this repository's own reviews of checklists.

- `AGENTS.md`, `plugins/AGENTS.md`, `bin/AGENTS.md`
- `docs/plugin-development.md`
- `.github/copilot-instructions.md`
- `.github/instructions/review-checklists.instructions.md`
- `README.md`, marketplace files and the plan

### Generated mirrors

Regenerated Codex mirrors for every changed plugin, plus the OpenCode symlink for the new skill.

- `.agents/plugins/marketplace.json`
- `dist/codex/plugins/**` (46 files)
- `dist/opencode/skills/set-up-review-config`

## File Inventory

**New files (48):** 26 canonical and 22 generated.

- Canonical: the plan; `bin/build-review-checklists`; `.github/instructions/review-checklists.instructions.md`; 7 source checklists; 14 files under `plugins/set-up-review-config/` (manifest, README, `SKILL.md`, 4 references, 7 generated copies); `tests/fixtures/review-checklist-fixture`; `tests/scrut/build-review-checklists.md`
- Generated: 14 files under `dist/codex/plugins/set-up-review-config/`, 7 checklist mirrors under `dist/codex/plugins/write-*/`, and `dist/opencode/skills/set-up-review-config`

**Modified files (63):** 2 marketplace files, `.github/copilot-instructions.md`, `.github/workflows/ci.yml`, `AGENTS.md`, `Makefile`, `README.md`, `bin/AGENTS.md`, `bin/validate-plugins`, `docs/plugin-development.md`, `plugins/AGENTS.md`, 11 plugins' manifests and skill or README files (with their Codex mirrors), `tests/fixtures/validate-plugin-fixture` and `tests/scrut/repo-tooling.md`.

**Deleted files:** none. **Renamed files:** none.

## Notable Changes

- **New merge gate**: validator rule 20 fails the build on stale, missing, orphaned or unlisted checklist copies.
- **Build pipeline order**: `make build` now runs three generators, and the checklist generator must precede the Codex mirror because the mirror copies `plugins/`.
- **CI**: the drift check now also covers `plugins/set-up-review-config/.../references/checklists/`, and the scrut environment gains two binaries.
- **Coupled versioning**: editing a source checklist now requires forward bumps in two plugins. This is documented in `docs/plugin-development.md` and `plugins/AGENTS.md`.
- **Network use in the skill**: the skill runs `git ls-remote` and fetches from `raw.githubusercontent.com` with `curl` against this marketplace. Both are optional, and the skill falls back to `unpinned`.

## Plan Compliance

Plan: `docs/plans/todo/2026-09-19-add-set-up-review-config-plugin.md`. It is the only plan on the branch and tracks #462. Its file name does not match the branch name, which is harmless.

**Verdict: good compliance.** Every design and implementation item is present and closely follows the plan's specified approach, including the step 0 gate, which was run and recorded before the layout was committed to. The remaining gaps are small: one README section the plan asked for is missing, and three verification or bookkeeping steps are unrecorded or depend on the PR. The plan's integration assumptions (rule 17's meaning, version baselines) have been overtaken by `main`, which is a fidelity concern rather than a compliance gap on the branch as written.

**Overall progress: 29/34 items done (85%)**, 4 partially done, 1 not verifiable from the branch.

### Done

- **Step 0**: the Copilot layout was confirmed on cboone/gh-problemas#18 and the result recorded in the plan. The fallback was correctly not built.
- **Review checklist format**: all seven checklists follow the H1, coverage line, three-section, bold-name structure; none has fences, tables or relative links; the largest is 4,396 bytes against the 5,000 cap. Script-only rules (strict mode) say so.
- **Target output, entry skill**: `code-review-skill.md` matches every listed reporting rule (changed lines only, citation format, Important blocks, five-Nit cap, CI and skip lists, precedence) and the hand-written `SKILL.md` handling.
- **Target output, checklist files**: managed first line with guide and pin, blank line, verbatim body; unmarked files are never overwritten.
- **Target output, `AGENTS.md`**: a block at the end of `## Code Review Rules`, symlink handling, ask-before-create with `/clean-up-agent-config`, and legacy-heading and nested-file reporting.
- **Target output, `REVIEW.md`**: inlined Important rules, a Nit cap with "plus N similar items", Important-only after the first review, and do-not-report lists.
- **Target output, marker rules**: blank lines inside markers; unbalanced markers stop the run (see the wording nit below).
- **Plugin manifest and catalog**: `1.0.0`, placed between `set-up-linters` and `set-up-secret-scanning`, with a 199-character description.
- **`SKILL.md` workflow**: all eight steps and `--dry-run` as specified.
- **`references/guides.md`**: all detection rules, including the `env -S` shebang forms, `#compdef`/`#autoload`, POSIX `sh` as unsupported, scrut exclusion from Markdown, and Pandoc signals. Each copy is named by its concrete path.
- **Templates**: in fenced blocks, none named `SKILL.md`.
- **Generated `checklists/`**: never hand-edited; rule 20 and CI enforce it.
- **No slash-form `code-review` references**: validation passes.
- **Generator**: sources, `LC_ALL=C`, exit 2 without `plugins/`, validate-all-before-write, byte-identical copies, orphan removal, `REVIEW_CHECKLISTS_DIR` override and unsafe-path refusal.
- **Makefile**: `build` order and `help` text.
- **Rule 20**: temporary regeneration, per-copy errors, relayed generator errors, the `guides.md` listing check, and "run make build" messages.
- **CI**: the generator in the mirror step and the extended `git status --porcelain` paths.
- **Double-bump documentation**: in `docs/plugin-development.md` and `plugins/AGENTS.md`.
- **Style guides**: all seven, at exactly the planned versions, with `SKILL.md` pointers.
- **`bootstrap-project` 1.5.0**: every listed touchpoint, including the renumbered example plan and the `overlap-rules.md` section and row.
- **`refresh-project-scaffolding` 2.2.0**: signature, strategy row, order, skill list and reference section, with content currency delegated to `--dry-run` as designed.
- **`clean-up-agent-config` 1.3.1**: target structure, "what goes where", audit list, and managed-content exemptions.
- **`create-plugin` 1.2.14**: `make build` and the review-checklist bullet.
- **Repository docs**: root, `plugins/` and `bin/` `AGENTS.md`, `docs/plugin-development.md`, and the new Copilot instructions file, listed in `copilot-instructions.md`.
- **Generator scrut suite**: every listed case, plus extra cases for non-Markdown files, the self-exclusion and absolute URLs.
- **Validator scenarios**: stale, orphan and unlisted, each producing exactly the rule 20 error and exit 1.
- **Environment registration**: `SCRUT_ENV`, `scrut-env` and `SCRUT_UNSET`.
- **Commits**: the ten planned commits in order, plus four follow-up `fix:`/`docs:` commits, all ending in `(#462)` and all carrying signatures.
- **Lean library acceptance**: run against `zhang-yeung-inequality` and recorded, including the spell-checker finding that led to a skill change.

### Partially done

- **Plugin README**: it has the verbatim paragraph, Requirements, Usage, Examples and See Also, but no Recommended Permissions JSON, which the plan lists. The root README row and External tools bullet are done.
- **Mechanical verification**: `make test-all` passes on the branch as written (verified in this review). The `check-versions` run before the PR is still to do, and it will fail after `main` is merged (see Issues to address).
- **Go CLI acceptance**: the plan records no result for this run. The Copilot acceptance used "the generated Go output", which implies it ran, but the expected guide set, the CI tools, the `go.sum` skip and the zero-change rerun are not recorded.
- **Copilot citation**: the result is recorded in the plan and the test PR is closed. Recording it in this repository's PR description waits for the PR.

### Not verifiable from the branch

- **Follow-up issue** for the seven remaining guides: nothing in the diff references a filed issue. It may exist; confirm it before the PR and consider naming it in the plan.

### Deviations

- **Generator does not check the backticked slash-word construct** (approach deviation). The plan lists it among the constructs the generator rejects; instead, `docs/plugin-development.md` says rule 19 catches it. **Reasonable**: rule 19 already owns cross-reference parsing, and duplicating it would drift.
- **Generator adds a bold-rule-name check** (scope addition). **Justified**: citation by rule name is the design's core, and the check is tested.
- **`invalid-review-checklist` validator scenario** (scope addition). **Justified**: it proves generator errors are relayed rather than masked.
- **Spell-checker handling in step 7, and the refined Pandoc citation signal** (scope additions from the Lean acceptance run). **Justified** and recorded in the plan.
- **Lean acceptance target changed** from `shannon-entropy` to `zhang-yeung-inequality`, because the former is a fork. **Reasonable**, and consistent with the fork policy.
- **Recommended Permissions omitted from the README** (omission). **Minor**, and 34 of 63 plugin READMEs, including the other `set-up-*` plugins, also lack the section, so it does not break a firm convention. The plan did ask for it, though.

### Fidelity concerns

- **The plan's constraints predate `main`'s Codex milestone.** The plan sizes the description against "rule 17 warns above 320", which is about the catalog description. On `main`, rule 17 is now the Codex skill-inventory budget, and the Codex mirror now keeps each skill's full `SKILL.md` routing description. The new skill's 846-character routing description is the largest in the inventory and pushes it over budget. The implementation is faithful to the plan, but the plan's target has moved.
- **Version baselines have moved.** The plan's versions were correct against the merge base, but two now collide with `main`.

## Code Quality Assessment

**Overall quality: high, but not mergeable until it is brought up to date with `main`.** The design is careful and the tooling is well built. Once `main` is merged, the branch fails validation for reasons it must fix itself, and two version numbers need to move.

### Strengths

- **Evidence-first design.** Step 0 validated the riskiest assumption (Copilot reading sibling files) on a live PR before any plugin work, and the acceptance runs fed real fixes back into the skill (spell checkers, Pandoc detection).
- **Generator robustness.** It validates every source before writing, so a bad source never half-updates the copies. It is locale-stable (`LC_ALL=C`), Bash 3.2-safe (`${sources[@]+"${sources[@]}"}`), refuses unsafe output paths, and leaves non-Markdown files alone. `bin/build-review-checklists:12-16` explains why each check exists.
- **A validator rule that cannot be fooled by rule 16.** Rule 20 regenerates independently. The comment at `bin/validate-plugins:218-226` explains why rule 16 cannot see stale copies (it mirrors whatever `plugins/` holds).
- **Tests that pin behavior, not just success.** Every error message and exit code is asserted; the failing-run case proves that nothing is written or removed; the real-repository check guards against a vacuous pass with a source count.
- **Idempotent, ownership-aware skill design.** Managed blocks, marked whole files, "rules outside the block take precedence", pins kept on unchanged bodies, and an explicit zero-change rerun in step 7 make reruns safe in repositories the user also edits.
- **Checklist content.** The seven checklists are condensed, derived from their guides, correctly severity-ranked, and exclude formatter-enforced rules through "Do not flag" rather than per item.

### Issues to address

1. **Merge `main` and fix the two validation failures it exposes (blocking).** A trial merge of `origin/main` (`f68b9a3f`) into a scratch clone conflicts in 24 files: `Makefile`, `tests/fixtures/validate-plugin-fixture`, `plugins/refresh-project-scaffolding/skills/refresh-project-scaffolding/SKILL.md`, 20 plugin manifests (10 plugins and their Codex mirrors), and the Codex mirror of the refresh skill. All are mechanical. After resolving them and running `make build`, `make validate` fails:
   - **Codex skill inventory over budget.** "Codex skill inventory costs 4945 tokens, over the 4840 available". `set-up-review-config` is the largest entry at 256 tokens, with an 846-character routing description (`plugins/set-up-review-config/skills/set-up-review-config/SKILL.md:3-15`) against a guideline of about 150. Tighten it to roughly the length of its peers: keep the trigger phrases and drop the reviewer-by-reviewer explanation and the "Pairs with" sentence.
   - **Undeclared skill dependency.** `refresh-project-scaffolding/SKILL.md` "invokes the set-up-review-config skill" (lines 81 and 138) but does not declare it under `## Skill dependencies`, which `main` now requires. Add it to the `- **Optional:**` list. Add it to `bootstrap-project`'s Optional list as well: the validator does not flag that skill because its invocation list does not use the canonical phrase, but `main`'s convention is to declare every composed skill, and `bootstrap-project` declares all its other candidates.

   With both fixed, the 18 `repo-tooling.md` scrut failures in the merged tree, which all come from `bin/validate-plugins` failing, should clear.

1. **Fix two version collisions after the merge (blocking).**
   - `clean-up-agent-config` is `1.3.1` on both `main` and this branch (`plugins/clean-up-agent-config/.claude-plugin/plugin.json:12`). The merge resolves silently to `1.3.1`, reusing a version `main` already shipped with different content. Bump it to `1.3.2`.
   - `create-plugin` is `1.2.14` here but `1.3.0` on `main` (`plugins/create-plugin/.claude-plugin/plugin.json:12`). Taking this branch's side would move the version backwards. Use `1.3.1`.

   The other nine bumps stay ahead of `main`'s patch bumps. Run the `check-versions` skill after the merge.

1. **Decouple the `unlisted-review-checklist` scenario from `write-latex` (medium).** `tests/fixtures/validate-plugin-fixture:51` copies a checklist into `plugins/write-latex/...` to simulate a guide with no `guides.md` entry. `write-latex` is the first guide in the follow-up issue. Once it gets a real checklist and a `guides.md` entry, this scenario will overwrite a real source, stop producing the expected error, and fail for an unrelated reason. Create a synthetic plugin directory, such as `plugins/write-fixture-guide/skills/write-fixture-guide/references/`, instead.

1. **Define the "user declines `AGENTS.md`" path (low).** `SKILL.md:49` asks before creating `AGENTS.md` when only a regular `CLAUDE.md` exists, but nothing says what happens on "no". Meanwhile `refresh-project-scaffolding/SKILL.md:522` requires each of the three instruction files to hold exactly one block, so a repository that declined will fail the audit on every refresh, and the dry run will keep proposing the file. State that a declined `AGENTS.md` skips the Codex block and is reported, and make the refresh check apply only to files that exist or were installed.

1. **Tighten the marker-balance wording in step 1 (low).** `SKILL.md:46` stops on "more than one of either, or an END before its BEGIN", which does not name a `BEGIN` without an `END`, or an `END` alone. Error Handling says "unbalanced", so the intent is clear, but step 1 is where an agent looks. Suggested wording: "stop unless the file has no markers, or exactly one BEGIN line followed later by exactly one END line."

1. **Reword the no-CI replacement line in `REVIEW.md` (low).** `references/review-md.md:55` replaces the CI bullet, which sits under `## Do not report`, with "Formatting and lint findings are Nits.", so a do-not-report list ends up containing a statement about what to report. Move that sentence out of the list when CI runs no checks, or phrase the bullet so it fits under the heading.

### Suggestions

- **Widen the generator's standalone checks.** The relative-link check (`bin/build-review-checklists:100-102`) matches only inline `](...)` links, so a reference-style definition such as `[guide]: ../SKILL.md` passes. The table check (line 106) needs a leading pipe, so a pipe-less GFM table passes. Neither occurs today; both are one-line additions with a scrut case each.
- **Guard the output-directory override against broad targets.** With `REVIEW_CHECKLISTS_DIR` set, orphan removal deletes every `*.md` in that directory that is not a current guide name (`bin/build-review-checklists:136-145`), so `REVIEW_CHECKLISTS_DIR=docs` would delete Markdown in `docs/`. Only `/`, `.`, `..` and their slash forms are refused (lines 157-163). This is a developer-only variable, and rule 20 always passes a fresh `mktemp -d`, so the risk is low. Refusing an existing directory that holds non-`write-*.md` Markdown, or requiring the override directory to be empty, would close it.
- **Name the `lakefile.lean` forms in Lean-tests detection.** `references/guides.md:31` names the TOML `testDriver = "NAMETest"` form only. The `lean_lib` name fallback covers `lakefile.lean`, but naming `testDriver := "..."` and `@[test_driver]` would make detection explicit.
- **Consider skipping the installed checklists in review.** `.github/skills/code-review/*.md` files are Markdown and fall under the `**/*.md` route, so a PR that updates the config has the Markdown checklist applied to managed, verbatim files. Copilot flagged nothing there in acceptance, so this is optional, but adding the managed files to SKIP-PATHS would prevent noise when a checklist is reworded.
- **Record the Go CLI acceptance result** in the plan, in the same form as the step 0 and Copilot results, so the verification section is complete before the PR.
