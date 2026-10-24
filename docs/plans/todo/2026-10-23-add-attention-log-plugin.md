# Add the attention-log plugin

## Context

Many Claude Code sessions run at once across tmux servers, mostly in auto mode, and a permission dialog can sit unseen in a pane nobody is watching. A session can also stop for good when an API error or a safeguard refusal ends its turn, and nothing records that either. Issue #641 asks for a plugin that writes one append-only JSON Lines file recording each of these moments, for watchers such as a pane monitor or a coordinating session to read. The file's format is a versioned contract agreed with such a monitor, which reads it directly.

Facts checked against Claude Code 2.1.309's hook table and hook code:

- `PermissionRequest` carries `tool_name`, `tool_input`, `permission_suggestions` and, for MCP tools, an `mcp_server` object; it has no `tool_use_id`, so the plugin generates ids.
- `PermissionDenied` fires in auto mode only, with `tool_use_id` and `reason`.
- `StopFailure` fires instead of `Stop` when the turn's last assistant message is an API error, with `error`, `error_details` and `last_assistant_message`. The query loop returns through `StopFailure` before it would run the `Stop` hooks.
- A safeguard refusal that survives the one same-model retry yields a `model_refusal_no_fallback` system record and then a synthetic assistant error record (`isApiErrorMessage`, `stop_reason: refusal`, `error: invalid_request`). That record ends the turn through the same API-error branch, so `StopFailure` fires for it with `error: invalid_request`, and `Stop` does not.
- Every command hook accepts `async: true`. The common input has `session_id`, `transcript_path`, `cwd`, `permission_mode` and, inside a subagent, `agent_id`. `session_title` arrives only on `SessionStart` and `UserPromptSubmit`.

Decisions taken: its own plugin, not part of notify; no notifications from this plugin; Claude Code only at first. A Bash request's `subject` was first to be its command, cut to 200 characters with secret-shaped values masked. After review kept finding quoting forms that masking missed, the maintainer dropped command specifics entirely: no event records a command, and `auto_denied` records no classifier reason, which can quote one. `subject` stays for file tools (the path) and `WebFetch` (the host).

**Classification:** feature (`feat`). One PR on this branch.

## Changes

### 1. `plugins/attention-log/` (new, 1.0.0)

- `scripts/attention-log`, one Bash script that parses under macOS `/bin/bash` 3.2:
  - `hook <Event>`: the hook entry point. It discards its own stdout, exits 0 whatever happens, and writes only to the state directory.
  - `wait [--from <position>] [--events <list>]`: blocks until a matching line is appended after the position, prints the line and then the position after it, `<inode>:<offset>`, and exits.
  - `pending [--older-than <seconds>]`: lists the open states as `session: window` lines.
- `hooks/hooks.json`: every hook async, for `PermissionRequest`, `PermissionDenied`, `Notification` (`permission_prompt`, `elicitation_dialog`, `elicitation_url_dialog`), `PostToolUse`, `PostToolUseFailure`, `StopFailure`, `Stop`, `UserPromptSubmit`, `SessionStart` and `SessionEnd`.
- `hooks/codex.hooks.json`, registering no hooks, and `.codex-plugin/plugin.json`, since validation requires a Codex manifest for every hook plugin.
- State lives in `~/.local/state/attention-log/`, or in `ATTENTION_LOG_DIR` when set: `events.jsonl`, `events.jsonl.1` and a `sessions/` directory holding each session's marker of open states and its captured title.

### 2. Events and fields

As agreed in the contract: `permission_request`, `permission_waiting`, `api_error_stop`, `refusal_stop`, `cleared`, `elicitation` and `auto_denied`, with `v`, `ts`, `event`, `id`, `host`, `harness`, `session_id`, `session_name`, `agent_id`, `tmux` (`socket`, `session`, `window`, `window_id`, `pane`), `cwd`, `permission_mode`, `tool`, `mcp_server`, `subject`, `notification_type`, `error` and `error_text`. Empty fields are left out. A `permission_prompt` notification with no request open, such as a sandbox network prompt, opens its own `permission_waiting` state.

- `StopFailure` with `invalid_request` reads the transcript's last records, metadata only, and logs `refusal_stop` when they show the refusal records after the turn's last prompt or ordinary reply. It retries briefly, since the transcript can lag the hook. Since `Stop` never fires for an API-error stop, `Stop` does not check for refusals.
- `refusal_stop` records no `error_text`, so a refusal's explanation never reaches the file.
- Lines are written whole, in one append of under 4 KB; oversized lines drop free-text fields until they fit. At 5 MiB the file is renamed to `events.jsonl.1`, under a lock, so concurrent writers never rename twice.

### 3. Tests

`tests/scrut/attention-log.md`: parsing under `/bin/bash`, the hook manifest (every hook async and dispatched), no stdout and exit 0 from every hook, field contents, the absence of any command, id pairing and the `"*"` clear, refusal labeling, whole lines under concurrent appends, rotation by rename, `wait` and `pending`. Each guarded behavior gets a planted defect.

### 4. Catalog and documentation

`.claude-plugin/marketplace.json`, the root README's hooks table, the plugin README, `Makefile` `SCRUT_ENV` and CI `scrut-env`, then `make build`.

## Verification

`make build`, `make test-all` and the `check-versions` skill.
