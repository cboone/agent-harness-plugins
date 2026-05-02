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

Scan for language and file-type markers using Glob. **Exclude `node_modules/`, `.yarn/`, `.lake/` (Lean dependency/build directory, including `.lake/packages/**`), and other dependency directories from all searches** to avoid false positives from vendored code.

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
| `lakefile.toml`, `lakefile.lean`, `lean-toolchain`, `*.lean`                                | Lean                  |
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

For Lean projects (any of `lakefile.toml`, `lakefile.lean`, `lean-toolchain`, or `*.lean` files present, with `.lake/` excluded so dependency-vendored `lakefile.*` and `*.lean` files do not trigger detection), the project uses `lake lint` driven by `lintDriver = "batteries/runLinter"` rather than an external linter. There is no tool to install: `lake` ships with the toolchain, `batteries/runLinter` ships with Batteries (already a transitive Mathlib dependency). Setup is wiring (the `lintDriver` field in `lakefile.toml`, a `lean-lint` Makefile target, and a CI step) rather than installation. Skip any toolchain install in this skill; the `scaffold-lean-library` skill handles `elan` and the bootstrap script. See `./references/languages/lean.md` for details.

Detect the **Pandoc-academic preset** separately from language detection. Enable it when the project contains `references/papers/` or `references/transcriptions/`, or when the user explicitly requests it with `--pandoc-academic` or equivalent wording such as "Pandoc-academic preset". This preset customizes markdownlint and cspell for paper-backed Lean/math projects that use YAML frontmatter titles, Pandoc citations, LaTeX math, raw `{=latex}` blocks, dense tables, and transcription trees treated as excluded reference material. See `./references/tools/markdownlint.md` and `./references/tools/cspell.md`.

If multiple languages are detected, present all of them (monorepo scenario).

### 2. Detect Existing Linters

Check for existing linter configs using these patterns (aligned with the `lint-and-fix` detection table):

| Config file(s)                                                                      | Tool          |
| ----------------------------------------------------------------------------------- | ------------- |
| `eslint.config.*`, `.eslintrc.*`                                                    | ESLint        |
| `.prettierrc*`, `prettier.config.*`                                                 | Prettier      |
| `.markdownlint.json`, `.markdownlint.yaml`, `.markdownlint-cli2.*`                  | markdownlint  |
| `.shellcheckrc`                                                                     | ShellCheck    |
| `.editorconfig`                                                                     | EditorConfig  |
| `.golangci.yml`, `.golangci.yaml`                                                   | golangci-lint |
| `pyproject.toml` with `[tool.ruff]`                                                 | Ruff          |
| `rustfmt.toml`, `.rustfmt.toml`                                                     | rustfmt       |
| `clippy.toml`, `.clippy.toml`                                                       | Clippy        |
| `deny.toml`                                                                         | cargo-deny    |
| `typos.toml`, `_typos.toml`                                                         | typos         |
| `.rubocop.yml`                                                                      | RuboCop       |
| `.stylelintrc*`, `stylelint.config.*`                                               | Stylelint     |
| `knip.json`, `knip.config.*`, `knip.ts`                                             | Knip          |
| `.hadolint.yaml`, `.hadolint.yml`                                                   | Hadolint      |
| `.yamllint.yml`, `.yamllint.yaml`                                                   | yamllint      |
| `taplo.toml`, `.taplo.toml`                                                         | Taplo         |
| `cspell.json`, `cspell.jsonc`, `.cspell.json`, `.cspell.jsonc`, `cspell.config.*`   | cspell        |
| `lakefile.toml` containing `lintDriver`, `lakefile.lean` containing `lintDriver :=` | `lake lint`   |

**CI workflow scanning**: Also scan `.github/workflows/*.yml` for tools running without config files. For example, a CI step like `shellcheck -S warning scripts/*` means ShellCheck is already in use even without a `.shellcheckrc`. Mark these tools as "Partial" (running in CI but missing local config). A partial tool should still appear in recommendations, but suggest adding the config file for local/CI parity rather than a full setup.

For each already-configured tool, mark it as "Existing" and skip it in recommendations. Exception: when the Pandoc-academic preset was detected or requested, do not treat generic markdownlint/cspell config presence as sufficient. Continue to the preset recommendation step unless the preset completeness check below passes. If everything is already set up, inform the user and stop.

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

