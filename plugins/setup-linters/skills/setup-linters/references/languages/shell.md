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
# Default shell dialect
shell=bash

# Disable "not following" warnings for sourced files
disable=SC1091
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
- ShellCheck supports `bash`, `sh`, `dash`, and `ksh`. The `shell=bash` default in `.shellcheckrc` can be overridden per-file with a shebang line.
- Common ShellCheck codes: SC2086 (unquoted variable), SC2046 (unquoted command substitution), SC2034 (unused variable).
