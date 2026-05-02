# CHANGELOG Format

Follow the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format with [Semantic Versioning](https://semver.org/).

## File Header

Every `CHANGELOG.md` starts with this header:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
```

## Unreleased Section

Always present immediately after the header. Contains changes that have not yet been released:

```markdown
## [Unreleased]
```

After a release, the Unreleased section should be empty (just the heading, no entries). New changes accumulate here between releases.

## Version Section Format

Each release gets a section with the version number and date in ISO 8601 format:

```markdown
## [VERSION] - YYYY-MM-DD
```

Example:

```markdown
## [1.2.0] - 2026-02-20
```

## Categories

Use these categories in this order. Omit categories that have no entries:

1. **Added** for new features
1. **Changed** for changes in existing functionality
1. **Deprecated** for soon-to-be removed features
1. **Removed** for now removed features
1. **Fixed** for bug fixes
1. **Security** for vulnerability fixes

## Entry Format

- Each entry is a bullet point starting with `-`
- Write concise, user-facing descriptions
- Reference PR or issue numbers when available: `(#42)`, `(PR #15)`
- Group related changes into a single entry when they form a logical unit

Example:

```markdown
### Added

- User authentication with OAuth 2.0 support (#42)
- Rate limiting middleware for API endpoints

### Fixed

- Login redirect loop when session expires (#38)
```

## Comparison Links

Place comparison links at the bottom of the file, one per version. These link to the diff between consecutive tags:

```markdown
[unreleased]: https://github.com/OWNER/REPO/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/OWNER/REPO/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/OWNER/REPO/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/OWNER/REPO/releases/tag/v1.0.0
```

The first release uses a `releases/tag/` URL instead of a comparison.

## First Release Template

For projects with no existing `CHANGELOG.md`, create the complete file:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [VERSION] - YYYY-MM-DD

### Added

- Initial release
- Feature descriptions here

[unreleased]: https://github.com/OWNER/REPO/compare/vVERSION...HEAD
[VERSION]: https://github.com/OWNER/REPO/releases/tag/vVERSION
```

## Date Format

All dates use ISO 8601: `YYYY-MM-DD`.

## Updating for a New Release

When creating a new release:

1. Move all entries from `## [Unreleased]` into a new version section below it
1. If the Unreleased section is empty, generate entries from the commit log
1. Add the new version's comparison link at the bottom
1. Update the `[unreleased]` link to compare from the new version tag
1. Leave the `## [Unreleased]` heading in place (empty, ready for new changes)
