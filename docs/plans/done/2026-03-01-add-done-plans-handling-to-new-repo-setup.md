# Add Done Plans Handling to New Repo Setup

## Context

GitHub Copilot's automated PR reviews examine `docs/plans/done/` files and flag discrepancies between completed plan descriptions and the final code. These are false positives: done plans are historical records, not specifications. Two changes are needed: (1) scaffold the `docs/plans/done/` directory in new repos so the directory structure is ready from the start, and (2) add a Copilot instruction telling it to ignore that directory during PR reviews.

## Changes

### 1. Update `scaffold-new-repo` command

**File:** `plugins/scaffold-new-repo/commands/scaffold-new-repo.md`

**Step 10 (Create docs/plans/):** Change from creating a single `.gitkeep` to creating two:

- `docs/plans/todo/.gitkeep`
- `docs/plans/done/.gitkeep`

This replaces the current `docs/plans/.gitkeep` with subdirectory-level `.gitkeep` files, which also preserves the parent directory.

**Copilot Instructions Template (Reference section):** Add a `## PR Review` section to the template with a rule telling Copilot to ignore `docs/plans/done/`:

```markdown
## PR Review

- **Done plans are historical records**: Files in `docs/plans/done/` are completed
  plan documents preserved for reference. They may not match the final
  implementation. Do not flag discrepancies between done plan content and the
  actual codebase.
```

Also update the Notes section to reflect that the template now includes a PR Review section by default.

### 2. Update `scaffold-go-cli` command

**File:** `plugins/scaffold-go-cli/commands/scaffold-go-cli.md`

Change the docs/plans stub directory creation from:

```bash
mkdir -p docs/plans && touch docs/plans/.gitkeep
```

to:

```bash
mkdir -p docs/plans/todo docs/plans/done
touch docs/plans/todo/.gitkeep docs/plans/done/.gitkeep
```

### 3. Update `scaffold-go-library` command

**File:** `plugins/scaffold-go-library/commands/scaffold-go-library.md`

Same change as scaffold-go-cli: create `todo/` and `done/` subdirectories with `.gitkeep` files instead of a single `docs/plans/.gitkeep`.

### 4. Update this repo's own Copilot instructions

**File:** `.github/copilot-instructions.md`

Add the done plans rule to the existing PR Review section so this repo also benefits:

```markdown
- **Done plans are historical records**: Files in `docs/plans/done/` are completed plan documents preserved for reference. They may not match the final implementation. Do not flag discrepancies between done plan content and the actual codebase.
```

### 5. Version bumps

- `scaffold-new-repo`: patch bump (behavior tweak, expanded directory structure and template)
- `scaffold-go-cli`: patch bump (directory structure tweak)
- `scaffold-go-library`: patch bump (directory structure tweak)
- Mirror each in `marketplace.json`

## Verification

1. Read each modified file to confirm the directory creation steps and templates are correct
2. Run `check-versions` skill to verify version consistency
3. Grep for `docs/plans` across the codebase to confirm no references were missed
