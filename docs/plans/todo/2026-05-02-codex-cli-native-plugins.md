# 2026-05-02: Make plugins installable natively via Codex CLI

## Context

This repository ships Claude Code plugins (skills plus the `notify` hook plugin) and produces a parallel `dist/opencode/` mirror of the skills for [OpenCode](https://opencode.ai), since OpenCode has no native plugin marketplace and instead consumes the `OPENCODE_CONFIG_DIR` environment variable. A separate worktree is in progress to extend the OpenCode mirror with hooks support.

OpenAI's [Codex CLI](https://developers.openai.com/codex/cli) takes the opposite approach: it has its own first-class plugin marketplace system and was designed for Claude Code source compatibility. The relevant compatibility points were verified directly against the openai/codex source (verified at `main` on 2026-05-02):

- **Marketplace discovery** (`codex-rs/core-plugins/src/marketplace.rs`): codex scans both `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json`, returning the first one found. Our existing `.claude-plugin/marketplace.json` is read as-is.
- **Per-plugin manifest discovery** (`codex-rs/utils/plugins/src/plugin_namespace.rs`): codex scans both `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json`, returning the first one found. With both present, `.codex-plugin/` wins. Our existing `.claude-plugin/plugin.json` files are read as-is when no `.codex-plugin/` sibling exists.
- **Hook environment variables** (`codex-rs/hooks/src/engine/discovery.rs`): codex sets `PLUGIN_ROOT`, `CLAUDE_PLUGIN_ROOT` (with the comment `// For OOTB compat with existing plugins that use this env var.`), `PLUGIN_DATA`, and `CLAUDE_PLUGIN_DATA` in the environment of plugin-bundled hook commands. Existing `${CLAUDE_PLUGIN_ROOT}/scripts/...` references resolve correctly with no rewrite.
- **Hook events** (`codex-rs/hooks/src/schema.rs`): codex defines a strict `HookEventNameWire` enum with exactly six variants: `PreToolUse`, `PermissionRequest`, `PostToolUse`, `SessionStart`, `UserPromptSubmit`, `Stop`. Claude-only events (`Notification`, `PreCompact`, `SubagentStop`, `SessionEnd`) are not in the enum and will fail to deserialize, breaking the entire `hooks.json` for that plugin on codex.
- **Plugin install:** `codex plugin marketplace add cboone/agent-harness-plugins` clones the repo into `~/.codex/plugins/cache/agent-harness-plugins/<plugin>/<version>/` and reads our existing `.claude-plugin/marketplace.json`. Codex CLI 0.128.0 does not expose a separate `codex plugin install` subcommand; `marketplace add` is the activation step. Plugin-bundled hooks are additionally gated behind the `plugin_hooks` feature flag (`codex features enable plugin_hooks`).

Net effect: most of this repository is already a working codex plugin marketplace. The `dist/codex/` mirror, `bin/build-codex-mirror`, and `bin/install-codex-hooks` ideas from the previous draft of this plan are unnecessary and have been dropped.

The only real compatibility gap is the `notify` plugin, whose `hooks/hooks.json` uses the Claude-only events `Notification` (3 matchers) and `PreCompact`. Loading it under codex would fail at deserialize time. Hook plugin status:

| Plugin   | Events used                               | Codex status                                                  |
| -------- | ----------------------------------------- | ------------------------------------------------------------- |
| `notify` | `Notification` (×3), `PreCompact`, `Stop` | Codex rejects the file. Needs a codex-specific hooks variant. |

Goal: each plugin in this repo installs cleanly via `codex plugin marketplace add cboone/agent-harness-plugins` (the only plugin install path exposed in Codex CLI 0.128.0). README documents the codex install path. CI verifies dual-manifest consistency for plugins that need it.

## Approach

Lean on codex's native Claude-style compatibility. Touch only the files that need to differ:

1. **Add a `.codex-plugin/plugin.json` for `notify` only**, pointing at a codex-compatible hooks file (`hooks/codex.hooks.json`) that contains the `Stop` event only. Claude Code continues to use the existing `.claude-plugin/plugin.json` and the original `hooks/hooks.json`. All other plugins keep their single `.claude-plugin/plugin.json`.
2. **Document codex's `notify = [...]` config and `tui.notifications` settings** in `plugins/notify/README.md` as the way codex users get the `Notification`/`PreCompact` behavior they would otherwise lose. These are codex-native mechanisms, not part of our plugin.
3. **Update the top-level `README.md`** with a "Using with Codex CLI" section parallel to the OpenCode one, with its own self-contained "Known limitations" subsection (per earlier user direction: do not merge with the OpenCode limitations).
4. **Update `CLAUDE.md`** so the "When adding new plugins" checklist mentions the codex compat consideration (only relevant when a plugin uses Claude-only hook events).
5. **Add CI validation** for dual-manifest consistency: when a plugin has both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, their `name`, `version`, `author`, `homepage`, `repository`, `license`, and `keywords` must match. The `description` and `hooks` fields are allowed to differ (description for system-specific phrasing, hooks because divergence is the whole point). Extend `bin/validate-plugins`.
6. **Bump `notify` plugin version** (minor) and **mirror in `marketplace.json`**, since the notify plugin gains codex-specific behavior. Per `CLAUDE.md` versioning rules: "Minor: new capabilities or meaningful behavior changes."
7. **Recompute `metadata.version` in `marketplace.json`** to reflect the new sum of plugin version components. `bin/validate-plugins` enforces that `metadata.version` matches the computed `catalog-M<sum>-m<sum>-p<sum>-n<count>` value, so any plugin version bump in this PR requires recomputing the catalog state tag.

## Files to create

### `plugins/notify/.codex-plugin/plugin.json`

A minimal codex-specific manifest. Mirrors the existing `.claude-plugin/plugin.json` byte-for-byte except for the addition of an explicit `hooks` field:

```json
{
  "author": { "name": "Christopher Boone" },
  "description": "Notifies you when Codex finishes a task or needs your attention.",
  "homepage": "https://github.com/cboone/agent-harness-plugins",
  "hooks": "./hooks/codex.hooks.json",
  "keywords": ["alerts", "macos", "notifications"],
  "license": "MIT",
  "name": "notify",
  "repository": "https://github.com/cboone/agent-harness-plugins",
  "version": "1.1.0"
}
```

Note: `description` mentions Codex instead of Claude. Everything else matches the Claude manifest. Version bumps to `1.1.0` (see versioning section).

### `plugins/notify/hooks/codex.hooks.json`

Codex-compatible hooks file. Contains only the `Stop` event from the original `hooks.json` (verbatim, including the `${CLAUDE_PLUGIN_ROOT}` reference, which codex sets correctly):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify stop",
            "type": "command"
          }
        ]
      }
    ]
  }
}
```

The dropped `Notification` and `PreCompact` events are documented in `plugins/notify/README.md` as covered by codex's native `notify = [...]` and `tui.notifications` configuration.

## Files to modify

### `plugins/notify/.claude-plugin/plugin.json`

Bump `version` from `1.0.3` to `1.1.0`. No other changes.

### `plugins/notify/README.md`

Add a "Using with Codex CLI" section that explains:

- Install via `codex plugin marketplace add cboone/agent-harness-plugins` (Codex CLI 0.128.0 has no separate `codex plugin install` subcommand). Plugin-bundled hooks also require `codex features enable plugin_hooks`.
- The plugin only wires the `Stop` event on codex (turn-end notification), since codex's hook schema does not include `Notification` or `PreCompact`.
- For idle/elicitation/permission notifications, recommend codex's built-in `tui.notifications = true` (and `tui.notification_method`, `tui.notification_condition`) in `~/.codex/config.toml`.
- Do not mention codex's `notify = [...]` config: it is officially deprecated in the codex source (`codex-rs/config/src/config_toml.rs`: "Deprecated optional external command to spawn for end-user notifications.") in favor of lifecycle hooks. Our `Stop` hook is the same mechanism for new automation.

### `.claude-plugin/marketplace.json`

Bump the `notify` entry's `version` from `1.0.3` to `1.1.0`. No other changes (no `metadata.version` bump).

### `README.md`

Two parallel insertions:

1. **Top-of-README pointer** (after the existing OpenCode subsection at lines 78-86). New "Using with Codex CLI" subsection: a heading, a one-sentence description, a fenced `bash` block with `codex plugin marketplace add cboone/agent-harness-plugins`, and a "see below" pointer linking to the detailed section and to the codex known-limitations subsection.

2. **Tail-of-README detailed section** (new section after the existing OpenCode section at lines 487-500, before `## License`). Sibling to "Using with OpenCode," same depth and structure, **separate** "Known limitations" subsection (no merge with the OpenCode one). Includes:

   - `codex plugin marketplace add` example (Codex CLI 0.128.0 has no separate `codex plugin install` subcommand; `marketplace add` is the activation step). Note that plugin-bundled hooks require `codex features enable plugin_hooks` (the flag is `under development` and `false` by default in 0.128.0).
   - Note that codex reads `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` natively (cite the upstream source paths once for credibility), and sets `CLAUDE_PLUGIN_ROOT` for hook commands "for OOTB compat with existing plugins."
   - **Codex CLI known limitations** subsection (scoped to this section only):
     - **No `Notification` or `PreCompact` events.** Codex has a strict hook event enum (`PreToolUse`, `PermissionRequest`, `PostToolUse`, `SessionStart`, `UserPromptSubmit`, `Stop`). The `notify` plugin therefore wires only the `Stop` hook on codex; for idle / elicitation / permission notifications, enable codex's native `tui.notifications` in `~/.codex/config.toml`.
     - **No custom prompts shipped.** Codex's `~/.codex/prompts/` mechanism is documented as deprecated; the repo only ships skills and hooks.

