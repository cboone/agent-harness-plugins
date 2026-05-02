---
name: create-issue
description: >-
  Create GitHub issues using tmpfiles to avoid permission prompts from large
  multiline Bash arguments.
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
mktemp /tmp/gh-issue-body-XXXXXX
# Returns a unique path, e.g.: /tmp/gh-issue-body-a1b2c3
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

Always remove the tmpfile after the issue creation attempt, regardless of whether it succeeded or failed. Issue the cleanup as a **separate Bash tool call**, not chained onto `gh issue create`:

```bash
rm -f TMPFILE
```

Each Bash tool call runs unconditionally and the prior call's exit code is preserved by the harness, so a separate call cleans up after both successful and failed issue creations without any shell-level wrapping. Never combine the two with `;` followed by an exit-code preservation idiom such as `gh issue create ...; status=$?; rm -f TMPFILE; exit $status`. In zsh (the macOS default shell), `status` is a read-only built-in alias for `$?`, so the assignment fails with `read-only variable: status` and falsely reports a successful issue creation as failed. See `plugins/use-git/skills/use-git/references/tmpfile-pattern.md` for the full rationale.

### 6. Report the Result

Share the issue URL returned by `gh issue create` with the user.

## Error Handling

- If `gh` is not installed or not authenticated, instruct the user to install it from https://cli.github.com/ and run `gh auth login`
- If the repository is not found, check that the user is in a git repo or specified the correct `--repo` flag
- If label assignment fails (label does not exist), create the issue without labels and note which labels were skipped
- Always clean up the tmpfile (using `rm -f`), even if the `gh` command fails
