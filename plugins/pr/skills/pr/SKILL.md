---
name: pr
description: >-
  Commit all changes (if needed), push to remote, and create a GitHub pull
  request in one automated step with no prompts. Handles plan files
  automatically (renaming, moving completed plans to done). Use when the user
  says "pr", "create a pr", "open a pr", "submit a pr", "push and create pr",
  "commit and create pr", or any variant involving creating a pull request from
  the current branch. Requires the gh CLI to be installed.
---

# PR

Commit, push, and create a pull request in one automated step. Never prompt the user for input — make opinionated decisions at every step.

## Workflow

### 1. Gather Context

First, detect the repository's base branch:

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

If `gh` is not available or the command fails, fall back to:

```bash
git remote show origin | grep 'HEAD branch' | sed 's/.*: //'
```

Use the detected value as `<default-branch>`.

#### Detect the PR base branch

The current branch may have been created from a non-default branch (e.g., for stacked PRs). Check the reflog for the branch creation point:

```bash
git reflog show $(git branch --show-current) --format='%gs' | tail -1
```

This produces output like `branch: Created from develop`, `branch: Created from origin/develop`, or `branch: Created from refs/heads/feature/parent`. If the last entry matches `branch: Created from <name>`, extract `<name>` and normalize it by stripping any `refs/heads/`, `refs/remotes/origin/`, or leading `origin/` prefix.

If a source branch name was extracted, verify it exists on the remote and is not the current branch. Note that `git ls-remote` always exits 0 regardless of whether the branch exists, so check for non-empty output:

```bash
git ls-remote --heads origin <source-branch> | grep -q .
```

If the command produces output (branch exists on the remote) and the branch is not the current branch, use it as `<base-branch>`. Otherwise, use `<default-branch>` as `<base-branch>`.

Then run these commands in parallel to understand the current state:

```bash
# Current branch and changed files
git status

# Staged changes
git diff --cached

# Unstaged changes
git diff

# Recent commit messages for style reference
git log --oneline -10

# Full diff of this branch against the base branch
git diff < base-branch > ...HEAD

# Commit history of this branch since diverging from the base branch
git log --oneline < base-branch > ..HEAD

# Check remote tracking status
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2> /dev/null || echo "no upstream"
```

### 2. Detect Connected Issues

Search for GitHub issues that this branch addresses. Combine results from the strategies below, deduplicate by issue number, and record the final list for use in the commit message (step 4) and PR body (step 6).

#### Strategy 1 — Issue numbers in the branch name

Extract the current branch name. Look for issue numbers in patterns like:

