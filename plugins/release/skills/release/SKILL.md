---
name: release
description: >-
  Prepare a versioned release: detect project type, analyze conventional commits,
  recommend a version bump, update version references and CHANGELOG.md, create a
  release commit, and tag it locally. Use when the user says "release", "create a
  release", "cut a release", "prepare a release", "bump the version", "tag a
  release", "make a release", or any variant involving creating a new versioned
  release.
---

# Release

Prepare a versioned release: analyze commits, update versions and changelog, create a release commit, and tag locally.

## Options

The user may provide these options inline:

- **--major**: Force a major version bump regardless of commit analysis
- **--minor**: Force a minor version bump regardless of commit analysis
- **--patch**: Force a patch version bump regardless of commit analysis
- **--dry-run**: Preview all changes without modifying any files, committing, or tagging

## Workflow

### 1. Pre-Flight Checks

Run these commands in parallel to understand the current state:

```bash
# Check for uncommitted changes
git status --porcelain

# Get current branch name
git branch --show-current

# List existing version tags, sorted by version
git tag --list 'v*' --sort=-version:refname

# Get today's date
date +%Y-%m-%d
```

**Abort conditions:**

- If the working tree is dirty (uncommitted changes exist), tell the user to commit first (suggest `/commit`) and stop.
- If this is not a git repository, report the error and stop.

### 2. Detect Project Type

Use the detection rules in `./references/project-types.md` to determine the project type. Check in priority order:

1. Go CLI (`go.mod` + `cmd/` or `.goreleaser.yml`/`.goreleaser.yaml`)
1. Go library (`go.mod` without main-package indicators)
1. Generic (fallback)

Report the detected type to the user. If the detection is ambiguous (e.g., multiple indicators conflict), ask the user to confirm.

### 3. Find Last Release

Find the most recent semver tag:

```bash
git tag --list 'v*' --sort=-version:refname | head -1
```

Parse the tag as `v<MAJOR>.<MINOR>.<PATCH>`. If no tags exist, this is the first release; use `v0.0.0` as the base version for bump calculation.

### 4. Analyze Commits

Get all commits since the last release tag:

<!-- prettier-ignore -->
```bash
git log <LAST-TAG>..HEAD --format='%H %s' --no-merges
```

If this is the first release (no tags), get all commits:

```bash
git log --format='%H %s' --no-merges
```

**Abort condition:** If there are no commits since the last tag, report that there is nothing to release and stop.

Parse each commit using the rules in `./references/conventional-commits.md`:

1. Classify each commit by type and determine its bump level
1. Check for breaking changes (both `!` suffix and `BREAKING CHANGE:` footer)
1. Map commits to changelog categories
1. Determine the overall recommended bump (highest level wins)

Present a grouped summary to the user:

```text
Commits since vX.Y.Z (N total):

  Added (M):
    - feat: description (#PR)

  Fixed (N):
    - fix: description

  Changed (P):
    - refactor: description

Recommended bump: minor (vX.Y.Z -> vX.Y+1.0)
```

If `--major`, `--minor`, or `--patch` was specified, use that bump level instead of the recommendation.

**Confirm the version with the user.** This is the one required confirmation point. Present the recommended (or forced) version and wait for approval before proceeding.

### 5. Update Version in Project Files

Based on the project type detected in step 2, update version strings in the appropriate files using the rules in `./references/project-types.md`:

- **Go CLI:** Update the version constant in Go source files if one exists. If the version is injected via ldflags only, skip this step.
- **Go library:** Update the exported `Version` constant if one exists. Otherwise skip.
- **Generic:** Update the version in the detected ecosystem file(s) (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.).

If no version file is found, note this to the user and rely solely on the git tag.

### 6. Update CHANGELOG.md

Follow the format defined in `./references/changelog-format.md`:

1. If `CHANGELOG.md` does not exist, create it using the first-release template.
1. If it exists, read it and parse the current structure.
1. Move entries from `## [Unreleased]` into a new version section (`## [VERSION] - YYYY-MM-DD`).
1. If the Unreleased section is empty, generate entries from the commits analyzed in step 4.
1. Add the new version's comparison link at the bottom of the file.
1. Update the `[unreleased]` comparison link to start from the new version tag.
1. Leave `## [Unreleased]` in place (empty, ready for new changes).

Determine the remote URL for comparison links:

```bash
git remote get-url origin
```

Convert SSH URLs (`git@github.com:user/repo.git`) to HTTPS format (`https://github.com/user/repo`). If no remote is configured, omit comparison links and note this to the user.

### 7. Auto-Update Version References in Docs

Follow the rules in `./references/version-patterns.md`:

1. Skip this step entirely on the first release (no old version to replace).
1. Search documentation files for the old version string.
1. Propose all changes to the user before applying them.
1. Apply confirmed changes.

### 8. Smart Documentation Checklist

Follow the rules in `./references/doc-checklist.md`:

1. Map the commits in this release to documentation areas that may need review.
1. Skip the checklist if all commits are `chore:`, `test:`, `style:`, `ci:`, or `build:`.
1. Present the filtered checklist as informational items.
1. Do NOT block the release on checklist items. This is advisory only.

### 9. Review Changes

Show a summary of all files modified during steps 5-7:

```text
Files modified:
  - CHANGELOG.md (updated)
  - package.json (version bumped)
  - README.md (version references updated)
```

If `--dry-run` was specified, report what would have been done and stop here. Do not modify any files, commit, or create a tag.

### 10. Create Release Commit

Stage all modified files and create a GPG-signed commit:

```bash
git add <FILES>
git commit -S -m "$(cat <<'EOF'
release: vVERSION
EOF
)"
```

The commit message is `release: vVERSION` (e.g., `release: v1.2.0`).

CRITICAL: Never use `git commit --amend`. Always create a new commit. If a pre-commit hook fails, fix the issue, re-stage, and create a new commit.

### 11. Create Annotated Git Tag

Create a GPG-signed annotated tag:

```bash
git tag -s vVERSION -m "vVERSION"
```

Do NOT push the tag or the commit. After tagging, remind the user how to push when ready:

```text
Release v1.2.0 is ready locally.

To publish:
  git push origin HEAD
  git push origin v1.2.0
```

## Reference Navigation

- `./references/project-types.md`: project type detection rules and version file locations
- `./references/changelog-format.md`: Keep a Changelog template and formatting rules
- `./references/conventional-commits.md`: commit parsing and bump classification
- `./references/version-patterns.md`: patterns for finding and updating version strings in docs
- `./references/doc-checklist.md`: commit-type-to-documentation mapping for review

## Error Handling

- **Dirty working tree:** Abort and suggest `/commit` first.
- **No commits since last tag:** Abort with a message that there is nothing to release.
- **No conventional commits:** Fall back to patch bump, classify all commits as Changed.
- **Version file not found:** Skip source file updates, rely on git tag, inform the user.
- **CHANGELOG parse error:** If the existing file has an unrecognized format, warn the user and offer to create a new one or append a version section at the top.
- **Tag already exists:** Abort with a message that the tag `vVERSION` already exists. Suggest choosing a different version.
- **Not a git repository:** Abort immediately.
- **No remote configured:** Skip comparison links in CHANGELOG, skip doc version updates, warn the user.
- **First release:** Use `v0.0.0` as the base for bump calculation, create the CHANGELOG from scratch, skip doc version updates (no old version to replace).
