# Launch workmux

Tests for launcher stdin prompt handling, tmux recovery, and workmux argument construction.

## Test helpers

```scrut
$ function prepare_stubs() {
>   state="$(mktemp -d)"
>   stub_dir="$(mktemp -d)"
>   cp "${WORKMUX_STUB_BIN}" "${stub_dir}/workmux"
>   cp "${TMUX_STUB_BIN}" "${stub_dir}/tmux"
>   chmod +x "${stub_dir}/workmux" "${stub_dir}/tmux"
> }
> function create_socket_fixture() {
>   tmux_tmpdir="$(mktemp -d)"
>   socket_dir="${tmux_tmpdir}/tmux-$(id -u)"
>   socket_path="${socket_dir}/projects"
>   socket_pid="$("${UNIX_SOCKET_FIXTURE_BIN}" "${socket_path}")"
>   socket_real_path="$(cd "${socket_dir}" && pwd -P)/$(basename "${socket_path}")"
> }
> function cleanup_socket_fixture() {
>   if [[ -n "${socket_pid:-}" ]]; then
>     kill "${socket_pid}" 2> /dev/null || true
>     socket_pid=""
>   fi
> }
```

## Create worktree launcher escapes stdin and passes base

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Prompt with {{ user }} and {% if ok %} and {# note #}' \
>     | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/stdin-prompt" --base "main" \
>   && sleep 0.1 \
>   && prompt_file="$(cat "${state}/prompt_path")" \
>   && if [[ -e "${prompt_file}" ]]; then echo "prompt cleanup: no"; else echo "prompt cleanup: yes"; fi
workmux add
branch: feature/stdin-prompt
open-if-exists: true
base: main
prompt:
Prompt with {{ "{{" }} user }} and {{ "{%" }} if ok %} and {{ "{#" }} note #}
prompt-file-exists: yes
prompt cleanup: yes
```

## Create worktree launcher uses `WORKMUX_TMUX`

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Prompt body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_TMUX="/tmp/tmux-501/projects,123,%4" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/workmux-tmux"
workmux add
branch: feature/workmux-tmux
open-if-exists: true
term: tmux-256color
tmux: /tmp/tmux-501/projects,123,%4
prompt:
Prompt body
prompt-file-exists: yes
```

## Create worktree from issue launcher uses `WORKMUX_TMUX`

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Issue body with {{ value }}' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_TMUX="/tmp/tmux-501/projects,123,%4" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN}" "feature/issue-265"
workmux add
branch: feature/issue-265
open-if-exists: true
term: tmux-256color
tmux: /tmp/tmux-501/projects,123,%4
prompt:
Issue body with {{ "{{" }} value }}
prompt-file-exists: yes
```

## Create worktree launcher keeps existing `TMUX`

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Prompt body' \
>     | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb TMUX="/tmp/tmux-501/existing,111,%1" WORKMUX_TMUX="/tmp/tmux-501/workmux,222,%2" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/existing-tmux"
workmux add
branch: feature/existing-tmux
open-if-exists: true
term: tmux-256color
tmux: /tmp/tmux-501/existing,111,%1
prompt:
Prompt body
prompt-file-exists: yes
```

