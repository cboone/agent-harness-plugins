# Notify (macOS)

Sends macOS notifications when Claude Code or Codex CLI finishes a task or needs your attention.

**Type:** Hook
**Requires:** [`alerter`](https://github.com/vjeantet/alerter) (>= 26.5). Install via [Homebrew](https://brew.sh): `brew install vjeantet/tap/alerter`. Also requires [`jq`](https://jqlang.github.io/jq/) and macOS `tmux` (only used when running inside a tmux session).

## Installation

### Claude Code

See the [marketplace install instructions](../../../../README.md#install).

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

The current stable Codex CLI supports all three events the plugin wires: `Stop`, `UserPromptSubmit`, and `PreToolUse` matching the `request_user_input` question tool. Questions use the same banner format and sound as Claude Code. See [Codex CLI known limitations](../../../../README.md#codex-cli-known-limitations) for what the plugin does not cover.

`PermissionRequest` is intentionally not wired: it runs before automatic approval review decides whether a human prompt is needed. Keep native terminal attention as a fallback, without duplicating plugin completion alerts:

```toml
[tui]
notifications = ["approval-requested", "plan-mode-prompt"]
notification_method = "auto"
notification_condition = "unfocused"
```

Automatic transport selection supports terminals where OSC 9 is unavailable. Native terminal attention does not provide the plugin's customized macOS approval banner. Plan confirmation prompts retain this fallback because they do not use the question tool hook.

### Granting notification permission

`alerter` posts notifications by impersonating Terminal's bundle identity (the v26.4+ default) so it appears under "Terminal" in System Settings → Notifications, where you grant alert permission once. You will not see a separate "alerter" entry. The first notification after install may not appear until permission is granted; the second will.

## What It Does

Delivers native macOS notifications so you can work in other apps while an agent runs. Each notification carries:

- **A per-harness icon**: Claude Code or Codex's app icon. The icon identifies the agent, so titles leave the harness name out.
- **A title that names the action**: `Done`, `Approve <Tool>?` (or `Needs approval` when no tool can be identified), `Question` or `<N> questions`, or `Plan ready for review`.
- **A subtitle that identifies the task**: `<repo> · <task>`. The repository name comes from git's shared repository directory, so a worktree reports its repository rather than its folder; outside git, the folder name is used. The task is the tmux pane title (set by `workmux`, Claude Code or similar) with leading status glyphs such as `✳` removed. When the pane title names no task (a shell, editor, `tmux`, `ssh` or harness name, a shell's `user@host:path` default, or the repository or folder name), the task is the branch suffix, everything after the first `/` (so `feature/improve-notifier` becomes `improve-notifier`).
- **A short body**: per-event content (see matrix below), kept within 140 characters.
  - Completion bodies summarize the agent's final reply. Markdown is removed, and headings, list items and paragraphs read as separate sentences. Fenced code and tables, with or without leading pipes, are dropped, as are status lines (a leading `▸`, or two or more `·` separators) when the reply has prose; a reply without prose uses its status lines, and one with neither uses its first code or table line. An unclosed fence is read as prose. Whole sentences are kept in order. A sentence that no longer fits is cut at a word boundary with `…` when it is the first sentence or at least 40 characters remain; otherwise it and every later sentence are dropped. A reply that is a JSON object with a string `summary` field is summarized from that field.
  - Claude Code permission bodies show a per-tool preview of the call the prompt is about. The Notification payload omits the call's input, so the plugin reads the current turn's tool calls without a result yet from the transcript and chooses one by the payload's message:
    - Interactive sessions send a fixed "Claude needs your permission", which names no tool. The plugin picks the oldest pending call that is not a question or a plan, since Claude Code asks about parallel calls in order. A call that is still running after automatic approval can be older than the one being asked about, so the preview can occasionally name it instead.
    - "Claude Code needs your approval for the plan" posts the plan banner.
    - Sessions driven through the SDK name the tool ("Claude needs your permission to use Bash"), and the plugin picks the oldest pending call with that name, matching MCP display names against `mcp__<server>__<tool>` by server and tool, then by tool.
    - Other messages, such as a sandboxed command's network request, are shown as they are.

    File paths are shown relative to the repository root (or under `~`) and truncated from the left so the file name stays visible. Bash commands drop a leading `cd` into the working directory or repository root. When no call matches, the body is the payload message.

  - Question bodies show the first question, followed by `(+N more)` when there are several.
- **Shared event sounds**: Tink for questions and plans, Funk for permission, and Glass for completion. Claude's idle reminders are disabled.
- **Session-specific groups**: banners from unrelated sessions do not replace one another. Completion alerts fire once until the next user prompt resets the completion marker. Subagent payloads are ignored.
- **Visibility-aware completion**: completion alerts are suppressed when the host terminal application is frontmost and a focused tmux client displays the originating pane. The terminal is identified from `$TERM_PROGRAM`, which must be one of Apple Terminal (`Apple_Terminal`), iTerm2 (`iTerm.app`), Ghostty (`ghostty`), WezTerm (`WezTerm`), VS Code (`vscode`) or Alacritty (`alacritty`). If focus cannot be determined, delivery is preserved. Questions and permissions remain visible regardless of focus.
- **Fire-and-forget delivery**: each `alerter` is stopped a short grace period after launch (see [Notes and caveats](#notes-and-caveats)), so no process waits on the banner. Banners stay in Notification Center, but clicking one does not focus the originating terminal or tmux pane.

## When it fires

### Claude Code

`UserPromptSubmit` resets completion deduplication without posting a banner. The idle reminder hook is not registered. Claude Code also raises a permission prompt for `AskUserQuestion`; that prompt posts nothing, because the question banner already covers it.

| Event                                         | Title                                 | Body                                                     | Sound   |
| --------------------------------------------- | ------------------------------------- | -------------------------------------------------------- | ------- |
| `PreToolUse:AskUserQuestion`                  | `Question` or `<N> questions`         | The first question, then `(+N more)`                     | `Tink`  |
| `Notification:elicitation_dialog`             | `Question`                            | The question text from the payload                       | `Tink`  |
| `Notification:permission_prompt`              | `Approve <Tool>?` or `Needs approval` | The tool preview, or the payload message                 | `Funk`  |
| `Notification:permission_prompt` for the plan | `Plan ready for review`               | The plan's first heading outside code, or its first line | `Tink`  |
| `Stop`                                        | `Done`                                | Summary of `last_assistant_message`                      | `Glass` |

MCP tools appear by their tool name, as in `Approve batch?`, with the server named in the body.

### Codex

| Event                           | Title                         | Body                                 | Sound   |
| ------------------------------- | ----------------------------- | ------------------------------------ | ------- |
| `PreToolUse:request_user_input` | `Question` or `<N> questions` | The first question, then `(+N more)` | `Tink`  |
| `Stop`                          | `Done`                        | Summary of `last_assistant_message`  | `Glass` |

`UserPromptSubmit` resets completion deduplication without posting a banner. Repeated Stop events in the same user turn are suppressed, including their sounds. A Stop hook that requests continuation can still cause the first completion banner before that continuation finishes; the notification plugin does not decide whether other Stop hooks will continue the turn.

## Notes and caveats

- Every event launches `alerter` in a detached process, so the harness is never held up. Completion markers are stored under `${XDG_CACHE_HOME:-$HOME/.cache}/agent-harness-notify/`; deleting this cache resets deduplication.
- A waiting `alerter` 26.5 polls the macOS notification daemon several times a second, and the daemon's load grows quickly with the number of waiting processes. The plugin therefore stops each `alerter` 2 seconds after launch with `SIGKILL`, which leaves the delivered banner and its sound intact; `SIGTERM` and `SIGINT` would make `alerter` remove the banner. Set `NOTIFY_WAIT_LIMIT` in the harness's environment to change the grace period, in whole seconds up to 60, for example if banners go missing under heavy load. Before 4.0.0 this variable bounded how long a banner stayed clickable; larger values are now capped at 60. `alerter`'s own 24-hour timeout remains only as a backstop, and it removes the banner when it expires.
- `scripts/notify` parses under macOS `/bin/bash` 3.2, which `#!/usr/bin/env bash` finds when Homebrew is not on `PATH`. A parse failure exits 2, which Claude Code treats as blocking the hook's event, so the test suite parses it with `/bin/bash`. CI runs on Linux, where `/bin/bash` is bash 5, so only local macOS runs check bash 3.2.
- The transcript-based extractors (pending tool use, and the last assistant message when a Stop payload lacks the field) stream the transcript JSONL newest line first (`tac`, or `tail -r` on stock macOS) into one `jq` pass that stops at the current turn's prompt; a slash-command invocation starts a turn like a typed prompt. Time and memory follow the current turn rather than the file: a 20,000-line turn takes under a tenth of a second. A pending call is reduced to the fields its preview reads, so a 50 MB `Write` takes under half a second.
- The `--app-icon` flag uses a private macOS API that `alerter` keeps working release to release. If a future macOS update breaks it, notifications will still fire but with the default Terminal icon.

## See Also

- [All plugins](../../../../README.md)
