# Formula Validation

Run the strongest checks available in the environment. Do not force through failures. Diagnose and adjust the formula.

## Check Prerequisites

```bash
command -v brew
brew --version
```

If Homebrew is not installed, skip local validation and report that limitation.

## Style and Audit

For a formula file in the current tap checkout:

```bash
brew style Formula/project-name.rb
brew audit --strict --online --formula Formula/project-name.rb
```

For a new formula intended for `homebrew/core`, add the stricter new-formula audit:

```bash
brew audit --new --formula Formula/project-name.rb
```

For a private tap, `--new` can still be useful, but do not treat every `homebrew/core` policy warning as a private-tap blocker unless it affects correctness, maintainability, or user safety.

## Install and Test

Install from the local formula file or the tapped formula name:

```bash
brew install --build-from-source --verbose ./Formula/project-name.rb
```

Then run the formula test:

```bash
brew test project-name
```

If the formula is already installed and Homebrew reports that state, inspect the installed version before deciding whether reinstalling is appropriate.

## GoReleaser Output

For generated formulae:

1. Validate the formula in the tap checkout.
1. If the formula is wrong because generated fields are wrong, update the source repository's GoReleaser config.
1. Regenerate the formula through the release process or document the manual tap override.

## SHA-256 Values

If checksums need to be computed for release assets:

```bash
shasum -a 256 path/to/archive.tar.gz
```

Use the checksum for the exact URL in the formula. Do not reuse checksums across platforms, architectures, or archives.

## Reporting

Always report:

- Commands run
- Passing checks
- Failing checks and the relevant error
- Skipped checks and why they were skipped
- Any remaining placeholders, especially SHA-256 placeholders
