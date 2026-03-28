# Update Plugins to Use Reusable Workflows

## Context

Issue #225 requests updating plugins to use Rust and scrut reusable workflows from `cboone/gh-actions`. The scope expands to include all recently added reusable workflows (Zig CI, Zig release, Rust release, standalone scrut). The Go and Shell migrations (PR #197, plan at `docs/plans/done/2026-03-09-migrate-to-gh-actions-reusable-workflows.md`) established the pattern: replace inline multi-job YAML templates with single `uses:` calls to reusable workflows. This plan follows that same pattern.

Available reusable workflows in `cboone/gh-actions` (latest release: v2.1.0, floating tags: v1, v2):

- `rust-ci.yml` -- test (nextest), lint (clippy), format, deny, audit, typos, coverage
- `rust-release.yml` -- cross-platform binary builds + GitHub release
- `zig-ci.yml` -- test, format, build, cross-compile, scrut
- `zig-release.yml` -- cross-platform binary packaging + GitHub release
- `scrut.yml` -- standalone scrut testing with SHA-256 checksum verification
- `go-ci.yml`, `go-release.yml`, `shell-lint.yml`, `text-lint.yml`, `github-lint.yml` -- already referenced

## Design Decisions

1. **Rust CI: 7 inline jobs to one call.** `rust-ci.yml` enables all checks by default (test, lint, format, deny, audit, typos), so no `with:` inputs needed. The separate `build` job is removed because `cargo nextest run` compiles implicitly. Notes section documents this tradeoff.

2. **Rust macOS-only variant uses `runs-on: macos-latest` input** rather than duplicating the entire workflow.

3. **Rust Release: build matrix to one call.** `rust-release.yml` accepts `binary-name` (required) and handles cross-compilation, checksums, and GitHub release creation. macOS-only variant constrains `targets`.

4. **Zig CI: 4 inline jobs to one call.** `zig-ci.yml` requires explicit `zig-version` input (unlike the inline template that relied on `mlugg/setup-zig@v2` reading `build.zig.zon`). Notes explain users must keep this in sync.

5. **Scrut CI: inline installation to reusable workflow.** The `scrut.yml` reusable workflow handles installation with SHA-256 checksum verification (the current inline template explicitly notes checksums are "not yet possible"). Uses `scrut-setup-cmd` for the build step and `scrut-env` for the binary path.

6. **Version tag: @v2 for all new references.** Consistent with existing Go workflow references.

## Changes

### 1. lint-and-fix (1.3.2 -> 1.3.3, patch)

**`plugins/lint-and-fix/skills/lint-and-fix/SKILL.md`**

- Line 64: Expand reusable workflow skip example to include `rust-ci.yml@v2` and `zig-ci.yml@v2` alongside `go-ci.yml@v2`
- Line 221: Same expansion in error handling section

**`plugins/lint-and-fix/.claude-plugin/plugin.json`** -- bump to 1.3.3

### 2. add-scrut-cli-tests (1.4.0 -> 1.5.0, minor)

**`plugins/add-scrut-cli-tests/commands/add-scrut-cli-tests.md`**

- Replace "Reference: CI Job" section (lines ~326-379): swap the inline job template with a `scrut.yml@v2` reusable workflow call
- New template structure:

  ```yaml
  test-scrut:
    uses: cboone/gh-actions/.github/workflows/scrut.yml@v2
    with:
      scrut-setup-cmd: "make build"
      scrut-env: "TOOL_BIN=BINARY_PATH"
  ```

- Update Placeholders table: remove `RUNNER_OS`, `LANGUAGE_SETUP_STEPS`, `SCRUT_VERSION`, `SCRUT_PLATFORM`; keep `TOOL_BIN`, `BINARY_PATH`; add `scrut-setup-cmd` and `scrut-env` descriptions
- Rewrite Notes: remove manual installation discussion and checksum unavailability note; add that the reusable workflow handles installation with SHA-256 verification, and that `scrut-setup-cmd` is the build command (omit for interpreted languages)
- Update step 6 prose to reference the reusable workflow pattern
- Local installation instructions (step 7) remain unchanged

**`plugins/add-scrut-cli-tests/.claude-plugin/plugin.json`** -- bump to 1.5.0

### 3. setup-ci Rust template (1.6.0 -> 1.7.0, minor)

**`plugins/setup-ci/references/ci-rust.md`**

- Replace 150-line inline 7-job template with:

  ```yaml
  jobs:
    ci:
      uses: cboone/gh-actions/.github/workflows/rust-ci.yml@v2
  ```

- Keep `on:`, `concurrency:`, `permissions:` blocks (same pattern as `ci-go-cli.md`)
- Rewrite Notes: explain parallel jobs are created internally, no separate build job, remove third-party action references
- Simplify macOS-only section to show `runs-on: macos-latest` input

### 4. setup-ci Zig template

**`plugins/setup-ci/references/ci-zig.md`**

- Replace 108-line inline 4-job template with:

  ```yaml
  jobs:
    ci:
      uses: cboone/gh-actions/.github/workflows/zig-ci.yml@v2
      with:
        zig-version: "0.14.0"
  ```

- Rewrite Notes: explain `zig-version` is required, parallel jobs created internally, `run-scrut` input available
- Remove `mlugg/setup-zig@v2` references

