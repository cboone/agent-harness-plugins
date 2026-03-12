# shfmt

## Purpose

Shell script formatter and parser. Supports bash, POSIX sh, mksh, and has experimental zsh support.

## Commands

Check mode (show diffs without modifying):

```bash
shfmt -d <file>
```

Fix mode (format in place):

```bash
shfmt -w <file>
```

With explicit zsh language flag:

```bash
shfmt -ln zsh -d <file>
```

## Installation

```bash
brew install shfmt
```

Or via Go:

```bash
go install mvdan.cc/sh/v3/cmd/shfmt@latest
```

## Zsh Support

shfmt has experimental zsh support via the `-ln zsh` language flag. It can also auto-detect zsh from shebangs (`#!/bin/zsh`, `#!/usr/bin/env zsh`).

### What Works

- Basic formatting (indentation, spacing, alignment)
- Function definitions
- Control flow (`if`/`then`/`fi`, `for`/`do`/`done`, `case`/`esac`)
- Command substitution `$(...)` and arithmetic `$((...))`)
- Here-documents and here-strings

### Known Limitations

- Some zsh-specific syntax may not parse correctly (e.g., complex parameter expansion flags)
- Anonymous functions `() { ... }` may not be handled
- Advanced glob qualifiers may cause parse errors
- `zstyle` and `autoload` patterns may not format as expected

## Configuration

shfmt reads formatting preferences from `.editorconfig`:

```ini
[*.zsh]
indent_style = space
indent_size = 4
binary_next_line = true
switch_case_indent = true
space_redirects = true
```

## Notes

- When shfmt encounters a zsh construct it cannot parse, it exits with a parse error. This is informational, not a bug in the script.
- If shfmt fails to parse a file, skip it gracefully for that file.
- shfmt's zsh support is evolving. Check for updates periodically.
