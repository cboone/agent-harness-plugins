# Preserve review validity across unrelated base advances

Authorization: issue 727 brief, CONDUCTOR records 11106b31 and 5a70e105.
Branch `fix/727-review-scope-base`; ready PR, TOOLING merges. No activation,
hooks or instruction changes. Immutable review base:
`ae3d14ef6bb8d353bf50d02d3e252c548407bffb`.

The existing shared helper and shared-reference builder implement the fix.
[Review scope validity](../../../plugins/review-pr-with-codex/skills/review-pr-with-codex/references/scope-validity.md)
is the canonical policy. Generated includes, an exact-wording include check and
parsed code guard replace independent caller policy. The one-time sweep and
all review counts are in [the ledger](../../reviews/2026-11-04-review-scope-727.md).

1. Completed: helper fix, three plugin patch bumps, generated mirrors, runtime
   and alias regressions, include/code-guard plants, guidance sweep.
2. Completed: structural loop, clean at Important after the recorded recurrence
   decisions. Pre-final plant gates and full validation passed.
3. Completed: focused correctness loop, clean at Important. Next: comment/prose
   trimming; disposable-clone Semgrep baseline; lint-and-fix without push;
   required locked full suites.
4. Tidy into logical signed commits with exact-tree comparison, verify versions,
   and generate final-tree checked-gate receipts and the JSON claim registry.
5. Push, open a ready PR closing the issue, and report the review précis and
   receipts to TOOLING. No merge from this worker.
