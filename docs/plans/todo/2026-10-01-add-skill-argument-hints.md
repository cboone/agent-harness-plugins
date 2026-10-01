# Show argument hints for skills that take options

## Context

Typing `/monitor-pr` in Claude Code shows only the skill description, while other plugins show inline ghost text such as `[pr-number] [--interval <duration>]`. Claude Code renders that text from the `argument-hint` frontmatter field. This repository already allows the field (rule 21 of `bin/validate-plugins`, table in `docs/plugin-development.md`), and the 2026-03-10 plan added hints to the old `commands/` files, but the hints were not carried over when commands became skills. No `SKILL.md` declares `argument-hint` today, so no skill shows its options.

Codex CLI and OpenCode ignore the field (measured and recorded in `docs/plugin-development.md`), so adding it changes nothing there.

## Approach

### 1. Add `argument-hint` to every skill that accepts arguments

Add one line after `description` in the frontmatter, as a double-quoted YAML string. Notation: `<x>` for a required value, `[x]` for an optional argument, `a|b` for alternatives. Order: positional arguments first, then flags in the order the `## Options` section lists them. Keep hints short; where a skill has many flags, list the frequently used ones and let the description cover the rest.

Proposed hints (verify each against its `## Options` and input sections while editing):

| Skill                            | `argument-hint`                                                                                                                           |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `monitor-pr`                     | `[pr-number] [--interval <duration>] [--ticks <n\|unlimited>] [--rounds <n\|unlimited>] [--confirm-clean] [--no-fix]`                     |
| `review-colleague-pr`            | `[pr-number] [requirement-urls...] [--fast\|--thorough] [--full] [--since <ref>]`                                                         |
| `triage-dependabot-prs`          | `[pr-number...] [--repo OWNER/REPO] [--verify] [--report-only]`                                                                           |
| `review-until-clean`             | `[--reviewer codex\|claude] [--base <ref>] [--effort <level>] [--severity important\|nit] [--max-rounds <n>] [--report-only] [--no-save]` |
| `review-branch`                  | `[--plan <path>] [--since <ref>] [--brief] [--no-save]`                                                                                   |
| `create-worktree`                | `<issue-number\|description> [--issue <n>\|--no-issue] [--branch <name>] [--base <branch>] [--resource <name>]`                           |
| `address-issue`                  | `<issue-number\|description> [--dry-run] [--no-approval] [--no-commit] [--commit-per-change]`                                             |
| `address-issue-in-worktree`      | `<issue-number> [--no-approval] [--resource <name>]`                                                                                      |
| `address-review`                 | `[review-path] [--dry-run] [--skip <numbers>] [--commit-per-item]`                                                                        |
| `commit`                         | `[--push] [--staged\|--plan\|--all]`                                                                                                      |
| `create-deferred-issues`         | `[pr-or-issue] [--dry-run] [--no-comment]`                                                                                                |
| `lint-and-fix`                   | `[--no-commit] [--no-push] [--tool <name>] [--check]`                                                                                     |
| `pin-everything`                 | `[--scope <list>] [--no-audit] [--no-dependabot] [--dry-run]`                                                                             |
| `merge-main`, `rebase-onto-main` | `[--base <branch>]`                                                                                                                       |
| `release`                        | `[--major\|--minor\|--patch] [--dry-run]`                                                                                                 |
| `review-dependabot-config`       | `[--repo OWNER/REPO] [--report-only]`                                                                                                     |
| `set-up-review-config`           | `[--dry-run]`                                                                                                                             |
| `suggest-next-issue`             | `[--label <name>] [--milestone <name>] [--limit <n>] [--include-prs] [--parallel-only]`                                                   |

Positional forms marked as unverified above (`address-review`, `create-deferred-issues`, `address-issue-in-worktree`) must match what the skill body actually reads; drop the positional if the skill takes none. For `suggest-next-issue`, match the hint to the phrasing its Options section accepts, rewording to flags only if the body already accepts them.

Verified outcome: `create-deferred-issues` takes no positional (it discovers its source from the branch), `address-review` requires its review path, `address-issue-in-worktree` accepts an issue number or description like `address-issue`, `create-worktree` also lists `--release-resource` and `--list-resources`, and `suggest-next-issue` uses `[--label <name>] [--parallel-only] [filters...]` because its other filters are natural language.

Also scan skills without an `## Options` section (for example `create-issue`, `pr`, `review-plan`, `create-plugin`) for documented arguments, and add a hint where one exists. Of these, only `review-plan` documents an argument (`[path]`).

### 2. Bump versions

Each touched plugin gets a patch bump in `.claude-plugin/plugin.json`, mirrored in `.codex-plugin/plugin.json` where present. The hint is display metadata, not new behavior.

### 3. Keep it from regressing

- Extend rule 21 in `bin/validate-plugins`: a `SKILL.md` with an `## Options` heading must declare a non-empty `argument-hint`. Add a passing and a failing case to the existing validator scrut suite (`tests/scrut/repo-tooling.md` or the suite rule 21 already uses; check `tests/AGENTS.md`).
- `docs/plugin-development.md`: in the skill frontmatter section, state that skills accepting arguments declare `argument-hint`, with the notation above.
- `plugins/create-plugin/skills/create-plugin/SKILL.md` and its checklist: move the `argument-hint` guidance from commands-only to skills too (patch bump `create-plugin`).

### 4. Regenerate mirrors

Run `make build` so `dist/` and `.agents/` carry the new frontmatter, and commit the regenerated output.

## Commits

Small Conventional Commits, GPG-signed: the validator rule and test, the docs and `create-plugin` guidance, then the skill hints with version bumps, then the regenerated mirrors. Commit this plan with the work, first renaming it to `docs/plans/todo/2026-10-01-add-skill-argument-hints.md`.

## Verification

- `make test-all` passes (lint, validate including the new rule, scrut).
- Run the `check-versions` skill before the PR.
- Manual: reload plugins in Claude Code from this worktree, type `/monitor-pr` and confirm the hint appears; spot-check `/review-colleague-pr` and `/commit`.
