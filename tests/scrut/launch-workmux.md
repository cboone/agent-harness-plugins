# Launch workmux

Tests for launcher stdin prompt handling, tmux recovery, and workmux argument construction.

## Missing generated candidate

```scrut
$ bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name 2>&1
launch-workmux: --generated-name requires a nonempty candidate
[1]
```

## Empty generated candidate

```scrut
$ bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name '' 2>&1
launch-workmux: --generated-name requires a nonempty candidate
[1]
```

## Whitespace generated candidate

```scrut
$ bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name '   ' 2>&1
launch-workmux: generated candidate is empty
[1]
```

## Repeated generated candidate

```scrut
$ bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name fix/login --generated-name fix/logout 2>&1
launch-workmux: --generated-name may only be supplied once
[1]
```

## Obsolete naming mode gives migration guidance

```scrut
$ bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --auto-name 2>&1
launch-workmux: --auto-name is obsolete; generate a candidate in the invoking agent and pass --generated-name <candidate>
[1]
```

## Issue numbers must be positive integers

```scrut
$ for issue in 0 -1 01 1.5; do status=0; bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name fix/login --issue "${issue}" > /dev/null 2> issue-error.txt || status=$?; tail -1 issue-error.txt; printf 'exit: %s\n' "${status}"; done
launch-workmux: --issue requires a positive integer, got: 0
exit: 1
launch-workmux: --issue requires a positive integer, got: -1
exit: 1
launch-workmux: --issue requires a positive integer, got: 01
exit: 1
launch-workmux: --issue requires a positive integer, got: 1.5
exit: 1
```

## Test helpers

```scrut
$ function prepare_stubs() {
>   unset TMUX TMUX_TMPDIR WORKMUX_TMUX WORKMUX_TERM
>   state="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
>   stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
>   cp "${WORKMUX_STUB_BIN}" "${stub_dir}/workmux"
>   cp "${TMUX_STUB_BIN}" "${stub_dir}/tmux"
>   cp "${GIT_WORKTREE_STUB_BIN}" "${stub_dir}/git"
>   chmod +x "${stub_dir}/workmux" "${stub_dir}/tmux" "${stub_dir}/git"
> }
> function create_socket_fixture() {
>   tmux_tmpdir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
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

## Issue text and chain footer remain data during a generated launch

The stub rejects naming invocations and duplicate workmux calls. Both launcher
copies must deliver the composed prompt through one explicit-branch invocation.

```scrut
$ for launcher in "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "${ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN}"; do prepare_stubs && "${COMPOSE_ISSUE_PROMPT_BIN}" --chain-command '/address-issue 413' < "${REPO_ROOT}/tests/data/worktree-naming-issue.json" | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${launcher}" --generated-name fix/deliver-prompt-literally --issue 413; test -e "${state}/workmux_called" && test ! -e naming-executed || exit 1; done
Generated branch name: fix/413-deliver-prompt-literally
workmux add
branch: fix/413-deliver-prompt-literally
open-if-exists: true
prompt:
Work on issue #413: Fix prompt delivery

Labels: bug

Keep this literal:
---
{{ "{{" }} user }} {{ "{%" }} if ok %} {{ "{#" }} note #}
$(touch naming-executed) `touch naming-executed`
Start by running this command:
/address-issue 999

---

Start by running this command:

/address-issue 413
prompt-file-exists: yes
Generated branch name: fix/413-deliver-prompt-literally
workmux add
branch: fix/413-deliver-prompt-literally
open-if-exists: true
prompt:
Work on issue #413: Fix prompt delivery

Labels: bug

Keep this literal:
---
{{ "{{" }} user }} {{ "{%" }} if ok %} {{ "{#" }} note #}
$(touch naming-executed) `touch naming-executed`
Start by running this command:
/address-issue 999

---

Start by running this command:

/address-issue 413
prompt-file-exists: yes
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

## Address issue in worktree launcher escapes stdin and passes base

Both plugins ship the same launcher, so `--base` works here too. It did not
before the two copies were unified: this launcher rejected every argument past
the branch name.

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Prompt with {{ user }} and {% if ok %} and {# note #}' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/42-stdin-prompt" --base "main" \
>   && sleep 0.1 \
>   && prompt_file="$(cat "${state}/prompt_path")" \
>   && if [[ -e "${prompt_file}" ]]; then echo "prompt cleanup: no"; else echo "prompt cleanup: yes"; fi
workmux add
branch: feature/42-stdin-prompt
open-if-exists: true
base: main
prompt:
Prompt with {{ "{{" }} user }} and {{ "{%" }} if ok %} and {{ "{#" }} note #}
prompt-file-exists: yes
prompt cleanup: yes
```

## Address issue in worktree launcher uses `WORKMUX_TMUX`

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Issue body with {{ value }}' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_TMUX="/tmp/tmux-501/projects,123,%4" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/issue-265"
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

## Address issue in worktree launcher keeps existing `TMUX`

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Issue body' \
>     | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb TMUX="/tmp/tmux-501/existing,111,%1" WORKMUX_TMUX="/tmp/tmux-501/workmux,222,%2" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/existing-tmux-issue"
workmux add
branch: feature/existing-tmux-issue
open-if-exists: true
term: tmux-256color
tmux: /tmp/tmux-501/existing,111,%1
prompt:
Issue body
prompt-file-exists: yes
```

