# Notify (macOS)

Sends macOS notifications when the agent finishes a task or needs your attention.

**Type:** Hook
**Requires:** [`terminal-notifier`](https://github.com/julienXX/terminal-notifier). Install via [Homebrew](https://brew.sh): `brew install terminal-notifier`

## Installation

### Claude Code

See the [marketplace install instructions](../../README.md#install).

### Codex CLI

```bash
codex plugin marketplace add cboone/cboone-cc-plugins
```

Codex CLI manages this plugin through the marketplace. For a Git-backed marketplace, refresh it after repository updates with `codex plugin marketplace upgrade cboone-cc-plugins` (note that `upgrade` takes the marketplace name `cboone-cc-plugins`, derived from the repository name, not the `owner/repo` identifier used by `add`). For a local-path marketplace, restart Codex after changing plugin files so it can rebuild cached plugin copies from the local source.

Enable plugin-bundled hooks once per host so the `Stop` hook fires:

```bash
codex features enable plugin_hooks
```

Without this flag the plugin installs successfully but the hook is ignored. See [Codex CLI known limitations](../../README.md#codex-cli-known-limitations) for context.

### Using with OpenCode

OpenCode loads the plugin automatically when [`OPENCODE_CONFIG_DIR`](../../README.md#using-with-opencode) is set to this repository's `dist/opencode/` mirror. The TypeScript plugin lives at [`opencode/index.ts`](./opencode/index.ts) and dispatches on OpenCode's event stream rather than Claude Code's named matchers.

OpenCode's event model differs from Claude Code's, so the parity is approximate:

| OpenCode event                    | Notification        | Claude Code equivalent                                     |
| --------------------------------- | ------------------- | ---------------------------------------------------------- |
| `session.idle`                    | Task completed      | `Stop` (with project + branch + last user message)         |
| `permission.updated`              | "Needs permission…" | `Notification` (`permission_prompt`, `elicitation_dialog`) |
| `experimental.session.compacting` | "Auto-compacting…"  | `PreCompact` (`auto`)                                      |

The standalone "Waiting for input…" notification (Claude Code's `Notification:idle_prompt`) is not separately representable: OpenCode's `session.idle` already carries the Stop semantics. The compacting hook depends on an experimental OpenCode API and may break on upgrades.

## What It Does

Delivers native macOS notifications so you can work in other apps while the agent runs.

## When It Fires

### Claude Code

Notifies you when Claude is waiting for input, needs a permission decision, needs your response to a question, is about to auto-compact, or has finished its current task.

| Event                       | Notification                |
| --------------------------- | --------------------------- |
| `Notification` (idle)       | "Waiting for input..."      |
| `Notification` (question)   | "Needs input..."            |
| `Notification` (permission) | "Needs permission..."       |
| `PreCompact` (auto)         | "Auto-compacting..."        |
| `Stop`                      | Task completed notification |

### Codex CLI

Codex's hook schema only supports the `Stop` event for our use cases (the `Notification` and `PreCompact` events do not exist). The plugin therefore wires the turn-completion notification only.

| Event  | Notification                |
| ------ | --------------------------- |
| `Stop` | Task completed notification |

For the cases that fall outside `Stop`, codex provides built-in TUI notifications. Enable them in `~/.codex/config.toml`:

```toml
[tui]
notifications = true
```

See [`tui.notifications`, `tui.notification_method`, `tui.notification_condition`](https://developers.openai.com/codex/config-advanced) for fine-grained control over which terminal events trigger desktop alerts and how they are delivered.

## See Also

- [All plugins](../../README.md)
