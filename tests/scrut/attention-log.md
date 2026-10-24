# Attention log

Tests for the `attention-log` plugin's bundled script. Its hooks append JSON Lines events to `ATTENTION_LOG_DIR/events.jsonl`; `wait` and `pending` read them.

`al` runs the script under `/bin/bash`, which is bash 3.2 on macOS, the shell `env bash` finds there without Homebrew. Every case points `ATTENTION_LOG_DIR` at a fresh work directory, so no test touches the real `~/.local/state/attention-log/`. `payload` builds a hook payload from a base session and the JSON object given. `in_tmux` runs a command as if inside pane `%7` of a tmux server named `projects`, through a `tmux` stub. `fresh` starts a new state directory.

```scrut {fail_fast: true}
$ set -o pipefail
> work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
> mkdir -p "${work}/bin"
> printf '#!/usr/bin/env bash\nprintf "main\\037editor\\037@3\\n"\n' > "${work}/bin/tmux"
> chmod +x "${work}/bin/tmux"
> state_count=0
> function fresh() {
>   state_count=$((state_count + 1))
>   export ATTENTION_LOG_DIR="${work}/state-${state_count}"
>   events_file="${ATTENTION_LOG_DIR}/events.jsonl"
> }
> function al() {
>   env -u TMUX -u TMUX_PANE /bin/bash "${ATTENTION_LOG_BIN}" "$@"
> }
> function in_tmux() {
>   env TMUX="/tmp/tmux-1000/projects,4242,0" TMUX_PANE="%7" PATH="${work}/bin:${PATH}" \
>     /bin/bash "${ATTENTION_LOG_BIN}" "$@"
> }
> function payload() {
>   local extra="${1:-}"
>   [[ -n "${extra}" ]] || extra="{}"
>   jq -nc --argjson extra "${extra}" --arg session "${2:-s1}" \
>     '{session_id: $session, transcript_path: "/nonexistent", cwd: "/work", permission_mode: "default"} + $extra'
> }
> function hook() {
>   payload "${2:-}" "${3:-s1}" | al hook "${1}"
> }
> function events() {
>   jq -c "${1:-.}" "${events_file}"
> }
> fresh
```

## Parses under the system bash

A parse failure exits 2, which Claude Code treats as blocking. CI runs on Linux, where `/bin/bash` is bash 5, so this case guards bash 3.2 only in local macOS runs.

```scrut
$ /bin/bash -n "${ATTENTION_LOG_BIN}" && echo "Parses"
Parses
```

## Help

```scrut
$ al --help | head -n 1
Usage: attention-log <command> [options]
```

## No command is a usage error

```scrut
$ al 2>&1 | head -n 1
Usage: attention-log <command> [options]
[2]
```

## Every hook is async and runs its own event

An async hook cannot hold up the session or answer its dialog. The plugin path is quoted, so a path with a space still runs.

```scrut
$ jq -r '.hooks | to_entries[] | .key as $event | .value[].hooks[]
>   | "\($event) \(.type) async=\(.async) \(.command | sub("^\"\\$\\{CLAUDE_PLUGIN_ROOT\\}/scripts/attention-log\" hook "; ""))"' \
>   "${REPO_ROOT}/plugins/attention-log/hooks/hooks.json"
PermissionRequest command async=true PermissionRequest
PermissionDenied command async=true PermissionDenied
Notification command async=true Notification
PostToolUse command async=true PostToolUse
PostToolUseFailure command async=true PostToolUseFailure
StopFailure command async=true StopFailure
Stop command async=true Stop
UserPromptSubmit command async=true UserPromptSubmit
SessionStart command async=true SessionStart
SessionEnd command async=true SessionEnd
```

## Notifications reach the hook only for prompts and MCP dialogs

```scrut
$ jq -r '.hooks.Notification[].matcher' "${REPO_ROOT}/plugins/attention-log/hooks/hooks.json"
permission_prompt|elicitation_dialog|elicitation_url_dialog
```

## No hook prints anything, and every hook exits 0

Hook output could be read as a permission decision. Each hook runs with a payload that records an event, with one that is not JSON, and with a state directory it cannot create.

