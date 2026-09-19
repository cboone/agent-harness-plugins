# Branch Review: fix/459-update-pr-comment-layout-again

Base: main (merge base: 046f1389)
Commits: 2
Files changed: 20 (5 added, 15 modified, 0 deleted, 0 renamed)
Reviewed through: 7b0856d2

## Summary

This branch addresses issues #456, #458, and #459 as one change to how Copilot review-body feedback is parsed and reported. `resolve-copilot-threads parse-reviews` now recognizes two `ccr-overview-v2` layouts (nested `Previously missed` findings and per-file summary-table findings), emits `verdict`, `hasFormatDrift`, `severity`, and the full `reviewBody`, and flags a non-clean v2 verdict with no parsed findings as drift. The `resolve-copilot-pr-feedback` skill now links every review-body row to its exact originating review, supports line-less findings, and requires a commit or rationale in each disposition. `monitor-pr` carries those links into its terminal and escalation reports and treats format drift as not clean.

## Changes by Area

### Review-body parser (`resolve-copilot-threads`)

Adds `normalize_path` (strips U+200B), `verdict`, `is_overview_v2`, `previously_missed_findings` (regex scan over nested `<details>`), and `table_findings` (semicolon-separated `Severity (N votes): text` items in file-summary cells). The legacy `findings` parser is renamed `suppressed_findings`, gains `severity: null`, and now runs over the whole body instead of the suppressed slice. Output gains `verdict`, `hasFormatDrift`, and `reviewBody`.

- `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`

### Resolver skill workflow and docs

Documents the new output fields, line-less findings, the `hasFormatDrift` rule, review-linked `Source` cells, a `Finding` column, and a `Disposition` column that must name the fixing commit or the no-change rationale. Step 1c identity rules now cover line-less findings.

- `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`
- `plugins/resolve-copilot-pr-feedback/README.md`

### Monitor skill workflow and docs

Adds format drift to the Copilot row of the ready criteria and to the step 7d confirmation standard, asks the resolver to return summary and review URLs, and adds those links to the terminal report and to two escalation rules.

- `plugins/monitor-pr/skills/monitor-pr/SKILL.md`
- `plugins/monitor-pr/README.md`

### Tests and fixtures

Four new v2 fixtures (previously missed, table, clean, drift) and five new scrut cases, plus a legacy-drift assertion for `hasFormatDrift`.

- `tests/data/copilot-reviews/format-d.json`
- `tests/data/copilot-reviews/format-d-clean.json`
- `tests/data/copilot-reviews/format-d-drift.json`
- `tests/data/copilot-reviews/format-d-previously-missed.json`
- `tests/scrut/resolve-copilot-threads.md`

### Versions and generated mirrors

`resolve-copilot-pr-feedback` 1.5.4 to 1.6.0; `monitor-pr` 1.2.0 to 1.2.1. Codex mirrors regenerated; `make build` on this head produces no further changes.

- `plugins/*/.claude-plugin/plugin.json` (2 files)
- `dist/codex/plugins/{monitor-pr,resolve-copilot-pr-feedback}/**` (7 files)

### Plan

- `docs/plans/done/2026-09-18-copilot-review-body-handling.md` (committed to `todo/` first, moved to `done/` in the implementation commit)

## File Inventory

- **New (5)**: `docs/plans/done/2026-09-18-copilot-review-body-handling.md`, `tests/data/copilot-reviews/format-d.json`, `tests/data/copilot-reviews/format-d-clean.json`, `tests/data/copilot-reviews/format-d-drift.json`, `tests/data/copilot-reviews/format-d-previously-missed.json`
- **Modified (15)**: 8 canonical plugin files (2 `plugin.json`, 2 `README.md`, 2 `SKILL.md`, 1 script) plus `tests/scrut/resolve-copilot-threads.md`, and 7 generated files under `dist/codex/`
- **Deleted (0)**
- **Renamed (0)** relative to the merge base

## Notable Changes

- **Output contract change in `parse-reviews` / `fetch-reviews`**: new fields `verdict`, `hasFormatDrift`, `reviewBody`, and `findings[].severity`; `findings[].line` may now be `null`. Callers that assumed every finding has a numeric line are affected; the skill text was updated accordingly.
- **Readiness semantics in `monitor-pr`**: format drift now blocks a clean Copilot axis. This is a change to the clean criteria, not only to reporting.
- **Output size**: every review now carries its complete `reviewBody`, and `fetch-reviews` returns all Copilot reviews on the PR, so output grows with review history.

## Plan Compliance

Plan: `docs/plans/done/2026-09-18-copilot-review-body-handling.md`

