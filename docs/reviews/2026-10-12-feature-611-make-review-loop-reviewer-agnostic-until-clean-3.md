# Review until clean: feature/611-make-review-loop-reviewer-agnostic

Base: main (b89fff26447e3f9064ce81997f5a9a1620b6106f)
Reviewer: /review-pr-with-codex --effort xhigh (from --reviewer)
Rounds: 1 of 3
Status: failed
Confirmation: off

This is the third run on this branch today; the earlier ledgers are `2026-10-12-feature-611-make-review-loop-reviewer-agnostic-until-clean.md` and `-until-clean-2.md`.

## Round 1

Snapshot: a6e42e07eb7b69a3f86e8d77e9503ca70fc8f5e8
Invocation: /review-pr-with-codex --effort xhigh (aspects code, errors, tests, comments; types skipped, no data definition changed; simplify skipped, an aspect failed)
Mode: report (no lasting changes found)
Coverage: full for the aspects that finished; the comments aspect did not finish

The review did not finish. The `comments` aspect failed partway: `codex` exited 1 with `ERROR: Selected model is at capacity. Please try a different model.` and wrote no output file. `review-pr-with-codex` reported the review as incomplete, so the round is failed and carries no clean verdict.

Reviewer reply, verbatim (the three aspects that finished):

```text
{
  "aspect": "code",
  "findings": [],
  "reviewed": "a6e42e07eb7b69a3f86e8d77e9503ca70fc8f5e8",
  "strengths": [
    "Edit rounds cannot report clean or queue findings against replaced code.",
    "Raw reviewer output and explicit coverage qualifiers preserve the evidence behind each result."
  ],
  "summary": "Reviewed the full committed scope and surrounding code against the base-revision project instructions. No introduced defects or guideline violations met the reporting threshold; the change meets the project's standards. Read-only shell syntax and failure-propagation checks passed."
}
{
  "aspect": "errors",
  "findings": [],
  "reviewed": "a6e42e07eb7b69a3f86e8d77e9503ca70fc8f5e8",
  "strengths": [
    "Missing, empty, incomplete, and malformed reviewer output explicitly fails the round.",
    "Exit status and complete stdout and stderr are preserved before cleanup.",
    "Shell execution preserves pipeline failures, and reviewer substitution cannot happen silently.",
    "Edit rounds and invalidated snapshots cannot produce a clean verdict."
  ],
  "summary": "Reviewed the complete committed scope, generated counterparts, and surrounding error-handling paths against the base-revision instructions. No reportable error-handling defects remain. Read-only syntax and status-capture checks passed; the full review loop was not executed."
}
{
  "aspect": "tests",
  "findings": [
    {
      "confidence": 99,
      "detail": "Criticality: 8/10. Existing review-scope tests verify snapshot movement, and codex-aspects tests detect edits, but neither exercises the loop's edit-round decisions. Recorded runs contain only report rounds. A regression could queue stale findings, report unreviewed edits as clean, or continue reviewing after an edit under --report-only. This coverage remains explicitly deferred in the ledger.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Add repeatable skill evaluations or recorded manual scenarios with an editing reviewer and a recording fixer. Verify stale findings remain non-actionable, subsequent rounds review the new snapshot, report-only ends decisions-needed without reverting, and edits at the cap or during confirmation cannot produce clean.",
      "line": 132,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not exercise edit-round decisions."
    },
    {
      "confidence": 98,
      "detail": "Criticality: 8/10. Codex integration tests cover that helper's validator, and the recorded incomplete Codex run exercises one failure case. Neither verifies arbitrary shell reviewers or native-report transcription. An empty successful process, error-only reply, malformed structured output, missing skill report, or concealed pipeline failure could become empty findings and a false clean result. The documented failure-injection scenarios have no recorded execution through the loop.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Run the actual skill with deterministic shell and in-session reviewers producing these failures, including a failing pipeline with a successful consumer. Assert failed status, preserved diagnostics, and no fixer invocation; include a completed no-findings report as a positive control.",
      "line": 47,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify generic completion failures."
    },
    {
      "confidence": 97,
      "detail": "Criticality: 7/10. Coverage now depends on interpreting the reviewer's report, but existing tests verify scope enumeration and Codex prompt construction only. Recorded rounds cover committed changes without exercising partial or unverified classification. A reviewer reporting only working-tree changes, or naming no scope, could incorrectly yield full coverage and plain clean over unread commits. This gap also remains deferred in the ledger.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Add scenarios with committed and working-tree changes whose reports cover every bucket, omit a bucket, or provide no coverage information. Verify full, partial, and unverified classifications and the corresponding final qualifiers, including confirmation runs.",
      "line": 123,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify report-derived coverage classifications."
    }
  ],
  "reviewed": "a6e42e07eb7b69a3f86e8d77e9503ca70fc8f5e8",
  "strengths": [
    "Existing scope tests cover all four buckets, content changes, staging and intent-to-add invariance, index preservation, and unavailable bases.",
    "Existing Codex integration tests cover missing, empty, malformed, schema-invalid, mismatched, and stale results, including non-zero exits after valid output.",
    "Existing integration tests verify concurrent result association, process cancellation, changed-path detection, and identical shipping copies of review-scope.",
    "The saved incomplete Codex run records failed status rather than presenting unfinished review coverage as clean."
  ],
  "summary": "Reviewed the complete committed scope, surrounding workflows, existing tests, and saved verification ledgers. Helper coverage is strong, but three important behavioral gaps remain in the reviewer-independent loop and are already recorded as deferred. Test suites were inspected without execution; read-only Bash syntax checks passed."
}
```

Findings from the finished aspects, not queued:

- `code`: none.
- `errors`: none.
- **F1** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:132`. No test covers edit-round decisions (tests). Matches F4 of the first run, declined.
- **F2** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:47`. No test covers generic completion failures (tests). Matches F5 of the first run, declined.
- **F3** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:123`. No test covers coverage classification (tests). Matches F19 of the first run, declined.

## Result

Failed: the review did not finish, because Codex was at capacity for the `comments` aspect. Had it finished with no findings, the round would have been `clean-with-declines`, since every finding from the other three aspects is a carried decline. That outcome is not established.
