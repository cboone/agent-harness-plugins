# Explicit edit mode for Review Anti-Patterns

Implement [issue 624](https://github.com/cboone/agent-harness-plugins/issues/624) as a bounded review, fix and verification workflow. Read-only remains the default, including callers such as the Copilot resolver. No live configuration changes.

## Prior art and reuse

- [ESLint](https://eslint.org/docs/latest/use/command-line-interface#--fix) makes writes explicit with `--fix` and still reports problems it cannot fix. Adopt that separation.
- [Semgrep](https://docs.semgrep.dev/writing-rules/rule-defined-fix) separates suggested fixes from `--autofix` and offers `--dryrun`. Keep report-only as the preview; no second preview option is needed.
- [CodeRabbit's autofix skill](https://github.com/coderabbitai/skills/blob/main/skills/autofix/SKILL.md) consumes existing review threads and includes GitHub writes. Reuse the idea of per-finding disposition, but keep this mode local.
- The repository's `review-until-clean` models `/simplify` as an editing reviewer, with a later report round, and owns repeated rounds, snapshots and ledgers. Keep those responsibilities there. Reuse this skill's report-only workflow, checklist, schema and completion checks for both phases, and the loop plugin's scope helper for captures; do not copy them or start the loop. `address-review` defaults to confirmation and commits, so composing its whole workflow would add inappropriate side effects.

## Implementation

1. Add `--edit` to routing, argument hint, options and README. Dispatch it in the calling session before choosing a read-only reviewer. Every review phase strips `--edit` and retains the existing read-only Codex sandbox; only the calling session fixes files.
1. Add a reference describing one initial review, one supported fix pass at `--severity` (Important only, or Important and Nit; default Nit), validation, and one final report-only review. Preserve findings without changing their severity. Decline only with concrete evidence; unsafe, ambiguous, blocked or unsupported fixes remain unresolved. Respect project gates and authorization for checks; `--edit` alone authorizes no commits or remote writes.
1. Preserve selected scope and exclusions. Permit only necessary sibling sites and documentation within the repository, never symlink targets or generated sources; regenerate outputs only with authorized project tooling. Require a clean working tree before starting edit mode, with a tested bundled refusal helper that also rejects hidden index flags and every gitlink, naming its path. Recheck after capture. Preserve any subsequent concurrent work by stopping. Capture exact pre-fix contents outside the repository. Review the resulting fix diff, including uncommitted edits and new sibling sites, without letting an original committed range hide them. Stop on concurrent changes or incomplete coverage.
1. Keep the existing JSON schema unchanged: emit a final aggregate in the existing shape and put the initial findings, dispositions, validation and final review separately in its plain-text report. Unresolved or declined findings stay visible. A failed or incomplete phase cannot become clean.
1. Bump the plugin minor version, synchronize catalog descriptions and regenerate mirrors with `make build`.

TOOLING design call, 2026-10-30: keep the completeness gate strict; require a clean worktree for edit mode and refuse with commit-or-stash guidance. This replaces the draft's dirty-checkout support. The issue does not require dirty-checkout editing.

## Verification and delivery

Use the full local review order: anti-patterns plus report-only simplify, general Codex aspects, trims, baseline Semgrep, lint, exact-tree tidy. Validate scope capture and refusal with focused Scrut cases and plants. Supplement the behavioral walkthrough with the existing opt-in evaluation convention: execute edit mode over a committed range, require both an existing and a newly added sibling in actual final review inputs, and plant the original-range verification mistake. Preserve assertions, HEAD, refs and index. Run affected Scrut documents while iterating and plant a missing refusal against the new boundary test. Run `make test-all` once under the TOOLING suite lock with `SCRUT_JOBS=2`; record the brief's known baseline failures separately. Check versions, push, open a ready PR and report to TOOLING, which merges.
