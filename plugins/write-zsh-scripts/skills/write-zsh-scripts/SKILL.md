---
name: write-zsh-scripts
description: >-
  Applies zsh style conventions when creating or editing zsh scripts,
  configurations, and completions.
  Use when: (1) creating new zsh scripts or .zsh files, (2) editing existing
  zsh configurations or plugins, (3) writing zsh completion functions, or
  (4) reviewing zsh code for bugs or style issues.
---

# Zsh Style Guide

Apply the zsh conventions from `./references/ZSH.md` when creating or editing zsh scripts, configurations, and plugins.

## Key Conventions

Read `./references/ZSH.md` for the complete guide. Summary:

### Script Structure

- Shebang: `#!/usr/bin/env zsh`
- Strict mode: `setopt ERR_EXIT NO_UNSET PIPE_FAIL`
- Main function called at end: `main "${@}"`

### Naming

- Functions: `snake_case`
- Local variables: `lower_case`
- Constants: `ALL_CAPS` with `readonly`
- Private/internal: `_underscore_prefix`

### Syntax

- Variable expansion: `${var}` not `$var`
- Command substitution: `$(...)` not backticks
- Tests: `[[ ]]` not `[ ]`
- Function syntax: `function name() { }` with both keyword and parentheses
- Arithmetic: `(( ))` for statements, `$(( ))` for expressions

### Quoting

- Always quote variable expansions: `"${var}"`
- Always quote command substitutions: `"$(cmd)"`
- Use arrays for lists, not word splitting
- Use `"${(@)array}"` to preserve elements in quoted context

### Variables and Scope

- Use `typeset` over `declare`
- Use `local` for all function variables
- Arrays are 1-based (not 0-based like Bash)
- Use `typeset -A` for associative arrays
- Separate `local` declaration from command substitution

### Zsh-Specific Features

- Expansion flags: `${(L)var}`, `${(s:/:)path}`, `${(u)array}`
- Glob qualifiers: `*(.)` for files, `*(/)` for dirs, `*(N)` for null glob
- Extended glob: `setopt EXTENDED_GLOB` for `^`, `~`, `#` patterns
- `always` blocks: `{ ... } always { ... }` for try/finally
- Named traps: `TRAPINT()`, `TRAPZERR()`, `TRAPEXIT()`
- Process substitution: `=(...)` creates a temp file (zsh-only)

## Completions

For zsh completion function conventions, read `./references/completions.md`. Key points:

- Use `_description` for all group descriptions; never pass text directly to `compadd`
- Every `compadd` call must include `"${expl[@]}"`
- Make `curcontext` local in functions using `_arguments -C`
- Register tags before offering matches
- Return zero if matches were added, non-zero otherwise

## Validation

Whenever possible, validate the script before finishing. Prefer using a project-specific validation script, if available. Common locations include declarations in `package.json`, `Makefile` targets, and scripts stored in `bin/`.

If those aren't present:

- `zsh -n path/to/script` for syntax checking
- `shellcheck --shell=bash` for general linting (limited zsh support, may produce false positives on zsh-specific syntax)