```scrut
$ fresh
> printf 'not a directory' > "${work}/blocked"
> for event in $(jq -r '.hooks | keys[]' "${REPO_ROOT}/plugins/attention-log/hooks/hooks.json"); do
>   for input in "$(payload '{"tool_name": "Bash", "tool_input": {"command": "ls"}, "notification_type": "permission_prompt", "error": "rate_limit", "session_title": "t"}')" '{"session_id": "s1", "decision": "allow" ' ""; do
>     output="$(printf '%s' "${input}" | al hook "${event}")" && status=0 || status=$?
>     blocked="$(printf '%s' "${input}" | ATTENTION_LOG_DIR="${work}/blocked/state" al hook "${event}")" && blocked_status=0 || blocked_status=$?
>     printf '%s %s %s/%s/%s\n' "${event}" "${status}" "${#output}" "${blocked_status}" "${#blocked}"
>   done
> done | sort | uniq -c | awk '{print $1, $2, $3, $4}'
3 Notification 0 0/0/0
3 PermissionDenied 0 0/0/0
3 PermissionRequest 0 0/0/0
3 PostToolUse 0 0/0/0
3 PostToolUseFailure 0 0/0/0
3 SessionEnd 0 0/0/0
3 SessionStart 0 0/0/0
3 Stop 0 0/0/0
3 StopFailure 0 0/0/0
3 UserPromptSubmit 0 0/0/0
```

## A permission request records who is asking and about what

```scrut
$ fresh
> printf '%s\n' '{"type":"agent-name","agentName":"docs-refresh"}' > "${work}/named.jsonl"
> payload "$(jq -nc --arg t "${work}/named.jsonl" '{transcript_path: $t, tool_name: "Edit", tool_input: {file_path: "/work/README.md"}}')" \
>   | in_tmux hook PermissionRequest
> events '{v, event, harness, session_id, session_name, tmux, cwd, permission_mode, tool, subject}'
{"v":1,"event":"permission_request","harness":"claude-code","session_id":"s1","session_name":"docs-refresh","tmux":{"socket":"projects","session":"main","window":"editor","window_id":"@3","pane":"%7"},"cwd":"/work","permission_mode":"default","tool":"Edit","subject":"/work/README.md"}
```

## Timestamps are UTC ISO 8601 ending in Z, and requests carry an id

```scrut
$ events '[(.ts | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")), (.id | type), (.host | type)]'
[true,"string","string"]
```

## Outside tmux there is no tmux object

```scrut
$ fresh
> hook PermissionRequest '{"tool_name": "Read", "tool_input": {"file_path": "/work/notes.md"}}'
> events '[has("tmux"), .subject]'
[false,"/work/notes.md"]
```

## The session title captured at start names later events

```scrut
$ fresh
> hook SessionStart '{"session_title": "release prep"}'
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "make"}}'
> events .session_name
"release prep"
```

## Session end removes the session's files

```scrut
$ hook SessionEnd && ls "${ATTENTION_LOG_DIR}/sessions" | wc -l | tr -d ' '
0
```

## Subjects name a file tool's path or a web fetch's host

Only the host of a URL, never its path or query. MCP tools name their server instead.

```scrut
$ fresh
> hook PermissionRequest '{"tool_name": "WebFetch", "tool_input": {"url": "https://user@docs.example.test:8443/page?q=1"}}'
> hook PermissionRequest '{"tool_name": "WebFetch", "tool_input": {"url": "https://user:pa@ss@docs.example.test/x"}}'
> hook PermissionRequest '{"tool_name": "NotebookEdit", "tool_input": {"notebook_path": "/work/a.ipynb"}}'
> hook PermissionRequest '{"tool_name": "mcp__search__query", "tool_input": {"q": "private words"}, "mcp_server": {"name": "search", "source": "user"}}'
> events '[.tool, .subject, .mcp_server]'
["WebFetch","docs.example.test",null]
["WebFetch","docs.example.test",null]
["NotebookEdit","/work/a.ipynb",null]
["mcp__search__query",null,"search"]
```

## No event records a command or a classifier's reason

A Bash request records its tool and no subject. An auto-denied call records neither its command nor the classifier's reason, which can quote the command. Neither line holds any of the command's text.

```scrut
$ fresh
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "deploy --target sample-cluster"}}'
> hook PermissionDenied '{"tool_name": "Bash", "tool_input": {"command": "deploy --target sample-cluster"}, "tool_use_id": "t1", "reason": "Would deploy to sample-cluster"}'
> events '[.event, .tool, has("subject"), has("reason")]'
> grep -c 'sample-cluster' "${events_file}"
["permission_request","Bash",false,false]
["auto_denied","Bash",false,false]
0
[1]
```

