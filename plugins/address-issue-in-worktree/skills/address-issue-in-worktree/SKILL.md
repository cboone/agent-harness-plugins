---
name: address-issue-in-worktree
description: >-
  Create a git worktree, branch, and tmux window for a GitHub issue using
  workmux, then have the new session run address-issue to plan the work and
  stop for approval. Use when the user says "address issue in worktree",
  "start issue", "work on issue #42 in a worktree", or references starting
  work on a GitHub issue by number (e.g., "#42") or by description (e.g.,
  "the dark mode issue") in a new worktree. Optionally claims a named
  exclusive resource for the worktree, so work that cannot run in parallel is
  recorded rather than remembered. Requires the gh CLI, workmux, and jq to be
  installed.
---

# Address Issue in Worktree

Create a worktree, branch, and tmux window for a GitHub issue, then have the new session run `address-issue` to plan the work and stop for approval.

The approval gate lives in `address-issue`, not here. This skill creates the worktree and injects a prompt telling the new session which command to run; the plan is produced and approved in that session, not in this one.

To create the worktree without chaining into `address-issue`, use `create-worktree` instead.

## Options

The user may provide these options inline:

- **--no-approval**: Pass `--no-approval` through to the chained `address-issue` command, so the new session plans and executes without stopping
- **--resource `<name>`**: Claim a named exclusive resource for the new worktree, and report the holder first if one holds it already

To list or release claims without creating a worktree, use `create-worktree`, which carries `--list-resources` and `--release-resource`.

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

**Save the issue JSON to a temporary file and reuse it** for steps 4 and 5 rather than fetching again later. Generate a unique path first, then write to it:

```bash
mktemp /tmp/issue-json-XXXXXX
# Prints a unique path, e.g. /tmp/issue-json-a1b2c3
```

```bash
gh issue view NUMBER --json number,title,labels,body,state > ISSUE_JSON
```

`ISSUE_JSON` stands for the exact path `mktemp` printed. Substitute that literal path here and in step 6; shell variables do not survive between separate command invocations, so a `${issue_json}` set in one call is empty in the next. A fixed path such as `/tmp/issue-NUMBER.json` would collide between concurrent runs against the same issue and leave the issue body behind when a run fails partway.

Step 3 adds an "in progress" label. A second fetch after that point would pick the new label up and inject `Labels: in progress, ...` into the prompt, telling the new session about a label this skill just added. Reading the cached file keeps the prompt describing the issue as the user filed it, and saves a redundant API call. Delete the file once the worktree exists.

### 2. Check the Resource Claim

Skip this step entirely when `--resource` was not given.

Some work cannot run in parallel across worktrees because it needs an exclusive resource: a DAW, a simulator, a device, a database, a port, a shared install location. A claim records which worktree holds one. It is advisory: it makes the constraint visible, it does not enforce it.

This runs before the issue is claimed in step 3 on purpose. A declined resource leaves no self-assignment and no "in progress" label behind on an issue nobody started.

**Resolve the name against the project's own list first.** Read whichever of `CLAUDE.md` and `AGENTS.md` exist in the repository root, and `copilot-instructions.md` under `.github/`. Any of them may be absent, which is normal, and `CLAUDE.md` is often a symlink to `AGENTS.md`, so read the target rather than treating it as a second source. Check any plan under `docs/plans/todo/` too. Look for a heading containing "exclusive resource" and take the backticked names beneath it as the project's declared list.

Use that list to map a loose phrase onto a declared name, so "the DAW" becomes `logic` without the user retyping it. If the name the user gave is not on the list, say so once and carry on. The resource name is a free string chosen per project, with no registry, so an undeclared name is not an error.

