# Child-side aspect process groups

## Goal and prior art

Fix issue 715 without filtering diagnostics. `bin/run-scrut-documents` uses
Perl's core POSIX module to establish a group in the child before exec, restores
INT and QUIT, and disables inherited Bash monitor mode. Reuse that approach.
`plugins/workmux/scripts/launch-workmux` suppresses launch stderr around monitor
mode; that hides diagnostics and is unnecessary when only the child sets its
group. Keep this change within review-pr-with-codex.

## Implementation

1. Disable inherited monitor mode. Launch each aspect through a Perl exec wrapper
   that checks child-only setpgid, resets asynchronous INT/QUIT, and preserves
   the child PID across exec. Require Perl before launching.
2. During cancellation signal registered leaders as well as groups so a child
   interrupted before group setup cannot escape cleanup. Retain escalation,
   group verification, launch registration deferral and artifact retention.
3. Assert silent launch, distinct leader-owned groups and disabled monitor mode
   using committed fixtures. Plant the old monitor launch and verify rejection.
   Exercise existing TERM, INT, descendant and launch-boundary coverage.
4. Bump the plugin patch version and regenerate mirrors with `make build`.

## Validation and delivery

During iteration run touched Scrut documents, error-output-guard and
environment-isolation, at most two concurrently. Run the full local review order
against the actual origin/main merge base, record findings and plants, then run
lint, version checks and one full suite with SCRUT_JOBS=2 under the designated
full-suite lock after checking thermal status. Tidy to logical signed commits
without changing the tested tree. Push, open a ready PR and report to TOOLING;
TOOLING merges.
