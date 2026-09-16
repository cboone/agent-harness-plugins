---
name: release
description: >-
  Prepare a versioned release or Claude Code marketplace catalog state tag:
  update release files, create a release commit, tag locally, and optionally
  publish a GitHub Release.
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

If the working tree is dirty, ask the user to commit or stash their changes and stop. If this is not a Git repository, report the error and stop.

### 2. Detect Project Type

Use `./references/project-types.md` and check in this order:

1. Claude Code marketplace
1. Go CLI
1. Go library
1. Generic

Report the detected type. If the indicators conflict, ask the user to confirm.

### 3. Claude Code Marketplace Releases

For a marketplace, each `plugins/<name>/.claude-plugin/plugin.json` is the sole SemVer source. Marketplace entries and marketplace metadata must not contain `version` fields.

Run validation and regenerate both mirrors:

```bash
bin/validate-json
bin/validate-plugins
make build
git status --porcelain dist/ .agents/
```

Identify the latest catalog release and compare its catalog inputs with `HEAD`:

```bash
latest_tag="$(git tag --list 'catalog-*' --sort=-creatordate | head -1)"
git diff --quiet "${latest_tag}" -- plugins/ .claude-plugin/marketplace.json
```

If there is no catalog tag, or the comparison reports a change, the catalog has changed. A push-to-main release workflow should tag that landing commit as `catalog-<full-commit-SHA>` and publish its GitHub Release. Do not create a local catalog tag when that workflow exists.

If the catalog inputs are unchanged, report that there is no marketplace release. Documentation-only changes do not create one.

Plugin content changes require an appropriate manifest version bump before the catalog change lands:

- Patch: wording fixes and prompt adjustments
- Minor: new capabilities or meaningful behavior changes
- Major: incompatible removal or restructuring

For `--dry-run`, report the changed plugin manifests and whether the catalog input comparison would release, then stop without modifying or publishing anything.

### 4. SemVer Releases

For Go CLI, Go library, and generic projects, follow the remaining release flow using the references below.

Find the latest SemVer tag, or use `v0.0.0` when none exists:

```bash
git tag --list 'v*' --sort=-version:refname | head -1
```

Analyze commits since that tag with `./references/conventional-commits.md`. Classify changes, identify breaking changes, determine the highest required bump, and present the proposed version for explicit user approval. `--major`, `--minor`, and `--patch` override the recommendation.

If `--dry-run` is specified, report the proposed version and files that would change, then stop.

Update version files according to `./references/project-types.md`, then update `CHANGELOG.md` according to `./references/changelog-format.md`. Use `./references/version-patterns.md` to find version references in documentation and propose those changes before editing them.

### 5. Pre-Tag Review and Publication

Before any commit or tag, present the changed files, proposed version, documentation checklist from `./references/doc-checklist.md`, and exact tag. Wait for explicit user approval.

Create a GPG-signed release commit and tag. Never amend, force-push, or retarget an existing tag. If a release workflow publishes on tag push, push the commit and tag but do not create a duplicate GitHub Release.

Otherwise, use `gh release create` only after the user approves publication. Generate release notes from the changelog and use `--verify-tag`. If a publish operation fails after the tag is pushed, report the remaining manual command rather than recreating or retargeting the tag.

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
