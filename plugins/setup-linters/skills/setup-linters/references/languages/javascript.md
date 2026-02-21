# JavaScript / TypeScript

## Tools

- **ESLint**: Configurable linter with flat config format and extensive plugin ecosystem. Uses `js.configs.all` as the base with selective overrides.
- **Prettier**: Code formatter. Configured separately in `../tools/prettier.md`.

## Framework Detection

After detecting a JavaScript or TypeScript project, check for frameworks and environments to determine which additional plugins to install:

| Marker | Framework | Additional Plugins |
| --- | --- | --- |
| `react` or `react-dom` in package.json deps | React | react, react-hooks, react-refresh, jsx-a11y |
| `next` in package.json deps, or `next.config.*` | Next.js | Same as React, plus config overrides |
| `astro` in package.json deps, or `astro.config.*` | Astro | (future: eslint-plugin-astro) |
| `svelte` in package.json deps, or `svelte.config.*` | Svelte | (future: eslint-plugin-svelte) |
| `vue` in package.json deps | Vue | (future: eslint-plugin-vue) |
| `express`, `fastify`, `koa`, or `hapi` in deps; or `server.*`, `api/`, `bin/` dirs; or `@types/node` in devDeps | Node.js | eslint-plugin-n |

## Install

Replace `npm install -D` with the project's package manager (`yarn add -D`, `pnpm add -D`, or `bun add -D`).

### Base (all JS/TS projects)

```bash
npm install -D eslint @eslint/js @eslint/json eslint-config-prettier \
  eslint-plugin-import eslint-plugin-unicorn eslint-plugin-promise \
  eslint-plugin-regexp eslint-plugin-security globals
```

### TypeScript (when tsconfig.json detected)

```bash
npm install -D typescript-eslint
```

### React (when react detected in dependencies)

```bash
npm install -D eslint-plugin-react eslint-plugin-react-hooks \
  eslint-plugin-react-refresh eslint-plugin-jsx-a11y
```

### Node.js (when server-side code detected)

```bash
npm install -D eslint-plugin-n
```

## Config

### eslint.config.js (JavaScript)

Complete base config for JavaScript projects. TypeScript, React, and Node.js additions follow.