## Long paths are cut to 200 characters

```scrut
$ fresh
> hook PermissionRequest "$(jq -nc --arg p "/work/$(printf 'y%.0s' {1..300})" '{tool_name: "Write", tool_input: {file_path: $p}}')"
> events '.subject | [length, .[-2:]]'
[200,"y…"]
```

## A tool result clears its own request, by id

A result for a different tool, or from a subagent, leaves the request open.

```scrut
$ fresh
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "make"}}'
> hook Notification '{"notification_type": "permission_prompt", "message": "Claude needs your permission"}'
> hook PostToolUse '{"tool_name": "Read", "tool_input": {}, "tool_response": {}, "tool_use_id": "t1"}'
> hook PostToolUse '{"tool_name": "Bash", "agent_id": "a1", "tool_input": {}, "tool_response": {}, "tool_use_id": "t2"}'
> al pending | sed 's/, [0-9]*s)$/, AGE)/'
> hook PostToolUseFailure '{"tool_name": "Bash", "tool_input": {}, "tool_use_id": "t3", "error": "failed"}'
> events '[.event, .tool]'
> jq -s '[.[0].id == .[1].id, .[0].id == .[2].id, (.[2] | keys)]' -c "${events_file}"
s1 (permission_request Bash, AGE)
["permission_request","Bash"]
["permission_waiting","Bash"]
["cleared",null]
[true,true,["cwd","event","harness","host","id","permission_mode","session_id","ts","v"]]
```

## A prompt notification holds the lock until its event is written

The notification pauses inside its locked section while its request's tool result arrives. The result's clear can only follow the waiting event.

```scrut
$ fresh
> mkdir -p "${work}/slow-bin"
> printf '#!/usr/bin/env bash\n: > "%s/paused"\nuntil [[ -e "%s/release" ]]; do sleep 0.1; done\nprintf "main\\037editor\\037@3\\n"\n' "${work}" "${work}" > "${work}/slow-bin/tmux"
> chmod +x "${work}/slow-bin/tmux"
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "x"}}'
> payload '{"notification_type": "permission_prompt", "message": "m"}' \
>   | env TMUX="/tmp/tmux-1000/projects,4242,0" TMUX_PANE="%7" PATH="${work}/slow-bin:${PATH}" /bin/bash "${ATTENTION_LOG_BIN}" hook Notification &
> until [[ -e "${work}/paused" ]]; do sleep 0.1; done
> hook PostToolUse '{"tool_name": "Bash", "tool_input": {}, "tool_response": {}, "tool_use_id": "t1"}' &
> sleep 1
> : > "${work}/release"
> wait
> jq -s -c '[.[].event], (.[0].id == .[1].id and .[1].id == .[2].id)' "${events_file}"
> al pending | wc -l | tr -d ' '
["permission_request","permission_waiting","cleared"]
true
0
```

## A tool result clears only its own request

```scrut
$ fresh
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "x"}}'
> hook PermissionRequest '{"tool_name": "Write", "tool_input": {"file_path": "/work/b"}}'
> hook PostToolUse '{"tool_name": "Write", "tool_input": {}, "tool_response": {}, "tool_use_id": "t1"}'
> al pending | sed 's/, [0-9]*s)$/, AGE)/'
> hook PostToolUse '{"tool_name": "Bash", "tool_input": {}, "tool_response": {}, "tool_use_id": "t2"}'
> jq -s -c '[.[2].id == .[1].id, .[3].id == .[0].id]' "${events_file}"
> al pending | wc -l | tr -d ' '
s1 (permission_request Bash, AGE)
[true,true]
0
```

## A lock whose owner has stopped is taken over

```scrut
$ fresh
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "x"}}'
> (exit 0) &
> stopped=$!
> wait "${stopped}"
> mkdir "${ATTENTION_LOG_DIR}/sessions/s1.lock"
> printf '%s\n' "${stopped}" > "${ATTENTION_LOG_DIR}/sessions/s1.lock/pid"
> hook PostToolUse '{"tool_name": "Bash", "tool_input": {}, "tool_response": {}, "tool_use_id": "t1"}'
> events .event | tail -n 1
> ls "${ATTENTION_LOG_DIR}/sessions" | grep -c lock
"cleared"
0
[1]
```

## A lock whose owner still runs is never taken over

