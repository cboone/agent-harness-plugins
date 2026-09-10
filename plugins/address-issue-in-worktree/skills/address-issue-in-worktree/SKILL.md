---
name: address-issue-in-worktree
description: >-
  Create a git worktree, branch, and tmux window for a GitHub issue using
  workmux, then have the new session run address-issue to plan the work and
  stop for approval. Use when the user says "address issue in worktree",
  "start issue", "work on issue #42 in a worktree", or references starting
  work on a GitHub issue by number (e.g., "#42") or by description (e.g.,
  "the dark mode issue") in a new worktree. Requires the gh CLI and workmux
  to be installed.
---

# Address Issue in Worktree

Create a worktree, branch, and tmux window for a GitHub issue, then have the new session run `address-issue` to plan the work and stop for approval.

The approval gate lives in `address-issue`, not here. This skill creates the worktree and injects a prompt telling the new session which command to run; the plan is produced and approved in that session, not in this one.

To create the worktree without chaining into `address-issue`, use `create-worktree` instead.

## Options

The user may provide these options inline:

- **--no-approval**: Pass `--no-approval` through to the chained `address-issue` command, so the new session plans and executes without stopping

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

**Save the issue JSON to a temporary file and reuse it** for steps 3 and 4 rather than fetching again later:

```bash
gh issue view NUMBER --json number,title,labels,body,state > /tmp/issue-NUMBER.json
```

Step 2 adds an "in progress" label. A second fetch after that point would pick the new label up and inject `Labels: in progress, ...` into the prompt, telling the new session about a label this skill just added. Reading the cached file keeps the prompt describing the issue as the user filed it, and saves a redundant API call. Delete the file once the worktree exists.

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

The `gh label create` command is safe to run even if the label already exists -- `2>/dev/null` suppresses the "already exists" error and `|| true` ensures a zero exit code so the subsequent command always runs. This ensures the label is available before `gh issue edit --add-label` attempts to use it, since `gh` does **not** auto-create labels.

Self-assignment is idempotent -- safe to re-run if the assignee already exists.

If any command fails, warn the user but continue with worktree creation. Status marking is best-effort and must never block the primary workflow.

The "in progress" label is intentionally retained beyond worktree creation and local implementation. It represents active issue lifecycle state until the related pull request is merged or the user explicitly abandons the effort. Do not remove it as part of creating the worktree.

### 3. Build the Branch Name

Construct a branch name in the format `TYPE/SLUG` where:

- **TYPE**: Derive from issue labels. Use `fix` for labels containing "bug" or "fix". Use `feature` for everything else (including when no labels match).
- **SLUG**: The issue number, a hyphen, then the slugified issue title.

**Slugify the title in this order:**

1. **Strip a leading conventional-commit prefix**, with or without a scope: `chore:`, `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `build:`, `ci:`, `perf:`, `style:`, and the scoped forms such as `fix(auth):`. TYPE already carries that meaning, so leaving the prefix in produces contradictions like `feature/356-chore-validate-...`.
1. Lowercase, replace spaces and special characters with hyphens, collapse consecutive hyphens, trim leading and trailing hyphens.
1. Truncate to 50 characters at a word boundary, never mid-word.
1. **Only if step 3 actually truncated**, drop the dangling fragment it left behind. Filler words are `a`, `an`, `and`, `as`, `at`, `before`, `but`, `by`, `for`, `from`, `in`, `into`, `of`, `on`, `or`, `the`, `to`, `when`, `while`, `with`, `without`. If either of the last two words is a filler word, cut from that filler word onward, and repeat. A branch ending in `-before`, `-in`, or `-in-bin` reads as if the name were cut off, because it was.

   The truncation guard matters: issue #108 below is under 50 characters, so nothing is dropped and `-with-special-chars` survives intact. Trimming unconditionally would mangle short titles that legitimately end in a prepositional phrase.

Leading with the issue number is what lets the `pr` skill link the resulting pull request back to the issue: its primary detection strategy reads `TYPE/N-description` straight out of the branch name. Without the number, `pr` falls back to searching GitHub by branch slug, which is slower and can match the wrong issue or none at all.

Examples:

- Issue #42 "Add dark mode support" with label "enhancement" -> `feature/42-add-dark-mode-support`
- Issue #108 "Login fails with special chars" with label "bug" -> `fix/108-login-fails-with-special-chars`
- Issue #7 "Update README" with no labels -> `feature/7-update-readme`
- Issue #356 "chore: validate skill and path cross-references in bin/validate-plugins" with label "maintenance" -> `feature/356-validate-skill-and-path-cross-references` (`chore:` stripped, dangling `in bin` dropped)
- Issue #358 "lint-and-fix: consult project agent config before running a destructive auto-fix" with label "bug" -> `fix/358-lint-and-fix-consult-project-agent-config` (dangling `before` dropped; `lint-and-fix:` is a component name, not a conventional-commit type, so it stays)

### 4. Compose the Issue Prompt

Use the bundled `compose-issue-prompt` helper to convert `gh issue view --json number,title,labels,body,state` output into the prompt. Pass `--chain-command` so the helper appends the instruction that points the new session at `address-issue`:

```text
Work on issue #NUMBER: TITLE