**Lean projects**: Lean has no external linter to install. Recommend `lake lint` driven by `lintDriver = "batteries/runLinter"` instead of a tool install. Setup is wiring (the `lintDriver` field, a `lean-lint` Makefile target gated on `_check-mathlib-cache`, and a CI step). Cross-language tools (markdownlint-cli2, cspell, EditorConfig, yamllint, Actionlint) still apply on top. See `./references/languages/lean.md`.

**Pandoc-academic preset**: If the preset was detected or requested, recommend markdownlint-cli2 and cspell with the Pandoc-academic configuration variant instead of the generic Markdown and spelling defaults. Mark the preset as "Existing" only when a markdownlint config already contains the Pandoc/LaTeX rule customizations and covers the preset ignore globs through either config-level `ignores` or `.markdownlintignore`, a cspell config (`cspell.json`, `cspell.jsonc`, `.cspell.json`, `.cspell.jsonc`, or `cspell.config.*`) contains the Pandoc/LaTeX ignore patterns and ignore paths for preset-specific files or directories that exist in the project, and the cspell project vocabulary is satisfiable through existing inline `words` or existing referenced dictionary files. Do not require optional ignore paths for absent directories such as `.lake/`.

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
| Lean         | lake lint (lintDriver = "batteries/runLinter")                                   | Partial  |
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

**Lean has nothing to install in this step.** `lake` ships with the toolchain and `batteries/runLinter` ships with the Batteries dependency. Do not install `lean`, `elan`, or any external Lean linter from this skill; the `scaffold-lean-library` skill owns toolchain provisioning. Skip directly to the wiring steps (config, Makefile, CI) below.

#### Pin tool versions to mitigate supply-chain risk

The reference files pin install commands to specific versions (e.g., `cargo install --locked --version X.Y.Z <crate>`, `pip install '<pkg>==X.Y.Z'`, `go install <path>@vX.Y.Z`). Unpinned installs (`@latest`, no `==`) pull whatever the registry currently serves; an attacker who compromises a maintainer account can publish a malicious patch release and have it picked up by every install that ran after the publish. Specific-version pins make the install reproducible and force an explicit bump when the version is updated.

When a pinned version drifts from upstream latest, the repository's `bin/version-audit` workflow opens an issue listing what bumped. Use that as the trigger to refresh the pin in the relevant reference file.

### 6. Create Config Files

Generate default config files and ignore files for each tool. Use templates from the reference files. Also generate:

- **`.editorconfig`** from `./references/tools/editorconfig.md` (adapted to project languages)
- **`.prettierrc.json`** and **`.prettierignore`** from `./references/tools/prettier.md`

For **Lean projects**, the equivalent of "creating a config file" is adding the `lintDriver` field to `lakefile.toml` (or the `package` block of `lakefile.lean`):

```toml
lintDriver = "batteries/runLinter"
```

If the field is already present, mark Lean as "Existing" and skip. If `lakefile.toml` exists but lacks the field, offer to add it. If neither `lakefile.toml` nor `lakefile.lean` exists in the detected Lean project, defer to the `scaffold-lean-library` skill rather than synthesizing one here. See `./references/languages/lean.md` for the `lakefile.lean` form.

Adapt to the project (e.g., TypeScript vs. JavaScript ESLint config, directory structure for ignore patterns).

For the **Pandoc-academic preset**, generate all of the following together when markdownlint and cspell do not already have supported config files. If a supported config file exists but fails the preset completeness check, update that existing config in place instead of adding a second config file that the tool may not load. Preserve the existing config format where practical, including `.markdownlint.yaml`, `.markdownlint-cli2.*`, `cspell.json`, `cspell.jsonc`, `.cspell.json`, `.cspell.jsonc`, and `cspell.config.*`; if the existing format cannot be updated confidently, explain the conflict and ask before creating a replacement.

- `.markdownlint-cli2.jsonc` using the Pandoc-academic markdownlint rule overrides from `./references/tools/markdownlint.md`
- `cspell.jsonc` using the Pandoc-academic `ignorePaths`, dictionary definition, and `ignoreRegExpList` from `./references/tools/cspell.md`
- `cspell-words.txt` seeded with the Lean/math vocabulary from `./references/tools/cspell.md`, plus core author surnames from citations the project actually uses (usually from `references/papers.bib`)

### 7. Add Package Manager Scripts

Add `lint`, `format`, and/or `lint:fix` scripts to `package.json`, `Makefile`, or equivalent. Read the language-specific reference for exact entries.

For **Lean projects**, the script entry is a `lean-lint` Makefile target that wraps `lake lint` and depends on the `_check-mathlib-cache` private target:

```makefile
lean-lint: _check-mathlib-cache ## Run Lean linter (batteries)
	lake lint
```

