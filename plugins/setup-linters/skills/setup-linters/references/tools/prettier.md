# Prettier

Cross-language formatter for JSON, YAML, Markdown, CSS, HTML, GraphQL, and more. Even non-Node projects benefit from Prettier for formatting config files, documentation, and data files.

## Install

### Node.js Projects

```bash
# npm
npm install -D prettier

# yarn
yarn add -D prettier

# pnpm
pnpm add -D prettier

# bun
bun add -D prettier
```

### Non-Node Projects

For projects without `package.json`, run Prettier via npx or install globally:

```bash
# npx (no install)
npx prettier --write .

# Homebrew
brew install prettier
```

## Config

### .prettierrc.json

Create `.prettierrc.json` in the project root:

```json
{
  "printWidth": 10000,
  "proseWrap": "preserve",
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all"
}
```

For non-JS projects that only use Prettier for Markdown, JSON, and YAML, a minimal config works:

```json
{
  "printWidth": 10000,
  "proseWrap": "preserve",
  "tabWidth": 2
}
```

### .prettierignore

Create `.prettierignore` in the project root. Adapt to the project's build directories and generated files:

```text
# Dependencies
node_modules/

# Build output
dist/
build/
out/

# Package manager lockfiles
package-lock.json
yarn.lock
pnpm-lock.yaml
bun.lock

# Generated files
coverage/
*.min.js
*.min.css

# Go
vendor/
go.sum

# Python
.venv/
venv/
__pycache__/
*.egg-info/

# Rust
target/
Cargo.lock
```

Remove sections that do not apply to the project (e.g., remove the Go section for a Python project).

## Integration with ESLint

When using ESLint + Prettier together, install `eslint-config-prettier` to disable ESLint rules that conflict with Prettier. See `../languages/javascript.md` for the full setup.

## Prettier Plugins

For Hugo or Go template projects, `prettier-plugin-go-template` formats `*.html` template files. No other formatter handles Go template syntax.

```bash
npm install -D prettier-plugin-go-template
```

Add a parser override to `.prettierrc.json`:

```json
{
  "overrides": [{ "files": ["*.html"], "options": { "parser": "go-template" } }],
  "plugins": ["prettier-plugin-go-template"]
}
```

Install plugins as dev dependencies and Prettier auto-discovers them. Avoid `prettier-plugin-sh` and `prettier-plugin-toml` as the dedicated tools (shfmt and Taplo) are faster and more capable.

## package.json Scripts

```json
{
  "scripts": {
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

## Notes

- Prettier is opinionated by design. The config options above are the most commonly customized settings.
- `.prettierignore` follows `.gitignore` syntax.
- Prettier already ignores files listed in `.gitignore` by default, so `.prettierignore` is mainly for files that are tracked but should not be formatted (e.g., lockfiles, generated code).
- For non-JS projects, Prettier still adds value by formatting Markdown, JSON, YAML, and other config files consistently.
