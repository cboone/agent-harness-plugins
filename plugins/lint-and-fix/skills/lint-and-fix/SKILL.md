---
name: lint-and-fix
description: >-
  Run a project's linters and formatters with auto-fix, fix the rest, then
  commit and push. Use for "lint and fix", "run the linters", or "fix lint".
---

# Lint and Fix

Detect project linters and formatters, run them with auto-fix, and resolve remaining issues.

## Options

The user may provide these options inline:

- **--no-commit**: Skip committing and pushing (default: commit and push after fixing)
- **--no-push**: Commit but leave push to the caller or user (default: push after committing)
- **--tool <name>**: Run only a specific tool (e.g., `--tool eslint`, `--tool prettier`)
- **--check**: Run in check-only mode (report issues without fixing)

## Parent Continuation Contract

When another skill invokes `lint-and-fix`, that parent skill may provide an explicit continuation block immediately after the command:

```text
Parent continuation:
- Caller: <parent skill name>
- Resume target: <parent workflow step to resume>
- On lint success: <what the parent must do next>
- On lint failure or skipped required lint work: <what the parent must do next>
```

Honor this block as part of the `lint-and-fix` invocation.

- `--no-push` means "commit fixes, but leave push to the caller or user." It is not a terminal stop when a parent continuation block is supplied.
- Do not ask the user whether to proceed when the continuation block says the parent should continue.
- Do not end with a vague handoff as the terminal outcome. Report the structured result and the caller resume target instead.
- On lint success, no tools detected, or no file changes needed, report the result and allow the parent to continue immediately according to `On lint success`.
- On unresolved lint issues, skipped required lint work, missing required tools, or tool execution failures, report a workflow failure result and list the unresolved items so the parent can follow `On lint failure or skipped required lint work`.
- A tool that [step 2](#2-consult-project-agent-config) downgraded to check mode is **not** skipped required lint work. When it runs in check mode and finds nothing, that is lint success: report it on the `Check-only by project policy` line, leave `Unresolved or skipped` as `none`, and let the parent continue. When it finds issues that step 6 cannot resolve by hand, that is an ordinary failure and belongs under `Unresolved or skipped`.
- A tool recorded as `check-only (no safe check command)` **is** skipped required lint work, because nothing ran and the tree was never checked. Report `Lint status: failure` and list the tool under `Unresolved or skipped` with the reason. It must never reach the parent as success: an unrun tool and a tool that ran clean are opposite results, and a parent such as `pr` would otherwise push a tree no one checked.
- That mode has two sources, and only one of them is policy. Step 2 assigns it when a project rule downgrades a tool and no verified check command exists, and step 4a assigns it when **--check** would otherwise take a write-mode fallback. Name only the first on the `Check-only by project policy` line, since the second is a limit of the user's own dry run and attributing it to the project misreports where the constraint came from. Both still count as skipped required lint work under `Unresolved or skipped`, which is what governs the parent.

Final output for a parent invocation must include:

```text
Lint status: <success|no-tools|failure>
Commit: <none|commit SHA>
Unresolved or skipped: <none|summary>
Check-only by project policy: <none|tool list>
Caller resume target: <target from continuation block>
```

## Workflow

### 1. Detect Available Tools

Check for linter and formatter configuration in the project. Use Glob and Read to find config files and check for installed tools. Run detection checks in parallel where possible.

#### Detection Table

| Config file(s)                                                                    | Tool               | Fix command                                              | Check command                                                  |
| --------------------------------------------------------------------------------- | ------------------ | -------------------------------------------------------- | -------------------------------------------------------------- |
| `eslint.config.*`, `.eslintrc.*`                                                  | eslint             | `npx eslint --fix .`                                     | `npx eslint .`                                                 |
| `.prettierrc*`, `prettier.config.*`, or a `prettier` key in `package.json`        | prettier           | `<package-manager-runner> prettier --write .`            | `<package-manager-runner> prettier --check .`                  |
| `.markdownlint.json`, `.markdownlint.jsonc`, `.markdownlint.yaml`                 | markdownlint       | `npx markdownlint-cli2 --fix "**/*.md"`                  | `npx markdownlint-cli2 "**/*.md"`                              |
| `.markdownlint-cli2.*`                                                            | markdownlint-cli2  | `npx markdownlint-cli2 --fix "**/*.md"`                  | `npx markdownlint-cli2 "**/*.md"`                              |
| Shell scripts in project                                                          | shellcheck         | _(no auto-fix)_                                          | `shellcheck <files>`                                           |
| Shell scripts in project                                                          | shfmt              | `shfmt -w <files>`                                       | `shfmt -d <files>`                                             |
| `knip.json`, `knip.config.*`, `knip.ts`                                           | knip               | _(no auto-fix)_                                          | `npx knip`                                                     |
| `cspell.json`, `cspell.jsonc`, `.cspell.json`, `.cspell.jsonc`, `cspell.config.*` | cspell             | _(no auto-fix)_                                          | `npx cspell --dot .`                                           |
| `package.json` has `lint` script                                                  | npm lint           | Try `npm run lint -- --fix`, fall back to `npm run lint` | `npm run lint`                                                 |
| `package.json` has `format` script                                                | npm format         | `npm run format`                                         | Try `npm run format -- --check`, fall back to `npm run format` |
| `bin/lint`, `scripts/lint`, `script/lint`                                         | Project script     | Try `<script> --fix` first                               | `<script>`                                                     |
| `.github/workflows/*.yml`, `.github/workflows/*.yaml` `run:` steps                | CI workflow script | Run detected command                                     | Run detected command                                           |

The fix commands in this table are defaults, not permissions. [Step 2](#2-consult-project-agent-config) decides which of them may actually run.

Replace `<package-manager-runner>` with the project's local-binary runner: `npx` for npm, `yarn` for Yarn, `pnpm exec` for pnpm, or `bunx` for Bun. Verify that the selected runner resolves the installed project dependency. If Prettier is available only as a verified global installation, use the bare `prettier` command instead; if it is unavailable both locally and globally, report that rather than invoking a runner that may fetch another version. Do not use `npx` in Yarn Plug'n'Play projects, where it may not resolve the locked local binary.

#### Detection Steps

1. **Config files**: Use Glob to check for each config pattern in the project root.
1. **Package.json configuration and scripts**: Read `package.json` for a `prettier` configuration key as well as `lint`, `format`, or `check` scripts. A `prettier` key identifies existing Prettier configuration even when no wrapper script exists.
1. **Shell scripts**: Use Glob to find `**/*.sh`, `bin/*`, `scripts/*`, `script/*`. If shell scripts are present, shellcheck and shfmt apply.
1. **Project lint scripts**: Check for `bin/lint`, `scripts/lint`, `script/lint`.
1. **CI workflow scripts**: Scan CI workflow files for repo-specific linting and validation steps not already covered by other detection methods. See [CI Workflow Detection](#ci-workflow-detection) below.
1. **Tool availability**: Verify detected tools are installed and can be resolved by the selected runner (check the package manager, project dependencies, and `which`). For Prettier, use the project runner only when it resolves the local dependency; if only a global installation is verified, use the bare `prettier` command.

#### CI Workflow Detection

Scan `.github/workflows/*.yml` and `.github/workflows/*.yaml` files to discover repo-specific linting and validation steps that go beyond standard tooling.

1. **Find workflow files**: Use Glob to find `.github/workflows/*.yml` and `.github/workflows/*.yaml`.
1. **Identify lint/validation jobs**: Read each workflow file. Look for jobs or steps whose `name` suggests linting, validation, or code quality (keywords: "lint", "check", "validate", "format", "style", "quality", "verify").
1. **Extract `run:` commands**: From matching jobs and steps, collect all `run:` values.
1. **Skip reusable workflow calls**: If a job uses `uses: org/repo/.github/workflows/workflow.yml@ref` (a reusable workflow call, e.g., `cboone/gh-actions/.github/workflows/run-go-ci.yml@v3.0.0`, `cboone/gh-actions/.github/workflows/run-rust-ci.yml@v3.0.0`, `cboone/gh-actions/.github/workflows/run-zig-ci.yml@v3.0.0`), skip it entirely. Reusable workflows run in CI only and cannot be executed locally. They are not a source of locally-runnable lint commands.
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

Do not apply **--tool** filtering here, and do not stop here when detection finds nothing. [Step 2](#2-consult-project-agent-config) can add commands this table cannot match, such as a spelling check invoked only from `make lint`, so a project whose entry point names one is unreachable if the run ends before the agent config is read. Both the filter and the empty-run exit belong at the end of step 2, once the run is complete.

### 2. Consult Project Agent Config

The detection table reconstructs a plausible lint invocation from the config files on disk. It is a guess. A project may document a different invocation, may require a particular order between tools, and may forbid a specific fix command outright. Fix commands rewrite files, so read the project's own instructions before running any of them. Skipping this step is how the skill ends up performing the exact destructive operation a project prohibits.

Read whichever of these exist: `CLAUDE.md` and `AGENTS.md` in the repository root, and `copilot-instructions.md` under `.github/`. Any of them may be absent, which is normal and not an error, and `CLAUDE.md` is often a symlink to `AGENTS.md`, so read the target rather than reporting a duplicate. Also honor any user-level instructions already present in context.

#### Constraints to Look For

| Constraint                   | What it looks like                                                                                                    | Effect on the run                                                                                                                                                                            |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Forbidden fix command**    | "never pass `--fix` to `markdownlint-cli2`", "this formatter is check-only here", "do not run the fixer on this tree" | Run that tool in check mode only. Do not substitute a different fixer for it, and do not drop the tool.                                                                                      |
| **Prescribed order**         | "run Prettier before the Markdown linter", "`npm run format`, then `npm run lint:md`"                                 | Run the named tools in that order, ahead of tools the config does not mention.                                                                                                               |
| **Documented lint sequence** | a list of the exact commands the project expects, a `make lint` target, "the full lint invocation is ..."             | Run the documented commands verbatim, in place of the table's reconstruction of the same tools, and add any command they name that detection did not find. Prohibitions still apply to them. |
| **Protected paths**          | "`docs/plans/done/` is an append-only historical record", "never reformat generated output"                           | Treat any fixer whose file selection reaches those paths as forbidden unless the project also documents how to exclude them.                                                                 |

#### Precedence

1. **A prohibition outranks every rule below it.** A forbidden fix command and a protected path decide what may not run, so apply them first, and apply them to documented commands too. A documented `npm run format` that wraps a fixer the same config forbids, or whose file selection reaches a protected path, is downgraded to check mode exactly as the table's reconstruction would be. A documented command is evidence of how the project runs a tool, not permission to run one the project prohibits. Report the conflict and both of its sources rather than resolving it silently in either direction.
1. **A documented command beats the table's version of the same tool**, verbatim, including its file selection, once it clears the prohibitions above. Projects narrow a tool's inputs on purpose: a `git ls-files`-driven `shfmt` invocation exists because `shfmt` does not read `.gitignore`, so a tree walk reaches vendored and generated scripts. Do not widen such a command back to a glob, and do not "improve" it.
1. **A documented order beats the table's order.** The detection table has no notion of ordering between two tools that claim the same files, so two fixers over `**/*.md` will fight without it.
1. **A documented sequence may name commands detection did not find.** A project entry point can include a checker that has no config file for the table to match, such as a spelling or typo check invoked only from `make lint`. Add those commands to the run, deduplicate them against the detected tools they already cover, and apply any **--tool** filter afterward, so the filter selects from everything that will run rather than from detection alone. Otherwise the skill promises to honor the project's entry point and then silently drops part of it.
1. **Detection still supplies everything the config does not mention.** Consulting the agent config narrows, reorders, downgrades, and extends the run; it does not replace detection. Keep every other detected tool.

#### Record the Outcome

For each tool in the run, whether detection found it or the agent config named it, carry these forward into the remaining steps:

- **Mode**: `fix`, `check-only (project policy)`, `check-only (no auto-fix)`, or `check-only (no safe check command)`
- **Command**: the command that will actually run
- **Source**: for a policy downgrade, the file and the rule, quoted in one line

**A policy downgrade needs a command that is verified not to write.** Two rows of the detection table fall back to a write-mode command when no check-mode form is available: the `format` script tries `npm run format -- --check` and falls back to `npm run format`, and the project-script row runs `<script>` without `--fix`, whose default behavior may still fix. Taking either fallback for a downgraded tool performs the write the project prohibits. So for a downgraded tool, use only a command whose check-only behavior is established, from the project's own documentation or from the tool's documented check flag. If no such command exists, do not fall back: record the tool as `check-only (no safe check command)`, run nothing for it, and report it alongside the downgrade and its source.

**A downgrade is never silent.** A tool moved to check mode by project policy must be reported as such in steps 3, 5, and 7, and on the `Check-only by project policy` line of the [Parent Continuation Contract](#parent-continuation-contract). "The fixer ran and found nothing" and "the fixer was not permitted to run" are different results, and a report that collapses them lets a skipped fixer read as a clean tree.

**If the user's invocation conflicts with a project rule**, for example `--tool markdownlint` in a repository that forbids `markdownlint --fix`, do not resolve it silently in either direction. Run the tool in check mode, report the conflict and its source, and let the user decide whether to override it.

If **no agent config files exist**, or none of them constrain linting, note that and run the detection table as-is. That is the common case and not an error.

#### Close the Run

The run is now complete, so apply the two gates step 1 deferred:

1. If **--tool <name>** was specified, filter the run to only that tool. Match against every tool in the run, including any the agent config added, so a documented entry point's own tools can be selected. If the named tool is in neither detection nor the config, report that and stop.
1. If **the run is empty**, report that no linters or formatters were found. If a parent continuation block was supplied, report `Lint status: no-tools`, include the caller resume target, and allow the parent workflow to continue according to its continuation block. Otherwise stop.

### 3. Present Detected Tools

Before running, display the detected tools, in the order they will run:

```text
## Detected Linters and Formatters

| Tool | Config | Command | Mode |
|------|--------|---------|------|
| prettier | .prettierrc.json | npx prettier --write . | fix |
| eslint | eslint.config.js | npx eslint --fix . | fix |
| markdownlint-cli2 | .markdownlint-cli2.jsonc | npx markdownlint-cli2 "**/*.md" | check-only (project policy) |
| shellcheck | (shell scripts found) | shellcheck bin/* | check-only (no auto-fix) |
```

Below the table, cite the source of every `check-only (project policy)` mode and of any ordering step 2 imposed:

```text
markdownlint-cli2: check-only per CLAUDE.md -- "never pass --fix to markdownlint-cli2"
prettier before markdownlint-cli2, per CLAUDE.md -- "run Prettier before the Markdown linter"
```

If running in **--check** mode, show check commands instead of fix commands. **--check** applies to every tool; a project policy downgrade applies to one tool and still has to be cited.

### 4. Run Each Tool

Run every tool in the run sequentially, in the order presented in step 3, including any the agent config added in step 2. For each tool:

#### 4a. Run the Command

Run the command step 2 recorded for that tool: its fix command, its check command where the project forbids fixing, or its check command if **--check** was specified. Capture stdout, stderr, and exit code.

**--check** is subject to the same rule as a policy downgrade. The detection table's check commands fall back to a write-mode form in two rows, so running them for a `--check` invocation would modify files in what the user asked to be a dry run. Use only a command whose check-only behavior is established; where none exists, record the tool as `check-only (no safe check command)`, run nothing for it, and report it as above.

**Tool-specific notes:**

- **eslint**: Exit code 0 = clean, 1 = issues found. Parse output for remaining error/warning counts.
- **prettier**: Exit code 0 = all clean, 1 = unformatted files found (check mode) or write errors.
- **markdownlint-cli2**: Exit code 0 = clean, 1 = issues found. With `--fix`, some issues auto-fix and others remain. `--fix` also ignores the paths given on the command line and rewrites every file matching the `globs` in its config, so its blast radius is the whole configured tree no matter how the invocation is narrowed.
- **shellcheck**: No auto-fix. All issues reported for manual resolution.
- **shfmt**: With `-w`, formats in place silently. With `-d`, shows diffs.
- **knip**: No auto-fix. Reports unused files, dependencies, and exports.
- **cspell**: No auto-fix. Runs with `--dot` so dotfiles and dot-directories match CI spell-check behavior. Users fix typos in the source or add words to `cspell.json` (`words` array) or a project word list file. In git worktrees, `--dot` can expose the `.git` file; if that happens, add `.git` as well as `.git/` to the project's cspell ignore paths.
- **npm scripts**: Exit codes depend on the underlying tool.
- **Project scripts**: Try with `--fix` first, unless step 2 downgraded the script to check mode. If the script does not recognize `--fix`, run without it.
- **CI workflow scripts**: Run exactly as specified in the workflow. These are typically check-only (no auto-fix). Exit code 0 = pass, non-zero = issues found.

#### 4b. Record Results

For each tool, record:

- **Tool**: Name
- **Mode**: The mode step 2 assigned
- **Exit code**: 0 (success) or non-zero
- **Files fixed**: Count from output (if available)
- **Remaining issues**: Count and summary of what auto-fix could not resolve
- **Output**: Full output for reference

### 5. Report Results

After all tools run, display a summary:

```text
## Lint and Fix Results

| Tool | Status | Fixed | Remaining |
|------|--------|-------|-----------|
| prettier | Ran with fixes | 5 files | 0 |
| eslint | Ran with fixes | 3 files | 2 errors |
| markdownlint-cli2 | Checked only (fix not permitted) | n/a | 0 |
| shellcheck | Check only (no auto-fix) | n/a | 4 warnings |
```

Keep these statuses distinct, because they mean different things about the tree:

- **`Ran with fixes`**: a fixer ran and corrected files.
- **`Pass`**: the tool's check came back clean. It says the tree is clean, not that a fixer ran, so it is the right status for a tool with no fixer and for one running in check mode.
- **`Checked only (fix not permitted)`**: step 2 downgraded the tool. A zero in the `Remaining` column here is a clean result, not a skipped one, but the run still did no fixing, so anything the fixer would have corrected is still uncorrected and appears as a remaining issue instead.
- **`Check only (no auto-fix)`**: the tool has no fixer at all.
- **`Not run (no safe check command)`**: step 2 could not find a command for this tool that is verified not to write, so nothing ran and the tree is unchecked for it. This is never a pass. Put it in the `Status` column, leave `Fixed` as `n/a`, put `unknown` in `Remaining` rather than a zero, and carry it into step 7 and into `Unresolved or skipped`.

Repeat the citation for each `Checked only (fix not permitted)` row below the table.

If **--check** was specified, show results and stop here.

If all tools passed with zero remaining issues (auto-fix resolved everything), skip step 6 and go directly to step 7. **Auto-fix commands modify files on disk even when they resolve all issues. You must still verify in step 7 and commit in step 8.**

### 6. Fix Remaining Issues

**Check the reported path before editing anything.** A protected path is protected from hand edits whatever reported the finding, so this guard applies to every tool, not only to one step 2 downgraded. A tool with no fixer, or an ordinary tool whose output happens to point at a protected file, reaches this step without passing through any downgrade, and a targeted edit there writes to the tree the project told you not to touch. Leave those findings alone, report them under `Unresolved or skipped` with the path and the rule that protects it, and remediate only where the project documents an exception.

For each remaining issue that auto-fix could not resolve, and whose file is not protected:

1. **Read the tool output** to identify the specific error, file, and line number.
1. **Read the relevant file** at the indicated location.
1. **Apply the fix** based on the error type:
   - **ESLint**: Read the rule from the error code (e.g., `no-unused-vars`), edit the code to comply.
   - **ShellCheck**: Read the SC code (e.g., SC2086), apply the recommended fix (quoting variables, using arrays, etc.).
   - **Markdownlint**: Fix heading levels, line lengths, trailing whitespace, etc.
   - **Knip**: Remove unused exports or dependencies after confirming they are truly unused.
1. **Re-run the tool** on the specific file to verify the fix.

For a tool step 2 downgraded to check mode, resolve its findings with targeted edits to the reported files. Do not reach for the forbidden fixer here, and do not invoke it with a narrower glob: the prohibition is on the command, not on the breadth of a single invocation, and tools such as `markdownlint-cli2 --fix` ignore the paths given to them and rewrite everything matching their configured globs anyway.

The protected-path guard above covers this case too: where the downgrade came from a protected path rather than a forbidden command, a targeted edit defeats the protection just as the fixer would.

If a remaining issue is ambiguous or risky to fix automatically (e.g., removing a dependency that might be used dynamically, or a lint rule that conflicts with project intent), skip it and report:

```text
Skipped: <file>:<line> -- <rule> -- <reason>
```

### 7. Final Verification

Re-run every tool in the run one final time in check mode to confirm a clean state, including any the agent config added in step 2. Verifying only the detected ones lets a config-only command such as a spelling or workflow check go unverified and be committed anyway. A tool recorded as `check-only (no safe check command)` cannot be re-run: carry its row through as `Not run (no safe check command)` rather than omitting it or letting it read as `Pass`. Here too `Pass` means the check came back clean, which is why a tool with no fixer and a tool running in check mode both earn it.

```text
## Final Verification

| Tool | Status |
|------|--------|
| prettier | Pass |
| eslint | Pass |
| markdownlint-cli2 | Pass (fix mode not permitted) |
| shellcheck | Pass (1 advisory skipped) |
```

Carry the policy annotation into this table too. Every tool runs in check mode here, so without it a downgraded tool's row is indistinguishable from one whose fixer ran.

**After verification, always proceed to step 8.** Tools that auto-fixed files will have modified files on disk that need to be committed.

### 8. Commit and Push

**This step is required unless --no-commit or --check was specified.** Linters and formatters modify files on disk when they auto-fix. Those changes must be committed even if every tool now reports a clean state.

Skip this step only if:

- **--no-commit** was specified, OR
- **--check** was specified (no changes were made)

Check for file changes and commit:

1. Run `git status --porcelain` and check whether its output is empty.
1. **If no files were modified** (i.e., `git status --porcelain` produced no output): Report "No changes needed, all files were already clean." If a parent continuation block was supplied, include the final output required by [Parent Continuation Contract](#parent-continuation-contract) and allow the parent workflow to continue according to its continuation block. Otherwise stop.
1. **If files were modified** (i.e., `git status --porcelain` produced any output): Stage all modified files and commit them.
1. Generate a conventional commit message:
   - Use `style:` for pure formatting and linting fixes.
   - Use `fix:` if linting changes corrected actual bugs (e.g., unused variables removed, error handling added).
   - Include which tools ran and a brief summary of manual fixes in the commit body.

After committing, push to the remote:

1. **If --no-push was specified without a parent continuation block**: Report the final lint status and commit SHA, then stop.
1. **If --no-push was specified with a parent continuation block**: Report the final output required by [Parent Continuation Contract](#parent-continuation-contract), including the caller resume target. The parent workflow should then continue according to its continuation block without asking the user for confirmation.
1. Push to the current branch's upstream remote.
1. If no upstream is set, push with `-u` to set it.

## Error Handling

- **No tools detected**: Report that no linters or formatters were found. Suggest common config files the user could add.
- **Tool not installed**: If a config file exists but the tool is not available, report which tool is missing and suggest installation (e.g., `npm install -D eslint`).
- **Execution failure**: Report the error output, then continue with the next tool rather than aborting.
- **Permission errors on project scripts**: Report the error, suggest `chmod +x <script>`.
- **Conflicting tools**: If both a `package.json` lint script and a standalone config (e.g., eslint) are detected, prefer the `package.json` script (it may have project-specific flags). Note the overlap to the user. A command documented in the project's agent config outranks both.
- **Agent config is ambiguous about a fixer**: If a rule reads as a prohibition but could also be read as a preference, treat it as a prohibition, run the tool in check mode, and say which reading was taken and why. The cost of an unnecessary check-only run is a slower loop; the cost of an unnecessary fix run is rewritten files.
- **Agent config forbids the only fixer for a file type**: Report that the file type has no permitted fixer, run the check, and resolve findings by hand in step 6. Do not fall back to a different fixer for the same files unless the agent config names it as the sanctioned one.
- **CI workflow tool requires setup**: Some CI workflow steps depend on GitHub Actions that install a tool (e.g., `mfinelli/setup-shfmt`). If the tool is not locally available, report the missing tool and suggest installation. Reusable workflow calls (e.g., `cboone/gh-actions/.github/workflows/run-go-ci.yml@v3.0.0`, `cboone/gh-actions/.github/workflows/run-rust-ci.yml@v3.0.0`, `cboone/gh-actions/.github/workflows/run-zig-ci.yml@v3.0.0`) are CI-only and should be skipped entirely.
- **CI workflow command uses CI-only syntax**: Some `run:` commands use GitHub Actions expressions (`${{ }}`) or environment variables only available in CI. Skip these commands and note them as CI-only.
- **Pre-commit hook failure on commit**: Fix the issue, re-stage, and create a new commit (never amend).
