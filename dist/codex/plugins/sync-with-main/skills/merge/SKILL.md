---
name: merge
description: >-
  Merge the base branch into this branch, resolve conflicts, and push. Use for
  "merge main" or "sync with main"; to rebase, use sync-with-main:rebase.
argument-hint: "[--base <branch>]"
---

# Merge Main

Fetch and merge the repository's base branch into the current feature branch.

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
```

If `--base <branch>` was specified, use that value instead of the detected default branch.

**If `gh` is not available**, fall back to detecting the default branch with:

```bash
git remote show origin | grep 'HEAD branch' | sed 's/.*: //'
```

**If the current branch is the default branch itself**, warn the user that merging the base branch into itself is a no-op and stop.

### 2. Handle Uncommitted Changes

If `git status` shows uncommitted changes (staged or unstaged):

1. Warn the user that there are uncommitted changes.
1. Ask whether to:
   - **Stash**: Run `git stash` before proceeding, then `git stash pop` after the merge completes.
   - **Commit first**: Invoke the `commit` skill with the continuation block below, then continue with the merge. `commit` is an optional dependency: if it is not installed, leave this choice out and tell the user why, so they can commit by hand, or install `commit`, before running this skill again.
   - **Abort**: Stop without doing anything.

When invoked by a parent, return uncommitted-change and ambiguous-conflict decisions through the contract above. Never run the child before that decision has an answer. Pass the answered staging scope as `--staged` or `--all` when applicable. If the child returns a decision, propagate it rather than asking independently. Pass:

```text
Parent continuation:
- Caller: sync-with-main:merge
- Resume target: Step 3
- On success: continue with Step 3
- On failure or skipped required work: stop and report
- On needs-decision: return the question to this skill's parent, or ask in a standalone invocation
```

### 3. Fetch and Merge

```bash
git fetch origin <default-branch>
git merge origin/<default-branch>
```

Where `<default-branch>` is the detected or overridden base branch name.

### 4. Handle Merge Result

#### Clean Merge

If the merge completes without conflicts:

1. Report success.
1. Show a summary of what was merged:

```bash
git log HEAD@{1}..HEAD --oneline
```

#### Already Up to Date

If git reports "Already up to date.", report that the branch is already current with the base branch and stop.

#### Conflicts

If the merge produces conflicts, proceed to the conflict resolution workflow below.

### 5. Conflict Resolution

When merge conflicts occur:

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

1. **Complete the merge commit** (GPG signed):

```bash
git commit -S --no-edit
```

This uses the default merge commit message generated by git. If the user wants a custom message, they can specify it.

### 6. Post-Merge Steps

After a successful merge (with or without conflict resolution):

1. **Lockfile changes**: If any lockfiles changed during the merge (e.g., `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `go.sum`, `Gemfile.lock`, `poetry.lock`, `Cargo.lock`, `composer.lock`), suggest running the appropriate install command:
   - `package-lock.json` -> `npm install`
   - `yarn.lock` -> `yarn install`
   - `pnpm-lock.yaml` -> `pnpm install`
   - `go.sum` -> `go mod tidy`
   - `Gemfile.lock` -> `bundle install`
   - `poetry.lock` -> `poetry install`
   - `Cargo.lock` -> `cargo build`
   - `composer.lock` -> `composer install`

1. **Push**:

```bash
git push
```

If the branch has no upstream, use:

```bash
git push -u origin HEAD
```

### 7. Stash Recovery

If changes were stashed in step 2, pop the stash after the merge completes:

```bash
git stash pop
```

If the stash pop produces conflicts, warn the user and list the conflicted files.

## Error Handling

- **On the default branch**: Warn that merging the base branch into itself is a no-op and stop.
- **No remote configured**: Report the error and stop.
- **Merge aborted by user**: Clean up with `git merge --abort`.
- **Fetch failure** (network issues, authentication): Report the error clearly and stop.
- **Stash pop conflicts**: Warn the user and list conflicted files so they can resolve manually.
