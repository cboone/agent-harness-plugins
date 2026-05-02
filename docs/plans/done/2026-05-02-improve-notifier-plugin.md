# Improve macOS notifier plugin with modern tools

## Context

The `notify` plugin currently shells out to [`terminal-notifier`](https://github.com/julienXX/terminal-notifier), which has been frozen at version 2.0.0 since November 2017. Two of its options that we want to use are broken or mutually exclusive (`-appIcon` is silently ignored on Big Sur and later; `-sender` and `-activate` cannot be combined). The README of the upstream project itself directs users to alternatives. The current plugin therefore ships unstyled, undifferentiated banners with limited click behavior.

The repository now ships three harnesses for the notify plugin:

- **Claude Code** (events: `Notification:idle_prompt`, `Notification:elicitation_dialog`, `Notification:permission_prompt`, `PreCompact:auto`, `Stop`).
- **OpenCode** (events: `session.idle`, `permission.updated`, `experimental.session.compacting`).
- **Codex CLI** (events available: `Stop`, plus `PermissionRequest` which the existing draft did not wire). Codex's hook event enum is strict and does not expose `Notification` or `PreCompact`.

The Codex variant lives on a sibling worktree (`feature/create-codex-versions`, base point `da14215`, branched before the OpenCode hooks PR landed). When that worktree merges main it will gain the OpenCode files; when this worktree merges main or the codex worktree it will gain the Codex manifest. The plan accounts for that coordination explicitly in the versioning and merge sections below.

This plan replaces `terminal-notifier` with [`alerter`](https://github.com/vjeantet/alerter) (Swift rewrite at v26.x, monthly releases through 2026, signed and notarized), adds richer per-event content, per-harness icons, click-to-focus into the originating terminal app and tmux pane, action buttons that actually decide on Codex's `PermissionRequest`, and per-event sound/group differentiation. There is no graceful fallback to `terminal-notifier` or `osascript`: the plugin hard-depends on `alerter` and is intended primarily for the maintainer's personal use.

## Goals

1. Drop `terminal-notifier`. Hard-depend on `alerter` (>= 26.5).
2. Surface useful, harness-aware content in every notification: pane title (when present) or branch suffix as subtitle context, last assistant message tail in the body for `Stop`, the literal elicitation question in the body for `elicitation_dialog`, per-tool previews in the body for permission events.
3. Per-harness icons (Claude Code, OpenCode, Codex). Per-event sounds and groups so notifications replace their predecessors instead of stacking.
4. Click on any notification activates the originating terminal app and switches the tmux client to the originating session/window/pane when applicable.
5. On Codex's `PermissionRequest` event, present `Approve` and `Deny` action buttons whose result is fed back to Codex via the hook's JSON response (`{"decision":"allow"|"deny"}`). On Claude Code and OpenCode the buttons are omitted because their permission events cannot be answered from a hook.
6. Achieve and maintain three-harness parity for the events each harness exposes.

## Approach

### Single shared bash script, harness-specific entrypoints

`plugins/notify/scripts/notify` (rewritten) is the single bash entrypoint for Claude Code and Codex. It reads JSON from stdin, extracts the relevant fields, computes shared subtitle context (project, pane title or branch suffix), looks up the harness icon and per-event sound/group, and shells out to `alerter`. A subcommand selects the event:

```text
notify cc-idle           # Claude Code Notification:idle_prompt
notify cc-elicit         # Claude Code Notification:elicitation_dialog
notify cc-permission     # Claude Code Notification:permission_prompt
notify cc-compact        # Claude Code PreCompact:auto
notify cc-stop           # Claude Code Stop
notify codex-permission  # Codex PermissionRequest (action-button decision)
notify codex-stop        # Codex Stop
```

OpenCode goes through its own TypeScript file (`opencode/index.ts`), rewritten to call `alerter` directly via Bun's `$`. The TS plugin reuses the same icon assets and the same per-event sound/group conventions as the bash script.

### Click handling

`alerter` blocks until the user interacts, prints the activation result on stdout (`@CONTENTCLICKED`, `@TIMEOUT`, `@CLOSED`, an action label on button click, etc.), then exits. Because hooks are subprocesses of the harness, the script must not block the harness on user interaction. Pattern:

```bash
nohup bash -c "$(cat <<'WRAPPER'
  result="$(alerter ... --json 2>/dev/null)"
  case "${result}" in
    *@CONTENTCLICKED*) exec "${0%/*}/focus-pane" "${term_program}" "${tmux_session}" "${tmux_window}" "${tmux_pane}" ;;
    *Approve*) printf 'allow\n' > "${decision_path}" ;;
    *Deny*)    printf 'deny\n'  > "${decision_path}" ;;
  esac
WRAPPER
)" >/dev/null 2>&1 &
disown
```

For Codex's `PermissionRequest` the wrapper is **not** detached: the hook must block until `alerter` returns, then emit the JSON decision on stdout for Codex to read. Detachment applies only to fire-and-forget events.

A separate script `plugins/notify/scripts/focus-pane` does the click-to-focus work. Two steps:

**Step 1: activate the host terminal app.** Run `osascript -e 'tell application id "<bundle-id>" to activate'`. The bundle ID is derived from `$TERM_PROGRAM`:

| `$TERM_PROGRAM`  | Bundle ID                |
| ---------------- | ------------------------ |
| `Apple_Terminal` | `com.apple.Terminal`     |
| `iTerm.app`      | `com.googlecode.iterm2`  |
| `ghostty`        | `com.mitchellh.ghostty`  |
| `WezTerm`        | `com.github.wez.wezterm` |
| `vscode`         | `com.microsoft.VSCode`   |
| `alacritty`      | `org.alacritty`          |
| (anything else)  | `com.apple.Terminal`     |

**Step 2: switch tmux pane.** If the hook captured tmux state (i.e. the user was inside tmux when the hook fired), run `tmux switch-client -t "${session}" \; select-window -t "${session}:${window}" \; select-pane -t "${session}:${window}.${pane}"`. `tmux switch-client` is only meaningful if a client is attached; if not, the user already saw the pane next time they open tmux. Do not error on failure. When not running inside tmux, this step is a no-op.

### Subtitle context

A small helper, in both bash and TS, computes the subtitle string used by every event:

```text
if $TMUX_PANE is set:
    title = tmux display-message -t "$TMUX_PANE" -p '#T'
    if title is non-empty AND title != cwd-basename AND title not in {zsh, bash, fish, sh, tmux, ssh, nvim, vim, ${default_command_set}}:
        subtitle = "${project} · ${title}"
        return
subtitle = "${project} · ${branch_suffix}"
```

`branch_suffix` strips everything before and including the first `/` in the current branch name (`feature/improve-notifier` becomes `improve-notifier`; `main` stays `main`). Implemented in bash as `${branch#*/}` after a guard for branches without a `/`.

`project` is `basename "${PWD}"` (matches existing behavior).

The "pane title not in default-set" check exists because tmux defaults the pane title to the running command name when the shell hasn't set one explicitly; we want to fall back to the branch suffix in that case.

### Last assistant message extraction

Symmetric to the existing `extract_last_user_message` function. Walks the transcript JSONL backward, finds the first record with `type` of `assistant` (Claude Code transcript convention), extracts the concatenated text content of that message, truncates to the requested limit. Used for both `Stop` and `idle_prompt`.

For Codex, the transcript format may differ. Verified at implementation time against the codex CLI's transcript output. If the format is identical (Codex was designed for Claude Code source compatibility), the same extractor works.

For OpenCode, the SDK's `client.session.messages` already returns structured messages and the existing helper iterates them; an analogous `lastAssistantMessage` helper is added.

### Per-tool permission previews

The body of permission notifications uses the tool name plus a per-tool preview of the most-relevant argument:

| Tool                    | Preview         |
| ----------------------- | --------------- |
| `Bash`                  | `command`       |
| `Edit`, `Write`, `Read` | `file_path`     |
| `WebFetch`              | `url`           |
| `Grep`, `Glob`          | `pattern`       |
| `Task`                  | `description`   |
| `NotebookEdit`          | `notebook_path` |
| (anything else)         | tool name only  |

Source of the tool name and input depends on the harness:

- Claude Code `Notification:permission_prompt`: payload includes the message text, but the structured tool name and input must be read from the most recent `tool_use` entry in the transcript JSONL (last record with `type` of `assistant` containing a `tool_use` content block).
- Codex `PermissionRequest`: payload includes `tool_name` and `tool_input` directly.
- OpenCode `permission.updated`: payload's `properties` includes the tool reference; resolve via the SDK if needed.

### Per-harness icons

PNG icons live in `plugins/notify/assets/`, sourced from each agent's `.app` bundle on the maintainer's machine and committed to the repo:

- `claude-code.png` from `/Applications/Claude.app/Contents/Resources/electron.icns`
- `opencode.png` from `/Applications/OpenCode.app/Contents/Resources/icon.icns`
- `codex.png` from `/Applications/Codex.app/Contents/Resources/electron.icns`

Each is converted with `sips -s format png --resampleHeightWidth 512 512 <path> --out <dest>`. `alerter` reads the file via `--app-icon "${CLAUDE_PLUGIN_ROOT}/assets/${harness}.png"`. The flag uses a private API but `alerter` keeps it functional release-to-release; this is an accepted tradeoff for the personal-use scope.

If any of the three icons cannot be extracted at acceptable quality (e.g. the Codex CLI ships only a small icon, or the OpenCode icon is monochrome at small sizes), this plan flags the gap and the maintainer supplies a replacement PNG. The plan does not block on icon perfection.

### Per-event sounds and groups

| Event              | Sound   | Group                |
| ------------------ | ------- | -------------------- |
| `cc-idle`          | `Tink`  | `claude-idle`        |
| `cc-elicit`        | `Tink`  | `claude-elicit`      |
| `cc-permission`    | `Funk`  | `claude-permission`  |
| `cc-compact`       | `Pop`   | `claude-compact`     |
| `cc-stop`          | `Glass` | `claude-stop`        |
| `oc-permission`    | `Funk`  | `opencode-permission`|
| `oc-compact`       | `Pop`   | `opencode-compact`   |
| `oc-stop`          | `Glass` | `opencode-stop`      |
| `codex-permission` | `Funk`  | `codex-permission`   |
| `codex-stop`       | `Glass` | `codex-stop`         |

`alerter --group <id>` causes a new notification with the same group ID to dismiss the previous one. Groups are namespaced per harness so a Claude Code stop notification doesn't dismiss an OpenCode stop notification when both are in flight.

### Timeout and detachment

Every fire-and-forget invocation passes `--timeout 86400` (24 hours) so orphaned `alerter` processes can't accumulate indefinitely. The wrapper subshell is `nohup`-ed and disowned so the hook returns to the harness immediately. Codex `PermissionRequest` is the exception: it blocks (timeout 600 seconds, defaults to deny on timeout).

## Notification content matrix

The complete per-event content. Every event uses the subtitle helper for its base subtitle (computed identically across harnesses); permission events suffix it with the tool name. Stop events fall back to the last user message alone if the last assistant tail is empty.

### Claude Code

`cc-idle` (`Notification:idle_prompt`):

- Title: `Claude Code · Idle`
- Subtitle: subtitle helper
- Body: last assistant message tail (≤120 chars); fallback `Waiting for input`
- Buttons: none

`cc-elicit` (`Notification:elicitation_dialog`):

- Title: `Claude Code · Question`
- Subtitle: subtitle helper
- Body: payload `message` field (≤140); fallback `Needs input`
- Buttons: none

`cc-permission` (`Notification:permission_prompt`):

- Title: `Claude Code · Permission`
- Subtitle: subtitle helper, suffixed `· <tool>`
- Body: per-tool preview (≤140), e.g. `pnpm test --run` or `src/main.go`
- Buttons: none (Claude Code permission events cannot be answered from a hook)

`cc-compact` (`PreCompact:auto`):

- Title: `Claude Code · Compacting`
- Subtitle: subtitle helper
- Body: `Auto-compacting context`
- Buttons: none

`cc-stop` (`Stop`):

- Title: `Claude Code · Done`
- Subtitle: subtitle helper
- Body: `<last user message ≤55> → <last assistant message tail ≤60>`; fallback last user message alone
- Buttons: none

### OpenCode

`oc-permission` (`permission.updated`):

- Title: `OpenCode · Permission`
- Subtitle: subtitle helper, suffixed `· <tool>`
- Body: per-tool preview (≤140)
- Buttons: none

`oc-compact` (`experimental.session.compacting`):

- Title: `OpenCode · Compacting`
- Subtitle: subtitle helper
- Body: `Auto-compacting context`
- Buttons: none

`oc-stop` (`session.idle`):

- Title: `OpenCode · Done`
- Subtitle: subtitle helper
- Body: `<last user message ≤55> → <last assistant message tail ≤60>`; fallback last user message alone
- Buttons: none

OpenCode has no separate idle event distinct from `session.idle`; the latter is the Stop equivalent and serves both roles.

### Codex

`codex-permission` (`PermissionRequest`):

- Title: `Codex · Permission`
- Subtitle: subtitle helper, suffixed `· <tool>`
- Body: per-tool preview (≤140)
- Buttons: `Approve`, `Deny`. Result fed back via the hook's JSON response (`{"decision":"allow"|"deny"}`). Hook blocks until interaction; defaults to `deny` on the 600-second timeout.

`codex-stop` (`Stop`):

- Title: `Codex · Done`
- Subtitle: subtitle helper
- Body: `<last user message ≤55> → <last assistant message tail ≤60>`; fallback last user message alone
- Buttons: none

## Repository layout changes

```text
plugins/notify/
├── .claude-plugin/
│   └── plugin.json              modified: version 2.0.0
├── .codex-plugin/
│   └── plugin.json              NEW (also coming from the codex worktree; this branch creates its own copy at 2.0.0)
├── assets/
│   ├── claude-code.png          NEW (extracted from /Applications/Claude.app)
│   ├── codex.png                NEW (extracted from /Applications/Codex.app)
│   └── opencode.png             NEW (extracted from /Applications/OpenCode.app)
├── hooks/
│   ├── hooks.json               modified: subcommand names change
│   └── codex.hooks.json         NEW: Stop and PermissionRequest entries
├── opencode/
│   └── index.ts                 rewrite: alerter, click-to-focus, per-event content
├── scripts/
│   ├── notify                   rewrite: subcommand-per-event, alerter, helpers
│   └── focus-pane               NEW: click handler script
└── README.md                    rewrite: alerter install, three-harness setup, click-to-focus, action buttons
```

## Files to create

### `plugins/notify/.codex-plugin/plugin.json`

Codex-specific manifest, mirrors the Claude manifest with codex-specific description and hook path. Version 2.0.0.

```json
{
  "author": { "name": "Christopher Boone" },
  "description": "Notifies you when Codex finishes a task or needs your attention.",
  "homepage": "https://github.com/cboone/cboone-cc-plugins",
  "hooks": "./hooks/codex.hooks.json",
  "keywords": ["alerts", "macos", "notifications"],
  "license": "MIT",
  "name": "notify",
  "repository": "https://github.com/cboone/cboone-cc-plugins",
  "version": "2.0.0"
}
```

### `plugins/notify/hooks/codex.hooks.json`

Wires `Stop` and `PermissionRequest`. The `PermissionRequest` entry is new compared to the codex worktree's draft, which had only `Stop`.

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "hooks": [
          {
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify codex-permission",
            "type": "command"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify codex-stop",
            "type": "command"
          }
        ]
      }
    ]
  }
}
```

### `plugins/notify/assets/{claude-code,opencode,codex}.png`

512x512 PNGs extracted from each agent's `.app` bundle:

```bash
sips -s format png --resampleHeightWidth 512 512 \
  /Applications/Claude.app/Contents/Resources/electron.icns \
  --out plugins/notify/assets/claude-code.png

