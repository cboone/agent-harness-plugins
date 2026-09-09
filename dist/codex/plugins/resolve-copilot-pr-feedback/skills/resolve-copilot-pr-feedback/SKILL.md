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
- Fetch Copilot review-body findings using the script's `fetch-reviews` command
- Read existing PR comments (never write them) to check for prior summaries
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

### 1. Fetch ALL Unresolved Copilot Feedback

Copilot leaves feedback in two places, and **you MUST check both**. Fetching only threads is how real feedback gets missed.

```bash
bash resolve-copilot-threads fetch OWNER REPO PR_NUMBER
bash resolve-copilot-threads fetch-reviews OWNER REPO PR_NUMBER
```

The script automatically handles pagination and filters for Copilot-authored content.

Record the `OWNER`, `REPO`, and `PR_NUMBER` values used for the fetch. This establishes PR context for the required final workflow summary in step 7. If PR context or GitHub authentication cannot be established, report that the required final summary could not be posted and do not mark the workflow complete.

#### 1a. Threads (`fetch`)

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

**`[]` from `fetch` is a statement about threads only. It is never proof that Copilot left no feedback.** Two separate things can hide behind it:

- Copilot may have filed findings in a review body instead of a thread. That is what `fetch-reviews` in step 1b is for, and you must run it before concluding anything.
- A previous attempt may have already done the work. Before using the no-op summary form, check whether this invocation is recovering from a prior failed summary-post step. If a previous run resolved threads or made code changes but failed to post the required final summary, reuse the preserved summary body from that run or reconstruct it from the prior local output, resolved review threads, branch commits, and branch diff. Do not downgrade that recovery summary to the no-op form just because a later fetch returns `[]`.

#### 1b. Review-body findings (`fetch-reviews`)

Copilot does not always open a thread. When it declines to comment on a line the latest push did not touch, it files the finding in the **review body** under a "suppressed comments" section and reports `Comments generated: 0 new`. Those findings are real and actionable, they have no thread id, and `fetch` cannot see them.

**Output format** (JSON array, one entry per Copilot review that has a body):

```json
[
  {
    "id": 5035762218,
    "url": "https://github.com/OWNER/REPO/pull/54#pullrequestreview-5035762218",
    "submittedAt": "2026-08-21T18:02:11Z",
    "headline": "### 🔵 Needs a closer look\n\nThe Phase 2 plan section is internally inconsistent...",
    "hasSuppressedMarker": true,
    "suppressed": "**docs/plans/todo/phased-build-plan.md:243**\n* This section now states...",
    "findings": [{ "location": "docs/plans/todo/phased-build-plan.md:243", "path": "docs/plans/todo/phased-build-plan.md", "line": 243, "body": "* This section now states..." }]
  }
]
```

- **`findings`**: the structured parse. Treat each entry exactly like a thread comment, except that it cannot be replied to or resolved.
- **`suppressed`**: the raw section, verbatim.
- **`headline`**: Copilot's verdict and lead paragraph. Sometimes the only place a finding is stated; read it.

**Format-drift rule (CRITICAL):** if `hasSuppressedMarker` is `true` but `findings` is empty, Copilot has changed its review-body layout. Read the `suppressed` field directly and extract the findings yourself. **Never treat that combination as "no findings."** Report the drift in the step 7 summary so it gets fixed.

An entry with `hasSuppressedMarker: false` and an empty `findings` array carries no review-body findings. If every entry looks like that, and `fetch` returned `[]`, only then is there genuinely nothing to process.

#### 1c. Check for findings handled in a previous run

Copilot re-emits the same suppressed finding in **every** later review until the underlying code changes. Review bodies are immutable, so a finding you fixed last run will still be there this run. Without a check, the skill would re-report or re-fix it forever.

Before acting on any review-body finding, read the PR's existing summary comments:

```bash
gh api repos/OWNER/REPO/issues/PR_NUMBER/comments --jq '.[] | select(.body | startswith("## Copilot Feedback Summary")) | .body'
```

This reads comments; it never writes one, so it does not violate the PR Comments Prohibition. Then, for each finding:

1. **Recorded before, and no longer applies.** A prior summary has a `Review body` row for this `path:line`, and reading the current code confirms the finding is addressed. Record it as `Previously handled` and change nothing.
1. **Recorded before, but still applies.** The earlier run deferred it, or a fix regressed. Process it normally.
1. **Path matches, line does not.** Line numbers drift as files change. Treat it as a candidate and let the code check decide, rather than assuming it is new.
1. **No match.** Process it normally.

Always verify against the current code before deciding. Verification is what keeps this correct when someone edits or deletes a summary comment: the cost is a re-check, not a wrong answer.

### 2. Categorize Each Comment

For each unresolved Copilot comment **and each review-body finding**:

