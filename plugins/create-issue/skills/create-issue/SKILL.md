---
name: create-issue
description: >-
  Create a GitHub issue using the gh CLI with tmpfile-based body content to
  avoid permission prompts from large multiline Bash arguments. Use when the
  user says "create issue", "create a GitHub issue", "file an issue", "open an
  issue", "new issue", "report a bug", "request a feature", or asks to create
  an issue on a GitHub repository. Requires the gh CLI to be installed and
  authenticated.
---

# Create Issue

Create GitHub issues cleanly by writing the body to a tmpfile and passing it via `--body-file`.

## Why This Skill Exists

When creating GitHub issues, passing a large multiline `--body` string directly to `gh issue create` in a Bash command triggers Claude Code permission prompts because the command appears complex. This skill avoids that by using the Write tool to create a temporary file containing the issue body, then passing a short, simple `gh issue create --body-file` command to Bash.

## Workflow

### 1. Gather Issue Details

Determine the issue title, body, labels, and assignees from the user's request. If the user's request is vague, ask clarifying questions. At minimum, you need:

- **Title**: A concise summary of the issue
- **Body**: A detailed description (can be multiple paragraphs, include code blocks, checklists, etc.)

Optional fields:

- **Labels**: Relevant labels (e.g., `bug`, `enhancement`, `documentation`)
- **Assignees**: GitHub usernames to assign
- **Milestone**: A milestone to associate with the issue
- **Project**: A GitHub project to add the issue to

### 2. Confirm the Repository

If the user specifies a repository (e.g., "file an issue on org/repo"), use the `--repo` flag. Otherwise, the issue will be created in the current repository.

### 3. Write the Issue Body to a Tmpfile

First, generate a unique temporary file path using `mktemp`:

```bash
mktemp /tmp/gh-issue-body-XXXXXX.md
# Returns a unique path, e.g.: /tmp/gh-issue-body-a1b2c3.md
```

Then use the **Write** tool to write the full issue body in Markdown format to the exact path returned by `mktemp`. In the examples below, `TMPFILE` is a placeholder for that path.

This is the critical step that avoids permission prompts: the Write tool handles multiline content natively, keeping the subsequent Bash command short and simple.

### 4. Create the Issue

Run a single, short `gh issue create` command using the tmpfile path from step 3:

```bash
gh issue create --title "Issue title here" --body-file TMPFILE
```

Add optional flags as needed:

```bash
gh issue create --title "Issue title here" --body-file TMPFILE --label "bug" --label "enhancement" --assignee "@me"
```

For a different repository:

```bash
gh issue create --repo owner/repo --title "Issue title here" --body-file TMPFILE
```

### 5. Clean Up

Always remove the tmpfile after the issue creation attempt, regardless of whether it succeeded or failed:

```bash
rm -f TMPFILE
```

### 6. Report the Result

Share the issue URL returned by `gh issue create` with the user.

## Error Handling

- If `gh` is not installed or not authenticated, instruct the user to install it from https://cli.github.com/ and run `gh auth login`
- If the repository is not found, check that the user is in a git repo or specified the correct `--repo` flag
- If label assignment fails (label does not exist), create the issue without labels and note which labels were skipped
- Always clean up the tmpfile (using `rm -f`), even if the `gh` command fails
