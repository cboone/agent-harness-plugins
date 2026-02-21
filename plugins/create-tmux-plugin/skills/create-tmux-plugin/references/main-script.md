# Main Script Template

Generate `scripts/PLUGIN-NAME.sh`. This is the primary script that implements the plugin's behavior.

Replace `PLUGIN-NAME` with the actual plugin name (kebab-case).

Mark the file executable after creating it: `chmod +x scripts/PLUGIN-NAME.sh`.

**Important:** Do not add `set -euo pipefail`. This script runs inside tmux's `run-shell` context, where a non-zero exit silently kills the plugin.

```bash
#!/usr/bin/env bash

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${CURRENT_DIR}/helpers.sh"

main() {
  # TODO: Implement plugin behavior.
  #
  # Common patterns:
  #
  # Read a tmux option:
  #   local value
  #   value="$(get_tmux_option "@PLUGIN-NAME-option" "default")"
  #
  # Set a tmux option:
  #   tmux set-option -g "@PLUGIN-NAME-result" "value"
  #
  # Update the status line:
  #   local status_right
  #   status_right="$(tmux show-option -gqv "status-right")"
  #   tmux set-option -g "status-right" "${status_right} #(${CURRENT_DIR}/status.sh)"
  #
  # Bind a key:
  #   tmux bind-key T run-shell "${CURRENT_DIR}/action.sh"
  :
}

main "$@"
```

## Notes

- Source `helpers.sh` from `CURRENT_DIR` (relative to the script's own directory, not the project root).
- The `:` (no-op) in the TODO body prevents the function from being empty, which would cause a syntax error.
- Pass `"$@"` to `main` so the entry point can forward arguments (e.g., style or mode flags).
- Additional scripts can be added alongside this one in `scripts/` for modular functionality.
