# Critical review severity threshold

Issue: [#615](https://github.com/cboone/agent-harness-plugins/issues/615)

Classification: feature. Scope: one coordinated change on the current branch.

## Approved behavior

- Accept `--severity critical`, retaining `important` as the default and `nit` as the inclusive threshold.
- Map Critical, blocker and P0 to Critical. Keep high, major, important, error, P1 and "must fix" as Important, and preserve existing Nit mappings.
- Keep unlabelled findings Important. Under the Critical threshold, Important and Nit findings remain printed, recorded and open, but do not block cleanliness or enter the fixer queue.
- Record the threshold in the ledger and report `clean at critical`, preserving coverage, decline and confirmation qualifiers.
- Preserve completion, snapshot, scope, edit-round and confirmation safeguards.

## Implementation

1. Update the canonical `review-until-clean` skill, README and reviewer, ledger and stop-rule references together.
1. Extend the finding schema in both byte-identical `review-scope` copies, including the copy shipped by `review-pr-with-codex`.
1. Add schema regression coverage and verify copy equality. Check documented scenarios for mixed severities, unlabelled findings, declines, confirmation and report-only operation.
1. Bump affected plugin versions, using a minor release for the new threshold capability, and regenerate bundled output with `make build`.
1. Run relevant formatting, lint, validation and scrut checks. Create signed implementation commits referencing #615.

## Boundaries

No push or pull request is included. Issue #615 remains in progress until merge or explicit abandonment. The existing `address-review --skip` contract selects the fixer queue; no general fixer behavior changes are required.

## Validation record

Pending implementation.
