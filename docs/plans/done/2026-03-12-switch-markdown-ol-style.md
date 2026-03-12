# Allow Either Ordered List Numbering Style in Markdown

## Context

The project currently enforces lazy numbering (`1.` for every item) via MD029's `"one"` style. The user wants to relax this to accept either lazy (`1. 1. 1.`) or sequential (`1. 2. 3.`) numbering, as long as each individual list is internally consistent. MD029's `"one_or_ordered"` style does exactly this.

This requires updating the markdownlint config and the write-markdown style guide. No existing markdown files need changing since they already use a valid style (`"one"`).

## Steps

### 1. Update markdownlint config

**File:** `.markdownlint.jsonc` (line 28)

Change:

```jsonc
"MD029": { "style": "one" },
```

To:

```jsonc
"MD029": { "style": "one_or_ordered" },
```

### 2. Update the write-markdown SKILL.md

**File:** `plugins/write-markdown/skills/write-markdown/SKILL.md`

- **Lines 40-58** (Common Mistakes): Remove the ordered-list entry entirely (it's no longer a "common mistake" if both styles are valid). This section becomes just tables and code blocks.
- **Line 105** (Key Conventions): Change to say either `1.` or sequential numbering is acceptable, as long as each list is consistent.

### 3. Update the MARKDOWN.md reference guide

**File:** `plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`

- **Lines 326-344** (Ordered list numbering section): Rewrite to show both styles as acceptable. Remove the "Avoid" example. Explain the constraint is internal consistency within a single list.

### 4. Version bump

**File:** `plugins/write-markdown/.claude-plugin/plugin.json`
**File:** `.claude-plugin/marketplace.json`

Bump the `write-markdown` plugin version (minor bump: meaningful behavior change).

### 5. Verify

Run the linter to confirm zero violations:

```bash
npx markdownlint-cli2 "**/*.md"
```

### 6. Commit

## Files to Modify

- `.markdownlint.jsonc`
- `plugins/write-markdown/skills/write-markdown/SKILL.md`
- `plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`
- `plugins/write-markdown/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

## Verification

1. `npx markdownlint-cli2 "**/*.md"` passes with zero violations
2. Style guide examples show both styles as valid
3. Run `check-versions` skill to verify version consistency
