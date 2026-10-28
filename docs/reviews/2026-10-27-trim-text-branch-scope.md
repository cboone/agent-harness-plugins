# Trim-text branch scope

Default invocation offers PR body versus branch changes when a matching PR exists, and selects branch changes otherwise. Explicit branch/base selection uses the appropriate merge base and limits trimming to changed prose units.

Issue: <https://github.com/cboone/agent-harness-plugins/issues/614>.

## Review

Standalone read-only gpt-6.1-sol reviews used high effort and an 872000-token window. Both measured review scopes stayed unchanged, with no lasting changes found.

| Reviewer's label                                        | Our severity                                        | Take or record                                                  | Review again                                                         |
| ------------------------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------- |
| important: scope expectations not exercised by any test | Important: fixtures alone cannot detect regressions | Took; committed the live evaluation runner and five scope cases | Tests-only fix; general Nit loop ended: fixes changed no behavior    |
| suggestion: redundant per-change assertion              | Nit: duplicate check adds no validation             | Took; removed it, retaining independent unit/count guards       | Tests-only fix; structural Nit loop ended: fixes changed no behavior |

The general round covered code, errors, tests and comments; types coverage was added for the runner's schemas and found none. Full order followed the Important finding. Anti-patterns found none; report-only simplify found the Nit above. Comment trim proposed none. Prose trim applied two README edits; its ambiguous rewrite of the default-scope conjunction was rejected. Trims used low effort with the same model/window.

## Behavioral evaluation

[Run the opt-in evaluator](../../tests/evals/README.md). It consumes committed scenario data and calls the existing Codex CLI; it is not part of CI.

All five scope cases and the real Git prose fixture passed. Expectations were withheld from model inputs. The prose check retained the sample requirement, unchanged paragraph, link and code fence without editing the fixture.

| Planted defect                  | Instrument                   | Observed                                            | Durable coverage        |
| ------------------------------- | ---------------------------- | --------------------------------------------------- | ----------------------- |
| Restore old scope rules         | Committed scope evaluator    | Failed branch selection                             | Five scope states       |
| Allow whole-file prose trimming | Committed Git evaluator      | Rejected a proposed edit to the unchanged paragraph | Changed-unit guard      |
| Remove unit assertion           | Prose judge with bad capture | Count assertion still failed                        | Independent count guard |
| Remove count assertion          | Prose judge with bad capture | Unit assertion still failed                         | Independent unit guard  |

All plants were restored; the restored judges accepted the passing captures. An initial legacy probe returned no cases and was inconclusive. The strengthened runner requires complete case results. An initially overstrict automatic-selection dialog assertion was corrected; actual scope/base selection was already correct.

## Checks

Build and version audit passed: trim-text 1.1.2 to 1.2.0, with marketplace coverage and manifest ownership clear. The configured Semgrep baseline scan in a disposable shared clone returned zero new findings and no errors; its scanned paths did not include the opt-in evaluator.

The initial parallel full suite had the known launch-workmux failure and one notification-tier failure. The unchanged notification-tier document passed its isolated rerun and the full serial rerun. The serial run passed 31 of 32 documents; only unchanged launch-workmux.md failed, matching the accepted local exception tracked in <https://github.com/cboone/agent-harness-plugins/issues/439>, <https://github.com/cboone/agent-harness-plugins/issues/397> and <https://github.com/cboone/agent-harness-plugins/issues/435>. Green PR CI remains required.
