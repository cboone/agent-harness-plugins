---
name: resolve-copilot-pr-feedback
description: >-
  Process and resolve GitHub Copilot automated PR review comments.
---

# Copilot Feedback Resolver

Process and resolve GitHub Copilot's automated PR review comments systematically.

## PR Comments Prohibition (CRITICAL)

**NEVER leave comments directly on GitHub PRs.** This is strictly forbidden:

- `gh pr review --comment` - FORBIDDEN
- `gh pr comment` - FORBIDDEN (except the single required final workflow summary in step 7)
- Any GraphQL mutation that creates new reviews or PR-level comments - FORBIDDEN
- Responding to human review comments - FORBIDDEN

**This skill ONLY processes GitHub Copilot threads.** Never interact with threads created by human reviewers.

**Permitted operations:**

- Fetch unresolved Copilot threads using the script's `fetch` command
- Reply to EXISTING Copilot threads using the script's `reply` command
- Resolve Copilot threads using the script's `resolve` command
- Reply and resolve in one step using the script's `reply-and-resolve` command

**Single exception:** Step 7 uses `gh pr comment` with `--body-file` to post one required final workflow summary after terminal workflow state once PR context exists. This is the ONLY permitted use of `gh pr comment` in this skill. The final summary is blocking: if it cannot be posted, the workflow is incomplete.

## Script Setup

All GraphQL operations use a dedicated script that handles pagination, variable binding, and Copilot author filtering automatically.

**At the start of your session**, locate the script by searching for `**/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`. Note the absolute path and use it with `bash` as the command prefix in all subsequent invocations. Do not use a shell variable, since shell state does not persist between commands.

In the examples below, `resolve-copilot-threads` is a placeholder for the script's **quoted absolute path** (e.g., `"/absolute/path/to/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads"`). Always invoke via `bash` followed by the quoted path, e.g., `bash "/absolute/path/to/scripts/resolve-copilot-threads" fetch ...`. This ensures the command token is `bash`, which matches stable allowlist patterns regardless of the plugin's installed path or version.

## CRITICAL REQUIREMENTS

### YOU MUST RESOLVE THREADS AFTER ADDRESSING THEM

**After fixing any Copilot feedback, you MUST:**

1. **Push the code changes** (`git push`)
1. **Resolve EACH thread** using the script (see below)
1. **Verify resolution** by re-fetching the PR threads

**Addressing feedback without resolving the thread is INCOMPLETE WORK.**

The thread resolution is NOT optional - it's the primary deliverable of this skill. Code changes alone are insufficient.

### Thread Resolution Command (USE THIS!)

```bash
# Replace THREAD_ID with actual thread ID (e.g., PRRT_kwDONZ...)
bash resolve-copilot-threads resolve THREAD_ID
```

Outputs `true` on success. The `reply-and-resolve` command also outputs `true` on success.

**You MUST call this for EVERY thread you address.**

### YOU MUST UPDATE COPILOT INSTRUCTIONS FOR INCORRECT FEEDBACK

**When Copilot feedback is categorized as INCORRECT (conflicts with project conventions/patterns), you MUST:**

1. **Update the project's Copilot instructions** to document the correct pattern
1. This prevents Copilot from flagging the same or similar things in future PRs
1. The update should be concise and explain why the pattern is intentional

**Failure to update Copilot instructions = INCOMPLETE WORK for Incorrect category feedback.**

#### Instructions File Strategy

Copilot supports two types of instruction files in the `.github/` directory:

- **`copilot-instructions.md`**: General instructions for the whole repository
- **`*.instructions.md`** (path-specific): Targeted instructions with `applyTo` frontmatter

**Prefer path-specific instructions files** when the incorrect feedback applies to a specific language or file pattern. Use `copilot-instructions.md` only for repo-wide conventions.

#### CRITICAL: Keep Instructions Concise

Copilot's PR review may not read the full instructions file. Long files risk having instructions truncated or ignored. To maximize effectiveness:

1. **Keep each instructions file under ~1,000 lines**
1. **Put the most important review rules first** in each file
1. **Start with 10-20 specific, actionable instructions** per file
1. **Split by concern**: use path-specific files instead of one large file
1. **Be specific**: clear, concrete instructions work better than vague directives

#### Path-Specific Instructions File Format

