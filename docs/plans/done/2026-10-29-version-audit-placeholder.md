# Version audit placeholder

Scope: [the phantom pip pin](https://github.com/cboone/agent-harness-plugins/issues/514). Base: `7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`.

Compare numeric pip releases by every numeric component, ignoring trailing zeroes. Report upgrades only and propagate comparison failures. Preserve nonnumeric PyPI version handling. No plugin content changes or version bumps are needed.

An Important defect in the small-change review activated the full local review order. Local review and validation are complete. Publication follows exact-tree tidy as logical signed commits. TOOLING merges the ready PR.

## Evidence

- Targeted Scrut: 8 cases passed, offline with verified curl, gh and jq stubs.
- Initial host failure: review incomplete; runner and children stopped, no lasting changes. Evidence: worker mailbox `review-514-blocked.tgz`.
- TOOLING relayed the ramp restart go-ahead on 2026-10-30. The restarted Nit round completed all four aspects on snapshot `24959e46e8f591d6cc97f1cdb77fa40dad518d0d`, with no lasting changes. Settings: `gpt-6.1-sol`, high effort, read-only, 872000-token window. Types inapplicable; simplify reserved for structural review.
- Structural Nit round: anti-patterns and report-only simplify clean at Nit, no edits. All four cleanup angles covered inline. Bash syntax, ShellCheck and shfmt passed on both changed scripts.
- Step 2 Important round: all four aspects completed on snapshot `6832e6987dfab7f883c940ba8307fc54355e6bf7`, with no lasting changes. No code, error-handling or comment findings. Tests found another missing boundary. Loop stopped for recurrence; TOOLING approved completing the explicit branch matrix, tests only, on 2026-10-30. No further correctness round; clean at Important.
- Trims: one read-only Codex round each for comments and prose, `gpt-6.1-sol`, low effort, 872000-token window. Took two comment rewrites and two prose rewrites; no behavior changed.
- Baseline Semgrep: disposable shared clone, merge base above, `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, explicit `p/ci` configuration with metrics off. Zero findings, zero errors or partial parsing; two applicable rules scanned three targets. Auto configuration rejected disabled metrics before scanning, so the explicit configuration was used.
- Lint-and-fix without push: passed Markdownlint, Prettier, ShellCheck, shfmt and actionlint. Formatted this record and deliberately lengthened the outer Scrut fence around the fenced template example; all eight targeted cases still passed.
- `SCRUT_JOBS=4 make test-all`: passed with exit 0; all 53 Scrut documents passed. An earlier `make -s` run suppressed nested command echoes and failed three environment-isolation snapshots. The normal-command rerun passed all 47 cases in that document without code changes. The known notify rollout document passed locally.
- Version checks: no changed plugins or required bumps. All 60 plugin directories are registered; manifest versions, optional Codex manifests and marketplace version ownership agree.

## Planted defects

| Plant                        | Instrument                  | Observed result                                | Regression coverage                      |
| ---------------------------- | --------------------------- | ---------------------------------------------- | ---------------------------------------- |
| Remove numeric upgrade gate  | Targeted version audit test | Both cases failed; restored tree passed        | Placeholder and numeric comparison cases |
| Compare major component only | Targeted version audit test | Case failed; restored tree passed              | Minor and patch upgrade case             |
| Suppress comparison failure  | Targeted version audit test | Expected exit 5 became 0; restored tree passed | Comparison failure case                  |
| Skip nonnumeric releases     | Targeted version audit test | Case failed; restored tree passed              | Nonnumeric fallback case                 |
| Report empty lookup as drift | Targeted version audit test | Unexpected drift row; restored tree passed     | Empty lookup case                        |

## Findings ledger

| Reviewer label                                                               | Assessed severity                                                               | Take or record                                                                                                                         | Review again                                          |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| errors: important, Checked commands, comparison errors treated as no upgrade | Important: weekly workflow could close a drift issue after a comparison failure | Take: separate comparison output from command status; propagate failure                                                                | Yes: behavior changed; next step 2 round at Important |
| tests: suggestion, Behavioral coverage omits minor and patch upgrades        | Nit: coverage gap for the new numeric comparison                                | Take: component and patch upgrade expectations                                                                                         | No for test edits alone                               |
| tests: suggestion, Behavioral coverage omits nonnumeric PyPI fallback        | Nit: new numeric branch lacked fallback coverage                                | Take under TOOLING recurrence call: complete numeric newer/equal/older, major/minor/patch, nonnumeric, empty-lookup and failure matrix | No: tests only; clean at Important                    |