The waiting hook gives up after about ten seconds and leaves the owner's lock in place.

```scrut
$ fresh
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "x"}}'
> sleep 30 &
> holder=$!
> mkdir "${ATTENTION_LOG_DIR}/sessions/s1.lock"
> printf '%s\n' "${holder}" > "${ATTENTION_LOG_DIR}/sessions/s1.lock/pid"
> hook PostToolUse '{"tool_name": "Bash", "tool_input": {}, "tool_response": {}, "tool_use_id": "t1"}'
> [[ "$(cat "${ATTENTION_LOG_DIR}/sessions/s1.lock/pid")" == "${holder}" ]] && echo "lock still held by its owner"
> kill "${holder}"
> events .event
lock still held by its owner
"permission_request"
```

## The next prompt clears every open state with "*"

Two requests stay open after a dismissed dialog, and one prompt closes both; a later prompt with nothing open writes nothing.

```scrut
$ fresh
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "a"}}'
> hook PermissionRequest '{"tool_name": "Write", "tool_input": {"file_path": "/work/b"}}'
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "c"}}' s2
> hook UserPromptSubmit '{"prompt": "go on"}'
> hook UserPromptSubmit '{"prompt": "again"}'
> hook Stop '{"stop_hook_active": false}'
> events '[.event, .session_id, (if .event == "cleared" then .id else .tool end)]'
["permission_request","s1","Bash"]
["permission_request","s1","Write"]
["permission_request","s2","Bash"]
["cleared","s1","*"]
```

## Turn ends and session ends clear too

```scrut
$ fresh
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "a"}}'
> hook Stop '{"stop_hook_active": false}'
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "b"}}'
> hook SessionEnd '{"reason": "other"}'
> events '[.event, .id == "*"]'
["permission_request",false]
["cleared",true]
["permission_request",false]
["cleared",true]
```

## An API error stop stays open until the next prompt

Tool results do not close it. Its error type and rendered line are recorded.

```scrut
$ fresh
> hook StopFailure '{"error": "rate_limit", "error_details": "429", "last_assistant_message": "API Error: Request rejected (429)"}'
> hook PostToolUse '{"tool_name": "Bash", "tool_input": {}, "tool_response": {}, "tool_use_id": "t1"}'
> al pending | sed 's/, [0-9]*s)$/, AGE)/'
> hook UserPromptSubmit '{"prompt": "retry"}'
> events '[.event, .error, .error_text, .id == "*"]'
s1 (api_error_stop rate_limit, AGE)
["api_error_stop","rate_limit","API Error: Request rejected (429)",false]
["cleared",null,null,true]
```

## A safeguard refusal is labeled from the transcript

The transcript's last records show the refusal: a `model_refusal_no_fallback` system record and an API-error assistant record that stopped for a refusal. The refusal's line is not recorded.

```scrut
$ fresh
> printf '%s\n' '{"type":"user","message":{"content":"a prompt"}}' '{"type":"system","subtype":"model_refusal_no_fallback"}' \
>   '{"type":"assistant","isApiErrorMessage":true,"message":{"stop_reason":"refusal"}}' > "${work}/refused.jsonl"
> hook StopFailure "$(jq -nc --arg t "${work}/refused.jsonl" '{transcript_path: $t, error: "invalid_request", last_assistant_message: "refused"}')"
> events '[.event, .error, has("error_text"), has("id")]'
["refusal_stop","invalid_request",false,true]
```

## A refusal from an earlier turn does not label a later error

A prompt after the refusal starts a new turn, so the next `invalid_request` stop is an ordinary API error. It records no error text, since a refusal the transcript could not confirm arrives the same way.

```scrut
$ fresh
> cp "${work}/refused.jsonl" "${work}/later.jsonl"
> printf '%s\n' '{"type":"user","message":{"content":"next prompt"}}' >> "${work}/later.jsonl"
> hook StopFailure "$(jq -nc --arg t "${work}/later.jsonl" '{transcript_path: $t, error: "invalid_request", last_assistant_message: "API Error: 400"}')"
> events '[.event, .error_text]'
["api_error_stop",null]
```

## A prompt with content blocks also starts a new turn

An image prompt's content is an array of blocks; a tool result's array is not a prompt and keeps the refusal.

