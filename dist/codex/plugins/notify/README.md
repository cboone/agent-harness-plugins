# Notify (macOS)

Sends rich, harness-aware macOS notifications when Claude Code, OpenCode, or Codex CLI finishes a task or needs your attention. Click a notification to focus the originating terminal app and tmux pane.

**Type:** Hook
**Requires:** [`alerter`](https://github.com/vjeantet/alerter) (>= 26.5). Install via [Homebrew](https://brew.sh): `brew install vjeantet/tap/alerter`. Also requires [`jq`](https://jqlang.github.io/jq/) and macOS `tmux` (only used when running inside a tmux session).

## Installation

### Claude Code

See the [marketplace install instructions](../../../../README.md#install).

### Using with Codex CLI

```bash
codex plugin marketplace add cboone/cboone-cc-plugins
```

Enable plugin-bundled hooks once per host so the `Stop` hook fires:

```bash
codex features enable plugin_hooks
```

Without this flag the plugin installs successfully but the hook is silently ignored. See [Codex CLI known limitations](../../../../README.md#codex-cli-known-limitations) for context.

Refresh the marketplace after repository updates:

```bash
codex plugin marketplace upgrade cboone-cc-plugins
```

Codex's hook event enum does not include `Notification` or `PreCompact`, so the plugin only wires the `Stop` event on Codex. `PermissionRequest` is intentionally not wired: that hook runs in the automatic-policy path before Codex's user approval UI is shown, not as a user-facing prompt, so notifying on it would alert the human about decisions Codex's internal approver is already making. For idle / elicitation / compact-style banners and approval prompts, enable Codex's native `tui.notifications = true` in `~/.codex/config.toml` (the two are complementary; both can run at once).

### Using with OpenCode

OpenCode loads the plugin automatically when [`OPENCODE_CONFIG_DIR`](../../../../README.md#using-with-opencode) is set to this repository's `dist/opencode/` mirror. The TypeScript plugin lives at [`opencode/index.ts`](./opencode/index.ts) and dispatches on OpenCode's event stream rather than Claude Code's named matchers.

OpenCode's event model differs from Claude Code's, so the parity is approximate:

| OpenCode event                    | Notification        | Claude Code equivalent                                     |
| --------------------------------- | ------------------- | ---------------------------------------------------------- |
| `session.idle`                    | Task completed      | `Stop` (with project + branch + last user/assistant turn)  |
| `permission.updated`              | "Needs permission…" | `Notification` (`permission_prompt`, `elicitation_dialog`) |
| `experimental.session.compacting` | "Auto-compacting…"  | `PreCompact` (`auto`)                                      |

The standalone "Waiting for input…" notification (Claude Code's `Notification:idle_prompt`) is not separately representable: OpenCode's `session.idle` already carries the Stop semantics. The compacting hook depends on an experimental OpenCode API and may break on upgrades.

### Granting notification permission

`alerter` posts notifications by impersonating Terminal's bundle identity (the v26.4+ default) so it appears under "Terminal" in System Settings → Notifications, where you grant alert permission once. You will not see a separate "alerter" entry. The first notification after install may not appear until permission is granted; the second will.

## What it does

Delivers native macOS notifications so you can work in other apps while an agent runs. Each notification carries:

- **A per-harness icon**: Claude Code, OpenCode, or Codex's app icon.
- **A subtitle that identifies the task**: when running inside tmux with a custom pane title (set by `workmux` or similar), the subtitle is `<project> · <pane title>`. Otherwise, `<project> · <branch suffix>`, where the branch suffix is everything after the first `/` (so `feature/improve-notifier` becomes `improve-notifier`).
- **An informative body**: per-event content (see matrix below). For permission events, the body includes a per-tool preview (the Bash command, the file path being edited, the URL being fetched, etc.). For Claude Code and OpenCode Stop events, the body is `<last user message> → <last assistant message tail>`. Codex Stop is the last assistant message alone, taken directly from the hook payload's `last_assistant_message`.
- **A per-event sound** (Tink for Claude Code idle/elicit and Codex done, Funk for permission, Pop for auto-compact, Glass for Claude Code and OpenCode done). Codex Stop uses the soft Tink rather than the louder Glass because Codex fires `Stop` once per "no follow-up needed" sampling cycle in its turn loop, so a single user turn can produce multiple notifications when Stop hooks request continuation. Each Stop updates the same notification group, so successive firings replace the previous banner in place rather than stacking.
- **A per-event group** so a fresh notification dismisses any prior notification of the same kind, instead of stacking.
- **Click-to-focus**: clicking the body of any notification activates the originating terminal app (auto-detected from `$TERM_PROGRAM`, supports Apple Terminal, iTerm2, Ghostty, WezTerm, VSCode, Alacritty) and, if you were inside tmux when the hook fired, switches the tmux client to the originating session, window, and pane.

## When it fires

### Claude Code

| Event                             | Title                      | Body                                                       | Sound   |
| --------------------------------- | -------------------------- | ---------------------------------------------------------- | ------- |
| `Notification:idle_prompt`        | `Claude Code · Idle`       | Last assistant message tail (fallback `Waiting for input`) | `Tink`  |
| `Notification:elicitation_dialog` | `Claude Code · Question`   | The actual question text from the payload                  | `Tink`  |
| `Notification:permission_prompt`  | `Claude Code · Permission` | `<Tool>: <preview>` (subtitle is suffixed with the tool)   | `Funk`  |
| `PreCompact:auto`                 | `Claude Code · Compacting` | `Auto-compacting context`                                  | `Pop`   |
| `Stop`                            | `Claude Code · Done`       | `<last user message> → <last assistant message tail>`      | `Glass` |

### Codex

| Event  | Title          | Body                                      | Sound  |
| ------ | -------------- | ----------------------------------------- | ------ |
| `Stop` | `Codex · Done` | `last_assistant_message` from the payload | `Tink` |

Codex fires `Stop` once per "no follow-up needed" sampling cycle in its turn loop (`codex-rs/core/src/session/turn.rs`), so a single user turn may produce multiple Stop notifications when Stop hooks request continuation. The notification uses the soft Tink sound and reuses the `codex-stop` group, so successive firings within one turn dismiss the prior banner rather than stacking. Click the body to focus the originating pane.

### OpenCode

| Event                             | Title                   | Body                                                  | Sound   |
| --------------------------------- | ----------------------- | ----------------------------------------------------- | ------- |
| `permission.updated`              | `OpenCode · Permission` | `<Tool>: <preview>`                                   | `Funk`  |
| `experimental.session.compacting` | `OpenCode · Compacting` | `Auto-compacting context`                             | `Pop`   |
| `session.idle`                    | `OpenCode · Done`       | `<last user message> → <last assistant message tail>` | `Glass` |

## Click-to-focus details

When you click the body of a notification, the plugin runs [`scripts/focus-pane`](./scripts/focus-pane) with the captured terminal program and tmux state. The script does two things.

**Activate the host terminal app** via `osascript -e 'tell application id "<bundle-id>" to activate'`. Bundle IDs are derived from `$TERM_PROGRAM`:

| `$TERM_PROGRAM`  | App          |
| ---------------- | ------------ |
| `Apple_Terminal` | Terminal.app |
| `iTerm.app`      | iTerm2       |
| `ghostty`        | Ghostty      |
| `WezTerm`        | WezTerm      |
| `vscode`         | VS Code      |
| `alacritty`      | Alacritty    |
| (anything else)  | Terminal.app |

**Switch the tmux client** if the hook fired inside tmux: `tmux switch-client -t <session> \; select-window -t <session>:<window> \; select-pane -t <session>:<window>.<pane>`.

Failures (closed pane, no client attached, missing terminal app) are silent: clicking a notification should never produce a visible error.

## Notes and caveats

- `alerter` blocks waiting for user interaction, so every event launches it in a detached subshell. The harness is never held up. Each invocation has a 24-hour timeout to prevent orphaned processes from accumulating.
- The transcript-based extractors (last user message, last assistant message tail, pending tool use) iterate the transcript JSONL. Performance is fine for typical sessions; very long transcripts may add a small delay before the notification appears.
- The `--app-icon` flag uses a private macOS API that `alerter` keeps working release to release. If a future macOS update breaks it, notifications will still fire but with the default Terminal icon.

## See also

- [All plugins](../../../../README.md)
