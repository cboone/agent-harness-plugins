# Consolidate CI Workflows

## Context

The project has two GitHub Actions workflows that overlap:

- **`ci.yml`** ("CI"): runs markdownlint, Prettier, ShellCheck, Actionlint, JSON validation, and plugin structure validation in a single job.
- **`lint.yml`** ("Lint"): runs markdownlint and Prettier as separate matrix jobs.

Since `ci.yml` already runs `yarn lint` (which is `yarn lint:md && yarn lint:prettier`), the `lint.yml` workflow is entirely redundant. Every PR triggers three identical lint passes for markdownlint and Prettier.

## Plan

1. **Delete** `.github/workflows/lint.yml`

That's it. `ci.yml` already covers all the checks from `lint.yml`.

## Files

- Delete: `.github/workflows/lint.yml`
- No changes to: `.github/workflows/ci.yml`

## Verification

- Run `yarn lint` locally to confirm linters still pass
- Confirm the remaining `ci.yml` workflow triggers on `push` to `main` and on `pull_request`
- Verify no other files reference `lint.yml` (workflow dispatch, badges, etc.)
