---
name: pr
description: >-
  Lint, commit, push, and create a pull request in one step with no prompts.
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

If a source branch name was extracted, verify it is a valid base for the PR. Run these checks in order, stopping at the first failure:

1. **Not the current branch**: The source branch must differ from the current branch.
1. **Exists on the remote**: Note that `git ls-remote` always exits 0 regardless of whether the branch exists, so check for non-empty output:

   ```bash
   git ls-remote --heads origin <source-branch> | grep -q .
   ```

1. **Not already merged into the default branch**: The source branch may have been merged into the default branch since this branch was created (e.g., a parent feature branch that has since landed). Check whether the source branch is an ancestor of the default branch:

   ```bash
   git fetch origin <default-branch> <source-branch> --quiet
   git merge-base --is-ancestor origin/<source-branch> origin/<default-branch>
   ```

   If the exit code is 0, the source branch has been fully merged into the default branch. Skip it and use `<default-branch>` as `<base-branch>` instead.

If all three checks pass, use the source branch as `<base-branch>`. If any check fails, use `<default-branch>` as `<base-branch>`.

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

Search for GitHub issues that this branch addresses. Combine results from the strategies below, deduplicate by issue number, and record the final list for use in the commit message (step 4) and PR body (step 7).

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

### 5. Lint and Fix

Run the `lint-and-fix` skill to catch lint and formatting errors before pushing. This prevents CI failures from code that does not pass project linters.

1. **Invoke the `lint-and-fix` skill** using the Skill tool with `--no-push`:

   ```text
   lint-and-fix --no-push

   Parent continuation:
   - Caller: pr
   - Resume target: Step 6, push branch, then Step 7, create the pull request.
   - On lint success: Continue immediately to Step 6 without asking the user for confirmation.
   - On lint failure or skipped required lint work: Stop before push and PR creation, then report the unresolved lint state.
   ```

   This runs all detected project linters and formatters, auto-fixes what it can, manually resolves remaining issues, and commits the fixes without pushing.

1. **If no linters are detected**: Proceed to step 6. The absence of linters is not an error.
1. **If all linters pass** (with or without auto-fixes) **and no issues remain unresolved or skipped**: Proceed to step 6. Any fix commits created by `lint-and-fix` will be included in the push.
1. **If any linting issues remain unresolved, any required lint work is skipped, or a required linter cannot run**: Stop and report the unresolved lint state. Do not push or create the PR. The user must resolve the remaining issues before retrying.

### 6. Push to Remote

Push the branch to the remote:

```bash
git push
```

If the branch has no upstream, use:

```bash
git push -u origin HEAD
```

If the push is rejected because the remote has diverged, report the error and stop. Never force push.

### 7. Create the Pull Request

Analyze all commits on the branch (from `git log <base-branch>..HEAD` and `git diff <base-branch>...HEAD`) to generate the PR title and body.

#### Detect the title convention

The title rules below are this skill's default, not an override. They yield to a PR title convention that the project enforces in CI, or that the project or the user documents in an agent config. Check these signals in order and stop at the first match:

1. **CI lints the PR title.** Use Glob to find `.github/workflows/*.yml` and `.github/workflows/*.yaml`, then read each one. Look for a workflow that feeds `github.event.pull_request.title` into a linter, either piped into `commitlint`:

   ```yaml
   - name: Lint PR title
     env:
       PR_TITLE: ${{ github.event.pull_request.title }}
     run: printf '%s\n' "$PR_TITLE" | pnpm exec commitlint
   ```

   or through an action such as `amannn/action-semantic-pull-request`.

   A commitlint config on its own (`.commitlintrc*`, `commitlint.config.*`, or a `commitlint` key in `package.json`) is **not** sufficient. It usually lints commit messages rather than the PR title. The reference to `github.event.pull_request.title` is what makes the title itself constrained.

   When such a workflow exists, read the commitlint config it uses and follow its `type-enum`, `scope-enum`, `subject-case`, and `header-max-length` values rather than the defaults below.

1. **Project agent config states a PR title format.** Read whichever of these exist: `CLAUDE.md` and `AGENTS.md` in the repository root, and `copilot-instructions.md` under `.github/`. Any of them may be absent, which is normal and not an error, and `CLAUDE.md` is often a symlink to `AGENTS.md`, so read the target rather than reporting a duplicate. Also honor any user-level instructions already present in context. If any of them specify a PR title format, follow it.

1. **Merged PR titles are consistent.** As a fallback:

   ```bash
   gh pr list --state merged --limit 20 --json title --jq '.[].title'
   ```

   If most of the returned titles match `^[a-z]+(\([^)]+\))?!?:\s`, the project uses conventional-commit PR titles. Match that style.

