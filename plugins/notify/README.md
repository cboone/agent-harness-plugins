# Notify (macOS)

Sends macOS notifications when Claude Code, OpenCode, or Codex CLI finishes a task or needs your attention.

**Type:** Hook
**Requires:** [`alerter`](https://github.com/vjeantet/alerter) (>= 26.5). Install via [Homebrew](https://brew.sh): `brew install vjeantet/tap/alerter`. Also requires [`jq`](https://jqlang.github.io/jq/) and macOS `tmux` (only used when running inside a tmux session).

## Installation

### Claude Code

See the [marketplace install instructions](../../README.md#install).

### Using with Codex CLI

Register the marketplace and install the plugin:

```bash
codex plugin marketplace add cboone/agent-harness-plugins
codex plugin add notify@agent-harness-plugins
```

Codex runs plugin hooks only after you review and trust them; installing the plugin does not trust its hooks, and no feature flag is involved. Open `/hooks` in a Codex session, review the `notify` hooks, and trust them. Codex records trust against each hook definition's hash, so when an upgrade changes a `notify` hook, Codex skips it until you review and trust it again in `/hooks`.

Refresh the installed plugin after repository updates:

```bash
codex plugin marketplace upgrade agent-harness-plugins
```

The current stable Codex CLI supports all four events the plugin wires: `Stop`, `UserPromptSubmit`, `PreToolUse` matching the `request_user_input` question tool, and `PreCompact` matching `auto`. Questions and automatic compaction use the same banner sounds and click routing as Claude Code. See [Codex CLI known limitations](../../README.md#codex-cli-known-limitations) for what the plugin does not cover.

`PermissionRequest` is intentionally not wired: it runs before automatic approval review decides whether a human prompt is needed. Keep native terminal attention as a fallback, without duplicating plugin completion alerts:

```toml
[tui]
notifications = ["approval-requested", "plan-mode-prompt"]
notification_method = "auto"
notification_condition = "unfocused"
```

Automatic transport selection supports terminals where OSC 9 is unavailable. Native terminal attention does not provide the plugin's customized macOS approval banner. Plan confirmation prompts retain this fallback because they do not use the question tool hook.

### Using with OpenCode

OpenCode loads the plugin automatically when [`OPENCODE_CONFIG_DIR`](../../README.md#using-with-opencode) is set to this repository's `dist/opencode/` mirror. The TypeScript plugin lives at [`opencode/index.ts`](./opencode/index.ts) and dispatches on OpenCode's event stream rather than Claude Code's named matchers.

OpenCode's event model differs from Claude Code's, so the parity is approximate:

| OpenCode event                    | Notification        | Claude Code equivalent                                     |
| --------------------------------- | ------------------- | ---------------------------------------------------------- |
| `session.idle`                    | Task completed      | `Stop` (with project + branch + last user/assistant turn)  |
| `permission.updated`              | "Needs permission…" | `Notification` (`permission_prompt`, `elicitation_dialog`) |
| `experimental.session.compacting` | "Auto-compacting…"  | `PreCompact` (`auto`)                                      |

The standalone "Waiting for input…" notification (Claude Code's `Notification:idle_prompt`) is not separately representable: OpenCode's `session.idle` already carries the Stop semantics. The compacting hook depends on an experimental OpenCode API and may break on upgrades.

### Granting notification permission

`alerter` posts notifications by impersonating Terminal's bundle identity (the v26.4+ default) so it appears under "Terminal" in System Settings → Notifications, where you grant alert permission once. You will not see a separate "alerter" entry. The first notification after install may not appear until permission is granted; the second will.

## What It Does

Delivers native macOS notifications so you can work in other apps while an agent runs. Each notification carries:

- **A per-harness icon**: Claude Code, OpenCode, or Codex's app icon.
- **A subtitle that identifies the task**: when running inside tmux with a custom pane title (set by `workmux` or similar), the subtitle is `<project> · <pane title>`. Otherwise, `<project> · <branch suffix>`, where the branch suffix is everything after the first `/` (so `feature/improve-notifier` becomes `improve-notifier`).
- **An informative body**: per-event content (see matrix below). Claude Code permission events show a per-tool preview (the Bash command, the file path being edited, etc.) reconstructed from the most recent `tool_use` block in the transcript, since the Notification payload itself omits tool details. OpenCode permission events use OpenCode's pre-computed `title`, falling back to `pattern` or per-tool `metadata`. Claude Code and OpenCode Stop events show `<last user message> → <last assistant message tail>`; the Claude Code assistant tail comes from the Stop payload's `last_assistant_message` rather than from a transcript walk. Codex Stop is the last assistant message alone, also taken from the payload.
- **Shared event sounds**: Tink for questions, Funk for permission, Pop for automatic compaction, and Glass for completion. Claude's idle reminders are disabled.
- **Session-specific groups**: banners from unrelated sessions do not replace one another. Claude and Codex completion alerts fire once until the next user prompt resets the completion marker. Subagent payloads are ignored.
- **Visibility-aware completion**: completion alerts are suppressed when the host terminal application is active and a tmux client displays the originating pane. If focus cannot be determined, delivery is preserved. Questions, permissions, and compaction remain visible regardless of focus.
- **Click-to-focus**: clicking the body of any notification activates the originating terminal app (auto-detected from `$TERM_PROGRAM`, supports Apple Terminal, iTerm2, Ghostty, WezTerm, VSCode, Alacritty) and, if you were inside tmux when the hook fired, switches the tmux client to the originating session, window, and pane.

## When it fires

### Claude Code

`UserPromptSubmit` resets completion deduplication without posting a banner. `PreToolUse:AskUserQuestion` posts a question banner using the actual question text and Tink sound. The idle reminder hook is not registered.

| Event                             | Title                      | Body                                                     | Sound   |
| --------------------------------- | -------------------------- | -------------------------------------------------------- | ------- |
| `Notification:elicitation_dialog` | `Claude Code · Question`   | The actual question text from the payload                | `Tink`  |
| `Notification:permission_prompt`  | `Claude Code · Permission` | `<Tool>: <preview>` (subtitle is suffixed with the tool) | `Funk`  |
| `PreCompact:auto`                 | `Claude Code · Compacting` | `Auto-compacting context`                                | `Pop`   |
| `Stop`                            | `Claude Code · Done`       | `<last user message> → <last assistant message tail>`    | `Glass` |

### Codex

| Event                           | Title                | Body                                      | Sound   |
| ------------------------------- | -------------------- | ----------------------------------------- | ------- |
| `PreToolUse:request_user_input` | `Codex · Question`   | Question text from tool input             | `Tink`  |
| `PreCompact:auto`               | `Codex · Compacting` | `Auto-compacting context`                 | `Pop`   |
| `Stop`                          | `Codex · Done`       | `last_assistant_message` from the payload | `Glass` |

`UserPromptSubmit` resets completion deduplication without posting a banner. Repeated Stop events in the same user turn are suppressed, including their sounds. A Stop hook that requests continuation can still cause the first completion banner before that continuation finishes; the notification plugin does not decide whether other Stop hooks will continue the turn.

### OpenCode

| Event                             | Title                   | Body                                                                              | Sound   |
| --------------------------------- | ----------------------- | --------------------------------------------------------------------------------- | ------- |
| `permission.updated`              | `OpenCode · Permission` | OpenCode's pre-computed `title`, falling back to `pattern` or per-tool `metadata` | `Funk`  |
| `session.error`                   | `OpenCode · Error`      | `error.data.message` (or the error name)                                          | `Funk`  |
| `experimental.session.compacting` | `OpenCode · Compacting` | `Auto-compacting context`                                                         | `Pop`   |
| `session.idle`                    | `OpenCode · Done`       | `<last user message> → <last assistant message tail>`                             | `Glass` |

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

**Switch the tmux client** if the hook fired inside tmux. Claude and Codex capture immutable session, window, and pane IDs using an explicit `TMUX_PANE` target. The detached process retains the originating tmux socket environment. Existing OpenCode callers using names and indexes remain supported.

Failures (closed pane, no client attached, missing terminal app) are silent: clicking a notification should never produce a visible error.

## Notes and caveats

- `alerter` blocks waiting for user interaction, so every event launches it in a detached subshell. The harness is never held up. Each invocation has a 24-hour timeout to bound background notification processes. Completion markers are stored under `${XDG_CACHE_HOME:-$HOME/.cache}/agent-harness-notify/`; deleting this cache resets deduplication.
- The transcript-based extractors (last user message, last assistant message tail, pending tool use) iterate the transcript JSONL. Performance is fine for typical sessions; very long transcripts may add a small delay before the notification appears.
- The `--app-icon` flag uses a private macOS API that `alerter` keeps working release to release. If a future macOS update breaks it, notifications will still fire but with the default Terminal icon.

## See Also

- [All plugins](../../README.md)
