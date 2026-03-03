# Add PR summary comment to resolve-copilot-pr-feedback skill

## Context

When the resolve-copilot-pr-feedback skill resolves Copilot review threads and makes code changes, reviewers and the PR author have no visibility into what was done unless they read each individual thread. This plan adds a summary comment to the PR thread after resolving feedback, so everyone can see what changed and why.

Additionally, issue #173 (mktemp .md suffix on macOS) is already fixed on main. This PR will close it via a `Closes #173` reference.

## Files to modify

1. `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md` (core changes)
1. `plugins/resolve-copilot-pr-feedback/.claude-plugin/plugin.json` (version bump)
1. `.claude-plugin/marketplace.json` (matching version bump)
1. `plugins/resolve-copilot-pr-feedback/README.md` (description and permissions update)

## Changes

### 1. SKILL.md: Update the PR Comments Prohibition section

Update the `gh pr comment` line (line 18) to note the step 7 exception:

```markdown
- `gh pr comment` - FORBIDDEN (except the single summary comment in step 7)
```

After the "Permitted operations" list (after line 30), add:

```markdown
**Single exception:** Step 7 uses `gh pr comment` with `--body-file` to post a one-time summary of code changes made while resolving feedback. This is the ONLY permitted use of `gh pr comment` in this skill.
```

### 2. SKILL.md: Add Step 7 (Post PR Summary Comment)

After the current step 6 (Verify Completion), add a new step 7.

**Condition:** Only post if at least one thread was categorized as Valid or Incorrect and resulted in code changes. If all threads were Nitpick, Outdated, or Deferred, skip this step.

**Comment format:**

```markdown
## Copilot Feedback Resolved

Addressed N Copilot review comment(s) with code changes:

| File            | Category  | Action                                            |
| --------------- | --------- | ------------------------------------------------- |
| `src/foo.ts:42` | Valid     | Fixed null check                                  |
| `lib/util.js:8` | Incorrect | Updated error handling; added Copilot instruction |

M additional comment(s) resolved without code changes (nitpicks, outdated).
```

- Table includes only threads that resulted in code changes (Valid and Incorrect)
- Count line for non-code-change threads shown only if any exist
- Incorrect category notes Copilot instruction additions in the Action column
- Thread IDs omitted (meaningless to human reviewers)

**Mechanics:**

1. `mktemp /tmp/copilot-summary-XXXXXX` (no .md suffix, macOS compatible)
1. Write comment body to tmpfile using the Write tool
1. `gh pr comment PR_NUMBER --body-file TMPFILE`
1. `rm -f TMPFILE`
1. If the comment fails, log the error but do not fail the workflow (best-effort)

### 3. SKILL.md: Update Success Criteria

Add item 8:

```markdown
8. **If code changes were made**: PR summary comment posted via step 7
```

### 4. SKILL.md: Update Error Handling

Add:

```markdown
- Summary comment failures: Log the error but treat as non-fatal. Thread resolution and code changes are the primary deliverables.
```

### 5. plugin.json: Version bump

`plugins/resolve-copilot-pr-feedback/.claude-plugin/plugin.json`: bump `1.2.1` to `1.3.0` (new capability = minor).

### 6. marketplace.json: Matching version bump

`.claude-plugin/marketplace.json`: bump resolve-copilot-pr-feedback entry from `1.2.1` to `1.3.0`.

### 7. README.md: Update description and permissions

Update "What It Does" paragraph (line 20) to mention the summary comment feature.

Update the permissions JSON (line 35) to add the new patterns:

```json
"Bash(gh pr comment *)",
"Bash(mktemp /tmp/copilot-summary-*)",
"Bash(rm -f /tmp/copilot-summary-*)"
```

## Verification

1. Read the modified SKILL.md and verify the step 7 section is coherent with the existing workflow
1. Run `check-versions` skill to verify version consistency
1. Run `lint-and-fix` on the changed Markdown files
1. Verify the prohibition section clearly limits `gh pr comment` to only step 7
