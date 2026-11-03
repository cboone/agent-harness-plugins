# Trim moved comments and check declined proposals

Implement [the stale moved-comment fix](https://github.com/cboone/agent-harness-plugins/issues/718) in `trim-text` and its `trim-comments` alias. Leave SL-VF ledger and précis policy unchanged.

## Prior art

- [clang-tidy's TODO checker](https://clang.llvm.org/extra/clang-tidy/checks/google/readability-todo.html) checks TODO syntax and associated references. It does not establish whether a dated statement still describes current code.
- [Vale's existence checks](https://docs.vale.sh/checks/existence) identify phrases through tokens and regular expressions. Use the idea of explicit review triggers, but establish validity against code rather than phrase matching.
- The repository already shares comment trimming through `trim-text` and has an opt-in live evaluator in `tests/evals/trim-text-scopes.py`. Extend those surfaces instead of adding a second workflow or tool.

## Changes

1. Treat moved and copied text as branch-owned; only unchanged text left in place is pre-existing.
2. Before declining a proposal to remove a dated fact, warning or temporary note, check current code. Report supporting evidence, or flag an unresolved check rather than claiming the note is valid.
3. Report every declined proposal and reason, including in checked dry runs and parent continuations. Keep the alias concise and return the shared report.
4. Extend the live evaluator with a moved docstring containing an unused dated link format, a copied note, and supported and unsupported retention proposals. Check alias, direct comment and prose behavior. Plant the old policy in an owned skill copy and require the regression to fail; restore and rerun.
5. Patch-bump changed plugins, regenerate mirrors and validate versions. TOOLING approved adding `Declined` to the commit and PR callers after structural review identified the missing relay.

## Verification and handoff

Run the full local review order: anti-patterns with report-only simplify, focused Codex aspects, comment and prose trims, baseline Semgrep in a disposable clone, then lint and exact-tree tidy. Read-only review runs use `gpt-6.1-sol`, high effort and window `872000`; trims and live evaluations use low effort with the same model and window.

During iteration, run only affected Scrut documents plus `error-output-guard.md` and `environment-isolation.md`, at most two concurrently. Before pushing, check thermal status and run `make test-all` once with `SCRUT_JOBS=2` while holding `~/Work/projects/.locks/tooling-full-suite.d`; wait if occupied. Record measured results and planted defects in a branch ledger. Push, open a ready PR, and report the review précis to TOOLING by mailbox. TOOLING merges.

## Completion

Implemented all three rules and caller relay, with four plugin patch bumps and regenerated mirrors. Live cases and policy plants passed their intended positive and negative checks. Structural review finished clean at Important; the focused Nit round ended with tests-only additions. Trims, baseline Semgrep, formatting, lint and validation completed. The locked full suite passed all 76 documents and 2,220 cases. See the [review ledger](../../reviews/2026-11-02-trim-moved-comments-ledger.md) for findings, declines and limits. Publication continues through signed commit tidy and a ready PR for TOOLING.
