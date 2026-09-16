---
name: release
description: >-
  Prepare a versioned release: detect project type, analyze conventional
  commits, update release files, create a release commit, tag it locally, and
  optionally push and create a GitHub Release. For Claude Code marketplaces,
  prepare plugin version bumps and a signed release commit, then let
  push-to-main automation publish changed catalog inputs. Use when the user says "release", "create a release", "cut a
  release", "prepare a release", "bump the version", "tag a release", or
  similar requests to create a versioned release.
---

# Release

Prepare a versioned release: analyze commits, update release files, create a release commit, tag it locally, and optionally publish a GitHub Release.

<!-- The bin/ and docs/ paths below name files in this repository, not in a project a skill runs against. -->
<!-- validate-plugins: repository-paths -->

## Options

- **--major**: Force a major version bump regardless of commit analysis
- **--minor**: Force a minor version bump regardless of commit analysis
- **--patch**: Force a patch version bump regardless of commit analysis
- **--dry-run**: Preview changes without modifying files, committing, or tagging

## Workflow

### 1. Pre-Flight Checks

Run these commands in parallel:

```bash
git status --porcelain
git branch --show-current
git tag --list 'v*' --sort=-version:refname
date +%Y-%m-%d
```

If this is not a Git repository, report the error and stop. Record existing staged and unstaged changes before editing. After detecting the project type, handle them according to its release flow.

### 2. Detect Project Type

Use `./references/project-types.md` and check in this order:

1. Claude Code marketplace
1. Go CLI
1. Go library
1. Generic

Report the detected type. If the indicators conflict, ask the user to confirm.

### 3. Claude Code Marketplace Releases

For a marketplace, each plugin manifest is the sole SemVer source. Marketplace entries and marketplace metadata must not contain `version` fields.

First determine whether a workflow publishes releases after a push to the default branch. A workflow is push-to-main automation only when it creates `catalog-${GITHUB_SHA}` tags, invokes `gh release create`, and has a `push` trigger limited to the default branch. A manually dispatched, scheduled, pull-request-only, or differently branched workflow is not push-to-main automation. A tag-triggered workflow is separate: it needs a locally created catalog tag to run.

Extract registered local plugin paths from string sources beginning with `./`. Other source forms are registration metadata, not local manifests to read. Do not interpret a remote repository or package source as a filesystem path:

```bash
jq -r '.plugins[].source | select(type == "string" and startswith("./"))' .claude-plugin/marketplace.json
git tag --list 'catalog-*' --sort=-creatordate
```

Use the latest catalog tag as the comparison base. If it exists, read its marketplace with `git show` and include both previous and current registered local paths in the catalog comparison so deleted plugins count. Compare the canonical marketplace file and these plugin directories using literal Git pathspecs. Repository-level files such as `plugins/AGENTS.md` and `plugins/CLAUDE.md` are outside registered plugin directories and do not trigger catalog publication. Root documentation alone creates no new catalog release; documentation inside a registered plugin is plugin content.

For each current local plugin, inspect its content changes and manifest relative to the previous catalog tag, including staged, unstaged, and untracked changes when preparing a release. Use `git cat-file -e` before reading a prior manifest with `git show`. Analyze the plugin's conventional commits and actual changes with `./references/conventional-commits.md`. Classify the required bump: patch for wording or fixes, minor for new capabilities, and major for incompatible removal or restructuring. `--major`, `--minor`, and `--patch` override this recommendation for each changed existing plugin. Never bump unchanged plugins or restore duplicate marketplace versions.

Prepare a per-plugin version table with released, current, and proposed versions. Preserve an already prepared forward bump when it meets the required level. Otherwise propose the required next version from the released version, without decreasing the current version. If the requested level cannot satisfy both constraints, ask the user to choose a forward version. New plugins start at `1.0.0`. With no catalog tag, treat this as a first release, validate existing manifest versions, and do not invent a prior Git revision or require bumps from an absent baseline.

Apply the `--dry-run` gate before editing, building, staging, committing, tagging, pushing, or creating a release. In a dry run, report the version table, files that would change, detected automation, catalog comparison, and any pending recovery of an existing tag's release, then stop without modifying anything.

Existing source changes within the selected plugins can be included in release preparation. Preserve unrelated changes and the user's staging choices; do not silently commit them. If changes outside release inputs are required, or a file mixes release and unrelated edits, stop and ask how to separate them.

Apply the proposed manifest bumps and update any release notes required by the project's conventions. Regenerate mirrors only when the repository exposes a build target for them; do not assume every marketplace has this repository's Makefile or generated directories. Run `make build` only when that target exists. Run `bin/validate-json` and `bin/validate-plugins` only when each script exists and is executable, after the build. Validate portable marketplace metadata with `jq` and each local manifest's `MAJOR.MINOR.PATCH` version even when repository validators are absent. Run the project's relevant lint and tests. Generated changes belong in the same release commit as their canonical manifest changes.

