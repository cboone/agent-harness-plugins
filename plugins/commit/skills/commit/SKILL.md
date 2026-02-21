---
name: commit
description: >-
  Create well-structured git commits with context-aware message generation, plan
  awareness, and support for common commit workflow variants. Use when the user
  says "commit", "commit the changes", "commit and push", "commit the plan",
  "commit staged", "commit just the staged changes", "give the plan a meaningful
  name and commit", or any variant involving committing code changes.
---

# Commit

Create smart, context-aware git commits with conventional commit messages.

## Core Principle: Small Logical Chunks

Always prefer committing in the smallest logical chunks that are appropriate. Each commit should represent a single coherent change: one bug fix, one new function, one refactor, one documentation update, etc. Do not batch unrelated changes into a single commit.

**Why this matters:**

- Small commits are easier to review, revert, cherry-pick, and bisect.
- Each commit tells a clear story about _one_ thing that changed and why.
- When something breaks, small commits make it straightforward to identify the cause.

**What constitutes a "logical chunk":**

- A single bug fix (even if it touches multiple files)
- A single new feature or capability
- A refactor that moves or renames code without changing behavior
- A documentation update
- A configuration or tooling change
- Test additions or updates for a specific feature

**What does NOT belong in the same commit:**

- A bug fix mixed with an unrelated refactor
- A new feature combined with formatting changes to unrelated files
- Documentation updates bundled with code changes they do not describe

## Options

The user may provide these options inline:

- **--push**: Commit and push to remote after committing
- **--staged**: Commit only staged changes (ignore unstaged changes)
- **--plan**: Commit only the plan file
- **--all**: Stage and commit all changes (including untracked files)

## Workflow

### 1. Check for Changes

Run these commands in parallel to understand the current state:

```bash
# See all changed and untracked files
git status

# See staged changes
git diff --cached

# See unstaged changes
git diff

# See recent commit messages for style reference
git log --oneline -10
```

If there are no changes at all (no staged, unstaged, or untracked files), report that there is nothing to commit and stop.

### 2. Determine What to Commit

First, resolve which files are in scope using these rules in order:

1. **If `--staged` was specified**: Only staged files are in scope. If nothing is staged, report that and stop.
1. **If `--plan` was specified**: See the [Plan-Aware Commits](#plan-aware-commits) section.
1. **If `--all` was specified**: All changes (staged, unstaged, and untracked) are in scope, but still exclude likely secret files (see below).
1. **If there are staged changes and no unstaged changes or untracked files**: Staged files are in scope.
1. **If there are only unstaged changes and/or untracked files**: All of them are in scope.
1. **If there are both staged changes and either unstaged changes or untracked files**: Ask the user whether to use only staged changes or include everything.

Never stage files that likely contain secrets (`.env`, `credentials.json`, `*.pem`, `*.key`, etc.). If such files are detected among untracked or unstaged changes, warn the user and exclude them.

### 3. Analyze Changes and Identify Logical Chunks

Review the in-scope changes and group them into the smallest logical chunks. Each chunk should be a self-contained, coherent change that makes sense on its own.

**How to identify chunks:**

1. **Examine the diff**: Look at all in-scope file changes and understand what each change accomplishes.
1. **Group by purpose**: Changes that serve the same purpose belong together. For example, a new function and its tests are one chunk, but an unrelated formatting fix is a separate chunk.
1. **Check for independence**: If a change can be committed on its own without leaving the codebase in a broken or inconsistent state, it is a candidate for its own chunk.
1. **Respect dependencies**: If change B depends on change A, commit A first. They may still be separate chunks if they represent distinct logical steps.

**Common chunk patterns:**

- Adding a new file and updating an index or registry that references it: one chunk.
- Fixing a bug in one module and reformatting an unrelated module: two chunks.
- Renaming a function across multiple call sites: one chunk.
- Adding a feature, adding its tests, and updating documentation: one to three chunks depending on whether the docs describe only the new feature or also cover unrelated material.

**When there is only one logical chunk**: Proceed directly to step 4 with all in-scope changes.

**When there are multiple logical chunks**: Process each chunk sequentially, repeating steps 4 through 6 for each one. Stage only the files belonging to the current chunk before committing. Report the plan (number of commits and a brief description of each) before creating the first commit.

### 4. Analyze Recent Commit Style

Before generating a message, examine the output from `git log --oneline -10` to understand the repository's commit message conventions:

- Do commits use conventional commits format (`type: description`)?
- What types are used (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, etc.)?
- What is the typical length and style?
- Are issue numbers referenced?

Match the repository's existing style. If there is no clear convention, default to conventional commits format.

### 5. Generate Commit Message

Analyze the diff to generate a commit message:

1. **Determine the type**: Based on the nature of the changes:
   - `feat`: New functionality
   - `fix`: Bug fix
   - `docs`: Documentation changes only
   - `refactor`: Code restructuring without behavior change
   - `test`: Adding or updating tests
   - `chore`: Build, tooling, or maintenance changes
   - `style`: Formatting, whitespace, or cosmetic changes
1. **Write the description**: A concise summary (under 72 characters) focused on _why_ the change was made, not _what_ files changed.
1. **Add context when relevant**: Reference issue numbers if they appear in branch names (e.g., branch `fix/issue-42-login-bug` suggests `fixes #42`).

### 6. Create the Commit

All commits must be GPG signed. Use a HEREDOC for the commit message to ensure proper formatting:

```bash
git commit -S -m "$(
  cat << 'EOF'
type: description here
EOF
)"
```

CRITICAL: Never use `git commit --amend`. Always create a new commit. If a pre-commit hook fails, fix the issue, re-stage, and create a new commit.

### 7. Post-Commit

After a successful commit:

1. Run `git status` to verify success.
1. Report the commit hash and message.
1. **If `--push` was specified**: Push to the remote.

```bash
git push
```

If the branch has no upstream, use:

```bash
git push -u origin HEAD
```

## Plan-Aware Commits

When the user mentions "commit the plan" or `--plan` is specified, or when plan files are detected in the changes:

### Detecting Plan Files

Plan files are typically found in `docs/plans/` or similar directories. Look for markdown files in plan-related directories among the changed files.

### "Commit the plan"

Commit only the plan file(s):

1. Stage only the plan file(s).
1. Generate a message like `docs: add plan for <meaningful-description>` where the description is derived from the plan's content or title.

### "Give the plan a meaningful name and commit"

1. Read the plan file to understand its content.
1. Rename the plan file to a descriptive name based on its content (e.g., `docs/plans/add-user-authentication.md`).
1. Stage both the deletion of the old file and the addition of the renamed file.
1. Commit with an appropriate message.

### "Commit the plan as one commit, then the changes as another"

Create two sequential commits:

1. First commit: Stage and commit only plan file(s) with a `docs:` message.
1. Second commit: Stage and commit the remaining changes with an appropriate message.

## Compound Commands

When the user gives compound instructions like "commit, then push" or "commit and push":

- Treat "and push" or "then push" as equivalent to `--push`.
- For other compound commands (e.g., "commit, then open a PR"), complete the commit first, then proceed with the next action.

## Error Handling

- **Nothing to commit**: Report cleanly, do not create an empty commit.
- **Pre-commit hook failure**: Read the hook output, fix the issue if possible, re-stage, and create a new commit (never amend).
- **Push failure**: Report the error. If it's a rejected push due to remote changes, suggest `git pull --rebase` first. Never force push unless the user explicitly requests it.
