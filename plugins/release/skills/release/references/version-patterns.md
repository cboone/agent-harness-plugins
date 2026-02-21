# Version Patterns in Documentation

Rules for finding and updating version references in documentation files after a version bump.

## Search Scope

Search these locations:

- `.md` files in the repository root
- `.md` files in `docs/` (recursively)

Exclude from search:

- `CHANGELOG.md` (managed separately)
- `vendor/` directory
- `node_modules/` directory
- `.git/` directory

## Patterns to Match

Look for the old version string in these common formats:

| Pattern | Example |
| ------- | ------- |
| Literal version with `v` prefix | `v1.2.3` |
| Literal version without prefix | `1.2.3` |
| Badge URLs | `badge/v1.2.3-blue` |
| Download URLs | `/releases/download/v1.2.3/` |
| Install commands with `@` | `tool@v1.2.3`, `package@1.2.3` |
| Install commands with `==` | `package==1.2.3` |
| Go install refs | `go install example.com/tool@v1.2.3` |
| Homebrew cask version | `version "1.2.3"` |

## Replacement Rules

- Preserve the `v` prefix (or lack thereof) as found in the original text
- If the original says `v1.2.3`, replace with `v1.3.0`
- If the original says `1.2.3`, replace with `1.3.0`
- Replace only exact matches of the old version, not partial matches (e.g., do not replace `v1.2.30` when updating from `v1.2.3`)

## Exclusions

Do NOT modify:

- GoReleaser template syntax: `{{.Version}}`, `{{ .Version }}`
- Other projects' versions (e.g., dependency version pins that happen to match)
- Version strings inside code blocks that describe other tools
- Historical references (e.g., "Added in v1.0.0") unless they clearly refer to the current version

## Process

1. Search documentation files for the old version string
1. For each match, determine whether it refers to the current project's version
1. Propose all changes to the user before applying them
1. Apply confirmed changes
1. Skip this step entirely on the first release (no old version to replace)