**Then check the claim:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/manage-resource-claims" check "RESOURCE_NAME"
```

Branch on the exit code:

- **0 with no output**: the resource is free. Continue.
- **0 with output**: a stale claim exists, from a worktree git no longer lists. Report it and continue; the claim on the new worktree replaces it.
- **3**: the resource is held. Report the holding branch, worktree, and timestamp exactly as the script gives them, and ask whether to proceed anyway.

**Never refuse.** If the user says to proceed, proceed: they always have a reason, and taking a claim over is recorded in step 6.

**Clean up before any exit from this step.** Step 1 has already written the issue body to `ISSUE_JSON`, and the only other instruction to remove it is in step 6, which none of these exits reach:

```bash
rm -f ISSUE_JSON
```

Substitute the literal path `mktemp` printed. This applies to every way step 2 can stop, not only the common one: the user declining a held resource, the user declining to proceed after the claim file turns out to be unreadable, and `manage-resource-claims` failing for any other reason. Leaving the file behind is the partial-run leak the temp-file handling in step 1 exists to avoid.

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

The `gh label create` command is safe to run even if the label already exists -- `2>/dev/null` suppresses the "already exists" error and `|| true` ensures a zero exit code so the subsequent command always runs. This ensures the label is available before `gh issue edit --add-label` attempts to use it, since `gh` does **not** auto-create labels.

Self-assignment is idempotent -- safe to re-run if the assignee already exists.

If any command fails, warn the user but continue with worktree creation. Status marking is best-effort and must never block the primary workflow.

The "in progress" label is intentionally retained beyond worktree creation and local implementation. It represents active issue lifecycle state until the related pull request is merged or the user explicitly abandons the effort. Do not remove it as part of creating the worktree.

### 4. Let the Launcher Name the Branch

**Do not construct the branch name.** The launcher does it in step 5, by passing `--auto-name --issue NUMBER`. That runs `workmux add -A -P <prompt> --dry-run`, which asks workmux's own generator to read the issue prompt and return a name, and creates nothing. Whatever it returns is used as-is, with the issue number inserted after the type prefix, or at the front when the generator returned a bare slug:

| Issue | Generator returns            | Branch created                   |
| ----- | ---------------------------- | -------------------------------- |
| 387   | `feature/make-things-better` | `feature/387-make-things-better` |
| 42    | `fix/fix-the-login-page`     | `fix/42-fix-the-login-page`      |
| 387   | `make-things-better`         | `387-make-things-better`         |

Leading with the issue number is what lets the `pr` skill link the resulting pull request back to the issue: its primary detection strategy reads `TYPE/N-description` and `N-description` straight out of the branch name. Without the number, `pr` falls back to searching GitHub by branch slug, which is slower and can match the wrong issue or none at all.

The type prefix comes from workmux's naming prompt, not from this skill, so it reflects the user's own `auto_name.system_prompt` and is not derived from the issue labels. Do not add, correct, or second-guess it.

**Reruns reuse the existing branch.** The launcher first looks for a local branch already carrying the issue number and reuses it, so running this skill twice for the same issue reopens the same worktree instead of generating a second name. It reports `Reusing branch <name> for issue <number>`. If more than one local branch matches, it lists them and exits; ask the user which to use and re-run the launcher with that name in the positional form.

#### If the generator is unavailable

`workmux add -A` needs a naming command: the configured agent's CLI, an `auto_name.command`, or the `llm` CLI. When none is reachable the launcher exits non-zero, printing workmux's error followed by `launch-workmux: workmux could not generate a branch name`.

Only then, build the name yourself as `TYPE/SLUG` and re-run with the positional form, `launch-workmux "BRANCH_NAME" --base "BASE_BRANCH"`. SLUG already begins with the issue number, so the finished name reads `feature/42-add-dark-mode-support`.

- **TYPE**: Derive from issue labels. Use `fix` for labels containing "bug" or "fix". Use `feature` for everything else (including when no labels match).
- **SLUG**: The issue number, a hyphen, then the slugified issue title.

**Slugify the title in this order:**

1. **Strip a leading conventional-commit prefix**, with or without a scope: `chore:`, `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `build:`, `ci:`, `perf:`, `style:`, and the scoped forms such as `fix(auth):`. TYPE already carries that meaning, so leaving the prefix in produces contradictions like `feature/356-chore-validate-...`.
1. Lowercase, replace spaces and special characters with hyphens, collapse consecutive hyphens, trim leading and trailing hyphens.
1. Truncate to 50 characters at a word boundary, never mid-word.
1. **Only if step 3 actually truncated**, drop the dangling fragment it left behind. Filler words are `a`, `an`, `and`, `as`, `at`, `before`, `but`, `by`, `for`, `from`, `in`, `into`, `of`, `on`, `or`, `the`, `to`, `when`, `while`, `with`, `without`. If either of the last two words is a filler word, cut from that filler word onward, and repeat. A branch ending in `-before`, `-in`, or `-in-bin` reads as if the name were cut off, because it was.

   The truncation guard matters: issue #108 below is under 50 characters, so nothing is dropped and `-with-special-chars` survives intact. Trimming unconditionally would mangle short titles that legitimately end in a prepositional phrase.

