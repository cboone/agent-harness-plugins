# Launcher destination options

Tests for config and agent forwarding and validation.

## Test helpers

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
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
```

## Config and agent reach an explicit launch

```scrut
$ prepare_stubs && printf 'agent: codex\n' > 'profile with spaces.yaml' && printf 'Task\n' | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --config 'profile with spaces.yaml' --agent 'claude --model opus'
workmux add
branch: feature/profile
config: profile with spaces.yaml
agent: claude --model opus
open-if-exists: true
prompt:
Task
prompt-file-exists: yes
```

## Config and agent reach a generated launch

```scrut
$ prepare_stubs && printf 'agent: codex\n' > profile.yaml && printf 'Task\n' | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" --generated-name feature/profile --issue 629 --config profile.yaml --agent codex
Generated branch name: feature/629-profile
workmux add
branch: feature/629-profile
config: profile.yaml
agent: codex
open-if-exists: true
prompt:
Task
prompt-file-exists: yes
```

## Config works without an agent override

```scrut
$ prepare_stubs && printf 'agent: codex\n' > profile.yaml && printf 'Task\n' | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --config profile.yaml
workmux add
branch: feature/profile
config: profile.yaml
open-if-exists: true
prompt:
Task
prompt-file-exists: yes
```

## Agent works without a config override

```scrut
$ prepare_stubs && printf 'Task\n' | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --agent codex
workmux add
branch: feature/profile
agent: codex
open-if-exists: true
prompt:
Task
prompt-file-exists: yes
```

## Missing config argument

```scrut
$ prepare_stubs && status=0; env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --config <<< 'Task' 2>&1 || status=$?; test ! -e "${state}/workmux_called" && test "${status}" = 1
launch-workmux: --config requires a readable file
```

## Empty config argument

```scrut
$ prepare_stubs && status=0; env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --config '' <<< 'Task' 2>&1 || status=$?; test ! -e "${state}/workmux_called" && test "${status}" = 1
launch-workmux: --config requires a readable file
```

## Config flag cannot consume another option

```scrut
$ prepare_stubs && status=0; env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --config --agent codex <<< 'Task' 2>&1 || status=$?; test ! -e "${state}/workmux_called" && test "${status}" = 1
launch-workmux: --config requires a readable file
```

## Missing config file

```scrut
$ prepare_stubs && status=0; env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --config missing-profile.yaml <<< 'Task' 2>&1 || status=$?; test ! -e "${state}/workmux_called" && test "${status}" = 1
launch-workmux: --config file is not a readable regular file: missing-profile.yaml
```

## Directory config

```scrut
$ prepare_stubs && status=0; env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --config . <<< 'Task' 2>&1 || status=$?; test ! -e "${state}/workmux_called" && test "${status}" = 1
launch-workmux: --config file is not a readable regular file: .
```

## Missing agent argument

```scrut
$ prepare_stubs && status=0; env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --agent <<< 'Task' 2>&1 || status=$?; test ! -e "${state}/workmux_called" && test "${status}" = 1
launch-workmux: --agent requires a nonempty name
```

## Empty agent argument

```scrut
$ prepare_stubs && status=0; env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --agent '' <<< 'Task' 2>&1 || status=$?; test ! -e "${state}/workmux_called" && test "${status}" = 1
launch-workmux: --agent requires a nonempty name
```

## Whitespace agent argument

```scrut
$ prepare_stubs && status=0; env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --agent '   ' <<< 'Task' 2>&1 || status=$?; test ! -e "${state}/workmux_called" && test "${status}" = 1
launch-workmux: --agent requires a nonempty name
```

## Agent flag cannot consume another option

```scrut
$ prepare_stubs && status=0; env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --agent --base main <<< 'Task' 2>&1 || status=$?; test ! -e "${state}/workmux_called" && test "${status}" = 1
launch-workmux: --agent requires a nonempty name
```

## Unreadable config file

```scrut
$ prepare_stubs && touch unreadable-profile.yaml && chmod 000 unreadable-profile.yaml && status=0; env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" bash "${LAUNCH_WORKMUX_BIN}" feature/profile --config unreadable-profile.yaml <<< 'Task' 2>&1 || status=$?; chmod 600 unreadable-profile.yaml; test ! -e "${state}/workmux_called" && test "${status}" = 1
launch-workmux: --config file is not a readable regular file: unreadable-profile.yaml
```
