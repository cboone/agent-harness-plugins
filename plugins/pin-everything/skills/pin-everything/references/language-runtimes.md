# Pinning Language Runtimes via Version Files

Per-language recipes for replacing inline language-version pins in CI with version-file refs, and for populating a missing version file with the current LTS or stable release.

## Why Version Files

Inline pins like `node-version: "20"` in a workflow file create a second source of truth: the version that CI runs is stored separately from the version that local dev uses. They drift. Version-file refs (`node-version-file: ".tool-versions"`) point CI at the same file the developer's `asdf`, `mise`, `nodenv`, or similar tool already reads, so local and CI agree by construction.

## Per-Language Table

Version-file selection is **prefer the file that already has the language's entry, not just any file that exists**. A bare `.tool-versions` is only useful here if it actually contains a line for the language being configured (e.g., `nodejs 22.10.0`); pointing CI at a `.tool-versions` that only lists `python` or `ruby` will break setup. The principle is: reuse the file local tooling already reads for *this* language (e.g., `.nvmrc` for `nvm`, `.ruby-version` for `rbenv`/`chruby`) so CI and local dev share one source of truth. Only fall back to creating `.tool-versions` when no language-specific file is present.

| Language | Action(s)                                                                         | Version-file input (in priority order)                                                                                                                                                                              | File format                                                                                | If no file is present                        |
| -------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------- |
| Node.js  | `actions/setup-node`                                                              | `node-version-file: ".tool-versions"` only if `.tool-versions` contains a `nodejs` line; else `.nvmrc`; else `.node-version`; else create `.tool-versions` (or add a `nodejs` line to an existing one)              | `.tool-versions`: `nodejs <version>` (one tool per line); `.nvmrc` / `.node-version`: bare | Create `.tool-versions` with current LTS     |
| Ruby     | `ruby/setup-ruby`                                                                 | `ruby-version-file: ".tool-versions"` only if `.tool-versions` contains a `ruby` line; else `.ruby-version`; else `Gemfile` (if it has a `ruby` directive); else create `.tool-versions` (or add a `ruby` line)     | `.tool-versions`: `ruby <version>`; `.ruby-version`: bare                                  | Create `.tool-versions` with current stable  |
| Go       | `actions/setup-go`                                                                | `go-version-file: "go.mod"`                                                                                                                                                                                         | `go X.Y` directive                                                                         | Always present in Go projects                |
| Python   | `actions/setup-python` / `astral-sh/setup-uv`                                     | uv reads `pyproject.toml` `requires-python` directly. For `actions/setup-python`: `python-version-file: ".python-version"` if present; else `pyproject.toml` if it declares `requires-python`; else create `.python-version` | `.python-version`: `X.Y.Z` (one per line); `pyproject.toml`: `requires-python = ">=X.Y"`   | Create `.python-version` with current stable |
| Rust     | `dtolnay/rust-toolchain`                                                          | _no version-file input_; `rust-toolchain.toml` is read by cargo directly                                                                                                                                            | `[toolchain]\nchannel = "stable"`                                                          | Create or pass `toolchain:` input            |
| Zig      | `mlugg/setup-zig` (action-direct) or `cboone/gh-actions/.../zig-ci.yml` (wrapper) | None for `mlugg/setup-zig` (reads `build.zig.zon` by default); `zig-version-file: build.zig.zon` on the wrapper                                                                                                     | `.{ .minimum_zig_version = "X.Y.Z" }` in `build.zig.zon`                                   | Always present in Zig projects               |

## Lookup Commands

Each language exposes its current LTS / stable via a queryable upstream. Use these to populate a missing version file.

### Node.js (LTS)

```bash
curl -fsSL https://nodejs.org/dist/index.json \
  | jq -r 'first(.[] | select(.lts != false)) | .version' \
  | sed 's/^v//'
```

### Ruby (stable)

```bash
gh api repos/ruby/ruby/releases \
  --jq 'first(.[] | select(.prerelease == false)) | .tag_name' \
  | sed 's/^v//; s/_/./g'
```

`ruby/ruby` tags use underscores (`v3_4_2`); the `sed` normalization converts to the version-file format. The `select(.prerelease == false)` filter prevents preview / rc tags from being chosen as "stable".

### Go (the `go.mod` directive)

`go.mod`'s `go X.Y` directive is the version of record; populate it via `go mod edit -go X.Y`. The current Go release series is announced at `https://go.dev/dl/?mode=json`:

```bash
curl -fsSL 'https://go.dev/dl/?mode=json' \
  | jq -r '.[0].version' \
  | sed 's/^go//'
```

### Python (stable)

```bash
gh api repos/python/cpython/releases --jq \
  '[.[] | select(.prerelease == false and (.tag_name | startswith("v3.")))][0].tag_name' \
  | sed 's/^v//'
```

### Rust (stable)

The `dtolnay/rust-toolchain@stable` action does the lookup at runtime; for a `rust-toolchain.toml` file the literal channel name `"stable"` is the conventional pin. If you want a specific version, query:

```bash
curl -fsSL https://forge.rust-lang.org/infra/channel-layout.html | head # informational
gh api repos/rust-lang/rust/releases --jq '.[0].tag_name'
```

### Zig (latest released)

```bash
gh api repos/ziglang/zig/releases --jq '.[0].tag_name'
```

For pre-release tracking (master), set `.minimum_zig_version = "0.X.Y-dev.NNNN+abcdef"` to the current master snapshot from `https://ziglang.org/download/index.json` — the unstable channel changes daily.

## Special Cases

### Zig Version-File Inputs

The pattern depends on which surface is in use:

1. **Action-direct (`mlugg/setup-zig`).** Pass no version input. The action reads `.minimum_zig_version` from `build.zig.zon` automatically when no `version` is specified.
2. **Reusable workflow (`cboone/gh-actions/.../zig-ci.yml`, v2.2.0+).** Pass `zig-version-file: build.zig.zon`. The wrapper forwards the file to `mlugg/setup-zig` so `.minimum_zig_version` is the single source of truth.
3. **Last resort.** If neither surface fits, mirror the value inline: read `.minimum_zig_version` and pass it as `zig-version: "X.Y.Z"` (or `version:` for action-direct). This restores the inline-pin drift problem the version-file approach exists to avoid; only do it if options 1 and 2 aren't available.

### Ruby Version-File Selection

`ruby/setup-ruby` accepts several version-file inputs; pick the most expressive one available, but only after confirming the file actually carries a Ruby pin:

| Condition                                                 | Input                                 |
| --------------------------------------------------------- | ------------------------------------- |
| `.tool-versions` exists AND contains a `ruby` line        | `ruby-version-file: ".tool-versions"` |
| `.ruby-version` exists                                    | `ruby-version-file: ".ruby-version"`  |
| `Gemfile` exists AND has a `ruby` directive               | `ruby-version-file: "Gemfile"`        |

A `.tool-versions` whose lines are all non-Ruby (e.g., `nodejs 22.10.0` only) does not satisfy the first row — point at `.ruby-version` or `Gemfile` instead, or add a `ruby` line to the existing `.tool-versions`. If none of the three conditions apply, create `.tool-versions` with `ruby <stable>` (or add a `ruby` line to an existing `.tool-versions`).

### Python With `pyproject.toml`

`astral-sh/setup-uv` reads `pyproject.toml`'s `[project] requires-python` automatically — no `python-version-file:` input is needed when uv handles the install. For `actions/setup-python` workflows that still want a version-file ref, create `.python-version` with the explicit `X.Y.Z`.
