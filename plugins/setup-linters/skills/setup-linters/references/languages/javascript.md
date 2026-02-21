# JavaScript / TypeScript

Two stack options for JS/TS projects. Offer the user a choice.

## Classic Stack: ESLint + Prettier

Mature ecosystem with rich plugin support. Use `eslint-config-prettier` to disable ESLint formatting rules that conflict with Prettier.

### Install

Detect the package manager from lockfiles and use the appropriate command:

```bash
# npm
npm install -D eslint prettier eslint-config-prettier

# yarn
yarn add -D eslint prettier eslint-config-prettier

# pnpm
pnpm add -D eslint prettier eslint-config-prettier

# bun
bun add -D eslint prettier eslint-config-prettier
```

For TypeScript projects, also install `typescript-eslint`:

```bash
# npm
npm install -D typescript-eslint

# yarn
yarn add -D typescript-eslint

# pnpm
pnpm add -D typescript-eslint

# bun
bun add -D typescript-eslint
```

### ESLint Config (JavaScript)

Create `eslint.config.js` (flat config format):

```js
import js from "@eslint/js";
import prettier from "eslint-config-prettier";

export default [
  js.configs.recommended,
  prettier,
  {
    rules: {
      "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
    },
  },
];
```

### ESLint Config (TypeScript)

Create `eslint.config.js` (flat config format with typescript-eslint):

```js
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import prettier from "eslint-config-prettier";

export default tseslint.config(
  js.configs.recommended,
  tseslint.configs.recommended,
  prettier,
  {
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],
    },
  },
);
```

### package.json Scripts (Classic)

```json
{
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint --fix .",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

## Modern Stack: Biome

All-in-one linter and formatter. 10-100x faster than ESLint + Prettier. Simpler config. Growing ecosystem, but fewer plugins than ESLint.

### Install

```bash
# npm
npm install -D --exact @biomejs/biome

# yarn
yarn add -D --exact @biomejs/biome

# pnpm
pnpm add -D --exact @biomejs/biome

# bun
bun add -D --exact @biomejs/biome
```

### Biome Config

Create `biome.json`:

```json
{
  "$schema": "https://biomejs.dev/schemas/2.0.0/schema.json",
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2
  }
}
```

### package.json Scripts (Biome)

```json
{
  "scripts": {
    "lint": "biome lint .",
    "format": "biome format --write .",
    "check": "biome check .",
    "check:fix": "biome check --fix ."
  }
}
```

## When to Choose Which

- **Classic (ESLint + Prettier)**: Existing ESLint plugins needed (e.g., eslint-plugin-react, eslint-plugin-vue), team already familiar with ESLint, need for highly customized rules.
- **Modern (Biome)**: New projects, speed is a priority, want simpler configuration, willing to accept a smaller plugin ecosystem.

## Notes

- ESLint flat config (`eslint.config.js`) is the current standard. Avoid the legacy `.eslintrc.*` format.
- `eslint-config-prettier` must be the last config in the array to override formatting rules.
- Biome uses `--exact` during install because its config schema is version-specific.
- Prettier config and ignore files are covered separately in `../tools/prettier.md`.
