# EditorConfig

Cross-language editor settings that establish consistent formatting baselines. Most editors and IDEs support EditorConfig natively or via plugins. Several tools (e.g., shfmt) also read `.editorconfig` for formatting preferences.

## Install

No installation needed. EditorConfig is a file-based standard supported by most editors.

## Config

Create `.editorconfig` in the project root. Adapt the language-specific sections to match the languages detected in the project.

### Base Template (all projects)

```ini
# EditorConfig
# https://editorconfig.org

root = true

[*]
charset = utf-8
end_of_line = lf
indent_size = 2
indent_style = space
insert_final_newline = true
trim_trailing_whitespace = true
```

### Language-Specific Overrides

Add these sections based on detected languages:

#### Go

```ini
[*.go]
indent_style = tab
```

#### Python

```ini
[*.py]
indent_size = 4
```

#### Rust

```ini
[*.rs]
indent_size = 4
```

#### Ruby

```ini
[*.rb]
indent_size = 2
```

#### Shell

```ini
[*.sh]
indent_size = 2
```

#### YAML

```ini
[*.{yml,yaml}]
indent_size = 2
```

#### Markdown

```ini
[*.md]
trim_trailing_whitespace = false
```

#### Makefile

```ini
[Makefile]
indent_style = tab
```

## Combining Overrides

When generating the final `.editorconfig`, combine the base template with only the overrides relevant to the detected project languages. For example, a Go project with shell scripts would include:

```ini
# EditorConfig
# https://editorconfig.org

root = true

[*]
charset = utf-8
end_of_line = lf
indent_size = 2
indent_style = space
insert_final_newline = true
trim_trailing_whitespace = true

[*.go]
indent_style = tab

[*.sh]
indent_size = 2

[*.{yml,yaml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

## Notes

- `root = true` stops editors from searching parent directories for more `.editorconfig` files.
- Go files must use tabs (gofmt enforces this).
- Python convention is 4-space indentation (PEP 8).
- Markdown has `trim_trailing_whitespace = false` because trailing spaces create line breaks.
- Makefile requires tabs for recipe lines (Make syntax requirement).
- `shfmt` reads `.editorconfig` for indent settings, so the shell section controls both editor and formatter behavior.