```scrut
$ fresh
> cp "${work}/refused.jsonl" "${work}/image.jsonl"
> printf '%s\n' '{"type":"user","message":{"content":[{"type":"image"},{"type":"text","text":"look"}]}}' >> "${work}/image.jsonl"
> cp "${work}/refused.jsonl" "${work}/result.jsonl"
> printf '%s\n' '{"type":"user","message":{"content":[{"type":"tool_result","tool_use_id":"t1"}]}}' >> "${work}/result.jsonl"
> for transcript in image result; do
>   hook StopFailure "$(jq -nc --arg t "${work}/${transcript}.jsonl" '{transcript_path: $t, error: "invalid_request", last_assistant_message: "API Error: 400"}')"
> done
> events .event
"api_error_stop"
"refusal_stop"
```

## Either refusal record alone labels a refusal

```scrut
$ fresh
> printf '%s\n' '{"type":"user","message":{"content":"a prompt"}}' '{"type":"system","subtype":"model_refusal_no_fallback"}' > "${work}/system-only.jsonl"
> printf '%s\n' '{"type":"user","message":{"content":"a prompt"}}' '{"type":"assistant","isApiErrorMessage":true,"message":{"stop_reason":"refusal"}}' > "${work}/assistant-only.jsonl"
> for transcript in system-only assistant-only; do
>   hook StopFailure "$(jq -nc --arg t "${work}/${transcript}.jsonl" '{transcript_path: $t, error: "invalid_request"}')"
> done
> events .event
"refusal_stop"
"refusal_stop"
```

## A refusal written after the hook starts is still found

The hook can run before the transcript has the turn's last records, so it looks again for a short while.

```scrut
$ fresh
> printf '%s\n' '{"type":"user","message":{"content":"a prompt"}}' > "${work}/late.jsonl"
> (sleep 1 && printf '%s\n' '{"type":"system","subtype":"model_refusal_no_fallback"}' >> "${work}/late.jsonl") &
> hook StopFailure "$(jq -nc --arg t "${work}/late.jsonl" '{transcript_path: $t, error: "invalid_request", last_assistant_message: "refused"}')"
> wait
> events '[.event, has("error_text")]'
["refusal_stop",false]
```

## Elicitation dialogs are recorded without an id

```scrut
$ fresh
> hook Notification '{"notification_type": "elicitation_url_dialog", "message": "m"}'
> hook Notification '{"notification_type": "idle_prompt", "message": "m"}'
> events '[.event, .notification_type, has("id")]'
["elicitation","elicitation_url_dialog",false]
```

## A prompt pairs only with its own agent's request

With only a subagent's request open, a main-thread prompt opens its own state. The subagent's prompt repeats its request's id.

```scrut
$ fresh
> hook PermissionRequest '{"tool_name": "Bash", "agent_id": "a1", "tool_input": {"command": "x"}}'
> hook Notification '{"notification_type": "permission_prompt", "message": "m"}'
> hook Notification '{"notification_type": "permission_prompt", "agent_id": "a1", "message": "m"}'
> jq -s -c '[.[1].id != .[0].id, (.[1] | has("agent_id")), .[2].id == .[0].id]' "${events_file}"
[true,false,true]
```

## A permission prompt with no request opens its own state

A sandbox's network prompt raises no `PermissionRequest`. A second notification for it repeats its id, and the next prompt clears it.

```scrut
$ fresh
> hook Notification '{"notification_type": "permission_prompt", "message": "m"}'
> hook Notification '{"notification_type": "permission_prompt", "message": "m"}'
> al pending | sed 's/, [0-9]*s)$/, AGE)/'
> hook UserPromptSubmit '{"prompt": "ok"}'
> jq -s -c '[(.[0].id | type), .[0].id == .[1].id, .[2].event, .[2].id]' "${events_file}"
s1 (permission_waiting, AGE)
["string",true,"cleared","*"]
```

## Only this user can read the state directory

The log holds paths and session names.

```scrut
$ find "${ATTENTION_LOG_DIR}" -maxdepth 1 -type d -perm 700 | wc -l | tr -d ' '
2
```

## Files are private even in an existing open directory

```scrut
$ fresh
> mkdir -p "${ATTENTION_LOG_DIR}"
> chmod 755 "${ATTENTION_LOG_DIR}"
> hook PermissionRequest '{"tool_name": "Read", "tool_input": {"file_path": "/work/a"}}'
> echo "$(find "${ATTENTION_LOG_DIR}" -type f -perm 600 | wc -l | tr -d ' ') of $(find "${ATTENTION_LOG_DIR}" -type f | wc -l | tr -d ' ') files are 0600"
2 of 2 files are 0600
```