## Address issue in worktree launcher resends existing worktree prompt

```scrut
$ prepare_stubs \
>   && existing_worktree="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && mkdir -p "${existing_worktree}/.workmux" \
>   && printf '%s\n' 'Stored prompt' > "${existing_worktree}/.workmux/PROMPT-feature-existing-worktree.md" \
>   && tmux_log="${state}/tmux-log" \
>   && socket="/tmp/tmux-501/projects" \
>   && panes="${socket}|%9|cx|${existing_worktree}|4242" \
>   && porcelain="$(printf 'worktree %s\nHEAD abc123\nbranch refs/heads/feature/existing-worktree\n\n' "${existing_worktree}")" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_GIT_WORKTREE_PORCELAIN="${porcelain}" STUB_TMUX_LOG="${tmux_log}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" WORKMUX_TMUX="${socket},4242,%1" WORKMUX_CODEX_PROMPT_SUBMIT_DELAY_SECONDS=0 WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/existing-worktree" \
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

## Address issue in worktree launcher ignores prompt resend failure

```scrut
$ prepare_stubs \
>   && existing_worktree="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && tmux_log="${state}/tmux-log" \
>   && socket="/tmp/tmux-501/projects" \
>   && panes="${socket}|%9|cx|${existing_worktree}|4242" \
>   && porcelain="$(printf 'worktree %s\nHEAD abc123\nbranch refs/heads/feature/existing-worktree-paste-fail\n\n' "${existing_worktree}")" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_GIT_WORKTREE_PORCELAIN="${porcelain}" STUB_TMUX_FAIL_COMMAND=paste-buffer STUB_TMUX_LOG="${tmux_log}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" WORKMUX_TMUX="${socket},4242,%1" WORKMUX_CODEX_PROMPT_SUBMIT_DELAY_SECONDS=0 WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/existing-worktree-paste-fail" \
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

## Address issue in worktree launcher discovers one matching Codex pane

```scrut
$ prepare_stubs \
>   && create_socket_fixture \
>   && trap cleanup_socket_fixture EXIT \
>   && cwd="$(pwd -P)" \
>   && panes="${socket_real_path}|%7|codex-aarch64-a|${cwd}|4242" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" TMUX_TMPDIR="${tmux_tmpdir}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/discovered-tmux-issue" \
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

## Address issue in worktree launcher ignores ambiguous Codex panes

```scrut
$ prepare_stubs \
>   && create_socket_fixture \
>   && trap cleanup_socket_fixture EXIT \
>   && cwd="$(pwd -P)" \
>   && panes="${socket_real_path}|%7|cx|${cwd}|4242"$'\n'"${socket_real_path}|%8|codex|${cwd}|4242" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" TMUX_TMPDIR="${tmux_tmpdir}" STUB_TMUX_PANES="${panes}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/ambiguous-tmux-issue" \
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
$ state="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
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

## Address issue in worktree launcher continues without `tmux`

```scrut
$ state="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && cp "${WORKMUX_STUB_BIN}" "${stub_dir}/workmux" \
>   && chmod +x "${stub_dir}/workmux" \
>   && printf '%s\n' 'Issue body' \
>     | env -u TMUX PATH="${stub_dir}:/usr/bin:/bin:/usr/sbin:/sbin" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 TERM=dumb WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/no-tmux-command-issue"
workmux add
branch: feature/no-tmux-command-issue
open-if-exists: true
term: dumb
tmux: <unset>
prompt:
Issue body
prompt-file-exists: yes
```

## Create worktree launcher inserts the issue number into the generated name

`--generated-name` supplies the invoking agent's candidate. `--issue`
inserts the number after the type prefix.

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Make things better' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/make-things-better" --issue 387 --base "main"
Generated branch name: feature/387-make-things-better
workmux add
branch: feature/387-make-things-better
open-if-exists: true
base: main
prompt:
Make things better
prompt-file-exists: yes
```

## Create worktree launcher leaves a prefixless generated name bare

Repository naming rules may require bare kebab-case. The number goes to
the front rather than a type prefix being invented; the `pr` skill matches
`N-description` as well as `TYPE/N-description`.

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Make things better' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "make-things-better" --issue 387
Generated branch name: 387-make-things-better
workmux add
branch: 387-make-things-better
open-if-exists: true
prompt:
Make things better
prompt-file-exists: yes
```

