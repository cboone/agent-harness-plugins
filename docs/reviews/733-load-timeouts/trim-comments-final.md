# Final comments trim

Files classified:
Makefile: code-comments
bin/lib/run-scrut-documents: code-comments
plugins/plant-defects/scripts/checked-gate: code-comments
plugins/plant-defects/scripts/checked-plant: code-comments
plugins/plant-defects/scripts/checked_core.py: code-comments
tests/checked_gate_test.py: code-comments
tests/checked_plant_test.py: code-comments
tests/checked_test_diagnostics.py: code-comments
tests/checked_timeout_budget_test.py: code-comments
tests/fixtures/checked-audit-lock.py: code-comments
tests/fixtures/checked-git-delay: code-comments
tests/fixtures/checked-pipeline-launch-lock.py: code-comments
tests/fixtures/checked-plant-detached.py: code-comments
tests/fixtures/scrut-stub: code-comments
tests/run_checked_budget.py: code-comments

| Location                        | Action  | Before                                                                                                                                                 | After                                                                                                                                      |
| ------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| bin/lib/run-scrut-documents:196 | Rewrite | `# Keep the checked-runner documents out of the parallel batch. Both batches`<br>`# remain in the one owned worker group, including when interrupted.` | `# Keep checked-runner documents out of the parallel batch.`<br>`# Both batches share one owned worker group, including when interrupted.` |

Scope: eligible comments against fixed base `302c0d91a77097f1ae66e39bd996253e4bbb17d8`.

Declined proposals: none. Flagged units: none. Cut material worth moving: none.

Verification, lint, formatting and tests: not run because this is a read-only dry run. Automated comment extraction was blocked by sandbox restrictions; review used Git diffs and direct text inspection.

No files changed. No commit or external write.