If a `Makefile` exists but has no `lean-lint` target, offer to add it. If the `Makefile` lacks `_check-mathlib-cache` as well, the project's Makefile predates the standard Mathlib-downstream target set; defer to the `scaffold-lean-library` skill rather than synthesizing the target wholesale here. If no `Makefile` exists at all, defer to the `scaffold-lean-library` skill.

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

For **Lean projects**, scan `.github/workflows/*.yml` for the `leanprover/lean-action` action:

- If found, confirm the `lint: true` input is set on the action. If it is, mark Lean CI as "Existing"; `lake lint` runs as part of the action. If `lint: true` is missing, offer to add it (or recommend a dedicated `lake lint` step if the project deliberately splits build, test, and lint into separate jobs).
- If not found, defer to the `scaffold-lean-library` skill rather than synthesizing a Lean CI workflow here.

**Tool dependency verification**: For every tool referenced in Makefile targets, confirm the CI workflow includes a corresponding setup/install step. Common tool-to-action mappings (all third-party `uses:` refs are SHA-pinned with a comment that matches the upstream tag, typically `# vX.Y.Z` but `# X.Y.Z` when upstream omits the `v` prefix, per the convention in `./references/tools/github-actions-ci.md`; refresh both SHA and comment to current latest before emitting):

| Tool          | CI Setup                                                                                                                  |
| ------------- | ------------------------------------------------------------------------------------------------------------------------- |
| shfmt         | `mfinelli/setup-shfmt@a25fda4c1fe115aec0f85e04126610841bc3141d # v4.0.1` or `go install mvdan.cc/sh/v3/cmd/shfmt@v3.13.1` |
| shellcheck    | `ludeeus/action-shellcheck@00cae500b08a931fb5698e11e79bfbd38e612a38 # 2.0.0`                                              |
| golangci-lint | `golangci/golangci-lint-action@1e7e51e771db61008b38414a730f564565cf7c20 # v9.2.0`                                         |
| swiftlint     | `brew install swiftlint` (macOS runner)                                                                                   |
| swiftformat   | `brew install swiftformat` (macOS runner)                                                                                 |
| checkbashisms | `apt-get install devscripts` (Ubuntu runner)                                                                              |
| shellharden   | `cargo install --locked --version 4.3.1 shellharden` (Ubuntu runner)                                                      |
| cargo-deny    | `taiki-e/install-action@b651345a718c8f44efa2460560b3dbf29cbd7ee1 # v2.75.26` (with `tool: cargo-deny`)                    |
| typos         | `crate-ci/typos@7c572958218557a3272c2d6719629443b5cc26fd # v1.45.2`                                                       |
| hadolint      | `hadolint/hadolint-action@2332a7b74a6de0dda2e2221d575162eba76ba5e5 # v3.3.0`                                              |
| actionlint    | `raven-actions/actionlint@205b530c5d9fa8f44ae9ed59f341a0db994aa6f8 # v2.1.2`                                              |
| cspell        | `cboone/gh-actions/actions/run-cspell@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0`                                  |
| lake lint     | `leanprover/lean-action@<sha> # <tag>` (with `lint: true`); refresh both SHA and tag to current latest before emitting    |

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
- **Auto-fix introduces compilation errors**: Some linter auto-fix rules can produce incorrect code in edge cases (notably SwiftLint's `redundant_nil_coalescing` rule, which can break double-optional expressions). After any auto-fix pass, re-run the project's compiler or test command (`swift test --build-tests`, `cargo build`, `go build`, `tsc`, etc.) to verify that the auto-fixes did not introduce compilation errors. Where applicable, include a compile or test verification step in the language reference's suggested auto-fix target.
- **Pre-commit hook failure on commit**: Fix the issue, re-stage, and create a new commit (never amend).

## Refresh `cboone/gh-actions` SHAs before scaffolding

The `cboone/gh-actions` reusable-workflow refs in this skill's templates are SHA-pinned with a `# vX.Y.Z` comment that was current when the template was authored. New releases of `cboone/gh-actions` rot those SHAs. Before emitting a workflow into a user's repo, refresh both the SHA and the comment to current latest:

```bash
TAG="$(gh release view --repo cboone/gh-actions --json tagName --jq '.tagName')"
SHA="$(gh api "repos/cboone/gh-actions/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

Replace each `cboone/gh-actions/.../<workflow>.yml@<old-sha> # <old-tag>` in the emitted workflow with the new SHA and tag. Dependabot in the user's repo keeps them in sync afterwards.