If no signal matches, no convention is enforced, so use the defaults below. Record whether signal 1 found a PR title lint workflow, because step 8 keys off it.

#### Title

**When a convention was detected**, follow it and skip the defaults below. Derive the conventional-commit type from the commits on the branch using the same type selection as step 4, use the project's scope vocabulary if it defines one, and respect its configured subject case and length. Under commitlint's defaults that means `type(scope): lowercase subject` in 72 characters or fewer.

**Otherwise**, use this skill's defaults:

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
mktemp /tmp/pr-body-XXXXXX
# Returns a unique path, e.g.: /tmp/pr-body-x4y5z6
```

Then use the **Write** tool to write the full PR body (Summary, Test plan, and Closes sections) to the exact path returned by `mktemp`. In the examples below, `TMPFILE` is a placeholder for that path.

Then create the PR with `--body-file`:

```bash
gh pr create --title "the pr title" --body-file TMPFILE
```

Pass `--base <base-branch>` if `<base-branch>` differs from `<default-branch>`. Do not pass `--draft`. Do not add labels or reviewers.

Always remove the tmpfile after the PR creation attempt, regardless of whether it succeeded or failed. Issue the cleanup as a **separate Bash tool call**, not chained onto `gh pr create`:

```bash
rm -f TMPFILE
```

Each Bash tool call runs unconditionally and the prior call's exit code is preserved by the harness, so a separate call cleans up after both successful and failed PR creations without any shell-level wrapping. Never combine the two with `;` followed by an exit-code preservation idiom such as `gh pr create ...; status=$?; rm -f TMPFILE; exit $status`. In zsh (the macOS default shell), `status` is a read-only built-in alias for `$?`, so the assignment fails with `read-only variable: status` and falsely reports a successful PR creation as failed. See `plugins/use-git/skills/use-git/references/tmpfile-pattern.md` for the full rationale.

### 8. Verify the Title Check

Skip this step entirely unless step 7 found a workflow that lints the PR title. When it did, confirm the title passed:

```bash
gh pr checks --json name,state,link,description,workflow 2> /dev/null || true
```

`gh pr checks` exits non-zero when checks are failing **or** still pending, so a non-zero exit is not an error here. Checks also frequently have not registered yet immediately after `gh pr create`.

This command returns **every** check on the PR, so narrow the result to the title lint before judging it. Match the `workflow` field against the workflow file identified in step 7, falling back to the `name` field when the workflow name is ambiguous. Only that check's state matters here; a red check belonging to any other workflow is out of scope for this step and belongs in the step 9 report as an ordinary CI failure.

- **Title check passed**: continue to step 9.
- **Title check failed**: report that check's `name`, its `description` (the short summary the check itself supplies; `gh pr checks` exposes no fuller reason, so link out rather than inventing one), and its `link`. Then give the user the exact remediation command with a corrected title:

  ```bash
  gh pr edit --title "<corrected title>"
  ```

  Do not run `gh pr edit` automatically.

- **Checks pending, or the title check is not among those returned**: report that the title check has not reported yet and continue.

This step is best-effort and must never block the workflow.

### 9. Report Results

After the PR is created, report:

1. The PR URL (returned by `gh pr create`).
1. The PR title, and whether a project title convention was detected (naming which signal matched) or the skill's defaults were used.
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
- **Lint issues unresolved**: If the `lint-and-fix` skill reports unresolved issues, skipped items, or a required linter that cannot run, stop before pushing. Report the remaining lint errors and suggest the user fix them manually before retrying `/pr`.
- **Push rejected**: Report the error. Suggest `git pull --rebase` if the remote has diverged. Never force push.
- **PR already exists**: If `gh pr create` fails because a PR already exists for this branch, run `gh pr view --web` to open the existing PR and report it to the user.
- **PR title lint check fails**: Report the failing check and a corrected title, following step 8. Never delete and recreate the PR to fix the title; `gh pr edit --title` is the remedy, and the user runs it.
- **No gh CLI**: Report that the `gh` CLI is required and link to https://cli.github.com/.
- **Secret files detected**: Warn the user and exclude them from staging. Continue with the remaining files.
- **Issue detection fails**: If `gh issue view` or `gh issue list` commands fail (network error, auth issue), skip issue detection silently and proceed without the `## Closes` section. Issue detection is best-effort and must never block PR creation.
- **Detected issue is already closed**: Still include it in the `## Closes` section. GitHub handles this gracefully (the keyword is a no-op for already-closed issues, and it still creates a visible cross-reference).
