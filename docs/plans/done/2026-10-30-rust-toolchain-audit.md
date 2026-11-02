# Read both Rust toolchain files

Fix [issue 420](https://github.com/cboone/agent-harness-plugins/issues/420)
by selecting `rust-toolchain` when present, otherwise `rust-toolchain.toml`.
Extract a quoted TOML channel first; only the legacy filename permits a bare
single non-empty line. Keep exact-version filtering and report the selected file.

## Prior art and scope

The [rustup book](https://rust-lang.github.io/rustup/overrides.html#the-toolchain-file)
permits TOML in both files and bare toolchain names only in `rust-toolchain`.
Rustup prefers the legacy filename when both exist; TOOLING directed this audit to match
rustup's precedence, superseding the brief's `.toml`-first order. File existence decides
precedence, so an empty or moving legacy channel must not expose a shadowed pin.

Node and Ruby handle multiple source files.
Python reads only `.python-version`, Go only `go.mod`, and Zig only
`build.zig.zon`, matching the skill's stated runtime wiring. Their omission of
`.tool-versions` runtime pins is a potential sibling gap, reported to TOOLING
without expanding this change.

## Parser boundary

TOOLING directed a dependency-free whitelist for the whole selected file.
Simple TOML accepts comments, blank lines, one `[toolchain]` header and ordinary
single-line quoted string assignments, with exactly one channel declaration.
The bare legacy form permits one non-empty channel line. Other syntax produces
an `unreadable toolchain pin` row for manual review, including otherwise valid
TOML outside the whitelist. Moving channels remain skipped.

## Implementation and validation

- Add legacy fallback, retain TOML channel extraction, bump pin-everything's
  patch version, and regenerate mirrors with `make build`.
- Add Scrut cases for bare and TOML legacy pins, `.toml` pins, precedence,
  first non-empty lines, moving channels, missing files and empty files.
- Commit tests before planting defects. Measure fallback removal, broken TOML
  extraction, moving-channel acceptance and incorrect reported locations.
- Use the full local review order unless the final diff qualifies for the
  brief's small-change path. Record findings and plants in a review ledger.
- Run affected Scrut documents while iterating. Acquire the shared full-suite
  lock before the single final `SCRUT_JOBS=2 make test-all` run, releasing it
  through an exit trap. Preserve the known `review-submodule-fixture` lint failure as outside scope.
- Check versions, tidy into signed logical commits with identical trees, push
  and open a ready PR. TOOLING merges; no live configuration changes.

## Completion

Implemented both filenames, rustup precedence, moving-channel skips and visible
manual-review rows for unsupported files under TOOLING's whitelist decisions.
Thirty-four behavior cases plus shared-environment setup pass; thirteen planted
defects were detected. Structural review ended clean at Critical, focused review
clean at Important, and trims, baseline Semgrep and version checks completed.
The single full suite failed on the documented fixture baseline and known runner
flake; its branch-local reset defect was fixed and affected checks rerun.
`make validate` passes. The isolated environment rerun has only its known fixture
case failing. TOOLING receives the ready PR with those validation caveats.