## Concurrent sessions never interleave lines

Forty sessions write three lines each at once, every line about 3 KB, near the size where one write could be split.

```scrut
$ fresh
> wide_cwd="/$(printf '日%.0s' {1..1000})"
> for session in $(seq 1 40); do
>   (
>     for n in 1 2 3; do
>       hook PermissionDenied "$(jq -nc --arg cwd "${wide_cwd}" '{cwd: $cwd, tool_name: "Bash", tool_input: {command: "x"}, reason: "r"}')" "s${session}"
>     done
>   ) &
> done
> wait
> echo "$(wc -l < "${events_file}" | tr -d ' ') lines, $(jq -c . "${events_file}" | wc -l | tr -d ' ') parse"
> LC_ALL=C awk '{ if (length($0) >= 3000 && length($0) < 4096) n++ } END { print n " between 3000 and 4095 bytes" }' "${events_file}"
120 lines, 120 parse
120 between 3000 and 4095 bytes
```

## An oversized line drops free-text fields until it fits

```scrut
$ fresh
> hook PermissionRequest "$(jq -nc --arg cwd "/$(printf '🙂%.0s' {1..1000})" '{cwd: $cwd, tool_name: "Edit", tool_input: {file_path: "/work/README.md"}}')"
> LC_ALL=C awk '{ print (length($0) <= 4000) }' "${events_file}"
> events '[has("subject"), has("cwd"), .tool]'
1
[false,false,"Edit"]
```

## Rotation renames the full file, keeping its inode

A reader following the file by inode carries on in `events.jsonl.1`.

```scrut
$ fresh
> mkdir -p "${ATTENTION_LOG_DIR}"
> head -c 5242880 /dev/zero > "${events_file}"
> inode="$(ls -i "${events_file}" | awk '{print $1}')"
> hook PermissionDenied '{"tool_name": "Bash", "tool_input": {"command": "x"}, "reason": "r"}'
> echo "rotated inode kept: $([[ "$(ls -i "${events_file}.1" | awk '{print $1}')" == "${inode}" ]] && echo yes || echo no)"
> echo "rotated size: $(wc -c < "${events_file}.1" | tr -d ' '), new lines: $(wc -l < "${events_file}" | tr -d ' ')"
rotated inode kept: yes
rotated size: 5242880, new lines: 1
```

## Concurrent writers rotate once

Twenty writers find the file full at once. A second rename would replace the rotated file with the new one's first lines. A writer that appends just before the rename lands in the rotated file, so the lines are counted across both.

```scrut
$ fresh
> mkdir -p "${ATTENTION_LOG_DIR}"
> head -c 5242880 /dev/zero > "${events_file}"
> for session in $(seq 1 20); do
>   hook PermissionDenied '{"tool_name": "Bash", "tool_input": {"command": "x"}, "reason": "r"}' "s${session}" &
> done
> wait
> echo "rotated file kept: $( (($(wc -c < "${events_file}.1") >= 5242880)) && echo yes || echo no)"
> echo "lines: $(cat "${events_file}.1" "${events_file}" | tr -d '\000' | grep -c '"event":"auto_denied"')"
rotated file kept: yes
lines: 20
```

## An abandoned rotation lock is taken over

```scrut
$ fresh
> mkdir -p "${ATTENTION_LOG_DIR}/rotate.lock"
> touch -t 202001010000 "${ATTENTION_LOG_DIR}/rotate.lock"
> head -c 5242880 /dev/zero > "${events_file}"
> hook PermissionDenied '{"tool_name": "Bash", "tool_input": {"command": "x"}}'
> echo "rotated: $(wc -c < "${events_file}.1" | tr -d ' '), new lines: $(wc -l < "${events_file}" | tr -d ' '), lock left: $(ls -d "${ATTENTION_LOG_DIR}/rotate.lock" 2> /dev/null | wc -l | tr -d ' ')"
rotated: 5242880, new lines: 1, lock left: 0
```

## Wait prints the next matching line and the position after it

The position is the file's inode and the byte offset after the line.

