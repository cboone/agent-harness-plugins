# Tag-Scoped Concurrency for Release Workflows

## Context

Issue #176: When the `optimize-runner-usage` command adds concurrency groups to tag-triggered (Release) workflows, it uses the standard pattern `${{ github.workflow }}-${{ github.ref }}`. Since each tag push produces a unique `github.ref` (e.g., `refs/tags/v1.0.0`), the concurrency group never prevents parallel runs. Two tags pushed in quick succession run simultaneously, wasting runner minutes and risking race conditions in artifact publication.

The fix: Release workflows should use a workflow-scoped concurrency group that serializes all runs regardless of which tag triggered them.

## Changes

### 1. Update the concurrency section in the command file

**File**: `plugins/optimize-runner-usage/commands/optimize-runner-usage.md`

In the **Concurrency** subsection (lines 95-115), make these changes:

**a)** Add a second concurrency group pattern for Release workflows, after the existing standard pattern:

```yaml
# Standard pattern (CI, Scheduled, Broad push, Mixed, Secret scanning, Reusable):
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # or false, per classification table

# Tag-scoped pattern (Release only):
concurrency:
  group: ${{ github.repository }}-${{ github.workflow }}
  cancel-in-progress: false
```

Explain why: each tag push has a unique `github.ref`, so including it in the group never deduplicates. The tag-scoped pattern serializes all runs of the same release workflow.

**b)** Update the `cancel-in-progress` table to note that Release workflows use the tag-scoped pattern. The value remains `false` (unchanged).

**c)** Update the "existing concurrency group" check (lines 113-115): the command should recognize both patterns as "standard" depending on classification. For Release workflows, the expected standard is `${{ github.repository }}-${{ github.workflow }}`. For all others, it remains `${{ github.workflow }}-${{ github.ref }}`. If an existing group matches the expected standard for that classification, check only `cancel-in-progress`. If it matches neither, flag for manual review.

### 2. Update the edge cases section

**File**: `plugins/optimize-runner-usage/commands/optimize-runner-usage.md`

Add an edge case entry for Release workflows:

- **Tag-triggered workflows (Release)**: Use workflow-scoped concurrency (`${{ github.repository }}-${{ github.workflow }}`) instead of the ref-scoped pattern, because each tag produces a unique `github.ref` that never deduplicates. Always use `cancel-in-progress: false`.

### 3. Bump the plugin version

**Files**:
- `plugins/optimize-runner-usage/.claude-plugin/plugin.json` (line 12): `1.0.0` -> `1.1.0`
- `.claude-plugin/marketplace.json`: update the `optimize-runner-usage` entry version to `1.1.0`

This is a minor bump: new capability (tag-scoped concurrency detection), no breaking changes.

## Verification

1. Read the modified command file and confirm:
   - Release workflows get `group: ${{ github.repository }}-${{ github.workflow }}` with `cancel-in-progress: false`
   - All other classifications still get `group: ${{ github.workflow }}-${{ github.ref }}` with their existing `cancel-in-progress` values
   - The existing concurrency group check recognizes both patterns as standard (per classification)
2. Run the `check-versions` skill to verify version consistency between `plugin.json` and `marketplace.json`
