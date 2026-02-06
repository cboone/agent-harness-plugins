---
name: resolve-copilot-pr-feedback
description: >-
  Process and resolve GitHub Copilot automated PR review comments. Use when the
  user says "check copilot review", "handle copilot comments", "resolve copilot
  feedback", "address copilot suggestions", or mentions Copilot PR comments.
  Also use after PR creation when Copilot has left automated review comments.
---

# Copilot Feedback Resolver

Process and resolve GitHub Copilot's automated PR review comments systematically.

## PR Comments Prohibition (CRITICAL)

**NEVER leave comments directly on GitHub PRs.** This is strictly forbidden:

- `gh pr review --comment` - FORBIDDEN
- `gh pr comment` - FORBIDDEN
- Any GraphQL mutation that creates new reviews or PR-level comments - FORBIDDEN
- Responding to human review comments - FORBIDDEN

**This skill ONLY processes GitHub Copilot threads.** Never interact with threads created by human reviewers.

**Permitted operations:**

- Reply to EXISTING Copilot threads using `addPullRequestReviewThreadReply`
- Resolve Copilot threads using `resolveReviewThread`

## CRITICAL REQUIREMENTS

### YOU MUST RESOLVE THREADS AFTER ADDRESSING THEM

**After fixing any Copilot feedback, you MUST:**

1. **Push the code changes** (`git push`)
2. **Resolve EACH thread** using the GraphQL mutation (see below)
3. **Verify resolution** by re-querying the PR

**Addressing feedback without resolving the thread is INCOMPLETE WORK.**

The thread resolution is NOT optional - it's the primary deliverable of this skill. Code changes alone are insufficient.

### Thread Resolution Mutation (USE THIS!)

**IMPORTANT:** Use inline values, NOT `$variable` syntax. The `$` character causes shell escaping issues (`Expected VAR_SIGN, actual: UNKNOWN_CHAR`).

```bash
# Replace THREAD_ID with actual thread ID (e.g., PRRT_kwDONZ...)
gh api graphql -f query='
mutation {
  resolveReviewThread(input: {threadId: "THREAD_ID"}) {
    thread { isResolved }
  }
}'
```

**You MUST call this mutation for EVERY thread you address.**

### YOU MUST UPDATE COPILOT INSTRUCTIONS FOR INCORRECT FEEDBACK

**When Copilot feedback is categorized as INCORRECT (conflicts with project conventions/patterns), you MUST:**

1. **Update the project's Copilot instructions** to document the correct pattern
2. This prevents Copilot from flagging the same or similar things in future PRs
3. The update should be concise and explain why the pattern is intentional

**Failure to update Copilot instructions = INCOMPLETE WORK for Incorrect category feedback.**

#### Instructions File Strategy

Copilot supports two types of instruction files in the `.github/` directory:

- **`copilot-instructions.md`**: General instructions for the whole repository
- **`*.instructions.md`** (path-specific): Targeted instructions with `applyTo` frontmatter

**Prefer path-specific instructions files** when the incorrect feedback applies to a specific language or file pattern. Use `copilot-instructions.md` only for repo-wide conventions.

#### CRITICAL: Keep Instructions Concise

Copilot's PR review may not read the full instructions file. Long files risk having instructions truncated or ignored. To maximize effectiveness:

1. **Keep each instructions file under ~1,000 lines**
2. **Put the most important review rules first** in each file
3. **Start with 10-20 specific, actionable instructions** per file
4. **Split by concern**: use path-specific files instead of one large file
5. **Be specific**: clear, concrete instructions work better than vague directives

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

Query review threads using GraphQL.

**CRITICAL:** `reviewThreads(first: 100)` is paginated. You MUST fetch every page (`hasNextPage`) so no unresolved Copilot threads are missed.

**IMPORTANT:** Use inline values, NOT `$variable` syntax. The `$` character causes shell escaping issues.

```bash
# Replace OWNER, REPO, PR_NUMBER with actual values
gh api graphql -f query='
query {
  repository(owner: "OWNER", name: "REPO") {
    pullRequest(number: PR_NUMBER) {
      reviewThreads(first: 100) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          originalLine
          startLine
          originalStartLine
          comments(first: 20) {
            nodes {
              author { login }
              body
            }
          }
        }
      }
    }
  }
}'
```

For additional pages, run the same query with `after: "END_CURSOR_FROM_PREVIOUS_PAGE"`:

```bash
gh api graphql -f query='
query {
  repository(owner: "OWNER", name: "REPO") {
    pullRequest(number: PR_NUMBER) {
      reviewThreads(first: 100, after: "END_CURSOR_FROM_PREVIOUS_PAGE") {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          originalLine
          startLine
          originalStartLine
          comments(first: 20) {
            nodes {
              author { login }
              body
            }
          }
        }
      }
    }
  }
}'
```

