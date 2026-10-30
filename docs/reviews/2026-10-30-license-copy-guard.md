# License copy guard review

The guard adds three explicit comparisons and documents the intentional Lean
and Zig exclusions. Small-change path: one Nit round, clean at Nit.

- Base: `5205fada80635f7d9dd4a1967c94a256e60a99cb` (`origin/main` merge base).
- Reviewed snapshot: `7edf8895e7e5a98e1d41a2f4b5e23444958cf9a8`.
- Code, tests and comments aspects: all completed, exit 0, schema-valid,
  nonempty results; no findings. No severity or disposition calls needed.
- Fresh standalone Codex runs in parallel: `gpt-6.1-sol`, high effort,
  872000-token window, read-only sandbox, approvals never, web search disabled.
- No lasting changes found; snapshot unchanged after review. Errors and types
  omitted because neither changed. Simplify not selected. Small-change path
  replaces structural, trim and Semgrep steps; no additional rounds needed.
- Positive control: affected Scrut document, 26 succeeded, zero failed/skipped.
- Version audit: all 60 plugins registered, valid manifest-owned versions,
  matching Codex versions. No plugin content changed; no bump applicable.

## Drift plants

Each plant appended one line, ran the affected document and restored exact bytes.
The regression home for every row is the new MIT section in `repo-tooling.md`.

| Plant                    | Instrument        | Observed result                 | Regression home |
| ------------------------ | ----------------- | ------------------------------- | --------------- |
| Go CLI reference differs | Scrut comparisons | 3 comparisons fail, make exit 2 | All three cases |
| Go library copy differs  | Scrut comparison  | 1 comparison fails, make exit 2 | Go library case |
| New repo copy differs    | Scrut comparison  | 1 comparison fails, make exit 2 | New repo case   |
| Rust CLI copy differs    | Scrut comparison  | 1 comparison fails, make exit 2 | Rust CLI case   |

## Final validation

- `lint-and-fix --no-push`: Markdown, Prettier, ShellCheck, shfmt and actionlint
  passed. Known operand-contract findings in `review-submodule-fixture` remain.
- Locked foreground `SCRUT_JOBS=2 make test-all`: exit 2 at that known lint
  failure. Ran the skipped `make validate test-scrut` targets once, exit 2.
- Validation passed. Full Scrut: 55 of 56 documents passed; only the briefed
  `environment-isolation.md:39` operand-contract assertion failed (50/51 passed).
  `repo-tooling.md` passed 26/26; `codex-aspects.md` passed without an INT retry.
- Lock released by the runner's exit trap. No unrelated files changed.
