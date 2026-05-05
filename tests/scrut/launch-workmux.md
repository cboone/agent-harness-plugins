# Launch workmux

Tests for launcher stdin prompt handling and workmux argument construction.

## Create worktree launcher escapes stdin and passes base

```scrut
$ state="$(mktemp -d)" && stub_dir="$(mktemp -d)" && cp "${WORKMUX_STUB_BIN}" "${stub_dir}/workmux" && chmod +x "${stub_dir}/workmux" && printf '%s\n' 'Prompt with {{ user }} and {% if ok %} and {# note #}' | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_LAUNCH_WORKMUX_BIN}" "feature/stdin-prompt" --base "main" && sleep 0.1 && prompt_file="$(cat "${state}/prompt_path")" && if [[ -e "${prompt_file}" ]]; then echo "prompt cleanup: no"; else echo "prompt cleanup: yes"; fi
workmux add
branch: feature/stdin-prompt
open-if-exists: true
base: main
prompt:
Prompt with {{ "{{" }} user }} and {{ "{%" }} if ok %} and {{ "{#" }} note #}
prompt-file-exists: yes
prompt cleanup: yes
```

## Create worktree from issue launcher reads stdin

```scrut
$ state="$(mktemp -d)" && stub_dir="$(mktemp -d)" && cp "${WORKMUX_STUB_BIN}" "${stub_dir}/workmux" && chmod +x "${stub_dir}/workmux" && printf '%s\n' 'Issue body with {{ value }}' | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 WORKMUX_TERM=tmux-256color WORKMUX_TMUX="/tmp/tmux-501/projects,123,%4" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN}" "feature/issue-265" && sleep 0.1 && prompt_file="$(cat "${state}/prompt_path")" && if [[ -e "${prompt_file}" ]]; then echo "prompt cleanup: no"; else echo "prompt cleanup: yes"; fi
workmux add
branch: feature/issue-265
open-if-exists: true
term: tmux-256color
tmux: /tmp/tmux-501/projects,123,%4
prompt:
Issue body with {{ "{{" }} value }}
prompt-file-exists: yes
prompt cleanup: yes
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