**Filter for:** `isResolved: false` AND author is Copilot (github-actions bot or copilot signature).

**File:Line extraction rule:** Use `path` and the first non-null of `line`, `originalLine`, `startLine`, `originalStartLine`. If all line fields are null, report `path:(no-line)`.

### 2. Categorize Each Comment

For each unresolved Copilot comment:

| Category      | Indicator                            | Action                                                          |
| ------------- | ------------------------------------ | --------------------------------------------------------------- |
| **Nitpick**   | Contains `[nitpick]` prefix          | Auto-resolve immediately                                        |
| **Outdated**  | Refers to code that no longer exists | Reply with explanation, resolve                                 |
| **Incorrect** | Misunderstands project conventions   | Reply with explanation, resolve, update Copilot instructions    |
| **Valid**     | Current, actionable concern          | Delegate to coder agent to fix                                  |
| **Deferred**  | Valid but out of scope for this PR   | Track in PROJECT.md, reply, resolve                             |

### 3. Resolve Threads

Use GraphQL mutation to resolve.

**IMPORTANT:** Use inline values, NOT `$variable` syntax.

```bash
# Replace THREAD_ID with actual thread ID (e.g., PRRT_kwDONZ...)
gh api graphql -f query='
mutation {
  resolveReviewThread(input: {threadId: "THREAD_ID"}) {
    thread { isResolved }
  }
}'
```

### 4. Handle Each Category

#### Nitpicks (`[nitpick]` prefix)

- Resolve immediately without changes
- Optional brief acknowledgment reply

#### Outdated/Incorrect Copilot Comments

**CRITICAL: Reply directly to the Copilot review thread, NOT to the PR.**

Use GraphQL to add a reply to the specific Copilot thread.

**IMPORTANT:** Use inline values, NOT `$variable` syntax.

```bash
# Replace THREAD_ID and message with actual values
gh api graphql -f query='
mutation {
  addPullRequestReviewThreadReply(input: {
    pullRequestReviewThreadId: "PRRT_xxx",
    body: "Your explanation here"
  }) {
    comment { id }
  }
}'
```

**FORBIDDEN COMMANDS - NEVER USE:**

- `gh pr review <PR_NUMBER> --comment` - adds PR-level comments, not thread replies
- `gh pr comment` - adds PR-level comments
- Any interaction with human reviewer threads

1. Reply to the thread with professional explanation:
   - Outdated: "This comment refers to code refactored in commit abc123. The issue is no longer applicable."
   - Incorrect: "This conflicts with our {convention name} convention. {Brief explanation}. See {reference file} for project guidelines."
2. Resolve the thread using the mutation from section 3
3. **Update Copilot instructions** to prevent recurrence:
   - **Prefer a path-specific file** (e.g., `.github/css.instructions.md` with `applyTo: "**/*.css"`) when the feedback targets a specific language or file pattern
   - **Use `copilot-instructions.md`** only for repo-wide conventions
   - Example: `- Do not suggest removing .sr-only classes - required accessibility utilities`
   - **If symlink:** Follow it and edit target file

#### Valid Concerns

1. Delegate to coder agent with:
   - PR number and title
   - File and line number
   - Copilot comment text
   - Thread ID for resolution after fix
2. Ensure coder pushes changes and resolves thread

#### Deferred (Out of Scope)

**When feedback is valid but out of scope for the current PR:**

1. **Track the follow-up work** in the project's task tracking (e.g., GitHub issue, PROJECT.md, or similar)
2. **Reply to the thread** explaining the deferral:
   - "Valid suggestion. Tracked as follow-up task for a future PR."
3. **Resolve the thread**

**CRITICAL:** Never defer feedback without tracking it. "Acknowledged for follow-up" without creating a trackable task is INCOMPLETE WORK.

### 5. Verify Completion

1. **Push any changes:** `git push`
2. Re-query PR (with pagination) to confirm ALL Copilot threads resolved
3. Report summary of actions taken

## Reply Templates

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
2. **EVERY addressed thread resolved via GraphQL mutation** (not just code fixed!)
3. **For INCORRECT feedback: Copilot instructions updated** (path-specific `*.instructions.md` preferred, or `copilot-instructions.md` for repo-wide conventions)
4. **For DEFERRED feedback: Task tracked** (GitHub issue, PROJECT.md, or similar)
5. Re-query confirms `isResolved: true` for all processed threads
6. Output summary table (see format below)

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

**Common failure mode:** Fixing code but forgetting to resolve the threads. This leaves the PR with unresolved conversations even though the issues are fixed. ALWAYS run the resolution mutation after pushing code.

## Error Handling

- API failures: Retry with proper auth
- Thread ID issues: Use alternative queries
- Delegation failures: Attempt simple fixes directly
- Partial resolution is better than none
