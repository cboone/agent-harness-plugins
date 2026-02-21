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
# Optional checks that align with the write-shell-scripts style guide
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

`shfmt` reads `.editorconfig` for indent style and size. No separate config file is needed when `.editorconfig` is present with a `[*.sh]` section (or when the default `[*]` section applies).

If `.editorconfig` is not present, pass formatting flags directly:

```bash
# 2-space indent, binary ops start of line, space after redirects
shfmt -i 2 -bn -sr -w .
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
- `shfmt` respects `.editorconfig` settings for indent style and size, so it integrates naturally with the EditorConfig setup.
- The optional checks enforce the `write-shell-scripts` style guide: `require-double-brackets` and `require-variable-braces` catch syntax style, `check-extra-masked-returns` catches the `local var=$(cmd)` anti-pattern, and `deprecate-which` enforces `command -v`.
- `external-sources=true` tells ShellCheck to follow `source`/`.` directives for cross-file analysis, rather than silently ignoring them.
- No `shell=bash` is set globally; ShellCheck detects the dialect from each file's shebang line (`#!/usr/bin/env bash`).
