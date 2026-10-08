---
name: resolve-copilot-pr-feedback
description: >-
  Process GitHub Copilot PR review comments: fix, reply to, and resolve each
  thread. Use for "resolve copilot feedback" or "handle copilot comments", or
  after opening a PR once Copilot has reviewed it.
---

# Copilot Feedback Resolver

Process and resolve GitHub Copilot's automated PR review comments systematically.

## PR Comments Prohibition (CRITICAL)

**NEVER leave comments directly on GitHub PRs.** This is strictly forbidden:

- `gh pr review --comment` - FORBIDDEN
- `gh pr comment` - FORBIDDEN (except the single required final workflow summary in step 7)
- Any GraphQL mutation that creates new reviews or PR-level comments - FORBIDDEN
- Responding to human review comments - FORBIDDEN

**This skill ONLY processes Copilot-authored feedback**, whether it arrives as a review thread or as a finding in a Copilot review body. Never interact with threads created by human reviewers.

**Permitted operations:**

- Fetch unresolved Copilot threads using the script's `fetch` command
- Fetch Copilot review bodies using the script's `fetch-reviews` command
- Audit every Copilot item on the PR using the script's read-only `audit` command
- Read existing PR comments (never write them) to check for prior summaries
- Reply to EXISTING Copilot threads using the script's `reply` command
- Resolve Copilot threads using the script's `resolve` command
- Reply and resolve in one step using the script's `reply-and-resolve` command

**Single exception:** Step 7 uses `gh pr comment` with `--body-file` to post one required final workflow summary after terminal workflow state once PR context exists. This is the ONLY permitted use of `gh pr comment` in this skill. The final summary is blocking: if it cannot be posted, the workflow is incomplete.

## Script Setup

All Copilot reads and thread writes use a dedicated script that handles pagination, variable binding, and Copilot author filtering automatically.

The script ships with this plugin. Invoke it via `bash` followed by the quoted path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" fetch OWNER REPO PR_NUMBER
```

Claude Code replaces the plugin-root placeholder with the installed plugin's absolute, version-correct directory before this file reaches you, so there is no search step and no need for a shell variable. Keeping `bash` as the command prefix keeps the command token stable across plugin versions, which is what permission allowlist rules match on.

**If the path was not substituted**, it still begins with `$` rather than `/`. Codex CLI substitutes the placeholder only in hook commands, and OpenCode does not substitute it at all. In that case locate the script with `**/resolve-copilot-pr-feedback/**/scripts/resolve-copilot-threads`, prefer a match inside the harness's own installed-plugin directory, ignore any match under a `.bak` or other backup directory, confirm it with `test -x`, and use that absolute path for the rest of the session.

The examples below abbreviate that path to just `resolve-copilot-threads` for readability. They are not literal commands: expand the abbreviation when you run one, so every invocation is `bash`, then the **double-quoted** absolute path, then the arguments shown.

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

Copilot supports two types of instruction files:

- **`.github/copilot-instructions.md`**: General instructions for the whole repository
- **`.github/instructions/**/*.instructions.md`** (path-specific): Targeted instructions with `applyTo` frontmatter

**Prefer path-specific instructions files** when the incorrect feedback applies to a specific language or file pattern. Use the repo-wide file only for conventions that apply broadly across the project.

#### CRITICAL: Make Sure Copilot Reads the File

An instructions file Copilot never loads does nothing, and nothing warns you. Location, not length, is the usual cause. Check all of these whenever you write or edit one:

1. **Location:** a path-specific file sits within or below `.github/instructions/` (subdirectories are allowed). A `*.instructions.md` directly under `.github/` is never read.
1. **Glob:** its `applyTo` matches the path of the file Copilot flagged. Separate multiple globs with commas.
1. **Agent:** `excludeAgent` is either absent or one of the supported strings `"code-review"` and `"cloud-agent"`. Reject any other value. For these review instructions, require the field to be absent or `"cloud-agent"`; `"code-review"` hides the file from PR review.

Copilot code review reads instructions from the pull request's head branch, so once pushed, the change governs the next review of the same PR. If the same finding recurs after that, re-check the three items above before adding more text.

#### CRITICAL: Keep Instructions Concise

GitHub advises limiting a single instructions file to about 1,000 lines, because response quality can decline past that and shorter files are more likely to be fully processed. To maximize effectiveness:

1. **Keep each instructions file under ~1,000 lines**
1. **Put the most important review rules first** in each file
1. **Start with 10-20 specific, actionable instructions** per file
1. **Split by concern**: use path-specific files instead of one large file
1. **Be specific**: clear, concrete instructions work better than vague directives

#### Path-Specific Instructions File Format

Place this file at `.github/instructions/<name>.instructions.md`:

```markdown
---
applyTo: "**/*.go"
---

