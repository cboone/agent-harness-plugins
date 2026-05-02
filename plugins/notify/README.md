# Notify (macOS)

Sends macOS notifications when Claude finishes a task or needs your attention.

**Type:** Hook
**Requires:** [`terminal-notifier`](https://github.com/julienXX/terminal-notifier). Install via [Homebrew](https://brew.sh): `brew install terminal-notifier`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Notify** from the available plugins.

### Using with OpenCode

OpenCode loads the plugin automatically when [`OPENCODE_CONFIG_DIR`](../../README.md#using-with-opencode) is set to this repository's `dist/opencode/` mirror. The TypeScript plugin lives at [`opencode/index.ts`](./opencode/index.ts) and dispatches on OpenCode's event stream rather than Claude Code's named matchers.

OpenCode's event model differs from Claude Code's, so the parity is approximate:

| OpenCode event                     | Notification          | Claude Code equivalent                                     |
| ---------------------------------- | --------------------- | ---------------------------------------------------------- |
| `session.idle`                     | Task completed        | `Stop` (with project + branch + last user message)         |
| `permission.updated`               | "Needs permission…"   | `Notification` (`permission_prompt`, `elicitation_dialog`) |
| `experimental.session.compacting`  | "Auto-compacting…"    | `PreCompact` (`auto`)                                      |

The standalone "Waiting for input…" notification (Claude Code's `Notification:idle_prompt`) is not separately representable: OpenCode's `session.idle` already carries the Stop semantics. The compacting hook depends on an experimental OpenCode API and may break on upgrades.

## What It Does

Delivers native macOS notifications so you can work in other apps while Claude runs. Notifies you when Claude is waiting for input, needs a permission decision, needs your response to a question, is about to auto-compact, or has finished its current task.

## When It Fires

| Event                       | Notification                |
| --------------------------- | --------------------------- |
| `Notification` (idle)       | "Waiting for input..."      |
| `Notification` (question)   | "Needs input..."            |
| `Notification` (permission) | "Needs permission..."       |
| `PreCompact` (auto)         | "Auto-compacting..."        |
| `Stop`                      | Task completed notification |

## See Also

- [All plugins](../../README.md)
