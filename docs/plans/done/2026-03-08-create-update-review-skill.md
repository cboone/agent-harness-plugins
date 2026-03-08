# Create update-review Skill

## Context

The review ecosystem has three skills: `review-branch` creates initial reviews and saves them to `docs/reviews/`, `address-review` works through feedback items. The missing piece is a skill that refreshes an existing review after more work has been done on the branch. Without this, users must re-run a full `/review-branch` and lose the continuity of what was previously assessed versus what is new.

The `update-review` skill finds the latest saved review for the current branch, identifies commits made since that review, and produces a unified updated document that synthesizes the original assessment with the new work.

## Prerequisite: Add "Reviewed through" metadata to review-branch

The review-branch output template currently has no way to record which commit was HEAD at review time. The update-review skill needs this anchor to determine which commits are new. Add a `Reviewed through: <short-hash>` metadata line to the output template in Step 6 of review-branch's SKILL.md.

### Files to modify

- `plugins/review-branch/skills/review-branch/SKILL.md` (lines 261-267): Add `Reviewed through: <short-hash>` after the `Files changed:` line in the output template. Also add a `git rev-parse --short HEAD` command in Step 2 (Gather Changes) to capture the value.
- `plugins/review-branch/.claude-plugin/plugin.json`: Bump version from `1.2.0` to `1.2.1` (patch: additive metadata, no behavior change).
- `.claude-plugin/marketplace.json`: Update the review-branch version entry from `1.2.0` to `1.2.1`.

## New plugin: update-review

### Directory structure

```text
plugins/update-review/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── update-review/
        └── SKILL.md
```

### plugin.json

```json
{
  "author": { "name": "Christopher Boone" },
  "description": "Find the latest branch review, assess commits made since, and update the review document with a synthesized reassessment.",
  "homepage": "https://github.com/cboone/cboone-cc-plugins",
  "keywords": ["branch", "code-review", "diff", "git", "review", "update"],
  "license": "MIT",
  "name": "update-review",
  "repository": "https://github.com/cboone/cboone-cc-plugins",
  "skills": "./skills",
  "version": "1.0.0"
}
```

### SKILL.md workflow

**Frontmatter triggers:** "update review", "update the review", "refresh the review", "re-review", "update branch review", "what's changed since the review"

**Options:**

- `--review <path>`: Path to a specific review document (overrides auto-detection)
- `--plan <path>`: Plan document for compliance evaluation
- `--brief`: High-level summary only

**Workflow steps:**

1. **Find the review document**
   - Get current branch name, sanitize it (same rules as review-branch Step 7a)
   - Search `docs/reviews/` for files matching `*-<sanitized-branch>.md`
   - If multiple matches (different dates), use the most recent (highest date prefix)
   - If none found, report no review exists and suggest `/review-branch`

1. **Parse the existing review**
   - Read the file and extract metadata: `Base:`, `Commits:`, `Reviewed through:`, `Files changed:`
   - Extract all section content for context
   - **Legacy fallback:** If no `Reviewed through:` line exists, infer the last reviewed commit using the commit count and merge base: `git log --oneline --reverse <merge-base>..HEAD | sed -n '<count>p'`. Warn about the legacy format.

1. **Gather new changes**
   - Verify the "Reviewed through" hash still exists on the branch:

     ```bash
     git rev-parse --verify <hash>
     git merge-base --is-ancestor <hash> HEAD
     ```

   - If HEAD equals the "Reviewed through" hash, report the review is already current and stop
   - Gather delta: `git log/diff <reviewed-through>..HEAD`
   - Also gather full picture: `git log/diff <merge-base>..HEAD`

1. **Assess the delta**
   - Analyze new commits specifically: what areas changed, what's new, what feedback was addressed
   - Re-evaluate plan compliance from scratch (merge base to HEAD) if a plan is available
   - Evaluate code quality across the full diff, highlighting changes since last review

1. **Synthesize the updated review**
   - Produce a single unified document in the same format as review-branch output
   - Add `Updated: <today> (previous: <original-date>)` metadata line
   - Add a `### Changes Since Last Review` section at the end with a concise delta summary
   - In the Code Quality Assessment, note: issues from prior review that were addressed, new issues, overall trajectory

1. **Write the updated review**
   - Overwrite the existing file at its original path (preserve the original date prefix)
   - Report: previous review covered N commits through `<old-hash>`, updated covers M commits through `<new-hash>` (K new commits)
   - Include address-review hint

**Error handling:**

- No review found: suggest `/review-branch`
- "Reviewed through" hash not found on branch (rebase/force-push): suggest fresh `/review-branch`
- No new commits: report review is current, stop
- Legacy format (no "Reviewed through" line): fall back to commit count inference, warn, upgrade the format
- Save failure: report error, terminal output already complete

## Registration and documentation

### marketplace.json

- Add new `update-review` entry in alphabetical order (after `update-everything`, before `use-git`)
- Category: `"productivity"` (matching review-branch and address-review)
- Bump `metadata.version` from `1.21.0` to `1.22.0` (minor: new plugin added)

### CLAUDE.md

- Add `update-review/` directory tree entry in alphabetical order (after `update-everything/`, before `use-git/`)

### README.md

- Add to ToC under "Code Review" subcategory: `∙ [Update Review](#update-review)` (after Resolve Copilot PR Feedback, alphabetically)
- Add description section under Code Review (after Resolve Copilot PR Feedback):
  - Brief description, trigger `/update-review`, link to plugin README

### Plugin README.md

- Standard format: what it does, installation, usage examples, options table, see-also links to review-branch and address-review

## Implementation order

1. Modify review-branch SKILL.md: add `Reviewed through: <short-hash>` to output template and Step 2
1. Bump review-branch version to 1.2.1 in plugin.json and marketplace.json
1. Create `plugins/update-review/` directory structure
1. Write SKILL.md with full workflow
1. Write plugin.json and README.md
1. Register in marketplace.json (new entry + metadata version bump)
1. Update CLAUDE.md directory tree
1. Update root README.md (ToC + description section)
1. Lint and fix
1. Commit in logical groups

## Verification

1. Confirm all JSON files are valid: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"`
1. Confirm version consistency: review-branch is 1.2.1 in both plugin.json and marketplace.json; update-review is 1.0.0 in both
1. Confirm marketplace metadata.version is 1.22.0
1. Confirm CLAUDE.md tree is alphabetically correct
1. Confirm README.md ToC links resolve to correct heading anchors
1. Run `/check-versions` skill to validate
1. Run linters via `/lint-and-fix`
