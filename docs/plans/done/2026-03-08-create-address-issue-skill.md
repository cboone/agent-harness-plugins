# Create Address Issue Skill

## Context

The user often says "Address issue #42" or similar phrases. Currently no skill handles this. The existing `create-worktree-from-issue` skill creates a new worktree for an issue, but there is no skill for addressing an issue directly in the current branch. This skill fills that gap by combining issue fetching (from `create-worktree-from-issue`) with systematic work execution (from `address-review`).

## Files to Create

### 1. `plugins/address-issue/.claude-plugin/plugin.json`

Standard plugin metadata. Version `1.0.0`, category `productivity`, keywords `["gh", "github", "issues", "workflow"]` (matching `create-issue`).

### 2. `plugins/address-issue/skills/address-issue/SKILL.md`

Core skill definition with YAML frontmatter. Trigger phrases cover: "address issue", "address issue #42", "address #42", "fix issue #42", "work on issue #42", "handle issue #42", "resolve issue #42", "tackle issue #42", "implement issue #42".

Workflow steps:

1. **Find the Issue** - By number (`gh issue view NUMBER --json ...`) or fuzzy text search (`gh issue list --search ...`). Reuses the exact patterns from `create-worktree-from-issue`.
2. **Check Issue State** - Warn on closed issues, ask to proceed.
3. **Mark Issue In Progress** - Self-assign (`gh issue edit NUMBER --add-assignee @me`) and add "in progress" label (create label if needed with `gh label create "in progress" ... 2>/dev/null || true`, then `gh issue edit NUMBER --add-label "in progress"`). Best-effort: warn on failure but continue. Skip for closed issues. Reuses the exact pattern from `create-worktree-from-issue`.
4. **Display Issue Context** - Show number, title, labels, assignees, body (truncated at ~2000 chars).
5. **Analyze the Issue** - Classify as bug fix, feature, documentation, refactor, or chore. Extract sub-tasks from unchecked task list items.
6. **Plan the Work** - Explore codebase, identify affected files, present plan for user confirmation.
7. **Execute the Changes** - Work through each change, announcing progress.
8. **Commit the Changes** - Conventional commits with issue references (e.g., `fix: resolve crash (#42)`). Commit type derived from issue classification.
9. **Mark Issue Done** - Remove "in progress" label (`gh issue edit NUMBER --remove-label "in progress"`). Best-effort: warn on failure but continue. Skip if step 3 was skipped or failed.
10. **Report Completion** - Summary table of changes made/skipped.
11. **Offer Next Steps** - Suggest `/pr`, note remaining items.

Options: `--dry-run`, `--no-commit`, `--commit-per-change`.

### 3. `plugins/address-issue/README.md`

User-facing docs following the `address-review` README pattern. Includes installation, what it does, usage examples, options table, recommended permissions (`gh issue view *`, `gh issue list *`, `gh issue edit *`, `gh label create *`), examples, and see-also links.

## Files to Modify

### 4. `plugins/create-worktree-from-issue/skills/create-worktree-from-issue/SKILL.md`

Remove "work on issue" from the description/trigger phrases. Keep the other triggers: "start issue", "create worktree from issue", "create worktree for issue", and references to starting work on a GitHub issue by number or description.

Bump `create-worktree-from-issue` version to `1.2.5` in both `plugin.json` and `marketplace.json` (patch bump for trigger phrase adjustment).

### 5. `.claude-plugin/marketplace.json`

- Add new `address-issue` entry (alphabetically after `add-scrut-cli-tests`, before `address-review`)
- Update `create-worktree-from-issue` version from `1.2.4` to `1.2.5`
- Bump `metadata.version` from `1.22.0` to `1.23.0` (minor bump for adding a plugin)

### 6. Root `README.md`

**Table of contents**: Add `[Address Issue](#address-issue)` as the first entry in "Issues and Worktrees" (alphabetically before "Create Issue"), shifting existing entries to use `∙` continuation prefix.

**Skill detail section**: Add `#### Address Issue` section under `### Issues and Worktrees`, before `#### Create Issue`.

## Key Design Decisions

- **Mark in progress / done lifecycle**: Like `create-worktree-from-issue`, self-assigns and adds "in progress" label at the start, then removes "in progress" at the end. Uses the same idempotent label-creation pattern. Best-effort: failures warn but do not block the workflow.
- **Task list extraction**: Issue bodies with GitHub checkboxes get each unchecked item treated as a sub-task, similar to how `address-review` extracts items from review documents.
- **Commit references**: All commits include `(#NUMBER)` for GitHub auto-linking.
- **"work on issue" moved here**: The trigger phrase "work on issue" is taken from `create-worktree-from-issue` and used by this skill instead, since addressing an issue in the current branch is the more common intent. `create-worktree-from-issue` keeps its other trigger phrases ("start issue", "create worktree from issue", "create worktree for issue").

## Verification

1. Check that `plugin.json` version matches the `marketplace.json` entry version
2. Verify marketplace.json is valid JSON
3. Confirm the README ToC entries are alphabetically ordered and follow the one-link-per-line format
4. Run `/check-versions` to verify version correctness
5. Test the skill by saying "address issue #42" in a repository with GitHub issues
