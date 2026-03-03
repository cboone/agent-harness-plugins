# Add Pre-Tag Blocking Gate to Release Skill

## Context

The release skill currently has only one user confirmation point: approving the version bump at Step 4. After that, Steps 5-11 run automatically, including the irreversible commit (Step 10) and tag (Step 11). The doc checklist at Step 8 is explicitly advisory only.

Since release tags are typically immutable, the user wants the process to stop before tagging if it finds anything that might warrant attention (e.g., missing docs updates). It is better to get it right the first time than to make an immediate follow-up release.

## Approach

Merge the current Step 8 (advisory doc checklist) and Step 9 (change summary) into a single blocking "Pre-Tag Review" gate. This reduces the workflow from 11 steps to 10 while adding meaningful protection at the critical point before the irreversible commit and tag.

**Why one combined gate, not two separate blocking steps:**

- Two sequential prompts ("approve doc checklist" then "approve changes") would be chatty with no opportunity to act between them
- The doc checklist and file changes are complementary: together they form a complete "pre-tag briefing"
- Keeps the confirmation cadence clean: one gate at Step 4 (version decision), one gate at Step 8 (final review before irreversible action)

## Changes

### 1. Replace Steps 8-9 with a single Pre-Tag Review gate

**File:** `plugins/release/skills/release/SKILL.md`

Replace current Steps 8 (advisory doc checklist) and 9 (change summary) with a new Step 8 "Pre-Tag Review" that:

- **8a** Builds the doc checklist (same logic as before, same skip conditions)
- **8b** Presents a combined review showing:
  - All files modified during Steps 5-7
  - Documentation areas needing review (if applicable)
  - A "Tags are immutable" reminder
  - An explicit "Proceed with commit and tag?" prompt
- **8c** Waits for user confirmation before proceeding
  - If approved: continue to commit and tag
  - If declined: stop the release, inform the user their changes are in the working tree (unstaged), and explain their options (make changes then re-run, or discard with `git checkout .`)

Move the `--dry-run` exit point from old Step 9 into new Step 8b (show the full review, then stop without asking for confirmation).

### 2. Renumber Steps 10-11 to 9-10

**File:** `plugins/release/skills/release/SKILL.md`

- Old Step 10 (Create Release Commit) becomes Step 9
- Old Step 11 (Create Annotated Git Tag) becomes Step 10

Content unchanged, only heading numbers.

### 3. Update doc-checklist.md to remove advisory language

**File:** `plugins/release/skills/release/references/doc-checklist.md`

- Change the opening description from "advisory, not blocking" to reference the pre-tag review gate
- Change the presentation section's closing paragraph from "Do not block the release" to "The user must explicitly approve before the release commit and tag are created"

### 4. Bump plugin version to 1.1.0

This is a meaningful behavior change (previously non-blocking step becomes blocking), so it warrants a minor bump.

- `plugins/release/.claude-plugin/plugin.json`: `1.0.1` to `1.1.0`
- `.claude-plugin/marketplace.json` (line 262): `1.0.1` to `1.1.0`
- Marketplace metadata version: no bump (no plugins added or removed)

## Files to Modify

1. `plugins/release/skills/release/SKILL.md` (primary: restructure Steps 8-11 into Steps 8-10)
2. `plugins/release/skills/release/references/doc-checklist.md` (update advisory language)
3. `plugins/release/.claude-plugin/plugin.json` (version bump)
4. `.claude-plugin/marketplace.json` (mirror version bump)

## Verification

1. Read the final SKILL.md and verify:
   - Steps 1-7 are unchanged
   - New Step 8 includes doc checklist, change summary, and explicit confirmation gate
   - Steps 9-10 (commit and tag) only proceed after Step 8 approval
   - `--dry-run` exits cleanly at Step 8b without prompting
2. Read doc-checklist.md and verify no "advisory only" or "do not block" language remains
3. Run `check-versions` skill to verify plugin.json and marketplace.json versions match
