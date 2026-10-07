# PR Review: feature/add-fan-out-option-to-worktree-creation

Base: `origin/main` (`94a77608`)
Commits: 8
Reviewed through: `8a1c1448`
Reviewers: general code, test coverage, silent failures, comment accuracy

## Summary

No critical issues. Five important issues and a set of suggestions follow. The two launcher copies are byte-identical and a test enforces it, both findings from the 2026-09-28 branch review are fixed, the detached handoff protocol is sound, and the skills, READMEs and plan agree on modes, aliases, option rejections, exit codes and marking order.

## Important

### 1. The await timeout cannot fire before the harness timeout

`launch-workmux` defaults `WORKMUX_LAUNCH_TIMEOUT_SECONDS` to 120, which equals Claude Code's default Bash tool timeout, and neither worktree skill tells the agent to raise the tool timeout. The tool times out first, so exit 124 is unreachable by default. The phase 2 exit table covers only 0, 1 and 124, so an agent may treat a tool timeout as a failure and start the next `workmux add` while the first still runs. The detached half shares the launcher's process group, so a tree-kill can stop `workmux add` partway through; if it survives, its state directory is never removed.

Fix: lower the default below the harness limit, have the skills run the launch with an explicit tool timeout above it, treat any other status like 124, and start the detached half in its own process group.

### 2. Combined mode marks issues before composing prompts

`address-issue-in-worktree` combined mode marks every issue at step 3 and composes prompts at step 5. A composition failure leaves the issues assigned and labeled with no worktree.

Fix: compose and check every prompt before step 3; composition reads only the cached issue JSON.

### 3. The completed-failure test cannot catch its regression

The failure case sets both `STUB_WORKMUX_EXIT=2` and `STUB_WORKMUX_SKIP_WORKTREE=1`, so it fails by either route. A refactor that treated an existing worktree as success would still pass it.

Fix: add a case where the stub records the worktree and then exits 2, asserting the failure and no `Worktree ready` line.

### 4. Resolve mode reports no branch when git fails

`existing_branch_for_issue` runs `git for-each-ref ... 2> /dev/null || true`, so `--resolve-issue-branch` exits 0 with no output on a git error, which preflight reads as "no existing branch". `worktree_path_for_branch` swallows failures the same way.

Fix: fail loudly when git fails in both helpers.

### 5. README allowlists miss the new commands

The `create-worktree` README does not allow `mktemp` or the issue JSON cleanup, and neither worktree README allows `workmux list`, which both fan-out phase 2 sections run.

Fix: add the entries.

## Suggestions

- **S1.** Launcher help text still says it waits briefly and reads stdin in every mode; it should describe `--await-completion` and `--resolve-issue-branch` accurately, name the `Worktree ready: PATH` line, and say `--issue` exits 1 when several branches match.
- **S2.** After a timeout the detached process deletes its log, so nothing records whether the launch succeeded; the skills give no way to resolve an uncertain result.
- **S3.** The fan-out report tables show no uncertain or not-launched rows.
- **S4.** Phase 2 does not say what to do when `workmux list` shows the window is not open.
- **S5.** The several-issues sections mention ambiguous text searches without saying whether a list may mix numbers and search text.
- **S6.** Test gaps: cleanup on the failure path, the timeout message when a worktree exists, the timeout test's narrow timing margin, cleanup checks that glob the shared `TMPDIR`, and resolve-mode edge arguments (no value, `0`, `042`, unasserted exit codes).
- **S7.** The `workmux-stub` worktree-recording comment and the `git-worktree-stub` porcelain-file comment are unclear or incomplete.

## Resolution
