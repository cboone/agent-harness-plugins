---
description: Set up GitHub Actions CI with test, lint, format, and vulnerability check jobs, plus matching Makefile targets.
disable-model-invocation: true
argument-hint: "[go-cli|go-library|javascript|python|rust|ruby|shell|zig|zsh]"
---

# Setup CI

Detect the project's language(s), create a GitHub Actions CI workflow with appropriate parallel jobs (test, lint, format, vulnerability check), and create matching Makefile targets for local development.

## Workflow

### 1. Detect Project Type

If `$ARGUMENTS` specifies a language (e.g., `go-cli`, `go-library`, `javascript`, `python`, `rust`, `ruby`, `shell`, `zig`, `zsh`), use it directly instead of scanning for markers. Still perform sub-detection steps as needed (e.g., JS package manager detection for `javascript`, or verifying `main.go`/`cmd/` for `go-cli` vs `go-library`).

Scan for language and file-type markers using Glob. **Exclude `node_modules/`, `.yarn/`, `vendor/`, and other dependency directories from all searches** to avoid false positives from vendored code.

| Marker(s)                                                                                                     | Language              |
| ------------------------------------------------------------------------------------------------------------- | --------------------- |
| `go.mod`                                                                                                      | Go                    |
| `package.json` + source files (`*.js`, `*.ts`, `*.jsx`, `*.tsx`, `*.mjs`, `*.mts`, excluding `node_modules/`) | JavaScript/TypeScript |
| `pyproject.toml`, `setup.py`, `requirements.txt`                                                              | Python                |
| `Cargo.toml`                                                                                                  | Rust                  |
| `build.zig`, `build.zig.zon`                                                                                  | Zig                   |
| `Gemfile`, `*.gemspec`                                                                                        | Ruby                  |
| `*.sh`, `bin/*`, `scripts/*`                                                                                  | Shell                 |
| `*.zsh`, `#!/usr/bin/env zsh` shebangs, `.zshrc`, `.zshenv`                                                   | Zsh                   |

**Go sub-detection**: If `main.go` exists at the root or a `cmd/` directory exists, classify as **Go CLI**. Otherwise classify as **Go Library**.

**JS/TS sub-detection**: Determine the package manager from lockfiles:

- `package-lock.json` = npm
- `yarn.lock` or `.yarnrc.yml` = yarn
- `pnpm-lock.yaml` = pnpm
- `bun.lock` = bun
- Default to npm if no lockfile found.

**Source file verification**: When `package.json` is detected, verify that actual JavaScript or TypeScript source files exist (`*.js`, `*.ts`, `*.jsx`, `*.tsx`, `*.mjs`, `*.mts`, excluding `node_modules/` and config files like `eslint.config.js`). A `package.json` used only for devDependencies (e.g., markdownlint tooling) does not make the project a JavaScript project. If no source files are found, skip JavaScript/TypeScript CI.

If multiple languages are detected, create a multi-language workflow with one job group per language. Present the detected languages to the user and confirm before proceeding.

If no language is detected, offer a generic workflow with `make test` and `make lint` targets.

### 2. Check for Existing CI

Look for existing CI files:

```bash
ls .github/workflows/ci.yml
ls .github/workflows/ci.yaml
ls .github/workflows/*.yml
```

If a CI workflow exists, present its contents and ask the user:

1. **Overwrite**: Replace the existing CI workflow entirely
1. **Merge**: Add missing jobs to the existing workflow (keep existing jobs intact)
1. **Abort**: Stop without changes

### 3. Check for Existing Makefile

If a `Makefile` exists, scan for existing CI-relevant targets:

```bash
grep -E '^(test|lint|fmt|vet|vuln|build|cover|coverage|tidy|tools|all|deny|audit|typos|changelog):' Makefile
```

Report which targets already exist and which will be added. Only add targets that do not already exist. Ask before modifying any existing target.

If no `Makefile` exists, offer to create one with the appropriate language-specific template from the Reference sections below. The Makefile provides standard targets for local development (`test`, `lint`, `fmt`, `vuln`, etc.) and is required by the Go CI reusable workflow (`go-ci.yml@v2`), which calls Makefile targets (`make test`, `make vet`, `make fmt`, etc.) directly. If the user declines, note that CI will fail for Go templates because the reusable workflow requires Makefile targets.

### 4. Create CI Workflow

Generate `.github/workflows/ci.yml` from the appropriate language template in the Reference sections below. Write the file using the Write tool. The `.github/workflows/` directory will be created automatically if it does not exist.

