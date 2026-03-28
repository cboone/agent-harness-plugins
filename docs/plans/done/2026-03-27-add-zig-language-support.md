# Plan: Add Zig Language Support Across Plugin Ecosystem

**Issue**: #223
**Branch**: `feature/add-zig-support`
**Classification**: feature (`feat`)

## Context

Zig is absent from all detection tables, templates, and reference files across the plugin ecosystem. During a recent bootstrap of a Zig CLI project ([cboone/seine](https://github.com/cboone/seine)), all Zig-specific setup had to be done manually. This plan adds native Zig support to 6 plugins, following the suggested implementation order from the issue.

**Detection marker**: `build.zig` or `build.zig.zon` (present in every Zig project, analogous to `Cargo.toml` for Rust).

**Closest analog**: Rust (compiled, cross-compilation, binary distribution, built-in formatter, build output directory).

**Key differences from Rust**: Simpler cross-compilation (single runner, no extra toolchains), no separate linter (no Clippy equivalent), different build system (`build.zig` is Zig code, not TOML).

## Changes

### 1. scaffold-new-repo (3 files modified)

**`plugins/scaffold-new-repo/commands/scaffold-new-repo.md`**:

- Add `zig-cli` to the valid types list (line 15, alongside existing types)
- Add `.gitignore` detection heuristic: `.zig-cache/` or `zig-out/` -> Zig (insert before the `target/` -> Rust rule, since `target/` is a weaker signal)
- Add `Zig CLI` to the project type options list

**`plugins/scaffold-new-repo/references/gitignore-templates.md`**:

- Add a `## Zig CLI` section with template (between Rust and Swift, or at the end before Generic):
  - Common entries (same as all templates)
  - Zig-specific: `.zig-cache/`, `zig-out/`, `*.o`, `*.d`, `*.pdb`

**`plugins/scaffold-new-repo/references/readme.md`**:

- Add a `### Zig CLI` installation placeholder section:

````markdown
```bash
git clone https://github.com/GITHUB-USERNAME/PROJECT-NAME.git
cd PROJECT-NAME
zig build -Doptimize=ReleaseSafe
```

The binary will be at `zig-out/bin/PROJECT-NAME`.
````

**Version bump**: `1.6.0` -> `1.7.0` (new capability: Zig project type)

### 2. setup-ci (3 files: 2 new, 1 modified)

**NEW `plugins/setup-ci/references/ci-zig.md`**:

- 5 parallel jobs: test, format, build, cross-compile, test-scrut (conditional)
- Toolchain setup: `mlugg/setup-zig@v2` with version from `build.zig.zon`
- Cross-compile job loops over 5 targets:
  - `x86_64-linux`, `aarch64-linux`, `x86_64-macos`, `aarch64-macos`, `x86_64-windows`
- All on `ubuntu-latest` (single runner, no macOS runners needed)
- No separate lint job (Zig has no Clippy equivalent; `zig fmt` is the only tool)
- Follow the same structure as `ci-rust.md` (header, YAML template, notes)

**NEW `plugins/setup-ci/references/makefile-zig.md`**:

- Targets: `build`, `test`, `fmt`, `fmt-check`, `lint` (fmt-check + debug build), `run`, `clean`, `release`, `help`
- Follow the same structure as `makefile-rust.md`

**`plugins/setup-ci/commands/setup-ci.md`**:

- Add `zig` to the argument-hint list (line 4)
- Add row to detection table: `build.zig, build.zig.zon` -> `Zig`
- Add `@${CLAUDE_PLUGIN_ROOT}/references/ci-zig.md` to CI Workflow Templates section
- Add `@${CLAUDE_PLUGIN_ROOT}/references/makefile-zig.md` to Makefile Templates section

**Version bump**: `1.5.0` -> `1.6.0` (new capability: Zig CI support)

### 3. setup-linters (2 files modified)

**`plugins/setup-linters/skills/setup-linters/SKILL.md`**:

- Add row to detection table (step 1): `build.zig, build.zig.zon` -> `Zig`
- No new linter config entries needed (Zig has no external linter; `zig fmt` is built into the toolchain)

**`plugins/setup-linters/skills/setup-linters/references/tools/editorconfig.md`**:

- Add a `#### Zig` section with `[*.zig]` override: `indent_size = 4` (Zig uses 4-space indent, like Rust)
- Add `[build.zig]` and `[build.zig.zon]` with `indent_size = 4`
- Update the notes section to mention Zig uses 4-space indentation (`zig fmt` enforces this)

**Version bump**: `1.7.0` -> `1.8.0` (new capability: Zig detection and EditorConfig)

### 4. setup-installers (1 file modified)

**`plugins/setup-installers/commands/setup-installers.md`**:

- Update frontmatter description to include Zig (line 2)
- Add Zig to the detection table: `build.zig` -> `Zig` with note "Check for executable targets"
- Add Zig binary detection description: Check `build.zig` for `addExecutable()` calls or `src/main.zig`
- Add Zig to the installer applicability table: Homebrew (Yes), Shell install script (Yes)
- Add a `#### Reference: Zig Release Workflow` section:
  - Single `ubuntu-latest` runner (not a build matrix)
  - Loop over 5 targets with `zig build -Dtarget=... -Doptimize=ReleaseSafe`
  - Same publish job pattern as Rust (download artifacts, checksums, gh-release)
  - Toolchain setup: `mlugg/setup-zig@v2`
- Update frontmatter `argument-hint` to include `zig-install` or keep as-is (Zig has no centralized package registry, so no `zig install` equivalent)

**Version bump**: `1.4.0` -> `1.5.0` (new capability: Zig release workflow and installers)

### 5. add-scrut-cli-tests (1 file modified)

**`plugins/add-scrut-cli-tests/commands/add-scrut-cli-tests.md`**:

- Add row to detection table: `build.zig` -> `Zig`
- Add Zig binary name inference: Check `build.zig` for `addExecutable()` name or use directory name
- Add Zig binary path: `$(CURDIR)/zig-out/bin/PROJECT-NAME`
- Add Zig to the language setup step notes in CI Job Template: `mlugg/setup-zig@v2`

**Version bump**: `1.3.1` -> `1.4.0` (new capability: Zig detection)

### 6. bootstrap-project (1 file modified)

**`plugins/bootstrap-project/skills/bootstrap-project/SKILL.md`**:

- Add row to detection table: `build.zig` + (`src/main.zig` or `src/`) -> `Zig CLI`
- No overlap rules changes needed (no Zig-specific scaffolder exists, simplest case like Rust)

**`plugins/bootstrap-project/skills/bootstrap-project/references/overlap-rules.md`**:

- No changes needed (Zig has no dedicated scaffolder, so all tools run at full scope)

**Version bump**: `1.1.0` -> `1.2.0` (new capability: Zig detection)

### 7. Marketplace and README

**`.claude-plugin/marketplace.json`**:

- Update version entries for all 6 modified plugins to match their new `plugin.json` versions
- No marketplace `metadata.version` bump (no plugins added or removed, only existing plugins updated)

**Root `README.md`**:

- No structural changes needed (plugin descriptions remain the same; Zig is just another supported language within existing plugins)

### 8. Plugin READMEs (6 files modified)

Each affected plugin's `README.md` should be updated to mention Zig in the supported languages list:

- `plugins/scaffold-new-repo/README.md`
- `plugins/setup-ci/README.md`
- `plugins/setup-linters/README.md`
- `plugins/setup-installers/README.md`
- `plugins/add-scrut-cli-tests/README.md`
- `plugins/bootstrap-project/README.md`

## File Summary

| # | File | Action |
| --- | --- | --- |
| 1 | `plugins/scaffold-new-repo/commands/scaffold-new-repo.md` | Modify |
| 2 | `plugins/scaffold-new-repo/references/gitignore-templates.md` | Modify |
| 3 | `plugins/scaffold-new-repo/references/readme.md` | Modify |
| 4 | `plugins/scaffold-new-repo/.claude-plugin/plugin.json` | Modify (version) |
| 5 | `plugins/scaffold-new-repo/README.md` | Modify |
| 6 | `plugins/setup-ci/commands/setup-ci.md` | Modify |
| 7 | `plugins/setup-ci/references/ci-zig.md` | **Create** |
| 8 | `plugins/setup-ci/references/makefile-zig.md` | **Create** |
| 9 | `plugins/setup-ci/.claude-plugin/plugin.json` | Modify (version) |
| 10 | `plugins/setup-ci/README.md` | Modify |
| 11 | `plugins/setup-linters/skills/setup-linters/SKILL.md` | Modify |
| 12 | `plugins/setup-linters/skills/setup-linters/references/tools/editorconfig.md` | Modify |
| 13 | `plugins/setup-linters/.claude-plugin/plugin.json` | Modify (version) |
| 14 | `plugins/setup-linters/README.md` | Modify |
| 15 | `plugins/setup-installers/commands/setup-installers.md` | Modify |
| 16 | `plugins/setup-installers/.claude-plugin/plugin.json` | Modify (version) |
| 17 | `plugins/setup-installers/README.md` | Modify |
| 18 | `plugins/add-scrut-cli-tests/commands/add-scrut-cli-tests.md` | Modify |
| 19 | `plugins/add-scrut-cli-tests/.claude-plugin/plugin.json` | Modify (version) |
| 20 | `plugins/add-scrut-cli-tests/README.md` | Modify |
| 21 | `plugins/bootstrap-project/skills/bootstrap-project/SKILL.md` | Modify |
| 22 | `plugins/bootstrap-project/.claude-plugin/plugin.json` | Modify (version) |
| 23 | `plugins/bootstrap-project/README.md` | Modify |
| 24 | `.claude-plugin/marketplace.json` | Modify (plugin versions) |

**Total**: 22 files modified, 2 files created

## Commit Strategy

Use `--commit-per-change` aligned with the 6 plugins, following the suggested implementation order:

1. `feat: add Zig support to scaffold-new-repo (#223)` (files 1-5)
2. `feat: add Zig CI workflow and Makefile templates to setup-ci (#223)` (files 6-10)
3. `feat: add Zig detection and EditorConfig to setup-linters (#223)` (files 11-14)
4. `feat: add Zig release workflow and installers to setup-installers (#223)` (files 15-17)
5. `feat: add Zig detection to add-scrut-cli-tests (#223)` (files 18-20)
6. `feat: add Zig detection to bootstrap-project (#223)` (files 21-23)
7. `chore: update marketplace.json versions for Zig support (#223)` (file 24)

## Verification

1. Run `check-versions` skill to verify all version numbers match between `plugin.json` and `marketplace.json`
2. Review each detection table to confirm Zig appears consistently
3. Verify new reference files (`ci-zig.md`, `makefile-zig.md`) follow the same structure as their Rust counterparts
4. Verify the `.gitignore` template includes the correct Zig entries from the issue
5. Verify the EditorConfig section uses 4-space indent for `*.zig` files
6. Confirm the release workflow template uses a single runner (not a build matrix) for cross-compilation
