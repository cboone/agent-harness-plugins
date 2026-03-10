# JavaScript/TypeScript CI Workflow

Use this template for JavaScript or TypeScript projects. Replace `PACKAGE-MANAGER`, `INSTALL-COMMAND`, and `RUN-PREFIX` with the values from the table below.

| Package Manager | `INSTALL-COMMAND`                | `RUN-PREFIX` |
| --------------- | -------------------------------- | ------------ |
| npm             | `npm ci`                         | `npx`        |
| yarn            | `yarn install --immutable`       | `yarn`       |
| pnpm            | `pnpm install --frozen-lockfile` | `pnpm exec`  |
| bun             | `bun install --frozen-lockfile`  | `bunx`       |

If the project has a `tsconfig.json`, include the optional typecheck job.

**Package manager setup variations:**

- **npm**: Use `actions/setup-node@v4` with `cache: "npm"`. No extra setup needed.
- **yarn** (detected via `.yarnrc.yml` or `yarn.lock`): Add a `run: corepack enable` step before `actions/setup-node@v4`. Use `cache: "yarn"`.
- **pnpm** (detected via `pnpm-lock.yaml`): Add a `run: corepack enable` step before `actions/setup-node@v4`. Use `cache: "pnpm"`.
- **bun** (detected via `bun.lock`): Replace the `actions/setup-node@v4` step entirely with `oven-sh/setup-bun@v2` (omit the `cache` and `node-version` parameters; Bun manages its own caching). The `actions/setup-node` `cache` option does not support Bun.

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "PACKAGE-MANAGER"

      - name: Install dependencies
        run: INSTALL-COMMAND

      - name: Run tests
        run: RUN-PREFIX jest

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "PACKAGE-MANAGER"

      - name: Install dependencies
        run: INSTALL-COMMAND

      - name: Run ESLint
        run: RUN-PREFIX eslint .

  format:
    name: Format
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "PACKAGE-MANAGER"

      - name: Install dependencies
        run: INSTALL-COMMAND

      - name: Check formatting
        run: RUN-PREFIX prettier --check .

  # Include this job only if tsconfig.json exists
  typecheck:
    name: Type check
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "PACKAGE-MANAGER"

      - name: Install dependencies
        run: INSTALL-COMMAND

      - name: Run type check
        run: RUN-PREFIX tsc --noEmit
```

## Notes

- Detect the test runner from `package.json` scripts (jest, vitest, mocha, etc.) and adjust the test command accordingly
- If `package.json` has a `test` script, use `npm test` (or equivalent) instead of calling the runner directly
- If `package.json` has `lint` or `format` scripts, prefer those over direct tool invocation
- Only include the typecheck job if `tsconfig.json` exists
- The template above shows the npm setup; see "Package manager setup variations" above for yarn, pnpm, and bun differences
- For **yarn** and **pnpm**: add `run: corepack enable` as a step before `actions/setup-node` so the correct package manager shim is available for caching and installation
- For **bun**: replace `actions/setup-node@v4` with `oven-sh/setup-bun@v2` and remove `node-version` and `cache` parameters