- **Pattern X**: Intentional in this project, do not flag
- **Pattern Y**: Required for Z reason
```

Use the `applyTo` glob to target specific languages or paths. Use `excludeAgent` to limit which Copilot agent reads the file. It accepts `"code-review"` and `"cloud-agent"`; `excludeAgent: "cloud-agent"` targets only code review.

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

## Skill dependencies

- **Required:** `lint-and-fix`
- **Optional:** None

## Core Workflow

### 1. Fetch ALL Unresolved Copilot Feedback

Copilot leaves feedback in threads and in review bodies, and occasionally somewhere neither reaches. **You MUST run all three commands.** Fetching only threads is how real feedback gets missed.

```bash
bash resolve-copilot-threads fetch OWNER REPO PR_NUMBER
bash resolve-copilot-threads fetch-reviews OWNER REPO PR_NUMBER --head HEAD_SHA [--skip REVIEW_IDS]
bash resolve-copilot-threads audit OWNER REPO PR_NUMBER
```

The script automatically handles pagination and filters for Copilot-authored content. `HEAD_SHA` is the pull request's `headRefOid` (`gh pr view PR_NUMBER --repo OWNER/REPO --json headRefOid`). Step 1b says which `--skip` ids to pass, and step 1d covers what `audit` reports. A command that exits nonzero has not read anything: record a workflow-level failure quoting its stderr, never an empty result.

Record the `OWNER`, `REPO`, and `PR_NUMBER` values used for the fetch. A caller such as `monitor-pr` may also pass `REVIEW_ID`, the review it dispatched for: that review must be among the reviews step 1d reads and lists under `Reviews read`, and if `fetch-reviews` does not return it, record a workflow-level failure that names it. This establishes PR context for the required final workflow summary in step 7. If PR context or GitHub authentication cannot be established, report that the required final summary could not be posted and do not mark the workflow complete.

#### 1a. Threads (`fetch`)

**Output format** (JSON array):

```json
[
  {
    "id": "PRRT_kwDONZ...",
    "path": "src/foo.ts",
    "location": "src/foo.ts:42",
    "isOutdated": false,
    "comments": [{ "author": "copilot", "body": "[nitpick] Consider...", "databaseId": 4212881859, "url": "https://github.com/OWNER/REPO/pull/54#discussion_r4212881859" }]
  }
]
```

- **`location`**: Uses the first non-null of `line`, `originalLine`, `startLine`, `originalStartLine`. If all line fields are null, reports `path:(no-line)`.
- **`databaseId`**: the review comment id, the number in the comment's `#discussion_r` link. Step 1d uses it to match a review body's `threadLinks` to a thread.
- **Copilot detection**: Matches author logins `copilot-pull-request-reviewer`, `copilot-pull-request-reviewer[bot]`, `copilot`, and `github-copilot[bot]` in any case, plus `github-actions[bot]` when the comment body opens with a severity tag. Both `[bot]`-suffixed and unsuffixed forms are listed because GraphQL and REST report the same Copilot account differently, so one list serves every command. The `github-actions[bot]` rule is the exception: it applies to thread comments only, because the severity tag is a thread-comment convention.

An empty array `[]` means no unresolved Copilot threads remain.

**`[]` from `fetch` is a statement about threads only. It is never proof that Copilot left no feedback.** Two separate things can hide behind it:

- Copilot may have filed findings in a review body instead of a thread. That is what step 1b is for, and you must run it before concluding anything.
- A previous attempt may have already done the work. Before using the no-op summary form, check whether this invocation is recovering from a prior failed summary-post step. If a previous run resolved threads or made code changes but failed to post the required final summary, reuse the preserved summary body from that run or reconstruct it from the prior local output, resolved review threads, branch commits, and branch diff. Do not downgrade that recovery summary to the no-op form just because a later fetch returns `[]`.

#### 1b. Review bodies (`fetch-reviews`)

Copilot does not always open a thread. It also states findings in the review body itself: in its lead paragraph, in lists of open or previously missed findings, in file-summary tables, and in whatever shape it adopts next. Those findings are real and actionable, they have no thread id, and `fetch` cannot see them.

**The script does not parse review bodies, and neither should you look for a particular layout.** Copilot reshapes its review-body layout often. The text always says what Copilot found, so read it as a person would.

**Output format** (JSON array, oldest first, one entry per selected Copilot review):

```json
[
  {
    "id": 5035762218,
    "url": "https://github.com/OWNER/REPO/pull/54#pullrequestreview-5035762218",
    "submittedAt": "2026-08-21T18:02:11Z",
    "commitId": "abc1234def5678",
    "threadLinks": [4212881859, 4212881910],
    "body": "<!-- ccr-overview-v2 -->\n\n### 🟡 Changes recommended\n\n..."
  }
]
```

- **`body`**: the complete raw review body, exactly as Copilot wrote it, HTML included. An empty body states nothing; any findings that review has are threads.
- **`commitId`**: the commit the review ran against. Compare it with the pull request's `headRefOid` (`gh pr view PR_NUMBER --repo OWNER/REPO --json headRefOid`) to tell a review of the current head from one of an older push.
- **`threadLinks`**: the review comment ids the body links to through `#discussion_r` links. A hint for matching a concern to a thread from `fetch` by its `databaseId`, nothing more: an empty list never means the body names no threads.

