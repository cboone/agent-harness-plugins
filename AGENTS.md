# Claude Code Plugins

## Project overview

This repository is the canonical source for a collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugins (skills and hooks). Committed mirrors under `dist/codex/` and `dist/opencode/` make the same plugins work in [Codex CLI](https://developers.openai.com/codex/cli) and [OpenCode](https://opencode.ai). User-facing details live in `README.md`.

## Where to find things

### Plugin sources and generated mirrors

- `plugins/<name>/`: canonical plugin source. Each plugin has `.claude-plugin/plugin.json`, `README.md`, and either `skills/<name>/SKILL.md` or `hooks/hooks.json` (or both).
- `.claude-plugin/marketplace.json`: catalog of record for the Claude Code marketplace. Source of truth for plugin metadata and versions.
- `.agents/plugins/marketplace.json` and `dist/codex/`: generated Codex CLI marketplace plus mirrored plugin roots. Regenerate with `bin/build-codex-marketplace`.
- `dist/opencode/`: generated OpenCode mirror. Regenerate with `bin/build-opencode-mirror`. CI fails if either generated tree drifts from source.

Never edit anything under `dist/` or `.agents/` by hand. Both are excluded from Prettier and markdownlint for that reason; fix the source and rebuild.

### Scripts

- `bin/validate-json` and `bin/validate-plugins`: pre-merge validation, both run by `.github/workflows/ci.yml`. `validate-plugins` enforces 18 rules covering manifest fields, marketplace agreement, alphabetical ordering, Codex hook manifests, skill description limits, and generated-tree freshness.
- `bin/compute-catalog-state`: canonical implementation of the marketplace catalog state tag (`metadata.version` in `marketplace.json`). Consumed by `bin/validate-plugins` and `.github/workflows/release.yml`.
- `bin/version-audit`: a weekly upstream-drift audit, not a merge gate. `.github/workflows/version-audit.yml` runs it on a Monday cron and files or updates a `version-audit`-labelled issue. Requires `gh` (authenticated), `jq`, and `curl`. Empty output means no drift.
- `bin/list-shell-scripts`: the single source of truth for which Bash scripts get linted. Used by the `Makefile` and CI so a new script is covered without widening a glob.

### Tests and tooling

- `tests/scrut/`: [scrut](https://github.com/facebookincubator/scrut) snapshot suites for the plugin-bundled scripts and the `bin/` tooling. `tests/fixtures/` holds executable stubs (`tmux-stub`, `workmux-stub`, and so on) and `tests/data/` holds JSON fixtures.
- `Makefile`: the entry point for local work. See [Running tests and linters](#running-tests-and-linters).
- `package.json` plus Yarn via Corepack: Markdown and formatting tooling only (`markdownlint-cli2`, `prettier`). Node and Yarn versions are pinned in `.tool-versions` and `packageManager`.
- `.github/workflows/`: `ci.yml` (lint, validate, scrut), `release.yml` (catalog state tag and GitHub Release on push to main), `version-audit.yml` (the weekly drift audit).
- Lint and format config: `.markdownlint.jsonc`, `.markdownlint-cli2.jsonc`, `cli.markdownlint-cli2.jsonc` (CLI-only, adds ESM custom rules), `.prettierrc.json`, `.prettierignore`, `.editorconfig`, `.shellcheckrc`, `.yarnrc.yml`.

### Documentation and agent config

- `AGENTS.md` (this file), symlinked as `CLAUDE.md`. `.github/copilot-instructions.md` carries the same conventions for Copilot.
- `.claude/skills/check-versions/`: a repo-local skill, not a published plugin. Use it to verify version correctness after branch operations.
- `docs/plans/`: planning documents, split into `todo/` and `done/`. Name every plan `YYYY-MM-DD-meaningful-description.md`; the `commit` and `pr` skills enforce that and will rename a plan that lacks a datestamp. `docs/plans/done/` is a historical archive that may not match current code, and is excluded from Prettier so reformatting cannot rewrite the record.
- `docs/reviews/`: branch review documents produced by the `review-branch` skill and consumed by `address-review`.

## Running tests and linters

```bash
make help          # list targets
make lint          # markdownlint + prettier + shellcheck + shfmt + actionlint
make validate      # bin/validate-json + bin/validate-plugins
make build         # regenerate both mirrors
make test-scrut    # run the scrut suites
make test-all      # lint + validate + test-scrut
```

`make format` auto-fixes Markdown and shell formatting. Yarn scripts (`yarn lint`, `yarn lint:fix`, `yarn format`) cover the Markdown half on their own.

Requires `shellcheck`, `shfmt`, `actionlint`, and `scrut` on `PATH`, plus Yarn via Corepack. ShellCheck runs at its default severity so the optional checks in `.shellcheckrc` are actually enforced.

## Plugin layout

A typical skill plugin looks like:

```text
plugins/commit/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── commit/
        └── SKILL.md
```

Skills with longer reference material add a `references/` subdirectory:

```text
plugins/handle-secrets/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── handle-secrets/
        ├── SKILL.md
        └── references/
            ├── anti-patterns.md
            ├── checklist.md
            └── ...
```

A skill can ship executable helpers too. `create-worktree`, `create-worktree-from-issue`, and `resolve-copilot-pr-feedback` each bundle a `scripts/` directory that the skill body invokes:

```text
plugins/create-worktree/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── scripts/
│   └── launch-workmux
└── skills/
    └── create-worktree/
        └── SKILL.md
```

The skill refers to the script as `${CLAUDE_PLUGIN_ROOT}/scripts/launch-workmux`, which Claude Code substitutes with the installed plugin root. Rule 18 of `bin/validate-plugins` checks that every such reference resolves to a shipped, executable file and rejects version-blind locator globs like `**/PLUGIN/scripts/NAME`. Bundled scripts belong in `tests/scrut/`.

A hook plugin that targets all three harnesses (Claude Code, Codex CLI, and OpenCode) carries split manifests, harness-specific entry points, and any helper scripts or assets:

```text
plugins/notify/
├── .claude-plugin/
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── README.md
├── assets/
├── hooks/
│   ├── codex.hooks.json
│   └── hooks.json
├── opencode/
│   └── index.ts
└── scripts/
    ├── focus-pane
    └── notify
```

`hooks/codex.hooks.json` carries only the events Codex understands (a subset of the full Claude Code set in `hooks/hooks.json`). `opencode/index.ts` is the OpenCode TypeScript plugin; `bin/build-opencode-mirror` mirrors it to `dist/opencode/plugins/`. Anything under `assets/` and `scripts/` is bundled with the plugin and reachable from hook commands via `${CLAUDE_PLUGIN_ROOT}`.

## Adding a plugin

1. Create the plugin directory under `plugins/`.
1. Add a `.claude-plugin/plugin.json` with metadata.
1. For hook plugins targeting Codex CLI, add a `.codex-plugin/plugin.json` sibling with a non-empty `hooks` field (usually `"hooks": "./hooks/hooks.json"`). If the Claude Code hook file uses events Codex does not support (`Notification`, `PreCompact`, `SubagentStop`, `SessionEnd`), point the Codex manifest at a separate compatible hooks file. Codex's strict hook schema (`PreToolUse`, `PermissionRequest`, `PostToolUse`, `SessionStart`, `UserPromptSubmit`, `Stop`) rejects the entire hook file if any unsupported event is present. See `plugins/notify/` for the split-manifest pattern.
1. Register the plugin in `.claude-plugin/marketplace.json`.
1. Create a per-plugin `README.md` in the plugin directory.
1. Add a row to the appropriate category table in the root `README.md`. If the plugin requires external tools, add a bullet to the category's `**External tools:**` list.
1. If the plugin bundles a script, add scrut coverage under `tests/scrut/` and register any needed binary path in the `SCRUT_ENV` block in the `Makefile` and the matching `scrut-env` list in `.github/workflows/ci.yml`.
1. Recompute `metadata.version` with `bin/compute-catalog-state` and write it into `.claude-plugin/marketplace.json`.
1. Regenerate the Codex and OpenCode mirrors with `bin/build-codex-marketplace` and `bin/build-opencode-mirror`, and commit the results.
1. Run `make test-all` and fix anything it reports before opening a PR.

## README catalog format

The root `README.md` lists plugins in a compact 3-column table (Plugin, Trigger, What it does) per category, plus a 2-column table for hooks (Plugin, What it does). External-tool requirements appear below each table as a `**External tools:**` bullet list, one bullet per plugin (or per group of plugins sharing the same requirement).

Use the canonical `description` field from `marketplace.json` for the "What it does" column, verbatim, so the README stays a thin mirror of the catalog of record.

The opening paragraph of each `plugins/<name>/README.md` must also match that same `description` verbatim. The plugin README may elaborate freely after that first paragraph, but the first paragraph is the catalog entry. This keeps three surfaces (catalog, root README, plugin README) from drifting into three different accounts of what a plugin does.

The `Trigger` column shows the slash command (for example `/commit`), plus a required argument when the skill takes one (for example `/address-review <path>`). Auto-activation behavior for style-guide skills is not annotated in the table; cover it in the per-plugin README instead.

Categories used in the README, in order: Git, Issues and Worktrees, Code Review, Code Quality, Writing, Scaffolding, CI and Release, Agents. Their `marketplace.json` `category` slugs are the same names lowercased and hyphenated (`git`, `issues-and-worktrees`, `code-review`, `code-quality`, `writing`, `scaffolding`, `ci-and-release`, `agents`).

Hook plugins are the ninth category. They carry `"category": "workflow"` and are listed under their own H2 rather than in one of the tables above.

If a plugin needs a `## Recommended Permissions` section, use a copy-pasteable JSON block (`{"permissions": {"allow": [...]}}`), not prose bullets, and make sure every command the skill actually runs appears in it. A plugin whose skill frontmatter declares a hard dependency (`gh`, `workmux`, `scrut`) also needs a `## Requirements` section.

## Versioning

This repository uses two levels of versioning:

**Marketplace `metadata.version`** (in `.claude-plugin/marketplace.json`):

- This is a catalog state tag, not SemVer.
- Format: `catalog-M<major-sum>-m<minor-sum>-p<patch-sum>-n<plugin-count>`
- `M`: sum of all plugin major versions
- `m`: sum of all plugin minor versions
- `p`: sum of all plugin patch versions
- `n`: number of marketplace plugins
- Do not normalize or carry between components.
- Recompute it from `.plugins[].version` whenever any marketplace plugin version changes. Use `bin/compute-catalog-state` (the canonical implementation, also consumed by `bin/validate-plugins` and `.github/workflows/release.yml`).

**Individual plugin `version`** (in `plugin.json` and mirrored in `marketplace.json`):

- **Patch**: bug fixes, wording tweaks, prompt adjustments
- **Minor**: new capabilities or meaningful behavior changes
- **Major**: breaking changes (for example, removing or restructuring a skill)
- New plugins start at `1.0.0`
- The version in `plugin.json` and its `marketplace.json` entry must always match.

**Version checks on branch operations**: After merging, rebasing, or before creating a PR, use the `check-versions` skill to verify version correctness. Another branch may have already incremented a version, so always check.

## Writing conventions

These apply to everything in the repository: skill bodies, reference material, plugin READMEs, the root README, plan and review documents, commit messages, PR and issue bodies. Skills here are prompts, so their prose is the product.

**No em dashes.** Use a comma, colon, semicolon, parenthetical, or a separate sentence instead. Where a dash genuinely reads best, use a spaced double hyphen (`--`). This is the house style throughout, and the `write-markdown` skill records it for downstream projects too.

**No time or effort estimates**, in any form: hours, days, sprints, "quick", "should be fast", t-shirt sizes, story points. This covers plan documents, issue bodies, and skill instructions that tell an agent to produce estimates. Describe scope instead: what is involved, what depends on what, what is uncertain. Estimates of _runtime_ behavior (algorithmic complexity, latency, throughput, memory) are fine and often useful.

**Neutral technical terminology.** Prefer plain state language over metaphor:

| Avoid                     | Use instead                                                           |
| ------------------------- | --------------------------------------------------------------------- |
| `alive` / `dead`          | `running` / `stopped`, `in use` / `unused`, `reachable`               |
| `kill a process`          | `terminate`, `stop`, `end`                                            |
| `sanity check`            | `validity check`, `plausibility check`, `smoke test`                  |
| `crazy` / `insane`        | `unexpected`, `surprising`, `pathological`                            |
| `dummy data`              | `placeholder data`, `sample data`                                     |
| `whitelist` / `blacklist` | `allowlist` / `blocklist`, `permitted` / `denied`                     |
| `master` / `slave`        | `primary` / `replica`, `leader` / `follower`, `controller` / `worker` |

Genuine proper nouns stay as they are: git's `master` branch when detecting a default branch, a `config/master.key` path, a BibTeX `@mastersthesis` entry.

## License

MIT License. See `LICENSE`.
