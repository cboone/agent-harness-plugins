# Remove install.sh Generation from setup-installers

## Context

The `setup-installers` plugin currently supports four installer types: Homebrew tap, shell install script (`install.sh`), `go install`, and `cargo install`. The user no longer wants to support shell install script generation. This plan removes that capability and all references to it across the codebase.

Since the "Other" project type column in the installer selection table only had "Yes" for the shell install script, that column is also removed; the command will require Go, Swift, or Rust projects.

## Versioning

| File                                                       | Field              | Before | After  | Reason                    |
| ---------------------------------------------------------- | ------------------ | ------ | ------ | ------------------------- |
| `plugins/setup-installers/.claude-plugin/plugin.json`      | `version`          | 1.4.0  | 2.0.0  | Major: removed capability |
| `.claude-plugin/marketplace.json` (setup-installers entry) | `version`          | 1.4.0  | 2.0.0  | Must match plugin.json    |
| `.claude-plugin/marketplace.json`                          | `metadata.version` | 1.25.0 | 1.26.0 | Minor: catalog changed    |

## Changes by File

### 1. `plugins/setup-installers/commands/setup-installers.md`

The core change. Work top to bottom:

- **Line 4**: Remove `shell` from argument-hint: `"[homebrew|go-install|cargo-install]"`
- **Lines 12-14**: Remove "Shell install script" bullet from installer types list
- **Line 45**: Replace fallback about shell install script with: "Inform the user that the project type is not supported. This command requires a Go, Swift, or Rust project."
- **Lines 51-52**: Remove "Shell install script" detection bullet
- **Line 61**: Remove `shell` from arguments list
- **Lines 65-70**: Remove "Shell install script" row and "Other" column from installer selection table
- **Lines 225-388**: Delete entire Section 6 "Set Up Shell Install Script" (template, macOS variant, ShellCheck, prettierignore)
- **Renumber** sections 7-10 to 6-9
- **Section 7 (new 6: Release Workflow)**: Change "If the user selected Homebrew or shell install script" to "If the user selected Homebrew"
- **Swift workflow notes**: Change "to match the `install.sh` convention" to "to match the tarball naming convention used by Homebrew formulas"
- **Section 9 (new 8: Update README)**: Remove "Shell script" subsection from the README template
- **Section 10 (new 9: Print Summary)**: Remove `.prettierignore` parenthetical, shell install script next-steps bullet, and ShellCheck note
- **Error Handling**: Remove "If ShellCheck is not installed" item

### 2. `plugins/setup-installers/.claude-plugin/plugin.json`

- Update description: remove "shell install script"
- Bump version: 1.4.0 to 2.0.0

### 3. `plugins/setup-installers/README.md`

- Update opening description: remove "shell install script"
- Remove "Shell Script" column from supported languages table
- Remove shell install script bullet from "What It Does"
- Remove "Also validates generated scripts with ShellCheck..." line
- Remove `/setup-installers shell` from usage examples
- Remove shell example from examples list

### 4. `.claude-plugin/marketplace.json`

- Update setup-installers description: remove "shell install script"
- Bump setup-installers entry version: 1.4.0 to 2.0.0
- Bump metadata.version: 1.25.0 to 1.26.0

### 5. `plugins/bootstrap-project/skills/bootstrap-project/SKILL.md`

- Line 57: Change `install.sh or Formula/` to `Formula/` in detection table
- Line 109: Change "Homebrew formula, install.sh" to "Homebrew formula" in example

### 6. `plugins/bootstrap-project/README.md`

- Line 30: Change "Homebrew formula, install script" to "Homebrew formula"

### 7. `plugins/update-everything/commands/update-everything.md`

- Line 48: Change `install.sh or Formula/` to `Formula/` in detection table
- Lines 475-488: Remove `install.sh` from Files list, remove "Checks for install.sh" subsection, keep "Checks for Formula/\*.rb"

### 8. `README.md` (root)

- Line 367: Remove "shell install script" from Setup Installers description

## Files NOT modified

Historical plan files in `docs/plans/done/` are not modified (they are records of past work).

## Verification

1. Grep for `install\.sh` across the codebase, confirm no remaining references outside of `docs/plans/done/`
2. Grep for `shell install` and `shell script` (in the installer context), confirm none remain
3. Grep for `ShellCheck` in setup-installers, confirm no references remain
4. Grep for `prettierignore` in setup-installers, confirm no references remain
5. Verify section numbering in setup-installers.md is sequential (1-9)
6. Run `check-versions` skill to verify version consistency
7. Confirm marketplace.json is valid JSON
