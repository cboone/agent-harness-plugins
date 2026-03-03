# Fix tmpfile template pattern confusion

## Context

When the `pr` skill runs, it creates a temporary file for the PR body. The `mktemp` command uses a template like `/tmp/pr-body-XXXXXX.md` where the X's are replaced by `mktemp` with random characters. However, the skill instructions confuse the LLM into using literal "X" characters in the path (e.g., `/tmp/pr_body_X.txt`). On subsequent runs, the file already exists, so the LLM appends more X's until it finds an unused path.

The same pattern appears in other skills across the repo. The root cause: after showing `mktemp /tmp/purpose-XXXXXX.md`, the instructions then show the XXXXXX template literal in subsequent commands (`--body-file`, `rm -f`) instead of using a clear placeholder for "the path mktemp returned."

## Changes

### 1. `plugins/use-git/skills/use-git/references/tmpfile-pattern.md` (canonical reference)

This is the reference doc other skills point to, so fix it first to establish the correct pattern.

- **Step 1 code block** (line 19): Add `# Returns a unique path, e.g.: /tmp/gh-pr-body-x4y5z6.md` comment after the `mktemp` command
- **Step 3 code block** (line 33): Replace `/tmp/gh-pr-body-XXXXXX.md` with `TMPFILE`
- **Cleanup code block** (line 41): Replace `/tmp/gh-pr-body-XXXXXX.md` with `TMPFILE`
- **Review reply mktemp** (line 83): Add a `# Returns` comment

Version: 1.1.0 -> 1.1.1 (patch: prompt clarification)

### 2. `plugins/create-issue/skills/create-issue/SKILL.md` (worst offender)

All `--body-file` and `rm` examples show the literal XXXXXX template.

- **Step 3 mktemp** (line 45): Add `# Returns a unique path, e.g.: /tmp/gh-issue-body-a1b2c3.md` comment
- **Step 3 prose** (line 48): Add note that `TMPFILE` in examples below is a placeholder for the returned path
- **Step 4 examples** (lines 57, 63, 69): Replace `/tmp/gh-issue-body-XXXXXX.md` with `TMPFILE`
- **Step 5 cleanup** (line 77): Replace `/tmp/gh-issue-body-XXXXXX.md` with `TMPFILE`

Version: 1.0.1 -> 1.0.2 (patch: prompt clarification)

### 3. `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`

Uses a hardcoded `/tmp/copilot-reply.md` without `mktemp` at all. Convert to the standard pattern.

- **Lines 188-199** (Outdated/Incorrect code block): Replace the fixed-path examples with the mktemp + `TMPFILE` placeholder pattern, including cleanup step
- **Line 269** (Reply Templates section): Replace "Write these to `/tmp/copilot-reply.md`" with mktemp instructions

Also update `plugins/resolve-copilot-pr-feedback/README.md` (line 35): Add `Bash(mktemp /tmp/copilot-reply-*)` and `Bash(rm -f /tmp/copilot-reply-*)` to the recommended permissions.

Version: 1.2.0 -> 1.2.1 (patch: add mktemp pattern)

### 4. `plugins/pr/skills/pr/SKILL.md` (least problematic)

Already uses `TMPFILE_PATH` placeholder, just needs the `# Returns` comment.

- **Line 251** (mktemp example): Add `# Returns a unique path, e.g.: /tmp/pr-body-x4y5z6.md` comment
- **Lines 254, 256, 259, 264, 267**: Rename `TMPFILE_PATH` to `TMPFILE` for consistency with the other files

Version: 1.4.2 -> 1.4.3 (patch: prompt clarification)

### 5. Version bumps in `plugin.json` and `marketplace.json`

For each plugin above, bump the patch version in both:

- `plugins/<name>/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json` (matching entry)

| Plugin | Current | New |
| --- | --- | --- |
| use-git | 1.1.0 | 1.1.1 |
| create-issue | 1.0.1 | 1.0.2 |
| resolve-copilot-pr-feedback | 1.2.0 | 1.2.1 |
| pr | 1.4.2 | 1.4.3 |

Marketplace metadata version stays at 1.19.0 (no plugins added or removed).

## Commits

One commit per plugin, smallest logical chunks:

1. `fix: clarify tmpfile template pattern in use-git reference doc`
2. `fix: replace literal tmpfile template with placeholder in create-issue skill`
3. `fix: add mktemp pattern to resolve-copilot-pr-feedback skill`
4. `fix: add returns comment to mktemp example in pr skill`

## Verification

After making the changes:

1. Search all SKILL.md and reference .md files for `/tmp/.*XXXXXX` appearing in non-mktemp commands (should only appear in `mktemp` lines, never in `--body-file`, `rm -f`, or similar)
2. Search for any remaining hardcoded `/tmp/copilot-reply.md` references
3. Verify all four `plugin.json` versions match their `marketplace.json` entries
4. Read each modified file to confirm placeholders and comments read naturally
