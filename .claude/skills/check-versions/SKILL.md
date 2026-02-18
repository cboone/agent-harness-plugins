---
name: check-versions
description: >-
  Verify that plugin versions and marketplace.json are correct and consistent
  after changes on the current branch. Use when the user says "check versions",
  "verify versions", "are the versions correct", "review version bumps", or any
  similar variant. Also use after merging, rebasing, or before creating a PR.
---

# Check Versions

Verify that plugin versions and marketplace.json are correct and consistent after changes on the current branch.

## Workflow

### 1. Determine the Comparison Base

Detect the default branch:

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

Fall back to local detection if `gh` is unavailable:

```bash
git rev-parse --abbrev-ref origin/HEAD | sed 's@^origin/@@'
```

Find the merge base between the default branch and HEAD:

```bash
git merge-base <default-branch> HEAD
```

If HEAD equals the merge base (on the default branch or no divergent commits), compare against the state before the most recent merge instead — use the most recent merge commit's first parent as the comparison base:

```bash
git rev-parse "$(git log --merges -1 --format='%H' HEAD)^1"
```

### 2. Identify Changed Plugins

List files changed since the comparison base and group them by plugin directory:

```bash
git diff --name-only <base>..HEAD
```

A file belongs to plugin `foo` if its path starts with `plugins/foo/`. For each plugin, track:

- **Content changes**: files other than `.claude-plugin/plugin.json` that were modified, added, or deleted
- **Version file changed**: whether `.claude-plugin/plugin.json` itself was modified

Also detect new plugins (directories at HEAD that did not exist at the base) and removed plugins (directories at the base that no longer exist).

### 3. Check Plugin Version Bumps

For each plugin with content changes:

1. Read the current version from `plugins/<name>/.claude-plugin/plugin.json`
1. Read the base version: `git show <base>:plugins/<name>/.claude-plugin/plugin.json`
1. Compare:
   - New plugin (file absent at base) — version should be `1.0.0`
   - Content files changed but version unchanged — **flag as missing version bump**
   - Version changed — verify the bump direction is forward, not a regression

Assess bump level (informational):

- Wording-only or prompt changes → patch
- New files, new capabilities → minor
- Deleted or restructured skill/hook files → major

### 4. Check Marketplace Sync

Read `.claude-plugin/marketplace.json` and verify:

- **Version matching**: each marketplace entry's `version` matches its `plugin.json`
- **Coverage**: every `plugins/*/` directory has a marketplace entry, and every marketplace entry points to an existing plugin directory
- **Metadata version**: if plugins were added or removed, `metadata.version` minor should have been bumped; if only existing plugins changed, it should NOT have been bumped

### 5. Report

Output a structured report:

```text
## Version Check Report

### Summary
<one-line status: all clear, or N issues found>

### Plugin Changes
- **<name>**: <base version> → <current version>
  Changes: <what changed>
  Status: ✅ OK / ⚠️ Missing bump / ⚠️ Marketplace mismatch

### Marketplace Sync
- Plugin versions: ✅ All match / ⚠️ Mismatches listed
- Coverage: ✅ All registered / ⚠️ Missing or orphaned entries
- Metadata version: <base> → <current> — ✅ Correct / ⚠️ Issue described

### Recommended Actions
1. <specific fix needed>
```

If there are no issues, report a clean result summarizing what was checked.

### 6. Offer to Fix

If issues were found, ask the user whether to fix them:

- Missing version bumps → bump patch in `plugin.json` (user can adjust level)
- Marketplace mismatches → update `marketplace.json` to match `plugin.json`
- Metadata version → bump minor if plugins were added or removed
- Missing marketplace entries → note that a full entry is needed (the create-plugin skill can help)

Only make changes after the user confirms.
