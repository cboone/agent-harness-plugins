# 2026-03-03: Fix write-markdown skill to reduce recurring lint failures

## Context

Claude frequently writes markdown that fails markdownlint and Prettier checks, requiring fix-up commits. Over 122 style-fix commits in the past month trace to three recurring issues: ragged table alignment, incremental ordered list numbering (`1. 2. 3.`), and bare code fences without language identifiers. The `write-markdown` skill is supposed to prevent these, but it has a bug (the "avoid" table example is identical to the "use" example) and its guidance is not prominent or procedural enough to change behavior.

## Changes

### 1. Fix broken "avoid" table example in MARKDOWN.md

**File:** `plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md` (lines 543-550)

The "avoid" example for table column alignment is character-for-character identical to the "use" example. Both show perfectly aligned pipes. Replace the "avoid" example with actually ragged/compact pipes:

```markdown
| Name    | Type   | Default |
| ------- | ------ | ------- |
| timeout | number | 30      |
| retries | number | 3       |
```

This lives inside a fenced code block, so it will not trigger lint violations.

### 2. Add procedural table formatting guidance in MARKDOWN.md

After the fixed avoid example, add a practical procedure explaining how to align tables:

1. Write all rows with their content
1. Find the longest content in each column (including header text)
1. Pad every cell to match the longest content's width with trailing spaces
1. Fill delimiter row hyphens to match the column width
1. Verify all pipes are in the same column positions across every row

Include a note that Prettier reformats tables to aligned style automatically and can serve as a safety net.

### 3. Strengthen ordered list section in MARKDOWN.md

**File:** `plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md` (lines 326-344)

- Change opening to: "Use `1.` as the prefix for every item in ordered lists. Never use `2.`, `3.`, `4.`, etc."
- Add: "This applies to all ordered lists, including nested ones."

### 4. Strengthen language identifiers section in MARKDOWN.md

**File:** `plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md` (lines 448-458)

- Change to: "Every fenced code block must include a language identifier"
- Add: "Never leave the opening fence bare"
- Add a list of common language identifiers: `bash`, `console`, `css`, `diff`, `go`, `html`, `javascript`, `json`, `jsonc`, `markdown`, `python`, `text`, `toml`, `typescript`, `yaml`

### 5. Add "Common Mistakes" section to SKILL.md

**File:** `plugins/write-markdown/skills/write-markdown/SKILL.md`

Insert a new `## Common Mistakes` section immediately before the existing `## Key Conventions` section. This section highlights the three most-violated rules with correct/wrong examples:

- **Tables:** Show aligned vs ragged pipes, plus the padding procedure
- **Ordered lists:** Show `1. 1. 1.` vs `1. 2. 3.`
- **Code blocks:** Show fenced with language vs bare fence

This puts the highest-impact guidance at the top of the context, before the broader reference summary.

### 6. Strengthen existing Key Conventions bullets in SKILL.md

Targeted wording tweaks to three existing bullets:

- Lists: change to "`1.` for every ordered list item, never `2.`, `3.`, etc."
- Tables: change to "Pad every cell so all pipe characters align vertically; pad delimiter hyphens to match"
- Code: change to "must have a language identifier (use `text` if none applies)"

### 7. Strengthen the Validation section in SKILL.md

The existing Validation section says "Whenever possible, validate Markdown before finishing." Replace it with stronger, more specific guidance:

- After creating or editing markdown files, run the project's lint-fix command (e.g., `yarn lint:fix`, `yarn lint:md:fix`) to auto-correct table alignment, list numbering, and other formatting issues
- Make running the linter in fix mode a standard final step, not an optional afterthought
- Keep the fallback note about `markdownlint-cli2` for projects without a custom lint script

### 8. Version bump

Patch bump from `1.1.1` to `1.1.2` in:

- `plugins/write-markdown/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json` (write-markdown entry)

Verify with `check-versions` skill before committing.

## Verification

1. Run `yarn lint` to confirm both modified files pass markdownlint and Prettier
1. Visually confirm the "avoid" table example in MARKDOWN.md actually shows ragged pipes
1. Visually confirm the "Common Mistakes" section in SKILL.md renders correctly
1. Run `check-versions` to verify version consistency
