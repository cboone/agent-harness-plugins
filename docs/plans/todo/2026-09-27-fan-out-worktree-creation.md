# Fan out worktree creation across several issues

## Context

`address-issue-in-worktree` is often invoked with several issue numbers, as in `/address-issue-in-worktree 42 57`. The invoking agent reads that as one combined piece of work and opens a single worktree for it. That reading is useful, but it is improvised: neither `address-issue-in-worktree` nor `create-worktree` mentions more than one issue anywhere, and their helpers are single-issue by design. `launch-workmux` takes one `--issue`, and `compose-issue-prompt` reads one issue object. How the combined worktree gets its branch number and prompt varies from run to run.

The goal is a second, explicit behavior: pass several issue numbers and get one worktree, branch, tmux window and session per issue. Adding it without defining the combined behavior would leave the two readings of `42 57` to the agent's judgment, so both become documented.

`create-worktree` has the same single-issue interface and the same gap, and gains the same option. Its classification step has an extra hazard: `42 57` matches neither the issue-number rule nor the branch rule in step 2, so it falls through to the task-description path today.

## Approach

### Two modes, three flags

- **Combined (default).** Several issue numbers produce one worktree. This keeps the behavior already relied on, now written down.
- **`--fan-out`.** Several issue numbers produce one worktree per issue. `--each` and `--separate` are aliases with identical behavior.

An explicit flag beats asking every time, since both readings are reasonable and the user knows which one they want when they type the command. Use `--fan-out` as the primary name in examples and report text; document the aliases in both skills and READMEs. Count distinct issues after removing duplicates. Each flag with one distinct issue is a no-op and follows the single-issue path, including its `--resource` and `--branch` options.

### Combined mode, specified

- Fetch every issue into its own `mktemp` file.
- The first issue given is the primary one: it supplies `--issue` to `launch-workmux`, so it owns the branch number and the branch-reuse lookup.
- The branch candidate is named for the combined work, not only the primary issue.
- The prompt carries every issue. Run `compose-issue-prompt` once per issue and check that every composition succeeds before invoking the launcher; a failed early issue must not leave a partial prompt to launch. Join the successful outputs. Omit `--chain-command` on all but the last call; the helper already emits the footer only when that option is present.
- In `address-issue-in-worktree`, the chain command lists every number: `/address-issue 42 57`. Update `address-issue` throughout its workflow, not only its entry point: fetch and show every issue, check each state, self-assign and label each open issue, collect the requirements into one plan with one approval gate, and report status for every issue. Its commits must reference every issue addressed by the combined work. Keep `--dry-run`, `--no-approval`, `--no-commit`, and `--commit-per-change` scoped to the one combined plan.
- In `address-issue-in-worktree`, every issue is self-assigned and labeled "in progress", since the session starts work on all of them.

### Fan-out mode

The loop lives in each `SKILL.md`, not in the scripts. The helpers already do one issue well, and a documented loop over them is simpler to reason about and test than a multi-issue launcher. Normalize `--each` and `--separate` to the same fan-out mode before checking option interactions.

Run it in two phases so a problem with one issue surfaces before anything is launched.

1. **Gather and validate everything first.**
   - Fetch every issue into its own `mktemp` file.
   - Flag closed issues and ambiguous text searches.
   - Resolve the default base branch once.
   - Generate every branch candidate.
   - Resolve existing local branches for every issue through a read-only `launch-workmux --resolve-issue-branch NUMBER` mode, so preflight uses the launcher's matching rules. Flag multiple matches and settle each branch choice before launch. Check for duplicate issue numbers so the same worktree is not launched twice.
   - Ask every outstanding question in one batch. A closed third issue must not stop the run after the first two already have worktrees, assignments and labels.
2. **Launch one at a time.** For each issue: compose its prompt, launch it, confirm its worktree and tmux window, mark it in progress after success (in `address-issue-in-worktree` only), and remove its temp file. Marking after success avoids leaving a newly assigned and labeled issue when its worktree was not created.
   - Extend `launch-workmux` with an `--await-completion` mode for the fan-out loop. Keep `workmux add` detached from the invoking agent, but have the detached process record its final exit status and log in per-launch temporary files. The caller waits for that result, verifies the selected branch's worktree and tmux window, and only then starts the next launch. A fixed sleep is not a completion signal; the current helper returns after `WORKMUX_LAUNCH_WAIT_SECONDS` even if `workmux add` is still running or has failed.
   - Put an explicit bound on waiting and report a timeout as an uncertain launch, with the branch and any observed worktree or window state. Do not launch another issue while the prior `workmux add` is still running, because concurrent additions can race in Git and tmux. Define cleanup ownership so neither the prompt nor the log is removed before the detached process finishes.
