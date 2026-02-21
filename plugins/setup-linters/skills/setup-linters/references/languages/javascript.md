# JavaScript / TypeScript

## ESLint + Prettier

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

### package.json Scripts

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

## Notes

- ESLint flat config (`eslint.config.js`) is the current standard. Avoid the legacy `.eslintrc.*` format.
- `eslint-config-prettier` must be the last config in the array to override formatting rules.
- Prettier config and ignore files are covered separately in `../tools/prettier.md`.
