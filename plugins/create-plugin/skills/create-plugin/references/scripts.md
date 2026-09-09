# Scripts Reference

Some plugins include shell scripts under a `scripts/` directory. These scripts are called by hooks or by Claude Code during skill execution.

## File Location

```text
plugins/PLUGIN-NAME/scripts/SCRIPT-NAME
```

Scripts have no file extension (they are executables, not sourced libraries).

## Script Structure

All scripts in this repository follow the Bash conventions from the `write-bash-scripts` plugin. The essential structure:

```bash
#!/usr/bin/env bash
# script-name -- Brief description of purpose
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_NAME

function usage() {
  cat << 'USAGE_TEXT'
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

When a SKILL.md instructs Claude to run a script via the Bash tool, write the path with `${CLAUDE_PLUGIN_ROOT}` and always use `bash` as the command prefix:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/script-name" arg1 arg2
```

**How the path resolves:** `CLAUDE_PLUGIN_ROOT` is *not* a shell environment variable during skill execution; running `echo "${CLAUDE_PLUGIN_ROOT}"` from the Bash tool prints nothing. Instead, Claude Code substitutes it as **prompt text** when the skill loads, replacing it with the installed plugin's absolute, version-correct root before the file reaches the model. The agent therefore sees a ready-to-use absolute path and needs no locating step.

**Never** instruct Claude to find the script by globbing for `**/plugin-name/scripts/script-name`. That shape describes the repository layout, not the installed one: the plugin cache interposes a version directory (`.../plugin-name/1.2.0/scripts/...`), so the glob cannot match the installed copy. It silently matches other copies instead (a marketplace checkout, a `dist/` build artifact, a stale backup), with nothing to choose between them.

**Why the `bash` prefix:** Claude Code's Bash tool permission rules match the whole command text. If the script path were the command itself, the version-specific segment (`.../1.2.0/scripts/...`) would sit at the front of every rule and break it on each release. Prefixing with `bash` keeps the leading token stable, so a rule like `Bash(bash "*/script-name" *)` keeps working across versions.

**Caveat for SKILL.md prose:** the substitution is a global, unconditional text replacement, so a SKILL.md cannot *document* the literal variable; every occurrence is rewritten, including inside fenced code blocks. Use the literal only where substitution is the intent. To describe the variable itself, put that prose in a `references/` file, which is read from disk and left untouched.

Other harnesses differ: Codex CLI substitutes the placeholder only in hook commands, and OpenCode does not substitute it at all. For a script-backed skill that must run there too, add a short fallback telling Claude that an unsubstituted path still begins with `$` rather than `/`, and to locate the script with `**/plugin-name/**/scripts/script-name` (note the `**` between the plugin name and `scripts`, which tolerates the version segment), preferring a match inside the harness's own installed-plugin directory.

## Notes

- Not all plugins need scripts. Skills that only provide guidance (style guides, workflow instructions) typically have no scripts.
- Scripts called by Stop hooks receive JSON on stdin.
- Use `shellcheck` to validate scripts before committing.