```markdown
---
applyTo: "**/*.go"
---

- **Pattern X**: Intentional in this project, do not flag
- **Pattern Y**: Required for Z reason
```

Use the `applyTo` glob to target specific languages or paths. Use `excludeAgent` to limit which Copilot agent reads the file (e.g., `excludeAgent: copilot-coding-agent` to target only code review).

#### General Instructions File (`copilot-instructions.md`)

Reserve for repo-wide conventions that apply to all file types:

```markdown
# GitHub Copilot Instructions

## PR Review

- **Pattern X**: Intentional, do not flag
- **Convention Y**: Required for Z reason

## Code Style

- General conventions here
```

---

## Processing Rules

**ONLY process UNRESOLVED comments. NEVER touch, modify, or re-process already resolved comments. Skip them entirely.**

## Core Workflow

### 1. Fetch ALL Unresolved Copilot Threads

```bash
bash resolve-copilot-threads fetch OWNER REPO PR_NUMBER
```

The script automatically handles pagination and filters for unresolved Copilot-authored threads.

Record the `OWNER`, `REPO`, and `PR_NUMBER` values used for the fetch. This establishes PR context for the required final workflow summary in step 7. If PR context or GitHub authentication cannot be established, report that the required final summary could not be posted and do not mark the workflow complete.

**Output format** (JSON array):

```json
[
  {
    "id": "PRRT_kwDONZ...",
    "path": "src/foo.ts",
    "location": "src/foo.ts:42",
    "isOutdated": false,
    "comments": [{ "author": "copilot", "body": "[nitpick] Consider..." }]
  }
]
```

- **`location`**: Uses the first non-null of `line`, `originalLine`, `startLine`, `originalStartLine`. If all line fields are null, reports `path:(no-line)`.
- **Copilot detection**: Matches author logins `copilot-pull-request-reviewer`, `copilot`, `github-copilot[bot]`, and `github-actions[bot]` (with severity tag verification for the latter).

An empty array `[]` means no unresolved Copilot threads remain.

Treat `[]` as "no currently unresolved Copilot threads," not proof that no work happened in a previous attempt. Before using the no-op summary form, check whether this invocation is recovering from a prior failed summary-post step. If a previous run resolved threads or made code changes but failed to post the required final summary, reuse the preserved summary body from that run or reconstruct it from the prior local output, resolved review threads, branch commits, and branch diff. Do not downgrade that recovery summary to the no-op form just because a later fetch returns `[]`.

### 2. Categorize Each Comment

For each unresolved Copilot comment:

| Category      | Indicator                            | Action                                                       |
| ------------- | ------------------------------------ | ------------------------------------------------------------ |
| **Nitpick**   | Contains `[nitpick]` prefix          | Auto-resolve immediately                                     |
| **Outdated**  | Refers to code that no longer exists | Reply with explanation, resolve                              |
| **Incorrect** | Misunderstands project conventions   | Reply with explanation, resolve, update Copilot instructions |
| **Valid**     | Current, actionable concern          | Fix directly, push, and resolve thread                       |
| **Deferred**  | Valid but out of scope for this PR   | Track in PROJECT.md, reply, resolve                          |

### 3. Resolve Threads

```bash
bash resolve-copilot-threads resolve THREAD_ID
```

### 4. Handle Each Category

#### Nitpicks (`[nitpick]` prefix)

- Resolve immediately without changes
- Optional brief acknowledgment reply

#### Outdated/Incorrect Copilot Comments

**CRITICAL: Reply directly to the Copilot review thread, NOT to the PR.**

**CRITICAL: Always use `--body-file` to pass reply bodies.** Write the response to a temp file first using the Write tool, then reference it with `--body-file`. This keeps the Bash command short and avoids permission prompts from long inline strings.

```bash
# Step 1: Generate a unique tmpfile path:
mktemp /tmp/copilot-reply-XXXXXX
# Returns a unique path, e.g.: /tmp/copilot-reply-r7s8t9

# Step 2: Write the response body to TMPFILE using the Write tool (not shown here as bash)

# Step 3: Pass TMPFILE to the script:
bash resolve-copilot-threads reply THREAD_ID --body-file TMPFILE

# Or reply and resolve in one step:
bash resolve-copilot-threads reply-and-resolve THREAD_ID --body-file TMPFILE
```