Labels: LABEL1, LABEL2

BODY_CONTENT

---

Start by running this command:

/address-issue NUMBER
```

- If the issue body exceeds approximately 2000 characters, truncate it at the nearest paragraph or sentence boundary and append: "(Issue body truncated. Run `gh issue view NUMBER` for full details.)"
- If the issue body is empty, omit it.
- If there are no labels, omit the labels line.

The chained command is `/address-issue NUMBER`, or `/address-issue NUMBER --no-approval` when the user passed `--no-approval`. The footer deliberately says nothing about stopping for approval: that is `address-issue`'s default behavior, and keeping the gate defined in one place stops the two skills from drifting apart.

### 5. Create the Worktree

**Important:** The `workmux add` command must be fully detached from the Claude Code process. `workmux` creates tmux windows and spawns new Claude sessions, which cannot initialize while the parent Claude Code process is still running. The `launch-workmux` script handles backgrounding, detaching, waiting, and outputting the log.

**Template escaping:** `workmux` renders the prompt body through MiniJinja, so any literal `{{`, `{%`, or `{#` token in the issue body (e.g. GitHub Actions `${{ inputs.x }}` expressions, Jinja/Liquid/Tera/Helm/Vue templates, Handlebars-style snippets) would otherwise be parsed as a template variable reference and rejected with `Template uses undefined variables`. The `launch-workmux` script reads the prompt from stdin, writes an escaped temporary prompt file for `workmux add -P`, and removes that temporary file after `workmux add` exits. Each escaped delimiter renders back to the literal characters, so the issue context stored at `<worktree>/.workmux/PROMPT-*.md` matches the original prompt.

**Invoking the scripts:** Both scripts ship with this plugin. Invoke each via `bash` followed by the quoted path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/compose-issue-prompt"
bash "${CLAUDE_PLUGIN_ROOT}/scripts/launch-workmux" "BRANCH_NAME"
```

Claude Code replaces the plugin-root placeholder with the installed plugin's absolute, version-correct directory before this file reaches you, so there is no search step and no need for a shell variable. Keeping `bash` as the command prefix keeps the command token stable across plugin versions, which is what permission allowlist rules match on.

**If the paths were not substituted**, they still begin with `$` rather than `/`. Codex CLI substitutes the placeholder only in hook commands, and OpenCode does not substitute it at all. In that case locate the scripts with `**/address-issue-in-worktree/**/scripts/compose-issue-prompt` and `**/address-issue-in-worktree/**/scripts/launch-workmux`, prefer matches inside the harness's own installed-plugin directory, ignore any match under a `.bak` or other backup directory, confirm each with `test -x`, and use those absolute paths for the rest of the session.

In the example below, `SCRIPTS_DIR/compose-issue-prompt` and `SCRIPTS_DIR/launch-workmux` are shorthand for the full **quoted paths** shown above.

**Always pass `--base`.** `workmux`'s default base is the _current_ branch, not the repository's default branch, so running this skill from a feature branch silently stacks the new worktree on top of that branch and carries its commits along. Detect the default branch and pass it explicitly:

```bash
gh repo view --json defaultBranchRef -q '.defaultBranchRef.name'
```

**If `gh` is not available**, fall back to:

```bash
git remote show origin | grep 'HEAD branch' | sed 's/.*: //'
```

If the user asked for a specific base branch, use that instead. If both detection methods fail, tell the user which branch `workmux` would default to and ask before proceeding.

```bash
bash "SCRIPTS_DIR/compose-issue-prompt" --chain-command "/address-issue NUMBER" < /tmp/issue-NUMBER.json \
  | bash "SCRIPTS_DIR/launch-workmux" "BRANCH_NAME" --base "BASE_BRANCH"
```

If the user passed `--no-approval`, the chained command carries it through:

```bash
bash "SCRIPTS_DIR/compose-issue-prompt" --chain-command "/address-issue NUMBER --no-approval" < /tmp/issue-NUMBER.json \
  | bash "SCRIPTS_DIR/launch-workmux" "BRANCH_NAME" --base "BASE_BRANCH"
```

Read the cached JSON from step 1 rather than calling `gh issue view` again here, so the "in progress" label added in step 2 does not leak into the prompt. Remove the temporary file afterwards.

The script outputs the workmux log directly and cleans up its own log file. Verify success:

```bash
git worktree list
```

### 6. Report Success

After confirming the worktree exists in `git worktree list`, report:

- The issue number and title
- The branch name created
- The tmux window name (to help the user switch to it)
- A note that the issue context was injected into the new session, and that the new session will run `/address-issue NUMBER`, produce a plan, and stop for approval there
- Whether the issue was marked in progress (assigned and labeled), or if status marking was skipped/failed
- If status marking succeeded, a note that the "in progress" label is retained until PR merge or explicit abandonment

Then stop. The plan and its approval happen in the new session, so do not wait for them here.

## Error Handling

- If `gh` is not authenticated, instruct the user to run `gh auth login`
- If `workmux` is not installed, inform the user
- If the issue is closed, warn the user and ask if they want to proceed anyway
- If status marking fails (assignment or labeling), warn the user but continue with worktree creation -- status marking is best-effort
