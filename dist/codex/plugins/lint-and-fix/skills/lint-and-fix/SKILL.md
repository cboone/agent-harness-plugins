---
name: lint-and-fix
description: >-
  Run a project's linters and formatters with auto-fix, fix the rest, then
  commit and push. Use for "lint and fix", "run the linters", or "fix lint", not
  to format one file; to configure linters, use set-up-linters.
argument-hint: "[--no-commit] [--no-push] [--tool <name>] [--check]"
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

Only **enforced** tools govern lint failure, `Unresolved or skipped`, and the push/parent continuation gate. Tools classified as **inferred only** below are advisory: their findings, missing tools, execution errors and unavailable safe checks belong solely on `Advisory (not enforced by project)`, never in required-work failures. Report their actual outcome, including unknown counts, rather than calling an unrun check clean. Host restrictions on required work remain failures.

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
- An enforced tool recorded as `check-only (no safe check command)` **is** skipped required lint work, because nothing ran and the tree was never checked. Report `Lint status: failure` and list the tool under `Unresolved or skipped` with the reason. It must never reach the parent as success: an unrun tool and a tool that ran clean are opposite results, and a parent such as `pr` would otherwise push a tree no one checked.
- That mode has two sources, and only one of them is policy. Step 2 assigns it when a project rule downgrades a tool and no verified check command exists, and step 4a assigns it when **--check** would otherwise take a write-mode fallback. Name only the first on the `Check-only by project policy` line, since the second is a limit of the user's own dry run and attributing it to the project misreports where the constraint came from. For enforced tools, both still count as skipped required lint work under `Unresolved or skipped`, which is what governs the parent.

Map successful lint work to `Status: success`, a clean no-change result to `no-op`, and failed or skipped required work to `failure`. A question without an answer returns `needs-decision` to the parent without asking independently. A host restriction is a failure, never `no-tools`. Existing `Lint status` values remain unchanged.

Final output for a parent invocation must include:

```text
Status: <success|no-op|failure|unavailable|needs-decision>
Lint status: <success|no-tools|failure>
Commit: <none|commit SHA>
Unresolved or skipped: <none|summary>
Check-only by project policy: <none|tool list>
Advisory (not enforced by project): <none|tool findings or reason not checked>
Caller resume target: <target from continuation block>
```

## Capabilities and authority

Use the tools this session actually offers. For a question, use a structured question tool when available in the active mode; otherwise present numbered choices and wait. In a noninteractive run, report the unresolved question and preserved state instead of choosing an answer. Tool names such as Write, Read, Glob and AskUserQuestion below are examples: perform the same file or question operation with the host's supported mechanism. Write a body file completely before issuing the command that reads it; never batch those dependent operations.