```js
/* eslint-disable import/max-dependencies */

import js from "@eslint/js";
import json from "@eslint/json";
import prettier from "eslint-config-prettier";
import importPlugin from "eslint-plugin-import";
import promise from "eslint-plugin-promise";
import regexpPlugin from "eslint-plugin-regexp";
import security from "eslint-plugin-security";
import unicorn from "eslint-plugin-unicorn";
import globals from "globals";

const importRules = {
  "import/consistent-type-specifier-style": "error",
  "import/default": "error",
  "import/enforce-node-protocol-usage": ["error", "always"],
  "import/exports-last": "error",
  "import/first": "error",
  "import/group-exports": "error",
  "import/max-dependencies": "error",
  "import/named": "error",
  "import/namespace": "error",
  "import/newline-after-import": "error",
  "import/no-absolute-path": "error",
  "import/no-amd": "error",
  "import/no-commonjs": "error",
  "import/no-cycle": ["error", { maxDepth: 5 }],
  "import/no-default-export": "error",
  "import/no-deprecated": "error",
  "import/no-duplicates": "error",
  "import/no-dynamic-require": "error",
  "import/no-empty-named-blocks": "error",
  "import/no-extraneous-dependencies": "error",
  "import/no-import-module-exports": "error",
  "import/no-mutable-exports": "error",
  "import/no-namespace": "error",
  "import/no-relative-packages": "error",
  "import/no-restricted-paths": "error",
  "import/no-self-import": "error",
  "import/no-unassigned-import": ["error", { allow: ["**/*.css"] }],
  "import/no-unused-modules": "error",
  "import/no-useless-path-segments": "error",
  "import/no-webpack-loader-syntax": "error",
  "import/order": "error",
  "import/unambiguous": "error",
};

const jsonRules = {
  ...json.configs.recommended.rules,
  "json/sort-keys": "error",
  "json/top-level-interop": "error",
};

const promiseRules = {
  ...promise.configs["flat/recommended"].rules,
  "promise/no-multiple-resolved": "error",
  "promise/prefer-await-to-callbacks": "error",
  "promise/prefer-await-to-then": "error",
  "promise/prefer-catch": "error",
  "promise/spec-only": "error",
};

const unicornRules = {
  ...unicorn.configs.all.rules,
  "unicorn/filename-case": "off",
  "unicorn/no-array-callback-reference": "off",
  "unicorn/no-keyword-prefix": [
    "error",
    {
      checkProperties: false,
      disallowedPrefixes: ["new"],
      onlyCamelCase: true,
    },
  ],
  "unicorn/no-null": "off",
  "unicorn/no-useless-undefined": "off",
  "unicorn/prevent-abbreviations": [
    "error",
    {
      allowList: { className: true },
      checkDefaultAndNamespaceImports: true,
      checkProperties: true,
      checkShorthandImports: true,
      checkShorthandProperties: true,
      replacements: {
        args: false,
        env: false,
        params: false,
        props: false,
        ref: false,
      },
    },
  ],
};

const sharedPlugins = {
  import: importPlugin,
  promise,
  regexp: regexpPlugin,
  security,
  unicorn,
};

const sharedRules = {
  ...js.configs.all.rules,
  ...importRules,
  ...promiseRules,
  ...regexpPlugin.configs["flat/all"].rules,
  "regexp/require-unicode-sets-regexp": "off",
  ...security.configs.recommended.rules,
  ...unicornRules,
  "capitalized-comments": "off",
  complexity: ["error", { max: 25 }],
  "default-case": ["error", { commentPattern: "^no default$" }],
  eqeqeq: ["error", "smart"],
  "func-names": ["error", "as-needed"],
  "func-style": "off",
  "grouped-accessor-pairs": ["error", "getBeforeSet"],
  "id-length": ["error", { exceptions: ["_"] }],
  "init-declarations": "off",
  "logical-assignment-operators": [
    "error",
    "always",
    { enforceForIfStatements: true },
  ],
  "max-depth": ["error", { max: 6 }],
  "max-lines": [
    "error",
    { max: 500, skipBlankLines: true, skipComments: true },
  ],
  "max-lines-per-function": [
    "error",
    { max: 100, skipBlankLines: true, skipComments: true },
  ],
  "max-params": "off",
  "max-statements": "off",
  "no-continue": "off",
  "no-implicit-coercion": ["error", { allow: ["!!"] }],
  "no-inline-comments": "off",
  "no-magic-numbers": [
    "error",
    {
      ignore: [-1, 0, 1, 2],
      ignoreArrayIndexes: true,
      ignoreDefaultValues: true,
    },
  ],
  "no-plusplus": "off",
  "no-restricted-syntax": [
    "error",
    {
      message:
        "Use export { } at the end of the file instead of inline export",
      selector: "ExportNamedDeclaration[declaration]",
    },
  ],
  "no-ternary": "off",
  "no-undefined": "off",
  "no-underscore-dangle": "off",
  "no-unused-vars": [
    "error",
    {
      argsIgnorePattern: "^_",
      caughtErrorsIgnorePattern: "^_",
      varsIgnorePattern: "^_",
    },
  ],
  "no-use-before-define": [
    "error",
    { classes: true, functions: false, variables: true },
  ],
  "one-var": ["error", "never"],
  "operator-assignment": ["error", "always"],
  "prefer-destructuring": ["error", { array: false, object: true }],
  "sort-imports": [
    "error",
    { ignoreDeclarationSort: true, ignoreMemberSort: false },
  ],
};

// eslint-disable-next-line import/no-default-export -- ESLint requires default export
export default [
  {
    linterOptions: {
      reportUnusedInlineConfigs: "error",
    },
  },

  {
    ignores: [
      ".claude/**",
      ".worktrees/**",
      "dist/**",
      "node_modules/**",
    ],
  },

  // JSON (strict)
  {
    files: ["**/*.json"],
    ignores: ["package.json", "package-lock.json"],
    language: "json/json",
    plugins: { json },
    rules: { ...jsonRules },
  },

  // package.json (no sort-keys, npm field order matters)
  {
    files: ["package.json"],
    language: "json/json",
    plugins: { json },
    rules: {
      ...jsonRules,
      "json/sort-keys": "off",
    },
  },

  // JSONC (JSON with comments)
  {
    files: ["**/*.jsonc", ".vscode/*.json", "jsconfig.json"],
    language: "json/jsonc",
    languageOptions: { allowTrailingCommas: true },
    plugins: { json },
    rules: { ...jsonRules },
  },

  // JavaScript files
  {
    files: ["**/*.{js,jsx,mjs,cjs}"],
    languageOptions: {
      ecmaVersion: "latest",
      globals: { ...globals.node },
      sourceType: "module",
    },
    plugins: { ...sharedPlugins },
    rules: { ...sharedRules },
  },

  prettier,

  {
    files: ["**/*.{js,jsx,mjs,cjs}"],
    rules: {
      curly: "error",
    },
  },
];
```

### TypeScript Modifications

For TypeScript projects, make these changes to the base config:

1. Add the import:

```js
import tseslint from "typescript-eslint";
```

2. Wrap the export with `tseslint.config()`:

