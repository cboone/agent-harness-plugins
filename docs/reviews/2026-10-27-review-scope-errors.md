# Review scope error handling

Fatal merge-base failures now preserve Git's stderr, name both commits and abort with the original status. Exit 1 retains unrelated-history handling. Help and comments describe normalization, schema ownership and stability limits accurately.

Issue: <https://github.com/cboone/agent-harness-plugins/issues/605>.

## Review

The full local order applies. Fresh standalone Codex runs used read-only sandboxes, high effort and an 872000-token window on gpt-6.1-sol.

| Loop                                          | Round | Result                                                                                                  |
| --------------------------------------------- | ----- | ------------------------------------------------------------------------------------------------------- |
| Anti-patterns and report-only simplify        | Nit   | One new Nit fixed; one pre-existing Nit recorded. Simplify found none. Ended: fixes changed no behavior |
| General review: code, errors, tests, comments | Nit   | No findings; clean at Nit                                                                               |
| Comment and prose trims                       | One   | Low effort, same model/window. Shortened merge-base explanation in both copies; no prose changes        |

Types were inapplicable. Both scope comparisons found no lasting changes and unchanged snapshots.

| Reviewer's label                                           | Our severity                                      | Take or record                          | Review again      |
| ---------------------------------------------------------- | ------------------------------------------------- | --------------------------------------- | ----------------- |
| nit: nonexistent backend reference                         | Nit: misleading maintenance pointer               | Took; point both copies to reviewers.md | No; comments only |
| nit: existing test explanation says index seeded from HEAD | Nit: pre-existing prose mismatch outside this fix | Recorded; no implementation impact      | No edit           |

## Validation

Targeted Scrut: all 44 cases passed. Build and version checks passed, including forward patch bumps to both consumers and marketplace ownership.

| Planted defect                          | Instrument     | Observed                                                                | Coverage                               |
| --------------------------------------- | -------------- | ----------------------------------------------------------------------- | -------------------------------------- |
| Treat fatal status as unrelated history | Targeted Scrut | 43 passed, new fatal-error case failed; all 44 passed after restoration | Inferred and explicit fatal-error case |

Semgrep ran report-only with the merge-base baseline in a disposable shared clone: zero new findings, no errors; both helpers scanned.

Local make test-all passed lint/validation and 30 of 31 documents; only unchanged launch-workmux.md failed. TOOLING authorized this known local exception, tracked in <https://github.com/cboone/agent-harness-plugins/issues/439>, <https://github.com/cboone/agent-harness-plugins/issues/397> and <https://github.com/cboone/agent-harness-plugins/issues/435>. Green PR CI remains required.
