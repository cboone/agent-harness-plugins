---
name: refresh-project-scaffolding
description: >-
  Refresh existing project scaffolding against the latest plugin templates.
---

# Refresh Project Scaffolding

Refresh the current repository's existing scaffolding against the latest templates and best practices from the agent-harness-plugins ecosystem. Detect which tools have been used, compare existing files against current standards, present a plan of what's out of date, confirm with the user, and apply targeted updates.

This is the maintenance companion to `bootstrap-project`: bootstrap sets things up, this keeps them current.

**Scope**: This skill audits tools already in use and updates their files to match current templates. For tools that are partially configured, it can restore missing expected files. It does not set up tools that were never used; for initial setup, use the bootstrap-project skill or the individual tool.

## Workflow

### 1. Detect Project Type

Scan for language and framework markers using Glob. Exclude `node_modules/`, `.yarn/`, `vendor/`, and other dependency directories from all searches.

| Marker(s)                                        | Project type          |
| ------------------------------------------------ | --------------------- |
| `go.mod` + (`main.go` or `cmd/`)                 | Go CLI                |
| `go.mod` without `main.go` or `cmd/`             | Go library            |
| `package.json` + JS/TS source files              | JavaScript/TypeScript |
| `pyproject.toml`, `setup.py`, `requirements.txt` | Python                |
| `Cargo.toml`                                     | Rust                  |
| `Gemfile`, `*.gemspec`                           | Ruby                  |
| `Package.swift`                                  | Swift                 |
| `*.sh`, `bin/*`, `scripts/*`                     | Shell                 |

If multiple types are detected (monorepo), note all of them.

### 2. Detect Which Tools Have Been Used

For each tool in the ecosystem, check for its signature artifacts. Only tools whose artifacts are found will be audited.

| Tool                      | Signature artifacts                                                       |
| ------------------------- | ------------------------------------------------------------------------- |
| `scaffold-new-repo`       | `LICENSE` + `README.md` + `.gitignore`                                    |
| `scaffold-go-cli`         | `go.mod` + `cmd/` + `.goreleaser.yml` + `.github/workflows/release.yml`   |
| `scaffold-go-library`     | `go.mod` (no `cmd/`) + `.golangci.yml` + `.github/workflows/ci.yml`       |
| `set-up-ci`               | `.github/workflows/ci.yml`                                                |
| `set-up-linters`          | `.editorconfig` or `.prettierrc.json` or `.golangci.yml`                  |
| `set-up-secret-scanning`  | `.github/workflows/gitleaks.yml` or `.github/workflows/trufflehog.yml`    |
| `add-goreleaser-homebrew` | `.goreleaser.yml` with `brews:` section + `.github/workflows/release.yml` |
| `add-community-files`     | `CONTRIBUTING.md` + `CODE_OF_CONDUCT.md`                                  |
| `add-scrut-cli-tests`     | `tests/scrut/` directory                                                  |
| `set-up-installers`       | `Formula/`                                                                |
| `optimize-runner-usage`   | `concurrency:` key in any `.github/workflows/*.yml`                       |
| `clean-up-agent-config`   | `AGENTS.md` or (`CLAUDE.md` + `.claude/settings.json`)                    |

For each detected tool, record which artifacts were found and which expected artifacts are missing (for "Partially set up" status).

### 3. Compare Against Latest Templates

For each detected tool, run through its checklist from the Reference sections at the bottom of this file. Read the target repo's files and check for the specified patterns.

For each failed check, record:

- The file path
- What's wrong (concise description)
- The recommended fix

Use Grep and Read to check file contents. Check action versions against the **Reference: Action Versions** table.

### 4. Build and Present the Update Plan

Present a table with all detected tools and their status:

```text
| # | Tool                    | Status         | Issues Found                                   | Action          |
|---|-------------------------|----------------|-------------------------------------------------|-----------------|
| 1 | set-up-ci               | Needs update   | actions/checkout@v4 (target: v6), no timeout    | Update workflow |
| 2 | set-up-linters          | Up to date     |                                                 | None            |
| 3 | set-up-secret-scanning  | Partially set  | TruffleHog workflow missing                     | Add workflow    |
| 4 | add-community-files     | Needs update   | CoC is v2.1 (current: v3.0)                     | Update CoC      |
| 5 | clean-up-agent-config   | Needs update   | CLAUDE.md is regular file, not symlink           | Convert to symlink |
| 6 | optimize-runner-usage   | Up to date     |                                                 | None            |
| 7 | scaffold-new-repo       | Needs update   | .gitignore missing .claude/settings.local.json   | Update file     |
| 8 | add-goreleaser-homebrew | Up to date     |                                                 | None            |
```

