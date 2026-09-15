# typos.toml Template

Create `typos.toml` in the project root with the following content.

Replace `PACKAGE-NAME` with the underscored package name (the same value `build.zig.zon` uses for `.name`).

```toml
[default.extend-identifiers]
PACKAGE-NAME = "PACKAGE-NAME"
```

## Notes

- `typos` is a fast source code spell checker.
- **`extend-identifiers`, not `extend-words`.** `typos` splits an identifier into words before judging it, so a word entry for the project name never matches: the checker is comparing the pieces, not the whole. Verified against `typos-cli` 1.50.1 with a project named `teh-tool`, where `teh` is in the dictionary:

  | Config                                      | `pub const teh_tool = 1;` |
  | ------------------------------------------- | ------------------------- |
  | none                                        | `teh` should be `the`     |
  | `[default.extend-words] teh-tool = ...`     | `teh` should be `the`     |
  | `[default.extend-identifiers] teh_tool = …` | clean                     |

  The word entry looks right, changes nothing, and the run still reports success. `plugins/plant-defects/skills/plant-defects/references/vacuous-passes.md` records the same failure shape.

- The identifier entry covers the package name where it appears in code, including `.name` in `build.zig.zon` and the module name in `build.zig`. It does **not** cover the hyphenated project name in prose: `teh-tool` in a comment or a usage string splits into `teh` and `tool`, and only a word entry suppresses those. Add one per flagged segment, when `typos` flags one:

  ```toml
  [default.extend-words]
  teh = "teh"
  ```

  Most project names need nothing here, because most segments are ordinary words. Add an entry after seeing the report, rather than guessing.

- Add further entries as `typos` flags legitimate terms. Zig accumulates a long list: `comptime`, `zon`, `aarch64` and target triples such as `x86_64-macos` are all common.
- To exclude entire files or directories, add a `[files]` section with `extend-exclude`:

  ```toml
  [files]
  extend-exclude = ["CHANGELOG.md"]
  ```
