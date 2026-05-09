# Prune `update-docs-reminder` and `update-review`

## Context

A skill-usage audit across 397 conversation transcripts (every `agent-harness-plugins` and predecessor `cboone-cc-plugins` worktree project directory in `~/.claude/projects/`) found that neither plugin is being used:

- **`update-review`** (skill, `/update-review`): 0 invocations across all transcripts. The neighbouring `review-branch` and `address-review` plugins are also low-traffic, but `update-review` in particular has never been called.
- **`update-docs-reminder`** (hook, `PostToolUse` on `Bash`): 0 invocations as a Skill tool call (expected; it's event-driven). No git-history evidence of follow-on actions taken in response to its reminders, and the user does not recall acting on it. Treated as effectively inert.

Removing both reduces the marketplace surface area, simplifies the Codex hook story (one fewer plugin gated on the `plugin_hooks` feature flag), and removes a Bash + jq runtime dependency the user no longer benefits from.

This plan removes the plugins from the canonical source, the marketplace catalog of record, both generated mirrors, and the README. Done plans under `docs/plans/done/` that reference the plugins are historical and remain untouched (per project convention: git history is authoritative for archived plans).

## Scope

Two plugins, both fully owned by this repo. No cross-plugin code dependencies (verified via grep). Two passing references in `plugins/create-plugin/skills/create-plugin/references/` use `update-docs-reminder` only as an *example* of a `workflow`-category hook plugin and are easy to swap.

One active plan, `docs/plans/todo/2026-05-02-codex-cli-native-plugins.md`, references `update-docs-reminder` in its test-step description. That plan has already been substantially executed; the reference is descriptive of past validation, not prescriptive of future work, so it stays as-is and will be archived to `done/` on its own schedule.

## Steps

### 1. Delete canonical plugin sources

```text
plugins/update-docs-reminder/
plugins/update-review/
```

Remove each directory in full, including:

- `update-docs-reminder/`: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `hooks/hooks.json`, `opencode/index.ts`, `scripts/check-docs`, `README.md`
- `update-review/`: `.claude-plugin/plugin.json`, `skills/update-review/SKILL.md`, `README.md`

### 2. Remove entries from the catalog of record

File: `.claude-plugin/marketplace.json`

- Delete the `update-docs-reminder` entry (currently lines 530–543, version `1.2.1`).
- Delete the `update-review` entry (currently lines 544–557, version `1.0.2`).
- Recompute `metadata.version` (the catalog state tag) by running `bin/compute-catalog-state` and writing its output back to `metadata.version`. Do not hand-compute. The current value `catalog-M61-m108-p156-n53` will decrease by `M=2, m=2, p=3, n=2`, but rely on the script for the exact string.

### 3. Regenerate the Codex mirror

Run `bin/build-codex-marketplace`. This will:

- Update `.agents/plugins/marketplace.json` to drop both plugin entries and refresh its `metadata.version`.
- Remove `dist/codex/plugins/update-docs-reminder/` and `dist/codex/plugins/update-review/`.

If the script does not delete stale generated directories on its own, remove `dist/codex/plugins/update-docs-reminder/` and `dist/codex/plugins/update-review/` manually after running it.

### 4. Regenerate the OpenCode mirror

Run `bin/build-opencode-mirror`. This will:

- Remove `dist/opencode/plugins/update-docs-reminder.ts`.
- Remove `dist/opencode/skills/update-review/SKILL.md` (and its parent directory if empty).

Same caveat as step 3: if the script doesn't prune stale outputs, delete those paths manually.

### 5. Update root `README.md`

- Remove the `Update Review` row from the **Code Review** table (currently line 77).
- Remove the `Update Docs Reminder` row from the **Hooks** table (currently line 161).
- Remove the `*Update Docs Reminder:* jq` external-tool bullet (currently line 166).
- In the "Enable plugin-bundled hooks" prose (currently line 176), change `the notify and update-docs-reminder hooks fire` to `the notify hook fires`.
- In the Codex CLI known-limitations bullet (currently lines 202–203), change `expecting notify or update-docs-reminder to fire on Codex` to `expecting notify to fire on Codex`.

### 6. Update cross-references in `create-plugin`

These are example lists, not load-bearing references:

- `plugins/create-plugin/skills/create-plugin/references/readme-updates.md` line 67: change the **Hooks** example column from `notify, update-docs-reminder` to `notify`.
- `plugins/create-plugin/skills/create-plugin/references/marketplace-json.md` line 76: change `(e.g., notify, update-docs-reminder)` to `(e.g., notify)`.

After these edits, regenerate the Codex mirror again so the copies under `dist/codex/plugins/create-plugin/...` match.

### 7. Validate

In order:

1. `bin/validate-json` — schema check on the trimmed marketplace files.
2. `bin/validate-plugins` — confirms each remaining plugin's `plugin.json` version matches its marketplace entry, and confirms the recomputed catalog state tag is consistent. Also verifies no orphan references.
3. `bin/version-audit` — sanity check on version fields.
4. `git status` — confirm the only remaining diff is the intended deletions, marketplace edits, README edits, and create-plugin reference edits. No accidental dist drift.
5. Spot-check: `grep -r 'update-docs-reminder\|update-review' --include='*.md' --include='*.json' --include='*.ts'` should return only matches inside `docs/plans/done/` and the active codex-native-plugins plan in `docs/plans/todo/`.

### 8. Commit

Per project convention, commit in logical groups. Suggested split:

- One commit removing `plugins/update-docs-reminder/` and its mirror artifacts.
- One commit removing `plugins/update-review/` and its mirror artifacts.
- One commit updating root `README.md`, `create-plugin` references, and the regenerated `marketplace.json` catalog state tag.

Each commit must be GPG-signed. Use Conventional Commits format, e.g. `chore: remove update-review plugin`.

## Files Modified

| Path | Action |
| --- | --- |
| `plugins/update-docs-reminder/` | delete (recursive) |
| `plugins/update-review/` | delete (recursive) |
| `.claude-plugin/marketplace.json` | edit: remove 2 entries, recompute `metadata.version` |
| `.agents/plugins/marketplace.json` | regenerated |
| `dist/codex/plugins/update-docs-reminder/` | delete (recursive) |
| `dist/codex/plugins/update-review/` | delete (recursive) |
| `dist/codex/plugins/create-plugin/skills/create-plugin/references/readme-updates.md` | regenerated (example list update) |
| `dist/codex/plugins/create-plugin/skills/create-plugin/references/marketplace-json.md` | regenerated (example list update) |
| `dist/opencode/plugins/update-docs-reminder.ts` | delete |
| `dist/opencode/skills/update-review/` | delete (recursive) |
| `README.md` | edit: 5 prose/table changes |
| `plugins/create-plugin/skills/create-plugin/references/readme-updates.md` | edit: example list |
| `plugins/create-plugin/skills/create-plugin/references/marketplace-json.md` | edit: example list |

## Out of Scope

- Other underused skills surfaced by the audit. Each warrants its own decision; this plan deliberately covers only the two the user has approved removing.
- `docs/plans/done/` and the active `2026-05-02-codex-cli-native-plugins.md` plan: historical references stay intact.
