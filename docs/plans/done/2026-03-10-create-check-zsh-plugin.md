# Create check-zsh Plugin

## Context

There is no skill for evaluating zsh scripts in this repository. The existing `write-shell-scripts` skill covers Bash conventions, and `lint-and-fix` runs general linters, but neither targets zsh-specific analysis. This plugin fills that gap by running seven complementary tools against zsh scripts: syntax checking (`zsh -n`), compilation (`zcompile`), static analysis (`shellcheck --shell=zsh`), bashism detection (`checkbashisms`), safety suggestions (`shellharden`), variable scope warnings (`setopt warn_create_global warn_nested_var`), and formatting (`beautysh`).

## Files to Create

### 1. `plugins/check-zsh/.claude-plugin/plugin.json`

Standard skills plugin metadata. Version `1.0.0`. Category `code-quality` (in marketplace only). Keywords: `beautysh`, `checkbashisms`, `shellcheck`, `shellharden`, `zsh`.

### 2. `plugins/check-zsh/skills/check-zsh/SKILL.md`

Frontmatter:

- `name: check-zsh`
- `description`: Check and evaluate zsh scripts using the seven tools. Trigger phrases: "check zsh", "lint zsh", "validate zsh", "zsh check". Auto-triggers on `.zsh`, `zshrc`, `zshenv`, `zprofile`, `zlogin`, `zlogout` files.

Body structure:

- **H1: Check Zsh**
- **Tool Overview table**: lists all 7 tools with purpose, zsh support level (Native / Yes / Limited / Indirect), and auto-fix capability
- **Workflow** (numbered steps):
  1. **Identify Files** - Glob for `**/*.zsh`, `**/.zsh{rc,env,profile,login,logout}`, `**/zsh{rc,env,profile,login,logout}`. Read other shell scripts to check for `#!/usr/bin/env zsh` or `#!/bin/zsh` shebangs.
  1. **Check Tool Availability** - `command -v` for each tool. Report missing tools with install commands. Minimum: `zsh` must be available.
  1. **Run Tools** - Run sequentially in this order, capturing stdout/stderr/exit code:
     - `zsh -n <file>` (syntax check)
     - `zcompile <file>` (compile check), then `rm -f <file>.zwc`
     - `shellcheck --shell=zsh <file>` (static analysis, filter false positives per `./references/tools/shellcheck.md`)
     - `checkbashisms <file>` (bashism detection, mostly informational per `./references/tools/checkbashisms.md`)
     - `shellharden --check <file>` (safety suggestions, filter per `./references/tools/shellharden.md`)
     - `zsh -c 'setopt warn_create_global warn_nested_var; source <file>'` (variable scope, per `./references/tools/setopt-warnings.md`)
     - `beautysh --check-only <file>` (formatting check)
  1. **Report Results** - Summary table (tool, status, issue count, filtered false positives), then detailed findings by file.
  1. **Fix Issues** - `beautysh <file>` for auto-formatting. For other tools, present findings with manual fix guidance from reference docs. Re-run `zsh -n` after fixes to verify no new syntax errors.
  1. **Clean Up** - Remove any `.zwc` artifacts.
- **Error Handling**: No zsh files found; tool not installed; zsh -n failure blocks other tools; setopt warnings expected in .zshrc files; shellcheck excessive false positives.

### 3. Reference Files (7 files in `plugins/check-zsh/skills/check-zsh/references/tools/`)

Each file documents: purpose, command syntax, installation, what it catches, zsh-specific limitations, false-positive guidance.

| File                 | Key Content                                                                                                                                   |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `zsh-n.md`           | Syntax checking without execution. Always run first.                                                                                          |
| `zcompile.md`        | Compile to wordcode. Clean up `.zwc` afterward.                                                                                               |
| `shellcheck.md`      | SC codes that apply to zsh vs. common false positives (SC2296/SC2299 for zsh param expansion flags, SC3000-series for zsh features).          |
| `checkbashisms.md`   | From `devscripts`. Most output is informational for zsh. Focus on constructs that truly differ (e.g., `BASH_SOURCE`, `shopt`).                |
| `shellharden.md`     | Quoting suggestions apply; some bash-specific syntax suggestions do not.                                                                      |
| `setopt-warnings.md` | `warn_create_global` + `warn_nested_var`. Note: sources the file, may have side effects. Noisy for `.zshrc` files that set globals by design. |
| `beautysh.md`        | Check mode (`--check-only`) and fix mode (in-place). Install via pip/pipx.                                                                    |

### 4. `plugins/check-zsh/README.md`

Per-plugin README following the template:

- Type: Skill
- Trigger: `/check-zsh` (also activates automatically)
- What It Does: Runs seven tools against zsh scripts in recommended order with false-positive filtering.
- Requirements: `shellcheck`, `beautysh`, `shellharden`, `checkbashisms` (with install commands for brew, pip, cargo)
- Recommended Permissions: `Bash(zsh -n *)`, `Bash(zsh -c *)`, `Bash(zcompile *)`, `Bash(shellcheck *)`, `Bash(checkbashisms *)`, `Bash(shellharden *)`, `Bash(beautysh *)`, `Bash(rm *.zwc)`
- See Also: Write Shell Scripts, Lint and Fix

## Files to Modify

### 1. `.claude-plugin/marketplace.json`

- Bump `metadata.version` from `1.23.0` to `1.24.0`
- Insert `check-zsh` entry (with `"category": "code-quality"`, `"source": "./plugins/check-zsh"`) alphabetically between `bootstrap-project` and `clean-up-agent-config`

### 2. `README.md`

- **ToC** (Code Quality section): Insert `[Check Zsh](#check-zsh)` as first entry, add `∙` prefix to the existing `[Handle Secrets](#handle-secrets)` line
- **Description section**: Insert new `#### Check Zsh` subsection before `#### Handle Secrets` (line 193)

### 3. `CLAUDE.md`

- Insert `check-zsh/` directory tree between `bootstrap-project/` (line 60) and `commit/` (line 61)

## Verification

1. `jq . < plugins/check-zsh/.claude-plugin/plugin.json` and `jq . < .claude-plugin/marketplace.json` parse without errors
1. `plugin.json` version (`1.0.0`) matches `marketplace.json` entry version
1. `marketplace.json` `metadata.version` is `1.24.0`
1. `marketplace.json` entry alphabetically between `bootstrap-project` and `clean-up-agent-config`
1. SKILL.md frontmatter has only `name` and `description` fields
1. All 7 reference files exist in `references/tools/`
1. README ToC has `[Check Zsh](#check-zsh)` before `[Handle Secrets](#handle-secrets)` in Code Quality
1. README description section has `#### Check Zsh` before `#### Handle Secrets`
1. CLAUDE.md tree has `check-zsh/` between `bootstrap-project/` and `commit/`
1. Run `check-versions` skill to validate consistency
