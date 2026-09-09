# Release

Prepare a versioned release or Claude Code marketplace catalog state tag: analyze commits, update release files, create a release commit, tag locally, and optionally publish a GitHub Release.

**Type:** Skill
**Trigger:** `/release`
**Requires:** [`jq`](https://jqlang.org/) for Claude Code marketplace releases; [`gh`](https://cli.github.com/) is optional for GitHub Release creation

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Detects your project type (Claude Code marketplace, Go CLI, Go library, or generic), analyzes conventional commits since the last release, updates release files, creates a GPG-signed release commit, and applies an annotated git tag. For Claude Code marketplaces, it computes `metadata.version` as a catalog state tag such as `catalog-M55-m101-p44-n49` from the individual plugin versions and uses `Marketplace <catalog-state>` as the GitHub Release title. For other projects, it recommends a SemVer bump, updates version references and `CHANGELOG.md`, and can create a GitHub Release with the version's changelog section as release notes.

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
    "allow": ["Bash(git status --porcelain)", "Bash(git branch --show-current)", "Bash(git tag *)", "Bash(git log *)", "Bash(git add *)", "Bash(git commit *)", "Bash(git rev-parse *)", "Bash(git remote get-url *)", "Bash(git push *)", "Bash(grep -rl *)", "Bash(command -v gh)", "Bash(jq *)", "Bash(mktemp -u /tmp/gh-release-notes-*)", "Bash(rm -f /tmp/gh-release-notes-*)", "Bash(gh release create *)", "Bash(date *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "release": analyzes commits, updates files, commits, and tags
- "cut a release": same behavior
- "bump the version": same behavior
- "release --dry-run": previews what would change without modifying anything
- "release --major": forces a major bump (e.g., v1.2.3 to v2.0.0)

## See Also

- [Commit](../commit/README.md): commit without creating a release
- [PR](../pr/README.md): commit, push, and open a pull request
- [Add GoReleaser Homebrew](../add-goreleaser-homebrew/README.md): set up the release pipeline that runs after tagging
- [All plugins](../../../../README.md)