Prior user authorization carries through the workflow; add no confirmation merely because the harness differs. Host approvals, active Plan or read-only mode, writable roots and network policy still apply. Stop before a prohibited write or any step dependent on a blocked operation, preserve state, and report the exact command and restriction. Never bypass controls or claim an unrun step completed. Separate completed, skipped, blocked and failed work in the result. For invocation hints, render the named skill with the running harness's form: slash invocation in Claude Code, dollar mention or the skills selector in Codex. A mention is not a tool call; load composed skills from their advertised locations.

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
1. **Shell scripts**: Use Glob to find `**/*.sh`, `bin/*`, `scripts/*`, `script/*`. If shell scripts are present, add shellcheck and shfmt as inferred-only candidates pending enforcement classification.
1. **Project lint scripts**: Check for `bin/lint`, `scripts/lint`, `script/lint`.
1. **CI workflow scripts**: Scan CI workflow files for repo-specific linting and validation steps not already covered by other detection methods. See [CI Workflow Detection](#ci-workflow-detection) below.
1. **Tool availability**: After step 2 classifies enforcement, verify detected tools are installed and can be resolved by the selected runner (check the package manager, project dependencies, and `which`). For Prettier, use the project runner only when it resolves the local dependency; if only a global installation is verified, use the bare `prettier` command.

#### CI Workflow Detection

Scan `.github/workflows/*.yml` and `.github/workflows/*.yaml` files to discover repo-specific linting and validation steps that go beyond standard tooling.

1. **Find workflow files**: Use Glob to find `.github/workflows/*.yml` and `.github/workflows/*.yaml`.
1. **Identify lint/validation jobs**: Read each workflow file. Look for jobs or steps whose `name` suggests linting, validation, or code quality (keywords: "lint", "check", "validate", "format", "style", "quality", "verify").
1. **Extract `run:` commands**: From matching jobs and steps, collect all `run:` values.
1. **Skip reusable workflow calls**: If a job uses `uses: org/repo/.github/workflows/workflow.yml@ref` (a reusable workflow call, e.g., `cboone/gh-actions/.github/workflows/run-go-ci.yml@v4.1.0`, `cboone/gh-actions/.github/workflows/run-rust-ci.yml@v4.1.0`, `cboone/gh-actions/.github/workflows/run-zig-ci.yml@v4.1.0`), do not execute the workflow locally. Its explicit tool selection can establish enforcement, but the workflow call alone is not a locally-runnable lint command. Preserve that evidence for classification below.
1. **Filter for repo-specific scripts**: Keep commands that invoke project scripts (paths starting with `bin/`, `scripts/`, `script/`, `./bin/`, `./scripts/`, or `./script/`). These are repo-specific validation tools. Also keep commands that invoke standalone tools not already covered by the detection table (e.g., `actionlint`, `taplo check`).
1. **Deduplicate**: Merge enforcement evidence into existing entries before excluding duplicate commands. Prefer the repository command and its file selection over a table default. Exclude any commands already covered by earlier detection steps. For example, if `shellcheck` was already detected from shell scripts in the project, do not add a duplicate entry from the CI workflow. Similarly, if `bin/lint` was already detected as a project lint script, skip it.
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

#### Classify Enforcement

Before selecting runnable commands, inspect tool configs (including tool-specific sections in shared configs), pre-commit configuration/hooks, CI, Makefile targets, package/project lint scripts, agent instructions and tests that execute linters. Add enforced checks absent from the table. Follow referenced local wrappers far enough to identify tools, arguments, allowlists and input scopes; a dependency declaration, filename match or incidental mention alone is not enforcement. A prohibition alone limits authority and does not require a tool to run.

For each tool record **Enforcement** (`enforced` or `inferred only`) and **Evidence** (file and relevant setting, hook, command or test; for inference, the matching file pattern and absence of an enforcement signal). A tool-specific config or an explicit project check establishes enforcement. Retain evidence when deduplicating, including tool selection in reusable CI workflows; retain the existing exclusion of CI-only workflow calls from the local run, report that coverage separately, and use a project-specified local equivalent when available. Missing tools or unsafe checks for required local commands still fail. Preserve existing exclusions and allowlists, including tests that wrap a tool, rather than substituting an unrestricted direct invocation.

With no enforcement signal, keep the tool **inferred only**. Use `check-only (advisory)` with a verified non-writing check command, or `check-only (no safe check command)` with command `none`. Never run an inferred-only fixer or remediate its findings by hand. `--tool` filters selection without promoting inference to enforcement or authorizing writes. Project prohibitions and protected paths still apply to advisory checks.

#### Constraints to Look For

| Constraint                   | What it looks like                                                                                                    | Effect on the run                                                                                                                                                                                                                                                                  |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Forbidden fix command**    | "never pass `--fix` to `markdownlint-cli2`", "this formatter is check-only here", "do not run the fixer on this tree" | Put that tool in check mode, subject to [the No-Write Rule](#the-no-write-rule): where no command qualifies, it runs nothing. Do not substitute a different fixer for it, and do not drop the tool from the run, which means keep reporting it rather than execute it at any cost. |
| **Prescribed order**         | "run Prettier before the Markdown linter", "`npm run format`, then `npm run lint:md`"                                 | Run the named tools in that order, ahead of tools the config does not mention.                                                                                                                                                                                                     |
| **Documented lint sequence** | a list of the exact commands the project expects, a `make lint` target, "the full lint invocation is ..."             | Run the documented commands verbatim, in place of the table's reconstruction of the same tools, and add any command they name that detection did not find. Prohibitions still apply to them.                                                                                       |
| **Protected paths**          | "`docs/plans/done/` is an append-only historical record", "never reformat generated output"                           | Treat any fixer whose file selection reaches those paths as forbidden unless the project also documents how to exclude them.                                                                                                                                                       |

#### Precedence

1. **A prohibition outranks every rule below it.** A forbidden fix command and a protected path decide what may not run, so apply them first, and apply them to documented commands too. A documented `npm run format` that wraps a fixer the same config forbids, or whose file selection reaches a protected path, is downgraded to check mode exactly as the table's reconstruction would be. A documented command is evidence of how the project runs a tool, not permission to run one the project prohibits. Report the conflict and both of its sources rather than resolving it silently in either direction.
1. **A documented command beats the table's version of the same tool**, verbatim, including its file selection, once it clears the prohibitions above. Projects narrow a tool's inputs on purpose: a `git ls-files`-driven `shfmt` invocation exists because `shfmt` does not read `.gitignore`, so a tree walk reaches vendored and generated scripts. Do not widen such a command back to a glob, and do not "improve" it.
1. **A documented order beats the table's order.** The detection table has no notion of ordering between two tools that claim the same files, so two fixers over `**/*.md` will fight without it.
1. **A documented sequence may name commands detection did not find.** A project entry point can include a checker that has no config file for the table to match, such as a spelling or typo check invoked only from `make lint`. Add those commands to the run, deduplicate them against the detected tools they already cover, and apply any **--tool** filter afterward, so the filter selects from everything that will run rather than from detection alone. Otherwise the skill promises to honor the project's entry point and then silently drops part of it. A documented command the sequence names separately is selectable like any other tool; one the sequence only wraps is not, and [Close the Run](#close-the-run) says what to do about that.
1. **Detection still supplies everything the config does not mention.** Consulting the agent config narrows, reorders, downgrades, and extends the run; it does not replace detection. Keep every other detected tool with its enforcement classification; inference alone never authorizes fixing.

#### Record the Outcome

For each tool in the run, whether detection found it or the agent config named it, carry these forward into the remaining steps:

- **Mode**: `fix`, `check-only (project policy)`, `check-only (no auto-fix)`, `check-only (user requested --check)`, `check-only (advisory)`, or `check-only (no safe check command)`
- **Command**: the command that will actually run in step 4
- **Check command**: the command step 7 will re-run to verify, or `none`
- **Source**: for a policy downgrade, the file and the rule, quoted in one line

**Record the check command separately, for every tool, including one in `fix` mode.** A tool that fixes runs its fix command in step 4 and still has to be verified in step 7, and step 7 is forbidden to reconstruct a command or take a fallback. Without its own field there is nothing for that step to use, so the run either re-invokes the writer or drops the tool. The two fields are the same command whenever the tool is already in a check-only mode, and `none` for `check-only (no safe check command)`, which is what makes that mode unrunnable in both steps rather than only in step 4.

**--check** sets `check-only (user requested --check)` for every tool in the run that would otherwise be `fix`, and the recorded command becomes that tool's check command. Record it here rather than leaving `Mode: fix` in place, or steps 3, 5 and 7 will present a dry run as though a fixer ran. It does not override a mode already assigned for another reason: a tool the project downgraded keeps `check-only (project policy)`, since that is the constraint worth reporting, and a tool with no fixer keeps `check-only (no auto-fix)`.

#### The No-Write Rule

**Whenever a tool is in any check-only mode, its command must be one that is verified not to write.** This holds wherever a check-mode command is chosen: when step 2 records one, when **--check** replaces a fix command, when step 4's tool-specific notes suggest a form, and when step 7 re-runs the tool. Every one of those is a place the run can quietly write to a tree the user or the project expected it to leave alone.

The detection table is the reason this needs saying, because three of its rows fall back to a write-mode command when no check form is available:

| Row             | Check command falls back to         | Why that writes                       |
| --------------- | ----------------------------------- | ------------------------------------- |
| `lint` script   | `npm run lint` after `-- --fix`     | the script's default behavior may fix |
| `format` script | `npm run format` after `-- --check` | it is the writer                      |
| Project script  | `<script>` without `--fix`          | the script's default behavior may fix |

Treat that list as illustrative, not exhaustive: any command whose check behavior is not established falls under the rule. A command qualifies when the project's own documentation or the tool's documented check flag establishes it does not write. Where none qualifies, do not fall back. Record the tool as `check-only (no safe check command)`, run nothing for it, and report it with the reason and, for a policy downgrade, its source.

**A downgrade is never silent.** A tool moved to check mode by project policy must be reported as such in steps 3, 5, and 7, and on the `Check-only by project policy` line of the [Parent Continuation Contract](#parent-continuation-contract). "The fixer ran and found nothing" and "the fixer was not permitted to run" are different results, and a report that collapses them lets a skipped fixer read as a clean tree.

**If the user's invocation conflicts with a project rule**, for example `--tool markdownlint` in a repository that forbids `markdownlint --fix`, do not resolve it silently in either direction. Run the tool in check mode, report the conflict and its source, and let the user decide whether to override it.

If **no agent config files exist**, or none of them constrain linting, note that and retain the detection candidates with their enforcement classification. Absence of agent config does not make inferred tools enforced. That is the common case and not an error.

#### Close the Run

The run is now complete, so apply the two gates step 1 deferred:

1. If **--tool <name>** was specified, filter the run to only that tool. Match against every tool in the run, including any the agent config added, so a documented entry point's own tools can be selected. If the named tool is in neither detection nor the config, report that and stop.

   **An aggregate documented command is indivisible, so it can conflict with this filter.** When the named tool is reachable only inside one, as `prettier` is in a project whose documented sequence is `make lint`, there is no filtered run to produce. Running the aggregate would execute the other tools the user excluded, and reconstructing the tool's own command would substitute this skill's version for the project's, which [precedence rule 2](#precedence) forbids. Do neither, and do not expand the aggregate into its parts. Report a selection conflict instead: name the tool, the aggregate command that contains it, and the file and rule that documented it, then stop and let the user choose between running the documented command whole and dropping the filter. This matches how step 2 already handles a `--tool` request that a project rule forbids, and it leaves the choice with the person who can make it.

1. If **the run is empty**, report that no linters or formatters were found. If a parent continuation block was supplied, report `Lint status: no-tools`, include the caller resume target, and allow the parent workflow to continue according to its continuation block. Otherwise stop.

### 3. Present Detected Tools

Before running, display the detected tools, in the order they will run:

```text
## Detected Linters and Formatters

| Tool | Evidence | Enforcement | Command | Mode |
|------|----------|-------------|---------|------|
| prettier | .prettierrc.json | enforced | npx prettier --write . | fix |
| eslint | eslint.config.js | enforced | npx eslint --fix . | fix |
| markdownlint-cli2 | .markdownlint-cli2.jsonc | enforced | npx markdownlint-cli2 "**/*.md" | check-only (project policy) |
| shellcheck | shell files only; no enforcement signal | inferred only | shellcheck bin/* | check-only (advisory) |
```

Below the table, cite the source of every `check-only (project policy)` mode and of any ordering step 2 imposed:

```text
markdownlint-cli2: check-only per CLAUDE.md -- "never pass --fix to markdownlint-cli2"
prettier before markdownlint-cli2, per CLAUDE.md -- "run Prettier before the Markdown linter"
```

If running in **--check** mode, show check commands instead of fix commands. **--check** applies to every tool; a project policy downgrade applies to one tool and still has to be cited.

### 4. Run Each Tool

Run every tool in the run sequentially, in the order presented in step 3, including any the agent config added in step 2. For each tool:

**Except `check-only (no safe check command)`.** That mode means step 2 found nothing safe to run, so its `Command` is `none` and there is nothing to execute. Skip it here rather than reaching for the writer it was denied or improvising a command, report it as unresolved if enforced or advisory if inferred only, and carry it into steps 5 and 7 with its status.

#### 4a. Run the Command

Run the command step 2 recorded for that tool: its fix command, its check command where the project forbids fixing, or its check command if **--check** was specified. Capture stdout, stderr, and exit code.

Run exactly the recorded command. Do not reconstruct one here, and do not take a fallback the recording rejected: for any check-only mode, including a **--check** dry run, [the No-Write Rule](#the-no-write-rule) already decided what may run.

**Tool-specific notes:**

- **eslint**: Exit code 0 = clean, 1 = issues found. Parse output for remaining error/warning counts.
- **prettier**: Exit code 0 = all clean, 1 = unformatted files found (check mode) or write errors.
- **markdownlint-cli2**: Exit code 0 = clean, 1 = issues found. With `--fix`, some issues auto-fix and others remain. `--fix` also ignores the paths given on the command line and rewrites every file matching the `globs` in its config, so its blast radius is the whole configured tree no matter how the invocation is narrowed.
- **shellcheck**: No auto-fix. All issues reported for manual resolution.
- **shfmt**: With `-w`, formats in place silently. With `-d`, shows diffs.
- **knip**: No auto-fix. Reports unused files, dependencies, and exports.
- **cspell**: No auto-fix. Runs with `--dot` so dotfiles and dot-directories match CI spell-check behavior. Users fix typos in the source or add words to `cspell.json` (`words` array) or a project word list file. In git worktrees, `--dot` can expose the `.git` file; if that happens, add `.git` as well as `.git/` to the project's cspell ignore paths.
- **npm scripts**: Exit codes depend on the underlying tool.
- **Project scripts**: Try with `--fix` first, but only for a tool in `fix` mode. In any check-only mode, run the recorded command and nothing else: falling back to a bare `<script>` because it does not recognize `--fix` would perform the write that [the No-Write Rule](#the-no-write-rule) exists to prevent.
- **CI workflow scripts**: Run exactly as specified in the workflow. These are typically check-only (no auto-fix). Exit code 0 = pass, non-zero = issues found.

#### 4b. Record Results

For each tool, record:

- **Tool**: Name
- **Enforcement and evidence**: The classification and source step 2 recorded
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
```

Report inferred-only outcomes separately, outside the enforced results table:

```text
Advisory (not enforced by project): shellcheck (4 warnings), shfmt (unavailable; not checked)
```

Only enforced findings proceed to step 6 or gate success. Advisory-only runs can succeed with findings and `Unresolved or skipped: none`; they are not `no-tools` when advisory checks ran. Apply this classification even when `--check` ends the workflow here, including the structured parent result.

Keep these statuses distinct, because they mean different things about the tree:

- **`Ran with fixes`**: a fixer ran and corrected files.
- **`Pass`**: the tool's check came back clean. It says the tree is clean, not that a fixer ran, so it is the right status for a tool with no fixer and for one running in check mode.
- **`Checked only (fix not permitted)`**: step 2 downgraded the tool. A zero in the `Remaining` column here is a clean result, not a skipped one, but the run still did no fixing, so anything the fixer would have corrected is still uncorrected and appears as a remaining issue instead.
- **`Check only (no auto-fix)`**: the tool has no fixer at all.
- **`Check only (--check requested)`**: the user asked for a dry run, so a tool that would have fixed did not. Nothing on disk changed, and anything its fixer would have corrected is still uncorrected.
- **`Not run (no safe check command)`**: step 2 could not find a command for this tool that is verified not to write, so nothing ran and the tree is unchecked for it. This is never a pass. Put it in the `Status` column, leave `Fixed` as `n/a`, put `unknown` in `Remaining` rather than a zero, and carry enforced entries into step 7 and into `Unresolved or skipped`; inferred-only entries stay advisory.

Repeat the citation for each `Checked only (fix not permitted)` row below the table.

If **--check** was specified, show results and stop here.

If all tools passed with zero remaining issues (auto-fix resolved everything), skip step 6 and go directly to step 7. **Auto-fix commands modify files on disk even when they resolve all issues. You must still verify in step 7 and commit in step 8.**

### 6. Fix Remaining Issues

**Remediate enforced findings only. Check the reported path before editing anything.** A protected path is protected from hand edits whatever reported the finding, so this guard applies to every tool, not only to one step 2 downgraded. A tool with no fixer, or an ordinary tool whose output happens to point at a protected file, reaches this step without passing through any downgrade, and a targeted edit there writes to the tree the project told you not to touch. Leave those findings alone, report them under `Unresolved or skipped` with the path and the rule that protects it, and remediate only where the project documents an exception.

For each remaining **enforced** issue that auto-fix could not resolve, and whose file is not protected:

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

Re-run every tool in the run one final time in check mode to confirm a clean state, including any the agent config added in step 2. Verifying only the detected ones lets a config-only command such as a spelling or workflow check go unverified and be committed anyway.

Every tool is in check mode here, so [the No-Write Rule](#the-no-write-rule) governs this step in full: use each tool's recorded check command, and never a write-mode fallback, or verification itself rewrites the tree it was meant to inspect. A tool that has no qualifying command, whether recorded that way in step 2 or found to have none here, is carried through as `Not run (no safe check command)` rather than omitted or allowed to read as `Pass`. Here too `Pass` means the check came back clean, which is why a tool with no fixer and a tool running in check mode both earn it.

```text
## Final Verification

| Tool | Status |
|------|--------|
| prettier | Pass |
| eslint | Pass |
| markdownlint-cli2 | Pass (fix mode not permitted) |
```

Report advisory verification outcomes on their separate line, including any failed or unrun advisory checks; do not label those as passes. Carry the policy annotation into this table too. Every tool runs in check mode here, so without it a downgraded tool's row is indistinguishable from one whose fixer ran.

**After verification, proceed to step 8 to commit.** Tools that auto-fixed files will have modified files on disk, and those changes must be committed rather than left in the working tree, so this transition happens even when verification reported problems.

**The push is gated on verification, the commit is not.** If any **enforced** tool ends verification as `Not run (no safe check command)`, or with unresolved findings, step 8 commits what is on disk and stops there. Do not push, and report the run as a lint failure with those tools listed under `Unresolved or skipped`. A commit keeps the fixes that did run; a push publishes a tree where a required tool was never checked, which is the outcome the unrun mode exists to flag. Under a parent continuation block this is the `On lint failure or skipped required lint work` path, so the parent decides what happens next.

**The failure survives every exit from step 8.** The gate suppresses the push; it never adds a commit, and it never turns into a success because nothing needed committing:

- With **--no-commit**, step 8 is skipped as usual. Report the lint failure and its unresolved items, and do not commit in order to satisfy this gate.
- With a clean `git status`, report that no changes were needed **and** the lint failure, rather than "all files were already clean" on its own. A tree that was already clean is not a tree that was checked, so the parent still takes the failure path.

### 8. Commit and Push

**This step is required unless --no-commit or --check was specified.** Linters and formatters modify files on disk when they auto-fix. Those changes must be committed even if every tool now reports a clean state.

Skip this step only if:

- **--no-commit** was specified, OR
- **--check** was specified (no changes were made)

Check for file changes and commit:

1. Run `git status --porcelain` and check whether its output is empty.
1. **If no files were modified** (i.e., `git status --porcelain` produced no output): Report "No file changes needed." If verification left any **enforced** tool `Not run (no safe check command)` or with unresolved findings, report that failure alongside it, because a clean tree is not a checked one. If a parent continuation block was supplied, include the final output required by [Parent Continuation Contract](#parent-continuation-contract) and allow the parent workflow to continue according to its continuation block, which is the failure path in that case. Otherwise stop.
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
- **Agent config is ambiguous about a fixer**: If a rule reads as a prohibition but could also be read as a preference, treat it as a prohibition, put the tool in check mode under [the No-Write Rule](#the-no-write-rule), and say which reading was taken and why. The cost of an unnecessary check-only run is a slower loop; the cost of an unnecessary fix run is rewritten files.
- **Agent config forbids the only fixer for a file type**: Report that the file type has no permitted fixer, check it under [the No-Write Rule](#the-no-write-rule), and resolve findings by hand in step 6. Do not fall back to a different fixer for the same files unless the agent config names it as the sanctioned one.

Neither bullet is an exception to the No-Write Rule. "Check mode" here means the rule's qualifying command, so where none exists the tool is recorded as `check-only (no safe check command)` and nothing runs, rather than the check falling back to the writer the prohibition was aimed at.

- **CI workflow tool requires setup**: Some CI workflow steps depend on GitHub Actions that install a tool (e.g., `mfinelli/setup-shfmt`). If the tool is not locally available, report the missing tool and suggest installation. Reusable workflow calls (e.g., `cboone/gh-actions/.github/workflows/run-go-ci.yml@v4.1.0`, `cboone/gh-actions/.github/workflows/run-rust-ci.yml@v4.1.0`, `cboone/gh-actions/.github/workflows/run-zig-ci.yml@v4.1.0`) are CI-only: do not execute them locally, but retain explicit tool-selection evidence and report CI-only coverage separately from locally required work.
- **CI workflow command uses CI-only syntax**: Some `run:` commands use GitHub Actions expressions (`${{ }}`) or environment variables only available in CI. Skip these commands and note them as CI-only, retaining any enforcement evidence and project-specified local equivalent.
- **Pre-commit hook failure on commit**: Fix the issue, re-stage, and create a new commit (never amend).
