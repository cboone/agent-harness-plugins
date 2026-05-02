---
name: create-worktree-from-issue
description: >-
  Find a GitHub issue in the current repository and create a new git worktree,
  branch, and tmux window for working on it using workmux. Use when the user
  says "start issue", "create worktree from issue", "create worktree for
  issue", or references starting work on a GitHub issue by number (e.g.,
  "#42") or by description (e.g., "the dark mode issue") in a new worktree.
  Requires the gh CLI and workmux to be installed.
---

# Create Worktree from Issue

Find a GitHub issue and create a dedicated worktree + tmux window via `workmux add`.

## Workflow

### 1. Find the Issue

The user provides either an issue number or descriptive text.

**By number:**

```bash
gh issue view NUMBER --json number,title,labels,body,state
```

**By text (fuzzy search):**

```bash
gh issue list --search "USER_TEXT" --state all --json number,title,labels,state --limit 10
```

If the search returns exactly one result, proceed automatically with that issue without asking for additional confirmation.

If the search returns multiple results, present them to the user and ask which one to use.

If no results, try broadening the search or ask the user to refine their query.

### 2. Mark Issue In Progress

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

The `gh label create` command is safe to run even if the label already exists — `2>/dev/null` suppresses the "already exists" error and `|| true` ensures a zero exit code so the subsequent command always runs. This ensures the label is available before `gh issue edit --add-label` attempts to use it, since `gh` does **not** auto-create labels.

Self-assignment is idempotent — safe to re-run if the assignee already exists.

If any command fails, warn the user but continue with worktree creation. Status marking is best-effort and must never block the primary workflow.

### 3. Build the Branch Name

Construct a branch name in the format `TYPE/SLUG` where:

- **TYPE**: Derive from issue labels. Use `fix` for labels containing "bug" or "fix". Use `feature` for everything else (including when no labels match).
- **SLUG**: Slugify the issue title: lowercase, replace spaces and special characters with hyphens, collapse consecutive hyphens, trim leading/trailing hyphens, truncate to 50 characters at a word boundary.

Examples:

- Issue "Add dark mode support" with label "enhancement" -> `feature/add-dark-mode-support`
- Issue "Login fails with special chars" with label "bug" -> `fix/login-fails-with-special-chars`
- Issue "Update README" with no labels -> `feature/update-readme`

### 4. Compose the Issue Prompt

Build a prompt from the issue data retrieved in step 1. Format:

```text
Work on issue #NUMBER: TITLE

Labels: LABEL1, LABEL2

BODY_CONTENT
```

- If the issue body exceeds approximately 2000 characters, truncate it at the nearest paragraph or sentence boundary and append: "(Issue body truncated. Run `gh issue view NUMBER` for full details.)"
- If the issue body is empty, omit it.
- If there are no labels, omit the labels line.

### 5. Create the Worktree

Derive a filesystem-safe name from the branch by replacing `/` with `-`. For example, `feature/add-dark-mode` becomes `feature-add-dark-mode`. This `SAFE_NAME` is used only for the temporary prompt file path; pass the original `BRANCH_NAME` (with the slash) to `launch-workmux`.

Use the Write tool to create a temporary prompt file at `/tmp/workmux-prompt-SAFE_NAME.md` with the composed prompt from step 4. Using the Write tool avoids shell escaping issues with arbitrary issue body content. Substituting the unsanitized `BRANCH_NAME` would cause the `Write` tool to treat the slash as a directory separator, creating a stray subdirectory under `/tmp/`.

**Important:** The `workmux add` command must be fully detached from the Claude Code process. `workmux` creates tmux windows and spawns new Claude sessions, which cannot initialize while the parent Claude Code process is alive. The `launch-workmux` script handles backgrounding, detaching, waiting, and outputting the log.

**Template escaping:** `workmux` renders the prompt body through MiniJinja, so any literal `{{`, `{%`, or `{#` token in the issue body (e.g. GitHub Actions `${{ inputs.x }}` expressions, Jinja/Liquid/Tera/Helm/Vue templates, Handlebars-style snippets) would otherwise be parsed as a template variable reference and rejected with `Template uses undefined variables`. The `launch-workmux` script wraps the prompt file through `escape_minijinja_delimiters` before invoking `workmux add`, replacing each delimiter with a `{{ "..." }}` expression that renders back to the literal characters. The rendered prompt stored at `<worktree>/.workmux/PROMPT-*.md` matches the original input verbatim, so the new agent session sees the issue body unchanged.

**Locating the script:** At the start of your session, locate the script by searching for `**/create-worktree-from-issue/scripts/launch-workmux`. Note the absolute path and use it with `bash` as the command prefix in all subsequent invocations. Do not use a shell variable, since shell state does not persist between commands.

In the example below, `SCRIPTS_DIR/launch-workmux` is a placeholder for the script's **quoted absolute path** (e.g., `"/absolute/path/to/plugins/create-worktree-from-issue/scripts/launch-workmux"`). Always invoke via `bash` followed by the quoted path. This ensures the command token is `bash`, which matches stable allowlist patterns regardless of the plugin's installed path or version.

**Important:** Do not delete the prompt file immediately after launching. `workmux` runs asynchronously and may not read the file for several seconds. Wait and verify success before cleaning up.

Do not specify a `--base` branch. Let `workmux` use its default.

```bash
bash "SCRIPTS_DIR/launch-workmux" "BRANCH_NAME" "/tmp/workmux-prompt-SAFE_NAME.md"
```

The script outputs the workmux log directly and cleans up its own log file. Verify success:

```bash
git worktree list
```

If the log shows success and the worktree appears in the list, clean up the prompt file:

```bash
rm -f /tmp/workmux-prompt-SAFE_NAME.md
```

If the log shows an error (e.g., "Failed to read prompt file"), the prompt file may have been deleted too early or another issue occurred. Check the log output for details.

### 6. Report Success

After confirming the worktree exists in `git worktree list`, report:

- The issue number and title
- The branch name created
- The tmux window name (to help the user switch to it)
- A note that the issue context was injected into the new session
- Whether the issue was marked in progress (assigned and labeled), or if status marking was skipped/failed

## Error Handling

- If `gh` is not authenticated, instruct the user to run `gh auth login`
- If `workmux` is not installed, inform the user
- If the issue is closed, warn the user and ask if they want to proceed anyway
- If status marking fails (assignment or labeling), warn the user but continue with worktree creation — status marking is best-effort