Examples of the fallback:

- Issue #42 "Add dark mode support" with label "enhancement" -> `feature/42-add-dark-mode-support`
- Issue #108 "Login fails with special chars" with label "bug" -> `fix/108-login-fails-with-special-chars`
- Issue #7 "Update README" with no labels -> `feature/7-update-readme`
- Issue #356 "chore: validate skill and path cross-references in bin/validate-plugins" with label "maintenance" -> `feature/356-validate-skill-and-path-cross-references` (`chore:` stripped, dangling `in bin` dropped)
- Issue #358 "lint-and-fix: consult project agent config before running a destructive auto-fix" with label "bug" -> `fix/358-lint-and-fix-consult-project-agent-config` (dangling `before` dropped; `lint-and-fix:` is a component name, not a conventional-commit type, so it stays)

### 5. Compose the Issue Prompt

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

### 6. Create the Worktree

**Important:** The `workmux add` command must be fully detached from the Claude Code process. `workmux` creates tmux windows and spawns new Claude sessions, which cannot initialize while the parent Claude Code process is still running. The `launch-workmux` script handles backgrounding, detaching, waiting, and outputting the log.

**Template escaping:** `workmux` renders the prompt body through MiniJinja, so any literal `{{`, `{%`, or `{#` token in the issue body (e.g. GitHub Actions `${{ inputs.x }}` expressions, Jinja/Liquid/Tera/Helm/Vue templates, Handlebars-style snippets) would otherwise be parsed as a template variable reference and rejected with `Template uses undefined variables`. The `launch-workmux` script reads the prompt from stdin, writes an escaped temporary prompt file for `workmux add -P`, and removes that temporary file after `workmux add` exits. Each escaped delimiter renders back to the literal characters, so the issue context stored at `<worktree>/.workmux/PROMPT-*.md` matches the original prompt.

**Invoking the scripts:** All three scripts ship with this plugin. Invoke each via `bash` followed by the quoted path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/compose-issue-prompt"
bash "${CLAUDE_PLUGIN_ROOT}/scripts/launch-workmux"
bash "${CLAUDE_PLUGIN_ROOT}/scripts/manage-resource-claims"
```

These show the path form only. The runnable invocations, with their arguments, are further down.

Claude Code replaces the plugin-root placeholder with the installed plugin's absolute, version-correct directory before this file reaches you, so there is no search step and no need for a shell variable. Keeping `bash` as the command prefix keeps the command token stable across plugin versions, which is what permission allowlist rules match on.

**If the paths were not substituted**, they still begin with `$` rather than `/`. Codex CLI substitutes the placeholder only in hook commands, and OpenCode does not substitute it at all. In that case locate the scripts with `**/address-issue-in-worktree/**/scripts/compose-issue-prompt`, `**/address-issue-in-worktree/**/scripts/launch-workmux` and `**/address-issue-in-worktree/**/scripts/manage-resource-claims`, prefer matches inside the harness's own installed-plugin directory, ignore any match under a `.bak` or other backup directory, confirm each with `test -x`, and use those absolute paths for the rest of the session.

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
bash "SCRIPTS_DIR/compose-issue-prompt" --chain-command "/address-issue NUMBER" < ISSUE_JSON \
  | bash "SCRIPTS_DIR/launch-workmux" --auto-name --issue NUMBER --base "BASE_BRANCH"
```

If the user passed `--no-approval`, the chained command carries it through:

```bash
bash "SCRIPTS_DIR/compose-issue-prompt" --chain-command "/address-issue NUMBER --no-approval" < ISSUE_JSON \
  | bash "SCRIPTS_DIR/launch-workmux" --auto-name --issue NUMBER --base "BASE_BRANCH"
```

`ISSUE_JSON` is the path `mktemp` printed in step 1; substitute that literal path. Read the cached JSON rather than calling `gh issue view` again here, so the "in progress" label added in step 3 does not leak into the prompt. Remove the file with `rm -f ISSUE_JSON` once the worktree exists.

The script prints the branch name it settled on, as either `Generated branch name: NAME` or `Reusing branch NAME for issue NUMBER`, then outputs the workmux log and cleans up its own log file. Read the branch name from that line rather than assuming one. Verify success:

