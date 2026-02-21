# Helpers Template

Generate `scripts/helpers.sh`. This file is sourced (not executed) by the entry point and other scripts, so it does not need a shebang or executable permission.

This file is identical across all tmux plugins. Use it verbatim.

```bash
get_tmux_option() {
  local option="$1"
  local default_value="$2"
  local option_value

  option_value="$(tmux show-option -gqv "${option}")"

  if [[ -n "${option_value}" ]]; then
    echo "${option_value}"
  else
    echo "${default_value}"
  fi
}
```

## Notes

- `tmux show-option -gqv` reads a global (`-g`) option quietly (`-q`) and returns only the value (`-v`).
- The function echoes the default when the option is unset or empty.
- This file should not contain `set -euo pipefail` because it is sourced into scripts that run in tmux's `run-shell` context.
- Additional helper functions can be added here as the plugin grows (e.g., logging, color utilities).
