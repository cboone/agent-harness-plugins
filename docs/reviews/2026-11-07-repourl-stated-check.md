# Repository URL identity ledger

The brief authorizes the small-change path through a ready PR for
[the identity predicate mismatch](https://github.com/cboone/agent-harness-plugins/issues/404).
No hooks, live publishing, activation or merge is in scope.

The filter shares `stated_repo_url` between coercion and suppression.
The matrix checks non-string values against omitted and explicit URLs in both
orderings, also changing the repository so redundant URL reporting is visible.

## Plant table

| Defect                           | Instrument      | Result                         | Regression                             |
| -------------------------------- | --------------- | ------------------------------ | -------------------------------------- |
| Restore the old `//` suppression | Identity matrix | See checked plant record below | `tests/fixtures/report-board-identity` |

## Helpers

- `plant-defects` 1.3.0: owned copy `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/plant-defects`;
  manifest SHA-256 `8cd8b823ea8f75c91d9457747fc0685ac85b183cd92bc0f79d301484cf0649a6`.
- `review-pr-with-codex` 2.3.5: owned copy `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/review-pr-with-codex`;
  manifest SHA-256 `a2e6ab3a740adf224f7f1b0c9a015e5e679137d6a74caf5a1b17c31e359ba441`.

## Review and checks

The complete diff includes process records and exceeds the brief's small-change
limit, so the full local review order applies. Structural review used frozen
`0007d05075fef5536d778b0313584a036172a45f`, gpt-6.1-sol, high effort and window
872000, with read-only standalone Codex and closed stdin. Prompt hashes and
completion validation are in the evidence directory.

Structural receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/structural-gate/receipt.json`.
Anti-pattern review has no findings. Simplify completed all cleanup angles
inline and proposed moving invariant fixture creation outside the inner loops.
Reviewer label: `suggestion`. Our severity: Nit, redundant test subprocesses.
Take: trivial local test cleanup. Review again: no, tests alone changed.
End state: ended: fixes changed no behavior.

The focused check gate recorded fixture ShellCheck diagnostics:
`/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/focused-check-gate/receipt.json`.
Required environment inputs now use explicit declarations. Final-tree checks
below supersede this diagnostic.

Plant receipt on the reviewed tree: `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/plant-gate/receipt.json`.

<!-- checked-plants:start -->

## Verified plants and controls

plant old-alternative-suppression: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-explicit-url: named assertion reached; red exit 1; restored; green exit 0.

plant keep-trailing-slash: named assertion reached; red exit 1; restored; green exit 0.

Evidence: `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/plant-run2/results.json`.

<!-- checked-plants:end -->

## Focused review

Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/focused-gate/receipt.json`.
Reviewed through `4556e76ce1398564c1753c6930269a5808fb82b4` with code, errors,
tests and comments, gpt-6.1-sol, high effort, window 872000. Types was skipped
because no type or schema definition changed. No lasting scope changes were
found. Simplify belongs to the preceding structural loop.

- Uncited: The plant table marks a verified regression as pending.
  Reviewer label: `suggestion`. Our severity: Nit.
  A stale process-table status does not affect shipped behavior.
  Take: Replace Pending with a reference to the generated plant record.
  Review again: no, only tests and documentation change.

- Uncited: The matrix does not independently verify preservation of explicit URLs.
  Reviewer label: `suggestion`. Our severity: Nit.
  The suppression regression is covered, but explicit URL preservation needs its own boundary coverage.
  Take: Add distinct-host URL and trailing-slash cases and plant both boundaries.
  Review again: no, only tests and documentation change.

End state: ended: fixes changed no behavior.

## Trims and baseline scan

Comment and prose trims on `a1206bbb1234bc47790b43dac7bac6ee83f421ec` used
gpt-6.1-sol, low effort, window 872000, read-only standalone Codex and closed
stdin. Both proposed no changes. Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/trim-gate/receipt.json`.

Semgrep used p/ci in the owned shared clone, with `SEMGREP_REPO_NAME` set to
`cboone/agent-harness-plugins` and `--baseline-commit` set to the merge base.
The check also rejects parse errors. Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/semgrep-gate/receipt.json`.

Expanded plant receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/plant-gate2/receipt.json`.

## Final-tree evidence

The lint-and-fix invocation uses `--no-push`. Markdownlint and Prettier are
enforced by `yarn lint`; ShellCheck, shfmt and actionlint by `make lint`;
validators by `make validate`. The documented `make format` wraps a Markdown
fixer that includes historical plans. The instruction to leave those plans
unchanged requires check-only mode for that aggregate. `make lint` is the
documented non-writing check. No required lint tool is omitted.

The initial lint gate stopped at the fixture-environment validator:
`/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/lint-gate/receipt.json`.
The new fixture now starts with the repository's shared environment reset.
The gate conservatively matches `git` inside the distinct-host sample URL;
the fixture itself invokes no Git command. No validator changes belong here.

The final gate binds lint, validation, the locked full suite, version checks,
build drift, tidy equivalence and reproducible plants to the final tree.
Its authoritative receipt is named in the handoff
claim registry at `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/precis.json`. Those external records are produced
after the final signed commits, so recording their results does not alter the
checked tree. Publication remains subject to those gates.

## Additional helper snapshots

- `review-anti-patterns` 1.2.1: `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/review-anti-patterns`; manifest SHA-256
  `a7fa1183042bb6ac53a0ffbc604908c90922f0a517df122753ec3285bb629f9b`.
- `trim-comments` 3.0.1: `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/trim-comments`; manifest SHA-256
  `1237657eb5d3c5535bc6695f39dc97a51e2876a248079500d0a3616ede11c7d8`.
- `trim-text` 1.3.1: `/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/trim-text`; manifest SHA-256
  `07248706d03ea056ca83d554ba16791b6b807c7e9ad3c626e93b345e64e45d68`.

## Heavy-suite yield and discovery contract

The initial final gate was yielded from the heavy queue at TOOLING's request
so SL-VF's waiters could run. The required full suite never acquired the lock;
this was a scheduling yield, not a test failure. The original final-gate receipt
cannot authorize publication. Yield evidence is
`/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/heavy-yield.json`.

TOOLING lifted the hold and supplied the discovery receipt contract: a suite
claim with scope `discovery`, and check argv exactly `["make","test-all"]`.
`SCRUT_JOBS` is an environment value. The heavy lock wraps the checked-gate
invocation, with ownership checks against that outer owner before and after
the suite. Waiting for the lock therefore consumes no gate check budget.

Fresh final attempts run after incorporating current origin/main and signed
tidy. A complete passing receipt and the external précis govern publication.
No production code changed after focused review.

## Full-suite compatibility inventory correction

The final-v3 run acquired the outer heavy lock and executed the full suite.
The compatibility inventory test found the new repository URL plant manifest
missing from `tests/data/checked-verdict-compatibility.json`. The failed gate is
`/Users/ctm/.local/state/codex-mailboxes/tooling/404-repourl-stated-check/evidence/final-v3-gate/receipt.json`.
This is a validation failure, distinct from the earlier yielded lock wait.

The compatibility fixture now includes baseline, red and restored-green rows
copied from the actual plant result, using the manifest's predicates and the
runner's computed verdicts. The change affects test data and this ledger only;
it requires no additional review round. A fresh final full-suite receipt is
still required before publication.
