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
$ state="$(mktemp -d)" && stub_dir="$(mktemp -d)" && cp "${WORKMUX_STUB_BIN}" "${stub_dir}/workmux" && chmod +x "${stub_dir}/workmux" && printf '%s\n' 'Issue body with {{ value }}' | env PATH="${stub_dir}:${PATH}" STUB_STATE="${state}" WORKMUX_LAUNCH_WAIT_SECONDS=1 bash "${CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN}" "feature/issue-265" && sleep 0.1 && prompt_file="$(cat "${state}/prompt_path")" && if [[ -e "${prompt_file}" ]]; then echo "prompt cleanup: no"; else echo "prompt cleanup: yes"; fi
workmux add
branch: feature/issue-265
open-if-exists: true
prompt:
Issue body with {{ "{{" }} value }}
prompt-file-exists: yes
prompt cleanup: yes
```
