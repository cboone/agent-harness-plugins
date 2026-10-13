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

Implementation is complete. `review-until-clean` is version `3.1.0`; the shared-helper update bumps `review-pr-with-codex` to `2.0.2`.

### Instruction-path checks

These checks trace the skill and reference rules; they are not live reviewer runs.

| Scenario                                                 | Specified result                                                            |
| -------------------------------------------------------- | --------------------------------------------------------------------------- |
| Critical, Important and Nit findings at `critical`       | Only Critical enters the fixer queue; all findings are printed and recorded |
| Only Important, Nit or unlabelled findings at `critical` | `clean at critical`; lower findings remain open                             |
| Critical and Important findings at default `important`   | Both block and enter the fixer queue                                        |
| Any severity at `nit`                                    | All three levels block and enter the fixer queue                            |
| Carried Critical decline at `critical`                   | `clean-with-declines at critical` when no blocking findings remain          |
| Only lower-severity declines at `critical`               | `clean at critical`                                                         |
| Confirmation with lower-severity findings                | Both rounds apply the same threshold and snapshot rules                     |
| Report-only with blocking Critical findings              | Findings are reported without a fix pass                                    |
| Failed review, edit round or invalid snapshot            | Threshold cannot make the round clean                                       |

### Automated checks

- `make build`: passed; generated Codex mirrors committed with the canonical sources.
- `make lint`: passed. Subsequent README and plan edits passed scoped Markdown lint and Prettier checks.
- `make validate`: passed after the final build.
- `make test-scrut`: 23 of 27 documents passed on the initial run. Codex-aspects, notifications and launch-workmux failed because the sandbox denied process-list access; all three passed when rerun with that access. The catalog suite detected mirror drift while README wording was being edited during the initial run; it passed after the final build. Every document has a passing final result.
- Changed review-scope suite: 43 cases passed, including the three-level severity schema and byte-identical shared helpers.
- `git diff --check`: passed.

No live reviewer loop was run. Threshold behavior is specified by agent instructions; the executable regression checks cover the schema, helpers and repository validators.
