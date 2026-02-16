---
name: pr
description: >-
  Commit all changes (if needed), push to remote, and create a GitHub pull
  request in one automated step with no prompts. Use when the user says "pr",
  "create a pr", "open a pr", "submit a pr", "push and create pr", "commit and
  create pr", or any variant involving creating a pull request from the current
  branch. Requires the gh CLI to be installed.
---

# PR

Commit, push, and create a pull request in one automated step. Never prompt the user for input — make opinionated decisions at every step.

## Workflow

### 1. Gather Context

Run these commands in parallel to understand the current state:

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
git diff main...HEAD

# Commit history of this branch since diverging from main
git log main..HEAD --oneline

# Check remote tracking status
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "no upstream"
```

Determine the base branch by running:

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

Use this as the base branch instead of hardcoding `main`. Fall back to `main` if the command fails.

### 2. Validate Preconditions

Stop and report an error if any of these are true:

- The current branch **is** the base branch. Do not create a PR from the base branch to itself.
- There are no changes to commit **and** no commits ahead of the base branch. There is nothing to open a PR for.

### 3. Commit Changes (if needed)

If there are staged changes, unstaged changes, or untracked files:

1. **Stage everything** — run `git add -A`. Never stage selectively; the goal is a clean working tree. Exception: never stage files that likely contain secrets (`.env`, `credentials.json`, `*.pem`, `*.key`, etc.). If such files are detected, warn the user and exclude them.
2. **Analyze the diff** to generate a commit message:
   - Examine `git log --oneline -10` output to match the repository's commit message style.
   - Determine the commit type (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`) based on the changes.
   - Write a concise description (under 72 characters) focused on _why_ the change was made.
   - Reference issue numbers if they appear in the branch name (e.g., branch `fix/issue-42` suggests `fixes #42`).
3. **Create the commit** — GPG signed, using a HEREDOC:

```bash
git commit -S -m "$(cat <<'EOF'
type: description here
EOF
)"
```

CRITICAL: Never use `git commit --amend`. Always create a new commit. If a pre-commit hook fails, fix the issue, re-stage, and create a new commit.

If there are no uncommitted changes, skip this step.

### 4. Push to Remote

Push the branch to the remote:

```bash
git push
```

If the branch has no upstream, use:

```bash
git push -u origin HEAD
```

If the push is rejected because the remote has diverged, report the error and stop. Never force push.

### 5. Create the Pull Request

Analyze all commits on the branch (from `git log main..HEAD` and `git diff main...HEAD`) to generate the PR title and body.

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
```

Keep the summary to 1-4 bullet points. Focus on what changed and why.

#### Create the PR

```bash
gh pr create --title "the pr title" --body "$(cat <<'EOF'
## Summary

- Key change 1
- Key change 2

## Test plan

- [ ] Verify change works as expected
EOF
)"
```

Do not pass `--base` unless the base branch is not the repository default. Do not pass `--draft`. Do not add labels or reviewers.

### 6. Report Results

After the PR is created, report:

1. The PR URL (returned by `gh pr create`).
2. The PR title.
3. The commit hash(es) included.
4. A brief summary of what was committed and pushed.

## Error Handling

- **On the base branch**: Report that PRs cannot be created from the base branch. Suggest creating a feature branch first.
- **Nothing to commit and no commits ahead**: Report there is nothing to create a PR for.
- **Pre-commit hook failure**: Fix the issue, re-stage, and create a new commit (never amend).
- **Push rejected**: Report the error. Suggest `git pull --rebase` if the remote has diverged. Never force push.
- **PR already exists**: If `gh pr create` fails because a PR already exists for this branch, run `gh pr view --web` to open the existing PR and report it to the user.
- **No gh CLI**: Report that the `gh` CLI is required and link to https://cli.github.com/.
- **Secret files detected**: Warn the user and exclude them from staging. Continue with the remaining files.
