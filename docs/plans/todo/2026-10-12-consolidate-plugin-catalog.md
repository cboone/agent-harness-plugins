# Consolidate the plugin catalog

Issue: [#586](https://github.com/cboone/agent-harness-plugins/issues/586). Classification: chore (breaking for anyone who installed a merged, folded or renamed plugin by name).

## Context

The catalog has 70 plugins on `main` at `b89fff26`. Several pairs ship byte-identical script copies only because rule 18 of `bin/validate-plugins` requires each `SKILL.md`'s `${CLAUDE_PLUGIN_ROOT}/scripts/NAME` reference to resolve inside its own plugin. Others always travel together, and a few small plugins mostly restate a larger one. This plan merges the first two groups into multi-skill plugins, folds the third into their hosts, and repositions `suggest-next-issue`. `wtaf` already ships two skills, so the multi-skill layout is established.

Decisions taken during planning:

- Merged skills use short names inside their plugin namespace. Every caller uses the qualified name and the README carries a mapping. Claude Code still resolves the retained bare names `create-worktree` and `create-issue` to their new plugins, as the scratch-session check confirms; the migration does not promise their rejection.
- Plugins that drive workmux become one `workmux` plugin. A plugin that dealt with git worktrees alone would take a worktree name; these two depend on workmux throughout. The upstream workmux marketplace is also named `workmux` and ships one plugin, `workmux-status`; marketplaces scope plugin names, so the names do not collide, though an upstream plugin named `workmux` would share the `workmux:` skill prefix.
- `address-issue` stays standalone. It runs on the current branch without workmux, and ships no scripts, so merging it removes no copies. The launched worktree sessions keep calling `/address-issue`, which is why the issue-launching skill is named `start-issue` rather than `address-issue`.
- `review-until-clean` and `review-pr-with-codex` stay separate while both are under active development, keeping their hand-maintained `review-scope` copies, the drift testcase, and the paragraph in `docs/plugin-development.md` that describes them.
- `bin/build-shared-references` (from #593) is not extended in this work. Moving `review-scope` into it, and the four identical `references/license.md` copies in the scaffold plugins, is a follow-up.
- `trim-text` and `trim-comments` stay separate: `commit` and `pr` invoke `trim-text` directly, and the two skills already route to each other. `push-notification` and `notify` stay separate: an ntfy skill and a macOS hook with different mechanisms.
- #548 closed with #593, which added a progress model that `make build` copies from `publish-report-board` into `suggest-next-issue`. That generated copy stays.
- #585 already shipped in its own catalog release (`catalog-e1f6ae4e...`), and releases are cut automatically per merge, so this work ships in the release its own merge creates.

## Name mapping

| New skill                             | Old plugin and skill          | Plugin version                     |
| ------------------------------------- | ----------------------------- | ---------------------------------- |
| `workmux:create-worktree`             | `create-worktree`             | new plugin, 1.0.0                  |
| `workmux:start-issue`                 | `address-issue-in-worktree`   | new plugin, 1.0.0                  |
| `monitor-pr:monitor`                  | `monitor-pr`                  | 2.1.1 to 3.0.0                     |
| `monitor-pr:resolve-copilot-feedback` | `resolve-copilot-pr-feedback` | joins `monitor-pr`                 |
| `sync-with-main:merge`                | `merge-main`                  | new plugin, 1.0.0                  |
| `sync-with-main:rebase`               | `rebase-onto-main`            | new plugin, 1.0.0                  |
| `dependabot:review-config`            | `review-dependabot-config`    | new plugin, 1.0.0                  |
| `dependabot:triage-prs`               | `triage-dependabot-prs`       | new plugin, 1.0.0                  |
| `use-git:create-issue`                | `create-issue`                | `use-git` 1.2.7 to 1.3.0           |
| `set-up-installers` (reference)       | `add-goreleaser-homebrew`     | `set-up-installers` 3.1.4 to 3.2.0 |
| `set-up-installers` (reference)       | `write-homebrew-formula`      | same                               |
| `scaffold-go-cli` (mode)              | `add-cobra-version`           | `scaffold-go-cli` 2.8.4 to 2.9.0   |
| `write-zsh-scripts` (section)         | `check-zsh-scripts`           | `write-zsh-scripts` 1.1.1 to 1.2.0 |
| `write-lean-code` (reference)         | `write-lean-tests`            | `write-lean-code` 1.1.1 to 1.2.0   |
| `set-up-ci` (section)                 | `optimize-runner-usage`       | `set-up-ci` 2.1.2 to 2.2.0         |
| `scaffold-new-repo` (optional step)   | `add-community-files`         | `scaffold-new-repo` 1.8.5 to 1.9.0 |

`monitor-pr` takes a major bump because its skill is renamed. `use-git` keeps `use-git:use-git` and gains a skill, so it takes a minor bump. The catalog drops from 70 to 58 entries: 15 plugins leave and 3 arrive. Re-check every starting version against `main` before bumping, since other branches keep landing.

## Changes

### 0. Namespaced cross-reference support

- Before migrating callers, extend `bin/check-cross-references` to recognize `plugin:skill` and `/plugin:skill` in invocation references, compositions, near-miss warnings and dependency declarations. Resolve a qualified name to `plugins/PLUGIN/skills/SKILL/SKILL.md`; preserve existing bare-name behavior for unchanged callers.
- Keep dependency declaration, resolution and use checks consistent: qualified names must identify the named plugin and skill, and compositions must remain declared under `## Skill dependencies`.
- Update `docs/plugin-development.md` with the qualified-name syntax and resolution rules. Add scrut cases in `tests/scrut/check-cross-references.md` for valid qualified references and declarations, missing plugins, missing skills, undeclared compositions, unused declarations and retained bare-name behavior.

### 1. `workmux` plugin

- Create `plugins/workmux/` with skills `create-worktree` (from `create-worktree`) and `start-issue` (from `address-issue-in-worktree`), and one copy of `launch-workmux`, `compose-issue-prompt` and `manage-resource-claims` in `scripts/`.
- Update each `SKILL.md` `name`, description routing ("to plan an issue there, use `workmux:start-issue`"), argument hints and cross-references between the two skills. Keep `/address-issue` in the composed launch prompt.
- Delete `plugins/create-worktree/` and `plugins/address-issue-in-worktree/`.
- Tests: point `tests/scrut/compose-issue-prompt.md`, `manage-resource-claims.md`, the `Makefile`'s `SCRUT_ENV` and `.github/workflows/ci.yml`'s `scrut-env` at `plugins/workmux/scripts/`; delete the three copy-drift testcases in `tests/scrut/repo-tooling.md`. Remove obsolete duplicate helper variables from both environment lists, retaining each surviving helper registration.
- Docs: delete the byte-identical-copies paragraph at `docs/plugin-development.md:51`, keeping the `review-scope` paragraph after it (reworded so it no longer says "the same way"); narrow `plugins/AGENTS.md:7` to the `review-scope` pair.
- Category `issues-and-worktrees`.

### 2. `monitor-pr` gains `resolve-copilot-feedback`

- Rename `plugins/monitor-pr/skills/monitor-pr/` to `skills/monitor/`; move `resolve-copilot-pr-feedback`'s skill to `skills/resolve-copilot-feedback/`. Keep one `scripts/resolve-copilot-threads`, plus `merge-flow`.
- `monitor`'s routing keeps the merge-and-sync step (from #583) separate from Copilot handling, and invokes `monitor-pr:resolve-copilot-feedback` where it invoked the old skill.
- Keep the catalog description from #583 and extend it to cover resolving Copilot threads on demand.
- Delete `plugins/resolve-copilot-pr-feedback/` and the `resolve-copilot-threads` drift testcase in `repo-tooling.md`; repoint `tests/scrut/resolve-copilot-threads.md` and its helper registration to `plugins/monitor-pr/scripts/resolve-copilot-threads` in both `SCRUT_ENV` and CI's `scrut-env`. Remove the obsolete duplicate registration from both lists.

### 3. `sync-with-main` plugin

- Create `plugins/sync-with-main/` with skills `merge` and `rebase` from `merge-main` and `rebase-onto-main`; share wording on base-branch detection and conflict resolution through a reference only if the two `SKILL.md` files already duplicate it.
- Delete both old plugins. Category `git`.

### 4. `dependabot` plugin

- Create `plugins/dependabot/` with skills `review-config` and `triage-prs`; carry over `triage-dependabot-prs`' scripts and repoint `tests/scrut/dependabot-prs.md` and its helper registration in both `SCRUT_ENV` and CI's `scrut-env`.
- Delete both old plugins. Category `ci-and-release`.

### 5. `use-git` gains `create-issue`

- Move `plugins/create-issue/skills/create-issue/` into `plugins/use-git/skills/create-issue/`; cross-link it with `use-git`'s tmpfile guidance rather than repeating it.
- Delete `plugins/create-issue/`. `tests/fixtures/validate-plugin-fixture` edits `plugins/create-issue/.../SKILL.md` in its copied tree (line 253); repoint it.

### 6. Folds

Each folded plugin becomes a reference, mode or section of its host, and its directory and catalog entry are removed.

- `add-goreleaser-homebrew` and `write-homebrew-formula` into `set-up-installers` as references; replace its current route to `add-goreleaser-homebrew`.
- `add-cobra-version` into `scaffold-go-cli` as an "add to an existing CLI" mode or reference. `tests/scrut/validate-plugins-catalog.md` uses `add-cobra-version` as a sample catalog entry; switch it to a surviving name.
- `check-zsh-scripts` into `write-zsh-scripts` as a lint section or reference.
- `write-lean-tests` into `write-lean-code` as a reference, merging its review checklist into the host's.
- `optimize-runner-usage` into `set-up-ci` as a section the generated workflows follow; `refresh-project-scaffolding` audits against it.
- `add-community-files` into `scaffold-new-repo` as an optional step.
- `set-up-review-config`: remove the separate `write-lean-tests` entry from `references/guides.md`; `make build` removes its bundled checklist and regenerates the merged `write-lean-code` checklist. Bump `set-up-review-config` from 1.0.2 to 1.0.3 for the changed shipped references and checklists, alongside the host guide's minor bump; re-check the starting version against `main` before bumping.

### 7. `suggest-next-issue` reposition

- Update its description, and `publish-report-board`'s backlog-triage reference, so each names the other's role: one focused answer to "what should I work on next", against the board's full picture.
- Patch bumps: `suggest-next-issue` 1.3.0 to 1.3.1, and `publish-report-board` 1.3.0 to 1.3.1 if its reference changes. Leave the shared progress model alone; a change to it needs forward bumps in both plugins (`plugins/AGENTS.md:12`).

### 8. Callers and catalog surfaces

- Use the namespaced support from section 0 when updating callers and dependency declarations; rule 19 checks supported reference forms, and the retired-identity checks below cover other mentions. Known callers include `address-issue`, `address-review`, `bootstrap-project`, `create-deferred-issues`, `create-plugin`, `pin-everything`, `plant-defects`, `pr`, `refresh-project-scaffolding`, `release`, `review-anti-patterns`, `review-colleague-pr`, `scaffold-*`, `set-up-linters`, `set-up-review-config`, `suggest-next-issue`, `trim-text`, `upgrade-everything`, `write-bash-scripts`, `write-formalization-roadmap`, `write-go-code`, `write-manual-verification-plan` and `wtaf`. Each caller whose shipped skill text, references or generated checklists change takes a patch bump unless a larger bump is already required by this plan.
- `.claude-plugin/marketplace.json` entries and categories; root `README.md` catalog rows; each new or host plugin's README, with descriptions matching the catalog verbatim and linking to `#install`.
- Root `README.md`: add a "Moved and removed plugins" section with the name mapping, and point former users to the new install commands.
- `plugins/AGENTS.md`, `docs/plugin-development.md` examples, and any `AGENTS.md` mention of the old names.
- `.github/copilot-instructions.md` and `.github/instructions/`: any rules that name moved scripts or plugins.
- `.github/workflows/ci.yml`: migrate all affected `scrut-env` paths alongside `SCRUT_ENV`, checking that local and CI registrations cover the same surviving helpers.

### 9. Build, validate, commit

- Run `make build` to regenerate `dist/codex/`, `.agents/` and the bundled checklists, then `make test-all`, and observe the final result.
- Use the `check-versions` skill before the PR.
- Commit each numbered section separately (signed, Conventional Commits, `(#586)` suffix), with the regenerated mirror in its own commit per section where it changes.

## Follow-ups

- Move `review-scope` to `bin/build-shared-references` once the review plugins settle, and consider the scaffold plugins' `references/license.md` copies at the same time.
- `notify`'s README does not point back to `push-notification`, and the two sit in different categories (`workflow` and `agents`).

## Verification

- `make test-all` passes, including rule 18 (script references resolve inside each plugin) and rule 19 (cross-references).
- `jq '.plugins | length' .claude-plugin/marketplace.json` reports 58.
- Search `plugins/`, `bin/`, `tests/`, `docs/plugin-development.md`, `AGENTS.md` and `.github/` for retired identities: deleted `plugins/OLD/` and `dist/codex/plugins/OLD/` paths, old plugin installation commands, old qualified invocations and obsolete bare invocation forms. Also inspect current README content outside the migration mapping. No operational reference to a retired identity remains; plans, reviews, migration documentation and tests that intentionally assert rejection are allowed.
- Retain `create-worktree` and `create-issue` as skill directory and frontmatter names in their new plugins, and allow their new qualified invocations. Do not use whole-word absence of every former plugin name as an acceptance criterion.
- Local `SCRUT_ENV` and CI `scrut-env` use the new helper paths, with no registrations pointing into deleted plugin directories.
- In a scratch Claude Code session with the branch's marketplace installed, `/workmux:start-issue`, `/monitor-pr:resolve-copilot-feedback`, `/sync-with-main:rebase`, `/dependabot:triage-prs` and `/use-git:create-issue` each load.
