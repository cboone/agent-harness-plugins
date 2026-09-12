---
name: scaffold-zig-cli
description: >-
  Scaffold a complete Zig CLI project with build.zig, build.zig.zon,
  cross-compiled releases, GitHub Actions CI/CD, and Makefile.
---

# Scaffold Zig CLI

Generate the full boilerplate for a new Zig CLI project.

## Workflow

### 1. Gather Project Information

If the user provided a project name in their request, use it as the project name and skip asking for it. Still ask for the remaining parameters unless already provided in the user's initial request.

Ask the user for these parameters:

- **Project name** -- kebab-case, used as the binary name and directory name (e.g., `my-tool`)
- **Short description** -- one sentence, used in the README

Derive the **package name** from the project name rather than asking: replace every hyphen with an underscore (`my-tool` becomes `my_tool`). Zig rejects a hyphenated package name outright with `error: name must be a valid bare zig identifier`, and quoting it as `.@"my-tool"` does not help. Wherever templates reference `PACKAGE-NAME`, use this underscored form; wherever they reference `PROJECT-NAME`, use the kebab-case form. The binary keeps the hyphens.

If the user already provided some or all of these in their initial request, do not re-ask. Derive what you can from context.

### 2. Detect User Identity

Detect the user's GitHub username and full name for use in templates:

```bash
# GitHub username (for repository URLs, Homebrew tap)
gh api user -q .login
```

```bash
# Full name (for LICENSE copyright)
git config user.name
```

If either command fails or produces no output, ask the user to provide the value. Use the GitHub username wherever templates reference `GITHUB-USERNAME` and the full name wherever they reference `COPYRIGHT-HOLDER`.

### 3. Verify the Target Directory

The project should be scaffolded in a directory named after the project. If the current directory is already named after the project and is empty (or nearly empty), use it. Otherwise, create a subdirectory.

If the directory already contains Zig files (`build.zig`, `build.zig.zon`, `src/`), warn the user before proceeding.

### 4. Initialize Git

Skip if already inside a git repository.

```bash
git init
```

### 5. Detect the Zig Toolchain

The templates target Zig 0.16 and later. Read the installed version:

```bash
zig version
```

Normalize the output to `MAJOR.MINOR.PATCH` and use it wherever templates reference `ZIG-VERSION`. A development toolchain prints something like `0.16.0-dev.164+bc7955306`; strip the prerelease and build metadata, because `minimum_zig_version` is what CI installs and a dev build is not reproducible. If the installed version is older than `0.16.0`, stop and tell the user: 0.16 removed `std.io` and `std.fs.File` and changed `main`'s signature, so these templates do not compile on 0.15.

If `zig version` fails, Zig is not installed or not on the PATH. Ask the user to install it before continuing.

### 6. Generate build.zig.zon

Read `./references/build-zig-zon.md` for the template and create `build.zig.zon` from it.

- Replace `PACKAGE-NAME` with the underscored package name
- Replace `ZIG-VERSION` with the normalized Zig version

Leave the `.fingerprint` field out entirely. Step 21 fills it in from the compiler's own output. Never copy a fingerprint from another project: it is half of a package's globally unique identity, and reusing one claims another package's identity.

### 7. Generate build.zig

Read `./references/build-zig.md` for the template and create `build.zig` from it.

- Replace `PROJECT-NAME` with the project name (kebab-case, this is the binary name)
- Replace `PACKAGE-NAME` with the underscored package name (this is the module name)

### 8. Generate src/root.zig

Read `./references/root-zig.md` for the template and create `src/root.zig` from it.

- Replace `PROJECT-NAME` with the project name
- Replace `PACKAGE-NAME` with the underscored package name

### 9. Generate src/main.zig

Read `./references/main-zig.md` for the template and create `src/main.zig` from it.

- Replace `PROJECT-NAME` with the project name
- Replace `PACKAGE-NAME` with the underscored package name

### 10. Generate typos.toml

Read `./references/typos.md` for the template and create `typos.toml` from it.

- Replace `PROJECT-NAME` with the project name

### 11. Generate Makefile

Read `./references/makefile.md` for the template and create `Makefile` from it.

- Replace `PROJECT-NAME` with the project name

### 12. Generate .gitignore

