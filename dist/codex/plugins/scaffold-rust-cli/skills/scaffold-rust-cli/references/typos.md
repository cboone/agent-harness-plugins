# typos.toml Template

Create `typos.toml` in the project root with the following content.

Replace `PROJECT-NAME` with the project name (kebab-case names often trigger false positives).

```toml
[default.extend-words]
PROJECT-NAME = "PROJECT-NAME"
```

## Notes

- `typos` is a fast source code spell checker written in Rust.
- The `[default.extend-words]` section allows project-specific words that would otherwise be flagged as typos. The project name is added by default since kebab-case names are commonly flagged.
- Add additional words as needed when `typos` flags legitimate terms in your codebase.
- To exclude entire files or directories, add a `[files]` section with `extend-exclude`:

```toml
[files]
extend-exclude = ["CHANGELOG.md"]
```