```js
// eslint-disable-next-line import/no-default-export -- ESLint requires default export
export default tseslint.config(
  // ... all config objects from the JavaScript version ...
);
```

3. Spread `tseslint.configs.strictTypeChecked` after the ignores block, and add parser options:

```js
  ...tseslint.configs.strictTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
```

4. Add a TypeScript-specific rule block (before the `prettier` entry):

```js
  {
    files: ["**/*.{ts,tsx,mts,cts}"],
    rules: {
      "@typescript-eslint/consistent-type-exports": "error",
      "@typescript-eslint/consistent-type-imports": [
        "error",
        { prefer: "type-imports", fixStyle: "inline-type-imports" },
      ],
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
        },
      ],
      "@typescript-eslint/no-use-before-define": [
        "error",
        { classes: true, functions: false, variables: true },
      ],
      "@typescript-eslint/no-magic-numbers": [
        "error",
        {
          ignore: [-1, 0, 1, 2],
          ignoreArrayIndexes: true,
          ignoreDefaultValues: true,
          ignoreEnums: true,
          ignoreNumericLiteralTypes: true,
          ignoreReadonlyClassProperties: true,
          ignoreTypeIndexes: true,
        },
      ],
    },
  },
```

5. Extend the JS file pattern and curly override to include TypeScript extensions:

```js
  files: ["**/*.{js,jsx,mjs,cjs,ts,tsx,mts,cts}"],
```

6. Add `tsconfig.json` to the JSONC files list:

```js
  files: ["**/*.jsonc", ".vscode/*.json", "jsconfig.json", "tsconfig.json"],
```

### React Additions

Add these imports:

```js
import jsxA11y from "eslint-plugin-jsx-a11y";
import reactPlugin from "eslint-plugin-react";
import reactHooksPlugin from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
```

Add these rule blocks:

```js
const reactRules = {
  ...reactPlugin.configs.flat.all.rules,
  "react/forbid-component-props": "off",
  "react/function-component-definition": "off",
  "react/jsx-max-depth": "off",
  "react/jsx-no-bind": "off",
  "react/jsx-no-literals": "off",
  "react/jsx-props-no-spreading": "off",
  "react/no-multi-comp": "off",
  "react/prop-types": "off",
  "react/react-in-jsx-scope": "off",

  ...reactHooksPlugin.configs.flat["recommended-latest"].rules,

  "react-refresh/only-export-components": [
    "error",
    { allowConstantExport: true },
  ],
};

const jsxA11yRules = {
  ...jsxA11y.flatConfigs.strict.rules,
  "jsx-a11y/lang": "error",
  "jsx-a11y/no-aria-hidden-on-focusable": "error",
};
```

Add this config block before the `prettier` entry. Adapt the `files` pattern to match the project's source directory:

```js
  // React files
  {
    files: ["src/**/*.{js,jsx,ts,tsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      globals: { ...globals.browser },
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      sourceType: "module",
    },
    plugins: {
      ...sharedPlugins,
      "jsx-a11y": jsxA11y,
      react: reactPlugin,
      "react-hooks": reactHooksPlugin,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...sharedRules,
      ...reactRules,
      ...jsxA11yRules,
    },
    settings: {
      react: { version: "detect" },
    },
  },
```

### Node.js Additions

Add this import:

```js
// eslint-disable-next-line id-length -- canonical plugin name
import nodePlugin from "eslint-plugin-n";
```

Add this rule block:

```js
const nodeRules = {
  ...nodePlugin.configs["flat/all"].rules,
  "n/file-extension-in-import": [
    "error",
    "always",
    { ".cjs": "never", ".js": "never", ".jsx": "never", ".mjs": "never" },
  ],
  "n/hashbang": "off",
  "n/no-process-env": "off",
  "n/no-sync": "off",
};
```

Add these config blocks before the `prettier` entry. Adapt the `files` patterns to match the project's directory structure:

```js
  // Node.js files (config, scripts, server)
  {
    files: ["*.js", "bin/**/*.js", "api/**/*.js", "server/**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      globals: { ...globals.node },
      sourceType: "module",
    },
    plugins: {
      ...sharedPlugins,
      // eslint-disable-next-line id-length -- canonical plugin name
      n: nodePlugin,
    },
    rules: {
      ...sharedRules,
      ...nodeRules,
    },
  },

  // CLI scripts (relaxed rules)
  {
    files: ["bin/**/*.js"],
    rules: {
      "n/no-process-exit": "off",
      "n/no-top-level-await": "off",
      "n/no-unpublished-import": "off",
      "no-await-in-loop": "off",
      "no-console": "off",
    },
  },
```

### Next.js Overrides

When Next.js is detected, add these overrides to allow default exports in files where Next.js requires them:

