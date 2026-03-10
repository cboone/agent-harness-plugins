---
name: check-zsh
description: >-
  Check and evaluate zsh scripts using shellcheck, beautysh, shfmt,
  shellharden, zsh -n, zcompile, setopt warn_create_global/warn_nested_var,
  and checkbashisms. Use when: (1) creating or editing zsh scripts (.zsh, zshrc,
  zshenv, zprofile, zlogin, zlogout), (2) reviewing zsh code for bugs or
  portability issues, (3) checking zsh variable scoping, (4) formatting zsh
  scripts, or (5) the user says "check zsh", "lint zsh", "validate zsh",
  "zsh check", or "check my zsh script".
---

# Check Zsh

Check and evaluate zsh scripts using multiple complementary static analysis, syntax checking, and formatting tools.

## Tool Overview

| Order | Tool                          | Purpose                              | Zsh Support  | Auto-Fix |
| ----- | ----------------------------- | ------------------------------------ | ------------ | -------- |
| 1     | `zsh -n`                      | Syntax check (parse without execute) | Native       | No       |
| 2     | `zcompile`                    | Compile to wordcode                  | Native       | No       |
| 3     | `shellcheck --shell=zsh`      | Static analysis                      | Limited      | No       |
| 4     | `checkbashisms`               | Identify bash-specific constructs    | Indirect     | No       |
| 5     | `shellharden --check`         | Safer syntax suggestions             | Limited      | Suggest  |
| 6     | `zsh -c 'setopt ...; source'` | Variable scope warnings              | Native       | No       |
| 7     | `shfmt -ln zsh`               | Shell formatter                      | Experimental | Yes      |
| 8     | `beautysh`                    | Code formatter                       | Yes          | Yes      |

## Workflow

### 1. Identify Files to Check

Scan the project for zsh files using Glob:

- `**/*.zsh`
- `**/.zshrc`, `**/.zshenv`, `**/.zprofile`, `**/.zlogin`, `**/.zlogout`
- `**/zshrc`, `**/zshenv`, `**/zprofile`, `**/zlogin`, `**/zlogout`

For other shell scripts, use Read to check shebangs for `#!/usr/bin/env zsh` or `#!/bin/zsh`.

If the user specified particular files, use those instead of scanning.

If no zsh files are found, report this and stop.

### 2. Check Tool Availability

For each tool, verify installation:

```bash
command -v zsh
command -v shellcheck
command -v checkbashisms
command -v shellharden
command -v shfmt
command -v beautysh
```

`zcompile` is a zsh builtin and does not need a separate check.

Present a table of available vs. missing tools. For missing tools, show the install command from the tool's reference file and continue with available tools.

Minimum requirement: `zsh` must be available (pre-installed on macOS).

### 3. Run Tools

Run each available tool sequentially in the order listed below. For each tool, capture stdout, stderr, and exit code.

#### 3a. Syntax Check

```bash
zsh -n <file>
```

If this fails, report the syntax errors prominently. Syntax errors may block meaningful results from other tools, but continue running other tools anyway since they may catch different issues.

See `./references/tools/zsh-n.md`.

#### 3b. Compile Check

```bash
zcompile <file>
```

Then clean up:

```bash
rm -f <file>.zwc
```

See `./references/tools/zcompile.md`.

#### 3c. Static Analysis

```bash
shellcheck --shell=zsh <file>
```

Filter false positives: SC2296, SC2299 (zsh parameter expansion flags), SC2154 (framework variables), SC1090 (non-constant source), SC2039/SC3000-series (zsh features flagged as non-POSIX), SC2168 (local in non-function contexts).

See `./references/tools/shellcheck.md` for the full list of applicable vs. false-positive SC codes.

#### 3d. Bashism Detection

```bash
checkbashisms <file>
```

Most output is informational for zsh scripts. Focus on constructs that truly differ between bash and zsh: `BASH_SOURCE`, `shopt`, `declare -n`, `readarray`/`mapfile`, `compgen`/`complete`.

See `./references/tools/checkbashisms.md`.

#### 3e. Safety Suggestions

```bash
shellharden --check <file>
```

If issues are found, show suggestions:

```bash
shellharden --suggest <file>
```

Note that some quoting suggestions are less critical in zsh (zsh does not split unquoted parameter expansions by default), but quoting remains good practice for portability.

See `./references/tools/shellharden.md`.

#### 3f. Variable Scope Warnings

```bash
zsh -c 'emulate -L zsh; setopt warn_create_global warn_nested_var; source <file>'
```

This sources the file, so review its contents for side effects first. For `.zshrc` and similar config files that intentionally set global state, many warnings are expected. Note this context when reporting.

See `./references/tools/setopt-warnings.md`.

#### 3g. Shell Formatting

```bash
shfmt -ln zsh -d <file>
```

If shfmt fails to parse a zsh-specific construct, skip it gracefully for that file and rely on beautysh.

See `./references/tools/shfmt.md`.

#### 3h. Code Formatting

```bash
beautysh --check-only <file>
```

See `./references/tools/beautysh.md`.

### 4. Report Results

Display a summary table:

```text
| Tool | Status | Issues | Filtered |
|------|--------|--------|----------|
| zsh -n | Pass/Fail | N | -- |
| zcompile | Pass/Fail | N | -- |
| shellcheck | Pass/Issues | N | M filtered |
| checkbashisms | Pass/Info | N | M filtered |
| shellharden | Pass/Suggestions | N | M filtered |
| setopt warnings | Pass/Warnings | N | -- |
| shfmt | Pass/Formatting | N files | -- |
| beautysh | Pass/Formatting | N files | -- |
```

Then list each genuine issue with:

- File path and line number
- Tool that found it
- Error/warning code (if applicable)
- Message
- Suggested fix

### 5. Fix Issues

For formatting issues, offer to auto-fix with shfmt and beautysh:

```bash
shfmt -ln zsh -w <file>
beautysh <file>
```

Run shfmt first (stricter parser), then beautysh for anything shfmt could not parse.

For other tools, present findings with manual fix guidance from the relevant reference documentation.

After applying fixes, re-run `zsh -n` to verify no new syntax errors were introduced.

### 6. Clean Up

Remove any `.zwc` files created during step 3b that were not already cleaned up:

```bash
rm -f <file>.zwc
```

## Error Handling

- **No zsh files found**: Report that no zsh files were detected in the project and stop.
- **Tool not installed**: Report the missing tool with its install command. Continue with available tools.
- **zsh -n failure**: Report syntax errors prominently. Continue running other tools.
- **zcompile failure when zsh -n passed**: Report the compilation error as a potential edge case worth investigating.
- **shellcheck excessive false positives**: If more than half the output is filtered, note this and suggest focusing on native zsh tools.
- **setopt warnings in config files**: For `.zshrc`, `.zshenv`, and similar files that set global state by design, note that `warn_create_global` warnings are expected.
- **shfmt parse error**: If shfmt cannot parse a zsh-specific construct, skip that file and rely on beautysh for formatting. The parse error is informational, not a bug in the script.
- **Source side effects**: Before running the setopt check (step 3f), review the file for commands that modify state. Skip this check for files with significant side effects if the user prefers.
