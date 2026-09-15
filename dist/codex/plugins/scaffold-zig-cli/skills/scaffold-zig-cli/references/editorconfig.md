# .editorconfig Template

Create `.editorconfig` in the project root with the following content. If an `.editorconfig` already exists, merge the Zig sections into it rather than overwriting.

No replacements needed.

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

[*.zig]
indent_size = 4

[build.zig]
indent_size = 4

[build.zig.zon]
indent_size = 4

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

## Notes

- Zig's convention is 4-space indentation and `zig fmt` enforces it, so the editor and the formatter agree rather than fighting.
- `[build.zig]` and `[build.zig.zon]` are listed separately from `[*.zig]` because `build.zig.zon` does not match the `*.zig` glob: its extension is `.zon`.
- `[Makefile]` must use tabs. Make treats a recipe line indented with spaces as a syntax error, and an editor silently converting them is a common way to break a working Makefile.
- `[*.md]` keeps trailing whitespace because two trailing spaces are a hard line break in Markdown.
- These sections match `set-up-linters`' own `.editorconfig` guidance, so running that skill afterwards finds nothing to change.
