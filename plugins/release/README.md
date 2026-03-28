# Release

Prepare a versioned release: analyze commits, update versions and changelog, create a release commit, tag locally, and optionally publish a GitHub Release.

**Type:** Skill
**Trigger:** `/release`
**Requires:** [`gh`](https://cli.github.com/) (optional, for GitHub Release creation)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Release** from the available plugins.

## What It Does

Detects your project type (Go CLI, Go library, or generic), analyzes conventional commits since the last release to recommend a version bump, updates version references in project files and documentation, manages `CHANGELOG.md` in Keep a Changelog format, creates a GPG-signed release commit, and applies an annotated git tag. Optionally pushes the commit and tag and creates a GitHub Release with the version's changelog section as release notes.

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

## Recommended Permissions

This skill runs git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git status --porcelain)", "Bash(git branch --show-current)", "Bash(git tag *)", "Bash(git log *)", "Bash(git add *)", "Bash(git commit *)", "Bash(git remote get-url *)", "Bash(git push *)", "Bash(gh release create *)", "Bash(date *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

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
