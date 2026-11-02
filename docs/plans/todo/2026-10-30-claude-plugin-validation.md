# Claude plugin validation in CI

Run Claude Code's schema validator beside the repository's convention validator for [issue 480](https://github.com/cboone/agent-harness-plugins/issues/480). TOOLING owns merging; no live configuration changes are included.

## Evidence and prior art

- Installed Claude Code 2.1.314 passed marketplace and every plugin validation under `env -i` with a newly created HOME, no credentials and only system PATH. No authentication is required. README installation advice is informational.
- Anthropic's [community validation action](https://github.com/anthropics/claude-plugins-community/blob/main/.github/actions/validate-plugins/action.yml) combines CLI schema checks with catalog invariants and validates plugin folders separately. Its version input supports pinning, but defaults to latest. Retain the two layers and pin deliberately; its external-source cloning and retry machinery are unnecessary here.
- The community [claude-code-guide check script](https://github.com/HermeticOrmus/claude-code-guide/blob/master/scripts/check.sh) checks both marketplace and individual plugin sources. Adopt that coverage, without its installation tests or other harness dependencies. Its advertised workflow path returned 404 during inspection.
- Extend `make validate` and the existing CI validation job; keep `bin/validate-plugins` untouched to avoid issue 518. Coordinate merge order with PRs 698 through 701 and issue 518 through TOOLING.

## Implementation

1. Add `bin/validate-claude-plugins`: require installed Claude Code 2.1.314 or newer, validate the marketplace and every canonical plugin manifest directory, and propagate failures. Never install locally.
1. Install exact npm package version 2.1.314 in the CI validation job using a user prefix; keep existing SHA-pinned actions. Add the helper to `make validate` and document the requirement.
1. Add Scrut coverage through the real Make target with committed CLI stubs, isolated PATH and fixture catalog: missing CLI, old CLI, successful coverage, marketplace failure and plugin failure. Plant suppressed failures and removed coverage to verify that the checks detect regressions.

## Validation and delivery

Run affected Scrut documents during iteration. Use the full local review order because the implementation and tests exceed the small-change path: structural and report-only simplify, focused aspects, trims, Semgrep baseline in a disposable shared clone, final lint, signed exact-tree tidy. Record findings and plants in a review ledger. Run `make test-all` once before push, at `SCRUT_JOBS=2`, under the shared full-suite directory lock with trap cleanup. Disclose the known baseline fixture failures. Run check-versions; repository-only tooling changes need no plugin bump unless plugin content changes. Push, open a ready PR and report by mailbox. Stop for authentication, broad plugin repairs, recurring review defects or other process gates.
