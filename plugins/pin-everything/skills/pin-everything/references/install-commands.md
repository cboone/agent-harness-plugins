# Pinning Install Commands

Per-package-manager pinning recipes for tool-install commands embedded in CI workflows, Makefiles, scripts, and documentation.

## Why Pin Install Commands

A `go install some/tool@latest` in CI installs whatever the upstream maintainer most recently tagged. If they tag a malicious release, CI runs the malicious binary on the next push. Pinning the install command to an explicit version means CI runs only the version that was reviewed when the line was added, so any upgrade is intentional. Note: install-command pins inside scripts, Makefiles, and skill prose are *not* tracked by Dependabot (it only scans manifest/lockfile ecosystems and workflow `uses:` refs). For drift coverage of these surfaces, pair this step with the bundled `version-audit` script (step 10).

## Per-Manager Recipes

| Manager                  | Pinned form                                      | Upstream-of-record                  | Lookup endpoint                                                         |
| ------------------------ | ------------------------------------------------ | ----------------------------------- | ----------------------------------------------------------------------- |
| `go install`             | `go install <path>@vX.Y.Z`                       | GitHub releases for the path's repo | `gh release view --repo <owner>/<repo> --json tagName`                  |
| `cargo install`          | `cargo install --locked --version X.Y.Z <crate>` | crates.io                           | `https://crates.io/api/v1/crates/<crate>` → `.crate.max_stable_version` |
| `pip install`            | `pip install '<pkg>==X.Y.Z'`                     | PyPI                                | `https://pypi.org/pypi/<pkg>/json` → `.info.version`                    |
| `uv pip install`         | `uv pip install '<pkg>==X.Y.Z'`                  | PyPI                                | Same as `pip`                                                           |
| `uv add`                 | `uv add '<pkg>==X.Y.Z'`                          | PyPI                                | Same as `pip`                                                           |
| `uv tool install`        | `uv tool install '<pkg>==X.Y.Z'`                 | PyPI                                | Same as `pip`                                                           |
| `uvx`                    | `uvx '<pkg>==X.Y.Z' [args]`                      | PyPI                                | Same as `pip`                                                           |
| `npx`                    | `npx <tool>@X.Y.Z`                               | npm registry                        | `https://registry.npmjs.org/<tool>/latest` → `.version`                 |
| `brew install` (formula) | _no in-line pin_; use a tap with versioned cask  | (not a pinning surface)             | —                                                                       |
| `brew install` (cask)    | `version "X.Y.Z"` in a tap-managed cask          | The tap's release process           | Owned by the publishing repo, not by this skill                         |

Keep the four uv verbs distinct when adding a `==` pin: `uv pip install` mutates the current environment, `uv add` writes the dependency to `pyproject.toml` and `uv.lock`, `uv tool install` installs a tool persistently to the user-global `~/.local/bin`, and `uvx` (alias for `uv tool run`) executes a tool ephemerally from a cached install. Each verb has a distinct destination; rewriting one as another silently changes which surface is pinned. Pin in place, never swap.

For the HTTP lookup endpoints (`crates.io`, `pypi.org`, `registry.npmjs.org`), fetch with `curl -fsSL <endpoint>` and extract with `jq -r '<filter>'`. The `go install` row uses `gh release view` instead — the upstream-of-record is a GitHub release for the install path's repo, not an HTTP API, so the recipe is `gh release view --repo <owner>/<repo> --json tagName --jq '.tagName'`. The bundled `version-audit-template` script wraps both shapes in error-tolerant boilerplate.

## `go install` Specifics

`go install path@version` needs a full module path. The version must be a Git tag in the path's repo (semver-prefixed with `v`, e.g. `v1.2.3`) or a pseudo-version like `v0.0.0-20240901123456-abcdef123456`. Use a release tag whenever one exists.

Map an install path to its upstream repo for the lookup:

| Install path                                             | Upstream repo            |
| -------------------------------------------------------- | ------------------------ |
| `github.com/golangci/golangci-lint/v2/cmd/golangci-lint` | `golangci/golangci-lint` |
| `golang.org/x/vuln/cmd/govulncheck`                      | `golang/vuln`            |
| `github.com/goreleaser/goreleaser/v2`                    | `goreleaser/goreleaser`  |
| `github.com/rhysd/actionlint/cmd/actionlint`             | `rhysd/actionlint`       |
| `mvdan.cc/sh/v3/cmd/shfmt`                               | `mvdan/sh`               |
| `github.com/google/yamlfmt/cmd/yamlfmt`                  | `google/yamlfmt`         |

For paths under `golang.org/x/`, the upstream is `golang/<name>`. For paths starting with `mvdan.cc/`, the upstream is `mvdan/<name>`. For `github.com/<owner>/<repo>/...`, the upstream is `<owner>/<repo>`.