**Choose which reviews to read by id**, using the summary comments step 1c reads. Selection never depends on timing, so a review that arrived while an earlier run was working, or after a run that failed, is still read.

1. **Settled ids**: from every prior summary whose status is `Completed` or `No unresolved Copilot feedback`, collect the review ids on its `Reviews read:` line. A `Partial` or `Failed` summary settles nothing, and a summary with no `Reviews read:` line settles nothing either.
1. Run `fetch-reviews` with `--skip` set to those ids, comma-separated, and `--head` set to the current head SHA. It returns every Copilot review no clearing run read, plus the newest review of the current head even if it was read before, so every run checks what Copilot currently says about the head.
1. With no settled ids, omit `--skip` and read every Copilot review on the PR.

Read every review it returns. A review whose body is not a string is left out and named on stderr (`Warning: skipping review ID: its body is not a string.`), and `audit` lists it as uncovered. Open it at its URL and read it by hand; if that is not possible, record a workflow-level failure that names it.

#### 1c. Check for findings handled in a previous run

Copilot re-emits the same review-body finding in **every** later review until the underlying code changes. Review bodies are immutable, so a finding you fixed last run will still be there this run. Without a check, the skill would re-report or re-fix it forever.

Before acting on any review-body finding, read the PR's existing summary comments. Only summaries posted by the authenticated account count, so a person quoting a summary cannot settle a review. Find that login first, then read the comments with it:

```bash
gh api user --jq .login
gh api --paginate repos/OWNER/REPO/issues/PR_NUMBER/comments --jq '.[] | select(.user.login == "LOGIN" and (.body | startswith("## Copilot Feedback Summary"))) | {created_at, body}'
```

Replace `LOGIN` with the login the first command printed. `--paginate` is required. Without it only the first page of comments is inspected, so on a PR with a long comment history the prior summaries fall out of view and every review-body finding looks new again, which is exactly the re-processing this step exists to prevent. These summaries also supply the settled ids for step 1b.

This reads comments; it never writes one, so it does not violate the PR Comments Prohibition.

**Carry forward unsettled rows.** Every row a prior summary left `Pending` or `Failed`, and every item under its `Remaining Required Action`, is work for this run whether or not the review it came from is read again. Process each one normally, and give it its own row in this run's summary.

Then, for each finding:

1. **Recorded before, and its disposition still holds.** A prior summary has a review-body row for the same finding: the same `path:line`, or for a line-less finding the same normalized path with a `Finding` excerpt that matches this finding's wording. That row usually links an earlier review, because Copilot repeats the finding in later reviews; the link records where the finding came from and is not part of its identity. Reading the current code confirms the recorded disposition still holds: for a `Fixed` row the fix is still in place, and for a `Noted` row (Incorrect, Outdated, or Nitpick) the code and evidence its rationale relied on are unchanged, so the same no-change decision applies. Record it as `Previously handled`, carry the prior disposition forward, and change nothing. A no-change finding never stops matching the code, so without this rule Copilot's repeats would be re-processed on every review.
1. **Recorded before, but no longer settled.** The earlier run deferred it, a fix regressed, or the code a no-change rationale relied on has changed since. Process it normally.
1. **Path matches, line does not.** Line numbers drift as files change. Treat it as a candidate and let the code check decide, rather than assuming it is new.
1. **Line-less path matches, excerpt does not.** No prior row for that path has an excerpt matching this finding. Treat it as a different finding. A review can carry several findings for one path, so the path alone is not an identity.
1. **No path at all.** A concern that names no file, wherever the body states it, has only its text and the label `(review body)`. A prior row labelled `(review body)`, or `(review overview)` as older summaries wrote it, whose `Finding` excerpt matches this concern is the same finding. Without one, it is new.
1. **No match.** Process it normally.

Always verify against the current code before deciding. Verification is what keeps this correct when someone edits or deletes a summary comment: the cost is a re-check, not a wrong answer.

#### 1d. Read each review and settle every concern

This step is the core of the review-body work. Do it for every review step 1b chose, and record each review's id for the summary's `Reviews read:` line, including a review that turns out to state no concern at all.

