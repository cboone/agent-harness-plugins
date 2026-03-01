# Add Initial CHANGELOG.md to Scaffolding Commands

## Context

The three scaffolding commands (scaffold-new-repo, scaffold-go-cli, scaffold-go-library) generate all standard repository files (LICENSE, README, .gitignore, agent configs) but omit CHANGELOG.md. A changelog is a standard part of any repo setup. The `release` skill already handles creating one from scratch on first release, but having it pre-created is cleaner and signals to contributors that the project tracks changes.

## CHANGELOG Template

All three commands use the same initial content, matching the format in `plugins/release/skills/release/references/changelog-format.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
```

No comparison links (no tags exist yet). The `release` skill adds them on first release.

## Changes

### 1. scaffold-new-repo

**File:** `plugins/scaffold-new-repo/commands/scaffold-new-repo.md`

- Add new step between current step 6 (README) and step 7 (.gitignore):
  - **New step 7: Generate CHANGELOG.md** using the template above
- Renumber steps 7-11 to 8-12
- Add a CHANGELOG.md Reference Template section (after the README Template reference)

### 2. scaffold-go-cli

**File:** `plugins/scaffold-go-cli/commands/scaffold-go-cli.md`

- Add new step between current step 14 (README) and step 15 (Directory Stubs):
  - **New step 15: Generate CHANGELOG.md** using the template above
- Renumber steps 15-18 to 16-19

No new reference template section needed; the template is inline (same pattern as scaffold-new-repo).

### 3. scaffold-go-library

**File:** `plugins/scaffold-go-library/commands/scaffold-go-library.md`

- Add new step between current step 17 (README) and step 18 (Directory Stubs):
  - **New step 18: Generate CHANGELOG.md** using the template above
- Renumber steps 18-22 to 19-23

No new reference template section needed; the template is inline.

## Version Bumps

All three plugins get a **patch** bump (new capability within an existing scaffolding workflow is minor-ish, but this is a small addition to existing behavior):

- `scaffold-new-repo`: patch bump in plugin.json + marketplace.json
- `scaffold-go-cli`: patch bump in plugin.json + marketplace.json
- `scaffold-go-library`: patch bump in plugin.json + marketplace.json

Check current versions before bumping, then use `/check-versions` to verify.

## Verification

1. Read each modified file and confirm:
   - Step numbering is sequential with no gaps or duplicates
   - The CHANGELOG step is correctly placed after README generation
   - The template content matches the release skill's format
   - All cross-references to step numbers in error handling or notes are updated
2. Run `/check-versions` to verify version consistency