Status values:

| Status           | Meaning                                                               |
| ---------------- | --------------------------------------------------------------------- |
| Up to date       | All checks pass; nothing to do                                        |
| Needs update     | Files exist but fail some checks                                      |
| Partially set up | Some expected files from a detected tool are missing entirely         |
| Not detected     | Tool was never used (run bootstrap-project or the individual skill)   |
| Not applicable   | Tool does not apply to this project type                              |

Items with status "Not detected" and "Not applicable" are informational only and are not actionable in this command.

### 5. User Confirmation

Ask the user which items to update. Only items with status "Needs update" or "Partially set up" are actionable. Present them as a numbered list and let the user:

- Confirm all actionable items
- Select specific items by number
- Skip specific items

If no items need updating (everything is up to date), congratulate the user and stop.

### 6. Execute Updates

For each confirmed update item, choose a strategy based on scope:

| Scenario                                       | Strategy                                                                             |
| ---------------------------------------------- | ------------------------------------------------------------------------------------ |
| Action version outdated                        | **Targeted**: find and replace the version string in the workflow file               |
| Missing config entry (e.g., .gitignore line)   | **Targeted**: add the missing entry to the appropriate section                       |
| Missing workflow key (e.g., `timeout-minutes`) | **Targeted**: add the key to each job in the workflow file                           |
| Missing `concurrency:` group                   | **Targeted**: add the concurrency block below the `on:` trigger block                |
| Missing `permissions:` block                   | **Targeted**: add the permissions block at the workflow level                        |
| CLAUDE.md is regular file, not symlink         | **Full re-run**: invoke `clean-up-agent-config` to reconcile CLAUDE.md and AGENTS.md |
| Community file outdated (e.g., CoC version)    | **Full re-run**: invoke the `add-community-files` skill via the Skill tool           |
| Missing file from a detected tool              | **Full re-run**: invoke the original skill via the Skill tool                        |

For full tool re-runs, all detected tools are skills. Invoke them via the Skill tool. Relevant skills include `add-community-files`, `set-up-linters`, `set-up-ci`, `set-up-secret-scanning`, `add-goreleaser-homebrew`, `set-up-installers`, `add-scrut-cli-tests`, `scaffold-new-repo`, and `optimize-runner-usage`.

Process updates in this order (matching the bootstrap-project execution order):

1. `scaffold-new-repo` (foundation files)
1. `scaffold-go-cli` / `scaffold-go-library` (language scaffold)
1. `set-up-ci` (CI workflow)
1. `set-up-linters` (linter configs)
1. `set-up-secret-scanning` (secret scanning)
1. `add-goreleaser-homebrew` (release config)
1. `add-community-files` (community files)
1. `set-up-installers` (distribution)
1. `add-scrut-cli-tests` (testing)
1. `optimize-runner-usage` (CI optimization)
1. `clean-up-agent-config` (agent config)

After each update, verify the change was applied correctly. If an update fails, report the error and ask whether to continue with remaining items or stop.

### 7. Summary

Print a summary grouped by outcome:

- **Updated**: list each change made, grouped by tool
- **Skipped**: items the user chose not to update
- **Already up to date**: tools that passed all checks
- **Errors**: any issues encountered during updates

Suggest next steps:

- Run `/lint-and-fix` to check formatting of updated files
- Commit the changes
- Push and verify CI passes

---

## Reference: Action Versions

The target versions for GitHub Actions that repositories should be updated to. When auditing workflow files, check `uses:` lines against this table. Actions not listed in this table are outside the scope of this audit and should be skipped without flagging.

