---
name: scaffold-rust-cli
description: >-
  Scaffold a complete Rust CLI project with Cargo, cargo-deny, cargo-nextest,
  git-cliff, GitHub Actions CI/CD, and Makefile.
---

# Scaffold Rust CLI

Generate the full boilerplate for a new Rust CLI project.

## Workflow

### 1. Gather Project Information

If the user provided a project name in their request, use it as the project name and skip asking for it. Still ask for the remaining parameters unless already provided in the user's initial request.

Ask the user for these parameters:

- **Project name** -- kebab-case, used as the crate name, binary name, and directory name (e.g., `my-tool`)
- **Short description** -- one sentence, used in `Cargo.toml` and README
- **Include clap?** -- whether to add clap for CLI argument parsing (adds `clap` dependency with `derive` feature and generates a skeleton with argument structs)
- **macOS-only project?** -- whether this project targets only macOS (affects CI runner selection and release workflow targets). Default: no (cross-platform).

If the user already provided some or all of these in their initial request, do not re-ask. Derive what you can from context.

### 2. Detect User Identity

Detect the user's GitHub username and full name for use in templates:

```bash
# GitHub username (for repository URLs, Homebrew tap)
gh api user -q .login
```

```bash
# Full name (for LICENSE copyright, Cargo.toml authors)
git config user.name
```

If either command fails or produces no output, ask the user to provide the value. Use the GitHub username wherever templates reference `GITHUB-USERNAME` and the full name wherever they reference `COPYRIGHT-HOLDER`.

### 3. Verify the Target Directory

The project should be scaffolded in a directory named after the project. If the current directory is already named after the project and is empty (or nearly empty), use it. Otherwise, create a subdirectory.

If the directory already contains Rust files (`Cargo.toml`, `src/`), warn the user before proceeding.

### 4. Initialize Git

Skip if already inside a git repository.

```bash
git init
```

### 5. Generate Cargo.toml

Read `./references/cargo-toml.md` for the `Cargo.toml` template and create `Cargo.toml` from it.

- Replace `PROJECT-NAME` with the project name
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username
- Replace `COPYRIGHT-HOLDER` with the detected full name

If clap was selected, add `clap = { version = "4", features = ["derive"] }` to the `[dependencies]` section.

### 6. Generate src/main.rs

Choose the template based on the clap parameter:

- **Without clap**: read `./references/main-rs.md`
- **With clap**: read `./references/main-rs-with-clap.md`

Replace in the with-clap template:

- `PROJECT-NAME` with the project name
- `PROJECT-DESCRIPTION` with the short description

### 7. Generate rust-toolchain.toml

Read `./references/rust-toolchain.md` for the template and create `rust-toolchain.toml` from it.

No replacements needed.

### 8. Generate rustfmt.toml

Read `./references/rustfmt.md` for the template and create `rustfmt.toml` from it.

No replacements needed.

### 9. Generate deny.toml

Read `./references/deny.md` for the template and create `deny.toml` from it.

No replacements needed.

### 10. Generate typos.toml

Read `./references/typos.md` for the template and create `typos.toml` from it.

- Replace `PROJECT-NAME` with the project name

### 11. Generate cliff.toml

Read `./references/cliff.md` for the template and create `cliff.toml` from it.

No replacements needed.

### 12. Generate Makefile

Read `./references/makefile.md` for the template and create `Makefile` from it.

No replacements needed.

### 13. Generate .gitignore

Read `./references/gitignore.md` for the template and create `.gitignore` from it.

No replacements needed.

If a `.gitignore` already exists, merge the template entries into it rather than overwriting.

### 14. Generate CI Workflow

Choose the appropriate CI template:

- **Cross-platform (default)**: read `./references/ci-workflow.md`
- **macOS-only**: read `./references/ci-workflow-macos-only.md`

Create `.github/workflows/ci.yml` from the chosen template. No replacements needed (the workflow is project-name-independent).

### 15. Generate Release Workflow

Choose the appropriate release template:

- **Cross-platform (default)**: read `./references/release-workflow.md`
- **macOS-only**: read `./references/release-workflow-macos-only.md`