```scrut
$ fresh
> hook PermissionDenied '{"tool_name": "Bash", "tool_input": {"command": "x"}, "reason": "r"}'
> al wait --events refusal_stop,api_error_stop > "${work}/waited" &
> waiter=$!
> (sleep 15 && kill "${waiter}") > /dev/null 2>&1 &
> guard=$!
> sleep 1.5
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "a"}}'
> hook StopFailure '{"error": "overloaded", "last_assistant_message": "API Error: overloaded"}'
> wait "${waiter}"
> kill "${guard}" 2> /dev/null
> head -n 1 "${work}/waited" | jq -c .event
> inode="$(ls -di "${events_file}" | awk '{print $1}')"
> [[ "$(tail -n 1 "${work}/waited")" == "${inode}:$(wc -c < "${events_file}" | tr -d ' ')" ]] && echo "position is the end of the matching line"
"api_error_stop"
position is the end of the matching line
```

## Wait from an offset returns a line already written

```scrut
$ al wait --from 0 > "${work}/waited"
> head -n 1 "${work}/waited" | jq -c .event
> [[ "$(tail -n 1 "${work}/waited")" == "${inode}:$(head -n 1 "${events_file}" | LC_ALL=C wc -c | tr -d ' ')" ]] && echo "position is the end of the first line"
"auto_denied"
position is the end of the first line
```

## Wait continues in the rotated file

The position names the file it was taken in, so after a rotation the rest of `events.jsonl.1` comes first, even when the new file has already grown past the old offset.

```scrut
$ position="$(tail -n 1 "${work}/waited")"
> mv "${events_file}" "${events_file}.1"
> for n in 1 2 3 4; do
>   hook Notification '{"notification_type": "elicitation_dialog", "message": "m"}'
> done
> (($(wc -c < "${events_file}") > ${position#*:})) && echo "new file is past the old offset"
> al wait --from "${position}" | head -n 1 | jq -c .event
new file is past the old offset
"permission_request"
```

## Wait reads the new file once the rotated one is done

```scrut
$ position="$(al wait --from "${position}" --events api_error_stop | tail -n 1)"
> al wait --from "${position}" | head -n 1 | jq -c .event
"elicitation"
```

## Positions with leading zeros are read as base 10

```scrut
$ fresh
> hook PermissionDenied '{"tool_name": "Bash", "tool_input": {"command": "x"}}'
> hook Notification '{"notification_type": "elicitation_dialog", "message": "m"}'
> first="$(head -n 1 "${events_file}" | LC_ALL=C wc -c | tr -d ' ')"
> al wait --from "00${first}" | head -n 1 | jq -c .event
"elicitation"
```

## Positions count bytes, whatever the locale

A session name outside ASCII makes the line longer in bytes than in characters.

```scrut
$ fresh
> hook SessionStart '{"session_title": "café ☕ notes"}'
> hook PermissionRequest '{"tool_name": "Read", "tool_input": {"file_path": "/work/a"}}'
> hook PermissionRequest '{"tool_name": "Read", "tool_input": {"file_path": "/work/b"}}'
> position="$(LC_ALL=en_US.UTF-8 al wait --from 0 | tail -n 1)"
> [[ "${position#*:}" == "$(head -n 1 "${events_file}" | LC_ALL=C wc -c | tr -d ' ')" ]] && echo "offset is the first line's byte length"
> LC_ALL=en_US.UTF-8 al wait --from "${position}" | head -n 1 | jq -c .subject
offset is the first line's byte length
"/work/b"
```

## After two rotations wait starts the current file from its start

The position's file is gone, so the current file's first event comes next, even though the file is longer than the old offset.

```scrut
$ fresh
> hook PermissionDenied '{"tool_name": "Bash", "tool_input": {"command": "x"}}'
> position="$(al wait --from 0 | tail -n 1)"
> mv "${events_file}" "${events_file}.1"
> hook PermissionDenied '{"tool_name": "Bash", "tool_input": {"command": "y"}}'
> mv "${events_file}" "${events_file}.1"
> for n in 1 2 3; do hook Notification '{"notification_type": "elicitation_dialog", "message": "m"}'; done
> (($(wc -c < "${events_file}") > ${position#*:})) && echo "current file is past the old offset"
> al wait --from "${position}" > "${work}/waited"
> head -n 1 "${work}/waited" | jq -c .event
> [[ "$(tail -n 1 "${work}/waited")" == "$(ls -di "${events_file}" | awk '{print $1}'):$(head -n 1 "${events_file}" | LC_ALL=C wc -c | tr -d ' ')" ]] && echo "position is the end of the current file's first line"
current file is past the old offset
"elicitation"
position is the end of the current file's first line
```