```bash
git worktree list
```

**Record the claim, if `--resource` was given.** Do this only after `git worktree list` confirms the worktree, and take the path from that output rather than guessing it: `workmux` owns placement, and a claim on a path that does not exist reads as stale the moment it is written.

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/manage-resource-claims" claim "RESOURCE_NAME" \
  --worktree "WORKTREE_PATH" --branch "BRANCH_NAME" --issue NUMBER
```

The script prints what it did: a fresh claim or a stale claim cleared. Relay that line rather than restating it.

**Add `--take-over "HOLDER_ID"` only if the user approved a takeover in step 2**, passing the `id` of the holder they were shown, which `check` prints and the refusal message repeats. Without it, `claim` exits 3 and refuses when another worktree holds the resource, which is deliberate: step 2's check and this write are separate operations, so a resource that was free at the check can be held by now.

The flag names a holder rather than saying yes because approval is about a particular one. If a third worktree took the resource in the meantime, consent to displace the first says nothing about displacing it, and `claim` refuses again rather than acting on approval the user did not give.

The token is the claim's `id` rather than its worktree path or its timestamp, because neither of those identifies a claim: a path can be reused, and a timestamp has second resolution, so an approval naming either could transfer to a different claim made in between. Either exit 3 means the holder changed under you: report what the script names and ask again, then re-run with the new id only if the user says to.

An exit 3 naming the user's own branch is possible but not expected. A claim records the worktree's git admin directory, which survives both `git worktree move` and `git switch`, so either operation is normally recognised as a refresh and needs no approval. It only falls back to requiring the path and the branch together when that identity cannot be resolved, as for a claim recorded against a path that is not a worktree. Where that fallback does produce an exit 3 naming the user's own branch, say so plainly rather than treating it as an error: they are confirming a takeover of their own claim.

If the claim cannot be written, say so and carry on. The worktree exists and the claim is advisory, so a failure here is worth reporting but is not worth unwinding the work.

**Offer a gitignore entry** when the claim file was created and nothing in the project's `.gitignore` covers it. Ignore the whole prefix rather than the one filename:

```text
.claude/worktree-resources.local.json*
```

The trailing `*` matters. The script writes a `.lock` directory beside the file while it mutates, and an interrupted write can leave a `.XXXXXX` temporary file. Ignoring only the exact filename leaves both committable.

**Add it to the `.gitignore` beside the claim file**, which is the main worktree's, not the one in the worktree this skill was invoked from. The claim file lives in the main worktree, and an uncommitted `.gitignore` only applies within the tree it sits in, so a rule added in a linked worktree leaves the actual file untracked and committable where it is. Committing that `.gitignore` is what makes the rule apply in every worktree.

### 7. Report Success

After confirming the worktree exists in `git worktree list`, report:

- The issue number and title
- The branch name, taken from the launcher's `Generated branch name:` or `Reusing branch` line, and whether it was newly generated or reused from an earlier run
- The tmux window name (to help the user switch to it)
- A note that the issue context was injected into the new session, and that the new session will run `/address-issue NUMBER`, produce a plan, and stop for approval there
- Whether the issue was marked in progress (assigned and labeled), or if status marking was skipped/failed
- If status marking succeeded, a note that the "in progress" label is retained until PR merge or explicit abandonment
- For the resource path, the resource claimed and whatever the claim replaced

Then stop. The plan and its approval happen in the new session, so do not wait for them here.

## Error Handling

- If `gh` is not authenticated, instruct the user to run `gh auth login`
- If `workmux` is not installed, inform the user
- If the launcher reports that workmux could not generate a branch name, fall back to naming it yourself and re-run with the positional form, as described in step 3
- If the launcher reports that the issue matches more than one local branch, show the user the candidates and ask which to use, then re-run with that name in the positional form
- If the issue is closed, warn the user and ask if they want to proceed anyway
- If status marking fails (assignment or labeling), warn the user but continue with worktree creation -- status marking is best-effort
- If `--resource` names a resource another worktree holds, report the holder and ask; if the user declines, stop before marking the issue in progress, so nothing is left behind on an issue nobody started
- If the claim file cannot be read, report the error and ask whether to proceed without a claim. A malformed file is never rewritten automatically
- If the claim cannot be written after the worktree exists, report it and continue. The claim is advisory, so a failure to record one does not undo the worktree
