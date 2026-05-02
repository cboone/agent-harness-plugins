# Version Surfaces

Use this checklist to find every repository version reference before resolving upstream versions. It extends the `pin-everything` surface audit with upgrade-oriented surfaces such as release tools, schema URLs, marketplace metadata, and version-like literals in docs or scripts.

## Exclusions

Exclude generated, vendored, and cache directories from all searches unless the user explicitly asks to audit them:

- `.git/`
- `node_modules/`
- `.yarn/`
- `.lake/`
- `vendor/`
- `dist/`
- `target/`
- `.venv/`
- package manager cache directories
- generated coverage or build output directories

## Surface Checklist

| Surface family                 | Common files and patterns                                                                                                                                                         | Capture                                                                                       | Notes                                                                                 |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Package manifests              | `package.json`, `pyproject.toml`, `requirements*.txt`, `uv.lock`, `poetry.lock`, `Pipfile.lock`, `go.mod`, `Cargo.toml`, `Gemfile`, `*.gemspec`, `Package.swift`, `composer.json` | Direct dependencies, dev dependencies, tool dependencies, language directives, workspace pins | Preserve public library compatibility ranges unless the user selects a tightening.    |
| Lockfiles                      | `yarn.lock`, `package-lock.json`, `pnpm-lock.yaml`, `uv.lock`, `poetry.lock`, `Cargo.lock`, `Gemfile.lock`, `Package.resolved`, `composer.lock`                                   | Locked package versions and transitive upgrade opportunities                                  | Do not hand-edit lockfiles when a package manager owns them.                          |
| GitHub Actions                 | `.github/workflows/*.{yml,yaml}`, `.github/actions/**/action.{yml,yaml}`                                                                                                          | `uses:` refs, action versions, setup action inputs, reusable workflow refs                    | Include SHA-pinned refs by resolving the adjacent version comment when available.     |
| Reusable workflows             | Workflow `uses:` values containing `.github/workflows/`                                                                                                                           | Calling repo, workflow path, ref, exposed inputs                                              | Treat org-owned reusable workflows as upstream dependencies.                          |
| Language runtimes              | `.tool-versions`, `.nvmrc`, `.node-version`, `.ruby-version`, `.python-version`, `rust-toolchain.toml`, `go.mod`, `build.zig.zon`, workflow runtime inputs                        | Runtime channel or exact version                                                              | Runtime jumps often carry higher risk than package patch upgrades.                    |
| Container images               | `Dockerfile*`, `docker-compose*.yml`, `.devcontainer/**`, Kubernetes manifests, Helm values                                                                                       | Image name, tag, digest, base image family                                                    | Prefer digest-aware registry metadata when available.                                 |
| Devcontainer features          | `.devcontainer/devcontainer.json`, `.devcontainer/*.json`                                                                                                                         | Feature IDs, feature versions, image tags                                                     | Treat features as dependencies even when they are not package-manager dependencies.   |
| Tool install commands          | `Makefile`, `justfile`, `Taskfile*.yml`, `bin/*`, `scripts/*`, `*.sh`, workflow `run:` blocks, Markdown setup docs                                                                | `go install`, `cargo install`, `pip install`, `uv add`, `uv tool install`, `uvx`, `npx` pins  | Preserve the original install verb when upgrading.                                    |
| Package manager pins           | `packageManager` in `package.json`, `.yarnrc.yml`, `.npmrc`, `.pnpmfile.cjs`, Corepack metadata                                                                                   | Package manager name, version, integrity suffix                                               | Package manager changes can affect all dependency resolution.                         |
| Schema URLs                    | `$schema` fields in JSON, YAML, TOML-adjacent config, and Markdown examples                                                                                                       | Schema URL, version segment, publisher                                                        | Some publishers expose only moving URLs; keep those as blocked or unpinnable.         |
| Release tooling                | `.goreleaser*.yml`, `cliff.toml`, release workflows, Homebrew formula files, package publishing config                                                                            | Tool versions, action refs, changelog tool pins, formula versions                             | Validate release configs with their native dry-run or check command when available.   |
| Marketplace and plugin data    | `.claude-plugin/marketplace.json`, plugin manifests, extension manifests, action metadata                                                                                         | Plugin versions, catalog state, manifest dependency versions                                  | Recompute derived catalog or aggregate versions after selected upgrades.              |
| Documentation version literals | `README.md`, `docs/**/*.md`, skill references, command templates                                                                                                                  | Real install commands, versioned examples, template defaults                                  | Distinguish real tool commands from placeholders such as `OWNER/REPO` or `<version>`. |
| Config version literals        | `*.json`, `*.jsonc`, `*.yaml`, `*.yml`, `*.toml`, `*.ini`, `*.conf`                                                                                                               | Version-like strings not covered elsewhere                                                    | Treat as low confidence until tied to an upstream source.                             |

## Candidate Rules

- A candidate is any version surface where a current upstream value can be newer, unknown, blocked, or intentionally held.
- High-risk candidates stay in the matrix. Risk changes recommendation and validation, not inclusion.
- Low-reward candidates stay in the matrix. Reward changes priority, not inclusion.
- If a surface appears in generated output and source input, report the source input as the editable candidate and summarize the generated output as affected.
- If the same dependency appears in multiple places, group the occurrences under one candidate only when they share an owner and can be upgraded together.
