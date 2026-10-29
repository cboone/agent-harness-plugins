# Notify (macOS)

Sends macOS notifications when Claude Code or Codex CLI finishes a task or needs your attention.

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

The current stable Codex CLI supports all three events the plugin wires: `Stop`, `UserPromptSubmit`, and `PreToolUse` matching the `request_user_input` question tool. Questions use the same banner format and sound as Claude Code. See [Codex CLI known limitations](../../README.md#codex-cli-known-limitations) for what the plugin does not cover.

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
- **A subtitle that identifies the task**: `<repo> · <task>`, or for a [tiered session](#session-tiers) in tmux, the tmux session and window to act in. The repository name comes from git's shared repository directory, so a worktree reports its repository rather than its folder; outside git, the folder name is used. The task is the tmux pane title (set by `workmux`, Claude Code or similar) with leading status glyphs such as `✳` removed. When the pane title names no task (a shell, editor, `tmux`, `ssh` or harness name, a shell's `user@host:path` default, or the repository or folder name), the task is the branch suffix, everything after the first `/` (so `feature/improve-notifier` becomes `improve-notifier`).
- **A short body**: per-event content (see matrix below), kept within 140 characters.
  - Completion bodies summarize the agent's final reply. Markdown is removed, and headings, list items and paragraphs read as separate sentences. Fenced code and tables, with or without leading pipes, are dropped, as are status lines (a leading `▸`, or two or more `·` separators) when the reply has prose; a reply without prose uses its status lines, and one with neither uses its first code or table line. An unclosed fence is read as prose. Whole sentences are kept in order. A sentence that no longer fits is cut at a word boundary with `…` when it is the first sentence or at least 40 characters remain; otherwise it and every later sentence are dropped. A reply that is a JSON object with a string `summary` field is summarized from that field.
  - Claude Code permission bodies show a per-tool preview of the call the prompt is about. The Notification payload omits the call's input, so the plugin reads the current turn's tool calls without a result yet from the transcript and chooses one by the payload's message:
    - Interactive sessions send a fixed "Claude needs your permission", which names no tool. The plugin picks the oldest pending call that is not a question or a plan, since Claude Code asks about parallel calls in order. A call that is still running after automatic approval can be older than the one being asked about, so the preview can occasionally name it instead.
    - "Claude Code needs your approval for the plan" posts the plan banner.
    - Sessions driven through the SDK name the tool ("Claude needs your permission to use Bash"), and the plugin picks the oldest pending call with that name, matching MCP display names against `mcp__<server>__<tool>` by server and tool, then by tool.
    - Other messages, such as a sandboxed command's network request, are shown as they are.

    File paths are shown relative to the repository root (or under `~`) and truncated from the left so the file name stays visible. Bash commands drop a leading `cd` into the working directory or repository root. When no call matches, the body is the payload message.

  - Question bodies show the first question, followed by `(+N more)` when there are several.
- **Event sounds**: Tink for questions and plans, Funk for permission, and Glass for completion by default. An optional [repository sound set](#repository-sound-set) substitutes variants, with [tier subsets](#tier-sound-subsets) for tiered sessions. Claude's idle reminders are disabled.
- **Session-specific groups**: banners from unrelated sessions do not replace one another. Completion alerts fire once until the next user prompt resets the completion marker. Subagent payloads are ignored.
- **Completions you started**: only a turn that began with your prompt posts `Done`. Claude Code turns started by a background task, another session, a scheduled or `/loop` wake, an idle notice or an SDK caller end silently. So do Codex subagents such as guardian reviews, and `codex exec` and `codex review` runs, with one exception in [Notes and caveats](#notes-and-caveats). When the origin is unknown, the banner is posted. Your turn's banner fires when the turn ends, even if its background work is still running. Later results post nothing.
- **Visibility-aware completion**: completion alerts are suppressed when the host terminal application is frontmost and a focused tmux client displays the originating pane. The terminal is identified from `$TERM_PROGRAM`, which must be one of Apple Terminal (`Apple_Terminal`), iTerm2 (`iTerm.app`), Ghostty (`ghostty`), WezTerm (`WezTerm`), VS Code (`vscode`) or Alacritty (`alacritty`). tmux 3.2 and later set `TERM_PROGRAM=tmux` in every pane; the terminal then comes from `__CFBundleIdentifier`, or else from the tmux server's global `TERM_PROGRAM`, both inherited from where the server started. tmux reports a focused client only with `set -g focus-events on`. If focus cannot be determined, delivery is preserved. Questions and permissions remain visible regardless of focus.
- **Fire-and-forget delivery**: each `alerter` is stopped a short grace period after launch (see [Notes and caveats](#notes-and-caveats)), so no process waits on the banner. Banners stay in Notification Center. Clicking one does not focus the originating terminal or tmux pane.

## When it fires

These tables describe untiered sessions; [tiered sessions](#session-tiers) post less.

### Claude Code

`UserPromptSubmit` resets completion deduplication without posting a banner. `Stop` posts only for turns that began with your prompt. `StopFailure` posts an error or refusal banner in every tier, including background turns and a visible pane. The idle reminder hook is not registered. Claude Code also raises a permission prompt for `AskUserQuestion`; that prompt posts nothing, because the question banner already covers it.

| Event                                         | Title                                      | Body                                                     | Sound   |
| --------------------------------------------- | ------------------------------------------ | -------------------------------------------------------- | ------- |
| `PreToolUse:AskUserQuestion`                  | `Question` or `<N> questions`              | The first question, then `(+N more)`                     | `Tink`  |
| `Notification:elicitation_dialog`             | `Question`                                 | The question text from the payload                       | `Tink`  |
| `Notification:permission_prompt`              | `Approve <Tool>?` or `Needs approval`      | The tool preview, or the payload message                 | `Funk`  |
| `Notification:permission_prompt` for the plan | `Plan ready for review`                    | The plan's first heading outside code, or its first line | `Tink`  |
| `Stop`                                        | `Done`                                     | Summary of `last_assistant_message`                      | `Glass` |
| `StopFailure`                                 | `Error: <session>` or `Refusal: <session>` | API error message or fixed refusal description           | `Funk`  |

MCP tools appear by their tool name, as in `Approve batch?`, with the server named in the body.

Failure titles name the session from the transcript, falling back to its ID. Their subtitle is `session: window` in tmux, even without a tier, or the repository/task subtitle outside tmux. An `invalid_request` is labeled `Refusal` only when the current transcript tail contains structured refusal metadata; a new prompt or ordinary reply clears earlier metadata. The hook allows up to two seconds for delayed transcript writes. A refusal body is always `Turn ended in a safeguard refusal.` Unclassified `invalid_request` events also use a fixed API-error description. Other errors use `last_assistant_message`, or `Turn ended in an API error.` when missing. Failure banners use the permission sound role and bypass completion deduplication. Approval waits retain their approval titles.

### Codex

| Event                           | Title                         | Body                                 | Sound   |
| ------------------------------- | ----------------------------- | ------------------------------------ | ------- |
| `PreToolUse:request_user_input` | `Question` or `<N> questions` | The first question, then `(+N more)` | `Tink`  |
| `Stop`                          | `Done`                        | Summary of `last_assistant_message`  | `Glass` |

`UserPromptSubmit` resets completion deduplication without posting a banner. `Stop` posts nothing for subagent sessions or `codex exec` and `codex review` runs, except a run started in a terminal with an option that takes a value before its command; see [Notes and caveats](#notes-and-caveats). Repeated Stop events in the same user turn are suppressed, including their sounds. A Stop hook that requests continuation can still cause the first completion banner before that continuation finishes; the notification plugin does not decide whether other Stop hooks will continue the turn.

Terminal-error and refusal banners for Codex are pending a follow-on watcher PR under the [shared turn-failure plan](https://github.com/cboone/agent-harness-plugins/blob/main/docs/plans/todo/2026-10-28-shared-turn-failure-notifications.md). Codex 0.165.0 does not run `Stop` on terminal API errors. Its `PostModelRequest` event precedes retry resolution, so a failed request does not prove the turn stopped. A watcher can observe terminal app-server `error` events (`willRetry: false`) or `turn/completed` with failed status and distinguish them from approval waits. This release adds the Claude Code half of that paired change.

## Session tiers

When many sessions run in tiers, each in a named tmux window, place each session in a tier so a banner fires only when nothing else brings the event to you:

- `top`: a session that coordinates others and keeps your list of open asks.
- `lead`: a session that asks you things directly, such as a project's conductor or a standing monitor. It adds each ask to the top session's list before asking.
- `worker`: a session that reports to a lead by message and never asks you anything.

A session placed in no tier is untiered and behaves as the rest of this README describes.

### What tiered sessions post

| Event                                              | `top` and `lead`                                                                             | `worker`                  |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------- |
| Completion of a turn your prompt started           | `Done`, unless you answered one of the session's questions or plans in it (Claude Code only) | nothing                   |
| Completion of a turn started any other way         | nothing                                                                                      | nothing                   |
| Permission prompt                                  | posts                                                                                        | posts, titled `Worker: …` |
| Claude Code API error or refusal stop              | posts                                                                                        | posts, titled `Worker: …` |
| Elicitation dialog                                 | posts                                                                                        | posts, titled `Worker: …` |
| Plan approval                                      | nothing                                                                                      | posts, titled `Worker: …` |
| Question (`AskUserQuestion`, `request_user_input`) | nothing                                                                                      | nothing                   |

- A top or lead session's questions and plans post nothing because the top session's list already carries them. Permission prompts and elicitation dialogs post because the harness or an MCP server raises them without an announcement, and only the session's pane can answer them.
- A worker reports by message, so its completions post nothing; it posts only prompts that stop it.
- A Claude Code completion is silent when its turn holds an `AskUserQuestion` or `ExitPlanMode` call you answered or rejected. A call that failed before reaching you does not count. Codex records a failed `request_user_input` call in the same form as an answered one, so a Codex top or lead session always posts its `Done`, which may repeat a question you just answered. A reply typed to a question asked in plain text looks like a new prompt, so that turn's `Done` still posts.
- In tmux, the subtitle is `<tmux session>: <window>`. Icon-font glyphs (Unicode private-use characters), which banners cannot render, are removed from the window name; a window named only with them shows the Claude session name, or the tmux session alone. Outside tmux the subtitle stays `<repo> · <task>`.
- Sounds come from the tier's [sound subset](#tier-sound-subsets) when one is installed.

### Placing sessions

`NOTIFY_TIER=top`, `lead` or `worker` in the environment inherited by Claude Code or Codex CLI places a session directly, for example from a launcher; other values are ignored. Otherwise the first matching rule in `${XDG_CONFIG_HOME:-$HOME/.config}/agent-harness-notify/tiers` decides, and a session that matches none stays untiered. The plugin ships no rules.

Each rule is a line `<tier> <field> <pattern>`. The pattern is the rest of the line, without its surrounding whitespace. Bash `=~` matches it against the field as a POSIX extended regular expression:

| Field     | Matches                                                                                                 |
| --------- | ------------------------------------------------------------------------------------------------------- |
| `window`  | the tmux window name                                                                                    |
| `session` | the tmux session name                                                                                   |
| `server`  | the tmux server name: the basename of the socket in `$TMUX`, `default` unless `tmux -L` names one       |
| `name`    | the Claude session name, set with `claude --name` or a rename, read from the transcript; Codex has none |
| `dir`     | `$CLAUDE_PROJECT_DIR`, or the hook's working directory                                                  |

```text
# tier    field    pattern
top       window   ^coordinator$
worker    dir      ^/Users/sample/projects/[^/]+/[^/]+/[^/]+
lead      name     ^[[:upper:]][[:upper:][:digit:] /&-]*$
lead      window   ^conductor$
```

- Lines that do not start with a tier name, including `#` comment lines, are skipped. Lines with an unknown field or a pattern bash cannot compile are also skipped.
- A field that is empty or unavailable, such as `window` outside tmux, matches nothing.
- Write a significant trailing space as `[ ]`, since editors strip trailing whitespace, and prefer classes such as `[[:upper:]]` to ranges such as `[A-Z]`, whose meaning depends on the locale.

To check a tiers file, run the installed plugin's `scripts/notify explain` by its full path in a session's pane without changing directory, for example with `!` at a Claude Code prompt. This gives `dir` rules the same directory as the hooks. It prints the tier, the matching rule, the session name, the subtitle and the sound for each role. It reads the session name from the transcript of `$CLAUDE_CODE_SESSION_ID`, or from a transcript path passed as its argument. It fails, naming the file, when the tiers file or a transcript argument cannot be read. When `$CLAUDE_CODE_SESSION_ID` is set but no readable transcript turns up, it fails, naming the session and the folder searched. The hooks treat an unreadable tiers file as absent.

## Repository sound set

Set `NOTIFY_SOUND_SET=<prefix>` in the environment inherited by Claude Code or Codex CLI to enable a separately installed sound set. Unset or empty keeps the default sounds. The prefix must match `^[A-Za-z0-9._-]+$`; invalid values are ignored.

Install files in `~/Library/Sounds` named `<prefix>-<role>-<n>.<ext>`, where `<ext>` is `aiff`, `wav` or `caf`. Each role's indices start at `0` and continue without gaps:

| Role         | Replaces | Events                                   |
| ------------ | -------- | ---------------------------------------- |
| `stop`       | Glass    | Task completion                          |
| `permission` | Funk     | Permission requests                      |
| `attention`  | Tink     | Questions, elicitation and plan approval |

For example, `NOTIFY_SOUND_SET=Chord` uses files such as `Chord-stop-0.aiff`, `Chord-permission-0.wav` and `Chord-attention-0.caf`. Add matching indices for each pitch or timbre variant. Sound files are produced and installed separately; this plugin does not include them.

The plugin counts indices per role until the first missing index, accepting any supported extension and counting an index only once. A role without index `0` falls back to its built-in sound. Files after a gap are ignored.

Selection uses POSIX `cksum` on the repository name's bytes without a trailing newline, modulo the role's count. The name is the same as the subtitle's repository name, shared across worktrees; outside Git, the folder name is used. Matching variant counts across roles select the same index, allowing a repository's sounds to share a pitch. Different counts use the same hash modulo their respective counts. Different repositories can select the same variant. Selection needs no saved state; changing the name or variant count can change the selection.

The selected name is passed to `alerter --sound` without an extension. macOS searches `~/Library/Sounds`, then `/Library/Sounds`, then `/System/Library/Sounds`. The plugin counts set files only in `~/Library/Sounds`. System Settings > Notifications > Terminal must allow sounds.

### Tier sound subsets

A [tiered session](#session-tiers) first looks for its tier's subset, `<prefix>-<tier>-<role>-<n>.<ext>`, such as `Chord-worker-permission-0.aiff`, counted the same way. A role without index `0` in the subset falls back to the plain set, then to its built-in sound. In tmux, a tiered session hashes its subtitle, `<tmux session>: <window>`, instead of the repository name, so sessions in one repository can play different variants. Untiered sessions use the plain set and the repository name as described above.

## Notes and caveats

- Every event launches `alerter` in a detached process, so the harness is never held up. Completion markers are stored under `${XDG_CACHE_HOME:-$HOME/.cache}/agent-harness-notify/`; deleting this cache resets deduplication.
- A waiting `alerter` 26.5 polls the macOS notification daemon several times a second, and the daemon's load grows quickly with the number of waiting processes. The plugin therefore stops each `alerter` with `SIGKILL` 2 seconds after launch. `SIGKILL` leaves the delivered banner and its sound intact; `SIGTERM` and `SIGINT` would make `alerter` remove the banner. Set `NOTIFY_WAIT_LIMIT` in the harness's environment to change the grace period, in whole seconds up to 60, for example if banners go missing under heavy load. `alerter`'s own 24-hour timeout is only a backstop; it removes the banner when it expires.
- `scripts/notify` parses under macOS `/bin/bash` 3.2, which `#!/usr/bin/env bash` finds when Homebrew is not on `PATH`. A parse failure exits 2, which Claude Code treats as blocking the hook's event, so the test suite parses it with `/bin/bash`. CI runs on Linux, where `/bin/bash` is bash 5, so only local macOS runs check bash 3.2.
- The transcript-based extractors (pending tool use, the turn's origin, and the last assistant message when a Stop payload lacks the field) stream the transcript JSONL newest line first (`tac`, or `tail -r` on stock macOS) into one `jq` pass that stops at the current turn's prompt; a slash-command invocation starts a turn like a typed prompt. The origin pass reads `turnOrigin`, or `origin.kind` and `isMeta` in older transcripts, from records sharing the turn's `promptId`. It stops at the previous turn's newest record, or at the current turn's prompt without `promptId`s. Time and memory follow the current turn rather than the file: a 20,000-line turn takes under a tenth of a second. A pending call is reduced to the fields its preview reads, so a 50 MB `Write` takes under half a second.
- A Codex session's source is in the `session_meta` record on its transcript's first line: `cli`, `exec` or a subagent. Resuming a session keeps its original source, so the plugin also reads the command line of the Codex process running the hook. `codex exec`, its alias `e` and `codex review` are headless, and any other Codex command is interactive. `ps` joins arguments with spaces, so the command is certain only when it is the first argument after any plain flags. After an option that may take a value containing spaces, or with a prompt instead of a command, the process's terminal decides. The interactive TUI has a terminal; a run an agent starts does not. A `codex exec` started in a terminal with such options before `exec` therefore posts its banner. A subagent source always ends silently. Otherwise, the transcript's `cli` or `exec` decides only when the parent is not Codex. `codex exec --ephemeral` writes no transcript.
- A tiered session reads its tmux session and window names with one `tmux` call, removes icon-font glyphs with one `jq` call, and finds its session name with `grep` only when a `name` rule or a glyph-only window needs it, which keeps a large transcript out of `jq`. With no tiers file and no `NOTIFY_TIER`, a session only checks that the file is absent.
- `alerter` replaces or removes banners by listing the notifications delivered as Terminal, and a later process sees none of them, so banners with the same group do not replace one another and `alerter --remove` has no effect.
- The `--app-icon` flag uses a private macOS API that `alerter` keeps working release to release. If a future macOS update breaks it, notifications will still fire but with the default Terminal icon.

## See Also

- [All plugins](../../README.md)
