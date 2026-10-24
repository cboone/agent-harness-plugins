# Attention Log

Records every time a Claude Code session waits on a person for permission, or stops because an API error or a safeguard refusal ended its turn, in one JSON Lines file that watchers read.

**Type:** Hook
**Requires:** [`jq`](https://jqlang.github.io/jq/), and `tmux` inside a tmux session.

## Installation

See the [marketplace install instructions](../../../../README.md#install). The plugin records Claude Code sessions only: its Codex manifest registers no hooks (see [Codex CLI known limitations](../../../../README.md#codex-cli-known-limitations)).

## What It Does

When many sessions run at once, mostly in auto mode, a permission dialog can sit unseen in a pane nobody is watching, and a session stopped by an API error or a safeguard refusal stays stopped until someone notices. This plugin appends one line to `~/.local/state/attention-log/events.jsonl` each time a session starts or stops waiting on a person, so a pane monitor, a coordinating session or a person can see which sessions need attention without reading every pane.

It posts no notifications; [Notify](../notify/README.md) covers banners. It never delays a session and never answers a permission dialog: every hook runs async, prints nothing on stdout and exits 0. A hook writes to stderr only to say it could not record an event, such as when `jq` is missing.

## When It Fires

| Hook                                                                     | Event                                                                                         |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| `PermissionRequest`, every tool                                          | `permission_request`, which opens a state                                                     |
| `Notification` type `permission_prompt`, after about six seconds waiting | `permission_waiting`, repeating the open request's `id`, or opening a state when none is open |
| `StopFailure`                                                            | `api_error_stop` or `refusal_stop`, which opens a state                                       |
| `PostToolUse` or `PostToolUseFailure` for the requested tool             | `cleared` with the request's `id`                                                             |
| `UserPromptSubmit`, `Stop` or `SessionEnd`                               | `cleared` with `id` `"*"`, closing every open state of a session                              |
| `Notification` types `elicitation_dialog` and `elicitation_url_dialog`   | `elicitation`, an MCP server's dialog                                                         |
| `PermissionDenied`, auto mode only                                       | `auto_denied`: the classifier blocked a call without a dialog                                 |
| `SessionStart`                                                           | Nothing; keeps the session's title for later events                                           |

- **Prompts without a request.** A sandbox's network prompt raises no `PermissionRequest`, so its `permission_waiting` opens a state with its own `id`. Later notifications for that prompt repeat the `id`.
- **Requests that cannot prompt.** `PermissionRequest` also fires for calls that cannot show a dialog, such as a background subagent's, which are then denied. Those events carry an `agent_id`.
- **Refusals.** A safeguard refusal that ends a turn reaches `StopFailure` as an `invalid_request` error. The hook labels it `refusal_stop` when the session transcript's last records show the refusal, reading record types and flags only, and `api_error_stop` otherwise. `Stop` does not fire for a turn that `StopFailure` ended.
- **Closing states.** A dismissed dialog can leave no hook behind, so the next prompt, turn end or session end closes every state the session still has open. An error or refusal stop stays open until the next prompt or session end.

## Event format

Readers parse the file directly as a versioned contract. Changing an event name, a field or the file layout breaks that contract and needs a new `v`.

### File

- `~/.local/state/attention-log/events.jsonl`, append-only, one JSON object per line. Each line is written whole in one append of under 4 KB, so lines from concurrent sessions never interleave.
- At 5 MiB the file is renamed to `events.jsonl.1`, replacing the previous one. It is never copied and truncated, so a reader following the file's inode and offset carries on across a rotation.
- `ATTENTION_LOG_DIR` replaces `~/.local/state/attention-log` for every command, for tests and trials.

### Fields

Every line has `v`, `ts`, `event`, `host`, `harness` and `session_id`. Other fields appear only when they have a value.

| Field               | Value                                                                                                                                                                |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `v`                 | `1`                                                                                                                                                                  |
| `ts`                | UTC, ISO 8601, ending in `Z`                                                                                                                                         |
| `event`             | One of the events above                                                                                                                                              |
| `id`                | On events that open a state, any unique string; repeated by `permission_waiting` and `cleared`, or `"*"`                                                             |
| `host`              | The machine's short host name                                                                                                                                        |
| `harness`           | `claude-code`                                                                                                                                                        |
| `session_id`        | Claude Code's session id                                                                                                                                             |
| `session_name`      | The `--name` or `/rename` title, from the transcript or captured at session start                                                                                    |
| `agent_id`          | The subagent's id, for a subagent's event                                                                                                                            |
| `tmux`              | `socket` (the socket file's name, which `tmux -L` takes for a server in the default socket directory), `session`, `window`, `window_id` and `pane`; absent elsewhere |
| `cwd`               | The session's working directory                                                                                                                                      |
| `permission_mode`   | The session's permission mode                                                                                                                                        |
| `tool`              | The tool asked about, on `permission_request`, `permission_waiting` and `auto_denied`                                                                                |
| `mcp_server`        | The MCP server's name, for an MCP tool                                                                                                                               |
| `subject`           | What the request is about; see below                                                                                                                                 |
| `notification_type` | The notification's type, on `permission_waiting` and `elicitation`                                                                                                   |
| `error`             | The `StopFailure` error type on stops, such as `rate_limit`, `overloaded`, `server_error` or `invalid_request`                                                       |
| `error_text`        | The rendered error line on `api_error_stop`, cut to 300 characters; never for `invalid_request`, the error a safeguard refusal arrives as, nor on `refusal_stop`     |

`subject` is the path for file tools and the host for `WebFetch`, never the URL's path or query, cut to 200 characters. It is absent for Bash, MCP and every other tool, so no event records a command.

A line that would reach 4 KB drops `subject`, then `error_text`, `cwd`, `session_name`, `tmux` and `mcp_server`, until it fits.

Never recorded: commands, tool output, file contents, environment variables, other tool input, the auto-mode classifier's reason, Claude's messages, or a refusal's explanation.

### Example

```json
{"v":1,"ts":"2026-10-23T14:02:11Z","event":"permission_request","id":"1792771331-48211-1904427","host":"workstation","harness":"claude-code","session_id":"0b6c1f6e-7d1e-4a9e-9f0c-2f5b8f0a7c3d","session_name":"docs-refresh","tmux":{"socket":"default","session":"docs","window":"refresh","window_id":"@12","pane":"%41"},"cwd":"/home/user/src/docs","permission_mode":"default","tool":"Edit","subject":"/home/user/src/docs/README.md"}
```

## Commands

The script reads the file for watchers:

```text
attention-log wait [--from <position>] [--events <list>]
attention-log pending [--older-than <seconds>]
```

- `wait` blocks until a line is appended after `<position>` (by default, the current end of the file) whose event is in the comma-separated `<list>` (by default, any). It prints that line, then the position after it on a line of its own, and exits, so a background command that exits on the next event needs no polling of its own. A position is `<inode>:<offset>`, the file's inode number and a byte offset in it; pass the printed one to the next `wait`. When the file has been rotated once since, `wait` reads the rest of `events.jsonl.1` first, however far the new file has grown; after two rotations the position's file is gone, and `wait` starts the current file from its start. A bare `<offset>` refers to the file that is current when `wait` starts.
- `pending` lists the states still open in both files, oldest first, as `<tmux session>: <window>` lines (the session's name or id outside tmux), followed by the event, its tool or error, and its age in seconds. `--older-than` lists only states at least that old. Both commands exit 1 when the state directory exists but cannot be read, rather than report an empty log.

```text
$ attention-log pending --older-than 300
docs: refresh (permission_request Bash, 1260s)
api: tests (api_error_stop rate_limit, 845s)
```

The script lives in the installed plugin's `scripts/` directory.

## Files

Besides the event files, `~/.local/state/attention-log/sessions/` holds a small file per session with open states, a lock while one changes, and the title captured at session start. `SessionEnd` removes a session's files; a session that never ends cleanly leaves them behind. The hooks create the state directory and its files readable by their owner only, since the log holds paths and session names.

## Known limits

- **Reading in the instant of a rotation.** A writer that opened `events.jsonl` just before another renamed it appends its line to `events.jsonl.1`, and a `wait` that has already finished `events.jsonl.1` and moved to the new file misses that line; `pending` still sees it. A reader that lands exactly on the rename can also misread it once: a `wait` may return an event it already returned, and a `pending` may list nothing. Rotations come once per 5 MiB of events.
- **A request can stay open until its turn ends.** Hooks run as separate async processes, so a tool result can be recorded before its request's hook has marked the request open, and the request is then not cleared by id. The session's next prompt, turn end or session end clears it with `"*"`. The realistic case is a subagent's request that is denied at once, which carries an `agent_id`.
- **Parallel calls of one tool.** A request is cleared by the next result for the same tool and agent, which can belong to another call of that tool. A dialog cleared that way is opened again, as `permission_waiting`, when its prompt notification arrives about six seconds later.
- **A lock left by a stopped hook.** A hook that stopped while holding its session's lock leaves it to the next hook, which takes it over. Two hooks that take it over at the same instant can both change the session's open states, losing or misordering one change; the session's next prompt clears what that leaves.
- **MCP dialogs open no state.** `elicitation` events carry no `id`, so `pending` does not list an open MCP dialog.
- **Sessions that end without `SessionEnd`.** A session that stops without its `SessionEnd` hook leaves its open states in `pending` until the events that opened them rotate out, and leaves its files in `sessions/`.
- **States older than two rotations.** `pending` replays only `events.jsonl` and `events.jsonl.1`, so a state whose opening event has rotated out of both, such as a session left stopped on an API error, drops out of the listing without being cleared.

## See Also

- [Notify](../notify/README.md): macOS banners for permission prompts, questions and completions
- [All plugins](../../../../README.md)
