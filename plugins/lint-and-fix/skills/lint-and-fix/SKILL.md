---
name: lint-and-fix
description: >-
  Detect available linters and formatters in the project, run them with
  auto-fix flags, report results, and manually resolve remaining issues.
  Use when the user says "lint and fix", "run the linter", "run linters",
  "fix lint errors", "format the code", "lint this project", "check and fix",
  "run eslint", "run prettier", or any variant involving running project
  linters or formatters.
---

# Lint and Fix

Detect project linters and formatters, run them with auto-fix, and resolve remaining issues.

## Options

The user may provide these options inline:

- **--commit** / **--no-commit**: Control whether to commit fixes (default: ask after fixing)
- **--tool <name>**: Run only a specific tool (e.g., `--tool eslint`, `--tool prettier`)
- **--check**: Run in check-only mode (report issues without fixing)

## Workflow

### 1. Detect Available Tools

Check for linter and formatter configuration in the project. Use Glob and Read to find config files and check for installed tools. Run detection checks in parallel where possible.

#### Detection Table

| Config file(s) | Tool | Fix command | Check command |
|----------------|------|-------------|---------------|
| `eslint.config.*`, `.eslintrc.*` | eslint | `npx eslint --fix .` | `npx eslint .` |
| `.prettierrc*`, `prettier.config.*` | prettier | `npx prettier --write .` | `npx prettier --check .` |
| `.markdownlint.json`, `.markdownlint.yaml` | markdownlint | `npx markdownlint-cli2 --fix "**/*.md"` | `npx markdownlint-cli2 "**/*.md"` |
| `.markdownlint-cli2.*` | markdownlint-cli2 | `npx markdownlint-cli2 --fix "**/*.md"` | `npx markdownlint-cli2 "**/*.md"` |
| Shell scripts in project | shellcheck | _(no auto-fix)_ | `shellcheck <files>` |
| Shell scripts in project | shfmt | `shfmt -w <files>` | `shfmt -d <files>` |
| `knip.json`, `knip.config.*`, `knip.ts` | knip | _(no auto-fix)_ | `npx knip` |
| `package.json` has `lint` script | npm lint | Try `npm run lint -- --fix`, fall back to `npm run lint` | `npm run lint` |
| `package.json` has `format` script | npm format | `npm run format` | Try `npm run format -- --check`, fall back to `npm run format` |
| `bin/lint`, `scripts/lint`, `script/lint` | Project script | Try `<script> --fix` first | `<script>` |

#### Detection Steps

1. **Config files**: Use Glob to check for each config pattern in the project root.
2. **Package.json scripts**: Read `package.json` and check for `lint`, `format`, or `check` scripts.
3. **Shell scripts**: Use Glob to find `**/*.sh`, `bin/*`, `scripts/*`, `script/*`. If shell scripts are present, shellcheck and shfmt apply.
4. **Project lint scripts**: Check for `bin/lint`, `scripts/lint`, `script/lint`.
5. **Tool availability**: Verify detected tools are installed (check `npx`, `which`, or `package.json` devDependencies).

If **--tool <name>** was specified, filter the detected list to only that tool. If the specified tool was not detected, report that and stop.

If **no tools are detected**, report that no linters or formatters were found and stop.

### 2. Present Detected Tools

Before running, display the detected tools:

```text
## Detected Linters and Formatters

| Tool | Config | Command |
|------|--------|---------|
| eslint | eslint.config.js | npx eslint --fix . |
| prettier | .prettierrc.json | npx prettier --write . |
| shellcheck | (shell scripts found) | shellcheck bin/* |
```

If running in **--check** mode, show check commands instead of fix commands.

### 3. Run Each Tool

Run each detected tool sequentially. For each tool:

#### 3a. Run the Command

Run the fix command (or check command if **--check** was specified). Capture stdout, stderr, and exit code.

**Tool-specific notes:**

- **eslint**: Exit code 0 = clean, 1 = issues found. Parse output for remaining error/warning counts.
- **prettier**: Exit code 0 = all clean, 1 = unformatted files found (check mode) or write errors.
- **markdownlint-cli2**: Exit code 0 = clean, 1 = issues found. With `--fix`, some issues auto-fix and others remain.
- **shellcheck**: No auto-fix. All issues reported for manual resolution.
- **shfmt**: With `-w`, formats in place silently. With `-d`, shows diffs.
- **knip**: No auto-fix. Reports unused files, dependencies, and exports.
- **npm scripts**: Exit codes depend on the underlying tool.
- **Project scripts**: Try with `--fix` first. If the script does not recognize `--fix`, run without it.

#### 3b. Record Results

For each tool, record:

- **Tool**: Name
- **Exit code**: 0 (success) or non-zero
- **Files fixed**: Count from output (if available)
- **Remaining issues**: Count and summary of what auto-fix could not resolve
- **Output**: Full output for reference

### 4. Report Results

After all tools run, display a summary:

```text
## Lint and Fix Results

| Tool | Status | Fixed | Remaining |
|------|--------|-------|-----------|
| eslint | Ran with fixes | 3 files | 2 errors |
| prettier | All formatted | 5 files | 0 |
| shellcheck | Check only | — | 4 warnings |
```

If **--check** was specified, show results and stop here.

If all tools passed with zero remaining issues, skip to step 6.

### 5. Fix Remaining Issues

For each remaining issue that auto-fix could not resolve:

1. **Read the tool output** to identify the specific error, file, and line number.
2. **Read the relevant file** at the indicated location.
3. **Apply the fix** based on the error type:
   - **ESLint**: Read the rule from the error code (e.g., `no-unused-vars`), edit the code to comply.
   - **ShellCheck**: Read the SC code (e.g., SC2086), apply the recommended fix (quoting variables, using arrays, etc.).
   - **Markdownlint**: Fix heading levels, line lengths, trailing whitespace, etc.
   - **Knip**: Remove unused exports or dependencies after confirming they are truly unused.
4. **Re-run the tool** on the specific file to verify the fix.

If a remaining issue is ambiguous or risky to fix automatically (e.g., removing a dependency that might be used dynamically, or a lint rule that conflicts with project intent), skip it and report:

```text
Skipped: <file>:<line> — <rule> — <reason>
```

### 6. Final Verification

Re-run all detected tools one final time in check mode to confirm a clean state:

```text
## Final Verification

| Tool | Status |
|------|--------|
| eslint | Pass |
| prettier | Pass |
| shellcheck | Pass (1 advisory skipped) |
```

### 7. Commit (Optional)

**If --no-commit was specified**: Stop here.

**If --commit was specified**: Commit immediately.

**Otherwise**: Ask the user whether to commit the fixes.

When committing:

1. Stage all files modified by the lint and format fixes.
2. Generate a conventional commit message:
   - Use `style:` for pure formatting and linting fixes.
   - Use `fix:` if linting changes corrected actual bugs (e.g., unused variables removed, error handling added).
   - Include which tools ran and a brief summary of manual fixes in the commit body.

## Error Handling

- **No tools detected**: Report that no linters or formatters were found. Suggest common config files the user could add.
- **Tool not installed**: If a config file exists but the tool is not available, report which tool is missing and suggest installation (e.g., `npm install -D eslint`).
- **Execution failure**: Report the error output, then continue with the next tool rather than aborting.
- **Permission errors on project scripts**: Report the error, suggest `chmod +x <script>`.
- **Conflicting tools**: If both a `package.json` lint script and a standalone config (e.g., eslint) are detected, prefer the `package.json` script (it may have project-specific flags). Note the overlap to the user.
- **Pre-commit hook failure on commit**: Fix the issue, re-stage, and create a new commit (never amend).
