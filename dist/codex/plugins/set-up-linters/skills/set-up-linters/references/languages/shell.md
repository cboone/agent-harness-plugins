# Shell

## Tools

- **ShellCheck**: Static analysis tool for shell scripts. Catches common bugs, pitfalls, and portability issues.
- **shfmt**: Shell script formatter. Supports bash, posix, and mksh dialects.

## Install

```bash
# Homebrew (recommended)
brew install shellcheck shfmt
```

## Config

### .shellcheckrc

Create `.shellcheckrc` in the project root:

```ini
# Optional checks that align with the write-bash-scripts style guide
enable=add-default-case
enable=avoid-negated-conditions
enable=avoid-nullary-conditions
enable=check-extra-masked-returns
enable=check-set-e-suppressed
enable=check-unassigned-uppercase
enable=deprecate-which
enable=quote-safe-variables
enable=require-double-brackets
enable=require-variable-braces
enable=useless-use-of-cat

# Follow source directives for cross-file analysis
external-sources=true
```

### shfmt

`shfmt` reads `.editorconfig` for all formatting preferences. No separate config file is needed. Add these properties to the `[*]` section (they are shfmt-specific and ignored by other tools):

```ini
# shfmt formatting
binary_next_line = true
space_redirects = true
switch_case_indent = true
```

| `.editorconfig` property | CLI flag | Effect                                         |
| ------------------------ | -------- | ---------------------------------------------- |
| `indent_size`            | `-i`     | Number of spaces for indentation               |
| `indent_style`           | `-i 0`   | `tab` uses tabs (flag value 0 means tabs)      |
| `binary_next_line`       | `-bn`    | Place binary operators at start of next line   |
| `space_redirects`        | `-sr`    | Add space after redirect operators (`> file`)  |
| `switch_case_indent`     | `-ci`    | Indent `case` patterns one level inside `case` |

The `switch_case_indent` property aligns with the write-bash-scripts style guide, which shows case patterns indented under `case`.

If `.editorconfig` is not present, pass formatting flags directly:

```bash
# 2-space indent, binary ops start of line, space after redirects, case indent
shfmt -i 2 -bn -sr -ci -w .
```

## Commands

```bash
# ShellCheck (lint)
shellcheck scripts/*.sh bin/*

# shfmt (check)
shfmt -d .

# shfmt (format in place)
shfmt -w .
```

## Makefile Targets

```makefile
.PHONY: lint fmt

lint: ## Lint shell scripts
	shellcheck scripts/*.sh bin/*

fmt: ## Format shell scripts
	shfmt -w .
```

Adjust the file patterns (`scripts/*.sh`, `bin/*`) to match the project's shell script locations.

## Notes

- ShellCheck has no auto-fix mode. All issues must be resolved manually (or by reading the SC code and applying the recommended fix).
- `shfmt` reads all its formatting preferences from `.editorconfig` (indent style, indent size, and the extended properties documented above), so it integrates naturally with the EditorConfig setup.
- The optional checks enforce the `write-bash-scripts` style guide: `require-double-brackets` and `require-variable-braces` catch syntax style, `check-extra-masked-returns` catches the `local var=$(cmd)` anti-pattern, and `deprecate-which` enforces `command -v`.
- `external-sources=true` tells ShellCheck to follow `source`/`.` directives for cross-file analysis, rather than silently ignoring them.
- No `shell=bash` is set globally; ShellCheck detects the dialect from each file's shebang line (`#!/usr/bin/env bash`).
