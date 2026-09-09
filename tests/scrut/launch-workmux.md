# Launch workmux

Tests for launcher stdin prompt handling, tmux recovery, and workmux argument construction.

## Test helpers

```scrut
$ function prepare_stubs() {
>   unset TMUX TMUX_TMPDIR WORKMUX_TMUX WORKMUX_TERM
>   state="$(mktemp -d)"
>   stub_dir="$(mktemp -d)"
>   cp "${WORKMUX_STUB_BIN}" "${stub_dir}/workmux"
>   cp "${TMUX_STUB_BIN}" "${stub_dir}/tmux"
>   cp "${GIT_WORKTREE_STUB_BIN}" "${stub_dir}/git"
>   chmod +x "${stub_dir}/workmux" "${stub_dir}/tmux" "${stub_dir}/git"
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
>   if [[ -n "${tmux_tmpdir:-}" ]]; then
>     rm -r -- "${tmux_tmpdir}"
>     tmux_tmpdir=""
>     socket_dir=""
>     socket_path=""
>     socket_real_path=""
>   fi
> }
```

## Create worktree launcher escapes stdin and passes base

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Prompt with {{ user }} and {% if ok %} and {# note #}' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/stdin-prompt" --base "main" \
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

## Create worktree from issue launcher resends existing worktree prompt

```scrut
$ prepare_stubs \
>   && existing_worktree="$(mktemp -d)" \
>   && mkdir -p "${existing_worktree}/.workmux" \
>   && printf '%s\n' 'Stored prompt' > "${existing_worktree}/.workmux/PROMPT-feature-existing-worktree.md" \
>   && tmux_log="${state}/tmux-log" \
>   && socket="/tmp/tmux-501/projects" \
>   && panes="${socket}|%9|cx|${existing_worktree}|4242" \
>   && porcelain="$(printf 'worktree %s\nHEAD abc123\nbranch refs/heads/feature/existing-worktree\n\n' "${existing_worktree}")" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_GIT_WORKTREE_PORCELAIN="${porcelain}" STUB_TMUX_LOG="${tmux_log}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" WORKMUX_TMUX="${socket},4242,%1" WORKMUX_CODEX_PROMPT_SUBMIT_DELAY_SECONDS=0 WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN}" "feature/existing-worktree" \
>   && sed "s|${existing_worktree}|<worktree>|g" "${tmux_log}"
workmux add
branch: feature/existing-worktree
open-if-exists: true
prompt:
Issue body
prompt-file-exists: yes
Sent prompt to existing Codex pane for * (glob)
tmux: load-buffer socket=/tmp/tmux-501/projects buffer=workmux-prompt-feature-existing-worktree file=*/.workmux/PROMPT-feature-existing-worktree.md (glob)
tmux: paste-buffer socket=/tmp/tmux-501/projects target=%9 buffer=workmux-prompt-feature-existing-worktree
tmux: send-keys socket=/tmp/tmux-501/projects target=%9 keys=Enter
tmux: send-keys socket=/tmp/tmux-501/projects target=%9 keys=Enter
tmux: delete-buffer socket=/tmp/tmux-501/projects buffer=workmux-prompt-feature-existing-worktree
```

## Create worktree from issue launcher ignores prompt resend failure

```scrut
$ prepare_stubs \
>   && existing_worktree="$(mktemp -d)" \
>   && tmux_log="${state}/tmux-log" \
>   && socket="/tmp/tmux-501/projects" \
>   && panes="${socket}|%9|cx|${existing_worktree}|4242" \
>   && porcelain="$(printf 'worktree %s\nHEAD abc123\nbranch refs/heads/feature/existing-worktree-paste-fail\n\n' "${existing_worktree}")" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_GIT_WORKTREE_PORCELAIN="${porcelain}" STUB_TMUX_FAIL_COMMAND=paste-buffer STUB_TMUX_LOG="${tmux_log}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" WORKMUX_TMUX="${socket},4242,%1" WORKMUX_CODEX_PROMPT_SUBMIT_DELAY_SECONDS=0 WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN}" "feature/existing-worktree-paste-fail" \
>   && sed "s|${existing_worktree}|<worktree>|g" "${tmux_log}"
workmux add
branch: feature/existing-worktree-paste-fail
open-if-exists: true
prompt:
Issue body
prompt-file-exists: yes
tmux: load-buffer socket=/tmp/tmux-501/projects buffer=workmux-prompt-feature-existing-worktree-paste-fail file=* (glob)
tmux: paste-buffer socket=/tmp/tmux-501/projects target=%9 buffer=workmux-prompt-feature-existing-worktree-paste-fail
tmux: delete-buffer socket=/tmp/tmux-501/projects buffer=workmux-prompt-feature-existing-worktree-paste-fail
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
$ branch="feature/missing-prompt-${BASHPID}" && safe_name="${branch//\//-}" && exit_code=0 && env -u TMUX WORKMUX_LAUNCH_WAIT_SECONDS=0 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "${branch}" < /dev/null 2>&1 || exit_code=$?; if compgen -G "/tmp/workmux-${safe_name}.log.*" > /dev/null || compgen -G "/tmp/workmux-prompt-${safe_name}.md.*" > /dev/null; then echo "temp cleanup: no"; else echo "temp cleanup: yes"; fi; exit "${exit_code}"
launch-workmux: expected prompt content on stdin
temp cleanup: yes
[1]
```

## Create worktree from issue launcher rejects empty stdin

```scrut
$ branch="feature/missing-prompt-${BASHPID}" && safe_name="${branch//\//-}" && exit_code=0 && env -u TMUX WORKMUX_LAUNCH_WAIT_SECONDS=0 bash "${CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN}" "${branch}" < /dev/null 2>&1 || exit_code=$?; if compgen -G "/tmp/workmux-${safe_name}.log.*" > /dev/null || compgen -G "/tmp/workmux-prompt-${safe_name}.md.*" > /dev/null; then echo "temp cleanup: no"; else echo "temp cleanup: yes"; fi; exit "${exit_code}"
launch-workmux: expected prompt content on stdin
temp cleanup: yes
[1]
```