Present the complete release diff, per-plugin version table, validation results, files to stage, and publication route for explicit approval before committing or publishing. After approval, stage only reviewed release files and create a GPG-signed Conventional Commit release commit with `git commit -S`. If all required bumps and source changes were already committed and nothing was prepared, do not create an empty release commit; report the existing release input commit instead. Compute the full release SHA after the commit, so a local catalog tag identifies the prepared release.

If push-to-main automation exists, publish the reviewed release commit only through the project's approved branch or PR flow. A feature-branch push does not publish a catalog release: automation tags the eventual landing commit as `catalog-<full-commit-SHA>` and creates its GitHub Release. Do not create a local catalog tag on this route.

Without push-to-main automation, propose the exact `catalog-<full-release-commit-SHA>` tag after the signed commit exists and obtain explicit approval for tag publication. Create a signed annotated tag, then push the approved commit and exact tag. If a tag-triggered workflow exists, let it publish the release. Otherwise check whether `gh` exists and offer `gh release create --verify-tag` after the tag is pushed. Never overwrite or retarget a tag.

Before presenting any command that pushes to `origin`, run `git remote get-url origin`. If it fails, stop and explain that this release flow needs a reachable `origin` remote; do this for both marketplace and SemVer publication.

When catalog inputs have not changed, create no new tag or release commit. Independently check publication of the latest existing catalog tag, even if a later documentation-only commit is now `HEAD`. Use `gh release view <latest-catalog-tag>` to verify its GitHub Release; distinguish a missing release from an authentication or API error. If the tag exists remotely but its release is missing, recover that release for the existing tag through a supported workflow rerun or an explicitly approved `gh release create --verify-tag`. Never substitute the later documentation commit's SHA. Report when neither a new release nor recovery is needed.

### 4. SemVer Releases

For Go CLI, Go library, and generic projects, follow the remaining release flow using the references below. Before publication, inspect workflow triggers to determine whether an exact `v*` tag starts a release workflow; only such a workflow owns GitHub Release creation.

If the working tree is dirty on this SemVer route, ask the user to commit or stash their changes and stop.

Find the latest SemVer tag. When none exists, use `v0.0.0` only as the base for calculating the next version, not as a Git revision:

```bash
git tag --list 'v*' --sort=-version:refname | head -1
```

Analyze commits since that tag with `./references/conventional-commits.md`. If a tag exists, use `git log <LAST-TAG>..HEAD --format='%H%n%s%n%b%n---END---' --no-merges`; for a first release, use `git log --format='%H%n%s%n%b%n---END---' --no-merges`. Classify changes, identify breaking changes, determine the highest required bump, and present the proposed version for explicit user approval. `--major`, `--minor`, and `--patch` override the recommendation.

If `--dry-run` is specified, report the proposed version and files that would change, then stop.

Update version files according to `./references/project-types.md`, then update `CHANGELOG.md` according to `./references/changelog-format.md`. Use `./references/version-patterns.md` to find version references in documentation and propose those changes before editing them. For a first release, create the changelog if needed and do not attempt replacements for a prior version.

### 5. SemVer Pre-Tag Review and Publication

Before any commit or tag, present the changed files, proposed version, documentation checklist from `./references/doc-checklist.md`, and exact tag. Wait for explicit user approval.

For this SemVer branch only, create a GPG-signed release commit and GPG-signed annotated `vVERSION` tag. Never amend, force-push, or retarget an existing tag. After the user approves publication, push the commit and exact version tag before any GitHub Release operation. If a release workflow publishes on tag push, do not create a duplicate GitHub Release.

Without a tag-triggered workflow, first run `command -v gh`. Generate release notes from the changelog into a temporary file, then pass that file to `gh` only after the tag push. Capture the `gh` status, remove the temporary file, and preserve that status. If `gh` is unavailable or publication fails after the tag is pushed, leave the tag in place and report the exact remaining `gh release create vVERSION --title "vVERSION" --notes-file <release-notes-file> --verify-tag` command with the release-notes file path. Never recreate or retarget the tag.

## Reference Navigation

- `./references/project-types.md`: project type detection and version file locations
- `./references/changelog-format.md`: Keep a Changelog template and formatting
- `./references/conventional-commits.md`: commit parsing and bump classification
- `./references/version-patterns.md`: version references in documentation
- `./references/doc-checklist.md`: release documentation review

## Error Handling

- **Dirty working tree:** stop and ask the user to resolve it.
- **No commits since the last tag:** report that there is nothing to release.
- **Invalid plugin manifest version:** correct it to `MAJOR.MINOR.PATCH` before publishing a marketplace change.
- **Duplicate marketplace version:** remove it. Plugin manifests are the only marketplace version source.
- **Catalog tag already exists:** a full commit SHA makes a conflicting tag unexpected. Verify the remote tag target and stop if it differs from the landing commit.
- **Push rejected:** report the error and show the remaining manual commands. Never force-push.
