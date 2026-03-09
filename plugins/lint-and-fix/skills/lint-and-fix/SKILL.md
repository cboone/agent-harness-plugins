---
name: lint-and-fix
description: >-
  Detect available linters and formatters in the project, run them with
  auto-fix flags, report results, manually resolve remaining issues, then
  commit and push the fixes. Use when the user says "lint and fix", "run the
  linter", "run linters", "fix lint errors", "format the code", "lint this
  project", "check and fix", "run eslint", "run prettier", or any variant
  involving running project linters or formatters.
---

# Lint and Fix

Detect project linters and formatters, run them with auto-fix, and resolve remaining issues.

## Options

The user may provide these options inline:

- **--no-commit**: Skip committing and pushing (default: commit and push after fixing)
- **--no-push**: Commit but do not push (default: push after committing)
- **--tool <name>**: Run only a specific tool (e.g., `--tool eslint`, `--tool prettier`)
- **--check**: Run in check-only mode (report issues without fixing)

## Workflow

### 1. Detect Available Tools

Check for linter and formatter configuration in the project. Use Glob and Read to find config files and check for installed tools. Run detection checks in parallel where possible.

#### Detection Table

| Config file(s)                                                     | Tool               | Fix command                                              | Check command                                                  |
| ------------------------------------------------------------------ | ------------------ | -------------------------------------------------------- | -------------------------------------------------------------- |
| `eslint.config.*`, `.eslintrc.*`                                   | eslint             | `npx eslint --fix .`                                     | `npx eslint .`                                                 |
| `.prettierrc*`, `prettier.config.*`                                | prettier           | `npx prettier --write .`                                 | `npx prettier --check .`                                       |
| `.markdownlint.json`, `.markdownlint.yaml`                         | markdownlint       | `npx markdownlint-cli2 --fix "**/*.md"`                  | `npx markdownlint-cli2 "**/*.md"`                              |
| `.markdownlint-cli2.*`                                             | markdownlint-cli2  | `npx markdownlint-cli2 --fix "**/*.md"`                  | `npx markdownlint-cli2 "**/*.md"`                              |
| Shell scripts in project                                           | shellcheck         | _(no auto-fix)_                                          | `shellcheck <files>`                                           |
| Shell scripts in project                                           | shfmt              | `shfmt -w <files>`                                       | `shfmt -d <files>`                                             |
| `knip.json`, `knip.config.*`, `knip.ts`                            | knip               | _(no auto-fix)_                                          | `npx knip`                                                     |
| `cspell.json`, `.cspell.json`, `cspell.config.*`                   | cspell             | _(no auto-fix)_                                          | `npx cspell .`                                                 |
| `package.json` has `lint` script                                   | npm lint           | Try `npm run lint -- --fix`, fall back to `npm run lint` | `npm run lint`                                                 |
| `package.json` has `format` script                                 | npm format         | `npm run format`                                         | Try `npm run format -- --check`, fall back to `npm run format` |
| `bin/lint`, `scripts/lint`, `script/lint`                          | Project script     | Try `<script> --fix` first                               | `<script>`                                                     |
| `.github/workflows/*.yml`, `.github/workflows/*.yaml` `run:` steps | CI workflow script | Run detected command                                     | Run detected command                                           |

#### Detection Steps

