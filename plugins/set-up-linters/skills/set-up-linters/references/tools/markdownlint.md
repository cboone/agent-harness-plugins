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
    "MD034": false,
  },

  // Files to ignore
  "ignores": ["node_modules/", "vendor/", ".venv/", "CHANGELOG.md"],
}
```

Configure MD060 according to whether Prettier formats the project's Markdown files:

- **Prettier formats Markdown:** Add the following inside `config`. Prettier formats Markdown when the project has a Prettier config (`.prettierrc*`, `prettier.config.*`, or a `prettier` key in `package.json`) or a format script that runs Prettier, and `.prettierignore` does not exclude the Markdown files. Prettier owns table alignment.

  ```jsonc
  // Prettier owns table alignment.
  "MD060": false,
  ```

- **Prettier does not format Markdown:** Add the following inside `config`. This requires aligned tables and prevents markdownlint's default `any` style from compacting a table that is nearly aligned when `--fix` runs.

  ```jsonc
  // Require aligned tables when no formatter owns their layout.
  "MD060": { "style": "aligned" },
  ```

For projects using scrut CLI tests, also add:

```jsonc
    // Allow dollar signs before commands (scrut test format)
    "MD014": false
```

### Pandoc-academic preset

Use this preset when the project contains `references/papers/`, `references/extractions/`, `references/transcriptions/`, or a Pandoc paper pipeline with `papers/**/main.md` plus `papers/shared/templates/*.latex`, or when the user explicitly requests `--pandoc-academic`.

Create `.markdownlint-cli2.jsonc` in the project root:

````jsonc
{
  "config": {
    // Pandoc and LaTeX source files are author-wrapped, not formatter-wrapped.
    "MD013": false,

    // Allow raw HTML.
    "MD033": false,

    // Allow bare URLs without angle brackets.
    "MD034": false,

    // The document title belongs in YAML frontmatter.
    "MD041": false,

    // Allow Pandoc raw LaTeX fences such as ```{=latex}```.
    "MD040": false,

    // Allow duplicate headings under different parents.
    "MD024": { "siblings_only": true },

    // Do not require a single H1 in body content.
    "MD025": false,

    // Allow trailing-colon headings common in theorem/proof transcriptions.
    "MD026": { "punctuation": ".,;!" },

    // Preserve hard tabs inside transcription/code blocks.
    "MD010": { "code_blocks": false },

    // Dense academic tables are acceptable.
    "MD060": false,
  },
  "ignores": [
    "node_modules/",
    "vendor/",
    ".venv/",
    "dist/",
    "build/",
    "CHANGELOG.md",
    ".lake/**",
    "references/papers/**",
    "references/papers.bib",
    "references/extractions/**",
    "references/transcriptions/**",
  ],
}
````

Use this preset instead of layering ad-hoc markdownlint disables throughout project-authored Pandoc sources. The bundled ignores exclude third-party papers, OCR or extraction outputs, and verbatim transcriptions; project-authored Pandoc sources outside those reference-material paths are linted with the relaxed rules above.

### .markdownlintignore (optional)

If the ignore list is long, create a separate `.markdownlintignore` file:

```text
node_modules/
vendor/
.venv/
dist/
build/
CHANGELOG.md
.lake/**
references/papers/**
references/papers.bib
references/extractions/**
references/transcriptions/**
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

| Rule  | Description                    | Default  | Recommended Override                       |
| ----- | ------------------------------ | -------- | ------------------------------------------ |
| MD013 | Line length                    | 80 chars | `false` (disable; Prettier handles it)     |
| MD014 | Dollar signs before commands   | Enabled  | `false` (for scrut test projects)          |
| MD024 | No duplicate sibling headings  | Enabled  | `{ "siblings_only": true }`                |
| MD033 | Inline HTML                    | Enabled  | `false` (GFM features)                     |
| MD034 | Bare URLs                      | Enabled  | `false` (allow bare URLs)                  |
| MD041 | First line must be top heading | Enabled  | `false` (frontmatter or partial files)     |
| MD060 | Table column style             | `any`    | `false` with Prettier; `aligned` otherwise |

## Notes

- `markdownlint-cli2` is the successor to `markdownlint-cli`. It has better config file support and is actively maintained.
- The `.jsonc` config format supports comments, which is useful for documenting rule overrides.
- When Prettier is also configured, disable MD013 (line length) in markdownlint to avoid conflicts. Prettier handles line wrapping.
- When Prettier formats Markdown, disable MD060 because Prettier owns table alignment. Otherwise use MD060's `aligned` style so `--fix` cannot compact a nearly aligned table.
- markdownlint-cli2 auto-fix can resolve many issues (trailing whitespace, heading style, blank lines) but not all (e.g., heading level skips require manual restructuring).