```bash
# Step 4: Clean up — issue this as a SEPARATE Bash tool call, not chained onto step 3:
rm -f TMPFILE
```

Replace `TMPFILE` with the actual path returned by `mktemp`. The cleanup must be a separate Bash tool call: each tool invocation runs unconditionally, so the tmpfile is removed whether step 3 succeeded or failed, and the harness preserves step 3's exit code without any shell wrapping. Never combine the two with `; status=$?; rm -f TMPFILE; exit $status` — in zsh (the macOS default shell), `status` is a read-only built-in alias for `$?`, so the assignment fails with `read-only variable: status`. See `plugins/use-git/skills/use-git/references/tmpfile-pattern.md` for the full rationale.

**NEVER pass the reply body inline** (e.g., via `echo "..." |` or heredocs). Always use the Write tool + `--body-file` pattern.

**FORBIDDEN COMMANDS - NEVER USE:**

- `gh pr review <PR_NUMBER> --comment` - adds PR-level comments, not thread replies
- `gh pr comment` - adds PR-level comments
- Any interaction with human reviewer threads

1. Reply to the thread with professional explanation:
   - Outdated: "This comment refers to code refactored in commit abc123. The issue is no longer applicable."
   - Incorrect: "This conflicts with our {convention name} convention. {Brief explanation}. See {reference file} for project guidelines."
1. Resolve the thread using `bash resolve-copilot-threads resolve THREAD_ID`
1. **Update Copilot instructions** to prevent recurrence:
   - **Prefer a path-specific file** (e.g., `.github/css.instructions.md` with `applyTo: "**/*.css"`) when the feedback targets a specific language or file pattern
   - **Use `copilot-instructions.md`** only for repo-wide conventions
   - Example: `- Do not suggest removing .sr-only classes - required accessibility utilities`
   - **If symlink:** Follow it and edit target file

#### Valid Concerns

1. Read the relevant file and understand the context around the flagged line
1. Fix the issue directly (edit the file, apply the suggested improvement)
1. Commit the fix (do NOT push yet; **Step 5: Lint and Fix** runs first)
1. Resolve the thread using the script

#### Deferred (Out of Scope)

**When feedback is valid but out of scope for the current PR:**

1. **Track the follow-up work** in the project's task tracking (e.g., GitHub issue, PROJECT.md, or similar)
1. **Reply to the thread** explaining the deferral:
   - "Valid suggestion. Tracked as follow-up task for a future PR."
1. **Resolve the thread**

**CRITICAL:** Never defer feedback without tracking it. "Acknowledged for follow-up" without creating a trackable task is INCOMPLETE WORK.

### 5. Lint and Fix

**After all code changes are made (from Valid or Incorrect categories), run the `lint-and-fix` skill to catch lint errors before pushing.**

This step prevents CI failures from lint issues introduced while resolving feedback.

1. **Check for changes**: If no files were modified during steps 2-4 (only nitpicks auto-resolved or threads replied to), skip this step. Run `git status --porcelain` to verify: empty output means a clean working tree and you may skip; any output means files were changed and you should continue.
1. **Invoke the `lint-and-fix` skill** using the Skill tool with `--no-push`:

   ```text
   lint-and-fix --no-push
   ```

   This runs all detected project linters and formatters, fixes issues, and commits the fixes without pushing.

1. If lint-and-fix finds and fixes issues, the fixes are committed automatically. Proceed to step 6.

### 6. Verify Completion

1. **Push any changes:** `git push`
1. Re-fetch to confirm all Copilot threads resolved:

   ```bash
   bash resolve-copilot-threads fetch OWNER REPO PR_NUMBER
   ```

   Expected output: `[]` (empty array)

1. Determine terminal workflow status and counts:
   - **No unresolved Copilot feedback**: The initial fetch returned `[]`
   - **Completed**: Every fetched thread was handled according to its category, no failed or pending items remain, and any required code changes were pushed
   - **Partial**: At least one fetched thread was handled, but one or more fetched threads, replies, resolutions, tracking items, instruction updates, lint runs, pushes, or verification checks failed or remain pending
   - **Failed**: The workflow could not fetch or process threads, or no required processing step succeeded
