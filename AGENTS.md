# Claude Code Plugins

## Project overview

This repository is the canonical source for a collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugins (skills, commands, and hooks). Committed mirrors under `dist/codex/` and `dist/opencode/` make the same plugins work in [Codex CLI](https://developers.openai.com/codex/cli) and [OpenCode](https://opencode.ai). User-facing details live in `README.md`.

## Where to find things

- `plugins/<name>/`: canonical plugin source. Each plugin has `.claude-plugin/plugin.json`, `README.md`, and either `skills/<name>/SKILL.md` or `hooks/hooks.json` (or both).
- `.claude-plugin/marketplace.json`: catalog of record for the Claude Code marketplace. Source of truth for plugin metadata and versions.
- `.agents/plugins/marketplace.json` and `dist/codex/`: generated Codex CLI marketplace plus mirrored plugin roots. Regenerate with `bin/build-codex-marketplace`.
- `dist/opencode/`: generated OpenCode mirror. Regenerate with `bin/build-opencode-mirror`. CI fails if either generated tree drifts from source.
- `bin/compute-catalog-state`: canonical implementation of the marketplace catalog state tag (`metadata.version` in `marketplace.json`). Consumed by `bin/validate-plugins` and `.github/workflows/release.yml`.
- `bin/version-audit`, `bin/validate-plugins`, `bin/validate-json`: pre-merge validation.
- `docs/plans/`: planning documents. `docs/plans/done/` is a historical archive and may not match current code.

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

A hook plugin that targets both Claude Code and Codex CLI carries split manifests and a script:

```text
plugins/notify/
├── .claude-plugin/
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── README.md
├── hooks/
│   └── hooks.json
└── scripts/
    └── notify
```

## Adding a plugin

1. Create the plugin directory under `plugins/`.
1. Add a `.claude-plugin/plugin.json` with metadata.
1. For hook plugins targeting Codex CLI, add a `.codex-plugin/plugin.json` sibling with a non-empty `hooks` field (usually `"hooks": "./hooks/hooks.json"`). If the Claude Code hook file uses events Codex does not support (`Notification`, `PreCompact`, `SubagentStop`, `SessionEnd`), point the Codex manifest at a separate compatible hooks file. Codex's strict hook schema (`PreToolUse`, `PermissionRequest`, `PostToolUse`, `SessionStart`, `UserPromptSubmit`, `Stop`) rejects the entire hook file if any unsupported event is present. See `plugins/notify/` for the split-manifest pattern.
1. Register the plugin in `.claude-plugin/marketplace.json`.
1. Create a per-plugin `README.md` in the plugin directory.
1. Add a row to the appropriate category table in the root `README.md`. If the plugin requires external tools, add a bullet to the category's `**External tools:**` list.
1. Regenerate the Codex and OpenCode mirrors with `bin/build-codex-marketplace` and `bin/build-opencode-mirror`, and commit the results.

## README catalog format

The root `README.md` lists plugins in a compact 3-column table (Plugin, Trigger, What it does) per category, plus a 2-column table for hooks (Plugin, What it does). External-tool requirements appear below each table as a `**External tools:**` bullet list, one bullet per plugin (or per group of plugins sharing the same requirement).

Use the canonical `description` field from `marketplace.json` for the "What it does" column, verbatim, so the README stays a thin mirror of the catalog of record.

The `Trigger` column shows just the slash command (for example `/commit`). Auto-activation behavior for style-guide skills is not annotated in the table; cover it in the per-plugin README instead.

Categories used in the README, in order: Git, Issues and Worktrees, Code Review, Code Quality, Writing, Scaffolding, CI and Release, Agents. Hooks are listed separately under their own H2.

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

## License

MIT License. See `LICENSE`.
