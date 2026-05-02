# .editorconfig Template

Use this template for `.editorconfig`. No replacements needed.

```ini
# EditorConfig
# https://editorconfig.org

root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.go]
indent_style = tab

[*.{yml,yaml}]
indent_size = 2
indent_style = space

[*.md]
indent_size = 2
indent_style = space
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

## Notes

- Go files use tabs (gofmt enforces this)
- YAML and Markdown files use 2-space indentation
- Markdown has `trim_trailing_whitespace = false` because trailing spaces are meaningful in Markdown (they create line breaks)
- Makefile requires tabs for recipe lines (Make syntax requirement)
- `insert_final_newline = true` ensures POSIX-compliant text files
- The `root = true` directive stops editors from looking for parent .editorconfig files
