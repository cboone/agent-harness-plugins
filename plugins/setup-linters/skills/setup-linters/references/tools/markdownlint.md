# markdownlint-cli2

Markdown linter that enforces consistent style and catches common issues. Uses the markdownlint rule set.

## Install

```bash
# npm
npm install -D markdownlint-cli2

# yarn
yarn add -D markdownlint-cli2

# pnpm
pnpm add -D markdownlint-cli2

# bun
bun add -D markdownlint-cli2
```

## Config

### .markdownlint-cli2.jsonc

Create `.markdownlint-cli2.jsonc` in the project root:

```jsonc
{
  "config": {
    // Line length: disabled (Prettier handles wrapping)
    "MD013": false,

    // Allow duplicate headings in different sections (e.g., ## Install / ## Notes)
    "MD024": { "siblings_only": true },

    // Allow inline HTML (needed for <br>, <details>, <kbd>, etc.)
    "MD033": false,

    // Allow bare URLs without angle brackets
    "MD034": false
  },

  // Files to ignore
  "ignores": ["node_modules/", "vendor/", ".venv/", "CHANGELOG.md"]
}
```

For projects using scrut CLI tests, also add:

```jsonc
    // Allow dollar signs before commands (scrut test format)
    "MD014": false
```

### .markdownlintignore (optional)

If the ignore list is long, create a separate `.markdownlintignore` file:

```text
node_modules/
vendor/
.venv/
dist/
build/
CHANGELOG.md
```

## Commands

```bash
# Lint all Markdown files
npx markdownlint-cli2 "**/*.md"

# Lint with auto-fix
npx markdownlint-cli2 --fix "**/*.md"
```

## package.json Scripts

```json
{
  "scripts": {
    "lint:md": "markdownlint-cli2 \"**/*.md\"",
    "lint:md:fix": "markdownlint-cli2 --fix \"**/*.md\""
  }
}
```

## Common Rule Customizations

| Rule  | Description                    | Default  | Recommended Override                    |
| ----- | ------------------------------ | -------- | --------------------------------------- |
| MD013 | Line length                    | 80 chars | `false` (disable; Prettier handles it)  |
| MD014 | Dollar signs before commands   | Enabled  | `false` (for scrut test projects)       |
| MD024 | No duplicate sibling headings  | Enabled  | `{ "siblings_only": true }`             |
| MD033 | Inline HTML                    | Enabled  | `false` (GFM features)                  |
| MD034 | Bare URLs                      | Enabled  | `false` (allow bare URLs)               |
| MD041 | First line must be top heading | Enabled  | `false` (frontmatter or partial files)  |

## Notes

- `markdownlint-cli2` is the successor to `markdownlint-cli`. It has better config file support and is actively maintained.
- The `.jsonc` config format supports comments, which is useful for documenting rule overrides.
- When Prettier is also configured, disable MD013 (line length) in markdownlint to avoid conflicts. Prettier handles line wrapping.
- markdownlint-cli2 auto-fix can resolve many issues (trailing whitespace, heading style, blank lines) but not all (e.g., heading level skips require manual restructuring).