3. **Continue past a completed failure.** Record the failure and move to the next issue only after the failed `workmux add` has exited. If the completion wait expires while it is still running, stop the loop and report the remaining issues as unlaunched. Remove each issue JSON file when no longer needed; the detached process owns its prompt and log files until it exits, including after a timeout.

The preflight branch check must agree with the launcher's final branch selection. Recheck at launch because another process can create a branch after preflight; if that creates a new ambiguity, record it for that issue rather than choosing a branch silently. If best-effort status marking fails after a successful launch, report the worktree as created and the marking result separately.

### Option interactions

| Option                                            | Combined                                             | `--fan-out`                                                                       |
| ------------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------- |
| `--no-approval` (`address-issue-in-worktree`)     | Passed to the one chained command                    | Passed to every chained command                                                   |
| `--resource`                                      | Claims for the one worktree                          | Rejected for several distinct issues: one resource cannot cover several worktrees |
| `--base` (`create-worktree`), or a requested base | Used for the one worktree                            | Used for every worktree                                                           |
| `--branch` (`create-worktree`)                    | Used as the one branch name                          | Rejected for several distinct issues: one name cannot serve several branches      |
| `--issue` (`create-worktree`)                     | Repeatable, or accepts several numbers               | Same                                                                              |
| `--no-issue` (`create-worktree`)                  | Forces the description path, so neither mode applies | Rejected as contradictory                                                         |

### Classification in `create-worktree`

Step 2 needs a rule for several issue numbers: two or more whitespace- or comma-separated tokens, each a bare integer or `#N`, are a list of issues. `--no-issue` still forces the description path, which is how a task that happens to be a list of numbers gets through.

### Reporting

Fan-out ends with one table: issue, title, branch (generated or reused), tmux window, whether it was marked in progress, and the error for any issue that failed. The existing per-issue report items still apply to each row.

## Files

- `plugins/address-issue-in-worktree/skills/address-issue-in-worktree/SKILL.md`: `--fan-out` option, combined-mode specification, fan-out workflow, option interactions, reporting, error handling.
- `plugins/address-issue-in-worktree/README.md`: option table and a usage example for each mode.
- `plugins/address-issue-in-worktree/.claude-plugin/plugin.json`: minor bump, 2.3.2 to 2.4.0.
- `plugins/create-worktree/skills/create-worktree/SKILL.md`: the same, plus the classification rule.
- `plugins/create-worktree/README.md`: option table and usage example.
- `plugins/create-worktree/.claude-plugin/plugin.json`: minor bump, 1.6.2 to 1.7.0.
- `plugins/address-issue/skills/address-issue/SKILL.md`: define the combined workflow across lookup, state checks, status marking, planning, execution, commits, and reporting.
- `plugins/address-issue/README.md` and `.claude-plugin/plugin.json`: usage example and a minor bump.
- `plugins/*/scripts/compose-issue-prompt`: only if joining prompts needs a footer switch. The script is duplicated across both worktree plugins, so any change lands in both copies with matching `tests/scrut/compose-issue-prompt.md` coverage.
- `plugins/*/scripts/launch-workmux`: add `--resolve-issue-branch` and `--await-completion` to both byte-identical copies, with matching `tests/scrut/launch-workmux.md` coverage.
- `dist/` and `.agents/` mirrors: regenerated by `make build`.

## Verification

- `make build`, then `make test-all`.
- Run the `check-versions` skill.
- Manual checks in a scratch repository with a few sample issues:
  - Combined: `/address-issue-in-worktree A B` opens one worktree numbered for A, whose session runs `/address-issue A B`.
  - Fan-out: `/address-issue-in-worktree A B C --fan-out` opens three worktrees, each running `/address-issue N` for its own issue.
  - Fan-out with one closed issue asks before launching anything.
  - Fan-out with an ambiguous branch for the last issue asks for a choice before launching the first; a branch created after preflight is detected at launch.
  - Fan-out with several distinct issues and `--resource` is rejected before anything is fetched or marked.
  - `/create-worktree A B --fan-out` opens two worktrees and marks nothing in progress.
  - `--each` and `--separate` produce the same per-issue behavior as `--fan-out` in both worktree skills, including the single-issue path and option rejections.
  - With one distinct issue, an alias and `--resource` use the ordinary resource path; `create-worktree` also accepts an alias with `--branch` and retains the issue prompt.
  - `/create-worktree A B` is classified as issues, not a task description.
  - No `issue-json-*` or `workmux-prompt-*` temp files remain after completed launches. After a timeout, the detached process removes its prompt and log when it exits.
  - A launch that fails or exceeds the completion wait is reported for its issue without starting another `workmux add` while it is still running. A completed failed launch does not appear as a success just because the launcher printed a generated branch name.
  - Combined `/address-issue A B` fetches and plans both issues under one approval gate, marks both open issues in progress, and includes both issue references in commits and completion reporting.
