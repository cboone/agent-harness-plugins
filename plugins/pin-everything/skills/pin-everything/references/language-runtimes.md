# Pinning Language Runtimes via Version Files

Per-language recipes for replacing inline language-version pins in CI with version-file refs, and for populating a missing version file with the current LTS or stable release.

## Why Version Files

Inline pins like `node-version: "20"` in a workflow file create a second source of truth: the version that CI runs is stored separately from the version that local dev uses. They drift. Version-file refs (`node-version-file: ".tool-versions"`) point CI at the same file the developer's `asdf`, `mise`, `nodenv`, or similar tool already reads, so local and CI agree by construction.

## Per-Language Table

| Language | Action(s)                                                                            | Version-file input                                                                                   | File format                                              | If file is missing                                   |
| -------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------- |
| Node.js  | `actions/setup-node`                                                                 | `node-version-file: ".tool-versions"`                                                                | `nodejs <version>` (one per line)                        | Create with current LTS                              |
| Ruby     | `ruby/setup-ruby`                                                                    | `ruby-version-file: ".tool-versions"`                                                                | `ruby <version>`                                         | Create with current stable                           |
| Go       | `actions/setup-go`                                                                   | `go-version-file: "go.mod"`                                                                          | `go X.Y` directive                                       | Always present in Go projects                        |
| Python   | `actions/setup-python` / `astral-sh/setup-uv`                                        | `python-version-file: ".python-version"` (setup-python); uv reads `pyproject.toml` `requires-python` | `X.Y.Z` (one per line)                                   | Create with current stable; or set `requires-python` |
| Rust     | `dtolnay/rust-toolchain`                                                             | _no version-file input_; `rust-toolchain.toml` is read by cargo directly                             | `[toolchain]\nchannel = "stable"`                        | Create or pass `toolchain:` input                    |
| Zig      | `mlugg/setup-zig` (action-direct) or `cboone/gh-actions/.../setup-zig.yml` (wrapper) | `version-file: build.zig.zon` or `version: ""` (passthrough)                                         | `.{ .minimum_zig_version = "X.Y.Z" }` in `build.zig.zon` | Always present in Zig projects                       |

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
gh api repos/ruby/ruby/releases --jq '.[0].tag_name' \
  | sed 's/^v//; s/_/./g'
```

`ruby/ruby` tags use underscores (`v3_4_2`); the `sed` normalization converts to the version-file format.

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

### Zig Without a Version-File Input

Most third-party Zig setup actions don't expose a `version-file:` input. Two workarounds:

1. **Pass `version: ""`.** The action interprets the empty string as "use the project's stated minimum" and falls through to `.minimum_zig_version` in `build.zig.zon`. Works with `mlugg/setup-zig` and the `cboone/gh-actions/setup-zig.yml` wrapper.
2. **Mirror the value inline.** Read `.minimum_zig_version` and pass it as `version: "X.Y.Z"`. This restores the inline-pin drift problem the version-file approach exists to avoid; only do it if option 1 isn't available.

The `cboone/gh-actions` wrapper exposes a real `version-file: "build.zig.zon"` input ([gh-actions#41](https://github.com/cboone/gh-actions/issues/41) tracks this); when that lands, prefer the wrapper.

### Ruby Without `.tool-versions`

`ruby/setup-ruby` accepts several version-file inputs; pick the most expressive one available:

| File present                    | Input                                 |
| ------------------------------- | ------------------------------------- |
| `.tool-versions`                | `ruby-version-file: ".tool-versions"` |
| `.ruby-version`                 | `ruby-version-file: ".ruby-version"`  |
| `Gemfile` with `ruby` directive | `ruby-version-file: "Gemfile"`        |

If none are present, create `.tool-versions` with `ruby <stable>`.

### Python With `pyproject.toml`

`astral-sh/setup-uv` reads `pyproject.toml`'s `[project] requires-python` automatically — no `python-version-file:` input is needed when uv handles the install. For `actions/setup-python` workflows that still want a version-file ref, create `.python-version` with the explicit `X.Y.Z`.