- `TYPE/N-description` (e.g., `fix/42-login-bug` → #42)
- `TYPE/description-N` (e.g., `feature/login-bug-42` → #42)
- `TYPE/issue-N` or `TYPE/issue-N-description` (e.g., `fix/issue-42` → #42)
- `N-description` (e.g., `42-add-login` → #42)

For each candidate number, verify it refers to an existing issue:

```bash
gh issue view NUMBER --json number,title,state --jq '.number' 2> /dev/null
```

Only include it if the command succeeds (the issue exists).

#### Strategy 2 — Issue references in commit messages

Scan the `git log <base-branch>..HEAD` output (already gathered in step 1) for `#N` references. Collect all unique issue numbers. For each, verify it refers to an actual issue:

```bash
gh issue view NUMBER --json number,title,state --jq '.number' 2> /dev/null
```

#### Strategy 3 — GitHub issue search by branch slug

Only run this strategy if strategies 1 and 2 found zero issues.

Extract the slug portion of the branch name (everything after the first `/`). Convert hyphens to spaces to form search keywords. Search for matching open issues:

```bash
gh issue list --search "KEYWORDS" --state open --json number,title --limit 5
```

Evaluate the results:

- If **exactly one** issue is returned, include it.
- If **multiple** issues are returned, compare each issue title against the branch slug. Include an issue only if its title, when slugified (lowercased, spaces and special characters replaced with hyphens), is a near-exact match with the branch slug. If no single issue clearly matches, include none.
- If **zero** issues are returned, skip.

#### Combine results

Merge issue numbers from all three strategies into a single deduplicated list. Preserve the order: branch-name issues first, then commit-message issues, then search-matched issues. Note the branch type prefix (`fix/*` vs other) for choosing the closing keyword later.

### 3. Validate Preconditions

Stop and report an error if any of these are true:

- The current branch **is** the base branch. Do not create a PR from the base branch to itself.
- There are no changes to commit **and** no commits ahead of the base branch. There is nothing to open a PR for.

### 4. Commit Changes (if needed)

If there are no staged changes, unstaged changes, or untracked files, skip this step.

Never stage files that likely contain secrets (`.env`, `credentials.json`, `*.pem`, `*.key`, etc.). If such files are detected, warn the user and exclude them.

#### Handle plan files

Before identifying logical chunks, check for plan files among the uncommitted changes. Plan files live under `docs/plans/` and its subdirectories (`todo/`, `done/`). If any Markdown files in these directories are among the staged, unstaged, or untracked files, apply [Plan-Aware Commits](#plan-aware-commits) rules to them.

Plan files always form their own logical chunk, committed separately from code changes. Process the plan file chunk first, then proceed with the remaining changes.

#### Identify logical chunks

Review all uncommitted changes (excluding any plan files already handled above) and group them into the smallest logical chunks. Each chunk should be a self-contained, coherent change that makes sense on its own:

1. **Examine the diff**: Look at all changed and untracked files and understand what each change accomplishes.
1. **Group by purpose**: Changes that serve the same purpose belong together. A new function and its tests are one chunk, but an unrelated formatting fix is a separate chunk.
1. **Check for independence**: If a change can be committed on its own without leaving the codebase in a broken or inconsistent state, it is a candidate for its own chunk.
1. **Respect dependencies**: If change B depends on change A, commit A first.

If all changes form a single logical chunk, create one commit. If they form multiple chunks, create a commit for each, processing them sequentially.

#### Create each commit

For each chunk:

1. **Stage only the files belonging to the current chunk** using `git add` with specific file paths.
1. **Analyze the diff** to generate a commit message:
   - Examine `git log --oneline -10` output to match the repository's commit message style.
   - Determine the commit type (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`) based on the changes.
   - Write a concise description (under 72 characters) focused on _why_ the change was made.
   - Reference connected issues detected in step 2. For `fix/*` branches, use `fixes #N`; for other branch types, use `closes #N`. If no connected issues were detected, omit issue references from the commit message. Only reference issues in the commit that most directly addresses them.
1. **Create the commit** using GPG signing and a HEREDOC:

```bash
git commit -S -m "$(
  cat << 'EOF'
type: description here
EOF
)"
```

CRITICAL: Never use `git commit --amend`. Always create a new commit. If a pre-commit hook fails, fix the issue, re-stage, and create a new commit.

### 5. Push to Remote

Push the branch to the remote:

```bash
git push
```

If the branch has no upstream, use:

```bash
git push -u origin HEAD
```

If the push is rejected because the remote has diverged, report the error and stop. Never force push.

### 6. Create the Pull Request

Analyze all commits on the branch (from `git log <base-branch>..HEAD` and `git diff <base-branch>...HEAD`) to generate the PR title and body.

#### Title

- Under 70 characters.
- Summarize the overall change, not individual commits.
- Use sentence case (capitalize the first word only).
- Do not include a conventional-commit type prefix in the PR title.

#### Body

Use the following format:

```markdown
## Summary

- Bullet point describing key change 1
- Bullet point describing key change 2
- Bullet point describing key change 3

## Test plan

- [ ] TODO: describe how to verify this change

## Closes

Closes #N
```

Keep the summary to 1-4 bullet points. Focus on what changed and why.

If connected issues were detected in step 2, add a `## Closes` section after `## Test plan`. Use one line per issue with the appropriate keyword:

- For issues detected from a `fix/*` branch: `Fixes #N`
- For all other issues: `Closes #N`

If no connected issues were detected, omit the `## Closes` section entirely.

#### Create the PR

First, generate a unique temporary file path using `mktemp`:

```bash
mktemp /tmp/pr-body-XXXXXX.md
```

Then use the **Write** tool to write the full PR body (Summary, Test plan, and Closes sections) to the path returned by `mktemp`.

Then create the PR with `--body-file`, using the actual path returned by `mktemp`:

```bash
gh pr create --title "the pr title" --body-file TMPFILE_PATH
```

Pass `--base <base-branch>` if `<base-branch>` differs from `<default-branch>`. Do not pass `--draft`. Do not add labels or reviewers.

Always remove the tmpfile after the PR creation attempt, regardless of whether it succeeded or failed. Use the same path returned by `mktemp`:

```bash
rm -f TMPFILE_PATH
```

### 7. Report Results

After the PR is created, report:

1. The PR URL (returned by `gh pr create`).
1. The PR title.
1. The commit hash(es) included.
1. A brief summary of what was committed and pushed.
1. Connected issues (if any) and the closing keywords used.

## Plan-Aware Commits

When plan files are detected among uncommitted changes, apply the rules in this section during step 4.

### Detecting Plan Files

Plan files live under `docs/plans/` and its subdirectories (`todo/`, `done/`). Look for Markdown files in these directories among the changed or untracked files.

### Plan Name Cleanup

Well-named plans follow the pattern `YYYY-MM-DD-meaningful-description.md`. Auto-generated names use nonsensical word combinations (e.g., `ethereal-booping-sunbeam.md`, `quizzical-imagining-cerf.md`).

**Every time a plan file is part of a commit, check its filename.** If the name lacks a datestamp prefix or uses a nonsensical auto-generated name:

1. Read the plan file to understand its content.
1. Choose a meaningful slug derived from the plan's title or purpose (e.g., `consolidate-ci-workflows`, `add-user-authentication`).
1. Rename the file to `YYYY-MM-DD-<slug>.md`, using the current date for new plans or the date from the plan's title/content if one is stated.
1. Stage both the deletion of the old path and the addition of the new path.

If the filename already has a datestamp prefix and a meaningful description, leave it as-is.

### Moving Completed Plans

Creating a PR typically means the work described in a plan is complete. When plan files are detected among the changes:

1. Check whether the plan's work is complete. Indicators: all the code changes on the branch correspond to the plan, or the user has already stated that the work is done.
1. If the work is complete, apply [Plan Name Cleanup](#plan-name-cleanup) first (if needed), so any rename happens before the move.
1. Move the (possibly renamed) plan file to `docs/plans/done/` (creating the directory if it does not exist). If both a rename and a move apply, perform a single `git mv` from the original path directly to the final destination (e.g., `docs/plans/done/YYYY-MM-DD-slug.md`).
1. If the plan is currently in `docs/plans/todo/`, the move goes from `todo/` to `done/`.
1. If the plan is in the `docs/plans/` root, the move goes from there to `done/`.
1. Stage the rename (if any) and the file move together as part of the plan commit.

Do not move a plan to `done/` if the work is only partially complete. Plans for work still in progress should stay in `docs/plans/todo/` or the `docs/plans/` root.

### Plan Commit Message

When committing plan files, use a message like `docs: add plan for <meaningful-description>` for new plans, or `docs: move plan to done for <meaningful-description>` when moving a completed plan.

## Error Handling

- **On the base branch**: Report that PRs cannot be created from the base branch. Suggest creating a feature branch first.
- **Nothing to commit and no commits ahead**: Report there is nothing to create a PR for.
- **Pre-commit hook failure**: Fix the issue, re-stage, and create a new commit (never amend).
- **Push rejected**: Report the error. Suggest `git pull --rebase` if the remote has diverged. Never force push.
- **PR already exists**: If `gh pr create` fails because a PR already exists for this branch, run `gh pr view --web` to open the existing PR and report it to the user.
- **No gh CLI**: Report that the `gh` CLI is required and link to https://cli.github.com/.
- **Secret files detected**: Warn the user and exclude them from staging. Continue with the remaining files.
- **Issue detection fails**: If `gh issue view` or `gh issue list` commands fail (network error, auth issue), skip issue detection silently and proceed without the `## Closes` section. Issue detection is best-effort and must never block PR creation.
- **Detected issue is already closed**: Still include it in the `## Closes` section. GitHub handles this gracefully (the keyword is a no-op for already-closed issues, and it still creates a visible cross-reference).
