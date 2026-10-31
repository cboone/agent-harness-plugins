# Distinct secret-scanning caller jobs

Fix [issue 432](https://github.com/cboone/agent-harness-plugins/issues/432) by naming the reusable-workflow callers `gitleaks` and `trufflehog`. Keep scanning behavior, permissions and pinned workflow revisions unchanged.

## Prior art and scope

- Read fosforo's local `.github/workflows/gitleaks.yml` and `trufflehog.yml`: both use tool names. Their comments record observing duplicate `scan / Validate inputs` rows on a real run.
- Read savera's two workflows through the GitHub contents API: both also use tool names and explain the duplicate validation rows.
- Existing multi-language templates use `go-ci` / `rust-ci` and `go-lint` / `rust-lint`; Go library callers use `ci-minimum` / `ci-stable`. Reuse the tool-name convention already demonstrated by fosforo and savera.
- Survey other reusable-workflow templates for collisions and report concerns without editing other plugins. There is no existing branch-protection guidance in this skill; add the resulting check names and migration guidance.

## Implementation and verification

1. Rename the two caller jobs, explaining the check-name prefix in one comment each. Document distinct validation and scan check rows, including updating existing required checks when adopting the templates.
2. Add scoped Scrut coverage for both emitted caller IDs. Commit the checks, prove each old `scan` ID fails its assertion, restore and rerun. Record assertion mutations too.
3. Patch-bump the plugin, regenerate with `make build`, and verify versions against current `origin/main`.
4. Run the full local review order. The small-change exception excludes secrets/security configuration, so it does not apply. Run read-only structural and simplify reviews, then aspect reviews, trims, baseline Semgrep, and lint. Record results and any stop faithfully.
5. Run the full suite once with the TOOLING directory lock and `SCRUT_JOBS=2`. Known main failures in `review-submodule-fixture` and `environment-isolation.md` remain outside scope. Tidy signed commits with exact-tree verification, push and open a ready PR if no unresolved process stop remains. Report by mailbox; TOOLING merges.

## Local completion

Implementation, plants and full review order are recorded in `docs/reviews/2026-10-30-secret-scanning-job-names.md`. The single full suite completed with the known fixture failure and an additional workmux timing failure; the conductor-requested targeted workmux rerun passed all 23 cases, opening publication. No additional template collision was identified. Publication identifiers and exact-tree tidy verification are reported in the mailbox handoff.