Read `./references/gitignore.md` for the template and create `.gitignore` from it.

No replacements needed.

If a `.gitignore` already exists, merge the template entries into it rather than overwriting.

### 13. Generate .editorconfig

Read `./references/editorconfig.md` for the template and create `.editorconfig` from it.

No replacements needed.

If an `.editorconfig` already exists, merge the Zig sections into it rather than overwriting.

### 14. Generate CI Workflow

Read `./references/ci-workflow.md` for the template and create `.github/workflows/ci.yml` from it.

No replacements needed (the workflow is project-name-independent).

### 15. Generate Release Workflow

Read `./references/release-workflow.md` for the template and create `.github/workflows/release.yml` from it.

- Replace `PROJECT-NAME` with the project name

### 16. Generate LICENSE

Read `./references/license.md` for the LICENSE template and create `LICENSE` from it.

- Replace `YEAR` with the current year (run `date +%Y` to get it)
- Replace `COPYRIGHT-HOLDER` with the detected full name

Generate `LICENSE` before running any build. `build.zig.zon` lists it in `.paths`, and that list determines the package hash a downstream consumer computes.

### 17. Generate README.md

Read `./references/readme.md` for the README template and create `README.md` from it.

- Replace `PROJECT-NAME` with the project name (kebab-case)
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username
- Replace `ZIG-VERSION` with the normalized Zig version

### 18. Generate CHANGELOG.md

Create `CHANGELOG.md` with the initial changelog template:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
```

No replacements needed. The `release` skill will populate version sections and comparison links on the first release.

### 19. Seed .claude/settings.json

Add the Zig commands this project runs constantly to the tracked allowlist, so building and formatting do not prompt on every invocation.

If `.claude/settings.json` exists (the scaffold-new-repo skill creates it with an empty allowlist when running in the bootstrap flow), merge these three entries into `permissions.allow`, preserving any entries already there:

```json
["Bash(zig build*)", "Bash(zig fmt*)", "Bash(zig version)"]
```

If the file does not exist, create it:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(zig build*)", "Bash(zig fmt*)", "Bash(zig version)"],
    "deny": []
  }
}
```

`Bash(zig build*)` has no space before the asterisk on purpose, so it covers bare `zig build` as well as `zig build test` and `zig build -Dtarget=...`. These belong in the tracked `settings.json` rather than the untracked `settings.local.json`: every contributor runs the same commands, so there is nothing machine-specific about them.

### 20. Create Directory Stubs

Create stub directories for the standard project layout:

```bash
# plans directory
mkdir -p docs/plans/todo docs/plans/done
touch docs/plans/todo/.gitkeep docs/plans/done/.gitkeep

# tests directory
mkdir -p tests
touch tests/.gitkeep
```

### 21. Verify the Build and Fill In the Fingerprint

`build.zig.zon` has no `.fingerprint` yet, so the first build is expected to fail with the value to use. Run:

```bash
zig build
```

The first invocation reports the missing field and prints the value in the same message:

```text
build.zig.zon:1:2: error: missing top-level 'fingerprint' field; suggested value: 0xd7ba43a4d5bc8918
```

Take the **last** `0x` value on that line and write it into `build.zig.zon` as the `.fingerprint` field, immediately after `.version`, keeping the trailing comment:

```zig
.fingerprint = 0xd7ba43a4d5bc8918, // Changing this has security and trust implications.
```

Two diagnostics can appear here and the skill must accept either. An absent field produces `missing top-level 'fingerprint' field; suggested value: 0x...`; a field that is present but wrong produces `invalid fingerprint: 0x...; if this is a new or forked package, use this value: 0x...`. Both put the value to use last on the line. Do not compute a fingerprint, and do not reuse one from another project: the compiler is the only correct source.

Then confirm the project builds, tests and formats cleanly:

```bash
zig build
zig build test
zig build fmt-check
```

All three must succeed before continuing. The comment on the fingerprint line is deliberate: it makes any later change to the field visible in code review.

### 22. Create Initial Commit

Stage all generated files and create the initial commit:

```bash
git add -A
git commit -S -m "feat: scaffold Zig CLI project"
```

### 23. Update Copilot Instructions

