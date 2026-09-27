# Fan out worktree creation across several issues

## Context

`address-issue-in-worktree` is often invoked with several issue numbers, as in `/address-issue-in-worktree 42 57`. The invoking agent reads that as one combined piece of work and opens a single worktree for it. That reading is useful, but it is improvised: neither `address-issue-in-worktree` nor `create-worktree` mentions more than one issue anywhere, and their helpers are single-issue by design. `launch-workmux` takes one `--issue`, and `compose-issue-prompt` reads one issue object. How the combined worktree gets its branch number and prompt varies from run to run.

The goal is a second, explicit behavior: pass several issue numbers and get one worktree, branch, tmux window and session per issue. Adding it without defining the combined behavior would leave the two readings of `42 57` to the agent's judgment, so both become documented.

`create-worktree` has the same single-issue interface and the same gap, and gains the same option. Its classification step has an extra hazard: `42 57` matches neither the issue-number rule nor the branch rule in step 2, so it falls through to the task-description path today.

## Approach

### Two modes, one flag

- **Combined (default).** Several issue numbers produce one worktree. This keeps the behavior already relied on, now written down.
- **`--fan-out`.** Several issue numbers produce one worktree per issue.

An explicit flag beats asking every time, since both readings are reasonable and the user knows which one they want when they type the command. `--fan-out` with a single issue is accepted and behaves exactly like the single-issue path.

### Combined mode, specified

- Fetch every issue into its own `mktemp` file.
- The first issue given is the primary one: it supplies `--issue` to `launch-workmux`, so it owns the branch number and the branch-reuse lookup.
- The branch candidate is named for the combined work, not only the primary issue.
- The prompt carries every issue. Run `compose-issue-prompt` once per issue and join the outputs, with the chain footer only on the last one. Check whether the helper needs a `--no-footer` or similar switch for this, or whether omitting `--chain-command` on all but the last call is enough.
- In `address-issue-in-worktree`, the chain command lists every number: `/address-issue 42 57`. `address-issue` does not mention several issue numbers either, so document the combined reading there as well: one plan, one branch, commits referencing every issue.
- In `address-issue-in-worktree`, every issue is self-assigned and labeled "in progress", since the session starts work on all of them.

### Fan-out mode

The loop lives in each `SKILL.md`, not in the scripts. The helpers already do one issue well, and a documented loop over them is simpler to reason about and test than a multi-issue launcher.

Run it in two phases so a problem with one issue surfaces before anything is launched.

1. **Gather and validate everything first.**
   - Fetch every issue into its own `mktemp` file.
   - Flag closed issues and ambiguous text searches.
   - Resolve the default base branch once.
   - Generate every branch candidate.
   - Ask every outstanding question in one batch. A closed third issue must not stop the run after the first two already have worktrees, assignments and labels.
2. **Launch one at a time.** For each issue: mark it in progress (in `address-issue-in-worktree` only), compose its prompt, launch it, confirm it in `git worktree list`, and remove its temp file.
   - Launches are sequential, not concurrent. Concurrent `workmux add` runs against one repository can race in `git worktree add` and in tmux window creation.
   - Each launch already waits `WORKMUX_LAUNCH_WAIT_SECONDS` (8 by default), so N issues take at least 8N seconds of wall-clock time.
3. **Continue past a single failure.** A launch that fails is recorded and the loop moves on. Temp files for every issue are removed however the run ends, including issues that were never launched.

### Option interactions

| Option                                            | Combined                                             | `--fan-out`                                                                       |
| ------------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------- |
| `--no-approval` (`address-issue-in-worktree`)     | Passed to the one chained command                    | Passed to every chained command                                                   |
| `--resource`                                      | Claims for the one worktree                          | Rejected, with the reason: an exclusive resource can be held by only one worktree |
| `--base` (`create-worktree`), or a requested base | Used for the one worktree                            | Used for every worktree                                                           |
| `--branch` (`create-worktree`)                    | Used as the one branch name                          | Rejected: one name cannot serve several branches                                  |
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
- `plugins/address-issue/skills/address-issue/SKILL.md`: document several issue numbers as one combined piece of work.
- `plugins/address-issue/README.md` and `.claude-plugin/plugin.json`: usage example and a minor bump.
- `plugins/*/scripts/compose-issue-prompt`: only if joining prompts needs a footer switch. The script is duplicated across both worktree plugins, so any change lands in both copies with matching `tests/scrut/compose-issue-prompt.md` coverage.
- `dist/` and `.agents/` mirrors: regenerated by `make build`.

## Verification

- `make build`, then `make test-all`.
- Run the `check-versions` skill.
- Manual checks in a scratch repository with a few sample issues:
  - Combined: `/address-issue-in-worktree A B` opens one worktree numbered for A, whose session runs `/address-issue A B`.
  - Fan-out: `/address-issue-in-worktree A B C --fan-out` opens three worktrees, each running `/address-issue N` for its own issue.
  - Fan-out with one closed issue asks before launching anything.
  - Fan-out with `--resource` is rejected before anything is fetched or marked.
  - `/create-worktree A B --fan-out` opens two worktrees and marks nothing in progress.
  - `/create-worktree A B` is classified as issues, not a task description.
  - No `issue-json-*` or `workmux-prompt-*` temp files remain afterward.

## Open questions

- Is the flag name `--fan-out` right, or would `--each` or `--separate` read better in the README?