1. **Config files**: Use Glob to check for each config pattern in the project root.
1. **Package.json scripts**: Read `package.json` and check for `lint`, `format`, or `check` scripts.
1. **Shell scripts**: Use Glob to find `**/*.sh`, `bin/*`, `scripts/*`, `script/*`. If shell scripts are present, shellcheck and shfmt apply.
1. **Project lint scripts**: Check for `bin/lint`, `scripts/lint`, `script/lint`.
1. **CI workflow scripts**: Scan CI workflow files for repo-specific linting and validation steps not already covered by other detection methods. See [CI Workflow Detection](#ci-workflow-detection) below.
1. **Tool availability**: Verify detected tools are installed (check `npx`, `which`, or `package.json` devDependencies).

#### CI Workflow Detection

Scan `.github/workflows/*.yml` and `.github/workflows/*.yaml` files to discover repo-specific linting and validation steps that go beyond standard tooling.

1. **Find workflow files**: Use Glob to find `.github/workflows/*.yml` and `.github/workflows/*.yaml`.
1. **Identify lint/validation jobs**: Read each workflow file. Look for jobs or steps whose `name` suggests linting, validation, or code quality (keywords: "lint", "check", "validate", "format", "style", "quality", "verify").
1. **Extract `run:` commands**: From matching jobs and steps, collect all `run:` values.
1. **Skip reusable workflow calls**: If a job uses `uses: org/repo/.github/workflows/workflow.yml@ref` (a reusable workflow call, e.g., `cboone/gh-actions/.github/workflows/go-ci.yml@v1`), skip it entirely. Reusable workflows run in CI only and cannot be executed locally. They are not a source of locally-runnable lint commands.
1. **Filter for repo-specific scripts**: Keep commands that invoke project scripts (paths starting with `bin/`, `scripts/`, `script/`, `./bin/`, `./scripts/`, or `./script/`). These are repo-specific validation tools. Also keep commands that invoke standalone tools not already covered by the detection table (e.g., `actionlint`, `taplo check`).
1. **Deduplicate**: Exclude any commands already covered by earlier detection steps. For example, if `shellcheck` was already detected from shell scripts in the project, do not add a duplicate entry from the CI workflow. Similarly, if `bin/lint` was already detected as a project lint script, skip it.
1. **Add as tools**: Register each remaining command as a CI workflow script in the detected tools list. Use the script's basename or the tool name as the tool identifier. If two scripts share the same basename (e.g., `bin/check` and `scripts/check`), use the relative path as the identifier to avoid collisions. These scripts typically have no auto-fix mode, so use the same command for both fix and check.

**Example**: A CI workflow containing these steps:

```yaml
- name: Validate JSON syntax
  run: bin/validate-json
- name: Validate plugin structure
  run: bin/validate-plugins
```

Would produce two additional detected tools:

| Tool             | Config                       | Command                |
| ---------------- | ---------------------------- | ---------------------- |
| validate-json    | CI workflow (ci.yml, step 6) | `bin/validate-json`    |
| validate-plugins | CI workflow (ci.yml, step 7) | `bin/validate-plugins` |

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
- **cspell**: No auto-fix. Reports spelling errors. Users fix typos in the source or add words to `cspell.json` (`words` array) or a project word list file.
- **npm scripts**: Exit codes depend on the underlying tool.
- **Project scripts**: Try with `--fix` first. If the script does not recognize `--fix`, run without it.
- **CI workflow scripts**: Run exactly as specified in the workflow. These are typically check-only (no auto-fix). Exit code 0 = pass, non-zero = issues found.

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

If all tools passed with zero remaining issues (auto-fix resolved everything), skip step 5 and go directly to step 6. **Auto-fix commands modify files on disk even when they resolve all issues. You must still verify in step 6 and commit in step 7.**

### 5. Fix Remaining Issues

For each remaining issue that auto-fix could not resolve:

1. **Read the tool output** to identify the specific error, file, and line number.
1. **Read the relevant file** at the indicated location.
1. **Apply the fix** based on the error type:
   - **ESLint**: Read the rule from the error code (e.g., `no-unused-vars`), edit the code to comply.
   - **ShellCheck**: Read the SC code (e.g., SC2086), apply the recommended fix (quoting variables, using arrays, etc.).
   - **Markdownlint**: Fix heading levels, line lengths, trailing whitespace, etc.
   - **Knip**: Remove unused exports or dependencies after confirming they are truly unused.
1. **Re-run the tool** on the specific file to verify the fix.

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

**After verification, always proceed to step 7.** Tools that auto-fixed files will have modified files on disk that need to be committed.

### 7. Commit and Push

**This step is required unless --no-commit or --check was specified.** Linters and formatters modify files on disk when they auto-fix. Those changes must be committed even if every tool now reports a clean state.

Skip this step only if:

- **--no-commit** was specified, OR
- **--check** was specified (no changes were made)

Check for file changes and commit:

1. Run `git status --porcelain` and check whether its output is empty.
1. **If no files were modified** (i.e., `git status --porcelain` produced no output): Report "No changes needed, all files were already clean." and stop.
1. **If files were modified** (i.e., `git status --porcelain` produced any output): Stage all modified files and commit them.
1. Generate a conventional commit message:
   - Use `style:` for pure formatting and linting fixes.
   - Use `fix:` if linting changes corrected actual bugs (e.g., unused variables removed, error handling added).
   - Include which tools ran and a brief summary of manual fixes in the commit body.

After committing, push to the remote:

1. **If --no-push was specified**: Stop after committing.
1. Push to the current branch's upstream remote.
1. If no upstream is set, push with `-u` to set it.

## Error Handling

- **No tools detected**: Report that no linters or formatters were found. Suggest common config files the user could add.
- **Tool not installed**: If a config file exists but the tool is not available, report which tool is missing and suggest installation (e.g., `npm install -D eslint`).
- **Execution failure**: Report the error output, then continue with the next tool rather than aborting.
- **Permission errors on project scripts**: Report the error, suggest `chmod +x <script>`.
- **Conflicting tools**: If both a `package.json` lint script and a standalone config (e.g., eslint) are detected, prefer the `package.json` script (it may have project-specific flags). Note the overlap to the user.
- **CI workflow tool requires setup**: Some CI workflow steps depend on GitHub Actions that install a tool (e.g., `mfinelli/setup-shfmt`). If the tool is not locally available, report the missing tool and suggest installation. Reusable workflow calls (e.g., `cboone/gh-actions/.github/workflows/go-ci.yml@v1`) are CI-only and should be skipped entirely.
- **CI workflow command uses CI-only syntax**: Some `run:` commands use GitHub Actions expressions (`${{ }}`) or environment variables only available in CI. Skip these commands and note them as CI-only.
- **Pre-commit hook failure on commit**: Fix the issue, re-stage, and create a new commit (never amend).
