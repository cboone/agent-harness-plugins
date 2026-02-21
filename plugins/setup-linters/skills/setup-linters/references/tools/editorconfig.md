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
indent_size = 4
indent_style = tab

[go.mod]
indent_size = 4
indent_style = tab

[go.sum]
indent_size = 4
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

When generating the final `.editorconfig`, combine the base template with only the overrides relevant to the detected project languages. Ruby, Shell, and YAML files use the base defaults (2-space indent), so they do not need separate sections.

For example, a Go project with shell scripts would include:

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
indent_size = 4
indent_style = tab

[go.mod]
indent_size = 4
indent_style = tab

[go.sum]
indent_size = 4
indent_style = tab

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

## Notes

- `root = true` stops editors from searching parent directories for more `.editorconfig` files.
- Go files must use tabs (gofmt enforces this). The `indent_size = 4` on tab-indented sections is a display hint that controls how wide tabs render in editors.
- `go.mod` and `go.sum` use the same tab indentation as Go source files.
- Python convention is 4-space indentation (PEP 8). Rust convention is also 4-space (rustfmt default).
- Ruby, Shell, and YAML all use 2-space indentation, matching the base `[*]` defaults, so they do not need separate sections.
- Markdown has `trim_trailing_whitespace = false` because trailing spaces create line breaks.
- Makefile requires tabs for recipe lines (Make syntax requirement).
- `shfmt` reads `.editorconfig` for indent settings, so the base `[*]` section controls both editor and formatter behavior for shell scripts.
