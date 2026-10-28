---
name: rebase
description: >-
  Rebase the current branch onto the base branch, resolving conflicts per
  commit, then force-with-lease push. Use for "rebase onto main".
argument-hint: "[--base <branch>]"
---

# Rebase Onto Main

Fetch and rebase the current feature branch onto the repository's base branch.

## Options

The user may provide these options inline:

- **--base `<branch>`**: Override the auto-detected base branch (e.g., `--base develop`)

## Skill dependencies

- **Required:** None
- **Optional:** `commit`

## Capabilities and authority

Use the tools this session actually offers. For a question, use a structured question tool when available in the active mode; otherwise present numbered choices and wait. In a noninteractive run, report the unresolved question and preserved state instead of choosing an answer. Tool names such as Write, Read, Glob and AskUserQuestion below are examples: perform the same file or question operation with the host's supported mechanism. Write a body file completely before issuing the command that reads it; never batch those dependent operations.

Prior user authorization carries through the workflow; add no confirmation merely because the harness differs. Host approvals, active Plan or read-only mode, writable roots and network policy still apply. Stop before a prohibited write or any step dependent on a blocked operation, preserve state, and report the exact command and restriction. Never bypass controls or claim an unrun step completed. Separate completed, skipped, blocked and failed work in the result. For invocation hints, render the named skill with the running harness's form: slash invocation in Claude Code, dollar mention or the skills selector in Codex. A mention is not a tool call; load composed skills from their advertised locations.

## Parent Continuation Contract

Honor a supplied parent continuation block and its resume target. On success, return control to the parent without asking whether to continue. When a decision has no supplied answer, do not ask independently or guess: return `Status: needs-decision`, the question, available choices and preserved state. The parent asks or stops, then invokes this skill with an answer. For an in-progress merge or rebase, list conflicts and the applicable abort command; do not abort or discard work merely to return a result.

Return `Status: <success|no-op|failure|unavailable|needs-decision>`, `Outputs`, `Unresolved or skipped` and `Caller resume target`. A no-op is successful only when no required work was skipped. Preserve any domain-specific status lines below. A host block or failed required check is failure, a missing required skill is unavailable, and unresolved choices are needs-decision. Standalone invocations retain their existing questions and reporting.

## Workflow

### 1. Pre-Flight Checks

Run these commands in parallel to understand the current state:

```bash
# Check for uncommitted changes
git status

# Detect the repository's default branch
gh repo view --json defaultBranchRef -q '.defaultBranchRef.name'

# Confirm which branch we are on
git branch --show-current

# Check whether the branch has been pushed to a remote
git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || echo "no upstream"
```

If `--base <branch>` was specified, use that value instead of the detected default branch.

**If `gh` is unavailable or its query fails**, detect the default branch with:

```bash
git symbolic-ref --quiet --short refs/remotes/origin/HEAD
```

Strip the `origin/` prefix from successful output. Treat empty output, a failed command, or `HEAD` as not found. Without an explicit `--base`, if neither query finds a base, ask for it and stop rather than guessing. Fetch the selected base in step 3 before validating its remote-tracking commit; never substitute a local branch.

**If the current branch is the default branch itself**, warn the user that rebasing the base branch onto itself is a no-op and stop.

### 2. Handle Uncommitted Changes

If `git status` shows uncommitted changes (staged or unstaged):

1. Warn the user that there are uncommitted changes.
1. Ask whether to:
   - **Stash**: Run `git stash` before proceeding, then `git stash pop` after the rebase completes.
   - **Commit first**: Invoke the `commit` skill with the continuation block below, then continue with the rebase. `commit` is an optional dependency: if it is not installed, leave this choice out and tell the user why, so they can commit by hand, or install `commit`, before running this skill again.
   - **Abort**: Stop without doing anything.

Rebase will refuse to start with a dirty working tree, so this step is mandatory before fetching.

When invoked by a parent, return uncommitted-change and ambiguous-conflict decisions through the contract above. Never run the child before that decision has an answer. Pass the answered staging scope as `--staged` or `--all` when applicable. If the child returns a decision, propagate it rather than asking independently. Pass:

```text
Parent continuation:
- Caller: sync-with-main:rebase
- Resume target: Step 3
- On success: continue with Step 3
- On failure or skipped required work: stop and report
- On needs-decision: return the question to this skill's parent, or ask in a standalone invocation
```

### 3. Fetch and Rebase

Capture the current HEAD so the post-rebase step can detect whether history was actually rewritten:

```bash
git rev-parse HEAD
```

Record this as `<pre-rebase-head>`. Then:

```bash
git fetch origin <default-branch>
git rev-parse --verify --quiet origin/<default-branch>^{commit}
git rebase origin/<default-branch>
```

Where `<default-branch>` is the detected or overridden base branch name. Stop if fetching or commit validation fails; run the merge or rebase only after both succeed.

### 4. Handle Rebase Result

#### Clean Rebase

If the rebase completes without conflicts:

1. Report success.
1. Show a summary of the replayed commits:

```bash
git log origin/<default-branch>..HEAD --oneline
```

This range lists exactly the commits that now sit on top of the rebased base, regardless of whether the branch has an upstream. Avoid `@{u}..HEAD` here: it fails when the branch has no upstream, and after a rebase it can also include base-branch commits the rebase moved onto, not just the replayed feature commits.

#### Already Up to Date

If git reports "Current branch <branch> is up to date." or "Fast-forwarded ...", report the result and continue to the post-rebase steps. In this case the local HEAD is unchanged (or only fast-forwarded), so the push step uses a normal `git push` rather than `--force-with-lease`.