```js
  // Next.js files that require default exports
  {
    files: [
      "src/app/**/layout.{js,jsx,ts,tsx}",
      "src/app/**/page.{js,jsx,ts,tsx}",
      "src/app/**/loading.{js,jsx,ts,tsx}",
      "src/app/**/error.{js,jsx,ts,tsx}",
      "src/app/**/not-found.{js,jsx,ts,tsx}",
      "src/app/**/template.{js,jsx,ts,tsx}",
      "next.config.*",
    ],
    rules: {
      "import/no-default-export": "off",
      "no-restricted-syntax": "off",
    },
  },
```

Also add `.next/**` to the ignores array.

### Logger / Console Override

For files where `console` usage is intentional (loggers, CLI output), add after the main JS config:

```js
  {
    files: ["**/lib/logger.{js,ts}", "**/utils/logger.{js,ts}"],
    rules: {
      "no-console": "off",
    },
  },
```

## Ignore Patterns

Add to the `ignores` array based on the project:

| Framework | Additional Ignores |
| --- | --- |
| Next.js | `.next/**` |
| Astro | `.astro/**` |
| Remix | `build/**` |
| Vite | `dist/**` (already included) |
| Yarn PnP | `.pnp.cjs`, `.pnp.loader.mjs`, `.yarn/**` |
| Netlify | `.netlify/**` |

## package.json Scripts

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

- ESLint flat config (`eslint.config.js`) is the current standard. Do not use the legacy `.eslintrc.*` format.
- `eslint-config-prettier` must be the last config in the array to disable formatting rules. The `curly: "error"` override must come after prettier to re-enable it.
- `js.configs.all` enables every built-in rule. The `sharedRules` object selectively disables rules that are impractical or conflict with modern patterns: `func-style` (allow arrow functions), `no-ternary` (ternaries are idiomatic), `no-continue` (useful for early-exit), `init-declarations` (impossible with try/catch), `max-params` and `max-statements` (other limits are sufficient).
- `import/no-default-export` enforces named exports for better refactoring and tree-shaking. Disable it for files where frameworks require default exports (Next.js pages, React.lazy, ESLint config itself).
- `import/exports-last` and `no-restricted-syntax` (ExportNamedDeclaration) together enforce grouping all exports at the bottom of each file via `export { name1, name2 }`.
- `unicorn.configs.all` enables all unicorn rules. Key overrides: `no-null` (null is valid for APIs), `no-useless-undefined` (useful for consistent returns), `filename-case` (allow camelCase), `no-array-callback-reference` (allow passing functions to map/filter).
- `prevent-abbreviations` allows common short names: `args`, `env`, `params`, `props`, `ref`. Add project-specific allowances as needed.
- `sort-imports` with `ignoreDeclarationSort: true` lets `import/order` handle import statement ordering while `sort-imports` handles member sorting within destructured imports.
- `reportUnusedInlineConfigs: "error"` catches stale `eslint-disable` comments that no longer suppress any rules.
- For TypeScript, `strictTypeChecked` enables all type-aware rules including `no-unsafe-*` rules. This requires `projectService: true` for type information.
- `@typescript-eslint/consistent-type-imports` with `inline-type-imports` enforces `import { type Foo }` syntax for type-only imports.
- The TypeScript rule block re-applies custom settings (like `^_` ignore patterns) to TypeScript-specific rule versions, since `strictTypeChecked` disables the base ESLint versions and enables the `@typescript-eslint/*` replacements.
- `@typescript-eslint/no-magic-numbers` extends the base rule with TypeScript-specific ignores: `ignoreEnums`, `ignoreNumericLiteralTypes`, `ignoreReadonlyClassProperties`, `ignoreTypeIndexes`.
- React config uses `reactPlugin.configs.flat.all` with selective disables: `prop-types` (redundant with TypeScript), `react-in-jsx-scope` (not needed since React 17), `jsx-no-literals` (no i18n requirement), `forbid-component-props` and `jsx-props-no-spreading` (too restrictive for Tailwind CSS patterns).
- `jsx-a11y` uses the `strict` preset for maximum accessibility coverage.
- Node.js config uses `nodePlugin.configs["flat/all"]` with selective disables: `no-process-env` (environment variables are fine), `no-sync` (sync methods are fine for scripts), `hashbang` (not all scripts need shebangs).
- CLI script files (`bin/**`) get additional relaxations: `no-console` (CLI needs output), `no-process-exit` (CLIs use exit codes), `no-await-in-loop` (sequential processing is intentional), `no-top-level-await` (scripts are not published packages).
- Prettier config and ignore files are covered separately in `../tools/prettier.md`.
- The config file itself needs `/* eslint-disable import/max-dependencies */` at the top (many imports) and `// eslint-disable-next-line import/no-default-export` before the export (ESLint requires default export).
