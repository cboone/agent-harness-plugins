# Improve Copilot review-body handling

## Objective

Address issues #456, #458, and #459 as one review-body workflow change. Detect
all observed Copilot review-body findings, preserve stable identities for
line-less findings, report unfamiliar non-clean layouts as format drift, and
connect every disposition visibly to its originating review.

## Scope

### Parser and output contract

1. Update `resolve-copilot-threads` to support all observed
   `ccr-overview-v2` sources:
   - Nested `Previously missed` findings from #458.
   - Per-file summary-table findings from #459.
   - Existing suppressed-comment layouts.
   - Exclude `Open` thread links and `Resolved since last review` entries from
     review-body findings.
1. Normalize v2 findings:
   - Strip U+200B characters from paths.
   - Preserve path, nullable line, severity, body, and originating review URL
     and ID.
   - Expose the verdict heading separately.
   - Preserve the relevant raw section for fallback inspection.
1. Add an explicit format-drift field:
   - A non-clean v2 verdict with no parsed finding reports drift.
   - `### 🟢 Approval recommended` is the verified clean v2 verdict.
   - Existing `hasSuppressedMarker` semantics remain compatible.

### Disposition visibility

1. Update `resolve-copilot-pr-feedback` so its single terminal summary:
   - Links each body finding to its exact originating review.
   - Identifies line-less findings using review ID, normalized path, and finding
     text.
   - Names the relevant commit for fixed findings.
   - Gives evidence or rationale for incorrect, outdated, and nitpick
     dispositions.
   - Retains prior-disposition detection and same-head no-op idempotency.
   - Posts no interim comments and does not attempt unsupported replies to
     review bodies.
1. Update `monitor-pr` so terminal and escalation reports:
   - Link to the disposition summary and originating review.
   - Distinguish actionable, previously handled, and no-change findings.
   - Preserve current-head validation and existing clean-review criteria.

### Fixtures and regression coverage

1. Add sanitized fixtures for:
   - The two public `Previously missed` examples from #458.
   - The two table findings from #459, including U+200B paths and null lines.
   - A clean v2 review using `Approval recommended`.
   - A non-clean, unparseable v2 review that must report drift.
   - Mixed inline-thread and body-only metadata.
   - Resolved entries that must not be reclassified.
1. Extend scrut coverage for:
   - Parsed fields and normalized paths.
   - Nested `<details>` handling.
   - Contradictory `Findings: None` content.
   - Table findings and line-less identities.
   - Clean versus drift verdicts.
   - Stable review IDs and URLs needed by disposition summaries.
   - Unchanged legacy fixture behavior.

### Documentation, versions, and generated artifacts

1. Update the resolver README and skill workflow, plus the monitor skill and
   README.
1. Bump `resolve-copilot-pr-feedback` from `1.5.4` to `1.6.0` because the
   combined work adds parsing and reporting capabilities.
1. Bump `monitor-pr` from `1.2.0` to `1.2.1` because its reporting contract
   changes without altering its readiness model.
1. Rebuild generated mirrors with `make build`. Do not edit them directly.

## Validation

1. Run Bash syntax checks and shell linting.
1. Run the focused `resolve-copilot-threads` scrut suite.
1. Run Markdown formatting and linting.
1. Run `make validate`.
1. Run `make test-all` and observe its final result.
1. Run the repository's `check-versions` skill.

## Delivery

1. Commit this plan as a signed baseline before implementation.
1. Keep implementation changes in small logical signed commits that reference
   #456, #458, and #459 as applicable.
1. Move this plan to `docs/plans/done/` with the final implementation commit.
1. Leave all three issues labeled `in progress` until the related pull request
   merges or the effort is explicitly abandoned.
