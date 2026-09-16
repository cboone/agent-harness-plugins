---
name: release
description: >-
  Prepare a versioned release: detect project type, analyze conventional
  commits, update release files, create a release commit, tag it locally, and
  optionally push and create a GitHub Release. For Claude Code marketplaces,
  verify plugin manifests and let push-to-main automation publish changed
  catalog inputs. Use when the user says "release", "create a release", "cut a
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

If the working tree is dirty, ask the user to commit or stash their changes and stop. If this is not a Git repository, report the error and stop.

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

Apply the `--dry-run` gate before any build or validator that can modify files. In a dry run, inspect manifests and workflow definitions only, report the changed manifests, detected automation, and whether the catalog comparison would release, then stop without modifying or publishing anything.

Run repository-specific validators only when they exist. Do not assume every marketplace has this repository's scripts or generated directories. Run portable validation in every marketplace:

```bash
jq -e 'all(.plugins[]; has("version") | not) and (.metadata | has("version") | not)' .claude-plugin/marketplace.json
jq -r '.plugins[].source' .claude-plugin/marketplace.json | while IFS= read -r source; do
  jq -e '.version | strings | test("^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$")' "${source}/.claude-plugin/plugin.json"
done
```

When `bin/validate-json`, `bin/validate-plugins`, and `make build` are present, run the build before validation so generated-tree freshness checks see synchronized output. Build a status path list only from generated directories that exist. If the build leaves generated changes, stop and require those changes to be reviewed and committed before tagging or publishing:

```bash
make build
bin/validate-json
bin/validate-plugins
git status --porcelain
```

Identify the latest catalog release and compare its catalog inputs with `HEAD`. Guard the first-release case rather than passing an empty revision to Git:

```bash
latest_tag="$(git tag --list 'catalog-*' --sort=-creatordate | head -1)"
if [[ -z "${latest_tag}" ]] || ! git diff --quiet "${latest_tag}" -- plugins/ .claude-plugin/marketplace.json; then
  catalog_changed=true
else
  catalog_changed=false
fi
```

For every plugin directory with content changes since `latest_tag`, compare the current manifest with its previous manifest. When there is no `latest_tag`, skip that previous-manifest comparison because there is no prior release input. Otherwise require a forward version bump before release: patch for wording or prompt changes, minor for new capabilities, and major for incompatible removal or restructuring.

If `catalog_changed` is false, report that there is no marketplace release. Documentation-only changes do not create one. If the latest catalog tag is already `catalog-<full-HEAD-SHA>`, do not treat the clean comparison as a no-op: check whether the tag and GitHub Release exist independently so an interrupted publication can be recovered.

If push-to-main automation exists, report that it will tag the landing commit as `catalog-<full-commit-SHA>` and publish its GitHub Release. Do not create a local catalog tag.

Otherwise, propose the exact `catalog-<full-HEAD-SHA>` tag for explicit user approval. Create and push that annotated tag after approval. If a tag-triggered workflow exists, let it publish the release. If no automation exists, offer `gh release create --verify-tag` after the tag is pushed.

### 4. SemVer Releases

For Go CLI, Go library, and generic projects, follow the remaining release flow using the references below. Before publication, inspect workflow triggers to determine whether an exact `v*` tag starts a release workflow; only such a workflow owns GitHub Release creation.

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

Without a tag-triggered workflow, first run `command -v gh`. If it is unavailable, leave the already-pushed tag in place and report the manual `gh release create vVERSION --title "vVERSION" --notes-file <release-notes-file> --verify-tag` command. If it is available, generate release notes from the changelog and run that command only after the tag push. If publication fails after the tag is pushed, report the remaining manual command rather than recreating or retargeting the tag.

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
