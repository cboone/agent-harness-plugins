# 2026-03-12: Update write-scrut-tests skill (issues #209 and #211)

## Context

The write-scrut-tests skill (`plugins/write-scrut-tests/`) is focused entirely on CLI binary testing. Two enhancements are needed:

- **Issue #211**: The SCRUT.md reference shows multi-command test blocks as long single-line `&&` chains. Scrut supports a `>` continuation prefix (inherited from cram) that improves readability. The guide should document and recommend this syntax.
- **Issue #209**: The skill lacks guidance for testing zsh plugins and sourced library code with scrut. This involves different invocation patterns (`source` instead of `${TOOL_BIN}`), a critical `ERR_EXIT`/`shopt` pitfall, the one-command-per-block constraint in markdown mode, and the `--shell zsh` flag.

Both are new capabilities, so the plugin version bumps from 1.0.2 to 1.1.0 (minor).

## Changes

### 1. Add continuation line syntax to SCRUT.md (#211)

**File:** `plugins/write-scrut-tests/skills/write-scrut-tests/references/SCRUT.md`

Insert a new `### Continuation Lines for Long Commands` subsection between "One Assertion Per Block" (ends line 138) and "Block Order" (starts line 140) in the Test Structure section.

Content:

- Explain the `>` continuation prefix for splitting long `&&`-chained commands across lines
- Show the existing single-line pattern rewritten with continuation lines (use the "Config init creates file" example already at line 134)
- Recommend continuation lines when commands exceed a comfortable line length
- Note that `>` must be followed by exactly two spaces of indentation for readability (indentation is literal)

Also update the existing multi-command example at line 131-138 to cross-reference the new subsection, adding a note like: "For long command chains, see `[Continuation Lines for Long Commands](#continuation-lines-for-long-commands)`."

### 2. Create zsh plugin testing reference file (#209)

**File (new):** `plugins/write-scrut-tests/skills/write-scrut-tests/references/zsh-plugin-testing.md`

Structure:

```text
# Testing Zsh Plugins and Sourced Libraries

## Shell Selection
- --shell zsh flag for scrut test / scrut update
- Makefile target variant

## Source-Based Invocation
- source "${TESTDIR}/path/to/helper.zsh" replaces ${TOOL_BIN}
- $TESTDIR references the test file's directory

## One Command Per Block
- Each fenced scrut block supports only one $ line
- Additional $ lines are treated as expected output
- Correct vs incorrect patterns

## ERR_EXIT and shopt Pitfall
- Problem: scrut's inter-block state management uses bash commands (shopt, alias -p)
- When sourced file sets ERR_EXIT at file level, subsequent blocks fail
- Workaround: emulate -L zsh with strict options inside functions, not at file level
- Good vs bad patterns

## Complete Example
- Full test file demonstrating all patterns
```

### 3. Update SKILL.md

**File:** `plugins/write-scrut-tests/skills/write-scrut-tests/SKILL.md`

- Update YAML frontmatter `description` to broaden scope: "...scrut test files for CLI binaries and zsh plugins..."
- Add "(4) testing zsh plugins or sourced libraries with scrut" to the "Use when" list
- Add a bullet under "### Test Structure" (line 26): continuation line prefix for long commands
- Add a new "## Zsh Plugin and Library Testing" section before "## Validation" (following the pattern from `write-zsh-scripts/SKILL.md` lines 64-72), pointing to `./references/zsh-plugin-testing.md` with key bullet points

### 4. Update plugin.json

**File:** `plugins/write-scrut-tests/.claude-plugin/plugin.json`

- Bump `version` from `"1.0.2"` to `"1.1.0"`
- Update `description` to mention zsh testing
- Add `"zsh"` to `keywords` array

### 5. Update marketplace.json

**File:** `.claude-plugin/marketplace.json`

- Update `write-scrut-tests` entry (lines 544-557): bump `version` to `"1.1.0"`, update `description`, add `"zsh"` to `keywords`
- Do NOT bump the marketplace `metadata.version` (no plugins added or removed)

### 6. Update plugin README

**File:** `plugins/write-scrut-tests/README.md`

- Update description paragraph (line 20) to mention zsh plugin testing
- Add a zsh testing example to the Examples section

### 7. Update root README

**File:** `README.md`

- Update the write-scrut-tests description (line 233) to mention zsh plugin/library testing

### 8. Update CLAUDE.md structure tree

**File:** `CLAUDE.md`

- Add `zsh-plugin-testing.md` under `references/` in the `write-scrut-tests` tree entry (line 391)

## Commit Strategy

1. `feat: document continuation line syntax in scrut guide (#211)` -- SCRUT.md changes, SKILL.md continuation bullet
1. `feat: add zsh plugin and sourced-library testing guide (#209)` -- new zsh-plugin-testing.md, SKILL.md zsh section
1. `chore: bump write-scrut-tests to v1.1.0` -- plugin.json, marketplace.json, both READMEs, CLAUDE.md tree

## Verification

1. Review all modified files for consistent cross-references
1. Run `/check-versions` to verify plugin.json and marketplace.json versions match
1. Confirm CLAUDE.md tree accurately reflects the new file structure
1. Read through the new zsh-plugin-testing.md to ensure technical accuracy of the ERR_EXIT pitfall description
1. Verify the continuation line examples use correct `>` syntax