sips -s format png --resampleHeightWidth 512 512 \
  /Applications/OpenCode.app/Contents/Resources/icon.icns \
  --out plugins/notify/assets/opencode.png

sips -s format png --resampleHeightWidth 512 512 \
  /Applications/Codex.app/Contents/Resources/electron.icns \
  --out plugins/notify/assets/codex.png
```

The `electron.icns` files all measure 1024x1024 source size, which downsamples cleanly. If the resulting PNG looks wrong (e.g. transparency artifacts, monochrome at small sizes), the plan flags the gap and the maintainer provides a replacement.

### `plugins/notify/scripts/focus-pane`

```bash
#!/usr/bin/env bash
# Activates a terminal app and (optionally) switches a tmux client to a pane.
# Usage: focus-pane <term-program> [<tmux-session> <tmux-window> <tmux-pane>]
```

Implementation outline:

1. Map `$1` (`$TERM_PROGRAM` value) to a bundle ID via the table above; default to `com.apple.Terminal`.
2. `osascript -e "tell application id \"${bundle_id}\" to activate"`. Ignore failure.
3. If `$2`, `$3`, `$4` are all set: `tmux switch-client -t "$2" \; select-window -t "$2:$3" \; select-pane -t "$2:$3.$4"`. Ignore failure (no client attached, target gone, etc.).

## Files to modify

### `plugins/notify/scripts/notify`

Rewritten as a subcommand dispatcher. New shape:

- `usage()`, `truncate_with_ellipsis()`: kept.
- `extract_last_user_message()`, `extract_last_assistant_message()`: walk transcript JSONL backward.
- `compute_subtitle()`: implements the subtitle helper described in Approach.
- `compute_branch_suffix()`: `${branch#*/}` with guard.
- `compute_pane_title()`: `tmux display-message -t "$TMUX_PANE" -p '#T'` with default-set guard.
- `compute_tmux_state()`: returns `session|window|pane` triple via `tmux display-message -t "$TMUX_PANE" -p '#S|#I|#P'` if `$TMUX_PANE` set, else empty.
- `tool_preview_from_transcript()` (CC), `tool_preview_from_payload()` (Codex): per-tool preview extractor.
- `notify_alerter()`: shared invocation that reads icon path, sound, group, subtitle, body, optional actions, and runs `alerter` (detached or blocking depending on event).
- `do_cc_idle()`, `do_cc_elicit()`, `do_cc_permission()`, `do_cc_compact()`, `do_cc_stop()`, `do_codex_permission()`, `do_codex_stop()`: one function per event, each reads stdin JSON, computes content per the matrix, calls `notify_alerter`.
- `main()`: dispatches the subcommand.

The Codex permission handler blocks on `alerter` and writes the resulting decision to stdout as Codex's expected JSON response. All other handlers detach.

The script applies the conventions in the `write-bash-scripts` skill (no global state, no unused vars, `set -euo pipefail`, `local` for everything in functions, etc.).

### `plugins/notify/hooks/hooks.json`

Subcommand names change from the current `(none)` and `stop` to the per-event names:

```json
{
  "hooks": {
    "Notification": [
      { "hooks": [{ "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify cc-idle",       "type": "command" }], "matcher": "idle_prompt" },
      { "hooks": [{ "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify cc-elicit",     "type": "command" }], "matcher": "elicitation_dialog" },
      { "hooks": [{ "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify cc-permission", "type": "command" }], "matcher": "permission_prompt" }
    ],
    "PreCompact": [
      { "hooks": [{ "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify cc-compact", "type": "command" }], "matcher": "auto" }
    ],
    "Stop": [
      { "hooks": [{ "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify cc-stop", "type": "command" }] }
    ]
  }
}
```

### `plugins/notify/opencode/index.ts`

Rewritten to:

- Replace `terminal-notifier` with `alerter`.
- Fix the hard-coded `TITLE = "Claude Code"` bug to derive `OpenCode` from harness identity.
- Compute subtitle via the same rule as the bash script (extract pane title via `$TMUX_PANE`, fall back to `project · branch-suffix`).
- Implement `lastAssistantMessage()` symmetric to the existing `lastUserMessage()`.
- Implement per-tool preview from `permission.updated` payload.
- For `session.idle`: build body as `<last user ≤55> → <last assistant tail ≤60>`.
- For `permission.updated`: tool name in subtitle suffix, preview in body.
- For `experimental.session.compacting`: `Auto-compacting context` body.
- Detach `alerter` invocations (Bun spawn with `nothrow().quiet()`, no `await` on the inner `alerter` for fire-and-forget cases; or wrap in a child process that the plugin doesn't await).
- Click-to-focus: same dispatch via the shared `focus-pane` script (resolve via `${import.meta.dir}/../scripts/focus-pane`).

### `plugins/notify/.claude-plugin/plugin.json`

Bump `version` from `1.0.3` to `2.0.0`. No other changes.

### `plugins/notify/README.md`

Rewrite to:

- Replace `brew install terminal-notifier` with `brew install vjeantet/tap/alerter`.
- Document the three-harness layout and where each one's installation lives in the README.
- Document the click-to-focus behavior, the action-button decision flow on Codex `PermissionRequest`, and the per-harness icons.
- Update the event/notification matrix to reflect the new content (drop the existing "What It Does" / "When It Fires" tables, replace with the matrix from this plan).
- Note Codex-specific limitations: only `Stop` and `PermissionRequest` events fire (no `Notification` or `PreCompact`); recommend Codex's native `tui.notifications = true` in `~/.codex/config.toml` for idle/elicitation/compact-style banners.
- Document the `alerter` permission grant: first run prompts the user to allow notifications for whichever sender alerter impersonates (defaults to Terminal identity in alerter v26.4+).

### `.claude-plugin/marketplace.json`

Bump the `notify` entry's `version` from `1.0.3` to `2.0.0`. No `metadata.version` bump (no plugin added or removed).

### Top-level `README.md`

No structural change. The notify plugin row stays as-is. If this branch lands before the codex worktree, the codex worktree's later README sections are unaffected. If the codex worktree lands first, this branch picks up its README sections via merge and may need a minor reword to mention the new alerter dep in the codex section.

## Files explicitly NOT changed

- **`bin/build-opencode-mirror`, `dist/opencode/`**: unchanged. The mirror picks up `plugins/notify/opencode/index.ts` and the `assets/` directory automatically via the existing copy/symlink logic.
- **`bin/validate-plugins`**: unchanged by this plan. The dual-manifest consistency check is added by the codex worktree (separate plan); this branch picks it up via merge.
- **`block-rm-rf`, `update-docs-reminder`**: unchanged.
- **`scripts/notify`'s shellcheck and shfmt configuration**: unchanged. The new script must pass the existing checks.

## Versioning and merge coordination

This branch bumps `notify` from 1.0.3 directly to **2.0.0**. The codex worktree currently bumps to 1.1.0. Two cases:

- **This branch merges first**: codex worktree rebases onto main, sees 2.0.0 in both manifests, drops its own version bump in favor of leaving 2.0.0 in place. The codex worktree's `.codex-plugin/plugin.json` and `hooks/codex.hooks.json` are now superseded by this branch's versions (which already include `PermissionRequest` and the 2.0.0 version), so the codex rebase is a no-op for those files (or a small reword for description if there's drift).
- **Codex worktree merges first**: this branch rebases onto main, picks up `.codex-plugin/plugin.json` at 1.1.0 and `hooks/codex.hooks.json` with only `Stop`, then this plan's modifications bump to 2.0.0 and add `PermissionRequest`.

In either case the dual-manifest consistency rule (added by the codex worktree to `bin/validate-plugins`) requires `version` to match across `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`. This plan honors that by setting both to 2.0.0.

`metadata.version` in `.claude-plugin/marketplace.json` is **not** bumped: the catalog gains and loses no plugins.

## Verification

In order:

1. **Static checks**.
   - `bin/validate-json` / project lint passes for the new `hooks/codex.hooks.json`, modified `hooks.json`, modified `plugin.json` files, modified `marketplace.json`.
   - `shellcheck plugins/notify/scripts/notify plugins/notify/scripts/focus-pane` clean.
   - `shfmt -d plugins/notify/scripts/notify plugins/notify/scripts/focus-pane` clean.
   - `tsc` / OpenCode mirror builder passes for `opencode/index.ts`.
   - `bin/validate-plugins` clean (dual-manifest consistency rule, when present, sees matching 2.0.0).
2. **Icon extraction sanity**. `file plugins/notify/assets/*.png` reports 512x512 RGBA PNGs. Open each in Preview and eyeball legibility at 64x64 (notification display size). Replace any that look bad.
3. **Local Claude Code smoke test**, in this repo's worktree:
   - Trigger `Stop` by ending a turn. Confirm notification shows `Claude Code · Done`, subtitle matches the pane-title rule, body shows `<last user> → <last assistant tail>`, click activates the host terminal and switches the tmux pane.
   - Trigger `Notification:permission_prompt` by attempting a tool that requires permission. Confirm tool name in subtitle suffix, preview in body, no buttons.
   - Trigger `Notification:elicitation_dialog` by using a tool that elicits input. Confirm body contains the actual question.
   - Wait for `Notification:idle_prompt` after a turn ends; confirm body shows last assistant tail.
   - Trigger `PreCompact:auto` (or simulate via a long context); confirm `Auto-compacting context` body.
4. **Local OpenCode smoke test**, with `OPENCODE_CONFIG_DIR=dist/opencode`:
   - Same trigger set as Claude Code, mapped to `session.idle`, `permission.updated`, `experimental.session.compacting`.
   - Confirm title is `OpenCode · …`, not `Claude Code · …` (the bug fix).
5. **Local Codex smoke test**, after `codex plugin marketplace add /path/to/this/repo` and `codex plugin install notify@cboone-cc-plugins`:
   - Trigger `Stop` by ending a turn. Confirm `Codex · Done` notification, click-to-focus works.
   - Trigger `PermissionRequest` by attempting a tool that requires permission. Confirm `Approve` / `Deny` buttons. Click `Approve`; confirm Codex proceeds. Repeat with `Deny`; confirm Codex denies.
   - Confirm Codex does not log a deserialize error for `Notification`/`PreCompact` (since `codex.hooks.json` doesn't reference them).
6. **Group replacement check**. Fire two `Stop` notifications in a row in the same harness; confirm only the second is visible (group dismissed the first).
7. **Detachment check**. After firing a notification, confirm the harness has returned (e.g. Claude Code's prompt is interactive); confirm `pgrep -f alerter` shows the detached process; close the notification or wait the timeout; confirm it cleans up.
8. **Click-to-focus across terminals**. Test from at least Apple Terminal and Ghostty (the maintainer's primary terminal). Skip iTerm2/WezTerm/etc. unless the maintainer uses them.

## Out of scope

- **Reply field**. Decided out: the user prefers switching to the pane and typing.
- **`ntfy.sh` cross-device push**. Out for this iteration; could be added as opt-in via env var later.
- **OSC 9 / OSC 99 / OSC 777 escape-sequence fallback**. Out; relies on `alerter` exclusively.
- **`NOTIFY_TERMINAL_APP` override env var**. Out; `$TERM_PROGRAM` auto-detect is sufficient.
- **Customizable per-event title/body/sound via env vars or config file**. Out; values are hardcoded for personal use.
- **Per-turn duration, tool count, token meter, `git diff --stat` summary in `Stop` body**. Out for this iteration; recommendation matrix decided that the `<last user> → <last assistant tail>` form is the right body.
- **GitHub Actions test job that exercises `alerter`**. Out; alerter is a GUI tool that needs Notification Center, which CI runners do not have.
- **Migration helper for users who had `terminal-notifier` configured**. Out; the README documents the new install command and the breaking change is signaled by the major version bump.
