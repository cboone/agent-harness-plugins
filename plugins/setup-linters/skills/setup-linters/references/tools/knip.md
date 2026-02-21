# Knip

Detects unused files, dependencies, and exports in JavaScript/TypeScript projects. Helps keep the dependency tree clean and reduces bundle size.

## When to Offer

When `package.json` is detected (JavaScript/TypeScript projects only).

## Install

```bash
# npm
npm install -D knip

# yarn
yarn add -D knip

# pnpm
pnpm add -D knip

# bun
bun add -D knip
```

## Config

Create `knip.json` in the project root:

```json
{
  "$schema": "https://unpkg.com/knip@latest/schema.json",
  "entry": ["src/index.{ts,js}"],
  "project": ["src/**/*.{ts,js}"]
}
```

Adapt the `entry` and `project` patterns to match the project structure. Common patterns:

- **Library**: `"entry": ["src/index.ts"]`
- **Next.js app**: `"entry": ["src/app/**/*.tsx", "src/pages/**/*.tsx"]`
- **CLI tool**: `"entry": ["src/cli.ts", "bin/*"]`

## Commands

```bash
# Report unused files, dependencies, and exports
npx knip

# Auto-remove unused exports (use with caution)
npx knip --fix

# Strict mode (also detect unused types)
npx knip --strict
```

## package.json Scripts

```json
{
  "scripts": {
    "knip": "knip"
  }
}
```

## Notes

- Knip has no auto-fix for unused dependencies. Run `npx knip` to identify them, then remove manually.
- `knip --fix` removes unused exports from source files. Review changes before committing.
- Knip detects unused `devDependencies`, unused `dependencies`, unused exported functions/types, and unreferenced files.
- Framework-specific plugins (Next.js, Remix, Astro, etc.) are built in and auto-detected. No manual plugin configuration is usually needed.
