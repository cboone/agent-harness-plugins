---
name: address-issue
description: >-
  Fetch a GitHub issue, analyze it, plan and execute the work in the current
  branch, and commit with issue references. Use when the user says
  "address issue", "address issue #42", "address #42", "fix issue #42",
  "work on issue #42", "handle issue #42", "resolve issue #42",
  "tackle issue #42", "implement issue #42", or references addressing a
  GitHub issue by number or description. Requires the gh CLI to be installed
  and authenticated.
---

# Address Issue

Fetch a GitHub issue, analyze it, plan and execute the work in the current branch, and commit with issue references.

## Options

The user may provide these options inline:

- **--dry-run**: Fetch and analyze the issue, present the plan, but do not make changes
- **--no-commit**: Make changes but do not commit them
- **--commit-per-change**: Commit after each logical change instead of grouping at the end

## Workflow

### 1. Find the Issue

The user provides either an issue number or descriptive text.

**By number:**

```bash
gh issue view NUMBER --json number,title,labels,assignees,body,state
```

**By text (fuzzy search):**

```bash
gh issue list --search "USER_TEXT" --state all --json number,title,labels,state --limit 10
```

If the search returns exactly one result, proceed automatically with that issue without asking for additional confirmation.

If the search returns multiple results, present them to the user and ask which one to use.

If no results, try broadening the search or ask the user to refine their query.

### 2. Check Issue State

If the issue is closed, warn the user and ask whether to proceed. Do not proceed without confirmation.

### 3. Mark Issue In Progress

If the issue is open, signal that work is starting. Skip this step for closed issues.

**Self-assign:**

```bash
gh issue edit NUMBER --add-assignee @me
```

**Ensure the label exists, then add it:**

```bash
gh label create "in progress" --description "Work is actively being done" --color FBCA04 2> /dev/null || true
gh issue edit NUMBER --add-label "in progress"
```

The `gh label create` command is safe to run even if the label already exists. `2>/dev/null` suppresses the "already exists" error and `|| true` ensures a zero exit code so the subsequent command always runs. This ensures the label is available before `gh issue edit --add-label` attempts to use it, since `gh` does **not** auto-create labels.

Self-assignment is idempotent, safe to re-run if the assignee already exists.

If any command fails, warn the user but continue. Status marking is best-effort and must never block the primary workflow. Record whether this step succeeded for use in step 9.

### 4. Display Issue Context

Show the issue details to establish shared context:

```text
## Issue #NUMBER: TITLE

**State:** open/closed
**Labels:** label1, label2
**Assignees:** user1, user2

BODY_CONTENT
```

- If the issue body exceeds approximately 2000 characters, truncate it at the nearest paragraph or sentence boundary and append: "(Issue body truncated. Run `gh issue view NUMBER` for full details.)"
- If the issue body is empty, note that the body is empty.
- If there are no labels, omit the labels line.
- If there are no assignees, omit the assignees line.

### 5. Analyze the Issue

**Classify the issue** into one of these types based on labels, title, and body content:

| Type            | Signals                                                             | Commit prefix |
| --------------- | ------------------------------------------------------------------- | ------------- |
| bug fix         | "bug" label, "fix", "crash", "error", "broken" in title/body       | `fix`         |
| feature         | "enhancement"/"feature" label, "add", "implement", "support"       | `feat`        |
| documentation   | "documentation" label, "docs", "readme", "guide"                   | `docs`        |
| refactor        | "refactor" label, "clean up", "simplify", "reorganize"             | `refactor`    |
| chore           | "chore"/"maintenance" label, "update", "bump", "dependencies"      | `chore`       |

Default to `feat` when the classification is ambiguous.

**Extract sub-tasks** from the issue body if it contains GitHub task list checkboxes:

- Unchecked items (`- [ ] ...`) become sub-tasks to address
- Checked items (`- [x] ...`) are treated as already completed and skipped

If there are no task list items, treat the entire issue as a single task.

### 6. Plan the Work

1. Explore the codebase to understand the relevant areas
1. Identify the files that need to be created, modified, or deleted
1. Present a plan to the user:

```text
## Plan for Issue #NUMBER

**Classification:** bug fix / feature / documentation / refactor / chore
**Sub-tasks:** N (if extracted from task list)

### Changes

1. Modify `src/auth.go` - fix null pointer in login handler
1. Add `src/auth_test.go` - add test for the fix
1. Update `README.md` - document the new behavior
```

Wait for the user to confirm, adjust, or reject the plan before proceeding.

**If `--dry-run` was specified**: Stop here after displaying the plan. Do not make any changes.

### 7. Execute the Changes

Work through each planned change, announcing progress:

```text
### Change 1 of N: Modify src/auth.go
```

If sub-tasks were extracted from the issue body, work through each sub-task in order.

### 8. Commit the Changes

**If `--no-commit` was specified**: Skip this step entirely.

**If `--commit-per-change` was specified**: Commit after each change in step 7 instead of waiting until the end.

**Default behavior** (neither flag): After all changes are complete, group them into the smallest logical commits that are appropriate. Each commit should be a self-contained, reviewable unit.

All commit messages must:

- Use the conventional commit prefix derived from the issue classification (step 5)
- Include the issue number for GitHub auto-linking: `(#NUMBER)`
- Be concise and descriptive

Examples:

```text
fix: resolve null pointer in login handler (#42)
feat: add dark mode toggle to settings page (#15)
docs: update installation instructions (#88)
```

For multi-commit cases, each commit references the same issue number.

### 9. Mark Issue Done

**Skip this step if**: step 3 was skipped (closed issue) or step 3 failed (status marking unsuccessful).

Remove the "in progress" label:

```bash
gh issue edit NUMBER --remove-label "in progress"
```

Best-effort: if the command fails, warn the user but do not treat it as an error.

### 10. Report Completion

Display a summary of what was done:

```text
## Summary for Issue #NUMBER: TITLE

| #   | Change                              | Status  | Commit  |
| --- | ----------------------------------- | ------- | ------- |
| 1   | Fix null pointer in auth.go         | Done    | abc1234 |
| 2   | Add test for login handler          | Done    | abc1234 |
| 3   | Update README                       | Skipped | -       |
```

**Total**: N changes made, M skipped
```

If any changes were skipped, list them with explanations.

### 11. Offer Next Steps

Suggest logical follow-up actions:

- `/pr` to create a pull request for the changes
- If the issue had sub-tasks and some remain unchecked, note which items still need attention
- If the issue references other issues, mention them

## Error Handling

- If `gh` is not installed or not authenticated, instruct the user to install it from https://cli.github.com/ and run `gh auth login`
- If the issue is not found, report that and stop
- If the issue is closed, warn and ask before proceeding
- If status marking fails (assignment or labeling), warn but continue with the work
- If a planned change cannot be made (file not found, ambiguous requirement), skip it with an explanation and continue with the remaining changes
- If commits fail, report the error and leave changes uncommitted for the user to handle
