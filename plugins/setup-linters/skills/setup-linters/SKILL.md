---
name: setup-linters
description: >-
  Detect project languages, recommend appropriate linters and formatters,
  install them, and generate config files.
---

# Setup Linters

Detect the project type, recommend appropriate linters and formatters, install them, generate sensible default configs, create `.editorconfig`, and optionally wire up CI.

## Workflow

### 1. Detect Project Type

Scan for language and file-type markers using Glob. **Exclude `node_modules/`, `.yarn/`, and other dependency directories from all searches** to avoid false positives from vendored code.

Use both files and directories as signals:

| Marker(s)                                                                                   | Language/Type         |
| ------------------------------------------------------------------------------------------- | --------------------- |
| `package.json`, `tsconfig.json`, `node_modules/`                                            | JavaScript/TypeScript |
| `go.mod`, `go.sum`                                                                          | Go                    |
| `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, `Pipfile`, `.venv/`, `venv/` | Python                |
| `Cargo.toml`, `Cargo.lock`                                                                  | Rust                  |
| `build.zig`, `build.zig.zon`                                                                | Zig                   |
| `Gemfile`, `*.gemspec`, `.ruby-version`                                                     | Ruby                  |
| `Package.swift`, `*.xcodeproj`, `*.xcworkspace`                                             | Swift                 |
| `*.sh`, `bin/*`, `scripts/*`                                                                | Shell                 |
| `*.zsh`, `#!/usr/bin/env zsh` shebangs, `.zshrc`, `.zshenv`                                 | Zsh                   |
| `*.css`, `*.scss`, `*.less`                                                                 | CSS/SCSS              |
| `Dockerfile`, `*.dockerfile`, `docker-compose.yml`                                          | Docker                |
| `.github/workflows/`                                                                        | GitHub Actions        |
| `*.toml` (beyond `Cargo.toml`)                                                              | TOML                  |
| `*.yaml`, `*.yml` (many files)                                                              | YAML                  |
| `*.md`                                                                                      | Markdown (always)     |

**Source file verification**: When `package.json` is detected, verify that actual JavaScript or TypeScript source files exist (`*.js`, `*.ts`, `*.jsx`, `*.tsx`, `*.mjs`, `*.mts`, excluding `node_modules/` and config files like `eslint.config.js`). A `package.json` used only for devDependencies (e.g., markdownlint tooling) does not make the project a JavaScript project. If no source files are found, skip JavaScript-specific tools (ESLint, Knip) and only recommend tools the project actually needs.

For Node.js projects, detect the package manager from lockfiles and config files:

- `package-lock.json` -- npm
- `yarn.lock` or `.yarnrc.yml` -- yarn
- `pnpm-lock.yaml` -- pnpm
- `bun.lock` -- bun

For CSS/SCSS projects, check whether Tailwind CSS is in use by looking for `tailwindcss` or `@tailwindcss/*` in `package.json` dependencies/devDependencies, or a `tailwind.config.*` file.

For JavaScript/TypeScript projects, perform framework sub-detection to determine which ESLint plugins to install. Check `package.json` dependencies for `react`/`react-dom` (React), `next` (Next.js), `express`/`fastify`/`koa`/`hapi` (Node.js), and look for server-side directory markers (`server.*`, `api/`, `bin/`). See `./references/languages/javascript.md` for the full detection table.

If multiple languages are detected, present all of them (monorepo scenario).

### 2. Detect Existing Linters

Check for existing linter configs using these patterns (aligned with the `lint-and-fix` detection table):

| Config file(s)                                                     | Tool          |
| ------------------------------------------------------------------ | ------------- |
| `eslint.config.*`, `.eslintrc.*`                                   | ESLint        |
| `.prettierrc*`, `prettier.config.*`                                | Prettier      |
| `.markdownlint.json`, `.markdownlint.yaml`, `.markdownlint-cli2.*` | markdownlint  |
| `.shellcheckrc`                                                    | ShellCheck    |
| `.editorconfig`                                                    | EditorConfig  |
| `.golangci.yml`, `.golangci.yaml`                                  | golangci-lint |
| `pyproject.toml` with `[tool.ruff]`                                | Ruff          |
| `rustfmt.toml`, `.rustfmt.toml`                                    | rustfmt       |
| `clippy.toml`, `.clippy.toml`                                      | Clippy        |
| `deny.toml`                                                        | cargo-deny    |
| `typos.toml`, `_typos.toml`                                        | typos         |
| `.rubocop.yml`                                                     | RuboCop       |
| `.stylelintrc*`, `stylelint.config.*`                              | Stylelint     |
| `knip.json`, `knip.config.*`, `knip.ts`                            | Knip          |
| `.hadolint.yaml`, `.hadolint.yml`                                  | Hadolint      |
| `.yamllint.yml`, `.yamllint.yaml`                                  | yamllint      |
| `taplo.toml`, `.taplo.toml`                                        | Taplo         |
| `cspell.json`, `.cspell.json`, `cspell.config.*`                   | cspell        |

**CI workflow scanning**: Also scan `.github/workflows/*.yml` for tools running without config files. For example, a CI step like `shellcheck -S warning scripts/*` means ShellCheck is already in use even without a `.shellcheckrc`. Mark these tools as "Partial" (running in CI but missing local config). A partial tool should still appear in recommendations, but suggest adding the config file for local/CI parity rather than a full setup.

For each already-configured tool, mark it as "Existing" and skip it in recommendations. If everything is already set up, inform the user and stop.

### 3. Recommend Linter Stack

Based on detected languages and file types, recommend the appropriate tool stack. Always include:

- **Language-specific linters** from `./references/languages/*.md`
- **Prettier** as a cross-language formatter (for all projects)
- **EditorConfig** (for all projects)
- **markdownlint-cli2** (if Markdown files detected)
- **File-type-specific tools** based on detection:
  - **Stylelint** when CSS/SCSS/Less files detected (excluding `node_modules/`)
  - **Knip** when `package.json` detected **and** JS/TS source files exist (skip for devDependencies-only projects)
  - **Hadolint** when Dockerfile detected
  - **Actionlint** when `.github/workflows/` detected
  - **Taplo** when `*.toml` files detected (beyond `Cargo.toml`)
  - **yamllint** when many YAML files detected
  - **cspell** as a cross-language spell checker (for all projects)

Read the appropriate reference files for details on each tool.

Present recommendations in a table using three status levels:

- **Existing**: Config file found and tool is fully set up. Skip in recommendations.
- **Partial**: Tool runs in CI but has no local config file. Recommend adding the config for local/CI parity.
- **New**: Tool is not set up at all. Recommend full setup.

```text
| Category     | Tools                          | Status   |
| ------------ | ------------------------------ | -------- |
| JavaScript   | ESLint + Prettier              | New      |
| Shell        | ShellCheck, shfmt              | Partial  |
| Zsh          | shellcheck, shfmt, shellharden, checkbashisms, zsh -n, zcompile, setopt warnings | New      |
| Formatting   | Prettier, EditorConfig         | New      |
| Markdown     | markdownlint-cli2              | Existing |
| Docker       | Hadolint                       | New      |
| CI           | Actionlint                     | New      |
```

### 4. Let User Choose

Ask which tools to install. Default to all recommended. User can:

- Deselect tools they do not want
- Add cross-language tools for any project

### 5. Install Dependencies

For each selected tool, install using the project's package manager. Read the appropriate reference file for exact commands:

- Language-specific: `./references/languages/<language>.md`
- Cross-language tools: `./references/tools/<tool>.md`

#### Pin tool versions to mitigate supply-chain risk

The reference files pin install commands to specific versions (e.g., `cargo install --locked --version X.Y.Z <crate>`, `pip install '<pkg>==X.Y.Z'`, `go install <path>@vX.Y.Z`). Unpinned installs (`@latest`, no `==`) pull whatever the registry currently serves; an attacker who compromises a maintainer account can publish a malicious patch release and have it picked up by every install that ran after the publish. Specific-version pins make the install reproducible and force an explicit bump when the version is updated.

When a pinned version drifts from upstream latest, the repository's `bin/version-audit` workflow opens an issue listing what bumped. Use that as the trigger to refresh the pin in the relevant reference file.

### 6. Create Config Files

Generate default config files and ignore files for each tool. Use templates from the reference files. Also generate:

- **`.editorconfig`** from `./references/tools/editorconfig.md` (adapted to project languages)
- **`.prettierrc.json`** and **`.prettierignore`** from `./references/tools/prettier.md`

Adapt to the project (e.g., TypeScript vs. JavaScript ESLint config, directory structure for ignore patterns).

### 7. Add Package Manager Scripts

Add `lint`, `format`, and/or `lint:fix` scripts to `package.json`, `Makefile`, or equivalent. Read the language-specific reference for exact entries.

### 8. Update Copilot Instructions

If `.github/copilot-instructions.md` exists, append entries to the PR review section for the tools just installed. Only add entries for tools that were actually set up (not skipped or already existing). Before appending each entry, check whether the bold key text already exists in the file; skip entries that are already present.

To locate the PR review section: look for an existing heading whose text includes "PR Review" or "Code Review" (e.g., `## PR Review`, `## Code Review`, `## PR Review Checklist (CRITICAL)`). If no matching heading exists, append a new `## PR Review` section at the end of the file and place the entries there.

If **Prettier** was installed:

- **Prettier `printWidth: 10000` is intentional**: This project uses a high `printWidth` in `.prettierrc.json` to prevent Prettier from wrapping lines. Combined with `proseWrap: preserve` for Markdown, this preserves author line breaks. Do not suggest reducing printWidth to 80 or 120.

If **golangci-lint** config (`.golangci.yml`) was created:

- **golangci-lint v2 config format is intentional**: This project uses golangci-lint v2 configuration which includes `formatters:` as a top-level key and supports `golangci-lint fmt` as a subcommand. These are correct v2 features. Do not suggest reverting to v1 config format.

If `.github/copilot-instructions.md` does not exist, skip this step.

### 9. Set Up CI (Optional)

Ask whether to create a GitHub Actions workflow. If yes, read `./references/tools/github-actions-ci.md` for templates.

If a CI workflow already exists, offer to add lint steps to it rather than creating a new file.

**Tool dependency verification**: For every tool referenced in Makefile targets, confirm the CI workflow includes a corresponding setup/install step. Common tool-to-action mappings (all third-party `uses:` refs are SHA-pinned with a `# vX.Y.Z` comment per the convention in `./references/tools/github-actions-ci.md`; refresh both SHA and comment to current latest before emitting):

| Tool          | CI Setup                                                                                            |
| ------------- | --------------------------------------------------------------------------------------------------- |
| shfmt         | `mfinelli/setup-shfmt@a25fda4c1fe115aec0f85e04126610841bc3141d # v4.0.1` or `go install mvdan.cc/sh/v3/cmd/shfmt@v3.13.1` |
| shellcheck    | `ludeeus/action-shellcheck@00cae500b08a931fb5698e11e79bfbd38e612a38 # 2.0.0`                        |
| golangci-lint | `golangci/golangci-lint-action@1e7e51e771db61008b38414a730f564565cf7c20 # v9.2.0`                   |
| swiftlint     | `brew install swiftlint` (macOS runner)                                                             |
| swiftformat   | `brew install swiftformat` (macOS runner)                                                           |
| checkbashisms | `apt-get install devscripts` (Ubuntu runner)                                                        |
| shellharden   | `cargo install --locked --version 4.3.1 shellharden` (Ubuntu runner)                                |
| cargo-deny    | `taiki-e/install-action@b651345a718c8f44efa2460560b3dbf29cbd7ee1 # v2.75.26` (with `tool: cargo-deny`) |
| typos         | `crate-ci/typos@7c572958218557a3272c2d6719629443b5cc26fd # v1.45.2`                                 |
| hadolint      | `hadolint/hadolint-action@2332a7b74a6de0dda2e2221d575162eba76ba5e5 # v3.3.0`                        |
| actionlint    | `raven-actions/actionlint@205b530c5d9fa8f44ae9ed59f341a0db994aa6f8 # v2.1.2`                        |
| cspell        | `streetsidesoftware/cspell-action@de2a73e963e7443969755b648a1008f77033c5b2 # v8.4.0`                |

### 10. Run Initial Lint (Optional)

Ask whether to run the newly installed linters. If yes, invoke `lint-and-fix` to fix existing issues.

### 11. Commit (Optional)

Ask whether to commit the setup. Suggest `chore: set up <tool list>` as the commit message prefix.

## Error Handling

- **No languages detected**: If the project has no recognizable language markers, still offer Prettier, EditorConfig, and markdownlint-cli2 as cross-language tools.
- **Everything already set up**: If all detected tools are already configured, inform the user and stop. Suggest running `lint-and-fix` instead.
- **Package manager not found**: If a Node.js project has no lockfile, default to npm. For non-Node projects, guide installation via Homebrew, Cargo, or the appropriate system package manager.
- **Install failure**: If a tool fails to install, report the error and continue with the next tool.
- **Config conflict**: If a generated config would overwrite an existing file, ask before overwriting.
- **Pre-commit hook failure on commit**: Fix the issue, re-stage, and create a new commit (never amend).

## Refresh `cboone/gh-actions` SHAs before scaffolding

The `cboone/gh-actions` reusable-workflow refs in this skill's templates are SHA-pinned with a `# vX.Y.Z` comment that was current when the template was authored. New releases of `cboone/gh-actions` rot those SHAs. Before emitting a workflow into a user's repo, refresh both the SHA and the comment to current latest:

```bash
TAG="$(gh release view --repo cboone/gh-actions --json tagName --jq '.tagName')"
SHA="$(gh api "repos/cboone/gh-actions/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

Replace each `cboone/gh-actions/.../<workflow>.yml@<old-sha> # <old-tag>` in the emitted workflow with the new SHA and tag. Dependabot in the user's repo keeps them in sync afterwards.