**Compliance verdict: partial compliance.** Every plan section has corresponding work, the scaffolding (fields, fixtures, docs, versions, mirrors) is complete, and the suite passes. But three plan intents are not met in substance: legacy layouts are not preserved unchanged, the drift signal fires on ordinary v2 reviews that have only inline threads, and the new step 1c identity rule undercuts the prior-disposition detection the plan says to retain.

**Overall progress: 15/21 items done (71%)**, 6 partially done, 0 not started.

### Parser and output contract

- **Partially done: support all observed v2 sources.** Previously missed, table findings, and Open/Resolved exclusion work on the fixtures. Two gaps:
  - Existing suppressed-comment layouts changed. `suppressed_findings` now scans `.body` instead of `$slice`, so the last finding in `format-a`, `format-b`, and `format-c` now absorbs `</details>` and, for `format-c`, the `- **Files reviewed:**` trailer. Verified by diffing base against branch output. Issue #459 requires these fixtures to "produce unchanged output."
  - Table parsing drops findings silently: an item whose text contains `;`, or a final item without a trailing `.`, does not match, and if any other finding in the review parsed, `hasFormatDrift` stays false.
- **Done: normalize v2 findings.** U+200B stripped, path/line/severity/body/URL/ID preserved, `verdict` exposed, raw content preserved (as the whole `reviewBody` rather than a relevant section; see deviations).
- **Partially done: explicit format-drift field.** The literal rule is implemented and legacy `hasSuppressedMarker` is compatible. But a v2 review whose non-clean verdict is explained entirely by `Open (N)` inline threads, the common case, reports `hasFormatDrift: true` (verified with a constructed fixture). See Code Quality issue 1.

### Disposition visibility

- **Partially done: resolver summary.** Links, line-less identities, fixing commits, no-change rationale, and the no-interim-comment rule are all specified. However, step 1c rule 1 now requires that "a prior summary links the same review," while line 235 of the same skill says Copilot re-emits the finding in every later review. A re-emitted finding in a new review can never match rule 1, so it is reprocessed rather than recorded as `Previously handled`. The plan says to retain prior-disposition detection.
- **Partially done: `monitor-pr` reporting.** Summary and review links, and the actionable / previously handled / no-change distinction, are in step 8 and the escalation rules. But the drift criterion was added only to the ready table and step 7d. Step 4's dispatch condition 6 still reads "open threads or findings", and the Dependabot section still says "left findings", so a drift-only review at the current head matches no dispatch condition and falls through to the wait loop.

### Fixtures and regression coverage

- **Done: fixtures.** Both `Previously missed` examples, both table findings with U+200B and null lines, clean v2, drift v2, mixed Open-link and body-only content (review `6000000002`), and resolved entries.
- **Partially done: scrut coverage.** Parsed fields, nested details, table findings, clean versus drift, and IDs/URLs are asserted. "Contradictory `Findings: None`" is exercised by fixture content but has no named assertion. "Unchanged legacy fixture behavior" is not asserted: existing cases project `location` or the first line of the first body, so the trailing-content regression above passes the suite.

### Documentation, versions, and generated artifacts

- **Done**: resolver README and skill, monitor skill and README updated.
- **Done**: `resolve-copilot-pr-feedback` bumped to 1.6.0.
- **Done**: `monitor-pr` bumped to 1.2.1.
- **Done**: mirrors rebuilt; `make build` is a no-op on this head.

### Validation

- **Done (6/6 by evidence)**: `make test-all` passes on this head (lint including shellcheck and shfmt, validate, 445/445 scrut cases). Whether the `check-versions` skill was run cannot be confirmed from the branch, but the resulting version state is consistent: both `plugin.json` files bumped, the catalog carries no version fields, and no `.codex-plugin/plugin.json` exists for either plugin.

### Delivery

- **Done**: plan committed first as a signed baseline (`4560f9c7`).
- **Partially done**: implementation landed as one signed commit (`7b0856d2`) spanning parser, two skills, fixtures, tests, versions, and mirrors, rather than small logical commits.
- **Done**: plan moved to `docs/plans/done/` in the final implementation commit.
- **Done**: #456, #458, and #459 still carry `in progress`.

### Deviations

- **Approach: legacy parser scope widened from slice to whole body.** Not called for by the plan and not needed by any v2 fixture (reverting to `$slice` keeps every scrut case green). Problematic: it causes the legacy regression and lets any bold `**path:N**` line anywhere in a Copilot body become a finding.
- **Approach: `reviewBody` instead of "the relevant raw section".** A superset of what the plan asked for. Reasonable, at the cost of output size.
- **Scope addition: monitor readiness criteria changed.** The plan says `monitor-pr` should "preserve existing clean-review criteria", and #456 scopes itself to "not changing the conditions for a clean Copilot assessment". Adding drift to the Copilot axis is justified by #459, but it contradicts both statements and makes the patch-level bump rationale ("without altering its readiness model") inaccurate. Reasonable in intent; the plan and the dispatch rules should be brought in line.
- **Process: single implementation commit.** Minor; the change is cohesive, but the plan asked for smaller commits.