Go, Rust, Zig, Shell, and secret scanning templates use `cboone/gh-actions` reusable workflows that handle tool installation, caching, and execution internally. Other language templates use inline jobs.

All templates share:

- Triggers: push to `main`, pull requests targeting `main`
- `paths-ignore` for documentation and agent configuration changes
- Concurrency groups to cancel in-progress runs on the same branch/PR
- `permissions: contents: read`
- `actions/checkout@v6` (in inline jobs) or handled by reusable workflows

#### Runner Usage Notes

The `paths-ignore` patterns skip CI for changes that do not affect build or test outcomes:

- `*.md` matches root-level Markdown only (README, CONTRIBUTING, etc.). Nested `.md` files such as Scrut CLI tests in `tests/scrut/` are NOT ignored, so CI still runs when test files change.
- `docs/**` skips documentation directory changes.
- `.claude/**`, `**/CLAUDE.md`, `**/AGENTS.md` skip AI agent configuration files.
- `LICENSE` and `.editorconfig` skip non-code metadata.

**When to adjust**: Remove `*.md` from `paths-ignore` if your project treats Markdown files as source code (e.g., documentation-focused projects where Markdown linting is a CI step). Remove `docs/**` if your docs directory contains generated API references that should trigger CI.

The concurrency group cancels in-progress CI runs when new commits are pushed to the same branch or PR. This prevents wasted minutes on superseded commits.

For multi-language projects, combine language-specific jobs into a single workflow file using the multi-language pattern from the Reference section.

### 5. Create or Update Makefile Targets

Add missing targets from the appropriate Makefile template in the Reference sections below. Include both targets that the CI workflow references directly (e.g., `make test`, `make vet`) and standard local-development targets (`test`, `lint`, `fmt`, `vuln`, etc.) even when the CI workflow runs equivalent commands directly rather than via `make`.

Rules:

- Only add targets that do not already exist in the Makefile
- Ask before modifying existing targets
- If creating a new Makefile, include a `help` target
- Preserve any existing Makefile content (append new targets at the end)

### 6. Summary

Print a summary of what was created or modified:

- List every file created or modified
- Suggest complementary plugins:
  - `/setup-secret-scanning` for secret scanning
  - `/setup-linters` for linter configuration (if no linter configs detected)
  - `/add-scrut-cli-tests` for CLI snapshot testing (if CLI project detected)
  - `/add-goreleaser-homebrew` for release automation (if Go project detected)

## Error Handling

- **Not a git repo**: Warn the user, suggest `git init`, then continue (CI workflow files do not require a git repo to create, but will not trigger without one)
- **No language detected**: Offer a generic workflow with checkout + `make test` / `make lint` targets
- **Existing CI**: Ask before overwriting (covered in step 2)
- **Missing Makefile**: Offer to create one; if the user declines, note that CI may fail for language templates whose workflows reference `make` targets

---

## CI Workflow Templates

@${CLAUDE_PLUGIN_ROOT}/references/ci-go-cli.md

@${CLAUDE_PLUGIN_ROOT}/references/ci-go-library.md

@${CLAUDE_PLUGIN_ROOT}/references/ci-javascript.md

@${CLAUDE_PLUGIN_ROOT}/references/ci-python.md

@${CLAUDE_PLUGIN_ROOT}/references/ci-rust.md

@${CLAUDE_PLUGIN_ROOT}/references/ci-ruby.md

@${CLAUDE_PLUGIN_ROOT}/references/ci-shell.md

@${CLAUDE_PLUGIN_ROOT}/references/ci-zig.md

@${CLAUDE_PLUGIN_ROOT}/references/ci-zsh.md

@${CLAUDE_PLUGIN_ROOT}/references/ci-multi-language.md

## Makefile Templates

@${CLAUDE_PLUGIN_ROOT}/references/makefile-go-cli.md

@${CLAUDE_PLUGIN_ROOT}/references/makefile-go-library.md

@${CLAUDE_PLUGIN_ROOT}/references/makefile-javascript.md

@${CLAUDE_PLUGIN_ROOT}/references/makefile-python.md

@${CLAUDE_PLUGIN_ROOT}/references/makefile-rust.md

@${CLAUDE_PLUGIN_ROOT}/references/makefile-ruby.md

@${CLAUDE_PLUGIN_ROOT}/references/makefile-shell.md

@${CLAUDE_PLUGIN_ROOT}/references/makefile-zig.md

@${CLAUDE_PLUGIN_ROOT}/references/makefile-zsh.md
