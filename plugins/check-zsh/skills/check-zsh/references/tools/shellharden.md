# shellharden

## Purpose

Suggest safer quoting and syntax. Primarily designed for bash/POSIX sh, but many suggestions apply equally to zsh.

## Commands

Check mode (report issues):

```bash
shellharden --check <file>
```

Suggest mode (show suggested changes):

```bash
shellharden --suggest <file>
```

## Installation

```bash
cargo install shellharden
```

Or via Homebrew:

```bash
brew install shellharden
```

## What Applies to Zsh

- Quoting variable expansions: `"$var"` instead of `$var`
- Quoting command substitutions: `"$(command)"` instead of `$(command)`
- Using `$()` instead of backticks
- Avoiding unquoted glob patterns in variable contexts

## What May Not Apply

- Some bash-specific syntax suggestions
- Glob-related warnings: zsh has different globbing defaults (`NO_NOMATCH` option, `GLOB_SUBST` differences)
- Word splitting warnings: zsh does not split unquoted parameter expansions by default (unlike bash), so some quoting suggestions are less critical in zsh
- Array syntax differences: zsh arrays are 1-indexed; expansion behavior differs

## Notes

- Despite zsh's safer defaults around word splitting, quoting is still a good practice for portability and clarity.
- Use `--suggest` to preview changes before applying them.
- shellharden cannot modify files in place for zsh; use its output as guidance for manual edits.