### Fidelity concerns

- The drift rule meets the letter ("non-clean v2 verdict with no parsed finding") but not the spirit (catch unrecognized body layouts), because it does not account for findings that live in inline threads.
- "Retains prior-disposition detection" is met in structure (step 1c still exists) but weakened in effect by keying on the same review.
- #456 asks for regression checks covering "repeated findings" and "no-change dispositions". Those are prompt-level behaviors with no executable coverage; the plan narrowed this without saying so.

## Code Quality Assessment

### Verdict

**Needs more work before merging.** The design is sound and the documentation is thorough, but the parser has one high-severity false-positive and two silent-loss or regression paths in exactly the area this change exists to make reliable.

### Strengths

- The v2 parsers are gated on the `ccr-overview-v2` marker, keeping ordinary file-summary tables as negative controls.
- The `previously_missed_findings` comment explains why the regex scans the full body (nested `</details>` would truncate a slice), which is the kind of reasoning future edits need.
- `hasFormatDrift` is a single, explicit signal that subsumes the old `hasSuppressedMarker`-plus-empty rule, and every consumer in both skills was switched to it.
- The disposition requirements (commit for fixes, rationale for no-change) directly answer #456 and are applied consistently across the PR summary, the partial example, and the local audit table.
- Fixtures are sanitized reproductions of the real reports, including U+200B paths and the contradictory `Findings: None` header.

### Issues to address

1. **High: false format drift on v2 reviews with only inline threads.** `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads:509-515`. A v2 review with verdict `### 🟡 Changes recommended`, an `Open (1)` section, and no body findings yields `hasFormatDrift: true`. Because `fetch-reviews` returns every Copilot review on the PR, each such historical review keeps reporting drift, so the resolver adds a workflow failure and ends `Partial` on every run, and `monitor-pr` escalates. Suggested fix: treat `Open` entries (`#discussion_r` links under the `Open (N)` summary) as accounting for a non-clean verdict, and add a fixture for an inline-only v2 review asserting `hasFormatDrift: false`.
1. **Medium: legacy finding bodies now include trailing content.** `resolve-copilot-threads:497` changed `($slice | findings)` to `(.body | suppressed_findings)`. The last finding in `format-a`, `format-b`, and `format-c` now ends with `</details>`, and `format-c` also carries the `Files reviewed` trailer lines. It also turns a bold `**path:N**` line in any Copilot overview into a finding that swallows the rest of the body. Reverting to `($slice | suppressed_findings)` restores base output for all three fixtures with the suite still green. Add an assertion on the last finding's body so this is covered.
1. **Medium: table findings can be dropped without drift.** `resolve-copilot-threads:461-480`. `[^;]+?` rejects any item containing `;`, and the terminator requires a final `.`. Either case silently loses that finding, and drift stays false if another finding in the review parsed. Consider splitting the cell on `;` followed by a severity token, stripping one trailing period, and flagging drift when the cell contains a severity token that produced no item.
1. **Medium: step 1c identity contradicts re-emission.** `SKILL.md:247` (step 1c rule 1) requires "a prior summary links the same review", but line 235 says Copilot re-emits findings in every later review. Key identity on `path:line` (or normalized path plus finding text for line-less findings) and treat the review link as provenance, not part of the key.
1. **Medium: `monitor-pr` dispatch does not route drift.** Step 4 condition 6 (`monitor-pr` `SKILL.md:137`) and the Dependabot section (`SKILL.md:63`) mention only threads and findings. A drift-only review at the current head is not clean, yet matches no dispatch condition, so the watch waits indefinitely. Add "or format drift" to condition 6 and to the Dependabot rule.
1. **Low: stale count in the resolver summary example.** At `SKILL.md:438`, the `Counts:` line still says `1 deferred`, but the example's deferred row was replaced by a Nitpick/Noted row.

### Suggestions

- `verdict` returns the first `###` line of any body, so legacy reviews report headings such as `### Reviewed changes`. Either scope it to v2 bodies or document that it is only meaningful there.
- The clean-verdict comparison is an exact string match. Trimming the heading (including a trailing `\r`) before comparing costs nothing and avoids a false drift if line endings change.
- Step 1c's line-less rule matches on "finding text", while the summary's `Finding` cell holds only "a concise identifying excerpt". Say explicitly that the excerpt is compared as a prefix or substring of the parsed `body`.
- The local audit table header now reads `Action taken`, while its column definition still says `Action Taken`.
- Consider a named scrut case for the contradictory `**Findings:** None` header, since #458 and #459 both call it out.
