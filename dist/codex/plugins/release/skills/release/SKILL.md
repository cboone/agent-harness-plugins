---
name: release
description: >-
  Prepare a versioned release or Claude Code marketplace catalog state tag:
  update release files, create a release commit, tag locally, and optionally
  publish a GitHub Release.
---

# Release

Prepare a versioned release or Claude Code marketplace catalog state tag: analyze commits, update release files, create a release commit, tag locally, and optionally publish a GitHub Release.

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

# List existing Claude Code marketplace catalog state tags
git tag --list 'catalog-M*-m*-p*-n*' --sort=-creatordate

# Get today's date
date +%Y-%m-%d

# Check for a release workflow triggered by release tags
if [ -d .github/workflows ]; then
  for f in .github/workflows/*.yml .github/workflows/*.yaml; do
    [ -f "$f" ] || continue
    if grep -q 'tags:' "$f" && grep -qE "^[[:space:]]*-[[:space:]]+['\"]?(v[*[0-9]|catalog-)" "$f"; then
      echo "$f"
    fi
  done
fi
```

If the loop prints any files, note that a **release workflow likely exists** that will automatically create a GitHub Release when a release tag is pushed. The detection looks for workflow files that contain both a `tags:` trigger and a YAML list entry whose value starts with `v` followed by `*`, `[`, or a digit (e.g., `- "v*"`, `- 'v*'`, `- "v[0-9]*.[0-9]*.[0-9]*"`, `- "v[0-9]+.[0-9]+.[0-9]+"`, or unquoted `- v*`), or starts with `catalog-` for Claude Code marketplace releases. Anchoring to list-item form avoids false positives from action refs like `actions/checkout@v4`. It is best-effort and may miss inline list forms (e.g., `tags: ['v*']`) or other exotic patterns. If the detection seems wrong, ask the user to confirm. This flag affects step 11.

**Abort conditions:**

- If the working tree is dirty (uncommitted changes exist), tell the user to commit first (suggest `/commit`) and stop.
- If this is not a git repository, report the error and stop.

### 2. Detect Project Type

Use the detection rules in `./references/project-types.md` to determine the project type. Check in priority order:

1. Claude Code marketplace (`.claude-plugin/marketplace.json` exists and has a top-level `plugins` array)
1. Go CLI (`go.mod` + `cmd/` or `.goreleaser.yml`/`.goreleaser.yaml`)
1. Go library (`go.mod` without main-package indicators)
1. Generic (fallback)

Report the detected type to the user. If the detection is ambiguous (e.g., multiple indicators conflict), ask the user to confirm.

If the project is a Claude Code marketplace, use the marketplace release flow below instead of the SemVer flow in steps 3-11.

### Claude Code Marketplace Release Flow

Claude Code marketplace repos use SemVer for individual plugin `version` fields, but the marketplace `metadata.version` is a catalog state tag, not SemVer.

The catalog state tag format is:

```text
catalog-M<major-sum>-m<minor-sum>-p<patch-sum>-n<plugin-count>
```

Compute it from `.claude-plugin/marketplace.json` `.plugins[].version` exactly:

- `M`: sum of all plugin major versions.
- `m`: sum of all plugin minor versions.
- `p`: sum of all plugin patch versions.
- `n`: number of marketplace plugins.
- Do not normalize or carry between components.

#### M1. Find Last Marketplace Release

Find the most recent marketplace catalog tag:

```bash
git tag --list 'catalog-M*-m*-p*-n*' --sort=-creatordate | head -1
```

If no catalog tags exist, this is the first marketplace release.

#### M2. Analyze Commits and Plugin Versions

Analyze commits since the last catalog tag, or all commits if no catalog tag exists:

<!-- prettier-ignore -->
```bash
git log <LAST-CATALOG-TAG>..HEAD --format='%H %s' --no-merges
```

For the first marketplace release:

```bash
git log --format='%H %s' --no-merges
```

Use the conventional commit analysis from step 4 to summarize changes. Identify which plugin directories changed and ensure each changed plugin gets an appropriate SemVer bump in both `plugins/<name>/.claude-plugin/plugin.json` and the matching marketplace entry. If those plugin version bumps are already present, preserve them.

**Abort condition:** If there are no commits since the last catalog tag, report that there is nothing to release and stop.

Confirm the individual plugin version changes with the user before modifying files. If `--dry-run` was specified, do not modify files; report the plugin version changes that would be made, the catalog state that would result, and stop after the dry-run pre-tag review in M5.

#### M3. Compute Catalog State

After plugin versions are final, compute the catalog state from marketplace plugin versions. Use strict `MAJOR.MINOR.PATCH` parsing (matching `bin/validate-plugins`) so malformed versions fail loudly instead of silently producing an incorrect tag:

```bash
jq -r '
  def parse_version:
    capture("^(?<major>[0-9]+)\\.(?<minor>[0-9]+)\\.(?<patch>[0-9]+)$")
    | {
        major: (.major | tonumber),
        minor: (.minor | tonumber),
        patch: (.patch | tonumber)
      };

  [.plugins[].version | parse_version] as $versions
  | "catalog-M\($versions | map(.major) | add)-m\($versions | map(.minor) | add)-p\($versions | map(.patch) | add)-n\($versions | length)"
' .claude-plugin/marketplace.json
```

Update `.claude-plugin/marketplace.json` `metadata.version` to exactly the computed catalog state.

#### M4. Abort if Tag Exists

Before any commit or tag operation, check whether the exact catalog state tag already exists:

```bash
git rev-parse -q --verify "refs/tags/CATALOG-STATE"
```

If the tag already exists, abort with a message that the tag `CATALOG-STATE` already exists. Do not create another tag or choose a different state tag unless the user explicitly changes plugin versions.

#### M5. Pre-Tag Review

Build a final review and wait for explicit user approval:

```text
Pre-tag review for CATALOG-STATE:

Files modified:
  - .claude-plugin/marketplace.json (metadata.version updated, plugin versions mirrored)
  - plugins/<name>/.claude-plugin/plugin.json (plugin version bumped)

Catalog state:
  - Tag: CATALOG-STATE
  - GitHub Release title: Marketplace CATALOG-STATE

Tags are immutable. Proceed with commit and tag?
```

If `--dry-run` was specified, present this as a proposed review and stop. Do not stage changes, commit, tag, push, or create a GitHub Release.

#### M6. Create Marketplace Release Commit

Stage only the files changed by the release and create a GPG-signed commit:

```bash
git add <FILES>
git commit -S -m "$(cat <<'EOF'
release: CATALOG-STATE
EOF
)"
```

CRITICAL: Never use `git commit --amend`. Always create a new commit. If a pre-commit hook fails, fix the issue, re-stage, and create a new commit.

#### M7. Create Marketplace Tag

Create a GPG-signed annotated tag using the exact catalog state:

```bash
git tag -s CATALOG-STATE -m "CATALOG-STATE"
```

Do not prefix the tag with `v`. Do not create floating tags. Create only the exact catalog state tag.

After tagging, confirm:

```text
Marketplace release CATALOG-STATE tagged locally.
```

#### M8. Publish Marketplace Release

Ask the user if they want to push the commit and tag.

If no release workflow was detected in step 1:

```text
Push and create a GitHub Release for CATALOG-STATE?
```

If a release workflow was detected in step 1:

```text
Push commit and tag for CATALOG-STATE?
(Release workflow detected; it will create the GitHub Release automatically.)
```

If the user declines and no release workflow was detected, show:

```text
Marketplace release CATALOG-STATE is ready locally.

To publish manually:
  git push origin HEAD
  git push origin CATALOG-STATE
  gh release create CATALOG-STATE --title "Marketplace CATALOG-STATE" --notes-file <release-notes-file> --verify-tag
```

If the user declines and a release workflow was detected, show:

```text
Marketplace release CATALOG-STATE is ready locally.

To publish manually:
  git push origin HEAD
  git push origin CATALOG-STATE

The release workflow will create the GitHub Release automatically when the tag is pushed.
```

If the user accepts, push the commit and tag:

First, check for a remote:

```bash
git remote get-url origin
```

If no remote is configured, report the error and tell the user to configure a Git remote before rerunning this step. Do not show any `git push origin ...` commands in this case. Stop.

```bash
git push origin HEAD
git push origin CATALOG-STATE
```

If the push is rejected, report the error and stop. Never force push. Show the remaining manual commands so the user can complete the process after resolving the push issue.

If a release workflow was detected, skip manual GitHub Release creation and report:

```text
Tagged CATALOG-STATE and pushed to origin.

  Tag: CATALOG-STATE
  GitHub Release: the release workflow is expected to create it automatically.
```

If no release workflow was detected, create release notes from the commit summary or changed plugin list. First, check that `gh` is available:

```bash
command -v gh
```

If `gh` is not available, skip GitHub Release creation. Report that `gh` is required for GitHub Releases and show the manual `gh release create` command. Do not create a tmpfile.

If `gh` is available, write the notes to a tmpfile and create the GitHub Release:

```bash
gh release create CATALOG-STATE --title "Marketplace CATALOG-STATE" --notes-file TMPFILE --verify-tag
```

Always remove the tmpfile after the command completes, regardless of success or failure. Issue the cleanup (`rm -f TMPFILE`) as a **separate Bash tool call**, not chained onto `gh release create`. The harness preserves the prior call's exit code, and a chained `; status=$?; rm -f ...; exit $status` wrapper breaks under zsh because `status` is a read-only built-in alias for `$?`. See `plugins/use-git/skills/use-git/references/tmpfile-pattern.md` for the full rationale.

Report:

```text
Marketplace release CATALOG-STATE published.

  Tag: CATALOG-STATE
  GitHub Release: <URL returned by gh release create>
```

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

**Confirm the version with the user.** Present the recommended (or forced) version and wait for approval before proceeding.

**Dry-run gate:** If `--dry-run` was specified, skip steps 5-7 and 11 entirely. Do not create or modify any files. Instead, describe what changes _would_ be made (which files would be updated, what the CHANGELOG entry would look like). Then proceed directly to step 8b.

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

### 8. Pre-Tag Review

This is the final gate before the irreversible commit and tag. Build a combined review and wait for explicit user approval.

#### 8a. Documentation checklist

Follow the rules in `./references/doc-checklist.md`:

1. Map the commits in this release to documentation areas that may need review.
1. Skip the checklist if all commits are `chore:`, `test:`, `style:`, `ci:`, or `build:`.

#### 8b. Combined review

Present a single review block:

```text
Pre-tag review for vVERSION:

Files modified:
  - CHANGELOG.md (updated)
  - package.json (version bumped)
  - README.md (version references updated)

Documentation areas to review:
  - [ ] README features section (new feat: commits detected)
  - [ ] Migration guide (breaking changes detected)

Tags are immutable. Proceed with commit and tag?
```

Omit the "Documentation areas to review" section if the checklist was skipped (all housekeeping commits).

If `--dry-run` was specified (steps 5-7 were skipped), present the review block as a proposed plan and stop here. Do not prompt for confirmation, stage changes, commit, or create a tag.

#### 8c. Wait for confirmation

Ask the user to confirm before proceeding. If the user declines:

1. Stop the release.
1. Inform the user that their changes are in the working tree (unstaged).
1. Explain their options: make changes and re-run the release skill, or discard all changes:
   - To discard modifications to tracked files: `git checkout .`
   - To also remove newly created untracked files (e.g., a new `CHANGELOG.md`): review with `git clean -n`, then remove with `git clean -f`

### 9. Create Release Commit

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

### 10. Create Annotated Git Tag

Create a GPG-signed annotated tag:

```bash
git tag -s vVERSION -m "vVERSION"
```

Do NOT create floating major version tags (e.g., `v2`). Create only the exact version tag shown above.

After tagging, confirm:

```text
Release vVERSION tagged locally.
```

### 11. Publish

Ask the user if they want to push the commit and tag.

If **no release workflow** was detected in step 1:

```text
Push and create a GitHub Release for vVERSION?
```

If a **release workflow was detected** in step 1:

```text
Push commit and tag for vVERSION?
(Release workflow detected; it will create the GitHub Release automatically.)
```

#### If the user declines

Show the manual commands and stop. The commands depend on whether a release workflow was detected.

If **no release workflow** was detected:

```text
Release vVERSION is ready locally.

To publish manually:
  git push origin HEAD
  git push origin vVERSION
  gh release create vVERSION --title "vVERSION" --notes-file <changelog-notes-file> --verify-tag
```

If a **release workflow was detected**:

```text
Release vVERSION is ready locally.

To publish manually:
  git push origin HEAD
  git push origin vVERSION

The release workflow will create the GitHub Release automatically when the tag is pushed.
```

#### If the user accepts

##### 11a. Check for remote

```bash
git remote get-url origin
```

If no remote is configured, report the error and tell the user to configure a Git remote (for example, `git remote add origin <url>`) before rerunning this step. Do not show any `git push origin ...` commands in this case. Stop.

##### 11b. Push commit and tag

```bash
git push origin HEAD
git push origin vVERSION
```

Do NOT push any floating major version tags (e.g., `v2`). Push only the exact version tag.

If the push is rejected, report the error and stop. Never force push. Show the remaining manual commands so the user can complete the process after resolving the push issue: retry the failed `git push` command(s), and if no release workflow was detected, also show the `gh release create` command.

##### 11c. Check for release workflow

If a **release workflow was detected** in step 1, skip steps 11d and 11e. Report:

```text
Tagged vVERSION and pushed to origin.

  Tag: vVERSION
  GitHub Release: the release workflow is expected to create it automatically.
```

Then stop.

If **no release workflow** was detected, continue to step 11d.

##### 11d. Extract changelog section

Read `CHANGELOG.md` and extract the content for the new version. The section starts after the `## [VERSION] - YYYY-MM-DD` heading and ends before the next `## [` heading or before the comparison link block at the bottom of the file. Include the category headings (`### Added`, `### Fixed`, etc.) and their entries. Do not include the version heading itself or comparison links.

If `CHANGELOG.md` does not exist or the version section cannot be found, use the fallback: `Release vVERSION`.

##### 11e. Create GitHub Release

First, check that `gh` is available:

```bash
command -v gh
```

If `gh` is not available, skip the GitHub Release creation. Report that `gh` is required for GitHub Releases and show the manual `gh release create` command. Do not create a tmpfile.

If `gh` is available, generate a temporary file for the release notes:

```bash
mktemp /tmp/gh-release-notes-XXXXXX
```

Write the extracted changelog section to the path returned by `mktemp` using the Write tool. Then create the release:

```bash
gh release create vVERSION --title "vVERSION" --notes-file TMPFILE --verify-tag
```

The `--verify-tag` flag ensures the command fails if the tag was not pushed successfully (safety net for step 11b).

Always remove the tmpfile after the command completes, regardless of success or failure. Issue the cleanup as a **separate Bash tool call**, not chained onto `gh release create`:

```bash
rm -f TMPFILE
```

Each Bash tool call runs unconditionally and the prior call's exit code is preserved by the harness, so a separate call cleans up after both successful and failed releases without any shell-level wrapping. Never combine the two with a `; status=$?; rm -f TMPFILE; exit $status` wrapper: in zsh (the macOS default shell), `status` is a read-only built-in alias for `$?`, so the assignment fails with `read-only variable: status`. See `plugins/use-git/skills/use-git/references/tmpfile-pattern.md` for the full rationale.

##### 11f. Report results

```text
Release vVERSION published.

  Tag: vVERSION
  GitHub Release: <URL returned by gh release create>
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
- **Marketplace catalog tag already exists:** Abort with a message that the tag `CATALOG-STATE` already exists. Recompute the catalog state only after the user changes individual plugin versions.
- **Not a git repository:** Abort immediately.
- **No remote configured:** Skip comparison links in CHANGELOG, skip push and GitHub Release in step 11, warn the user.
- **First release:** Use `v0.0.0` as the base for bump calculation, create the CHANGELOG from scratch, skip doc version updates (no old version to replace).
- **Push rejected:** Report the error and show remaining manual commands. Never force push.
- **Release workflow detected:** Skip manual GitHub Release creation; the workflow will create it when the tag is pushed. Push the commit and tag only.
- **`gh` not available:** Push the commit and tag, skip GitHub Release creation, note that `gh` is required for GitHub Releases and show the manual `gh release create` command.
- **GitHub Release creation fails:** The push already succeeded, so the tag is on the remote. Report the `gh` error and show the manual `gh release create` command for the user to retry.