Create `.github/workflows/release.yml` from the chosen template.

- Replace `PROJECT-NAME` with the project name

### 16. Generate LICENSE

Read `./references/license.md` for the LICENSE template and create `LICENSE` from it.

- Replace `YEAR` with the current year (run `date +%Y` to get it)
- Replace `COPYRIGHT-HOLDER` with the detected full name

### 17. Generate README.md

Read `./references/readme.md` for the README template and create `README.md` from it.

- Replace `PROJECT-NAME` with the project name (kebab-case)
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username

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

### 19. Create Directory Stubs

Create stub directories for the standard project layout:

```bash
# plans directory
mkdir -p docs/plans/todo docs/plans/done
touch docs/plans/todo/.gitkeep docs/plans/done/.gitkeep

# tests directory
mkdir -p tests
touch tests/.gitkeep
```

### 20. Verify the Build

Run a quick build to confirm everything compiles:

```bash
cargo build
```

If the build fails, diagnose and fix the issue before continuing.

### 21. Create Initial Commit

Stage all generated files and create the initial commit:

```bash
git add -A
git commit -S -m "feat: scaffold Rust CLI project"
```

### 22. Update Copilot Instructions

If `.github/copilot-instructions.md` exists (created by the scaffold-new-repo skill when running in the bootstrap flow, or already present in an existing repo), append the following entries to the PR review section. Before appending each entry, check whether the bold key text already exists in the file; skip entries that are already present.

To locate the PR review section: look for an existing heading whose text includes "PR Review" or "Code Review" (e.g., `## PR Review`, `## Code Review`, `## PR Review Checklist (CRITICAL)`). If no matching heading exists, append a new `## PR Review` section at the end of the file and place the entries there.

- **Rust edition 2024 is intentional**: This project uses Rust edition 2024 in both `Cargo.toml` and `rustfmt.toml`. Do not suggest downgrading to edition 2021.
- **cargo-deny and typos are CI-verified**: The CI workflow includes `cargo deny check` and `typos` jobs. Do not suggest removing these checks or marking them as optional.

If `.github/copilot-instructions.md` does not exist, skip this step.

### 23. Summary

Print a summary of what was created:

- List every file and directory generated
- Note which optional features were included (clap, macOS-only)
- Remind the user to:
  - Run `make help` to see available Makefile targets
  - Run the add-community-files skill to add CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and .github/PULL_REQUEST_TEMPLATE.md
  - Run the set-up-installers skill when ready to set up a Homebrew formula and shell install script
  - Tag a release with `git tag v0.1.0 && git push origin v0.1.0` to trigger the release workflow
  - Use `make changelog` (requires `git-cliff`) to generate the changelog from conventional commits

## Error Handling

- If `cargo build` fails, check that Rust is installed and on the PATH. Verify the edition is supported by the installed toolchain.
- If `cargo build` fails for clap, check that the dependency specification is correct in `Cargo.toml`
- If the target directory already contains Rust files (`Cargo.toml`, `src/`), ask the user before overwriting
- If `git init` fails, continue generating files but warn the user
- If the build verification fails, show the error and attempt to fix it before continuing

## Reference Templates

- `./references/cargo-toml.md` -- `Cargo.toml` template
- `./references/main-rs.md` -- `src/main.rs` without clap
- `./references/main-rs-with-clap.md` -- `src/main.rs` with clap
- `./references/rust-toolchain.md` -- `rust-toolchain.toml`
- `./references/rustfmt.md` -- `rustfmt.toml`
- `./references/deny.md` -- `deny.toml`
- `./references/typos.md` -- `typos.toml`
- `./references/cliff.md` -- `cliff.toml`
- `./references/makefile.md` -- Makefile template
- `./references/gitignore.md` -- `.gitignore` template
- `./references/ci-workflow.md` -- cross-platform CI workflow
- `./references/ci-workflow-macos-only.md` -- macOS-only CI workflow
- `./references/release-workflow.md` -- cross-platform release workflow
- `./references/release-workflow-macos-only.md` -- macOS-only release workflow
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
