---
name: rebase-onto-main
description: >-
  Fetch and rebase the current feature branch onto the base branch (usually
  main), handling conflicts per commit and force-with-lease pushing. Use when
  the user says "rebase onto main", "rebase on main", "rebase against main",
  "rebase from main", "rebase main", "rebase branch", "update branch via
  rebase", "rebase against base branch", "replay commits onto main", or any
  variant involving rebasing the current working branch onto the default
  branch.
---

# Rebase Onto Main

Fetch and rebase the current feature branch onto the repository's base branch.

## Options

The user may provide these options inline:

- **--base `<branch>`**: Override the auto-detected base branch (e.g., `--base develop`)

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
git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null
```

If `--base <branch>` was specified, use that value instead of the detected default branch.

**If `gh` is not available**, fall back to detecting the default branch with:

```bash
git remote show origin | grep 'HEAD branch' | sed 's/.*: //'
```

**If the current branch is the default branch itself**, warn the user that rebasing the base branch onto itself is a no-op and stop.

### 2. Handle Uncommitted Changes

If `git status` shows uncommitted changes (staged or unstaged):

1. Warn the user that there are uncommitted changes.
1. Ask whether to:
   - **Stash**: Run `git stash` before proceeding, then `git stash pop` after the rebase completes.
   - **Commit first**: Invoke the `/commit` skill, then continue with the rebase.
   - **Abort**: Stop without doing anything.

Rebase will refuse to start with a dirty working tree, so this step is mandatory before fetching.

### 3. Fetch and Rebase

Capture the current HEAD so the post-rebase step can detect whether history was actually rewritten:

```bash
git rev-parse HEAD
```

Record this as `<pre-rebase-head>`. Then:

```bash
git fetch origin <base-branch>
git rebase origin/<base-branch>
```

Where `<base-branch>` is the detected or overridden base branch name.

### 4. Handle Rebase Result

#### Clean Rebase

If the rebase completes without conflicts:

1. Report success.
1. Show a summary of the replayed commits:

```bash
git log @{u}..HEAD --oneline
```

If the branch has no upstream yet, fall back to `git log origin/<base-branch>..HEAD --oneline`.

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

   First decide whether a force push is actually required by comparing the current HEAD against `<pre-rebase-head>` from step 3:

   ```bash
   git rev-parse HEAD
   ```

   If the commit hash changed, history was rewritten and any already-published copy of the branch needs a force push. If the hash is unchanged (no-op rebase) or only fast-forwarded onto upstream commits that were already pushed, a normal push is sufficient.

   Choose the push command based on three cases:

   - **No upstream** (fresh branch never pushed): no force needed.

     ```bash
     git push -u origin HEAD
     ```

   - **Upstream exists, HEAD unchanged after rebase** (no-op or fast-forward only, nothing to push): skip the push entirely, or run a plain `git push` if there are local commits ahead of upstream that haven't been pushed yet.

     ```bash
     git push
     ```

   - **Upstream exists, HEAD rewritten by rebase**: force-with-lease is required to replace the previously pushed history.

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
