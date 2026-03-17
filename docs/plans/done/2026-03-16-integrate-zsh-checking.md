# Integrate Zsh Checking into setup-linters, setup-ci, and bootstrap-project

Addresses [#218](https://github.com/cboone/cboone-cc-plugins/issues/218) and [#219](https://github.com/cboone/cboone-cc-plugins/issues/219).

## Context

**Issue #218**: The `check-zsh-scripts` skill (v2.1.0) has comprehensive knowledge of how to validate zsh scripts using 7 complementary tools, but the `setup-linters`, `setup-ci`, and `bootstrap-project` plugins do not account for zsh projects. They treat all shell scripts as bash: configuring `.shellcheckrc` with bash-oriented optional checks, using `shfmt` without `-ln zsh`, and generating CI with only ShellCheck/shfmt. This plan integrates zsh-specific checking knowledge into all three plugins.

**Issue #219**: The `check-zsh-scripts` skill has two documentation gaps in its shellcheck reference:

1. SC2034 ("Variable appears unused") is classified as reliably applying to zsh, but it produces false positives for zsh completion system variables (`PREFIX`, `SUFFIX`, etc.), cross-file globals, and indirect expansion via `${(P)var_name}`.
2. The SKILL.md instructs filtering SC3xxx codes from shellcheck output, but SC3xxx codes only fire with `--shell=sh`, not `--shell=bash`. Since the skill uses `--shell=bash`, this filtering is a no-op.

## Design Decisions

1. **Zsh as a sibling of Shell, not a sub-type.** A project can have both `.sh` (bash) and `.zsh` (zsh) files. Both detection rows are evaluated independently, and both tool stacks can coexist.

2. **Inline CI job (not reusable workflow).** No `cboone/gh-actions` reusable workflow exists for zsh checking. The zsh CI job installs tools directly on Ubuntu, like the JS/Python/Rust/Ruby/Swift templates.

3. **Generated scripts are templates within the reference file.** The `scripts/check-zsh.zsh` and `scripts/lib/find-zsh-files.zsh` mentioned in the issue are templates that `setup-linters` generates in the target project. They live as code blocks within the new `zsh.md` language reference.

4. **Minimal `.shellcheckrc` for zsh.** For zsh-only projects, `.shellcheckrc` contains only `external-sources=true`. Bash-specific optional checks are omitted. The `--shell=bash --exclude=SC1090,SC2039,SC2154,SC2168,SC2296,SC2299` flags are handled per-invocation in the check script.

5. **No marketplace metadata.version bump.** No plugins are added or removed; only existing plugin versions change.

## Changes

### Phase 0: check-zsh-scripts docs fixes (v2.1.0 -> v2.1.1) -- Issue #219

#### 0a. EDIT: `plugins/check-zsh-scripts/skills/check-zsh-scripts/references/tools/shellcheck.md`

Two changes:

1. **Line 25 (SC2034 entry)**: Add a caveat to the "Reliably Apply to Zsh" entry. Change:

   ```text
   - **SC2034**: Variable appears unused (verify it is not exported or used by a framework)
   ```

   to:

   ```text
   - **SC2034**: Variable appears unused (verify it is not exported or used by a framework). May need project-specific exclusion for: zsh completion system variables (`PREFIX`, `SUFFIX`, `IPREFIX`, `ISUFFIX`), cross-file globals consumed in a different file, and indirect expansion via `${(P)var_name}`
   ```

2. **Line 37 (SC3000-series entry)**: Add a note that SC3xxx codes only fire with `--shell=sh`. Change:

   ```text
   - **SC2039, SC3000-series**: Zsh-specific features flagged as "not POSIX" or "not supported in sh"
   ```

   to:

   ```text
   - **SC2039**: Zsh-specific features flagged as "not supported in sh"
   - **SC3000-series**: Zsh features flagged as "not POSIX" (only fires with `--shell=sh`, not `--shell=bash`; no filtering needed when using `--shell=bash`)
   ```

#### 0b. EDIT: `plugins/check-zsh-scripts/skills/check-zsh-scripts/SKILL.md`

**Lines 96-98 (section 3c)**: Update the SC3000-series filtering instruction. Change:

```text
Additionally, filter SC3000-series codes (too numerous for `--exclude`) from the output, as they flag zsh features as non-POSIX.
```

to:

```text
Note: SC3000-series codes only fire with `--shell=sh`, not `--shell=bash`. Since this workflow uses `--shell=bash`, no SC3xxx filtering is needed. If the project ever switches to `--shell=sh`, add SC3xxx filtering at that point.
```

#### 0c. EDIT: `plugins/check-zsh-scripts/.claude-plugin/plugin.json`

- Version: `"2.1.0"` -> `"2.1.1"` (patch: wording fix)

#### 0d. EDIT: `.claude-plugin/marketplace.json`

- check-zsh-scripts version: `"2.1.0"` -> `"2.1.1"` (line 122)

### Phase 1: setup-linters (v1.6.1 -> v1.7.0)

#### 1a. NEW: `plugins/setup-linters/skills/setup-linters/references/languages/zsh.md`

The core new reference file, structured like `shell.md`. Sections:

- **Tools**: All 7 tools from check-zsh-scripts (zsh -n, zcompile, shellcheck with exclusions, checkbashisms, shellharden, setopt warnings, shfmt -ln zsh)
- **Install**: `brew install shellcheck shfmt shellharden` plus `devscripts` for checkbashisms
- **Config**: Minimal `.shellcheckrc` (only `external-sources=true`); `.editorconfig` zsh section with shfmt properties
- **Generated Scripts**: Template for `scripts/check-zsh.zsh` (runs the 7-tool pipeline, cleans up .zwc files, reports summary; no SC3xxx filtering needed per #219) and template for `scripts/lib/find-zsh-files.zsh` (file discovery helper)
- **Commands**: Full check pipeline, format-only, syntax-check-only
- **Makefile Targets**: `check-zsh` and `format-zsh`
- **Notes**: Cross-references check-zsh-scripts skill; notes on shfmt experimental mode, setopt side effects, mixed bash/zsh projects

#### 1b. EDIT: `plugins/setup-linters/skills/setup-linters/SKILL.md`

- Line 28 detection table: Add row after Shell: `| *.zsh, #!/usr/bin/env zsh shebangs, .zshrc, .zshenv | Zsh |`
- Section 3 recommendation table example (line ~108): Add Zsh row
- Tool dependency verification table (line ~167): Add checkbashisms and shellharden entries

#### 1c. EDIT: `plugins/setup-linters/skills/setup-linters/references/checklist.md`

- Add Zsh row to the Language-Specific Linters table (after Shell, line 14)

#### 1d. EDIT: `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`

- Add Zsh CI template section after Shell (line 286), before Swift (line 288)

#### 1e. EDIT: `plugins/setup-linters/.claude-plugin/plugin.json`

- Version: `"1.6.1"` -> `"1.7.0"`
- Keywords: add `"zsh"`

#### 1f. EDIT: `plugins/setup-linters/README.md`

- Add "Zsh" to the supported languages list

### Phase 2: setup-ci (v1.4.0 -> v1.5.0)

#### 2a. NEW: `plugins/setup-ci/references/ci-zsh.md`

Inline CI workflow template. Installs zsh, shellcheck, devscripts (checkbashisms), shfmt (via `mfinelli/setup-shfmt@v4`), and shellharden (via `cargo install`). Runs `make check-zsh`.

#### 2b. NEW: `plugins/setup-ci/references/makefile-zsh.md`

Makefile template with `check-zsh` (runs `./scripts/check-zsh.zsh`) and `format-zsh` (runs `shfmt -ln zsh -w`) targets.

#### 2c. EDIT: `plugins/setup-ci/commands/setup-ci.md`

- Line 4 argument-hint: Add `|zsh`
- Line 15: Add `zsh` to the valid argument list
- Line 26 detection table: Add Zsh row after Shell
- Line 146: Add `@${CLAUDE_PLUGIN_ROOT}/references/ci-zsh.md` after ci-shell.md
- Line 164: Add `@${CLAUDE_PLUGIN_ROOT}/references/makefile-zsh.md` after makefile-shell.md

#### 2d. EDIT: `plugins/setup-ci/.claude-plugin/plugin.json`

- Version: `"1.4.0"` -> `"1.5.0"`
- Keywords: add `"zsh"`

#### 2e. EDIT: `plugins/setup-ci/README.md`

- Add "Zsh" to the supported languages list

### Phase 3: bootstrap-project (v1.0.2 -> v1.1.0)

#### 3a. EDIT: `plugins/bootstrap-project/skills/bootstrap-project/SKILL.md`

- Line 31 detection table: Add Zsh row after Shell: `| *.zsh, #!/usr/bin/env zsh shebangs, .zshrc, .zshenv | Zsh |`

No other workflow logic changes needed; bootstrap-project delegates to setup-linters and setup-ci, which now handle Zsh natively.

#### 3b. EDIT: `plugins/bootstrap-project/.claude-plugin/plugin.json`

- Version: `"1.0.2"` -> `"1.1.0"`
- Keywords: add `"zsh"`

### Phase 4: Marketplace and root README

#### 4a. EDIT: `.claude-plugin/marketplace.json`

- Line 108: bootstrap-project version `"1.0.2"` -> `"1.1.0"`, add `"zsh"` to keywords
- Line 388: setup-ci version `"1.4.0"` -> `"1.5.0"`, add `"zsh"` to keywords
- Line 416: setup-linters version `"1.6.1"` -> `"1.7.0"`, add `"zsh"` to keywords
- metadata.version stays at `"1.25.0"` (no plugins added/removed)

#### 4b. EDIT: `README.md` (root)

- Line 254: Add "Zsh" to setup-linters supported languages
- Line 353: Add "Zsh" to setup-ci supported languages

## Commit Plan

1. `docs(check-zsh-scripts): note SC2034 false positives and SC3xxx no-op with --shell=bash (#219)` - Phase 0 (0a-0d)
2. `feat(setup-linters): add zsh project detection and configuration (#218)` - Phase 1 (1a-1f)
3. `feat(setup-ci): add zsh CI job and Makefile targets (#218)` - Phase 2 (2a-2e)
4. `feat(bootstrap-project): add zsh project type detection (#218)` - Phase 3 (3a-3b)
5. `chore: update marketplace versions and root README for zsh support (#218)` - Phase 4 (4a-4b)

## Verification

1. Verify shellcheck.md SC2034 entry has the caveat about completion variables, cross-file globals, and indirect expansion
2. Verify SKILL.md section 3c no longer instructs filtering SC3xxx codes (replaced with explanatory note)
3. Inspect the new `zsh.md` reference file for completeness against the check-zsh-scripts SKILL.md tool list
4. Verify all three detection tables include the Zsh row with consistent marker patterns
5. Run `/check-versions` to confirm plugin.json and marketplace.json versions match
6. Verify the CI template in `ci-zsh.md` installs all 5 external tools (zsh, shellcheck, devscripts, shfmt, shellharden)
7. Verify the `setup-ci.md` argument-hint and template references include zsh entries
8. Confirm no existing Shell behavior is changed (bash projects still get ShellCheck + shfmt only)
