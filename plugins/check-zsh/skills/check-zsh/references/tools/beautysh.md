# beautysh

## Purpose

Code formatter for bash and zsh scripts. The only tool in this suite with auto-fix capability.

## Commands

Check mode (report formatting issues without modifying):

```bash
beautysh --check-only <file>
```

Fix mode (format in place):

```bash
beautysh <file>
```

## Installation

```bash
pip install beautysh
```

Or via pipx (isolated environment):

```bash
pipx install beautysh
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--indent-size N` | Number of spaces per indent level | 4 |
| `--tab` | Use tabs instead of spaces | Off |
| `--backup` | Create a backup before modifying | Off |
| `--force-function-style STYLE` | Force function style: `fnpar` (name()), `fnonly` (name), `paronly` (()) | None |

## Zsh Support

Good. Handles zsh-specific syntax including:

- `function name()` declarations
- `if [[ ]]` constructs
- `case`/`esac` with zsh glob patterns
- `for` loops with zsh-style iteration
- Anonymous functions `() { ... }`

## Notes

- Formatting is opinionated. Present the indent settings to the user and allow adjustment.
- If the project has an `.editorconfig`, respect its `indent_size` and `indent_style` settings.
- beautysh may have periods of low maintenance activity. If unavailable, `shfmt` is an alternative, though it has more limited zsh support.
- Run `beautysh --check-only` first to preview changes before applying.
