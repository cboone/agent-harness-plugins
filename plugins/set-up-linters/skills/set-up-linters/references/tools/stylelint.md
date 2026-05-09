# Stylelint

Linter for CSS, SCSS, and Less. Catches errors, enforces conventions, and supports auto-fix for many rules.

## When to Offer

When any CSS, SCSS, or Less files are detected in the project (`*.css`, `*.scss`, `*.less`).

## Detection

Check whether the project uses Tailwind CSS by looking for `tailwindcss` or `@tailwindcss/*` in `package.json` dependencies or devDependencies, or a `tailwind.config.*` file. This determines which install and config variant to use.

## Install

### CSS with Tailwind (default)

```bash
# npm
npm install -D stylelint stylelint-config-standard @dreamsicle.io/stylelint-config-tailwindcss

# yarn
yarn add -D stylelint stylelint-config-standard @dreamsicle.io/stylelint-config-tailwindcss

# pnpm
pnpm add -D stylelint stylelint-config-standard @dreamsicle.io/stylelint-config-tailwindcss

# bun
bun add -D stylelint stylelint-config-standard @dreamsicle.io/stylelint-config-tailwindcss
```

### CSS without Tailwind

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

### CSS with Tailwind (.stylelintrc.json)

```json
{
  "extends": ["@dreamsicle.io/stylelint-config-tailwindcss", "stylelint-config-standard"],
  "rules": {
    "alpha-value-notation": null,
    "at-rule-empty-line-before": null,
    "block-no-empty": null,
    "color-function-alias-notation": null,
    "color-function-notation": null,
    "color-hex-length": null,
    "declaration-empty-line-before": null,
    "import-notation": null,
    "nesting-selector-no-missing-scoping-root": null,
    "no-descending-specificity": null,
    "no-invalid-position-declaration": null,
    "rule-empty-line-before": null,
    "selector-class-pattern": null
  }
}
```

### CSS without Tailwind (.stylelintrc.json)

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
- The Tailwind config must come before `stylelint-config-standard` in the `extends` array so that the standard config takes precedence where they overlap.
- The nullified rules in the Tailwind config handle patterns like `@import "tailwindcss"` (no `url()`), empty `@utility` blocks, Tailwind's custom class naming, and modern CSS functions like `color-mix()`.
- Stylelint auto-fix resolves formatting issues (indentation, empty lines, shorthand properties) but not logical errors.
