# Plan: Add GitHub Release Creation to Release Skill (#222)

## Context

The release skill ends at step 10 after creating a local annotated git tag, then shows a push reminder. It never creates a GitHub Release, which is a separate artifact from a git tag. Users must manually run `gh release create` to populate the GitHub Releases page. This plan adds an interactive step 11 that offers to push and create a GitHub Release using the changelog section as release notes.

## Changes

### 1. `plugins/release/skills/release/SKILL.md`

**Modify step 10** (lines 224-232): Remove the push reminder block. Step 10 should end with a confirmation that the tag was created:

```text
Release vVERSION tagged locally.
```

**Add step 11: Publish**: After step 10, add an interactive step that asks the user whether to push and create a GitHub Release.

- If declined: show manual commands (current push reminder + `gh release create` command)
- If accepted:
  - 11a. Check for remote (`git remote get-url origin`)
  - 11b. Push commit and tag (`git push origin HEAD` then `git push origin vVERSION`)
  - 11c. Extract changelog section for the new version from CHANGELOG.md (between the version heading and the next `## [` heading, excluding comparison links). Fallback: `Release vVERSION` if no CHANGELOG or section not found
  - 11d. Write notes to a tmpfile, run `gh release create vVERSION --title "vVERSION" --notes-file TMPFILE --verify-tag`, clean up tmpfile
  - 11e. Report success with tag and GitHub Release URL

**Update dry-run gate** (line 115): Add step 11 to the skip list so it reads "skip steps 5-7 and 11."

**Update frontmatter description** (lines 3-9): Add "and optionally push and create a GitHub Release."

**Update heading description** (line 14): Add "and optionally publish a GitHub Release."

**Add error handling entries**: Push rejected (show remaining manual commands, never force push), `gh` not available (push only, note `gh` is required for releases), GitHub Release creation fails after push (show manual `gh release create` command).

### 2. `plugins/release/.claude-plugin/plugin.json`

- Bump version: `1.1.0` -> `1.2.0` (minor: new capability, no breaking changes)
- Update description to mention GitHub Release
- Add keywords: `"gh"`, `"github-release"`

### 3. `.claude-plugin/marketplace.json`

- Mirror plugin.json changes for the release entry (lines 292-305): version, description, keywords
- Do NOT bump `metadata.version` (existing plugin content change, not a catalog change)

### 4. `plugins/release/README.md`

- Update one-liner (line 3) and "What It Does" section (line 20) to mention GitHub Release
- Add `"Bash(git push *)"` and `"Bash(gh release create *)"` to recommended permissions
- Add `> **Requires:** [`gh`](https://cli.github.com/) (optional, for GitHub Release creation)` after the Trigger line

### 5. Root `README.md`

- Update Release description (line 103) to mention pushing and creating a GitHub Release
- Add `> **Requires:** [`gh`](https://cli.github.com/) (optional, for GitHub Release creation)` line after the Trigger line (line 105)

## Edge Cases

- **No CHANGELOG.md**: Use fallback release notes (`Release vVERSION`)
- **No remote**: Report error, show no push/release commands, stop
- **First release**: Works normally; changelog section from step 6 provides content
- **`--dry-run`**: Step 11 is unreachable (dry-run stops at step 8b)
- **User declines at step 8c**: Steps 9-11 all skipped
- **Push rejected**: Report error, show remaining manual commands, never force push
- **`gh` not installed**: Push commit and tag, skip GitHub Release, note `gh` is required
- **`gh release create` fails after push**: Tag is on remote; show manual retry command

## Verification

1. Run `/release --dry-run` on a test project and verify step 11 is mentioned in the dry-run output but not executed
2. Run `/release` on a test project, decline at step 11, verify manual commands are shown (including `gh release create`)
3. Run `/release` on a test project, accept at step 11, verify push and GitHub Release are created
4. Run `check-versions` skill to verify version consistency
