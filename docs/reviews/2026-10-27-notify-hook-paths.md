# Notification hook paths

All eight commands in the Claude and Codex hook manifests quote the notifier path. A test loads both manifests and executes each command with a plugin root containing spaces, using a local stub that sends no notifications.

Issue: <https://github.com/cboone/agent-harness-plugins/issues/643>.

## Review

Small-change path: one Nit round of review-pr-with-codex. Fresh standalone read-only Codex runs used gpt-6.1-sol, high effort and an 872000-token window. Code, tests and comments all succeeded with no findings: clean at Nit. Errors and types were inapplicable; simplify was not selected. The scope stayed unchanged, with no lasting changes found.

## Validation

Targeted Scrut passed. Build and check-versions passed: notify advanced from 4.2.0 to 4.2.1 in both manifests; marketplace coverage and version ownership are clear.

| Planted defect                   | Instrument        | Observed                                          | Coverage                 |
| -------------------------------- | ----------------- | ------------------------------------------------- | ------------------------ |
| Remove quotes in Claude manifest | Hook command test | Failed with exit 127                              | All five Claude commands |
| Remove quotes in Codex manifest  | Hook command test | Failed with exit 127 after Claude commands passed | All three Codex commands |

Both plants were restored; the test passed again.

Final formatting and lint passed. Local make test-all passed lint/validation and 31 of 32 documents; only unchanged launch-workmux.md failed. TOOLING authorized this known local exception, tracked in <https://github.com/cboone/agent-harness-plugins/issues/439>, <https://github.com/cboone/agent-harness-plugins/issues/397> and <https://github.com/cboone/agent-harness-plugins/issues/435>. Green PR CI remains required.
