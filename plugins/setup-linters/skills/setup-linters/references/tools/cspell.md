# cspell

Spell checker for source code, comments, strings, and documentation. Uses built-in language dictionaries and supports project-specific word lists.

## When to Offer

All projects. Spelling errors are universal and affect code readability, documentation quality, and professionalism.

## Install

```bash
# npm
npm install -D cspell

# yarn
yarn add -D cspell

# pnpm
pnpm add -D cspell

# bun
bun add -D cspell
```

## Config

### cspell.json

Create `cspell.json` in the project root:

```json
{
  "version": "0.2",
  "language": "en",
  "ignorePaths": ["node_modules/", "vendor/", ".venv/", "dist/", "build/", "coverage/", "*.lock", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "go.sum", ".git/"]
}
```

### cspell-words.txt (optional)

For project-specific dictionary words, create a `cspell-words.txt` file (one word per line) and reference it in `cspell.json`:

```json
{
  "version": "0.2",
  "language": "en",
  "dictionaryDefinitions": [
    {
      "name": "project-words",
      "path": "./cspell-words.txt",
      "addWords": true
    }
  ],
  "dictionaries": ["project-words"],
  "ignorePaths": ["node_modules/", "vendor/", "dist/", "*.lock", ".git/"]
}
```

To build an initial word list from existing code:

```bash
npx cspell . --unique --words-only --no-progress | sort > cspell-words.txt
```

Review the generated list and remove any actual misspellings before committing.

## Commands

```bash
# Check all files for spelling errors
npx cspell .

# Check specific files or patterns
npx cspell "src/**/*.ts" "docs/**/*.md"

# List unique unknown words (useful for building word lists)
npx cspell . --unique --words-only --no-progress
```

## package.json Scripts

```json
{
  "scripts": {
    "spell": "cspell .",
    "spell:list": "cspell . --unique --words-only --no-progress"
  }
}
```

## Configuration Options

| Option             | Description                                   | Example                            |
| ------------------ | --------------------------------------------- | ---------------------------------- |
| `language`         | Default language for spell checking           | `"en"`                             |
| `words`            | Additional words to accept                    | `["cboone", "goreleaser"]`         |
| `ignorePaths`      | Files and directories to skip                 | `["node_modules/", "dist/"]`       |
| `ignoreWords`      | Words to ignore (not added to dictionaries)   | `["asdf", "qwerty"]`               |
| `flagWords`        | Words that should always be flagged as errors | `["hte", "teh"]`                   |
| `dictionaries`     | Named dictionaries to enable                  | `["project-words", "typescript"]`  |
| `enabledFileTypes` | File types to check (all enabled by default)  | `{"markdown": true, "css": false}` |
| `overrides`        | Per-file-pattern configuration for monorepos  | See below                          |

### Monorepo Overrides

For monorepos with different terminology per package:

```json
{
  "version": "0.2",
  "overrides": [
    {
      "filename": "packages/api/**",
      "words": ["fastify", "prisma"]
    },
    {
      "filename": "packages/ui/**",
      "words": ["tailwindcss", "headlessui"]
    }
  ]
}
```

## Notes

- cspell has no auto-fix mode. All issues must be resolved manually by fixing the typo or adding the word to the dictionary.
- Built-in dictionaries cover common programming languages, frameworks, and technical terms. Most valid technical words are already recognized.
- cspell does not conflict with Prettier or any other formatter.
- For non-Node projects, `npx cspell .` works without installing cspell as a project dependency.
- The `addWords: true` option on dictionary definitions lets cspell update the word list file when using `cspell --words-only`.