| Category      | Indicator                            | Action                                                       |
| ------------- | ------------------------------------ | ------------------------------------------------------------ |
| **Nitpick**   | Contains `[nitpick]` prefix          | Auto-resolve immediately                                     |
| **Outdated**  | Refers to code that no longer exists | Reply with explanation, resolve                              |
| **Incorrect** | Misunderstands project conventions   | Reply with explanation, resolve, update Copilot instructions |
| **Valid**     | Current, actionable concern          | Fix directly, push, and resolve thread                       |
| **Deferred**  | Valid but out of scope for this PR   | Track in PROJECT.md, reply, resolve                          |

The same five categories apply to review-body findings, but the Action column does not: they have no thread to reply to or resolve. See [Review-Body Findings](#review-body-findings-no-thread) for what to do instead. Note also that review-body findings carry **no `[nitpick]` prefix**, so judge Nitpick from the prose rather than looking for a tag.

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

#### Review-Body Findings (no thread)

Findings from `fetch-reviews` have **no thread id**. Do not attempt `reply`, `resolve`, or `reply-and-resolve` for them; there is nothing to address those commands to, and the calls will fail. Do not invent a thread by opening a PR comment either: the PR Comments Prohibition still applies, and the step 7 summary is the only reporting channel these findings have.

Apply the same categories, minus the thread operations:

| Category      | What to do                                                                    | Outcome recorded |
| ------------- | ----------------------------------------------------------------------------- | ---------------- |
| **Valid**     | Read the flagged line, fix the issue, commit (do not push; step 5 runs first) | `Fixed`          |
| **Incorrect** | Update the Copilot instructions file so it stops recurring                    | `Noted`          |
| **Deferred**  | Track the follow-up work in a GitHub issue, PROJECT.md, or similar            | `Tracked`        |
| **Outdated**  | Confirm against current code, then record it; no code change                  | `Noted`          |
| **Nitpick**   | Record it; no code change                                                     | `Noted`          |

Every review-body finding gets a row in the step 7 summary and in the local audit table, whatever its category. Since Copilot will keep re-emitting it and there is no thread to resolve, that row **is** the record that it was handled, and step 1c reads it back on the next run.

If step 1b reported format drift (`hasSuppressedMarker: true`, empty `findings`), extract what you can from the raw `suppressed` text, process those findings normally, and add a workflow-level failure noting that the review-body format changed and the parser needs updating.

### 5. Lint and Fix

**After all code changes are made (from Valid or Incorrect categories), run the `lint-and-fix` skill to catch lint errors before pushing.**

This step prevents CI failures from lint issues introduced while resolving feedback.

1. **Check for changes**: If no files were modified during steps 2-4 (only nitpicks auto-resolved or threads replied to), skip this step. Run `git status --porcelain` to verify: empty output means a clean working tree and you may skip; any output means files were changed and you should continue.
1. **Invoke the `lint-and-fix` skill** using the Skill tool with `--no-push`:

   ```text
   lint-and-fix --no-push

   Parent continuation:
   - Caller: resolve-copilot-pr-feedback
   - Resume target: Step 6, push changes, re-fetch Copilot threads, then Step 7 summary comment.
   - On lint success: Continue immediately to Step 6 without asking the user for confirmation.
   - On lint failure or skipped required lint work: Record a workflow failure, skip Step 6 push and verification, then continue directly to the required terminal summary path in Step 7 because PR context exists.
   ```

   This runs all detected project linters and formatters, fixes issues, and commits the fixes without pushing.

1. If `lint-and-fix` reports `Lint status: success` or `Lint status: no-tools`, proceed to step 6. Any fix commits created by `lint-and-fix` will be included in the push.
1. If `lint-and-fix` reports unresolved lint issues, skipped required lint work, missing required tools, or tool execution failures, record a workflow-level failure. Do not claim lint success, do not push potentially non-compliant changes, skip step 6, and post the required partial or failed summary in step 7 because PR context exists.

### 6. Verify Completion

Do not run this step if step 5 recorded a lint failure or skipped required lint work. In that case, go directly to step 7 and report the lint failure in the final summary.

1. **Push any changes:** `git push`
1. Re-fetch to confirm all Copilot threads resolved:

   ```bash
   bash resolve-copilot-threads fetch OWNER REPO PR_NUMBER
   ```

   Expected output: `[]` (empty array)

   **Do not re-run `fetch-reviews` as a completion check.** Review bodies are immutable, so a review-body finding you just fixed still appears in the old body and always will. It will never go empty, and treating it as a verification signal produces a false Partial forever. Only the thread `fetch` is expected to reach `[]`.

1. Determine terminal workflow status and counts:
   - **No unresolved Copilot feedback**: the initial `fetch` returned `[]` **and** `fetch-reviews` surfaced no findings needing attention (every entry had `hasSuppressedMarker: false`, or every finding was `Previously handled`). Never use this status without having run `fetch-reviews`.
   - **Completed**: Every fetched thread and every review-body finding was handled according to its category, no failed or pending items remain, and any required code changes were pushed
   - **Partial**: At least one fetched thread or review-body finding was handled, but one or more items, replies, resolutions, tracking items, instruction updates, lint runs, pushes, or verification checks failed or remain pending
   - **Failed**: The workflow could not fetch or process feedback, or no required processing step succeeded
1. Track feedback metrics separately from workflow-level failures. Feedback metrics cover fetched, resolved, pending, failed, deferred, code-change, review-body, and previously handled items. Workflow-level failures cover non-thread steps such as instruction updates, follow-up tracking, lint runs, pushes, verification checks, and review-body format drift.
1. Proceed to step 7 before claiming completion

### 7. Post PR Summary Comment

**Required:** Once PR context exists, always post exactly one final PR summary comment after terminal workflow state. Do this for every outcome: no unresolved comments, fully resolved comments, only non-code-change resolutions, code-change resolutions, partial processing, failures, and pending items.

Post a summary comment to the PR so reviewers can see the workflow outcome at a glance. Do not post interim PR comments.

**Comment format:**

```markdown
## Copilot Feedback Summary

Status: Completed
Head SHA: `abc1234`

| Source      | File               | Category  | Outcome            | Action                                            |
| ----------- | ------------------ | --------- | ------------------ | ------------------------------------------------- |
| Thread      | `src/foo.ts:42`    | Valid     | Resolved           | Fixed null check                                  |
| Thread      | `lib/util.js:8`    | Incorrect | Resolved           | Updated error handling; added Copilot instruction |
| Thread      | `docs/api.md:5`    | Nitpick   | Resolved           | Auto-resolved                                     |
| Review body | `docs/plan.md:243` | Valid     | Fixed              | Corrected phase status                            |
| Review body | `src/ui.tsx:20`    | Deferred  | Tracked            | Follow-up issue filed                             |
| Review body | `src/ring.zig:196` | Valid     | Previously handled | Recorded in an earlier run                        |

Counts: 6 fetched, 3 resolved, 3 review-body findings, 1 deferred, 1 previously handled, 2 code-change threads.
```

- Status must be one of `Completed`, `No unresolved Copilot feedback`, `Partial`, or `Failed`
- **`Source`** is `Thread` or `Review body`. Review-body findings have no thread, so this column is what makes a thread-less row legible instead of implied.
- **`Outcome`** for `Thread` rows is `Resolved`, `Failed`, or `Pending`. `Resolved` means a thread was actually resolved, so it is never correct for a `Review body` row. Those use `Fixed`, `Tracked`, `Noted`, `Previously handled`, or `Failed`.
- The trailing `Counts:` line is one short sentence at the end of the comment. Include only non-zero counts from this set: fetched, resolved, pending, failed, deferred, code-change threads, review-body findings, previously handled, workflow failures. Omit zero-valued metrics; do not render an empty table or "0" entries. If every count is zero, omit the `Counts:` line entirely.
- Pluralize naturally (`1 fetched`, `2 fetched`; `1 code-change thread`, `2 code-change threads`; `1 review-body finding`, `2 review-body findings`; `1 workflow failure`, `2 workflow failures`).
- Table includes all processed threads and review-body findings when the comment remains safely postable, not only Valid and Incorrect items
- If the table would make the PR comment too large, replace detailed rows with aggregate category/outcome rows and state how many detail rows were omitted. Keep the full row-by-row table in the local final output for the agent/user audit trail. **Never aggregate away a `Review body` row's `path:line`**, since step 1c reads those back to avoid re-processing on the next run.
- Incorrect category notes Copilot instruction additions in the Action column
- Thread IDs omitted (meaningless to human reviewers)
- Non-thread failures, including review-body format drift, must be described in a failure details section, not forced into the feedback table

If neither the thread fetch nor the review-body fetch surfaced anything needing attention, use this no-op form:

```markdown
## Copilot Feedback Summary

Status: No unresolved Copilot feedback
Head SHA: `abc1234`

No unresolved Copilot threads and no review-body findings were found.
```

**Only use this form after running `fetch-reviews`.** An empty `fetch` alone does not justify it.

If processing was partial or failed, include failure details, the remaining required action, and the trailing counts line:

```markdown
## Copilot Feedback Summary

Status: Partial
Head SHA: `abc1234`

| Source      | File               | Category | Outcome  | Action                    |
| ----------- | ------------------ | -------- | -------- | ------------------------- |
| Thread      | `src/foo.ts:42`    | Valid    | Resolved | Fixed null check          |
| Thread      | `src/bar.ts:7`     | Outdated | Failed   | Reply failed              |
| Thread      | `lib/baz.ts:9`     | Nitpick  | Pending  | Resolution still required |
| Review body | `docs/plan.md:243` | Valid    | Fixed    | Corrected phase status    |

### Failure Details

| Scope    | Item       | Outcome | Remaining action    |
| -------- | ---------- | ------- | ------------------- |
| Workflow | `git push` | Failed  | Push branch changes |

### Remaining Required Action

- Resolve the failed reply for `src/bar.ts:7`
- Resolve the pending nitpick at `lib/baz.ts:9`
- Push branch changes

Counts: 4 fetched, 2 resolved, 1 pending, 1 failed, 1 review-body finding, 2 code-change threads, 1 workflow failure.
```

**No-op summary idempotency:** Before posting a `No unresolved Copilot feedback` summary, inspect existing top-level PR comments for a `## Copilot Feedback Summary` comment with the same head SHA and no-op status. If one already exists and this invocation did not recover a failed summary-post attempt, do not add another no-op comment. Report the existing summary comment URL locally and treat that existing same-head no-op summary as satisfying the final summary requirement for this no-op run. This idempotency exception applies only to runs where **both** the thread fetch and the review-body fetch came back with nothing needing attention; if this invocation processed threads or review-body findings, made code changes, or is recovering a failed summary-post attempt, post the required outcome summary.

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
1. **BOTH `fetch` and `fetch-reviews` were run** (a thread fetch alone cannot see review-body findings)
1. **EVERY addressed thread resolved via the script** (not just code fixed!)
1. **EVERY review-body finding handled and recorded** in the step 7 summary, since there is no thread to resolve and the summary row is the only record
1. **For INCORRECT feedback: Copilot instructions updated** (path-specific `*.instructions.md` preferred, or `copilot-instructions.md` for repo-wide conventions)
1. **For DEFERRED feedback: Task tracked** (GitHub issue, PROJECT.md, or similar)
1. **Linters and formatters pass** (via `lint-and-fix` skill, if any files were changed while addressing feedback)
1. Re-fetch confirms empty array `[]` for all processed **threads**. This does not apply to `fetch-reviews`, which never empties.
1. Output summary table (see format below)
1. **Final PR summary comment posted via step 7** after terminal workflow state, once PR context exists. For empty-fetch no-op runs only, an existing same-head no-op summary may satisfy this requirement without adding a duplicate comment.

If PR context or GitHub authentication is unavailable, or if `gh pr comment` fails, the workflow is incomplete. Report the failure locally and include the remaining action needed to post the required summary.

### Required Output: Feedback Summary Table

**You MUST output this table after processing all threads and review-body findings:**

```text
| Source      | Thread ID | File:Line | Category | Action Taken | Status |
|-------------|-----------|-----------|----------|--------------|--------|
| Thread      | PRRT_xxx  | src/foo.ts:42 | Nitpick | Auto-resolved | Resolved |
| Thread      | PRRT_yyy  | src/bar.ts:15 | Valid | Fixed null check | Resolved |
| Thread      | PRRT_zzz  | lib/util.js:8 | Outdated | Code refactored | Resolved |
| Review body | —         | src/ui.tsx:20 | Deferred | Tracked in PROJECT.md | Tracked |
| Review body | —         | docs/plan.md:243 | Valid | Corrected phase status | Fixed |
```

**Column definitions:**

- **Source**: `Thread` or `Review body`
- **Thread ID**: GraphQL thread ID (truncated for readability); `—` for review-body findings, which have none
- **File:Line**: Location of the comment
- **Category**: Nitpick, Valid, Outdated, Incorrect, or Deferred
- **Action Taken**: Brief description of resolution (10 words max)
- **Status**: `Resolved`, `Failed`, or `Pending` for threads; `Fixed`, `Tracked`, `Noted`, `Previously handled`, or `Failed` for review-body findings

**Common failure modes:**

- Fixing code but forgetting to resolve the threads. This leaves the PR with unresolved conversations even though the issues are fixed. ALWAYS run the resolution command after pushing code.
- Reporting `No unresolved Copilot feedback` on the strength of an empty `fetch` alone. Copilot regularly files findings in review bodies where a thread query cannot see them, and this reads as success while real feedback goes unread. ALWAYS run `fetch-reviews` too.

## Error Handling

- API failures: Retry with proper auth
- Thread ID issues: Use alternative queries
- Review-body format drift (`hasSuppressedMarker: true` with empty `findings`): read the raw `suppressed` text, process the findings from it, and record a workflow failure so the parser gets updated. Never report this as "no findings."
- Fix failures: Retry with alternative approach or defer if out of scope
- Summary comment failures: Log the error, preserve the intended summary Markdown in the local final output, and treat the workflow as incomplete until the required final summary posts successfully
- Partial resolution is better than none, but a partial or failed terminal state still requires the final PR summary once PR context exists