1. **Read the whole body before deciding anything.** Never stop at the first heading or paragraph: findings appear anywhere, including in table cells and collapsed `<details>` blocks.
1. **Decide whether it is a review or a notice.** A notice says Copilot did not review the head: for example, it hit an error, or every changed file was excluded. A notice has no findings, which is exactly what a clean review looks like, so never read one as clean. If the newest Copilot review against the current head is a notice, record a workflow-level failure whose failure row names it as a **Copilot notice** with its review `id` and quotes it. A body that is plainly neither a review nor a notice is also a workflow-level failure, quoted the same way. `monitor-pr` reads that row to take its notice path.
1. **List every concern the review states, wherever it states it.** Typical places are the lead paragraph, lists of open, new or previously missed findings, file-summary table cells (often with a severity and a vote count), suppressed or low-confidence sections, and any section Copilot introduces later. Skip text that states no finding, such as "no final comments" in a file summary, descriptions of what the change does, and calls to action. One sentence can hold several concerns: "A moderate cleanup-trap defect and two unresolved sandbox-path documentation gaps remain" is three.
1. **Settle each concern**, in the first of these that applies:
   1. **Matched**: it restates a thread from `fetch`, open or already resolved, or a `Previously handled` row from step 1c. A concern beside a `#discussion_r` link usually belongs to the thread whose comment `databaseId` matches; confirm by reading. Record it against that item; nothing new is processed.
   1. **New**: it names a defect nothing else records. Handle it as a review-body finding with the most specific location the text supports: `path:line` when the text gives a line, otherwise the normalized path, otherwise `(review body)`. Never invent a line. Strip zero-width spaces Copilot inserts into paths.
   1. **Advisory**: it names no defect and asks for human judgment, such as "Authentication and logout changes warrant final human review". See step 2.
   1. **No concern**: it states nothing to act on, such as a summary of what the change does or "All reviewed changes are covered by passing tests". Record it as `Noted` with that rationale.
1. **Read the `audit` result.** It reports `surfaces` (counts of Copilot reviews, review comments and PR comments) and `uncovered`. Each `uncovered` entry is Copilot feedback that neither `fetch` nor `fetch-reviews` reaches: a reply inside an unresolved thread a person opened, a review comment no thread holds, a comment on the PR itself, or a review whose body is not a string. Read it at its `url`, then categorize and handle it like a review-body finding. It has no Copilot thread to resolve. Never reply on a person's thread or on the PR: the PR Comments Prohibition still applies.

A vague concern, such as one naming a defect class without a location, still gets settled: search for it, and if nothing matches after a real search, record it as `Noted` with what was checked, so the next run does not repeat the search.

Nothing about a review's layout can fail the workflow. If a body is hard to read, read it more carefully, and open the review at its `url` if the raw text still leaves a concern unclear.

### 2. Categorize Each Comment

For each unresolved Copilot comment **and each review-body finding**:

| Category       | Indicator                                      | Action                                                       |
| -------------- | ---------------------------------------------- | ------------------------------------------------------------ |
| **Nitpick**    | Contains `[nitpick]` prefix                    | Auto-resolve immediately                                     |
| **Outdated**   | Refers to code that no longer exists           | Reply with explanation, resolve                              |
| **Incorrect**  | Misunderstands project conventions             | Reply with explanation, resolve, update Copilot instructions |
| **Valid**      | Current, actionable concern                    | Fix directly, push, and resolve thread                       |
| **Deferred**   | Valid but out of scope for this PR             | Track in PROJECT.md, reply, resolve                          |
| **Advisory**   | Asks for human review, names no defect         | Record it and surface it in the summary; never blocks        |
| **No concern** | Review-body text that states nothing to act on | Record it with the rationale; no code change                 |