1. Track thread metrics separately from workflow-level failures. Thread metrics cover fetched, resolved, pending, failed, deferred, and code-change threads. Workflow-level failures cover non-thread steps such as instruction updates, follow-up tracking, lint runs, pushes, and verification checks.
1. Proceed to step 7 before claiming completion

### 7. Post PR Summary Comment

**Required:** Once PR context exists, always post exactly one final PR summary comment after terminal workflow state. Do this for every outcome: no unresolved comments, fully resolved comments, only non-code-change resolutions, code-change resolutions, partial processing, failures, and pending items.

Post a summary comment to the PR so reviewers can see the workflow outcome at a glance. Do not post interim PR comments.

**Comment format:**

```markdown
## Copilot Feedback Summary

Status: Completed
Head SHA: `abc1234`

| File            | Category  | Outcome  | Action                                            |
| --------------- | --------- | -------- | ------------------------------------------------- |
| `src/foo.ts:42` | Valid     | Resolved | Fixed null check                                  |
| `lib/util.js:8` | Incorrect | Resolved | Updated error handling; added Copilot instruction |
| `src/ui.tsx:20` | Deferred  | Resolved | Tracked follow-up work                            |
| `docs/api.md:5` | Nitpick   | Resolved | Auto-resolved                                     |

Counts: 4 fetched, 3 resolved, 1 deferred, 2 code-change threads.
```

- Status must be one of `Completed`, `No unresolved Copilot feedback`, `Partial`, or `Failed`
- The trailing `Counts:` line is one short sentence at the end of the comment. Include only non-zero counts from this set: fetched, resolved, pending, failed, deferred, code-change threads, workflow failures. Omit zero-valued metrics; do not render an empty table or "0" entries. If every count is zero, omit the `Counts:` line entirely.
- Pluralize naturally (`1 fetched`, `2 fetched`; `1 code-change thread`, `2 code-change threads`; `1 workflow failure`, `2 workflow failures`).
- Table includes all processed threads when the comment remains safely postable, not only Valid and Incorrect threads
- If the processed-thread table would make the PR comment too large, replace detailed rows with aggregate category/outcome rows and state how many thread detail rows were omitted. Keep the full thread-by-thread table in the local final output for the agent/user audit trail.
- Incorrect category notes Copilot instruction additions in the Action column
- Thread IDs omitted (meaningless to human reviewers)
- Non-thread failures must be described in a failure details section, not forced into the thread table

If no unresolved Copilot comments were found, use this no-op form:

```markdown
## Copilot Feedback Summary

Status: No unresolved Copilot feedback
Head SHA: `abc1234`

No unresolved Copilot comments were found.
```

If processing was partial or failed, include failure details, the remaining required action, and the trailing counts line:

```markdown
## Copilot Feedback Summary

Status: Partial
Head SHA: `abc1234`

| File            | Category | Outcome  | Action                        |
| --------------- | -------- | -------- | ----------------------------- |
| `src/foo.ts:42` | Valid    | Resolved | Fixed null check              |
| `src/bar.ts:7`  | Outdated | Failed   | Reply failed                  |
| `lib/baz.ts:9`  | Nitpick  | Pending  | Resolution still required     |

### Failure Details

| Scope    | Item       | Outcome | Remaining action    |
| -------- | ---------- | ------- | ------------------- |
| Workflow | `git push` | Failed  | Push branch changes |

### Remaining Required Action

- Resolve the failed reply for `src/bar.ts:7`
- Resolve the pending nitpick at `lib/baz.ts:9`
- Push branch changes

Counts: 3 fetched, 2 resolved, 1 pending, 1 failed, 1 code-change thread, 1 workflow failure.
```

**No-op summary idempotency:** Before posting a `No unresolved Copilot feedback` summary, inspect existing top-level PR comments for a `## Copilot Feedback Summary` comment with the same head SHA and no-op status. If one already exists and this invocation did not recover a failed summary-post attempt, do not add another no-op comment. Report the existing summary comment URL locally and treat that existing same-head no-op summary as satisfying the final summary requirement for this no-op run. This idempotency exception applies only to empty-fetch no-op runs; if this invocation processed threads, made code changes, or is recovering a failed summary-post attempt, post the required outcome summary.

**Mechanics:**

```bash
# Step 1: Generate a unique tmpfile path:
mktemp /tmp/copilot-summary-XXXXXX

# Step 2: Write comment body to TMPFILE using the Write tool (not shown here as bash)

# Step 3: Post the comment:
gh pr comment PR_NUMBER --repo OWNER/REPO --body-file TMPFILE
```