## Create worktree from issue launcher keeps existing `TMUX`

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Issue body' \
>     | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb TMUX="/tmp/tmux-501/existing,111,%1" WORKMUX_TMUX="/tmp/tmux-501/workmux,222,%2" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN}" "feature/existing-tmux-issue"
workmux add
branch: feature/existing-tmux-issue
open-if-exists: true
term: tmux-256color
tmux: /tmp/tmux-501/existing,111,%1
prompt:
Issue body
prompt-file-exists: yes
```

## Create worktree launcher discovers one matching Codex pane

```scrut
$ prepare_stubs \
>   && create_socket_fixture \
>   && trap cleanup_socket_fixture EXIT \
>   && cwd="$(pwd -P)" \
>   && panes="${socket_real_path}|%7|cx|${cwd}|4242" \
>   && printf '%s\n' 'Prompt body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" TMUX_TMPDIR="${tmux_tmpdir}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/discovered-tmux" \
>   && cleanup_socket_fixture \
>   && trap - EXIT
workmux add
branch: feature/discovered-tmux
open-if-exists: true
term: tmux-256color
tmux: */projects,4242,%7 (glob)
prompt:
Prompt body
prompt-file-exists: yes
```

## Create worktree from issue launcher discovers one matching Codex pane

```scrut
$ prepare_stubs \
>   && create_socket_fixture \
>   && trap cleanup_socket_fixture EXIT \
>   && cwd="$(pwd -P)" \
>   && panes="${socket_real_path}|%7|codex-aarch64-a|${cwd}|4242" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" TMUX_TMPDIR="${tmux_tmpdir}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN}" "feature/discovered-tmux-issue" \
>   && cleanup_socket_fixture \
>   && trap - EXIT
workmux add
branch: feature/discovered-tmux-issue
open-if-exists: true
term: tmux-256color
tmux: */projects,4242,%7 (glob)
prompt:
Issue body
prompt-file-exists: yes
```

## Create worktree launcher ignores ambiguous Codex panes

```scrut
$ prepare_stubs \
>   && create_socket_fixture \
>   && trap cleanup_socket_fixture EXIT \
>   && cwd="$(pwd -P)" \
>   && panes="${socket_real_path}|%7|cx|${cwd}|4242"$'\n'"${socket_real_path}|%8|codex|${cwd}|4242" \
>   && printf '%s\n' 'Prompt body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" TMUX_TMPDIR="${tmux_tmpdir}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/ambiguous-tmux" \
>   && cleanup_socket_fixture \
>   && trap - EXIT
workmux add
branch: feature/ambiguous-tmux
open-if-exists: true
term: dumb
tmux: <unset>
prompt:
Prompt body
prompt-file-exists: yes
```

## Create worktree from issue launcher ignores ambiguous Codex panes

```scrut
$ prepare_stubs \
>   && create_socket_fixture \
>   && trap cleanup_socket_fixture EXIT \
>   && cwd="$(pwd -P)" \
>   && panes="${socket_real_path}|%7|cx|${cwd}|4242"$'\n'"${socket_real_path}|%8|codex|${cwd}|4242" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" TMUX_TMPDIR="${tmux_tmpdir}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN}" "feature/ambiguous-tmux-issue" \
>   && cleanup_socket_fixture \
>   && trap - EXIT
workmux add
branch: feature/ambiguous-tmux-issue
open-if-exists: true
term: dumb
tmux: <unset>
prompt:
Issue body
prompt-file-exists: yes
```

## Create worktree launcher continues without `tmux`

```scrut
$ state="$(mktemp -d)" \
>   && stub_dir="$(mktemp -d)" \
>   && cp "${WORKMUX_STUB_BIN}" "${stub_dir}/workmux" \
>   && chmod +x "${stub_dir}/workmux" \
>   && printf '%s\n' 'Prompt body' \
>     | env -u TMUX PATH="${stub_dir}:/usr/bin:/bin:/usr/sbin:/sbin" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/no-tmux-command"
workmux add
branch: feature/no-tmux-command
open-if-exists: true
term: dumb
tmux: <unset>
prompt:
Prompt body
prompt-file-exists: yes
```

## Create worktree from issue launcher continues without `tmux`

```scrut
$ state="$(mktemp -d)" \
>   && stub_dir="$(mktemp -d)" \
>   && cp "${WORKMUX_STUB_BIN}" "${stub_dir}/workmux" \
>   && chmod +x "${stub_dir}/workmux" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:/usr/bin:/bin:/usr/sbin:/sbin" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN}" "feature/no-tmux-command-issue"
workmux add
branch: feature/no-tmux-command-issue
open-if-exists: true
term: dumb
tmux: <unset>
prompt:
Issue body
prompt-file-exists: yes
```

## Create worktree launcher rejects empty stdin

```scrut
$ branch="feature/missing-prompt-${BASHPID}" && safe_name="${branch//\//-}" && exit_code=0 && env WORKMUX_LAUNCH_WAIT_SECONDS=0 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "${branch}" < /dev/null 2>&1 || exit_code=$?; if compgen -G "/tmp/workmux-${safe_name}.log.*" > /dev/null || compgen -G "/tmp/workmux-prompt-${safe_name}.md.*" > /dev/null; then echo "temp cleanup: no"; else echo "temp cleanup: yes"; fi; exit "${exit_code}"
launch-workmux: expected prompt content on stdin
temp cleanup: yes
[1]
```

## Create worktree from issue launcher rejects empty stdin

```scrut
$ branch="feature/missing-prompt-${BASHPID}" && safe_name="${branch//\//-}" && exit_code=0 && env WORKMUX_LAUNCH_WAIT_SECONDS=0 bash "${CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN}" "${branch}" < /dev/null 2>&1 || exit_code=$?; if compgen -G "/tmp/workmux-${safe_name}.log.*" > /dev/null || compgen -G "/tmp/workmux-prompt-${safe_name}.md.*" > /dev/null; then echo "temp cleanup: no"; else echo "temp cleanup: yes"; fi; exit "${exit_code}"
launch-workmux: expected prompt content on stdin
temp cleanup: yes
[1]
```