## Wait rejects unknown events

```scrut
$ al wait --events permission_requested 2>&1 | head -n 1
attention-log: unknown event 'permission_requested'
[2]
```

## Pending lists open states as session: window lines

```scrut
$ fresh
> payload '{"tool_name": "Bash", "tool_input": {"command": "a"}}' | in_tmux hook PermissionRequest
> hook StopFailure '{"error": "server_error"}' s2
> hook PermissionRequest '{"tool_name": "Write", "tool_input": {"file_path": "/work/b"}}' s3
> hook PostToolUse '{"tool_name": "Write", "tool_input": {}, "tool_response": {}, "tool_use_id": "t"}' s3
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "b"}}' s4
> hook UserPromptSubmit '{"prompt": "never mind"}' s4
> al pending | sed 's/, [0-9]*s)$/, AGE)/'
main: editor (permission_request Bash, AGE)
s2 (api_error_stop server_error, AGE)
```

## Pending can skip recent states

```scrut
$ fresh
> mkdir -p "${ATTENTION_LOG_DIR}"
> printf '%s\n' \
>   '{"v":1,"ts":"2020-01-01T00:00:00Z","event":"permission_request","id":"old","session_id":"s1","session_name":"long wait","tool":"Bash"}' \
>   '{"v":1,"ts":"2020-01-01T00:00:00Z","event":"permission_request","id":"done","session_id":"s2","tool":"Bash"}' \
>   '{"v":1,"ts":"2020-01-01T00:00:05Z","event":"cleared","id":"done","session_id":"s2"}' > "${events_file}"
> hook PermissionRequest '{"tool_name": "Bash", "tool_input": {"command": "new"}}' s3
> al pending --older-than 03600 | sed 's/, [0-9]*s)$/, AGE)/'
long wait (permission_request Bash, AGE)
```

## Pending replays the rotated file first

A state opened before the rotation stays listed until the current file clears it.

```scrut
$ fresh
> mkdir -p "${ATTENTION_LOG_DIR}"
> printf '%s\n' \
>   '{"v":1,"ts":"2020-01-01T00:00:00Z","event":"permission_request","id":"a","session_id":"s1","tool":"Read"}' \
>   '{"v":1,"ts":"2020-01-01T00:00:01Z","event":"permission_request","id":"b","session_id":"s2","tool":"Write"}' > "${events_file}.1"
> printf '%s\n' \
>   '{"v":1,"ts":"2020-01-01T00:00:02Z","event":"cleared","id":"b","session_id":"s2"}' \
>   '{"v":1,"ts":"2020-01-01T00:00:03Z","event":"api_error_stop","id":"c","session_id":"s3","error":"overloaded"}' > "${events_file}"
> al pending | sed 's/, [0-9]*s)$/, AGE)/'
s1 (permission_request Read, AGE)
s3 (api_error_stop overloaded, AGE)
```

## Readers reject numbers too large to hold

```scrut
$ al pending --older-than 1234567890123456 2>&1 | head -n 1
attention-log: --older-than needs a number of seconds
[2]
```

## Readers report a state directory they cannot read

```scrut
$ fresh
> mkdir -p "${ATTENTION_LOG_DIR}"
> chmod 000 "${ATTENTION_LOG_DIR}"
> al pending 2>&1 | sed "s|${ATTENTION_LOG_DIR}|STATE|"; status=$?
> chmod 700 "${ATTENTION_LOG_DIR}"
> exit "${status}"
attention-log: cannot read STATE
[1]
```

## A hook without jq says so on stderr

It still prints nothing on stdout and exits 0.

```scrut
$ fresh
> mkdir -p "${work}/no-jq"
> for tool in cat mkdir; do ln -sf "$(command -v "${tool}")" "${work}/no-jq/${tool}"; done
> output="$(payload '{"tool_name": "Read", "tool_input": {"file_path": "/work/a"}}' | env -u TMUX -u TMUX_PANE PATH="${work}/no-jq" /bin/bash "${ATTENTION_LOG_BIN}" hook PermissionRequest 2> "${work}/no-jq.err")"; echo "exit $? stdout ${#output}"
> cat "${work}/no-jq.err"
exit 0 stdout 0
attention-log: jq is required and is not on PATH; no event was recorded
```

## Pending with no file prints nothing

```scrut
$ fresh
> al pending
```