| Action                          | Target version |
| ------------------------------- | -------------- |
| `actions/checkout`              | `v6`           |
| `actions/download-artifact`     | `v8`           |
| `actions/setup-go`              | `v6`           |
| `actions/setup-node`            | `v6`           |
| `actions/upload-artifact`       | `v7`           |
| `astral-sh/setup-uv`            | `v8`           |
| `dtolnay/rust-toolchain`        | `stable`       |
| `gitleaks/gitleaks-action`      | `v2`           |
| `golangci/golangci-lint-action` | `v9`           |
| `goreleaser/goreleaser-action`  | `v7`           |
| `ludeeus/action-shellcheck`     | `2.0.0`        |
| `mfinelli/setup-shfmt`          | `v4`           |
| `oven-sh/setup-bun`             | `v2`           |
| `ruby/setup-ruby`               | `v1`           |
| `Swatinem/rust-cache`           | `v2`           |
| `trufflesecurity/trufflehog`    | `v3`           |

When auditing, treat SHA-pinned references (e.g., `actions/checkout@a5ac7e5...`) as compliant if the pinned commit corresponds to the listed version or newer. Do not downgrade SHA pins to mutable version tags.

<!-- Maintenance: update this table when any command template changes its action versions. -->

## Reference: CI Workflow Checks (set-up-ci)

### Files

- `.github/workflows/ci.yml`
- `Makefile`

### Checks for ci.yml

- All `uses:` references match the Action Versions table above
- Has a top-level `permissions:` block (typically `contents: read`)
- Has a `concurrency:` block with `group: ${{ github.workflow }}-${{ github.ref }}` and `cancel-in-progress: true`
- Every job has `timeout-minutes:` set (typically 15 for test/lint, 10 for format/vuln)
- Has `paths-ignore:` on push and pull_request triggers with the standard list (see Reference: Standard paths-ignore)
- Go projects: uses `go-version-file: go.mod` instead of a pinned Go version
- Go libraries: has a multi-version test matrix (minimum + stable)
- JS/TS projects: detects package manager from lockfile and uses the correct install command

### Checks for Makefile

- Has `.PHONY:` declarations
- Has a `help` target
- Go CLI targets: build, test, lint, vet, fmt, vuln, clean, cover, tidy
- Go library targets: all, build, test, lint, vet, fmt, vuln, clean, coverage, tools
- JS/TS targets: test, lint, fmt (or format)
- Python targets: test, lint, fmt
- Rust targets: test, lint, fmt, build, clean
- Ruby targets: test, lint
- Shell targets: lint, fmt

## Reference: Secret Scanning Checks (set-up-secret-scanning)

### Files

- `.github/workflows/gitleaks.yml`
- `.github/workflows/trufflehog.yml`
- `.gitleaks.toml`

### Checks for gitleaks.yml

- Uses `cboone/gh-actions/.github/workflows/scan-for-secrets.yml` with a refreshed SHA-pinned ref and current version comment
- Sets `tool: gitleaks`
- Has `permissions:` block with `contents: read`
- Has `concurrency:` group with `group: ${{ github.workflow }}-${{ github.ref }}` and `cancel-in-progress: true`
- Triggers on `push: branches: [main]`
- Has `pull_request:` trigger
- Has `workflow_dispatch:` trigger
- The reusable workflow handles checkout with `fetch-depth: 0` and tool installation internally

### Checks for trufflehog.yml

- Uses `cboone/gh-actions/.github/workflows/scan-for-secrets.yml` with a refreshed SHA-pinned ref and current version comment
- Sets `tool: trufflehog`
- Has `permissions:` block with `contents: read`
- Triggers on `push: branches: [main]`
- Has `pull_request:` trigger
- Has `workflow_dispatch:` trigger
- Has `concurrency:` group with `group: ${{ github.workflow }}-${{ github.ref }}` and `cancel-in-progress: true`
- The reusable workflow handles checkout with `fetch-depth: 0`, TruffleHog version pinning, and tool execution internally

### Checks for .gitleaks.toml

- Has `[allowlist]` section
- Includes lockfile patterns relevant to the detected project type (`go.sum` for Go, `package-lock.json` for JS, etc.)

## Reference: Foundation File Checks (scaffold-new-repo)

### Files

- `LICENSE`
- `README.md`
- `CHANGELOG.md`
- `.gitignore`
- `AGENTS.md`
- `CLAUDE.md`
- `.claude/settings.json`
- `.github/copilot-instructions.md`

### Checks for LICENSE

- Contains "MIT License" text
- Copyright year includes the current year (or is a range ending in the current year)

### Checks for .gitignore

Must include these universal entries:

```text
.DS_Store
.claude/settings.local.json
.env
.env.*
!.env.example
!.env.sample
*.pem
*.key
*.p12
credentials.json
token.json
```

Must include language-specific entries appropriate for the detected project type:

- **Go**: `*.exe`, `*.test`, `*.out`, `coverage.*`, `go.work`, `go.work.sum`, `bin/`, `dist/`
- **JavaScript**: `node_modules/`, `coverage/`, `dist/`, `*.log`
- **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `dist/`, `build/`
- **Rust**: `target/`
- **Ruby**: `*.gem`, `.bundle/`, `vendor/bundle`, `pkg/`

### Checks for agent config

- `CLAUDE.md` is a symlink pointing to `AGENTS.md` (run `readlink CLAUDE.md` to verify)
- `.claude/settings.json` exists
- `.github/copilot-instructions.md` exists and references `AGENTS.md`
- `.claude/settings.local.json` is listed in `.gitignore`

## Reference: Linter Config Checks (set-up-linters)

### Files

- `.editorconfig`
- `.prettierrc.json`
- `.prettierignore`
- `.markdownlint-cli2.jsonc` (or `.markdownlint-cli2.yaml`, `.markdownlint.json`, `.markdownlint.jsonc`, `.markdownlint.yaml`)
- Language-specific linter configs (`.golangci.yml`, `.shellcheckrc`, etc.)

### Checks for .editorconfig

- Has `root = true` at the top
- Has base settings: `charset = utf-8`, `end_of_line = lf`, `insert_final_newline = true`, `trim_trailing_whitespace = true`
- Go projects: has `[*.go]` section with `indent_style = tab`
- Python/Rust projects: has language section with `indent_size = 4`
- Has `[Makefile]` section with `indent_style = tab` (if Makefile exists)
- Has `[*.md]` section with `trim_trailing_whitespace = false`
- Shell projects: has shfmt properties (`binary_next_line`, `space_redirects`, `switch_case_indent`)

### Checks for .prettierrc.json

- Has `printWidth` set to `10000` (not the default 80)
- Has `proseWrap` set to `"preserve"`
- Has `tabWidth` set to `2`
- JS projects: has `semi: false`, `singleQuote: true`, `trailingComma: "all"`

### Checks for .prettierignore

- Exists (if `.prettierrc.json` exists)
- Includes `node_modules/` and build output directories

### Checks for markdownlint config

- Config file exists (any supported name)
- `MD013` is set to `false` (Prettier handles line length)
- `MD033` is set to `false` (allow inline HTML)
- `MD034` is set to `false` (allow bare URLs)
- Ignores list includes `CHANGELOG.md`
- Scrut projects: `MD014` is set to `false` (allow dollar signs before commands)

## Reference: Community File Checks (add-community-files)

### Files

- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `.github/SECURITY.md`
- `.github/PULL_REQUEST_TEMPLATE.md`

### Checks for CODE_OF_CONDUCT.md

- Contains "Contributor Covenant" attribution
- References version 3.0 (check for `version/3/0` in the URL or "version 3.0" in text)
- If it references an older version (1.4, 2.0, 2.1), flag as outdated
- Has 4-tier enforcement ladder (Warning, Temporarily Limited Activities, Temporary Suspension, Permanent Ban)

### Checks for CONTRIBUTING.md

- Has a Development Setup section with build/test/lint commands
- Commands match the project's actual build system (check against Makefile targets or package.json scripts)
- Has a Commit Messages section referencing Conventional Commits
- Has a Pull Request Process section with branch naming conventions

### Checks for .github/SECURITY.md

- Instructs users to use GitHub private vulnerability reporting (not public issues)
- Has response timeline (24h acknowledgment, 48h assessment)

### Checks for .github/PULL_REQUEST_TEMPLATE.md

- Exists
- Has a checklist with at least: tests pass, style followed, documentation updated

## Reference: GoReleaser Checks (add-goreleaser-homebrew)

### Files

- `.goreleaser.yml`
- `.github/workflows/release.yml`

### Checks for release.yml