### `CLAUDE.md`

Update the "When adding new plugins" section (currently 5 numbered steps) with one extra bullet: "If the plugin has hooks that use Claude-only events (`Notification`, `PreCompact`, `SubagentStop`, `SessionEnd`), add a `.codex-plugin/plugin.json` that points at a codex-compatible hooks variant. See `plugins/notify/` for the pattern."

### `bin/validate-plugins`

Extend with a new validation rule: for each plugin directory, if both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` exist, verify that these fields match across the two: `name`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`. The `description` and `hooks` fields are allowed to differ (description for system-specific phrasing; hooks because that's the whole point). Use `jq` (already a dep). Failure prints `::error::` and increments the existing error counter.

## Files explicitly NOT changed

- **`bin/build-opencode-mirror`, `dist/opencode/`, the OpenCode CI step:** unchanged. OpenCode has no native plugin marketplace; the mirror remains the right approach for it.
- **No `dist/codex/`, no `bin/build-codex-mirror`, no `bin/install-codex-hooks`:** none of these get created. Codex's native plugin install handles distribution.
- **`.agents/plugins/marketplace.json`:** not added. Codex reads `.claude-plugin/marketplace.json` directly per the source (`MARKETPLACE_MANIFEST_RELATIVE_PATHS`); a parallel file would just be dead weight to keep in sync.
- **All other plugins' `.claude-plugin/plugin.json`:** unchanged. Codex reads them as-is (verified at `plugin_namespace.rs:DISCOVERABLE_PLUGIN_MANIFEST_PATHS`). No `.codex-plugin/plugin.json` siblings needed except for `notify`.
- **`plugins/notify/hooks/hooks.json`:** unchanged. Claude Code continues to use it.
- **`plugins/notify/scripts/notify`:** unchanged. The same script is used by both systems via `${CLAUDE_PLUGIN_ROOT}` resolution.
- **`.gitignore`, `.prettierignore`, `cli.markdownlint-cli2.jsonc`:** no change.

## Verification

End-to-end sanity, in order:

1. **Static checks pass.** `yarn lint`, `bin/validate-json`, `bin/validate-plugins` (with the new dual-manifest consistency rule) all succeed locally and in CI.
2. **Marketplace structure check.** `jq '.plugins[] | select(.name == "notify") | .version' .claude-plugin/marketplace.json` returns `"1.1.0"`. `cmp <(jq -S 'del(.description, .hooks)' plugins/notify/.claude-plugin/plugin.json) <(jq -S 'del(.description, .hooks)' plugins/notify/.codex-plugin/plugin.json)` returns no diff.
3. **JSON syntax of new files.** `jq . plugins/notify/.codex-plugin/plugin.json plugins/notify/hooks/codex.hooks.json` exits 0.
4. **Local marketplace install (codex CLI required, manual).** From a separate clean directory:
   - `codex plugin marketplace add /path/to/this/repo` (local source).
   - `codex plugin list` shows all our plugins under the `agent-harness-plugins` marketplace. (Codex CLI 0.128.0 has no separate `codex plugin install` subcommand; `marketplace add` is the activation step.)
   - In a codex session run `/skills` and confirm `commit` appears with the expected description.
   - End a turn in codex and confirm the `notify` `Stop` hook fires. Verify codex does not log a deserialize error for `Notification`/`PreCompact` (since the codex-flavored manifest points at `hooks/codex.hooks.json` which has neither).
5. **Negative test for dual-manifest divergence.** Temporarily edit `plugins/notify/.codex-plugin/plugin.json` to change `version` to `9.9.9` and confirm `bin/validate-plugins` flags the inconsistency. Revert.
6. **Remote marketplace install (manual, after merge).** Once merged: `codex plugin marketplace add cboone/agent-harness-plugins` from the repo root URL succeeds.

## Out-of-scope but adjacent

- **GitHub Actions test job that exercises codex install.** Could add later if a codex CLI is reliably installable in CI. Not part of this PR.
- **`.agents/plugins/marketplace.json` parallel catalog.** Codex's source treats it as the preferred path. We could generate it from `.claude-plugin/marketplace.json` for forward-compat, but every byte gets validated by both mechanisms today via the second alternate path; defer until codex deprecates the Claude-style fallback.

## Decisions

- **System-specific phrasing kept in dual `description` fields** (Claude vs Codex). The validate-plugins consistency check ignores `description` so this is fine.
- **Codex's `notify = [...]` config is not documented.** Deprecated upstream; the `Stop` hook covers the same case via the current API.