#### Conflicts

If the rebase produces conflicts, proceed to the conflict resolution workflow below.

### 5. Conflict Resolution

Rebase resolves conflicts **per commit**, not as a single merge. For each conflicting commit, git pauses the rebase, marks the conflicting files, and waits for resolution before continuing.

For each pause:

1. **Identify the conflicting commit**:

```bash
git status
```

The status output names the commit currently being applied (e.g., "You are currently rebasing branch '...' on '<sha>'."). Read it and look at the commit being replayed:

```bash
git log -1 --oneline REBASE_HEAD
```

1. **List conflicted files**:

```bash
git diff --name-only --diff-filter=U
```

1. **Resolve each conflicted file**:
   - Read the file and examine the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
   - Use the surrounding code context, the intent of both sides, and the project's conventions to determine the correct resolution.
   - For trivial conflicts (whitespace, import ordering, adjacent non-overlapping changes), resolve automatically.
   - For non-trivial conflicts where the correct resolution is ambiguous, show the user both sides and ask which to keep or how to combine them.

1. **Stage resolved files**:

```bash
git add <resolved-file>
```

1. **Continue the rebase**:

```bash
git rebase --continue
```

This re-applies the commit with the resolved content. Git will reuse the original commit message; if the commit becomes empty after resolution, it prompts to skip with `git rebase --skip`.

1. **Repeat** until git reports the rebase complete. Each subsequent commit may produce its own conflicts.

If at any point the situation becomes unrecoverable, abort cleanly:

```bash
git rebase --abort
```

This restores the branch to its pre-rebase state.

### 6. Post-Rebase Steps

After a successful rebase (with or without conflict resolution):

1. **Lockfile changes**: If any lockfiles changed during the rebase (e.g., `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `go.sum`, `Gemfile.lock`, `poetry.lock`, `Cargo.lock`, `composer.lock`), suggest running the appropriate install command:
   - `package-lock.json` -> `npm install`
   - `yarn.lock` -> `yarn install`
   - `pnpm-lock.yaml` -> `pnpm install`
   - `go.sum` -> `go mod tidy`
   - `Gemfile.lock` -> `bundle install`
   - `poetry.lock` -> `poetry install`
   - `Cargo.lock` -> `cargo build`
   - `composer.lock` -> `composer install`

1. **Push**:

   First decide whether a force push is actually required. A change in HEAD alone is not enough to conclude that history was rewritten: when the local branch had no commits beyond the base, `git rebase` simply fast-forwards HEAD onto the new tip without rewriting anything. Distinguish the two cases by checking whether `<pre-rebase-head>` from step 3 is still reachable from the post-rebase HEAD:

   ```bash
   git rev-parse HEAD
   git merge-base --is-ancestor <pre-rebase-head> HEAD
   ```

   If `git merge-base --is-ancestor` exits 0, the pre-rebase commit is an ancestor of the new HEAD, so the rebase was a no-op or a fast-forward and no force push is needed. If it exits non-zero, the original commits are no longer on the branch's history line, so the rebase rewrote history and any already-published copy of the branch must be replaced with a force push.

   Choose the push command based on three cases:
   - **No upstream** (fresh branch never pushed): no force needed.

     ```bash
     git push -u origin HEAD
     ```

   - **Upstream exists, no-op or fast-forward only** (`<pre-rebase-head>` is an ancestor of the post-rebase HEAD): history was not rewritten. Skip the push entirely if HEAD is unchanged, or run a plain `git push` if there are local commits ahead of upstream that haven't been pushed yet.

     ```bash
     git push
     ```

   - **Upstream exists, history rewritten by rebase** (`<pre-rebase-head>` is no longer an ancestor of the post-rebase HEAD): force-with-lease is required to replace the previously pushed history.

     ```bash
     git push --force-with-lease
     ```

   **Always use `--force-with-lease`, never plain `--force`.** `--force-with-lease` refuses to overwrite the remote if someone else has pushed in the meantime; plain `--force` clobbers their work without checking.

   The user's CLAUDE.md forbids using force flags as a workaround without explicit instruction. Force-pushing after a rebase that rewrote history is the documented exception: it is required by the rebase workflow itself, not a workaround for an unexpected failure. Still prefer `--force-with-lease` over `--force` and surface the command before running it.

   **Never** run `git push --force` (without `--force-with-lease`) and **never** force-push the default branch.

### 7. Stash Recovery

If changes were stashed in step 2, pop the stash after the rebase completes:

```bash
git stash pop
```

If the stash pop produces conflicts, warn the user and list the conflicted files.

## Error Handling

- **On the default branch**: Warn that rebasing the base branch onto itself is a no-op and stop.
- **No remote configured**: Report the error and stop.
- **Dirty working tree**: Rebase refuses to start. Step 2 must resolve this before fetching.
- **Rebase aborted by user**: Clean up with `git rebase --abort`, which restores the pre-rebase state.
- **Empty commit during rebase** (the commit's changes are already present in the base): Use `git rebase --skip` to drop it, after confirming with the user.
- **Fetch failure** (network issues, authentication): Report the error clearly and stop.
- **`--force-with-lease` rejection** (someone else pushed to the remote branch since you last fetched): Do **not** escalate to `--force`. Stop, report the divergence, and ask the user how to proceed (typically: fetch, inspect the upstream changes, decide whether to integrate them).
- **Stash pop conflicts**: Warn the user and list conflicted files so they can resolve manually.
