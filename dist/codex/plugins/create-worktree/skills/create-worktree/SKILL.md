---
name: create-worktree
description: >-
  Create a git worktree, branch, and tmux window from an issue number or a task
  description, with a prompt injected using workmux.
---

# Create Worktree

Create a dedicated worktree + tmux window via `workmux add`, with a prompt injected into the new agent session.

This skill creates the worktree and stops. It does not start the work. To have the new session also plan the issue, use `address-issue-in-worktree` instead.

## Options

The user may provide these options inline:

- **--issue `<number>`**: Force issue lookup, for when a task description is itself a number
- **--no-issue**: Force description handling, even if the argument looks like an issue number
- **--base `<branch>`**: Base the worktree on a specific branch instead of the repository's default branch
- **--resource `<name>`**: Claim a named exclusive resource for the new worktree, and report the holder first if one holds it already
- **--release-resource `<name>`**: Release a claim and stop, creating nothing
- **--list-resources**: Report every claim and stop, creating nothing

## Workflow

### 1. Handle a Claim-Only Request

`--list-resources` and `--release-resource` are about claims, not worktrees. Handle them here and stop: do not classify an argument, build a branch name, or create anything. Neither needs `workmux`, since neither reaches worktree creation.

There is no claim-only counterpart. `--resource` records a claim for a worktree this skill is creating, so a request to claim a resource without creating one has no path here: say so rather than inventing a worktree to attach the claim to.

**Resolve the name first for `--release-resource`**, exactly as step 4a does. The user releases a resource by the name they call it, so "release the DAW" has to reach `release logic`; passing `DAW` through verbatim finds no claim and reports success at having done nothing.

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/manage-resource-claims" list
bash "${CLAUDE_PLUGIN_ROOT}/scripts/manage-resource-claims" release "RESOURCE_NAME"
```

`release` reports `no claim to release` when nothing matched. Treat that as a signal to check the name rather than as success: show the user what `list` reports, so a resource held under a different name is visible instead of silently missed.

`list` prints one `key=value` line per claim and nothing at all when there are none, so report "no resources are claimed" rather than showing empty output. A line carrying `state=stale` names a worktree git no longer lists; say so, and offer `prune` to clear it:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/manage-resource-claims" prune
```

For the rest of the workflow, skip to the next step.

### 2. Classify the Argument

Decide what the user gave you, in this order:

1. **An issue number**: a bare integer or `#N` (e.g. `/create-worktree 42`, `/create-worktree #42`), or anything passed via `--issue N`
2. **An explicit branch name**: a string containing `/` that looks like `type/slug` (e.g. `/create-worktree feature/my-thing`) -- use as-is
3. **A task description**: anything else (e.g. `/create-worktree Fix a bug`)

`--no-issue` forces a bare integer down the description path.

If an issue number was given but `gh` is not installed or not authenticated, say so and ask whether to treat the argument as a task description instead. Do not silently fall back.

### 3. Determine the Branch Name

**From an issue number**, fetch the issue first:

```bash
gh issue view NUMBER --json number,title,labels,body,state
```

If the issue is closed, warn the user and ask whether to proceed.

Build the branch name as `TYPE/NUMBER-SLUG`:

- **TYPE**: `fix` if the labels contain "bug" or "fix", `feature` otherwise
- **SLUG**: slugify the issue title (see the rules below)

Leading with the issue number is what lets the `pr` skill link the resulting pull request back to the issue: its primary detection strategy reads `TYPE/N-description` straight out of the branch name. Without the number, `pr` falls back to searching GitHub by branch slug, which is slower and can match the wrong issue or none at all.

Examples:

- issue 42 "Add dark mode support" labeled `enhancement` -> `feature/42-add-dark-mode-support`
- issue 108 "Login fails with special chars" labeled `bug` -> `fix/108-login-fails-with-special-chars`
- issue 356 "chore: validate skill and path cross-references in bin/validate-plugins" labeled `maintenance` -> `feature/356-validate-skill-and-path-cross-references`
- issue 358 "lint-and-fix: consult project agent config before running a destructive auto-fix" labeled `bug` -> `fix/358-lint-and-fix-consult-project-agent-config`

