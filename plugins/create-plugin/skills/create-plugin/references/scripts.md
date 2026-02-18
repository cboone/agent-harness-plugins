# Scripts Reference

Some plugins include shell scripts under a `scripts/` directory. These scripts are called by hooks or by Claude Code during skill execution.

## File Location

```text
plugins/PLUGIN-NAME/scripts/SCRIPT-NAME
```

Scripts have no file extension (they are executables, not sourced libraries).

## Script Structure

All scripts in this repository follow the Bash conventions from the `write-shell-scripts` plugin. The essential structure:

```bash
#!/usr/bin/env bash
# script-name -- Brief description of purpose
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_NAME

function usage() {
  cat <<'USAGE_TEXT'
Usage: script-name <command> [options]

Description of what the script does.

Commands:
  command1    Description
  command2    Description

Options:
  -h, --help  Show this help
USAGE_TEXT
}

function do_command1() {
  # implementation
}

function main() {
  if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
  fi

  case "${1:-}" in
    command1)
      shift
      do_command1 "$@"
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"
```

## Key Conventions

### Header

- Shebang: `#!/usr/bin/env bash`
- Comment with script name, dash separator, and brief description
- `set -euo pipefail` immediately after header comments

### Constants

- `SCRIPT_NAME` is captured and made `readonly` at the top
- Other constants use `ALL_CAPS` with `readonly`

### Functions

- Use `function name() { }` syntax (both keyword and parentheses)
- Function names use `snake_case`
- Prefix implementation functions with `do_` (e.g., `do_fetch`, `do_resolve`)
- Declare local variables with `local`
- Separate `local` declaration from command substitution to preserve exit codes

### Main Function

- Always define a `main` function
- Handle `-h`/`--help` first
- Use `case` for command dispatch
- Call `main "$@"` at the end of the file

### Error Handling

- Use a `die` function for error exits:

  ```bash
  function die() {
    echo "Error: ${1}" >&2
    exit "${2:-1}"
  }
  ```

- Send error messages to stderr
- Check dependencies before running commands

### Quoting

- Always quote variable expansions: `"${var}"`
- Always quote command substitutions: `"$(cmd)"`
- Use `${var}` not `$var`

## Permissions

Scripts must be executable. After creating a script:

```bash
chmod +x plugins/PLUGIN-NAME/scripts/SCRIPT-NAME
```

## Hook Integration

When a script is called from `hooks.json`, use `${CLAUDE_PLUGIN_ROOT}` to reference it:

```json
{
  "command": "${CLAUDE_PLUGIN_ROOT}/scripts/script-name arg1",
  "type": "command"
}
```

Hook commands are executed by the hooks system directly, so the script path can be used as the command.

## Skill Integration

When a SKILL.md instructs Claude to run a script via the Bash tool, always use `bash` as the command prefix:

```bash
bash "/absolute/path/to/scripts/script-name" arg1 arg2
```

**Why:** Claude Code's Bash tool permission allowlist matches on the command token (the first word of the command). If the script path is used directly, the resolved absolute path — including version-specific segments like `.../1.2.0/scripts/...` — becomes the command token. This breaks allowlist entries whenever the plugin version changes. Using `bash` as the prefix makes the command token stable: users add `Bash(bash:*)` once and it covers all script invocations permanently.

In SKILL.md files, instruct Claude to:

1. Locate the script path at the start of the session (e.g., by globbing for `**/plugin-name/scripts/script-name`)
1. Invoke it with `bash` followed by the **quoted absolute path** and arguments

## Notes

- Not all plugins need scripts. Skills that only provide guidance (style guides, workflow instructions) typically have no scripts.
- Scripts called by Stop hooks receive JSON on stdin.
- Use `shellcheck` to validate scripts before committing.
