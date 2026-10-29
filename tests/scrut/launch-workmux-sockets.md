# Launch workmux socket discovery

Socket-dependent launcher cases are separate so restricted environments still run
the other launcher tests. Scrut suppresses captured output when a document is
skipped, so its summary shows skip counts without the fixture's stderr reason.
Run the fixture directly to see that reason.

## Test helpers

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut {fail_fast: true}
$ function prepare_stubs() {
>   unset TMUX TMUX_TMPDIR WORKMUX_TMUX WORKMUX_TERM
>   state="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
>   stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
>   cp "${WORKMUX_STUB_BIN}" "${stub_dir}/workmux"
>   cp "${TMUX_STUB_BIN}" "${stub_dir}/tmux"
>   cp "${WORKTREE_GIT_STUB_BIN}" "${stub_dir}/git"
>   chmod +x "${stub_dir}/workmux" "${stub_dir}/tmux" "${stub_dir}/git"
>   local tool
>   for tool in workmux tmux git; do
>     [[ "$(PATH="${stub_dir}:${PATH}" command -v "${tool}")" == "${stub_dir}/${tool}" ]] || return 1
>   done
> }
> function create_socket_fixture() {
>   tmux_tmpdir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
>   socket_dir="${tmux_tmpdir}/tmux-$(id -u)"
>   socket_path="${socket_dir}/projects"
>   local socket_status=0
>   socket_pid="$("${UNIX_SOCKET_FIXTURE_BIN}" "${socket_path}")" || socket_status=$?
>   if ((socket_status != 0)); then
>     cleanup_socket_fixture
>     exit "${socket_status}"
>   fi
>   socket_real_path="$(cd "${socket_dir}" && pwd -P)/${socket_path##*/}"
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

## Socket availability

The fixture exits with Scrut's document skip code (80) and a reason when socket
creation or connection is denied. Other fixture errors remain failures.

```scrut {fail_fast: true}
$ create_socket_fixture && cleanup_socket_fixture
```

## Create worktree launcher discovers one matching Codex pane

```scrut
$ prepare_stubs \
>   && create_socket_fixture \
>   && trap cleanup_socket_fixture EXIT \
>   && cwd="$(pwd -P)" \
>   && panes="${socket_real_path}|%7|cx|${cwd}|4242" \
>   && printf '%s\n' 'Prompt body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" TMUX_TMPDIR="${tmux_tmpdir}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb bash "${LAUNCH_WORKMUX_BIN}" "feature/discovered-tmux" \
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

## Address issue in worktree launcher discovers one matching Codex pane

```scrut
$ prepare_stubs \
>   && create_socket_fixture \
>   && trap cleanup_socket_fixture EXIT \
>   && cwd="$(pwd -P)" \
>   && panes="${socket_real_path}|%7|codex-aarch64-a|${cwd}|4242" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" TMUX_TMPDIR="${tmux_tmpdir}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb bash "${LAUNCH_WORKMUX_BIN}" "feature/discovered-tmux-issue" \
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
>     | env -u TMUX PATH="${stub_dir}:${PATH}" TMUX_TMPDIR="${tmux_tmpdir}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb bash "${LAUNCH_WORKMUX_BIN}" "feature/ambiguous-tmux" \
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

## Address issue in worktree launcher ignores ambiguous Codex panes

```scrut
$ prepare_stubs \
>   && create_socket_fixture \
>   && trap cleanup_socket_fixture EXIT \
>   && cwd="$(pwd -P)" \
>   && panes="${socket_real_path}|%7|cx|${cwd}|4242"$'\n'"${socket_real_path}|%8|codex|${cwd}|4242" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" TMUX_TMPDIR="${tmux_tmpdir}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb bash "${LAUNCH_WORKMUX_BIN}" "feature/ambiguous-tmux-issue" \
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
