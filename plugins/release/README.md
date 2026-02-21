# Release

Prepare a versioned release: analyze commits, update versions and changelog, create a release commit, and tag locally.

**Type:** Skill
**Trigger:** `/release`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Release** from the available plugins.

## What It Does

Detects your project type (Go CLI, Go library, or generic), analyzes conventional commits since the last release to recommend a version bump, updates version references in project files and documentation, manages `CHANGELOG.md` in Keep a Changelog format, creates a GPG-signed release commit, and applies an annotated git tag. The tag and commit stay local until you push.

## Usage

```text
/release
/release --major
/release --minor
/release --patch
/release --dry-run
```

| Option      | Description                                                         |
| ----------- | ------------------------------------------------------------------- |
| `--major`   | Force a major version bump regardless of commit analysis            |
| `--minor`   | Force a minor version bump regardless of commit analysis            |
| `--patch`   | Force a patch version bump regardless of commit analysis            |
| `--dry-run` | Preview all changes without modifying files, committing, or tagging |

## Examples

- "release": analyzes commits, recommends a bump, updates files, commits, and tags
- "cut a release": same behavior
- "bump the version": same behavior
- "release --dry-run": previews what would change without modifying anything
- "release --major": forces a major bump (e.g., v1.2.3 to v2.0.0)

## See Also

- [Commit](../commit/README.md): commit without creating a release
- [PR](../pr/README.md): commit, push, and open a pull request
- [Add GoReleaser Homebrew](../add-goreleaser-homebrew/README.md): set up the release pipeline that runs after tagging
- [All plugins](../../README.md)
