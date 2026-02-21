# Stylelint

Linter for CSS, SCSS, and Less. Catches errors, enforces conventions, and supports auto-fix for many rules.

## When to Offer

When any CSS, SCSS, or Less files are detected in the project (`*.css`, `*.scss`, `*.less`).

## Install

### CSS

```bash
# npm
npm install -D stylelint stylelint-config-standard

# yarn
yarn add -D stylelint stylelint-config-standard

# pnpm
pnpm add -D stylelint stylelint-config-standard

# bun
bun add -D stylelint stylelint-config-standard
```

### SCSS

```bash
# npm
npm install -D stylelint stylelint-config-standard-scss

# yarn
yarn add -D stylelint stylelint-config-standard-scss

# pnpm
pnpm add -D stylelint stylelint-config-standard-scss

# bun
bun add -D stylelint stylelint-config-standard-scss
```

## Config

### CSS (.stylelintrc.json)

```json
{
  "extends": ["stylelint-config-standard"]
}
```

### SCSS (.stylelintrc.json)

```json
{
  "extends": ["stylelint-config-standard-scss"]
}
```

## Commands

```bash
# Lint
npx stylelint "**/*.css"

# Lint with auto-fix
npx stylelint --fix "**/*.css"

# SCSS variant
npx stylelint "**/*.scss"
```

## package.json Scripts

```json
{
  "scripts": {
    "lint:css": "stylelint \"**/*.css\"",
    "lint:css:fix": "stylelint --fix \"**/*.css\""
  }
}
```

## Notes

- `stylelint-config-standard` extends `stylelint-config-recommended` and enforces common CSS conventions.
- The SCSS config (`stylelint-config-standard-scss`) replaces the base config entirely. Do not use both together.
- Stylelint integrates with Prettier via `stylelint-config-prettier` (if needed to avoid conflicts), but this is rarely necessary since Prettier and Stylelint target different aspects of CSS.
- Stylelint auto-fix resolves formatting issues (indentation, empty lines, shorthand properties) but not logical errors.