**From a task description**, build `TYPE/SLUG`:

- **TYPE**: Use `fix` if the user mentions "fix", "bug", "patch", or similar. Use `feature` for everything else.
- **SLUG**: Slugify the description.

**Slugify rules**, applied in this order:

1. **Strip a leading conventional-commit prefix**, with or without a scope: `chore:`, `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `build:`, `ci:`, `perf:`, `style:`, and scoped forms such as `fix(auth):`. TYPE already carries that meaning, so leaving the prefix in produces contradictions like `feature/356-chore-validate-...`. A component name followed by a colon, such as `lint-and-fix:`, is not a conventional-commit type and stays.
1. Lowercase, replace spaces and special characters with hyphens, collapse consecutive hyphens, trim leading and trailing hyphens.
1. Truncate to 50 characters at a word boundary, never mid-word.
1. **Only if step 3 actually truncated**, drop the dangling fragment it left behind. Filler words are `a`, `an`, `and`, `as`, `at`, `before`, `but`, `by`, `for`, `from`, `in`, `into`, `of`, `on`, `or`, `the`, `to`, `when`, `while`, `with`, `without`. If either of the last two words is a filler word, cut from that filler word onward, and repeat. A branch ending in `-before`, `-in`, or `-in-bin` reads as if the name were cut off, because it was.

   The truncation guard matters: `Login fails with special chars` is under 50 characters, so nothing is dropped and `-with-special-chars` survives intact. Trimming unconditionally would mangle short titles that legitimately end in a prepositional phrase.

Examples:

- "create worktree for adding dark mode" -> `feature/adding-dark-mode`
- "spin up a worktree to fix the auth timeout" -> `fix/auth-timeout`
- "new worktree feature/refactor-config" -> `feature/refactor-config` (used as-is)

### 4. Check the Resource Claim

Skip this step entirely when `--resource` was not given.

Some work cannot run in parallel across worktrees because it needs an exclusive resource: a DAW, a simulator, a device, a database, a port, a shared install location. A claim records which worktree holds one. It is advisory: it makes the constraint visible, it does not enforce it.

**4a. Resolve the name against the project's own list first.** Read whichever of `CLAUDE.md` and `AGENTS.md` exist in the repository root, and `copilot-instructions.md` under `.github/`. Any of them may be absent, which is normal, and `CLAUDE.md` is often a symlink to `AGENTS.md`, so read the target rather than treating it as a second source. Check any plan under `docs/plans/todo/` too. Look for a heading containing "exclusive resource" and take the backticked names beneath it as the project's declared list.

Use that list to map a loose phrase onto a declared name, so "the DAW" becomes `logic` without the user retyping it. If the name the user gave is not on the list, say so once and carry on. The resource name is a free string chosen per project, with no registry, so an undeclared name is not an error.

Step 1 resolves names the same way, so a release reaches the claim it means.

**4b. Then check the claim:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/manage-resource-claims" check "RESOURCE_NAME"
```

Branch on the exit code:

- **0 with no output**: the resource is free. Continue.
- **0 with output**: a stale claim exists, from a worktree git no longer lists. Report it and continue; the claim on the new worktree replaces it.
- **3**: the resource is held. Report the holding branch, worktree, and timestamp exactly as the script gives them, and ask whether to proceed anyway.

**Never refuse.** If the user says to proceed, proceed: they always have a reason, and taking a claim over is recorded in the next step. Checking here rather than after the worktree exists means a declined claim stops before any work is done.

### 5. Compose the Prompt

**From an issue number**, pipe the `gh issue view` output through the bundled `compose-issue-prompt` script, which produces:

```text
Work on issue #NUMBER: TITLE

Labels: LABEL1, LABEL2

BODY_CONTENT
```

The script truncates a body longer than about 2000 characters at a paragraph or sentence boundary and appends a pointer to `gh issue view NUMBER`. Do not assemble this block by hand.

**From a task description**, build the prompt directly:

