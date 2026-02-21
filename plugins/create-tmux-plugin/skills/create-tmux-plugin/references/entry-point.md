# Entry Point Template

Generate `PLUGIN-NAME.tmux` in the project root. This is the file that TPM sources when the plugin loads.

Replace `PLUGIN-NAME` with the actual plugin name (kebab-case). Replace `OPTION-NAME` and `OPTION-DEFAULT` with each configurable option and its default value.

Mark the file executable after creating it: `chmod +x PLUGIN-NAME.tmux`.

**Important:** Do not add `set -euo pipefail`. The entry point runs inside tmux's `run-shell` context, where a non-zero exit silently kills the plugin.

```bash
#!/usr/bin/env bash

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${CURRENT_DIR}/scripts/helpers.sh"

main() {
  local option_value
  option_value="$(get_tmux_option "OPTION-NAME" "OPTION-DEFAULT")"

  # TODO: Use option_value to configure plugin behavior.

  "${CURRENT_DIR}/scripts/PLUGIN-NAME.sh"
}

main
```

## Multiple Options

When the plugin has multiple configurable options, read each one in `main()`:

```bash
main() {
  local enabled
  enabled="$(get_tmux_option "@PLUGIN-NAME-enabled" "on")"

  if [[ "${enabled}" != "on" ]]; then
    return 0
  fi

  local style
  style="$(get_tmux_option "@PLUGIN-NAME-style" "default")"

  "${CURRENT_DIR}/scripts/PLUGIN-NAME.sh" "${style}"
}
```

## Notes

- The `CURRENT_DIR` pattern is standard across all tmux plugins for reliable path resolution.
- Option names use the `@plugin-name-option` convention (prefixed with `@`).
- The entry point delegates to scripts in `scripts/` rather than containing logic directly.
