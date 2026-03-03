# Optimize GitHub Actions Runner Usage

## Context

Private GitHub repos pay for Actions minutes, and macOS runners cost 10x Linux runners. This repository both runs its own CI and provides CI/release workflow templates to other projects via plugins. Optimizing the templates has a multiplier effect: every project scaffolded with these plugins benefits automatically.

Three categories of optimization apply:

1. **Path filtering**: Skip CI for docs-only changes (README, CHANGELOG, LICENSE, `docs/`)
1. **Concurrency groups**: Cancel in-progress runs when new commits are pushed, preventing wasted minutes on superseded commits
1. **Timeout limits**: Prevent runaway jobs from consuming minutes indefinitely

A fourth optimization, replacing macOS runners with Linux cross-compilation for Rust darwin release builds, is noted as a comment since it involves trade-offs.

## Changes

### 1. This repo's CI workflow

**File**: `.github/workflows/ci.yml`

Add concurrency group and timeout. Do NOT add `paths-ignore` because `.md` files are source code in this repository (SKILL.md files contain actual plugin logic, and markdown linting is a primary CI step).

```yaml
# Add after the on: block
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Add `timeout-minutes: 15` to the `ci` job.

### 2. Setup CI plugin (primary CI templates)

**File**: `plugins/setup-ci/commands/setup-ci.md`

This is the largest change. All 8 language templates get three additions.

**Shared description update** (around line 73): Add to the "All templates share:" list:

- `paths-ignore` for documentation-only changes
- Concurrency groups to cancel in-progress runs
- Timeout limits on all jobs

**Add a "Runner usage optimization" section** after the shared description explaining the three optimizations and when to adjust them. Notes to include:

- Remove `*.md` from `paths-ignore` if `.md` files are source code (e.g., documentation-focused projects)
- The `*.md` pattern only matches root-level files; scrut tests in `tests/scrut/*.md` (or other nested `.md` files) are NOT ignored, so CI still runs correctly when test files change
- `.claude/**`, `**/CLAUDE.md`, and `**/AGENTS.md` are ignored because AI agent configuration changes do not affect build or test outcomes

**Each template's `on:` block** changes from:

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

to:

```yaml
on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Scrut test caveat**: Projects with Scrut CLI tests store tests as `.md` files (typically in `tests/scrut/`). The `*.md` pattern only matches root-level markdown files, so `tests/scrut/*.md` is NOT ignored and CI still runs when scrut tests change. The runner optimization notes section should call this out explicitly so users understand the behavior is correct by default.

**Timeout values per job type**:

| Job type                        | Timeout |
| ------------------------------- | ------- |
| Test, lint, build, format       | 15 min  |
| Vulnerability check, shell lint | 10 min  |
| Rust build                      | 20 min  |

Templates affected: Go CLI, Go Library, JS/TS, Python, Rust, Ruby, Shell, Multi-Language (8 templates total).

### 3. Scaffold Go CLI plugin

**File**: `plugins/scaffold-go-cli/commands/scaffold-go-cli.md`

- CI template: same `paths-ignore`, `concurrency`, and `timeout-minutes` as setup-ci Go CLI template
- Release template (tag-triggered): add `concurrency` with `cancel-in-progress: false` (do not cancel in-progress releases) and `timeout-minutes: 30`; no `paths-ignore` (tags should always trigger releases)

### 4. Scaffold Go Library plugin

**File**: `plugins/scaffold-go-library/commands/scaffold-go-library.md`

Same treatment as scaffold-go-cli: CI template gets all three optimizations, release template gets concurrency (no cancel) and timeout only.

### 5. Setup Installers plugin (release workflows)

**File**: `plugins/setup-installers/commands/setup-installers.md`

Release workflows trigger on tags, so no `paths-ignore`. Add to each:

- **Go Release**: `concurrency` (cancel-in-progress: false), `timeout-minutes: 30` on build, `timeout-minutes: 10` on publish
- **Swift Release**: same concurrency and timeouts; add comment that macOS runner is required for Swift compilation
- **Rust Release**: same concurrency and timeouts; add comment noting that macOS runners cost 10x Linux and that `cargo-zigbuild` can cross-compile darwin targets on Linux for cost savings

### 6. GoReleaser + Homebrew plugin

**File**: `plugins/add-goreleaser-homebrew/commands/add-goreleaser-homebrew.md`

Release template: `concurrency` (cancel-in-progress: false), `timeout-minutes: 30`. No `paths-ignore`.

### 7. Setup Linters plugin (lint CI reference templates)

**File**: `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`

All per-language lint templates: add `paths-ignore`, `concurrency`, and `timeout-minutes: 15` (or 10 for shell). Add a note about runner optimization at the top of the file.

### 8. Secret Scanning plugin

**File**: `plugins/setup-secret-scanning/commands/setup-secret-scanning.md`

No `paths-ignore` (secrets can appear in any file, including docs). Add `concurrency` and `timeout-minutes: 15` to both gitleaks templates and the TruffleHog template.

### 9. Scrut CLI Tests plugin

**File**: `plugins/add-scrut-cli-tests/commands/add-scrut-cli-tests.md`

Job template only (no standalone `on:` trigger): add `timeout-minutes: 15`.

### 10. Version bumps

Each modified plugin gets a patch version bump in both `plugin.json` and `marketplace.json`. No marketplace metadata version change (no plugins added or removed).

Plugins requiring version bumps:

- setup-ci
- scaffold-go-cli
- scaffold-go-library
- setup-installers
- add-goreleaser-homebrew
- setup-linters
- setup-secret-scanning
- add-scrut-cli-tests

## Implementation order

1. `.github/workflows/ci.yml` (this repo, simplest, immediately verifiable)
1. `plugins/setup-ci/commands/setup-ci.md` (largest, sets the pattern)
1. `plugins/scaffold-go-cli/commands/scaffold-go-cli.md`
1. `plugins/scaffold-go-library/commands/scaffold-go-library.md`
1. `plugins/setup-installers/commands/setup-installers.md`
1. `plugins/add-goreleaser-homebrew/commands/add-goreleaser-homebrew.md`
1. `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`
1. `plugins/setup-secret-scanning/commands/setup-secret-scanning.md`
1. `plugins/add-scrut-cli-tests/commands/add-scrut-cli-tests.md`
1. Version bumps (all plugin.json + marketplace.json entries)

## Verification

1. Run the repo's CI locally: `yarn lint`, `shellcheck`, `shfmt -d`, `bin/validate-json`, `bin/validate-plugins`
1. Verify YAML syntax within all modified markdown code blocks (actionlint will catch workflow errors)
1. Use `check-versions` skill to verify version consistency
1. Push the branch and confirm CI passes
