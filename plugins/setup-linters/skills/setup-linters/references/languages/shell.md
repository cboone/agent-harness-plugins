# Shell

## Tools

- **ShellCheck**: Static analysis tool for shell scripts. Catches common bugs, pitfalls, and portability issues.
- **shfmt**: Shell script formatter. Supports bash, posix, and mksh dialects.
- **prettier-plugin-sh**: Prettier plugin for shell scripts. Alternative to shfmt for projects already using Prettier.

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
- Do NOT use shfmt and `prettier-plugin-sh` together in the same project. They produce conflicting output on heredoc spacing, redirection operators, case indentation, and pipe continuation. Choose one or the other.

## prettier-plugin-sh (Alternative to shfmt)

If the project already uses Prettier, `prettier-plugin-sh` can replace shfmt for shell formatting. It integrates shell formatting into the existing Prettier workflow.

### When to Choose Which

- **shfmt**: Use when the project does not use Prettier, or when you want a standalone shell formatter with no Node.js dependency.
- **prettier-plugin-sh**: Use when the project already uses Prettier for other file types. Consolidates formatting into a single tool and config.

### Install

```bash
# npm
npm install -D prettier-plugin-sh

# yarn
yarn add -D prettier-plugin-sh
```

### Config

Add shell overrides to `.prettierrc.json` (or equivalent):

```json
{
  "overrides": [
    {
      "files": ["**/*.sh", "scripts/*", "bin/*"],
      "options": {
        "parser": "sh",
        "indent": 2,
        "binaryNextLine": true,
        "spaceRedirects": true,
        "switchCaseIndent": true
      }
    }
  ]
}
```

Prettier auto-discovers the plugin from `devDependencies`, so no `plugins` array is needed.

### WARNING: Do Not Use Both

Do NOT configure both shfmt and prettier-plugin-sh in the same project. They produce conflicting formatting output on heredoc spacing, redirection operators, case-arm indentation, and pipe continuation. This creates a "ping-pong" effect where running one undoes the other's changes.

If `prettier-plugin-sh` is in the project's dependencies, do not add shfmt. If shfmt is already configured, do not add `prettier-plugin-sh`.
