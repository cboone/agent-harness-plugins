# Pinning Language Runtimes via Version Files

Per-language recipes for replacing inline language-version pins in CI with version-file refs, and for populating a missing version file with the current LTS or stable release.

## Why Version Files

Inline pins like `node-version: "20"` in a workflow file create a second source of truth: the version that CI runs is stored separately from the version that local dev uses. They drift. Version-file refs (`node-version-file: ".tool-versions"`) point CI at the same file the developer's `asdf`, `mise`, `nodenv`, or similar tool already reads, so local and CI agree by construction.

## Per-Language Table

Version-file selection is **prefer the file that already has the language's entry, not just any file that exists**. A bare `.tool-versions` is only useful here if it actually contains a line for the language being configured (e.g., `nodejs 22.10.0`); pointing CI at a `.tool-versions` that only lists `python` or `ruby` will break setup. The principle is: reuse the file local tooling already reads for *this* language (e.g., `.nvmrc` for `nvm`, `.ruby-version` for `rbenv`/`chruby`) so CI and local dev share one source of truth. Only fall back to creating `.tool-versions` when no language-specific file is present.

**Normalize the file's value to an exact `X.Y.Z` before treating the version-file ref as a pin.** The same files frequently carry moving forms that look pinned but aren't: `.nvmrc` accepts aliases like `lts/*`, `lts/iron`, `node`, and `latest`; `.ruby-version`, `.python-version`, and `.tool-versions` entries are often major-only (`3.4`) or truncated to major+minor (`3.13`). CI that reads any of those values resolves them at install time, which means each fresh runner can pick a different patch release. After selecting (or creating) the file, inspect its current contents and, if the value is anything other than an exact `X.Y.Z`, rewrite it to the matching exact release **within the existing release line**: the latest patch in the same major for Node.js (a `.nvmrc = 23` repo stays on the `23.x` line), and the latest patch in the same X.Y feature line for Ruby and Python (a `.ruby-version = 3.4` repo stays on `3.4.z`). Use the in-series lookup commands in [Lookup Commands](#lookup-commands) below for that case. Only fall back to the absolute LTS / stable lookup when no version file existed before this pass and a fresh release line is being chosen, since that path will move the project onto the current global LTS / stable major rather than preserving the existing one. Only then has the runtime actually been pinned.

| Language | Action(s)                                                                             | Version-file input (in priority order)                                                                                                                                                                          | File format                                                                                | If no file is present                                                                                                      |
| -------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Node.js  | `actions/setup-node`                                                                  | `node-version-file: ".tool-versions"` only if `.tool-versions` contains a `nodejs` line; else `.nvmrc`; else `.node-version`; else create `.tool-versions` (or add a `nodejs` line to an existing one)          | `.tool-versions`: `nodejs <version>` (one tool per line); `.nvmrc` / `.node-version`: bare | Create `.tool-versions` with current LTS                                                                                   |
| Ruby     | `ruby/setup-ruby`                                                                     | `ruby-version-file: ".tool-versions"` only if `.tool-versions` contains a `ruby` line; else `.ruby-version`; else `Gemfile` (if it has a `ruby` directive); else create `.tool-versions` (or add a `ruby` line) | `.tool-versions`: `ruby <version>`; `.ruby-version`: bare                                  | Create `.tool-versions` with current stable                                                                                |
| Go       | `actions/setup-go`                                                                    | `go-version-file: "go.mod"`                                                                                                                                                                                     | `go X.Y.Z` directive (exact patch; the bare `go X.Y` form is a floor, not a pin)           | Always present in Go projects                                                                                              |
| Python   | `actions/setup-python` / `astral-sh/setup-uv`                                         | `astral-sh/setup-uv`: no input (reads `pyproject.toml` `requires-python` directly). `actions/setup-python`: `python-version-file: ".python-version"` if present; else create `.python-version`                  | `.python-version`: `X.Y.Z` (one per line); `pyproject.toml`: `requires-python = ">=X.Y"`   | `setup-uv`: ensure `pyproject.toml` `requires-python` is set; `setup-python`: create `.python-version` with current stable |
| Rust     | `dtolnay/rust-toolchain`                                                              | _no version-file input_; `rust-toolchain.toml` is read by cargo directly                                                                                                                                        | `[toolchain]\nchannel = "stable"`                                                          | Create or pass `toolchain:` input                                                                                          |
| Zig      | `mlugg/setup-zig` (action-direct) or `cboone/gh-actions/.../run-zig-ci.yml` (wrapper) | None for `mlugg/setup-zig` (reads `build.zig.zon` by default); `zig-version-file: build.zig.zon` on the wrapper                                                                                                 | `.{ .minimum_zig_version = "X.Y.Z" }` in `build.zig.zon`                                   | Always present in Zig projects                                                                                             |

## Lookup Commands

Each language exposes its current LTS / stable via a queryable upstream. Two shapes of lookup are useful here:

- **In-series** (use for normalizing an existing partial pin like `.nvmrc = 23` or `.ruby-version = 3.4`): pick the latest patch within the major (Node.js) or X.Y feature line (Ruby, Python) that the project is already on. This preserves the release line.
- **Create-from-scratch** (use only when no prior version file exists): pick the current global LTS / stable. This selects a release line.

Pick the in-series form by default during a pinning pass; only fall back to the create-from-scratch form when there is no existing pin to preserve.

### Node.js

In-series (preserve an existing major like `23`):

```bash
MAJOR=23  # use the major found in the existing version file
curl -fsSL https://nodejs.org/dist/index.json \
  | jq -r --arg prefix "v${MAJOR}." \
    'first(.[] | select(.version | startswith($prefix))) | .version' \
  | sed 's/^v//'
```

Create-from-scratch (current LTS):

```bash
curl -fsSL https://nodejs.org/dist/index.json \
  | jq -r 'first(.[] | select(.lts != false)) | .version' \
  | sed 's/^v//'
```

### Ruby

In-series (preserve an existing X.Y series like `3.4`):

```bash
SERIES=3.4  # use the X.Y series found in the existing version file
gh api repos/ruby/ruby/releases --paginate \
  --jq '.[] | select(.prerelease == false) | .tag_name' \
  | sed 's/^v//; s/_/./g' \
  | grep -E "^${SERIES//./\\.}\.[0-9]+$" \
  | jq -R -s -r 'split("\n") | map(select(length > 0)) | sort_by(split(".") | map(tonumber? // 0)) | last // empty'
```

Create-from-scratch (current stable):

```bash
gh api repos/ruby/ruby/releases \
  --jq 'first(.[] | select(.prerelease == false)) | .tag_name' \
  | sed 's/^v//; s/_/./g'
```

`ruby/ruby` tags use underscores (`v3_4_2`); the `sed` normalization converts to the version-file format. The `select(.prerelease == false)` filter prevents preview / rc tags from being chosen as "stable". The `jq` slurp picks the highest version-aware match without relying on GNU `sort -V`, which BSD `sort` on stock macOS does not implement; `jq` is already a dependency, so this stays portable across Linux runners and macOS dev machines.

### Go (the `go.mod` directive)

`go.mod`'s `go` directive is the version of record. Two forms are syntactically valid, and only one of them actually pins the runtime:

- `go X.Y` is a **module-spec floor**: `actions/setup-go` resolves it to the latest patch in the X.Y series at install time, so successive CI runs can pick different patches as upstream cuts new releases. The bundled `bin/version-audit` template silently skips this form because there is no fixed value to compare against.
- `go X.Y.Z` is an **exact pin**: `actions/setup-go` installs that exact patch and the audit treats it as auditable drift against the latest patch in the same X.Y line.

Populate the file with the exact form via `go mod edit -go X.Y.Z` (Go 1.21+ accepts the three-segment value). The current Go release series is announced at `https://go.dev/dl/?mode=json`, which already returns an exact `X.Y.Z`:

```bash
curl -fsSL 'https://go.dev/dl/?mode=json' \
  | jq -r '.[0].version' \
  | sed 's/^go//'
```

To preserve an existing X.Y series instead of jumping to the newest one, filter for that prefix:

```bash
SERIES=1.23  # use the X.Y series found in the existing go.mod directive
curl -fsSL 'https://go.dev/dl/?mode=json&include=all' \
  | jq -r --arg prefix "go${SERIES}." \
    'first(.[] | select(.version | startswith($prefix))) | .version' \
  | sed 's/^go//'
```

### Python

In-series (preserve an existing X.Y series like `3.13`):

```bash
SERIES=3.13  # use the X.Y series found in the existing version file
gh api repos/python/cpython/releases --paginate \
  --jq '.[] | select(.prerelease == false) | .tag_name' \
  | sed 's/^v//' \
  | grep -E "^${SERIES//./\\.}\.[0-9]+$" \
  | jq -R -s -r 'split("\n") | map(select(length > 0)) | sort_by(split(".") | map(tonumber? // 0)) | last // empty'
```

The trailing `jq` slurp avoids GNU `sort -V`, which BSD `sort` on stock macOS does not implement. `jq` is already required, so this works on both Linux runners and macOS dev machines without an extra coreutils dependency.

Create-from-scratch (current stable):

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
2. **Reusable workflow (`cboone/gh-actions/.../run-zig-ci.yml`, v2.2.0+).** Pass `zig-version-file: build.zig.zon`. The wrapper forwards the file to `mlugg/setup-zig` so `.minimum_zig_version` is the single source of truth.
3. **Last resort.** If neither surface fits, mirror the value inline: read `.minimum_zig_version` and pass it as `zig-version: "X.Y.Z"` (or `version:` for action-direct). This restores the inline-pin drift problem the version-file approach exists to avoid; only do it if options 1 and 2 aren't available.

### Ruby Version-File Selection

`ruby/setup-ruby` accepts several version-file inputs; pick the most expressive one available, but only after confirming the file actually carries a Ruby pin:

| Condition                                          | Input                                 |
| -------------------------------------------------- | ------------------------------------- |
| `.tool-versions` exists AND contains a `ruby` line | `ruby-version-file: ".tool-versions"` |
| `.ruby-version` exists                             | `ruby-version-file: ".ruby-version"`  |
| `Gemfile` exists AND has a `ruby` directive        | `ruby-version-file: "Gemfile"`        |

A `.tool-versions` whose lines are all non-Ruby (e.g., `nodejs 22.10.0` only) does not satisfy the first row — point at `.ruby-version` or `Gemfile` instead, or add a `ruby` line to the existing `.tool-versions`. If none of the three conditions apply, create `.tool-versions` with `ruby <stable>` (or add a `ruby` line to an existing `.tool-versions`).

### Python With `pyproject.toml`

`astral-sh/setup-uv` reads `pyproject.toml`'s `[project] requires-python` automatically — no `python-version-file:` input is needed when uv handles the install, and **no `.python-version` should be created on top of it**. The established convention in this repo's setup-ci templates (see `plugins/setup-ci/skills/setup-ci/SKILL.md` and `plugins/setup-ci/skills/setup-ci/references/ci-python.md`) is that `requires-python` is the only version source for uv workflows; introducing a parallel `.python-version` adds a second source uv ignores and lets local tooling drift apart from CI. If `requires-python` is missing, add it to `pyproject.toml`. For `actions/setup-python` workflows that have no equivalent automatic source, create `.python-version` with the explicit `X.Y.Z`.
