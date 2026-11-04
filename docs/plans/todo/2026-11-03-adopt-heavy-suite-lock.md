# Adopt the machine-wide heavy-suite lock

## Scope and design

Extend the existing Scrut entry points with the installed SL-VF heavy lock,
following the installed shared lock contract.
The local `suite-lock --help` confirms indefinite waiting and validated nested
ownership. No new lock implementation is needed. This repository has no pytest
entry point or `make test` target.

1. Add a command wrapper that uses executable
   `~/Work/sl-vf/bin/suite-lock run heavy --`, falling back to direct execution
   when absent. Allow a path override for isolated tests.
2. Wrap `make test-all` and directory Scrut runs, keeping named documents, help
   and listing direct. Move the existing document coordinator behind its public
   wrapper without changing its output, environment reset or status handling.
3. Document automatic local use, CI fallback and nested ownership. No current
   repository guidance requires a pre-suite `pgrep` check; replace that procedure
   explicitly in the testing guidance.
4. Commit isolated stub coverage for selection, fallback, nesting and command
   status/output/environment. Run only affected documents, at most two at once.
   Retain raw fix-removal plant outputs without declaring hand-run plants passed.

## Validation and handoff

Run the full local review order: structural anti-patterns plus report-only
simplify, focused Codex aspects, trims, baseline Semgrep, lint without push and
signed logical-commit tidy with identical-tree verification. Check plugin
versions; repository-only tooling needs no plugin bump. Before push, take the
TOOLING directory lock, check `pmset -g therm`, then run the full suite once via
`~/Work/sl-vf/bin/suite-lock run heavy -- env SCRUT_JOBS=2 make test-all`.
Open a ready PR and report the review précis to TOOLING by mailbox. TOOLING merges.