### 5. setup-ci multi-language and command prose

**`plugins/setup-ci/references/ci-multi-language.md`**

- Expand example to show Go + Rust + JS (three-language combo with two reusable + one inline)
- Update Notes to list Go, Rust, and Zig as reusable workflow options

**`plugins/setup-ci/commands/setup-ci.md`**

- Line 79: Change "Go, Shell, and secret scanning" to "Go, Rust, Zig, Shell, and secret scanning"

**`plugins/setup-ci/.claude-plugin/plugin.json`** -- bump to 1.7.0

### 6. scaffold-rust-cli CI templates (1.0.0 -> 1.1.0, minor)

**`plugins/scaffold-rust-cli/references/ci-workflow.md`**

- Replace 150-line inline template with `rust-ci.yml@v2` call (same as setup-ci)

**`plugins/scaffold-rust-cli/references/ci-workflow-macos-only.md`**

- Replace inline template with `rust-ci.yml@v2` call using `runs-on: macos-latest`

### 7. scaffold-rust-cli release templates

**`plugins/scaffold-rust-cli/references/release-workflow.md`**

- Replace ~96-line inline build matrix + publish with:

  ```yaml
  jobs:
    release:
      uses: cboone/gh-actions/.github/workflows/rust-release.yml@v2
      with:
        binary-name: PROJECT-NAME
  ```

- Keep `on:` (tag trigger), `concurrency:`, `permissions: contents: write`

**`plugins/scaffold-rust-cli/references/release-workflow-macos-only.md`**

- Same, constraining targets to macOS only

**`plugins/scaffold-rust-cli/.claude-plugin/plugin.json`** -- bump to 1.1.0

### 8. setup-linters (1.8.0 -> 1.9.0, minor)

**`plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`**

- Rust section (lines 155-210): Replace inline clippy/rustfmt/deny/typos job with `rust-ci.yml@v2` example (with `run-test: false` for lint-only usage)
- Combined Multi-Language Workflow (lines 492-545): Add Rust and Zig reusable workflow examples
- Notes (line 562): Update "Go and Shell templates" to include Rust and Zig

**`plugins/setup-linters/.claude-plugin/plugin.json`** -- bump to 1.9.0

### 9. Version bumps

**`.claude-plugin/marketplace.json`** -- update versions for all 5 plugins:

| Plugin              | Current | New   |
| ------------------- | ------- | ----- |
| setup-ci            | 1.6.0   | 1.7.0 |
| add-scrut-cli-tests | 1.4.0   | 1.5.0 |
| setup-linters       | 1.8.0   | 1.9.0 |
| lint-and-fix        | 1.3.2   | 1.3.3 |
| scaffold-rust-cli   | 1.0.0   | 1.1.0 |

`metadata.version` stays at 1.26.0 (no plugins added or removed).

## Commit Strategy

One commit per logical change, `feat(<scope>):` prefix:

1. `feat(lint-and-fix): add Rust and Zig to reusable workflow skip examples (#225)`
2. `feat(add-scrut-cli-tests): use scrut.yml reusable workflow for CI job template (#225)`
3. `feat(setup-ci): use rust-ci.yml reusable workflow for Rust CI template (#225)`
4. `feat(setup-ci): use zig-ci.yml reusable workflow for Zig CI template (#225)`
5. `feat(setup-ci): add Rust and Zig to multi-language template and command prose (#225)`
6. `feat(scaffold-rust-cli): use rust-ci.yml reusable workflow for CI templates (#225)`
7. `feat(scaffold-rust-cli): use rust-release.yml reusable workflow for release templates (#225)`
8. `feat(setup-linters): update Rust and multi-language sections with reusable workflows (#225)`
9. `chore: bump versions for reusable workflow migration (#225)`

## Verification

1. Run `check-versions` skill to verify version consistency
2. Grep for eliminated action references to confirm none remain in migrated templates: `dtolnay/rust-toolchain` (in Rust CI templates), `mlugg/setup-zig` (in Zig template), `gh release download.*scrut` (in scrut template)
3. Verify each modified template produces valid YAML
4. Confirm `on:`, `concurrency:`, and `permissions:` blocks preserved in all calling workflows
5. Verify Makefile templates are NOT modified (local development, unchanged)

## Files Modified

- `plugins/lint-and-fix/skills/lint-and-fix/SKILL.md`
- `plugins/lint-and-fix/.claude-plugin/plugin.json`
- `plugins/add-scrut-cli-tests/commands/add-scrut-cli-tests.md`
- `plugins/add-scrut-cli-tests/.claude-plugin/plugin.json`
- `plugins/setup-ci/references/ci-rust.md`
- `plugins/setup-ci/references/ci-zig.md`
- `plugins/setup-ci/references/ci-multi-language.md`
- `plugins/setup-ci/commands/setup-ci.md`
- `plugins/setup-ci/.claude-plugin/plugin.json`
- `plugins/scaffold-rust-cli/references/ci-workflow.md`
- `plugins/scaffold-rust-cli/references/ci-workflow-macos-only.md`
- `plugins/scaffold-rust-cli/references/release-workflow.md`
- `plugins/scaffold-rust-cli/references/release-workflow-macos-only.md`
- `plugins/scaffold-rust-cli/.claude-plugin/plugin.json`
- `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`
- `plugins/setup-linters/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
