---
name: write-bash-scripts
description: >-
  Applies Bash style conventions when creating or editing Bash scripts.
  Use when: (1) creating new Bash scripts, (2) editing existing scripts in /bin/,
  or (3) reviewing Bash code for bugs or style issues.
---

# Bash Style Guide

Apply the Bash conventions from `./references/BASH.md` when creating or editing Bash scripts.

## Key Conventions

Read `./references/BASH.md` for the complete guide. Summary:

### Script Structure

- Shebang: `#!/usr/bin/env bash`
- Strict mode: `set -euo pipefail`
- Main function called at end: `main "$@"`

### Naming

- Functions: `snake_case`
- Local variables: `lower_case`
- Constants: `ALL_CAPS` with `readonly`

### Syntax

- Variable expansion: `${var}` not `$var`, except the argument lists `"$@"` and `"$*"`, which stay unbraced
- Command substitution: `$(...)` not backticks
- Tests: `[[...]]` not `[...]`
- Function syntax: `function name() { }` with both keyword and parentheses

### Quoting

- Always quote variable expansions: `"${var}"`
- Always quote command substitutions: `"$(cmd)"`
- Use arrays for lists, not word splitting
- Guard an array that can be empty: `${array[@]+"${array[@]}"}`

### Local Variables

- Declare with `local`
- Separate declaration from command substitution to preserve exit codes

### Bash 3.2 (macOS)

macOS ships bash 3.2 as `/bin/bash`, which is what `#!/usr/bin/env bash` finds on a stock Mac. Under `set -u` it exits on an empty `"${@}"` or `"${array[@]}"`, and it has no associative arrays, `readarray` or `mapfile`, `${var,,}` or `${var^^}`, or namerefs. See "Bash 3.2 (macOS)" in `./references/BASH.md` for replacements.

## Pull Request Review

When reviewing a pull request, apply `./references/review-checklist.md`: the rules of this guide that a reviewer can check in a diff, ranked as Important, Nits and Do not flag. The same checklist is installed into repositories for automated reviewers, so update it whenever a rule here changes.

## Validation

Whenever possible, validate the script before finishing. Prefer using a project-specific validation script, if available. Common locations include declarations in `package.json` and scripts stored in `bin/`. If those aren't present, `shellcheck` is a commonly available linter for Bash scripts.