```bash
# Step 4: Clean up — issue this as a SEPARATE Bash tool call, not chained onto step 3:
rm -f TMPFILE
```

Replace `OWNER`, `REPO`, `PR_NUMBER`, and `TMPFILE` with actual values recorded during fetch. Always pass `--repo OWNER/REPO` so the final summary targets the intended PR even if the current checkout or working directory changes. The cleanup must be a separate Bash tool call (see [Outdated/Incorrect Copilot Comments](#outdatedincorrect-copilot-comments) above for the rationale): chaining with `; status=$?; rm -f TMPFILE; exit $status` breaks under zsh because `status` is a read-only built-in alias for `$?`.

If the comment fails, log the error and do not claim completion. Thread resolution, code changes, and the required final PR summary are all workflow deliverables.

When the final summary comment fails, preserve the exact intended summary Markdown in the local final output. A later retry must use that preserved body, or reconstruct the same outcome from available PR and git evidence, before falling back to any no-op summary.

## Reply Templates

First, generate a unique tmpfile path with `mktemp /tmp/copilot-reply-XXXXXX`. Write these to the returned path using the Write tool, then pass via `--body-file`. Clean up the tmpfile (`rm -f TMPFILE`) after each reply operation as a **separate Bash tool call**, not chained onto the reply command.

**For outdated comments:**

```text
This comment refers to code that has been refactored in commit [hash]. The issue is no longer applicable.
```

**For incorrect/convention conflicts:**

```text
This suggestion conflicts with our {convention name} convention. {Brief explanation of why}. See {reference file} for project guidelines.
```

## Success Criteria

**Task is INCOMPLETE until ALL of these are done:**

1. All code changes pushed to the PR branch
1. **EVERY addressed thread resolved via the script** (not just code fixed!)
1. **For INCORRECT feedback: Copilot instructions updated** (path-specific `*.instructions.md` preferred, or `copilot-instructions.md` for repo-wide conventions)
1. **For DEFERRED feedback: Task tracked** (GitHub issue, PROJECT.md, or similar)
1. **Linters and formatters pass** (via `lint-and-fix` skill, if any files were changed while addressing feedback)
1. Re-fetch confirms empty array `[]` for all processed threads
1. Output summary table (see format below)
1. **Final PR summary comment posted via step 7** after terminal workflow state, once PR context exists. For empty-fetch no-op runs only, an existing same-head no-op summary may satisfy this requirement without adding a duplicate comment.

If PR context or GitHub authentication is unavailable, or if `gh pr comment` fails, the workflow is incomplete. Report the failure locally and include the remaining action needed to post the required summary.

### Required Output: Thread Summary Table

**You MUST output this table after processing all threads:**

```text
| Thread ID | File:Line | Category | Action Taken | Status |
|-----------|-----------|----------|--------------|--------|
| PRRT_xxx  | src/foo.ts:42 | Nitpick | Auto-resolved | Resolved |
| PRRT_yyy  | src/bar.ts:15 | Valid | Fixed null check | Resolved |
| PRRT_zzz  | lib/util.js:8 | Outdated | Code refactored | Resolved |
| PRRT_aaa  | src/ui.tsx:20 | Deferred | Tracked in PROJECT.md | Resolved |
```

**Column definitions:**

- **Thread ID**: GraphQL thread ID (truncated for readability)
- **File:Line**: Location of the comment
- **Category**: Nitpick, Valid, Outdated, Incorrect, or Deferred
- **Action Taken**: Brief description of resolution (10 words max)
- **Status**: Resolved, Failed, or Pending

**Common failure mode:** Fixing code but forgetting to resolve the threads. This leaves the PR with unresolved conversations even though the issues are fixed. ALWAYS run the resolution command after pushing code.

## Error Handling

- API failures: Retry with proper auth
- Thread ID issues: Use alternative queries
- Fix failures: Retry with alternative approach or defer if out of scope
- Summary comment failures: Log the error, preserve the intended summary Markdown in the local final output, and treat the workflow as incomplete until the required final summary posts successfully
- Partial resolution is better than none, but a partial or failed terminal state still requires the final PR summary once PR context exists