## `cargo install` Specifics

Always pass `--locked` alongside `--version`. Without `--locked`, cargo resolves the dependency graph fresh from the registry at install time, which means CI installs whatever transitive deps are current — not the deps the crate authors tested against.

```bash
cargo install --locked --version 0.19.4 cargo-deny
```

Crates.io's API exposes `max_stable_version` (excludes pre-releases) and `max_version` (includes them); prefer `max_stable_version` for default lookups.

## `pip` / `uv` Specifics

Single-quote the requirement spec so the shell doesn't interpret `==`:

```bash
pip install 'ruff==0.15.12'
uv pip install 'ruff==0.15.12'
uv add 'ruff==0.15.12'
uv tool install 'ruff==0.15.12'
uvx 'ruff==0.15.12' check .
```

`uv` is preferred over `pip` for newly written install commands: it resolves and installs an order of magnitude faster and (in the case of `uv add`) writes to `uv.lock` for reproducibility. **Do not convert existing `pip install` lines to `uv add` (or any other uv verb) as part of pin-everything.** Each verb has a distinct destination — see the per-verb breakdown below — so swapping verbs silently changes which surface is touched. Pin in place: a `pip install foo` line becomes `pip install 'foo==X.Y.Z'`, not `uv add 'foo==X.Y.Z'`.

The five forms are not interchangeable:

- `pip install 'pkg==X.Y.Z'` and `uv pip install 'pkg==X.Y.Z'` install into the current environment without recording the dependency.
- `uv add 'pkg==X.Y.Z'` records the pin in `pyproject.toml` and updates `uv.lock`.
- `uv tool install 'pkg==X.Y.Z'` installs a tool persistently to the user-global `~/.local/bin` (or `$UV_TOOL_BIN_DIR`). Use this when CI or local dev needs a stable tool binary on `PATH` without touching the project's `pyproject.toml` (linters, formatters, build helpers).
- `uvx 'pkg==X.Y.Z' [args]` is shorthand for `uv tool run` — it resolves the tool to the pinned version, caches it on first run, and invokes it ephemerally without persisting anything to a tool dir or to `pyproject.toml`. The `pkg@X.Y.Z` (`@`) shorthand is equivalent but the `==` form composes with the rest of this guide.

Preserve the verb when adding a pin: rewriting `uv add` as `uv pip install` drops the manifest update; rewriting `uv tool install` as `uv add` adds the tool to the project as a dependency rather than to the user's tool dir; rewriting `uvx` as `uv tool install` persists a binary that was meant to be ephemeral.

## `npx` Specifics

`npx <tool>` without a version uses the highest version cached locally, falling back to a fresh registry resolve. In CI without a local install, that fresh resolve picks up whatever `latest` tags to right now. Pin both for CI invocations and for one-off invocations in scripts:

```bash
npx prettier@3.8.3 --check .
npx markdownlint-cli2@0.22.1 '**/*.md'
```

If the tool is already a `devDependency` in a `package.json` repo (the common case for `prettier`, `eslint`, etc.), `npx` resolves it via the lockfile. Don't add a version pin in that case — the lockfile is the version of record. Only pin standalone `npx` invocations in CI templates and scripts.

## `brew install` Caveats

Homebrew formulae don't accept an inline `@version` argument; reproducible installs require a custom tap with versioned cask blocks. This skill leaves `brew install <formula>` unpinned by default because:

1. The pinning mechanism (a tap) lives in a separate repo, owned by the publisher.
2. Most CI doesn't use Homebrew (Linux runners use apt, ubuntu-latest's preinstalled tooling, or the project's own setup-* actions).
3. Pinning Homebrew on macOS dev machines is a workstation concern, not a CI hardening one.

When the consuming project owns its own tap (for example, via `add-goreleaser-homebrew`), the cask `version` field is the pinning surface and falls under that tap's release process.

## User-Facing vs Tool-Install Discriminator

The single most important judgment call in this step. Skip pinning when the install path matches any of these patterns — it's a placeholder for the downstream user's project, not a real install:

- Path contains `OWNER/REPO`, `GITHUB-USERNAME`, `PROJECT-NAME`, or `<...>`-style substitution markers.
- Command appears under a `## Usage` or `## Installation` heading in a scaffolded README template.
- Command is in a `code` block in a skill's reference docs whose audience is the next user (not the agent).

Real tool installs that should be pinned:

- Lines in `.github/workflows/*.yml` (these run in CI).
- Lines in `Makefile` targets (these run in local dev and CI).
- Lines in `scripts/*` and `bin/*` (these run when invoked).
- Lines in skill orchestration prose that the agent will execute (as opposed to print).

When ambiguous, prompt the user.