The same categories apply to review-body findings, but the Action column does not: they have no thread to reply to or resolve. See [Review-Body Findings](#review-body-findings-no-thread) for what to do instead. Note also that review-body findings carry **no `[nitpick]` prefix**, so judge Nitpick from the prose rather than looking for a tag.

Advisory arises from a review body, usually its lead paragraph, not from a thread. It needs no code change and never holds the workflow short of `Completed`, but it must reach a person: list each one under the summary's `Requests for human review` heading in step 7, quoted with its review link.

A review-body concern that step 1d settled as **Matched** takes the category of the thread or prior row it restates. A concern matched to a thread is `Noted`; one matched to a prior summary row is `Previously handled`. Either way its disposition names what it restates.

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
# Step 1: Generate a unique tmpfile path (-u so the file is NOT created):
mktemp -u "${TMPDIR:-/tmp}/copilot-reply-XXXXXX"
# Returns a unique path that does NOT exist on disk, e.g.: /tmp/claude-501/copilot-reply-r7s8t9

# Step 2: Write the response body to TMPFILE using the Write tool (not shown here as bash)

# Step 3: Pass TMPFILE to the script -- a SEPARATE call, issued after step 2 returns:
bash resolve-copilot-threads reply THREAD_ID --body-file TMPFILE

# Or reply and resolve in one step:
bash resolve-copilot-threads reply-and-resolve THREAD_ID --body-file TMPFILE
```

```bash
# Step 4: Clean up -- issue this as a SEPARATE Bash tool call, not chained onto step 3:
rm -f TMPFILE
```

Replace `TMPFILE` with the actual path returned by `mktemp -u`. The `-u` flag is required: plain `mktemp` creates an empty file at the path it prints, and the Write tool refuses to overwrite a file it has not Read first, so step 2 would fail with `File has not been read yet`.

**Never batch step 2 and step 3 into one message.** The reply script reads the body file at invocation time, so a parallel batch can run step 3 before the file exists and post an empty reply. This is a deliberate exception to the general preference for parallel tool calls: these two steps are dependent, because step 3 consumes the file step 2 produces.

The cleanup must be a separate Bash tool call: each tool invocation runs unconditionally, so the tmpfile is removed whether step 3 succeeded or failed, and the harness preserves step 3's exit code without any shell wrapping. Never combine the two with `; status=$?; rm -f TMPFILE; exit $status` -- in zsh (the macOS default shell), `status` is a read-only built-in alias for `$?`, so the assignment fails with `read-only variable: status`. See the `use-git` skill's tmpfile pattern reference for the full rationale.

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
   - **Prefer a path-specific file** (e.g., `.github/instructions/css.instructions.md` with `applyTo: "**/*.css"`) when the feedback targets a specific language or file pattern
   - **Use `.github/copilot-instructions.md`** only for repo-wide conventions
   - Example: `- Do not suggest removing .sr-only classes - required accessibility utilities`
   - **If symlink:** Follow it and edit target file
   - **Confirm Copilot will read it** against [Make Sure Copilot Reads the File](#critical-make-sure-copilot-reads-the-file)

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

Findings from `fetch-reviews` have **no thread id**. Do not attempt `reply`, `resolve`, or `reply-and-resolve` for them; there is nothing to address those commands to, and the calls will fail. GitHub supports replies to line-level review comments, not to the immutable review body itself. Do not invent a thread or post an interim PR comment: the PR Comments Prohibition still applies, and the single step 7 summary is the reporting channel for these findings.

Apply the same categories, minus the thread operations:

| Category       | What to do                                                                    | Outcome recorded |
| -------------- | ----------------------------------------------------------------------------- | ---------------- |
| **Valid**      | Read the flagged line, fix the issue, commit (do not push; step 5 runs first) | `Fixed`          |
| **Incorrect**  | Update the Copilot instructions file so it stops recurring                    | `Noted`          |
| **Deferred**   | Track the follow-up work in a GitHub issue, PROJECT.md, or similar            | `Tracked`        |
| **Outdated**   | Confirm against current code, then record it; no code change                  | `Noted`          |
| **Nitpick**    | Record it; no code change                                                     | `Noted`          |
| **Advisory**   | Quote it under `Requests for human review` in step 7; no code change          | `Noted`          |
| **No concern** | Record it with the rationale; no code change                                  | `Noted`          |

Every review-body finding gets a row in the step 7 summary and in the local audit table, whatever its category. Link its source to the exact review URL. A fixed finding names the fixing commit; an Incorrect, Outdated, or Nitpick disposition states the evidence or rationale for making no code change. Since Copilot will keep re-emitting the finding and there is no thread to resolve, that linked row **is** the record that it was handled, and step 1c reads it back on the next run.

### 5. Lint and Fix

**After all code changes are made (from Valid or Incorrect categories), run the `lint-and-fix` skill to catch lint errors before pushing.**

This step prevents CI failures from lint issues introduced while resolving feedback.

1. **Check for changes**: If no files were modified during steps 2-4 (only nitpicks auto-resolved or threads replied to), skip this step. Run `git status --porcelain` to verify: empty output means a clean working tree and you may skip; any output means files were changed and you should continue.
1. **Invoke the `lint-and-fix` skill** with `--no-push`:

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
   - **No unresolved Copilot feedback**: the initial `fetch` returned `[]`, `fetch-reviews` and `audit` both exited successfully, `fetch-reviews` with `--head` returned a Copilot review whose `commitId` is the current `headRefOid` and which step 1d read as a review rather than a notice, every review it returned was read and is listed under `Reviews read`, those reviews stated no concern other than `Previously handled` ones and no-concern text, no review was skipped with a warning, no prior row was carried forward as unsettled, and `audit` reported nothing `uncovered`. Never use this status without having run `fetch-reviews` and `audit` and read the reviews they returned. An empty `fetch-reviews` is not "nothing to process": if Copilot has not reviewed the current head, record a workflow-level failure that says so instead.
   - **Completed**: Every fetched thread, review-body concern, carried-forward row and uncovered item was handled according to its category, `fetch-reviews` and `audit` both exited successfully, every review `fetch-reviews` returned and every review it skipped with a warning was read and is listed under `Reviews read`, a caller's `REVIEW_ID`, if given, is among them, no failed or pending items remain, and any required code changes were pushed. Advisory items do not prevent this status. A failed `audit` is a workflow-level failure, because the items it would have reported went unread.
   - **Partial**: At least one item was handled, but one or more items, replies, resolutions, tracking items, instruction updates, lint runs, pushes, or verification checks failed or remain pending, or a workflow-level failure was recorded
   - **Failed**: The workflow could not fetch or process feedback, or no required processing step succeeded. This includes a run whose only Copilot review for the current head is a notice: nothing was reviewed.
1. Track feedback metrics separately from workflow-level failures. Feedback metrics cover fetched, resolved, pending, failed, deferred, code-change, review-body, uncovered, advisory and previously handled items. Workflow-level failures cover non-thread steps such as instruction updates, follow-up tracking, lint runs, pushes, verification checks, and a Copilot notice or unreadable body in place of a review.
1. Proceed to step 7 before claiming completion

### 7. Post PR Summary Comment

**Required:** Once PR context exists, always post exactly one final PR summary comment after terminal workflow state. Do this for every outcome: no unresolved comments, fully resolved comments, only non-code-change resolutions, code-change resolutions, partial processing, failures, and pending items.

Post a summary comment to the PR so reviewers can see the workflow outcome at a glance. Do not post interim PR comments.

**Comment format:**

```markdown
## Copilot Feedback Summary

Status: Completed
Head SHA: `abc1234`

| Source                                                                                       | Finding                                               | Category  | Outcome            | Disposition                                                 |
| -------------------------------------------------------------------------------------------- | ----------------------------------------------------- | --------- | ------------------ | ----------------------------------------------------------- |
| Thread                                                                                       | `src/foo.ts:42`                                       | Valid     | Resolved           | Fixed null check                                            |
| Thread                                                                                       | `lib/util.js:8`                                       | Incorrect | Resolved           | Updated error handling; added Copilot instruction           |
| Thread                                                                                       | `docs/api.md:5`                                       | Nitpick   | Resolved           | Auto-resolved                                               |
| [Review body 5035762218](https://github.com/OWNER/REPO/pull/54#pullrequestreview-5035762218) | `docs/plan.md:243`                                    | Valid     | Fixed              | Corrected phase status in commit `abc1234`                   |
| [Review body 5035762219](https://github.com/OWNER/REPO/pull/54#pullrequestreview-5035762219) | `src/ui.tsx` - avoid redundant state synchronization | Nitpick   | Noted              | Existing state flow is required by the upstream component   |
| [Review body 5035762220](https://github.com/OWNER/REPO/pull/54#pullrequestreview-5035762220) | `src/ring.zig:196`                                    | Valid     | Previously handled | Fixed in commit `def5678`; current code retains the boundary |

Review concerns: 2 matched, 2 handled as new, 1 no concern.
Reviews read: 5035762218, 5035762219, 5035762220.

Counts: 6 fetched, 3 resolved, 3 review-body findings, 1 previously handled, 2 code-change threads.
```

When any item is Advisory, add this section between `Head SHA` and the table, one bullet per request, quoted verbatim:

```markdown
### Requests for human review

- "Authentication and logout changes warrant final human review." ([Review body 5035762221](https://github.com/OWNER/REPO/pull/54#pullrequestreview-5035762221))
```

Whenever step 1d read a review, add two lines directly under the table. The first counts each concern it listed once by how it was settled, omitting zero counts. The second lists the id of every review step 1d read, including one that stated no concern and one read by hand after a skip warning, so step 1b of the next run can skip it:

```markdown
Review concerns: 3 matched, 1 handled as new, 1 advisory, 2 no concern.
Reviews read: 5035762218, 5035762219.
```

The `Reviews read:` line is required in every summary for which `fetch-reviews` ran, whatever the status, the no-op form included. Never list a review that was not read in full.
`matched` covers a concern restating a thread or a `Previously handled` row. That line is what makes it measurable, across a PR's summaries, how much of a review body only restates feedback the threads already carry.

- Status must be one of `Completed`, `No unresolved Copilot feedback`, `Partial`, or `Failed`
- **`Source`** is `Thread`, a `Review body REVIEW_ID` link using the exact `url` returned by `fetch-reviews`, or for an `audit` item an `Uncovered review comment ID` or `Uncovered PR comment ID` link using its `url`. Those items have no Copilot thread, so the link visibly connects the disposition to its source.
- **`Finding`** is `path:line` when a line exists. For a finding with no line, use the normalized path plus a concise excerpt copied verbatim from the review body, so step 1c can find it in a repeated finding; a path alone is ambiguous when one table row carries several findings. For a finding with no path, use `(review body)` plus the excerpt; give each concern its own row with its own excerpt. Choose an excerpt that contains no `|` character: a pipe would end the table cell, and escaping it as `\|` would stop the cell text from appearing verbatim in the body. Any distinctive run of words from the body works, so pick one that sits between pipes.
- **`Outcome`** for `Thread` rows is `Resolved`, `Failed`, or `Pending`. `Resolved` means a thread was actually resolved, so it is never correct for any other row. Those use `Fixed`, `Tracked`, `Noted`, `Previously handled`, or `Failed`. A review-body concern matched to a thread is `Noted`, and one matched to a prior summary row is `Previously handled`; either way its disposition names what it restates.
- **`Disposition`** names the fixing commit for `Fixed` and fixed `Previously handled` rows. For `Incorrect`, `Outdated`, `Nitpick`, `Advisory` and no-concern rows, state the evidence or rationale for making no code change. Do not leave a category-only disposition that forces readers to reconstruct the decision.
- The trailing `Counts:` line is one short sentence at the end of the comment. Include only non-zero counts from this set: fetched, resolved, pending, failed, deferred, code-change threads, review-body findings, uncovered items, advisory requests, previously handled, workflow failures. Omit zero-valued metrics; do not render an empty table or "0" entries. If every count is zero, omit the `Counts:` line entirely.
- Pluralize naturally (`1 fetched`, `2 fetched`; `1 code-change thread`, `2 code-change threads`; `1 review-body finding`, `2 review-body findings`; `1 workflow failure`, `2 workflow failures`).
- Table includes all processed threads and review-body findings when the comment remains safely postable, not only Valid and Incorrect items
- If the table would make the PR comment too large, replace thread details with aggregate category/outcome rows first and state how many detail rows were omitted. Keep the full row-by-row table in the local final output for the agent/user audit trail. **Never aggregate away a review-body source link or finding identity**, since step 1c reads those back to avoid re-processing on the next run.
- Incorrect category notes Copilot instruction additions in the Disposition column
- Thread IDs omitted (meaningless to human reviewers)
- Non-thread failures, including a Copilot notice or an unreadable body in place of a review, must be described in a failure details section, not forced into the feedback table. A notice row says `Copilot notice`, links the review and names its `id`, so `monitor-pr` can find it.

If neither the fetches nor the audit surfaced anything needing attention, use this no-op form:

```markdown
## Copilot Feedback Summary

Status: No unresolved Copilot feedback
Head SHA: `abc1234`

No unresolved Copilot threads, no review-body findings, and no Copilot feedback outside their reach were found.

Reviews read: 5035762230.
```

**Only use this form after running `fetch-reviews` and `audit`.** An empty `fetch` alone does not justify it.

If processing was partial or failed, include failure details, the remaining required action, and the trailing counts line:

```markdown
## Copilot Feedback Summary

Status: Partial
Head SHA: `abc1234`

| Source                                                                                       | Finding            | Category | Outcome  | Disposition                                |
| -------------------------------------------------------------------------------------------- | ------------------ | -------- | -------- | ------------------------------------------ |
| Thread                                                                                       | `src/foo.ts:42`    | Valid    | Resolved | Fixed null check                           |
| Thread                                                                                       | `src/bar.ts:7`     | Outdated | Failed   | Reply failed                               |
| Thread                                                                                       | `lib/baz.ts:9`     | Nitpick  | Pending  | Resolution still required                  |
| [Review body 5035762218](https://github.com/OWNER/REPO/pull/54#pullrequestreview-5035762218) | `docs/plan.md:243` | Valid    | Fixed    | Corrected phase status in commit `abc1234` |

Review concerns: 1 matched, 1 handled as new.
Reviews read: 5035762218.

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

**No-op summary idempotency:** Before posting a `No unresolved Copilot feedback` summary, inspect existing top-level PR comments for a `## Copilot Feedback Summary` comment with the same head SHA and no-op status. If one already exists and this invocation did not recover a failed summary-post attempt, do not add another no-op comment. Report the existing summary comment URL locally and treat that existing same-head no-op summary as satisfying the final summary requirement for this no-op run. This idempotency exception applies only to runs where the thread fetch, the review-body fetch and the audit all came back with nothing needing attention; if this invocation processed threads or review-body findings, made code changes, or is recovering a failed summary-post attempt, post the required outcome summary.

**Mechanics:**

```bash
# Step 1: Generate a unique tmpfile path (-u so the file is NOT created):
mktemp -u "${TMPDIR:-/tmp}/copilot-summary-XXXXXX"
# Returns a unique path that does NOT exist on disk, e.g.: /tmp/claude-501/copilot-summary-k2m9p4

# Step 2: Write comment body to TMPFILE using the Write tool (not shown here as bash)

# Step 3: Post the comment -- a SEPARATE call, issued after step 2 returns:
gh pr comment PR_NUMBER --repo OWNER/REPO --body-file TMPFILE
```

```bash
# Step 4: Clean up -- issue this as a SEPARATE Bash tool call, not chained onto step 3:
rm -f TMPFILE
```

Replace `OWNER`, `REPO`, `PR_NUMBER`, and `TMPFILE` with actual values recorded during fetch. Always pass `--repo OWNER/REPO` so the final summary targets the intended PR even if the current checkout or working directory changes. The cleanup must be a separate Bash tool call (see [Outdated/Incorrect Copilot Comments](#outdatedincorrect-copilot-comments) above for the rationale): chaining with `; status=$?; rm -f TMPFILE; exit $status` breaks under zsh because `status` is a read-only built-in alias for `$?`.

If the comment fails, log the error and do not claim completion. Thread resolution, code changes, and the required final PR summary are all workflow deliverables.

When the final summary comment fails, preserve the exact intended summary Markdown in the local final output. A later retry must use that preserved body, or reconstruct the same outcome from available PR and git evidence, before falling back to any no-op summary.

## Reply Templates

First, generate a unique tmpfile path with `mktemp -u "${TMPDIR:-/tmp}/copilot-reply-XXXXXX"` (the `-u` keeps `mktemp` from creating the file, which would block the Write tool). Write these to the returned path using the Write tool, then, in a **separate message**, pass the path via `--body-file`. Never batch the Write and the reply command together: the command reads the file at invocation time, so a parallel batch can post an empty reply. Clean up the tmpfile (`rm -f TMPFILE`) after each reply operation as a **separate Bash tool call**, not chained onto the reply command.

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
1. **`fetch`, `fetch-reviews` and `audit` were all run** (a thread fetch alone cannot see review-body findings, and neither fetch sees a Copilot comment outside a Copilot thread)
1. **EVERY addressed thread resolved via the script** (not just code fixed!)
1. **EVERY review step 1b chose read in full, and every concern it states and every uncovered item handled and recorded** in the step 7 summary, since there is no thread to resolve and the summary row is the only record
1. **EVERY review read listed under `Reviews read`**, so the next run's step 1b can skip it, and every row a prior summary left `Pending` or `Failed` carried forward
1. **EVERY Advisory request quoted** under `Requests for human review`
1. **For INCORRECT feedback: Copilot instructions updated** (path-specific `.github/instructions/**/*.instructions.md` preferred, or `.github/copilot-instructions.md` for repo-wide conventions)
1. **For DEFERRED feedback: Task tracked** (GitHub issue, PROJECT.md, or similar)
1. **Linters and formatters pass** (via `lint-and-fix` skill, if any files were changed while addressing feedback)
1. Re-fetch confirms empty array `[]` for all processed **threads**. This does not apply to `fetch-reviews`, which never empties.
1. Output summary table (see format below)
1. **Final PR summary comment posted via step 7** after terminal workflow state, once PR context exists. For empty-fetch no-op runs only, an existing same-head no-op summary may satisfy this requirement without adding a duplicate comment.

If PR context or GitHub authentication is unavailable, or if `gh pr comment` fails, the workflow is incomplete. Report the failure locally and include the remaining action needed to post the required summary.

### Required Output: Feedback Summary Table

**You MUST output this table after processing all threads and review-body findings:**

```markdown
| Source                                                                                       | Thread ID | Finding                                               | Category  | Action taken                   | Status   |
| -------------------------------------------------------------------------------------------- | --------- | ----------------------------------------------------- | --------- | ------------------------------ | -------- |
| Thread                                                                                       | PRRT_xxx  | `src/foo.ts:42`                                       | Nitpick   | Auto-resolved                  | Resolved |
| Thread                                                                                       | PRRT_yyy  | `src/bar.ts:15`                                       | Valid     | Fixed null check               | Resolved |
| Thread                                                                                       | PRRT_zzz  | `lib/util.js:8`                                       | Outdated  | Code refactored                | Resolved |
| [Review body 5035762218](https://github.com/OWNER/REPO/pull/54#pullrequestreview-5035762218) | --        | `docs/plan.md:243`                                    | Valid     | Fixed in commit `abc1234`      | Fixed    |
| [Review body 5035762219](https://github.com/OWNER/REPO/pull/54#pullrequestreview-5035762219) | --        | `src/ui.tsx` - avoid redundant state synchronization | Nitpick   | Existing flow is intentional   | Noted    |
```

**Column definitions:**

- **Source**: `Thread` or an exact originating review link
- **Thread ID**: GraphQL thread ID (truncated for readability); `--` for review-body findings, which have none
- **Finding**: `path:line`, or normalized path plus identifying text when the finding has no line
- **Category**: Nitpick, Valid, Outdated, Incorrect, Deferred, Advisory, or No concern (review-body text that states nothing to act on)
- **Action taken**: Brief description of resolution (10 words max)
- **Status**: `Resolved`, `Failed`, or `Pending` for threads; `Fixed`, `Tracked`, `Noted`, `Previously handled`, or `Failed` for review-body findings

**Common failure modes:**

- Fixing code but forgetting to resolve the threads. This leaves the PR with unresolved conversations even though the issues are fixed. ALWAYS run the resolution command after pushing code.
- Reporting `No unresolved Copilot feedback` on the strength of an empty `fetch` alone. Copilot regularly files findings in review bodies where a thread query cannot see them, and this reads as success while real feedback goes unread. ALWAYS run `fetch-reviews` and `audit` too.
- Reading a Copilot notice as a clean review. It has no verdict and no findings because no review happened. Read the body and decide in step 1d.
- Skimming a review body. Reading the verdict and lead and skipping the tables and collapsed blocks misses findings Copilot states only there.
- Treating one sentence as one item. A sentence often names several concerns, and each needs settling in step 1d.

## Error Handling

- API failures: Retry with proper auth
- Thread ID issues: Use alternative queries
- A Copilot notice in place of a review: record a workflow failure that names it as a Copilot notice with its review `id` and quotes it. Do not request a new review from this skill; `monitor-pr` owns review requests.
- A skipped review on stderr (`Warning: skipping review ID: its body is not a string.`): the other reviews still came through. Open that review at its URL and read it by hand, then list it under `Reviews read`; if it cannot be read, record a workflow failure that names it.
- Fix failures: Retry with alternative approach or defer if out of scope
- Summary comment failures: Log the error, preserve the intended summary Markdown in the local final output, and treat the workflow as incomplete until the required final summary posts successfully
- Partial resolution is better than none, but a partial or failed terminal state still requires the final PR summary once PR context exists