- Uses `cboone/gh-actions/.github/workflows/release-go-binaries.yml` with a refreshed SHA-pinned ref and current version comment
- Go CLI releases pass `go-version-file: go.mod`
- Triggers on `push: tags: ["v*"]`
- Has `permissions: contents: write`
- Has `concurrency:` group with `group: ${{ github.repository }}-${{ github.workflow }}` and `cancel-in-progress: false` (never interrupt releases)
- The reusable workflow handles checkout with `fetch-depth: 0`, Go setup, GoReleaser installation, and release execution internally

### Checks for .goreleaser.yml

- Has `version: 2` (GoReleaser v2 config format)
- Has `changelog:` section with `use: github` or grouped categories

## Reference: Runner Optimization Checks (optimize-runner-usage)

### Files

- All `.github/workflows/*.yml` files

### Checks for each workflow

- Has `concurrency:` block (pattern depends on workflow type, see below)
- Every job has `timeout-minutes:` set
- CI workflows: has `paths-ignore:` on push/pull_request triggers

### Concurrency patterns by workflow type

| Workflow type           | Concurrency group pattern                         | cancel-in-progress |
| ----------------------- | ------------------------------------------------- | ------------------ |
| CI                      | `${{ github.workflow }}-${{ github.ref }}`        | `true`             |
| Release                 | `${{ github.repository }}-${{ github.workflow }}` | `false`            |
| Secret scanning         | `${{ github.workflow }}-${{ github.ref }}`        | `true`             |
| Scheduled               | `${{ github.workflow }}-${{ github.ref }}`        | `true`             |
| Mixed (branches + tags) | `${{ github.workflow }}-${{ github.ref }}`        | `false`            |

### Timeout guidelines

| Job type            | Recommended timeout |
| ------------------- | ------------------- |
| Release/publish     | 30 minutes          |
| Rust builds         | 20 minutes          |
| Test/lint (general) | 15 minutes          |
| Format/vuln check   | 10 minutes          |

### Do NOT apply paths-ignore to

- Release workflows
- Mixed-trigger workflows (branches + tags)
- Scheduled workflows
- Secret scanning workflows
- Workflows with existing `paths:` positive filters
- Reusable workflows

## Reference: Agent Config Checks (clean-up-agent-config)

### Files

- `AGENTS.md`
- `CLAUDE.md`
- `.claude/settings.json`
- `.claude/settings.local.json`
- `.claude/rules/*.md`
- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`

### Checks

- `AGENTS.md` exists and is the canonical instruction file (not a symlink)
- `CLAUDE.md` is a symlink pointing to `AGENTS.md` (verify with `readlink`)
- If `CLAUDE.md` is a regular file and `AGENTS.md` also exists, flag the duplication
- `.claude/settings.json` exists and contains only team-shared settings (permissions, hooks, env vars for conventions)
- `.claude/settings.local.json` is gitignored (check `.gitignore` for the entry)
- `.github/copilot-instructions.md` cross-references `AGENTS.md`
- `.github/instructions/*.instructions.md` files have `applyTo:` frontmatter

## Reference: Scrut Test Checks (add-scrut-cli-tests)

### Files

- `tests/scrut/` directory
- `Makefile` (for scrut targets)
- `.github/workflows/ci.yml` (for scrut CI job)

### Checks

- `tests/scrut/` directory exists and contains `.md` test files
- `Makefile` has `test-scrut` and `test-scrut-update` targets
- `Makefile` has `test-all` target that depends on both `test` and `test-scrut`
- CI workflow has a job or step that installs and runs scrut
- If markdownlint config exists: `MD014` is set to `false`

## Reference: Installer Checks (set-up-installers)

### Files

- `Formula/*.rb`

### Checks for Formula/\*.rb

- Has `desc` field
- Has `homepage` field
- Has platform-specific blocks (`on_macos`/`on_linux` or `depends_on :macos`)

## Reference: Standard paths-ignore

The standard `paths-ignore` list for CI workflow push and pull_request triggers:

```yaml
paths-ignore:
  - "*.md"
  - "docs/**"
  - "LICENSE"
  - ".editorconfig"
  - ".claude/**"
  - "**/CLAUDE.md"
  - "**/AGENTS.md"
```

Note: `tests/scrut/*.md` files are source code and should NOT be ignored. If the project uses scrut tests, verify that the paths-ignore pattern does not exclude nested `.md` files (the `"*.md"` pattern only matches root-level files).

<!-- Maintenance: when any plugin template changes, update the corresponding Reference section above. -->
