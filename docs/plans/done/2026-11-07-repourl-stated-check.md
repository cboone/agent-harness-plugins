# Repository URL identity guard

Fix [the identity predicate mismatch](https://github.com/cboone/agent-harness-plugins/issues/404)
within the existing backlog comparison filter. Share the string-only URL
definition between coercion and suppression, preserving valid-input output.

Extend comparison coverage across objects, numbers and false, on either side
of omitted and explicit URLs, with unchanged and changed repository names.
Restore the old suppression predicate through checked-plant to demonstrate
the regression. Bump publish-report-board's patch version and rebuild Codex.

The complete diff exceeds the small-change limit with reproducible plant
inputs and records. Use the full review order on committed SHAs, then
lint-and-fix without pushing, signed tidy, version checks and the locked full
suite. Keep helper snapshots and checked receipts in the worker's evidence
directory. Open a ready PR and hand its receipt registry to TOOLING; no merge,
publishing, cache activation or issue closure belongs to this worker.
