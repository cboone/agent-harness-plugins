# Branch Review: chore/reduce-version-conflicts

Base: `main` (merge base: `9b53039`)
Commits: 4
Files changed: 44 (8 added, 34 modified, 1 deleted, 1 renamed)
Reviewed through: `c43821c2`

## Summary

This branch makes each plugin manifest the only SemVer authority, removing duplicated version fields from both marketplace manifests and deleting the catalog-state calculator. It replaces collision-prone aggregate catalog tags with immutable commit-SHA tags, refreshes release and validation guidance, and restructures repository contributor instructions into focused scoped files.

## Changes by Area

### Catalog version ownership

Marketplace entry and metadata versions are removed from the canonical and generated marketplaces. `bin/validate-plugins` now requires strict manifest SemVer and rejects duplicate marketplace version state; the obsolete state calculator and its CI environment registration are removed.

Files: `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `bin/validate-plugins`, `bin/compute-catalog-state`, `.claude/skills/check-versions/SKILL.md`, `Makefile`, `.github/workflows/ci.yml`, and `tests/scrut/repo-tooling.md`.

### Catalog release automation

The release workflow now compares plugin sources and canonical catalog metadata against the newest catalog tag, then releases changed inputs as `catalog-<full-commit-SHA>`. It retains validation, generated-mirror drift checks, idempotent tag and release checks, and serialized execution.

Files: `.github/workflows/release.yml`, `plugins/release/skills/release/SKILL.md`, `plugins/release/README.md`, and `plugins/release/skills/release/references/project-types.md`.

### Plugin guidance and generated mirrors

The create-plugin and upgrade-everything guidance now describes manifest-only versioning. The three affected plugin versions were bumped, and their Codex mirrors were regenerated.

Files: `plugins/create-plugin/`, `plugins/release/`, `plugins/upgrade-everything/`, and matching `dist/codex/plugins/` paths.

### Scoped contributor documentation

The large root contributor guide was condensed; detailed plugin-development material moved to `docs/plugin-development.md`; directory-specific instructions were added for `bin`, `docs`, `plugins`, and `tests`.

Files: `AGENTS.md`, `docs/plugin-development.md`, `bin/AGENTS.md`, `docs/AGENTS.md`, `plugins/AGENTS.md`, `tests/AGENTS.md`, and their `CLAUDE.md` symlinks.

## File Inventory

### New files

- `bin/AGENTS.md`
- `bin/CLAUDE.md`
- `docs/AGENTS.md`
- `docs/CLAUDE.md`
- `plugins/AGENTS.md`
- `plugins/CLAUDE.md`
- `tests/AGENTS.md`
- `tests/CLAUDE.md`

### Modified files

34 files were modified, including catalog manifests, release automation, the validator, published skill sources, generated Codex mirrors, root and scoped documentation, and repository tooling tests.

### Deleted files

- `bin/compute-catalog-state`

### Renamed files

- `AGENTS.md` content was moved into `docs/plugin-development.md`, then the root file was rewritten as a concise operating guide.

## Notable Changes

- Catalog tags change from an aggregate SemVer-derived identifier to `catalog-<full-commit-SHA>`. This eliminates aggregate-version collisions and preserves the exact release target.
- The catalog is no longer a duplicate version authority. Plugin manifests are now the only SemVer source, and validation enforces that boundary.
- The release workflow continues to create annotated tags and GitHub Releases only for catalog-input changes on `main`.

## Plan Compliance

No plan matched the `chore/reduce-version-conflicts` branch name, so no branch-specific plan compliance assessment applies.

## Code Quality Assessment

Overall quality: needs one documentation correction before merging.

Strengths:

- The version-ownership rule is consistently encoded in catalog data, validation, generated mirrors, published guidance, and release automation.
- The release tag is collision-free and the workflow still handles partial prior runs by independently checking the remote tag and GitHub Release.
- The validation and test changes exercise the new invariant instead of retaining tests for the removed helper.

Issues to address:

1. **Medium: an active plan retains the removed version-state workflow.** `docs/plans/todo/2026-09-14-new-skill-review-in-depth.md:220` instructs contributors to put a version in the marketplace entry, and line 222 instructs them to run `bin/compute-catalog-state`, which this branch deletes. Because this is an active plan rather than a historical `docs/plans/done/` record, it should be updated to use manifest-only versioning and omit catalog-state recomputation. Otherwise, executing the plan will produce invalid catalog data and a missing-command failure.

Suggestions:

- Add an execution-level release-workflow test if practical. The existing scrut test checks key workflow text, while a fixture-driven test of the unchanged, first-release, and changed-catalog decisions would make the intended release boundary more durable.

## Validation

- `make validate`: passed.
- `actionlint .github/workflows/release.yml .github/workflows/ci.yml`: passed.
- `git diff --check 9b530390..HEAD`: passed.
- `make test-scrut`: started but did not complete within the observed command windows, so this review does not treat it as a passing result.
