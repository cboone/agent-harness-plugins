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

For this generic configuration, configure MD060 from actual formatter coverage. Verify that Prettier is already available or was selected and installed during setup; configuration alone does not establish ownership. Inspect the existing or planned format command's paths, globs, working directory, and options. Honor its effective ignore files: `.gitignore` and `.prettierignore` by default, or the files specified by `--ignore-path`. The Pandoc-academic preset below keeps MD060 disabled regardless of Prettier to allow dense academic tables.

- **Prettier formats all Markdown covered by this config:** Add the following inside `config` only when the command includes those Markdown files and they are not excluded. A command restricted to JavaScript or other non-Markdown files does not qualify. Prettier owns table alignment for this scope.

  ```jsonc
  // Prettier owns table alignment.
  "MD060": false,
  ```

- **Prettier does not format every Markdown file covered by this config:** Add the following inside `config`, including when the scope mixes formatted and unformatted files. This requires aligned tables and prevents markdownlint's default `any` style from compacting a table that is nearly aligned when `--fix` runs.

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

| Rule  | Description                    | Default  | Recommended Override                                                                                                   |
| ----- | ------------------------------ | -------- | ---------------------------------------------------------------------------------------------------------------------- |
| MD013 | Line length                    | 80 chars | `false` (disable; Prettier handles it)                                                                                 |
| MD014 | Dollar signs before commands   | Enabled  | `false` (for scrut test projects)                                                                                      |
| MD024 | No duplicate sibling headings  | Enabled  | `{ "siblings_only": true }`                                                                                            |
| MD033 | Inline HTML                    | Enabled  | `false` (GFM features)                                                                                                 |
| MD034 | Bare URLs                      | Enabled  | `false` (allow bare URLs)                                                                                              |
| MD041 | First line must be top heading | Enabled  | `false` (frontmatter or partial files)                                                                                 |
| MD060 | Table column style             | `any`    | `false` when Prettier covers all linted Markdown or for the Pandoc-academic preset; `{ "style": "aligned" }` otherwise |

## Notes

- `markdownlint-cli2` is the successor to `markdownlint-cli`. It has better config file support and is actively maintained.
- The `.jsonc` config format supports comments, which is useful for documenting rule overrides.
- When Prettier is also configured, disable MD013 (line length) in markdownlint to avoid conflicts. Prettier handles line wrapping.
- For the generic preset, disable MD060 only when Prettier formats all Markdown covered by the config; otherwise use MD060's `aligned` style so `--fix` cannot compact a nearly aligned table. The Pandoc-academic preset keeps MD060 disabled to allow dense academic tables.
- markdownlint-cli2 auto-fix can resolve many issues (trailing whitespace, heading style, blank lines) but not all (e.g., heading level skips require manual restructuring).
