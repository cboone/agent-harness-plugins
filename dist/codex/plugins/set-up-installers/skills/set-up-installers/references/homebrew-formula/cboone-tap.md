# `cboone/homebrew-tap` Conventions

Use `cboone/homebrew-tap` as the only cboone-specific pattern source. Do not derive conventions from abandoned taps or retired source repositories.

## Current Formula Set

As checked on 2026-05-03, `cboone/homebrew-tap` contained:

- `Formula/bopca.rb`
- `Formula/gh-problemas.rb`
- `Formula/pbcopy2.rb`
- `Formula/right-round.rb`

Refresh the live list when working on a formula:

```bash
gh api repos/cboone/homebrew-tap/contents/Formula --jq '.[].path'
```

If a local checkout of `cboone/homebrew-tap` is available, prefer reading that checkout over remote GitHub content.

## Tap Patterns

### GoReleaser-generated macOS arm64 formula

`bopca` shows a GoReleaser-generated formula with these traits:

- Generated-file header
- `desc`, `homepage`, `version`, and `license`
- Runtime dependency on `container`
- Build dependency on Go
- macOS and arm64 constraints
- Install step for the binary
- Shared config/example files under `share`
- Runtime completions generated from the executable
- Man pages installed under `man1`
- Heredoc caveats for DNS setup and config paths
- Tests covering help output and version output

When updating this kind of formula, prefer changing the upstream GoReleaser configuration that emits the formula rather than hand-editing generated output.

### GoReleaser-generated cross-platform binary formula

`gh-problemas` shows a generated formula with platform and architecture-specific release archive URLs:

- Runtime dependency on `gh`
- `on_macos` and `on_linux` blocks
- Intel and arm64 checks inside each platform block
- Per-platform `url`, `sha256`, and `def install`
- Version-output test

Use this pattern when the release process publishes separate prebuilt archives per OS and architecture.

### Manual macOS binary formula

`pbcopy2` shows a hand-written macOS-only formula:

- `depends_on :macos`
- Separate Intel and Apple Silicon release archives
- One install block that installs multiple binaries
- Version-output tests for each installed executable

Use this pattern when the release assets are prebuilt binaries and the formula does not build from source.

### HEAD-only Go source formula

`right-round` shows a pre-release formula with:

- `head "https://github.com/cboone/<name>.git", branch: "main"`
- No stable `url` or `sha256`
- `depends_on "go" => :build`
- Go source build using `std_go_args`
- Help-output test

Use this pattern only when no tagged stable release is available or the user explicitly wants a HEAD install.

## Local Conventions

- Prefer `license "MIT"` for cboone-owned MIT-licensed projects, but verify the license instead of assuming.
- Use heredoc `caveats` for setup instructions and config paths.
- Install config examples under `share` unless a formula intentionally writes user config during `post_install`.
- Use `generate_completions_from_executable` when the installed binary exposes completions.
- Install man pages with `man1.install` when release assets include them.
- Prefer a functional test when practical. Existing tap formulae often use `assert_match` against help or version output when functional tests are not practical.
- Use `depends_on :macos` for macOS-only tools and `depends_on arch: :arm64` for arm64-only tools.

## HEAD-to-Stable Migration Checklist

When replacing a HEAD-only formula with a stable formula:

1. Confirm a SemVer-style tag exists.
1. Confirm release assets are published for the intended platforms and architectures.
1. Add stable `url` and `sha256` values.
1. Preserve `head` only if users should still be able to install from the development branch.
1. Update the install block only if the release archive layout differs from the source tree.
1. Run audit, style, install, and test checks.

## Out-of-Scope Repositories

Do not use these repositories as formula convention sources:

- `cboone/homebrew-bopca`
- `cboone/homebrew-heliocron`
- `cboone/diurnal-terminal`

They are abandoned for this skill's purposes.
