# Bash 3.2 empty lists

Fix [the empty-list compatibility issue](https://github.com/cboone/agent-harness-plugins/issues/433)
on `fix/433-bash32-empty-lists`, from `origin/main` at
`7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`.

The relayed overnight batch authorizes implementation through a PR ready
for review. TOOLING merges. Hooks, installed configuration and software
installation remain outside this workstream.

1. Inventory braced argument lists and array expansions across canonical Bash
   scripts and fixtures. Record every match and its empty-list behavior in the
   review ledger. Stop if a hook needs changing.
1. Use unbraced positional lists and guard arrays that can be empty. Preserve
   argument boundaries and existing diagnostics. Bump affected shipped plugins
   and regenerate their mirrors.
1. Add native `/bin/bash` regression tests for empty arguments and arrays, plus
   a target requiring Bash 3.2. Run the relevant suites with Bash 3.2 on PATH.
   Commit tests, plant the original defects, observe failures and restore.
1. Run the full local review order: anti-patterns and report-only simplify,
   aspect review, trims, disposable-clone Semgrep baseline, then lint and
   `make test-all`. A code-mode host negotiation timeout requires stopping.
1. Check versions, tidy into logical signed commits with an identical tree,
   push, open a ready PR and send the review précis to TOOLING.

The issue has no comments and no separate “Done when” section. Acceptance is
the brief's PR, passing local checks and conductor handoff, with the issue's
empty-list reproductions covered. Existing Bash guidance from the completed
guide fix supplies the implementation; this extends the current tooling and
Scrut coverage without adding a plugin.

Local implementation and validation are complete: 53 documents and 1,839 cases
passed the required suite, 16 cases passed the native Bash 3.2 target, four
original-defect plants were detected and restored, and local review ended
clean at Nit for introduced changes. Baseline scan coverage and pre-existing
concerns are recorded in the review ledger. Publication and exact-tree tidy
are recorded in the worker's TOOLING handoff; TOOLING merges.