```text
Work on: [user's task description]

Branch: [BRANCH_NAME]
```

Keep the prompt concise -- a few sentences at most. Use the user's own description of the task as the core content.

If the user provided only a branch name with no description, derive a human-readable description from the branch name (e.g., `feature/add-dark-mode` becomes "Work on: add dark mode").

### 6. Create the Worktree

**Important:** The `workmux add` command must be fully detached from the Claude Code process. `workmux` creates tmux windows and spawns new Claude sessions, which cannot initialize while the parent Claude Code process is still running. The `launch-workmux` script handles backgrounding, detaching, waiting, and outputting the log.

**Template escaping:** `workmux` renders the prompt body through MiniJinja, so any literal `{{`, `{%`, or `{#` token in the task description (e.g. GitHub Actions `${{ inputs.x }}` expressions, Jinja/Liquid/Tera/Helm/Vue templates, Handlebars-style snippets) would otherwise be parsed as a template variable reference and rejected with `Template uses undefined variables`. The `launch-workmux` script reads the prompt from stdin, writes an escaped temporary prompt file for `workmux add -P`, and removes that temporary file after `workmux add` exits. Each escaped delimiter renders back to the literal characters, so the prompt stored at `<worktree>/.workmux/PROMPT-*.md` matches the original input.

**Invoking the scripts:** All three scripts ship with this plugin. Invoke them via `bash` followed by the quoted path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/compose-issue-prompt"
bash "${CLAUDE_PLUGIN_ROOT}/scripts/launch-workmux"
bash "${CLAUDE_PLUGIN_ROOT}/scripts/manage-resource-claims"
```

These show the path form only. The runnable invocations, with their arguments, are further down.

Claude Code replaces the plugin-root placeholder with the installed plugin's absolute, version-correct directory before this file reaches you, so there is no search step and no need for a shell variable. Keeping `bash` as the command prefix keeps the command token stable across plugin versions, which is what permission allowlist rules match on.

**If the path was not substituted**, it still begins with `$` rather than `/`. Codex CLI substitutes the placeholder only in hook commands, and OpenCode does not substitute it at all. In that case locate the scripts with `**/create-worktree/**/scripts/compose-issue-prompt`, `**/create-worktree/**/scripts/launch-workmux` and `**/create-worktree/**/scripts/manage-resource-claims`, prefer a match inside the harness's own installed-plugin directory, ignore any match under a `.bak` or other backup directory, confirm it with `test -x`, and use those absolute paths for the rest of the session.

In the examples below, `SCRIPTS_DIR/compose-issue-prompt` and `SCRIPTS_DIR/launch-workmux` are shorthand for the full **quoted paths** shown above.

**Always pass `--base`.** `workmux`'s default base is the _current_ branch, not the repository's default branch, so running this skill from a feature branch silently stacks the new worktree on top of that branch and carries its commits along. Detect the default branch and pass it explicitly:

```bash
gh repo view --json defaultBranchRef -q '.defaultBranchRef.name'
```

**If `gh` is not available**, fall back to:

```bash
git remote show origin | grep 'HEAD branch' | sed 's/.*: //'
```

If the user passed `--base BRANCH`, use that instead. If both detection methods fail, tell the user which branch `workmux` would default to and ask before proceeding.

Then launch the worktree.

**From an issue number**, pipe the issue JSON through both scripts:

```bash
gh issue view NUMBER --json number,title,labels,body,state \
  | bash "SCRIPTS_DIR/compose-issue-prompt" \
  | bash "SCRIPTS_DIR/launch-workmux" "BRANCH_NAME" --base "BASE_BRANCH"
