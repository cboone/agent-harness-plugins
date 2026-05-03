---
name: write-homebrew-formula
description: >-
  Write or update Homebrew formulae using current Homebrew guidance and
  cboone/homebrew-tap conventions. Use when the user says "write a Homebrew
  formula", "update a formula", "add a brew formula", "review this formula",
  "convert this HEAD formula to stable", or asks for Homebrew tap packaging.
  Supports stable release formulae, HEAD-only formulae, Go source builds,
  GoReleaser-generated outputs, shell tools, caveats, services, completions,
  man pages, config files, and formula validation. Requires Homebrew for full
  local validation.
---

# Write Homebrew Formula

Write or update Homebrew formulae with official Homebrew rules and `cboone/homebrew-tap` conventions.

## Scope Boundaries

- Use `cboone/homebrew-tap` as the only cboone-specific formula pattern source.
- Do not use abandoned tap repositories such as `homebrew-bopca`, `homebrew-heliocron`, or `diurnal-terminal` for conventions or examples.
- Treat official Homebrew documentation as the source of truth for generic formula DSL behavior.
- When a formula rule may have changed recently, check today's date first and refresh the relevant official Homebrew documentation before editing.

## Workflow

### 1. Gather Context

Identify whether the user wants a new formula, an update to an existing formula, a review, or a migration from HEAD-only to stable.

Collect these facts before editing:

- Formula path and tap repository, if one exists
- Project name, marketed name, binary names, and expected formula filename
- Homepage, source URL, license, release tag or branch, and SHA-256 values
- Build type: prebuilt archive, Go source build, GoReleaser output, shell script, or mixed assets
- Platform constraints: macOS-only, Linux support, Intel, Apple Silicon, or arm64-only
- Runtime, build, and test dependencies
- Optional assets: completions, man pages, config files, service files, launchd plists, caveats, `post_install`, and `post_uninstall`
- Testable behavior that avoids credentials, destructive actions, GUI-only behavior, or user input

### 2. Load References

Read only the reference files needed for the requested formula type:

| Reference                          | Use When                                                                  |
| ---------------------------------- | ------------------------------------------------------------------------- |
| `./references/homebrew-current.md` | You need current Homebrew DSL, naming, test, service, or validation rules |
| `./references/cboone-tap.md`       | You need `cboone/homebrew-tap` conventions or current local examples      |
| `./references/patterns.md`         | You need a concrete formula template or migration shape                   |
| `./references/validation.md`       | You are ready to run Homebrew checks                                      |

### 3. Choose the Formula Shape

Select the smallest matching pattern:

- **Stable prebuilt release**: use `url`, `sha256`, optional `version`, platform or architecture blocks, and `bin.install`.
- **Stable source build**: use a release tarball plus build dependencies, such as `depends_on "go" => :build` and `std_go_args` for Go projects.
- **HEAD-only pre-release**: use `head "...git", branch: "main"` with no stable `url` or `sha256`.
- **GoReleaser-managed formula**: preserve generated structure, review for consistency, and prefer updating the release configuration upstream rather than hand-editing generated output.
- **Shell tool**: install scripts directly, add completions/config assets when present, and use service or lifecycle blocks only when the tool genuinely needs them.

### 4. Write or Update the Formula

Apply the selected pattern and keep edits scoped to the requested formula.

Required defaults:

- Formula filename is lowercase and matches the marketed formula name.
- Class name is strict CamelCase derived from the filename.
- Use `desc`, `homepage`, and `license`.
- Use `license "MIT"` only when the project license is actually MIT.
- Use stable release `url` plus `sha256` when a tagged release exists.
- Use `head` for pre-release source installs when no stable release exists.
- Use `depends_on` for build, runtime, and test dependencies so Homebrew puts build-time tools on `PATH`.
- Use `caveats` only for packaging-specific setup or non-standard paths.
- Prefer functional tests. If practical behavior cannot be tested without credentials, GUI access, services, or heavy setup, use the existing tap convention of `assert_match` on help or version output.

### 5. Validate

Run the relevant checks from `./references/validation.md`.

If Homebrew is unavailable, report which checks were skipped and why. If a check fails, diagnose the cause from the output and adjust the formula instead of forcing the command through.

### 6. Summarize

Report:

- Formula files created or changed
- Pattern selected and why
- Source URLs, tags, branches, and SHA-256 values used
- Tests and validation commands run
- Any skipped validation and the reason
- Any remaining manual work, such as waiting for a first tagged release or filling in SHA-256 values

## Error Handling

- If the project has no stable release and the user requested a stable formula, explain the gap and offer a HEAD-only formula or release checklist.
- If SHA-256 values are unavailable, leave explicit placeholders only when the user is preparing a draft and list the exact artifacts that need checksums.
- If the formula requires secrets, credentials, or private URLs, use environment variables and never write secrets into the formula.
- If current `cboone/homebrew-tap` examples conflict with official Homebrew guidance, call out the conflict and prefer official Homebrew behavior unless the user explicitly chooses the tap convention.

## Sources

- Homebrew Formula Cookbook: <https://docs.brew.sh/Formula-Cookbook>
- Homebrew acceptable formulae: <https://docs.brew.sh/Acceptable-Formulae>
- Homebrew `Formula` API: <https://docs.brew.sh/rubydoc/Formula.html>