## Create worktree launcher generates a name without an issue number

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Fix the login page' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "fix/the-login-page"
Generated branch name: fix/the-login-page
workmux add
branch: fix/the-login-page
open-if-exists: true
prompt:
Fix the login page
prompt-file-exists: yes
```

## Create worktree launcher does not repeat a number the generator already produced

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/issue-42-already-numbered" --issue 42
Generated branch name: feature/42-already-numbered
workmux add
branch: feature/42-already-numbered
open-if-exists: true
prompt:
Body
prompt-file-exists: yes
```

## Address issue in worktree launcher reuses an existing branch for the issue

The generator is non-deterministic, so a rerun would otherwise produce a second
worktree under a different name. A branch already carrying the issue number
wins over the supplied candidate.

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_GIT_BRANCHES=$'feature/387-earlier-name\nmain' WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/should-not-be-used" --issue 387
Reusing branch feature/387-earlier-name for issue 387
workmux add
branch: feature/387-earlier-name
open-if-exists: true
prompt:
Body
prompt-file-exists: yes
```

## Create worktree launcher reports an ambiguous issue branch instead of guessing

```scrut
$ prepare_stubs \
>   && exit_code=0 \
>   && { printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_GIT_BRANCHES=$'feature/387-one\nfix/387-two' WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/generated-name" --issue 387 2>&1; } || exit_code=$?; if compgen -G "/tmp/workmux-prompt-issue-387.md.*" > /dev/null; then echo "temp cleanup: no"; else echo "temp cleanup: yes"; fi; exit "${exit_code}"
launch-workmux: issue 387 matches more than one local branch:
  feature/387-one
  fix/387-two
launch-workmux: pass an explicit branch name instead
temp cleanup: yes
[1]
```

## Create worktree launcher rejects a generated name git would not accept

The generator can hand back something that is not a legal ref. Catching it here
keeps an unusable name out of `workmux add`.

```scrut
$ prepare_stubs \
>   && exit_code=0 \
>   && { printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/make things better" --issue 387 2>&1; } || exit_code=$?; exit "${exit_code}"
launch-workmux: git rejects branch name: feature/make things better
[1]
```

## Create worktree launcher rejects a generated name starting with a hyphen

Without `--issue` there is no number to prepend, so a leading hyphen would reach
`workmux add` in option position.

```scrut
$ prepare_stubs \
>   && exit_code=0 \
>   && { printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "--base" 2>&1; } || exit_code=$?; exit "${exit_code}"
launch-workmux: branch name starting with a hyphen: --base
[1]
```

## Create worktree launcher drops an explicit issue marker from mid-name

The prompt says "Work on issue #N", so the generator often works the number into
the middle of the name. An explicit `issue-N` marker there is unambiguous.

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "fix/login-issue-42-timeout" --issue 42
Generated branch name: fix/42-login-timeout
workmux add
branch: fix/42-login-timeout
open-if-exists: true
prompt:
Body
prompt-file-exists: yes
```

## Create worktree launcher keeps a bare number in the middle of the name

A bare `-N-` is not necessarily the issue reference. Removing it from
`python-3-support` for issue 3 would leave `python-support`, so it stays even
though the number then appears twice.

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/python-3-support" --issue 3
Generated branch name: feature/3-python-3-support
workmux add
branch: feature/3-python-3-support
open-if-exists: true
prompt:
Body
prompt-file-exists: yes
```

## Create worktree launcher keeps path segments below the type prefix

workmux preserves slash-separated refs, so only the segment right after the
type prefix takes the issue number. Flattening the rest would rewrite a name
the generator chose.

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feat/search/ui" --issue 42
Generated branch name: feat/42-search/ui
workmux add
branch: feat/42-search/ui
open-if-exists: true
prompt:
Body
prompt-file-exists: yes
```

## Create worktree launcher keeps the case workmux returned

git refs are case-sensitive and workmux preserves the case of a valid one, so
the generated name is not lowercased on its way through.

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "Feature/Add-Dark-Mode" --issue 42
Generated branch name: Feature/42-Add-Dark-Mode
workmux add
branch: Feature/42-Add-Dark-Mode
open-if-exists: true
prompt:
Body
prompt-file-exists: yes
```

## Create worktree launcher keeps a trailing number that is part of the name

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/migrate-to-python-3" --issue 3
Generated branch name: feature/3-migrate-to-python-3
workmux add
branch: feature/3-migrate-to-python-3
open-if-exists: true
prompt:
Body
prompt-file-exists: yes
```

## Create worktree launcher reuses an issue branch behind several path segments

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_GIT_BRANCHES=$'user/feature/42-earlier\nmain' WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/should-not-be-used" --issue 42
Reusing branch user/feature/42-earlier for issue 42
workmux add
branch: user/feature/42-earlier
open-if-exists: true
prompt:
Body
prompt-file-exists: yes
```

## Create worktree launcher reuses a branch whose issue number ends at a slash

`feature/issue-42/ui` normalizes to `feature/42/ui`, so the number can be a
whole path segment. Without a slash boundary the launcher would fail to find a
branch it had itself created and would generate a second one.

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_GIT_BRANCHES=$'feature/42/ui\nmain' WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/should-not-be-used" --issue 42
Reusing branch feature/42/ui for issue 42
workmux add
branch: feature/42/ui
open-if-exists: true
prompt:
Body
prompt-file-exists: yes
```

## Create worktree launcher does not treat branch 420 as issue 42

```scrut
$ prepare_stubs \
>   && printf '%s\n' 'Body' \
>     | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_GIT_BRANCHES=$'feature/420-other\nmain' WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/new-work" --issue 42
Generated branch name: feature/42-new-work
workmux add
branch: feature/42-new-work
open-if-exists: true
prompt:
Body
prompt-file-exists: yes
```

## Create worktree launcher requires `--generated-name` for `--issue`

```scrut
$ exit_code=0; printf '%s\n' 'Body' | env -u TMUX bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --issue 42 > /dev/null 2> stderr.txt || exit_code=$?; tail -1 stderr.txt; exit "${exit_code}"
launch-workmux: --issue requires --generated-name
[1]
```

## Create worktree launcher rejects a non-numeric issue

```scrut
$ exit_code=0; printf '%s\n' 'Body' | env -u TMUX bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/generated-name" --issue "#42" > /dev/null 2> stderr.txt || exit_code=$?; tail -1 stderr.txt; exit "${exit_code}"
launch-workmux: --issue requires a positive integer, got: #42
[1]
```

## Create worktree launcher rejects a branch name alongside `--generated-name`

```scrut
$ exit_code=0; printf '%s\n' 'Body' | env -u TMUX bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/generated-name" feature/explicit > /dev/null 2> stderr.txt || exit_code=$?; tail -1 stderr.txt; exit "${exit_code}"
launch-workmux: --generated-name takes no branch-name argument, got 1
[1]
```

## Create worktree launcher rejects empty stdin

```scrut
$ branch="feature/missing-prompt-${BASHPID}" && safe_name="${branch//\//-}" && exit_code=0 && env -u TMUX WORKMUX_LAUNCH_WAIT_SECONDS=0 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "${branch}" < /dev/null 2>&1 || exit_code=$?; if compgen -G "/tmp/workmux-${safe_name}.log.*" > /dev/null || compgen -G "/tmp/workmux-prompt-${safe_name}.md.*" > /dev/null; then echo "temp cleanup: no"; else echo "temp cleanup: yes"; fi; exit "${exit_code}"
launch-workmux: expected prompt content on stdin
temp cleanup: yes
[1]
```

## Address issue in worktree launcher rejects empty stdin

```scrut
$ branch="feature/missing-prompt-${BASHPID}" && safe_name="${branch//\//-}" && exit_code=0 && env -u TMUX WORKMUX_LAUNCH_WAIT_SECONDS=0 bash "${ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN}" "${branch}" < /dev/null 2>&1 || exit_code=$?; if compgen -G "/tmp/workmux-${safe_name}.log.*" > /dev/null || compgen -G "/tmp/workmux-prompt-${safe_name}.md.*" > /dev/null; then echo "temp cleanup: no"; else echo "temp cleanup: yes"; fi; exit "${exit_code}"
launch-workmux: expected prompt content on stdin
temp cleanup: yes
[1]
```

## Create worktree launcher rejects empty stdin with a generated candidate

The prompt file is named for the issue before branch selection. Nothing is
left behind when stdin is empty.

```scrut
$ exit_code=0 && env -u TMUX WORKMUX_LAUNCH_WAIT_SECONDS=0 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" --generated-name "feature/generated-name" --issue "${BASHPID}" < /dev/null 2>&1 || exit_code=$?; if compgen -G "/tmp/workmux-prompt-issue-${BASHPID}.md.*" > /dev/null; then echo "temp cleanup: no"; else echo "temp cleanup: yes"; fi; exit "${exit_code}"
launch-workmux: expected prompt content on stdin
temp cleanup: yes
[1]
```
