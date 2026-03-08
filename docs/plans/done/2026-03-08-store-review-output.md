# Store Review Output to `docs/reviews/`

## Context

The `review-branch` skill generates detailed branch reviews but only outputs them to the terminal. The `address-review` skill expects to read review documents from `docs/reviews/`. There is no bridge between these two skills: users must manually copy terminal output into a file to use `address-review`. This change makes `review-branch` automatically save its output to `docs/reviews/` with a datestamp-prefixed filename, closing the gap.

## Changes

### 1. Add `--no-save` option to SKILL.md

**File:** `plugins/review-branch/skills/review-branch/SKILL.md` (line 23)

Add a fourth option to the Options section:

```markdown
- **--no-save**: Skip saving the review to `docs/reviews/` (default: save after outputting)
```

Saving is the default behavior. The opt-out flag covers cases where the user wants a quick terminal-only review.

### 2. Add step 7: Save the Review

**File:** `plugins/review-branch/skills/review-branch/SKILL.md` (insert after line 292, before the `## Error Handling` section)

Add a new workflow step with these substeps:

- **7a. Determine the filename**: Build from today's date (`date +%Y-%m-%d`) and the branch name from step 2. Sanitize the branch name for filenames: replace `/` and other unsafe characters with `-`, collapse consecutive hyphens, trim leading/trailing hyphens. Format: `YYYY-MM-DD-sanitized-branch-name.md`.
- **7b. Create the directory**: `mkdir -p docs/reviews`
- **7c. Write the file**: Use the Write tool to save the full review markdown (same content displayed in step 6) to `docs/reviews/<filename>`. If a file with the same name already exists, overwrite it (a re-review on the same day replaces the earlier one).
- **7d. Report the saved path**: Tell the user the file path and suggest using `address-review` to work through the items.

Skip this entire step if `--no-save` was specified.

### 3. Add save failure to Error Handling

**File:** `plugins/review-branch/skills/review-branch/SKILL.md` (Error Handling section)

Add a bullet: if the review file cannot be written, report the error but do not fail the review, since the terminal output is already complete.

### 4. Update README

**File:** `plugins/review-branch/README.md`

- Add `--no-save` to the options table
- Add `/review-branch --no-save` to the usage examples
- Add a sentence to "What It Does" noting that the review is saved to `docs/reviews/` for use with address-review
- Add address-review to "See Also"

### 5. Bump versions

- **`plugins/review-branch/.claude-plugin/plugin.json`**: `1.1.0` to `1.2.0` (minor: new capability)
- **`.claude-plugin/marketplace.json`** (line 304): `1.1.0` to `1.2.0` (must match plugin.json)
- Marketplace `metadata.version` stays at `1.21.0` (no plugin added or removed)

## Filename Examples

| Branch                  | Date       | Filename                              |
| ----------------------- | ---------- | ------------------------------------- |
| `feature/store-reviews` | 2026-03-08 | `2026-03-08-feature-store-reviews.md` |
| `fix/auth-bug`          | 2026-03-08 | `2026-03-08-fix-auth-bug.md`          |
| `user/feature/thing`    | 2026-03-08 | `2026-03-08-user-feature-thing.md`    |
| Detached HEAD           | 2026-03-08 | `2026-03-08-HEAD.md`                  |

## Edge Cases

- **File already exists**: Overwrite silently (re-review replaces earlier version)
- **Detached HEAD**: Use `HEAD` as the branch name
- **`--brief` mode**: Still saves the brief output
- **`docs/reviews/` missing**: Created via `mkdir -p`
- **Write fails**: Report error, do not fail the review

## Verification

1. Read the modified SKILL.md and confirm step 7 follows naturally from step 6
1. Confirm `--no-save` appears in both the Options section and step 7's skip condition
1. Confirm README documents the new option and behavior
1. Run `check-versions` to verify plugin.json and marketplace.json versions match