If `.github/copilot-instructions.md` exists (created by the scaffold-new-repo skill when running in the bootstrap flow, or already present in an existing repo), append the following entries to the PR review section. Before appending each entry, check whether the bold key text already exists in the file; skip entries that are already present.

To locate the PR review section: look for an existing heading whose text includes "PR Review" or "Code Review" (e.g., `## PR Review`, `## Code Review`, `## PR Review Checklist (CRITICAL)`). If no matching heading exists, append a new `## PR Review` section at the end of the file and place the entries there.

- **The fingerprint is compiler-generated**: `.fingerprint` in `build.zig.zon` was emitted by Zig for this package and is half of its globally unique identity. Do not suggest changing, regenerating, or copying it from another project.
- **`minimum_zig_version` is the only Zig version pin**: CI resolves the toolchain by reading `build.zig.zon`. Do not suggest restating the version in a workflow file.
- **Tests must not write to stdout**: `zig build test` runs the test binary with stdout wired to the build runner's IPC channel. Suggest writing into a buffer, as `src/root.zig` does, rather than printing.

If `.github/copilot-instructions.md` does not exist, skip this step.

### 24. Summary

Print a summary of what was created:

- List every file and directory generated
- Note the detected Zig version written into `minimum_zig_version`, and the fingerprint the compiler emitted
- Remind the user to:
  - Run `make help` to see available Makefile targets
  - Run `make check` before pushing, which runs the format check, the build and the tests together
  - Run the add-community-files skill to add CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and .github/PULL_REQUEST_TEMPLATE.md
  - Run the set-up-installers skill when ready to set up a Homebrew formula and shell install script
  - Run the add-scrut-cli-tests skill to add snapshot tests for the CLI
  - Tag a release with `git tag v0.1.0 && git push origin v0.1.0` to trigger the release workflow

## Error Handling

- If `zig version` fails, Zig is not installed or not on the PATH. Point the user at [ziglang.org/download](https://ziglang.org/download/) and stop.
- If the installed Zig is older than 0.16, stop. These templates use `std.Io` and the `std.process.Init` form of `main`, neither of which exists in 0.15.
- If `zig build` reports `name must be a valid bare zig identifier`, the package name in `build.zig.zon` still contains a hyphen. Replace it with an underscore; the binary name in `build.zig` keeps the hyphen.
- If `zig build` reports a missing or invalid fingerprint after step 21, the value was transcribed incorrectly. Re-read the diagnostic and take the last `0x` value on the line.
- If the target directory already contains Zig files (`build.zig`, `build.zig.zon`, `src/`), ask the user before overwriting
- If `git init` fails, continue generating files but warn the user
- If `git commit -S` fails because signing is not configured, tell the user rather than retrying without `-S`. Signing is deliberate, and dropping it is the user's call.
- If the build verification fails, show the error and attempt to fix it before continuing

## Reference Templates

- `./references/build-zig-zon.md` -- `build.zig.zon` manifest template
- `./references/build-zig.md` -- `build.zig` build script template
- `./references/root-zig.md` -- `src/root.zig` library module
- `./references/main-zig.md` -- `src/main.zig` CLI entry point
- `./references/typos.md` -- `typos.toml`
- `./references/makefile.md` -- Makefile template
- `./references/gitignore.md` -- `.gitignore` template
- `./references/editorconfig.md` -- `.editorconfig` template
- `./references/ci-workflow.md` -- CI workflow
- `./references/release-workflow.md` -- release workflow
- `./references/license.md` -- MIT license template
- `./references/readme.md` -- README template

## Refresh `cboone/gh-actions` SHAs before scaffolding

The `cboone/gh-actions` reusable-workflow refs in this skill's templates are SHA-pinned with a `# vX.Y.Z` comment that was current when the template was authored. New releases of `cboone/gh-actions` rot those SHAs. Before emitting a workflow into a user's repo, refresh both the SHA and the comment to current latest:

```bash
TAG="$(gh release view --repo cboone/gh-actions --json tagName --jq '.tagName')"
SHA="$(gh api "repos/cboone/gh-actions/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

Replace each `cboone/gh-actions/.../<workflow>.yml@<old-sha> # <old-tag>` in the emitted workflow with the new SHA and tag. Dependabot in the user's repo keeps them in sync afterwards.
