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
