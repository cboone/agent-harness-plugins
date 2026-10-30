# Gitleaks starter coverage

## Goal and scope

Fix [the starter allowlist issue](https://github.com/cboone/agent-harness-plugins/issues/537) in the template and generation instructions. Keep default rules enabled without added exclusions. Document reviewed, narrow suppressions and the separate [PR configuration trust limitation](https://github.com/cboone/gh-actions/issues/157). No workflow or live configuration changes.

## Prior art

- [Gitleaks configuration](https://github.com/gitleaks/gitleaks#configuration) documents rule-specific allowlists with content matching and AND conditions. Its lockfile examples illustrate mechanisms, not a requirement to exclude lockfiles. Use rule and content scope; omit blanket path and rule-disable examples.
- [Gitleaks ignore support](https://github.com/gitleaks/gitleaks#gitleaksignore) identifies individual findings by report fingerprint. Use this for isolated, reviewed false positives.
- [TruffleHog](https://github.com/trufflesecurity/trufflehog#usage) offers detector and result filters. The surveyed README does not prescribe blanket lockfile exclusions; verification filters are not proof that an unverified finding is harmless. Keep review as the decision point.
- [GitHub secret scanning](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-secret-scanning-alerts/resolving-alerts) resolves reviewed alerts individually. Adopt finding-level review rather than hiding entire file categories.

## Implementation and validation

1. Reduce the first TOML fence to default-rule extension only; replace broad suppression examples with reviewed finding and rule/content guidance. Update skill instructions and patch version.
2. Add a Scrut guard for the starter's exact active configuration, using only existing shell tools. Test malformed/missing starters and exclusion/default-disable mutations. Run the installed Gitleaks locally against synthetic credentials in all five lockfiles and a vendor file, including history.
3. Commit checks before manual plants; plant the original path exclusion and disabled defaults against the canonical template, record failures and restore.
4. Regenerate mirrors. Run the full structural, aspect, trim, baseline Semgrep and final lint order, check versions, and `make test-all`. Record the known unrelated submodule fixture lint failure without changing it. Tidy into signed logical commits with identical trees, push and open a ready PR. TOOLING merges.

## Outcome

Implemented the default-only starter, reviewed suppression guidance, trust-limit warning, patch version and regenerated mirrors. Runtime checks showed inherited Gitleaks 8.30.1 exclusions; TOOLING directed documenting this limit and the full-configuration alternative without building it. The literal lockfile acceptance therefore holds only where the default configuration permits scanning.

Structural review ended clean at Nit. The aspect Nit round found an Important fingerprint granularity issue, fixed in skill and reference; the next round ended clean at Important. Final trims proposed no changes. Baseline Semgrep and repository validation passed. The full Scrut run completed with 55 of 57 documents passing; the starter passed five of five cases. The known operand check fails both lint and its direct Scrut assertion; a separate unchanged runner case emitted a macOS setpgid diagnostic. TOOLING directed publication with both failures disclosed and will file the runner defect. See [the review ledger](../../reviews/2026-10-30-gitleaks-starter-allowlist.md).
