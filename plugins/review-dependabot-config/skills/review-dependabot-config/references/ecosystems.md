# Ecosystems

How to turn what is in the repository into the `package-ecosystem` entries and directories a config should have.

GitHub adds ecosystems over time. The table below covers the common ones. For a manifest it does not list, check the current [supported ecosystems page](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories) before reporting a gap or a stale entry.

## Manifest to ecosystem

| Found in a directory                                                                                  | `package-ecosystem` | Notes                                                                                                                                                                      |
| ----------------------------------------------------------------------------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.github/workflows/*.yml`, `action.yml`, `action.yaml`                                                | `github-actions`    | `directory: /` covers `.github/workflows/`. A composite action elsewhere needs its own directory when it has external `uses:`                                              |
| `package.json` with `package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`                             | `npm`               | npm, Yarn, and pnpm all use `npm`. A workspace root covers its members                                                                                                     |
| `package.json` with `bun.lock`                                                                        | `bun`               | Version updates only. The legacy binary `bun.lockb` is not supported: migrating to the text `bun.lock` is the fix                                                          |
| `deno.json` or `deno.jsonc`                                                                           | `deno`              |                                                                                                                                                                            |
| `uv.lock`                                                                                             | `uv`                | A `pyproject.toml` with `uv.lock` is `uv`, not `pip`                                                                                                                       |
| `requirements*.txt`, `requirements*.in`, `Pipfile`, `poetry.lock`, `pyproject.toml` without `uv.lock` | `pip`               | pip, pip-compile, pipenv, and Poetry all use `pip`                                                                                                                         |
| `environment.yml` (conda)                                                                             | `conda`             |                                                                                                                                                                            |
| `go.mod`                                                                                              | `gomod`             | A `go.work` workspace lists its modules; each module directory with its own `go.mod` still needs coverage                                                                  |
| `Cargo.toml` with `Cargo.lock`                                                                        | `cargo`             | A Cargo workspace root covers its members                                                                                                                                  |
| `rust-toolchain.toml` or `rust-toolchain`                                                             | `rust-toolchain`    | Version updates only. Separate from `cargo`, which covers crate dependencies                                                                                               |
| `Gemfile`, `Gemfile.lock`, `*.gemspec`                                                                | `bundler`           |                                                                                                                                                                            |
| `composer.json`                                                                                       | `composer`          |                                                                                                                                                                            |
| `pom.xml`                                                                                             | `maven`             |                                                                                                                                                                            |
| `build.gradle`, `build.gradle.kts`, `settings.gradle*`                                                | `gradle`            |                                                                                                                                                                            |
| `*.csproj`, `packages.config`, `Directory.Packages.props`                                             | `nuget`             |                                                                                                                                                                            |
| `global.json`                                                                                         | `dotnet-sdk`        | Version updates only                                                                                                                                                       |
| `pubspec.yaml`                                                                                        | `pub`               |                                                                                                                                                                            |
| `mix.exs`                                                                                             | `mix`               | Version updates only                                                                                                                                                       |
| `Package.swift`                                                                                       | `swift`             | Only when `Package.swift` is the real source of dependencies. A project generated from another tool's spec (an XcodeGen `project.yml`, say) gets no useful updates from it |
| `Dockerfile`, `*.Dockerfile`, `Containerfile`                                                         | `docker`            | Version updates only                                                                                                                                                       |
| `docker-compose.yml`, `compose.yaml`                                                                  | `docker-compose`    | Version updates only                                                                                                                                                       |
| `Chart.yaml`                                                                                          | `helm`              | Version updates only                                                                                                                                                       |
| `*.tf`                                                                                                | `terraform`         | Version updates only                                                                                                                                                       |
| `*.tf` or `*.tofu` in a project run with OpenTofu                                                     | `opentofu`          | Version updates only. A Terraform project uses `terraform`                                                                                                                 |
| `.devcontainer/devcontainer.json`, `.devcontainer.json`                                               | `devcontainers`     | Version updates only                                                                                                                                                       |
| `.gitmodules`                                                                                         | `gitsubmodule`      | Version updates only                                                                                                                                                       |
| `.pre-commit-config.yaml`                                                                             | `pre-commit`        | Version updates only                                                                                                                                                       |
| `flake.nix` with `flake.lock`                                                                         | `nix`               | Version updates only                                                                                                                                                       |
| `MODULE.bazel`                                                                                        | `bazel`             | Version updates only                                                                                                                                                       |

"Version updates only" means the ecosystem gets scheduled update PRs but no automatic security update PRs, so a vulnerability there needs a person.

## Directories

- **`directory` or `directories`.** `directory` takes one path. `directories` takes a list and accepts globs (`/apps/*`, `/**`). Use `directories` whenever an ecosystem lives in more than one place.
- **What `/` covers.** For most ecosystems, `/` covers only the manifest at the repository root. For `github-actions`, `/` covers `.github/workflows/` too.
- **Composite actions.** A composite action under `.github/actions/NAME/` or `actions/NAME/` that references another action in a `uses:` step needs `/.github/actions/NAME` (or `/actions/NAME`) in the `github-actions` entry. A composite action made only of `run:` steps has nothing to update and needs no entry. When a new external `uses:` is added to such an action later, the directory has to be added then.
- **Workspaces.** A workspace root (npm, Yarn, and pnpm workspaces; a Cargo workspace) covers its members from the root directory. A nested project with its own lockfile is a separate install tree and needs its own directory.
- **Out of scope.** Leave out vendored copies, test fixtures, examples that are never installed, and subtrees whose dependencies another repository manages. A committed `dist/` or build output is never a source of truth.

## Surfaces Dependabot does not track

Dependabot updates manifests, lockfiles, and workflow references. It does not see:

| Surface                            | Examples                                                                              |
| ---------------------------------- | ------------------------------------------------------------------------------------- |
| Runtime version files              | `.tool-versions`, `.nvmrc`, `.node-version`, `.python-version`, `.ruby-version`       |
| Package manager pins               | `packageManager` in `package.json`                                                    |
| Tool versions in workflows         | `env:` values and action inputs that choose a tool version, such as a linter or CLI   |
| Install commands                   | `curl .../v1.2.3/...`, `go install tool@v1.2.3`, `pip install tool==1.2.3` in scripts |
| Action references in documentation | `uses:` lines inside Markdown templates                                               |
| Checksums                          | SHA-256 values pinned beside a download                                               |

Report these in the untracked surfaces section rather than as config findings.
