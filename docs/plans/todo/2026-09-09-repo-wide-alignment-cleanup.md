# Repo-wide alignment cleanup

## Context

The repository has absorbed a lot of change recently (#309, #322, #323/#326, #324, #328, plus the Prettier config fix in `36de9ce`). Several of those efforts landed partially, and one piece of scheduled tooling has been failing silently for months. This plan is the result of a full read-only audit across the catalog, the generated mirrors, CI, the build scripts, and all 51 plugins' skill content.

**What is already healthy** (verified, no work needed):

- 51 plugin directories map 1:1 onto 51 `marketplace.json` entries. Every `version`, `description`, `name`, `author`, `keywords`, `homepage`, `license`, and `repository` field is byte-identical between each `plugin.json` and its marketplace entry.
- `metadata.version` is correct: `bin/compute-catalog-state` emits `catalog-M63-m83-p142-n51`, matching the committed value. `release.yml` still consumes that format correctly.
- All 51 root-README "What it does" cells are byte-identical to the canonical marketplace descriptions.
- The generated trees are genuinely in sync. `dist/codex/`, `dist/opencode/`, and `.agents/plugins/marketplace.json` show zero content drift from source.
- Every "See Also" and "Pairs with" cross-reference resolves. No skill references a removed or renamed plugin.

The problems are elsewhere: a dead audit job, corrupted command examples shipped to users, a validator that checks the wrong copy of a file, doc drift, and conventions that contradict each other between skills.

**Intended outcome**: every surface in the repo agrees with every other surface, the weekly audit works again, and the conventions the skills teach are the conventions the skills follow.

---

## Phase 1: Correctness bugs

### 1.1 `bin/version-audit` has failed every scheduled run for 12+ weeks

`gh run list --workflow=version-audit.yml` shows `failure` for every run back to at least 2026-06-22. Two independent causes in `bin/version-audit`:

- **crates.io rejects the default curl User-Agent.** `crates_io_latest` (`bin/version-audit:167-170`) calls the crates.io API with no `User-Agent` header. crates.io's crawler policy returns **HTTP 403**, and `curl -f` turns that into exit 56. Verified directly against `shellharden`, `cargo-deny`, `typos-cli`, `cargo-nextest`, and `taplo` — all 403.
- **`set -euo pipefail` aborts before the report prints.** `crates_io_latest`, `npm_latest` (`:106-109`), and `pypi_latest` (`:193-196`) are bare `curl | jq` pipelines assigned via command substitution, with no `|| true`. Under `set -e` a failing lookup terminates the whole script, so the `if [[ -z "${latest}" ]]` guards that were clearly written to handle failure can never be reached. `github_latest_release` (`:28-31`) already has the correct `|| true` guard — the other three were missed.

The workflow does `report="$(bin/version-audit)"` (`.github/workflows/version-audit.yml:38`), so the step fails and no drift issue is ever filed.

**Fix**: add a descriptive `User-Agent` to the crates.io request, and append `|| true` to all three curl helper pipelines to match `github_latest_release`.

**Third bug, same script**: `audit_pip_install_pins` (`:198-215`) uses the loose regex `\'?([a-zA-Z0-9_-]+)==([0-9]+(\.[0-9]+)*)\'?`, which matches the literal placeholder `pkg==1.2.3` in a documentation comment at `plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-template:731` and reports `pkg 1.2.3 → 0.2`. Tighten it to require the install-command prefix in the extraction regex, not just in the feeding `grep`.

**Fourth, cosmetic**: `record_drift` at `:98` hardcodes the Location column to `"skill templates"` for every action pin, but the feeding `grep` at `:101` covers `.github/` too, so drift in the repo's own workflows is misreported.

Verify the fix reproduces this full drift table before moving on (run the script directly; empty output means no drift, so a non-empty table is the success condition here).

### 1.2 Seven corrupted `git` command examples ship to users

Commit `b3bdc08` ("style: reformat files with now-working prettier config", 2026-02-19) padded angle-bracket placeholders inside fenced `bash` blocks into shell redirects. An agent copying these literally would try to read a file named `base-branch` and truncate the `..HEAD` range:

- `plugins/pr/skills/pr/SKILL.md:80` — `git diff < base-branch > ...HEAD`
- `plugins/pr/skills/pr/SKILL.md:83` — `git log --oneline < base-branch > ..HEAD`
- `plugins/review-branch/skills/review-branch/SKILL.md:53` — `git merge-base < base-ref > HEAD`
- `plugins/review-branch/skills/review-branch/SKILL.md:66`, `:69`, `:72`, `:84` — same pattern with `< merge-base >`

The correct unpadded form survives elsewhere in the same files (`pr/SKILL.md:112`, `:230`) and in `merge-main`, `rebase-onto-main`, and `use-git/references/diff-output.md`, which confirms these seven are corruption rather than intent.

Commit `36de9ce` (today) added `"embeddedLanguageFormatting": "off"` to `.prettierrc.json` and swept a batch of similar damage, but missed these. **This phase finishes that sweep.** After fixing, re-run `yarn format:check` to confirm the current config leaves them alone.

### 1.3 The skill-description length check validates the wrong copy

`bin/validate-plugins` rule 17 (`:306-374`) enforces Codex's 1024-character cap, but only against `dist/codex/plugins/*/skills/*/SKILL.md` (`:353-370`). The build script replaces every mirrored description with the short marketplace copy (max 233 chars), so the cap is measured against text that can never exceed it, while the canonical file goes unchecked.

`plugins/write-lean-tests/skills/write-lean-tests/SKILL.md` has a **1058-character** description, over the limit and shipped to Claude Code users. `write-formalization-roadmap` is next at 971.

**Fix**: extend rule 17 to also measure the canonical `plugins/*/skills/*/SKILL.md` descriptions, then shorten the `write-lean-tests` description below 1024 (target the 320-character preference the rule already warns at).

### 1.4 `release` references an unbound `TMPFILE`

`plugins/release/skills/release/SKILL.md:601-607` says to write notes to a tmpfile and then passes `--notes-file TMPFILE` with no `mktemp -u` line, no `-u` rationale, and no "never batch the Write with the `gh` call" rule. The SemVer path in the same file (`:889-901`) has all three. Bring the catalog path up to match. This was explicitly deferred in `docs/plans/todo/2026-09-09-fix-tmpfile-write-race-in-gh-skills.md:157`.

### 1.5 Two skills contradict the tmpfile conventions they point at

Both also deferred in the same plan, both still live:

- `plugins/scaffold-go-cli/skills/scaffold-go-cli/SKILL.md:246-252` — multiline inline `gh issue create --body "..."`, which `use-git/references/tmpfile-pattern.md:123-128` labels an anti-pattern.
- `plugins/set-up-installers/skills/set-up-installers/SKILL.md:203-211` — plain `mktemp` (no `-u`) plus a `trap 'rm -f ...' EXIT` chained into the same shell invocation, violating both the `-u` rule and the "cleanup is a separate Bash call" rule.

---

## Phase 2: Tooling and CI gaps

### 2.1 The OpenCode mirror drift check cannot detect additions

`.github/workflows/ci.yml:43-46` and `.github/workflows/release.yml:52-53` run:

```yaml
bin/build-opencode-mirror
git diff --exit-code dist/
```

`bin/build-opencode-mirror:155` does `rm -rf "${OUTPUT_DIR}"` and recreates the symlinks. `git diff` compares the worktree to the index and **ignores untracked files**, so a newly added plugin skill produces a brand-new untracked symlink under `dist/opencode/skills/` and the check reports clean. Deletions and retargets are caught; additions are not.

**Fix**: replace with `git status --porcelain dist/` (fail if non-empty), or `git add -A dist/ && git diff --cached --exit-code`. The Codex tree does not share this hole — `bin/validate-plugins:277-304` regenerates into a `mktemp -d` and uses `diff -qr`, which catches both directions.

### 2.2 `.shellcheckrc`'s optional checks are inert

`.shellcheckrc:2-12` enables 12 optional checks, most of which emit at `style`/`info` severity, but `ci.yml:31` runs `shellcheck -S warning`, discarding all of them. Measured locally on the same file set: CI's exact command finds **0**; default severity finds **25** (14× SC2312, 8× SC2310, 4× SC2016, 2× SC2249).

**Decide and align**: either drop `-S warning` from CI and fix the 25 findings, or drop the `enable=` block. As written the config states an intent CI never enforces. Recommend dropping `-S warning` and fixing, since `bin/version-audit`'s unguarded-pipeline bug (Phase 1.1) is exactly the class SC2312 flags.

### 2.3 CI's shellcheck/shfmt globs miss a real bash script

`ci.yml:31,35` glob `plugins/*/scripts/*`, which does not reach `plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-template` — a 33 KB executable `#!/usr/bin/env bash` file. It passes both tools today (verified), so this is latent, not broken. Widen the glob to `plugins/**/scripts/*`.

### 2.4 `shellcheck` is the only unpinned tool in the repo

`ci.yml:31` uses whatever `ubuntu-latest` ships, while node, yarn, prettier, markdownlint, shfmt, actionlint, and scrut are all pinned. Inconsistent with the repo's own `pin-everything` doctrine. Pin it.

### 2.5 `dist/` is Prettier-ignored but not markdownlint-ignored

`.prettierignore:11-13` excludes `dist/`; neither `.markdownlint-cli2.jsonc:9` nor `cli.markdownlint-cli2.jsonc:18` does (both ignore only `.workmux/` and `**/node_modules/**`). Of 763 real markdown files, **337 are under `dist/`**, and fast-glob follows the `dist/opencode/skills/*` symlinks back into `plugins/`, so markdownlint reports linting 1051 files — every source `SKILL.md` gets linted three times. It passes today, but a failure inside `dist/codex` would be unfixable except by editing source and rebuilding.

**Fix**: add `dist/` to both markdownlint configs' `ignores`. Also add `.agents/` to `.prettierignore` for consistency with its sibling generated tree.

### 2.6 Makefile and entry-point consolidation

`Makefile` has only `test-scrut`, `test-scrut-update`, and `test-all` (`:3`, `:31`) — and `test-all` runs only scrut, no lint and no validate. There is no `make lint`, `make validate`, or `make build`. Three entry points (Makefile for tests, `yarn` for markdown/prettier, bare `bin/*` for validate/build) are unified nowhere, and `ci.yml` reproduces the third by hand. `package.json:13` defines `"validate": "bin/validate-plugins"` which nothing calls.

Add `lint`, `validate`, `build`, and a `test-all` that genuinely runs everything. The 9-entry scrut env list is currently duplicated three times (`Makefile:7-15`, `Makefile:20-28`, `ci.yml:53-61`) with nothing enforcing agreement; collapse the two Makefile copies into one variable.

### 2.7 Smaller items

- `.github/workflows/version-audit.yml:40-43` uses a fixed `GITHUB_OUTPUT` heredoc delimiter (`AUDIT_REPORT_EOF`) for content derived from repo files. Use a random delimiter.
- `release.yml` re-runs `bin/validate-plugins` and the mirror check that `ci.yml` already ran on the same commit, but **skips `bin/validate-json`**, which `ci.yml:40` runs. Make the two symmetric.
- `bin/build-codex-marketplace` hardcodes its output path at `:138` and `:193` and a 4-level `../../../../README.md` at `:128`, despite `CODEX_DIST_DIR` being parameterized at `:7`. Honor the variable throughout.
- `bin/build-codex-marketplace:138` rewrites only the string form of `"source"`, though `plugin_source_path` (`:23-27`) also accepts the object form. All 51 entries are strings today; either handle both or reject the object form explicitly.
- `.gitignore` (3 lines) omits `.workmux/`, which both markdownlint configs go out of their way to exclude, and `.DS_Store` on a macOS-primary repo.
- Neither build script supports `--help` or `--check`. Add a `--check` mode so drift verification stops depending on git state.

### 2.8 No tests for `bin/*`

All three scrut suites test plugin-bundled scripts only. Untested: `build-codex-marketplace`, `build-opencode-mirror`, `compute-catalog-state`, `validate-json`, `validate-plugins` (423 lines, 18 rules), `version-audit`. `compute-catalog-state` alone determines the release tag name. These are pure stdin/stdout/exit-code scripts, so scrut coverage is cheap.

**Add at minimum**: a `compute-catalog-state` test (known fixture → known tag) and a `version-audit` test that asserts a non-zero exit does not silently produce empty output — the exact failure mode of Phase 1.1. Also add a guard test for the Phase 1.2 corruption class: assert no `SKILL.md` contains `< base-` or `< merge-` inside a fenced block.

`plugins/notify/scripts/notify` (15 KB) and `focus-pane` are also shellchecked but never executed.

---

## Phase 3: Version drift (20 items)

With the audit repaired, this is the backlog it should have been reporting since June. Confirmed live against upstream:

| Category | Name | Current | Latest |
| --- | --- | --- | --- |
| Node.js | nodejs (LTS) | 24.15.0 | 24.21.0 |
| Yarn | yarn (Corepack) | 4.14.1 | 4.18.0 |
| Actions | `actions/checkout` | v7.0.0 | v7.0.1 |
| Actions | `astral-sh/setup-uv` | v8.1.0 | v10.0.1 |
| Actions | `ruby/setup-ruby` | v1.306.0 | v1.321.0 |
| Actions | `raven-actions/actionlint` | v2.1.2 | v2.2.0 |
| Actions | `hadolint/hadolint-action` | v3.3.0 | v3.5.0 |
| Actions | `actions/setup-go` | v6.4.0 | v7.0.0 |
| npx | `markdownlint-cli2` | 0.22.1 | 0.23.2 |
| npx | `knip` | 6.9.0 | 6.35.1 |
| npx | `prettier` | 3.8.3 | 3.9.6 |
| npx | `stylelint` | 17.9.1 | 17.15.0 |
| go install | `shfmt` | v3.13.1 | v3.14.1 |
| go install | `golangci-lint` | v2.12.1 | v2.13.2 |
| go install | `goreleaser/v2` | v2.15.4 | v2.18.1 |
| cargo | `shellharden` | 4.3.1 | 4.3.2 |
| cargo | `cargo-deny` | 0.19.4 | 0.20.2 |
| cargo | `typos-cli` | 1.45.2 | 1.50.1 |
| pip / uv | `ruff` | 0.15.12 | 0.16.6 |

The pins concentrate in a small set of files: `set-up-ci/references/ci-*.md`, `set-up-linters/references/tools/github-actions-ci.md` and `references/languages/*.md`, `set-up-installers/SKILL.md`, `pin-everything/references/*`, `check-zsh-scripts/references/tools/shfmt.md`, `scaffold-go-cli` and `scaffold-go-library` `references/makefile.md`, and `release/references/version-patterns.md`. The repo's own `.github/workflows/*` and `.github/copilot-instructions.md:25` also carry `actions/checkout` pins.

Notes for execution:

- **`actions/setup-go` v6→v7 and `astral-sh/setup-uv` v8→v10 are major bumps.** Read their release notes for breaking changes before updating the templates; these are instructions handed to other projects, so a bad template propagates. If a major bump needs template changes beyond the version string, do it and say so.
- Every action pin is a **SHA with a trailing `# vX.Y.Z` comment**. Resolve the new SHA per tag (`gh api repos/OWNER/REPO/git/ref/tags/vX.Y.Z --jq '.object.sha'`, dereferencing annotated tags) rather than hand-editing the comment.
- Bump `.tool-versions` and `package.json`'s `packageManager` (which carries an integrity hash — regenerate it, do not hand-edit).
- Bump `markdownlint-cli2` and `prettier` in the templates to match what `package.json` already pins, so the repo's own versions and the versions it teaches agree.

Re-run `bin/version-audit` afterward; a clean run prints nothing.

---

## Phase 4: `AGENTS.md` and repo-level docs

`AGENTS.md` (symlinked as `CLAUDE.md`) never mentions a large part of the repo. Nothing it *does* mention is missing, so this is purely additive except where noted.

**Add to "Where to find things"**: `tests/` (scrut suites, fixtures, `tests/data/copilot-reviews/`), the `Makefile`, `package.json`/yarn/Corepack, `.github/workflows/`, `.claude/skills/check-versions/` (referenced at `AGENTS.md:112` but never located), `docs/reviews/`, and the lint/format config surface (`.markdownlint*.jsonc`, `cli.markdownlint-cli2.jsonc`, `.prettierrc.json`, `.prettierignore`, `.editorconfig`, `.shellcheckrc`, `.tool-versions`, `.yarnrc.yml`), plus `.github/copilot-instructions.md`.

**Add a "Running tests and linters" section.** `make`, `make test-scrut`, `yarn lint`, and `yarn validate` appear **zero times** in either `AGENTS.md` or `README.md`. This is the single largest onboarding gap.

**Correct `AGENTS.md:14`**: it calls `bin/version-audit` "pre-merge validation". It is not — it runs on a Monday cron and files a labelled issue. Only `validate-plugins` and `validate-json` gate merges. Note its `gh`/`jq`/`curl` requirements.

**Extend "Plugin layout" (`:17-67`)** with a skill-plus-`scripts/` variant. Line 67 frames `scripts/` as hook-specific, but three skill plugins ship one (`create-worktree`, `create-worktree-from-issue`, `resolve-copilot-pr-feedback`) and `bin/validate-plugins` rule 18 exists specifically to validate `${CLAUDE_PLUGIN_ROOT}/scripts/...` references inside SKILL.md bodies.

**Extend "Adding a plugin" (`:69-77`)** with the verification loop: run `bin/validate-plugins`, run `yarn lint`/`yarn format`, add scrut tests when the plugin ships a script, and recompute `metadata.version`.

**Document `docs/plans/` properly (`:15`)**: the `todo/` + `done/` layout and the `YYYY-MM-DD-meaningful-description.md` naming rule that `commit` and `pr` enforce in every repo they touch, including this one.

**Resolve the category-count contradiction**: `AGENTS.md:87` lists eight README categories, but `.claude-plugin/marketplace.json:268` gives `notify` a ninth, `category: "workflow"`, which is documented nowhere. Either document `workflow` as the hooks category or move `notify` onto an existing one. `docs/plans/todo/2026-09-09-file-issues-for-zig-audio-and-verification-gaps.md:371` already tells issue authors to pick "a category from the nine valid values", pointing at a list of eight.

**Fix `.github/copilot-instructions.md`**: it references `.prettierrc.json5`; the repo has `.prettierrc.json`.

**Fix `README.md:200`**: it claims `notify` wires "`Stop` and `PermissionRequest`" on Codex. `plugins/notify/hooks/codex.hooks.json` contains only `Stop`, and `plugins/notify/README.md:34` says "`PermissionRequest` is intentionally not wired."

**Fix `.claude-plugin/marketplace.json:4`**: `metadata.description` advertises "Claude Code commands, hooks, and skills", but the repo ships **zero** commands (`find . -type d -name commands` is empty), and `README.md:3`, `AGENTS.md:5`, and `README.md:202` all say skills and hooks. `bin/validate-plugins` rule 15 requires the two metadata blobs to match, so fixing the source fixes `.agents/` too.

**Add missing `**External tools:**` bullets to `README.md`**: the Code Review section (`:71-76`) has no list at all despite `resolve-copilot-pr-feedback` being built entirely on `gh`; the Git bullet (`:52`) omits `review-branch`, which uses the same `gh repo view --json defaultBranchRef` pattern as `merge-main` and `rebase-onto-main` (its fallback differs, so reword the parenthetical); Scaffolding and CI-and-Release omit the scaffolders and `set-up-installers`, which all call `gh api user`; Code Quality omits `scrut` for `write-scrut-tests`.

**Reconcile the `Trigger` column rule**: `README.md:75` shows `/address-review <path>` while `AGENTS.md:85` says the column shows "just the slash command". The argument is real and documented in the plugin's own README, so amend the `AGENTS.md` rule to permit a required argument rather than stripping it.

---

## Phase 5: Per-plugin README alignment (all 51)

34 of 51 plugin READMEs open with a paragraph that differs from the canonical marketplace description. Make all 51 opening paragraphs match their `marketplace.json` description, and add a rule to `AGENTS.md`'s "README catalog format" section requiring it, so it stays true.

Roughly 11 are semantically stale rather than merely reworded, and these are the ones that matter most:

| Plugin | Problem |
| --- | --- |
| `pr` | README:3 drops the lint step entirely; the skill *does* lint (`SKILL.md:190`, and an unresolved lint state is a hard stop at `:202-210`). The **SKILL.md frontmatter is stale too** — fix both. |
| `create-worktree` | Never names workmux, which it requires. |
| `write-scrut-tests` | Drops the zsh-plugin half of its scope. |
| `write-markdown` | Describes markdownlint alignment instead of what the skill does. |
| `scaffold-new-repo` | Omits the concrete file list. |
| `add-cobra-version`, `add-goreleaser-homebrew`, `create-worktree-from-issue`, `scaffold-go-library`, `set-up-installers`, `release` | Wording that contradicts or under-describes the catalog entry. |

**Also normalize while here**: `plugins/notify/README.md:54,120` uses `## What it does` / `## See also`; all 50 others use title case. `plugins/address-issue/README.md:32-39` lists permissions as prose bullets; the other 13 use a copy-pasteable JSON block.

**Add `## Requirements` sections** where the SKILL.md frontmatter already declares a hard dependency but the README is silent: `address-issue`, `pr`, `suggest-next-issue`, `create-worktree`, `create-worktree-from-issue` (gh/workmux), `add-scrut-cli-tests` (scrut), `resolve-copilot-pr-feedback` (gh). Only 5 of 51 have one today.

**Add missing permission entries**: `plugins/pr/SKILL.md:56-57` runs `git fetch` and `git merge-base --is-ancestor`, but `plugins/pr/README.md:32` allowlists neither, though `merge-main` and `rebase-onto-main` both do. Only 14 of 51 plugin READMEs have a Recommended Permissions section at all; add one to `review-branch` (10 raw git commands, writes files, runs `mkdir`) and the five scaffolders (all run `gh api user`, `git init`, `git commit -S`).

---

## Phase 6: Cross-skill convention reconciliation

These are conflicts where two skills teach incompatible things. Each needs a decision, then propagation.

### 6.1 Branch naming conflict that breaks `pr`'s issue detection

- `use-git/references/common-operations.md:76-87` defines six prefixes and says *"Include issue numbers when working from an issue: `fix/42-login-timeout`."*
- `create-worktree/SKILL.md:27` and `create-worktree-from-issue/SKILL.md:69-76` define only two types, make `feature/` primary (`use-git` calls it an alternative to `feat/`), and their examples **omit the issue number**.
- `pr/SKILL.md:95-101` parses issue numbers out of the branch name as its *primary* detection strategy.

So branches created by `create-worktree-from-issue` are unparseable by `pr`, silently forcing a fallback path. Pick one scheme, make `create-worktree-from-issue` embed the issue number, and align all four skills.

### 6.2 `review-branch` looks in a directory nothing creates

`review-branch/SKILL.md:153` runs `ls docs/plans/in-progress/`. Every scaffolder creates only `todo/` and `done/`, and `commit`/`pr` recognize only `todo/`, `done/`, and the `docs/plans/` root. Remove or replace it.

Relatedly, `review-branch/SKILL.md:157` gives `add-dark-mode.md` as a plan-name example, which the `commit` (`:174-183`) and `pr` (`:404-413`) datestamp rule forbids.

### 6.3 Review-document location is unsettled

`review-branch/SKILL.md:334` writes to `docs/reviews/`; `address-review/SKILL.md:28` accepts `docs/reviews/`, `docs/plans/reviews/`, "or any markdown file". No scaffolder creates either. Settle on one and have the scaffolders create it.

### 6.4 `use-git` is the declared source of truth but is missing what it is cited for

Four skills point at `use-git/references/tmpfile-pattern.md` "for the full rationale" (`pr:357`, `create-issue:103`, `release:607` and `:911`, `resolve-copilot-pr-feedback:290`), but:

- **The verify step is not there.** `pr:331-347` and `create-issue:77-93` implement post-create body verification; `tmpfile-pattern.md` goes from step 3 straight to Cleanup. `release` and `resolve-copilot-pr-feedback` have no verification at all.
- **The tmpfile prefix conflicts.** `tmpfile-pattern.md:20,91,98` uses `gh-pr-body-`; `pr/SKILL.md:313` uses `pr-body-` and `pr/README.md:32` allowlists `Bash(mktemp -u /tmp/pr-body-*)`. Copying the canonical example triggers a permission prompt.
- **There is no `gh api` section at all**, so the `--paginate` rule that `resolve-copilot-pr-feedback/SKILL.md:223` explains lives in exactly one skill. Meanwhile `pin-everything/references/version-audit.md:30-38` calls endpoints "(paginated)" while `references/language-runtimes.md:119,130,136` shows the same endpoints without `--paginate`.
- **The decision table is stale.** `use-git/SKILL.md:37` says worktree prompts use "Write tool to `/tmp/`", but both worktree skills now pipe through stdin (`create-worktree/SKILL.md:72-80`, `create-worktree-from-issue/SKILL.md:120-123`).

Fix `use-git` first, then propagate.

### 6.5 Commit messages do not defer to project config, but PR titles now do

`pr/SKILL.md:234-270` (from #322) builds a full detection ladder for PR titles: commitlint `type-enum`/`header-max-length`, agent config, merged-PR sampling. The commit path has no equivalent — `commit/SKILL.md:121-129`, `pr/SKILL.md:175-177`, and `use-git/references/common-operations.md:53-65` all hardcode a seven-type list and "under 72 characters". Extend the same ladder to commit subjects, or extract it into `use-git` and have both cite it.

### 6.6 Terminology collisions

- `<base-branch>` means the repository default branch in `use-git/references/common-operations.md:21`, `merge-main:66`, and `rebase-onto-main:80`, but the possibly-different stacked-PR base in `pr/SKILL.md:32,62`. Rename one.
- HEREDOC style is split: `use-git/references/heredoc-pattern.md:20`, `commit:137`, and `pr:181` use the wrapped `$(\n  cat << 'EOF'` form; `release:426,764` uses the one-line `$(cat <<'EOF'` form.

### 6.7 Fix dead cross-reference paths

Those four skills cite `use-git` by **repo-relative source path** (`plugins/use-git/skills/use-git/references/tmpfile-pattern.md`), which does not exist in an installed plugin tree. Reference the skill by name instead.

### 6.8 `set-up-linters` has the only description with no trigger phrases

`plugins/set-up-linters/skills/set-up-linters/SKILL.md:3-5` is 112 characters with no "Use when the user says …" clause; all 50 other skills have one, so this skill under-triggers. It also drops the Pandoc-academic preset that its own `plugin.json:5` and `README.md:18` advertise and that `SKILL.md:54,86,109,169-172` implements.

---

## Phase 7: Terminology sweep

Bring the repo in line with the global preferences, and **document them in the project context** so they stick: add a terminology section to `AGENTS.md` and `.github/copilot-instructions.md`, and state the em dash convention in the `write-markdown` skill as a documented house convention.

- **Em dashes → `--` or restructured punctuation.** 47 markdown files. Usage correlates with skill age; newer skills already use `--`, so this is finishing a transition rather than starting one. Heaviest: `pin-everything/SKILL.md` (27), `manage-repo-licensing/SKILL.md` (19), `manage-repo-licensing/references/commit-sequence.md` (17), `example-flows.md` (15), plus `resolve-copilot-pr-feedback`, `suggest-next-issue`, `pr`, `create-worktree-from-issue`, `lint-and-fix`, `create-plugin`, `review-branch`. **Exclude `docs/plans/done/`** (historical archive, already Prettier-ignored) and `dist/` (regenerated).
- **"sanity check" → "validity check" / "plausibility check"**: `write-formalization-roadmap/references/comprehensive/conventions.md:60`, `milestone-anatomy.md:92,94`, `essential/checklist.md:28`; `write-math/references/comprehensive/theorems-and-proofs.md:82`, `revision-and-process.md:227`.
- **"whitelist" → "allowlist"**: `pin-everything/SKILL.md:144`, `pin-everything/references/yarn-corepack.md:78`. No "blacklist" anywhere.
- **"master" (Zig release channel) → "the development channel"**: `pin-everything/references/version-audit.md:15`, `language-runtimes.md:139`. The other 12 hits are legitimate (git default-branch detection, upstream URLs, `@mastersthesis`, Rails `config/master.key`) and stay.
- **"alive" → "running"**: the identical duplicated sentence at `create-worktree/SKILL.md:52` and `create-worktree-from-issue/SKILL.md:96` ("cannot initialize while the parent Claude Code process is alive").
- **Time estimates**: `suggest-next-issue/SKILL.md:96` ("can be resolved quickly"), `:127` ("### Quick Wins", an output category the skill instructs the agent to emit), and `README.md:15`. Recast as scope rather than duration.

---

## Phase 8: Plans and branch housekeeping

**`docs/plans/todo/` — two of three plans are done:**

- `2026-09-09-fix-tmpfile-write-race-in-gh-skills.md` — complete once Phase 1.4 and 1.5 land (those are exactly its three deferred items). Move to `done/`.
- `2026-05-02-codex-cli-native-plugins.md` — every deliverable exists, and the plan is now factually wrong: line 126 says `dist/codex/` and a codex build script "are unnecessary and have been dropped", yet both ship. Move to `done/`.
- `2026-09-09-file-issues-for-zig-audio-and-verification-gaps.md` — its sole deliverable (filing #338-#357 and `gh-actions#85`-`#88`) is met. Move to `done/` unless deliberately held open.

**Rename the eight `done/` plans that violate the repo's own naming rule**, four of which are auto-generated nonsense: `declarative-noodling-pudding.md`, `ethereal-booping-sunbeam.md`, `memoized-purring-pie.md`, `quizzical-imagining-cerf.md`, plus `add-create-worktree-skill-with-prompt-injection.md`, `create-create-plugin-skill.md`, `extract-copilot-graphql-into-script.md`, `fix-marketplace-structure.md`. Derive datestamps from `git log --diff-filter=A --format=%cs -1 -- <file>`.

Note the irony worth resolving: `commit/SKILL.md:174` and `pr/SKILL.md:404` cite `ethereal-booping-sunbeam.md` and `quizzical-imagining-cerf.md` **by name** as examples of bad plan names, and both files still sit in `done/` under exactly those names. Update those citations after renaming.

**Branches**: `feature/add-strunk-and-white-skill` is fully merged into `main` with zero unique commits and an abandoned worktree (last touched 2026-05-06) — remove the worktree and delete the branch. Five remote branches are 844-1192 commits behind with work from January and February (`claude/review-marketplace-plugin-setup-Gjjmz`, `feature/new-skill-create-tmux-plugin`, `feature/update-golangci-lint-action-to-v9-in-scaffold`, `fix/create-worktree-skills`, `fix/lint-discrepancies`) — confirm each is abandoned before deleting. Leave `test/330-fix-scrut-bug` alone; it has active work for #330.

**Close resolved issues**: #330's fix is in flight on its own branch. Check whether any of #334, #335, #336 are resolved by Phase 3's markdownlint bump.

---

## Phase 9: Versions, mirrors, and validation

Do this last, after all content changes have landed.

1. **Bump plugin versions.** Nearly every plugin gets a content change in this plan. Patch-bump for wording, pin bumps, terminology, and README alignment. Minor-bump where behavior meaningfully changes: `use-git` (new verify step, new `gh api` section), `set-up-linters` (rewritten description changes activation), and any skill whose major action-pin bump (`setup-go` v7, `setup-uv` v10) changes what it instructs. Keep `plugin.json` and the `marketplace.json` entry identical.
2. **Recompute `metadata.version`** with `bin/compute-catalog-state` and write it to `.claude-plugin/marketplace.json`.
3. **Regenerate both mirrors**: `bin/build-codex-marketplace` and `bin/build-opencode-mirror`. Commit the results.
4. **Run the `check-versions` skill** to confirm version correctness before opening the PR.

Commit at each phase boundary rather than batching, per the repo's small-commit convention. Phases 1-2 are independent of 3-7 and can land first.

---

## Verification

```bash
# Repo validators (all must pass)
bin/validate-json
bin/validate-plugins
bin/compute-catalog-state          # must equal marketplace.json metadata.version

# The audit must now run to completion. After Phase 3 it should print nothing.
bin/version-audit; echo "exit=$?"

# Mirrors must be byte-identical to a fresh build, including additions
bin/build-codex-marketplace
bin/build-opencode-mirror
git status --porcelain dist/ .agents/    # must be empty -- not `git diff`

# Lint and format
yarn install --immutable
yarn lint
yarn format:check
shellcheck bin/* plugins/**/scripts/*    # at the severity CI settles on in 2.2
actionlint

# Tests
make test-all
```

Targeted checks for this plan's specific fixes:

```bash
# Phase 1.2: no corrupted placeholders remain anywhere, including mirrors
grep -rn '< *base-branch *>\|< *merge-base *>\|< *base-ref *>' plugins/ dist/    # must be empty

# Phase 1.3: no canonical skill description exceeds the Codex cap
bin/validate-plugins    # rule 17 now covers plugins/*/skills/*/SKILL.md

# Phase 2.1: the drift check must catch an addition
touch dist/opencode/skills/__probe && git status --porcelain dist/ && rm dist/opencode/skills/__probe

# Phase 7: terminology
grep -rn '—' plugins/ docs/ --include='*.md' | grep -v 'docs/plans/done/'    # must be empty
grep -rni 'sanity check\|whitelist\|blacklist' plugins/                       # must be empty
```

End-to-end, confirm the weekly job actually works by dispatching it manually rather than waiting for Monday:

```bash
gh workflow run version-audit.yml
gh run watch "$(gh run list --workflow=version-audit.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
```

A green run that files or updates no issue means both the script fix (Phase 1.1) and the pin bumps (Phase 3) are complete.