```

Do not pass `--chain-command` here. This skill creates the worktree and stops; `address-issue-in-worktree` is the skill that chains into `address-issue`.

This skill also does not self-assign the issue or label it "in progress". Creating a worktree is not a commitment to do the work, and the user may be setting up several at once. `address-issue-in-worktree` does claim the issue, because it starts the work.

**From a task description**, feed the prompt in directly:

```bash
bash "SCRIPTS_DIR/launch-workmux" "BRANCH_NAME" --base "BASE_BRANCH" <<'WORKMUX_PROMPT'
Work on: [user's task description]

Branch: [BRANCH_NAME]
WORKMUX_PROMPT
```

The script outputs the workmux log directly and cleans up its own log file. Verify success:

```bash
git worktree list
```

**Record the claim, if `--resource` was given.** Do this only after `git worktree list` confirms the worktree, and take the path from that output rather than guessing it: `workmux` owns placement, and a claim on a path that does not exist reads as stale the moment it is written.

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/manage-resource-claims" claim "RESOURCE_NAME" \
  --worktree "WORKTREE_PATH" --branch "BRANCH_NAME" --issue NUMBER
```

Drop `--issue` on the description path. The script prints what it did: a fresh claim or a stale claim cleared. Relay that line rather than restating it.

**Add `--take-over "HOLDER_ID"` only if the user approved a takeover in step 4**, passing the `id` of the holder they were shown, which `check` prints and the refusal message repeats. Without it, `claim` exits 3 and refuses when another worktree holds the resource, which is deliberate: step 4's check and this write are separate operations, so a resource that was free at the check can be held by now.

The flag names a holder rather than saying yes because approval is about a particular one. If a third worktree took the resource in the meantime, consent to displace the first says nothing about displacing it, and `claim` refuses again rather than acting on approval the user did not give.

The token is the claim's `id` rather than its worktree path or its timestamp, because neither of those identifies a claim: a path can be reused, and a timestamp has second resolution, so an approval naming either could transfer to a different claim made in between. Either exit 3 means the holder changed under you: report what the script names and ask again, then re-run with the new id only if the user says to.

An exit 3 naming the user's own branch is the expected result after `git worktree move` or `git switch`. Same-worktree requires both the path and the branch to match, because matching either would let a worktree that later checked out the same branch take the claim silently. Say that plainly rather than treating it as an error: the user is confirming a takeover of their own claim.

If the claim cannot be written, say so and carry on. The worktree exists and the claim is advisory, so a failure here is worth reporting but is not worth unwinding the work.

**Offer a gitignore entry** when the claim file was created and nothing in the project's `.gitignore` covers it. Ignore the whole prefix rather than the one filename:

```text
.claude/worktree-resources.local.json*
```

The trailing `*` matters. The script writes a `.lock` directory beside the file while it mutates, and an interrupted write can leave a `.XXXXXX` temporary file. Ignoring only the exact filename leaves both committable.

**Add it to the `.gitignore` beside the claim file**, which is the main worktree's, not the one in the worktree this skill was invoked from. The claim file lives in the main worktree, and an uncommitted `.gitignore` only applies within the tree it sits in, so a rule added in a linked worktree leaves the actual file untracked and committable where it is. Committing that `.gitignore` is what makes the rule apply in every worktree. All of it is machine-local state, and committing any of it puts one worktree's claims on every branch.

### 7. Report Success

After confirming the worktree exists in `git worktree list`, report:

- The branch name created
- The tmux window name (to help the user switch to it)
- A note that the prompt was injected into the new session
- For the issue path, the issue number and title
- For the resource path, the resource claimed and whatever the claim replaced

Then stop. Do not start the work.

## Error Handling

- If `workmux` is not installed, inform the user and suggest installing it
- If an issue number was given and `gh` is not installed or not authenticated, say so and ask whether to treat the argument as a task description
- If the issue is not found, report that and stop
- If the issue is closed, warn and ask before proceeding
- If the branch already exists and `--open-if-exists` opens it, note that the prompt is only injected on initial creation
- If `--resource` names a resource another worktree holds, report the holder and ask; if the user declines, stop without creating anything
- If the claim file cannot be read, report the error and ask whether to proceed without a claim. A malformed file is never rewritten automatically
- If the claim cannot be written after the worktree exists, report it and continue. The claim is advisory, so a failure to record one does not undo the worktree
- If `--resource` is given outside a git repository, `manage-resource-claims` cannot resolve the shared claim file; report that and stop
