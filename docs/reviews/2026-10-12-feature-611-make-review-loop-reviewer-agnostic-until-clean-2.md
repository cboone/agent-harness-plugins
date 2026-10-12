# Review until clean: feature/611-make-review-loop-reviewer-agnostic

Base: main (b89fff26447e3f9064ce81997f5a9a1620b6106f)
Reviewer: /review-pr-with-codex --effort xhigh (from --reviewer)
Rounds: 1 of 3
Status: failed
Confirmation: off

This is the second run on this branch; the first run's ledger is `2026-10-12-feature-611-make-review-loop-reviewer-agnostic-until-clean.md`.

## Round 1

Snapshot: af942048b9f1304c843e91db45eb91922fe98453
Invocation: /review-pr-with-codex --effort xhigh (aspects code, errors, tests, comments; types skipped, no data definition changed; simplify skipped, an aspect failed)
Mode: report (no lasting changes found)
Coverage: full for the aspects that finished; the comments aspect did not run

The review did not finish. The `comments` aspect failed: `codex` exited 1 with `ERROR: Selected model is at capacity. Please try a different model.` and wrote no output file. `review-pr-with-codex` reported the review as incomplete, so the round is failed and its findings are not queued. They are recorded below for the next run.

Reviewer reply, verbatim (the three aspects that finished):

```text
{
  "aspect": "code",
  "findings": [
    {
      "confidence": 96,
      "detail": "The `bash -c` invocation runs only the reviewer; the surrounding assignments remain in the caller's shell. In zsh, `status` is read-only. Even a successful reviewer therefore triggers `read-only variable: status` and exits 1, preventing exit-status capture and subsequent ledger handling. This was reproduced without writing files.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Rename the capture variable to `reviewer_status` in both branches and regenerate the Codex mirror.",
      "line": 72,
      "severity": "important",
      "title": "write-bash-scripts: Checked commands: Exit-status capture fails when the caller uses zsh."
    }
  ],
  "reviewed": "af942048b9f1304c843e91db45eb91922fe98453",
  "strengths": [
    "Edit-round findings remain outside the fixer queue until a subsequent review.",
    "Raw replies and coverage qualifications preserve evidence for the reported result."
  ],
  "summary": "Reviewed the complete supplied commit range and surrounding code against the base-revision instructions. One reproduced zsh compatibility issue should be fixed; both shell helpers passed read-only syntax checks."
}
{
  "aspect": "errors",
  "findings": [
    {
      "confidence": 99,
      "detail": "The outer if/else runs in the session shell, where zsh reserves status as a read-only variable. Read-only reproductions with reviewer exits 0 and 7 both failed with 'read-only variable: status'. Authentication, network, or output-processing failures therefore lose their original captured exit code, and diagnostic handling is interrupted by an unrelated assignment error.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Use reviewer_exit_code in both branches: then reviewer_exit_code=0; else reviewer_exit_code=$?; fi. Record that variable alongside complete stdout and stderr before cleanup.",
      "line": 72,
      "severity": "important",
      "title": "write-bash-scripts: Checked commands: Exit-status capture fails in zsh."
    },
    {
      "confidence": 94,
      "detail": "The edit-round handler unconditionally jumps to step 10 before reaching the report-only termination rule at line 140. Following that jump after /simplify or a concurrent formatter changes the tree under --report-only starts another review instead of reporting decisions-needed. Later rounds can make additional edits or return clean, masking the required decision about the first round's changes.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Handle --report-only inside the edit-round branch before jumping: record the changed paths and go directly to step 11 with decisions-needed. Continue to step 10 only for ordinary edit rounds.",
      "line": 132,
      "severity": "important",
      "title": "write-markdown: Commands and output: Edit-round handling bypasses report-only termination."
    }
  ],
  "reviewed": "af942048b9f1304c843e91db45eb91922fe98453",
  "strengths": [
    "Empty, incomplete, malformed, and error-only replies explicitly fail instead of becoming empty findings.",
    "Complete stdout and stderr must be preserved before temporary captures are removed.",
    "Reviewer failures prohibit silent substitution, and pipeline failures propagate through bash -e -o pipefail."
  ],
  "summary": "Reviewed the complete committed scope and surrounding error-handling workflows against the base-revision instructions, including generated counterparts. Two important issues remain in exit-status capture and edit-round termination; shell reproductions were read-only."
}
{
  "aspect": "tests",
  "findings": [
    {
      "confidence": 99,
      "detail": "Criticality: 8/10. Existing review-scope tests verify snapshot movement, and codex-aspects tests detect edits, but neither exercises the loop's edit-round decisions. The recorded run contains only report rounds. No scenario catches stale findings reaching the fixer, unreviewed edits being reported clean, or incorrect stopping after edits under --report-only or confirmation past the round cap.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Add repeatable skill evaluations, or recorded manual scenarios, with an editing reviewer and a recording fixer. Assert that stale findings remain non-actionable, subsequent rounds review the new snapshot, report-only preserves edits and reports decisions-needed, and edits at the cap cannot produce clean.",
      "line": 132,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage is missing for edit-round decisions."
    },
    {
      "confidence": 99,
      "detail": "Criticality: 8/10. Existing Codex failure tests exercise that helper's validator, not arbitrary reviewers or native-report transcription. The ledger records shell-status reproductions, but no failure-injection run of the actual loop. Empty successful processes, error-only replies, malformed structured output, and missing skill reports could become empty findings and a false clean result without existing tests detecting it.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Exercise the actual skill with deterministic shell and in-session reviewers producing these failures, including a failing pipeline followed by a successful consumer. Assert failed status, retained diagnostics, and no fixer invocation; include a completed no-findings report as a positive control.",
      "line": 47,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify generic completion failures."
    },
    {
      "confidence": 97,
      "detail": "Criticality: 7/10. Coverage now depends on interpreting the reviewer's report, but existing tests verify scope enumeration and Codex prompt construction only. The recorded rounds demonstrate full committed coverage, without partial or unverified cases. A report covering only uncommitted changes, or naming no scope, could incorrectly yield full coverage and plain clean over unread commits.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Add scenarios with committed and working-tree changes whose reviewer reports cover every bucket, omit a bucket, or provide no scope information. Assert full, partial, and unverified classifications and their final status qualifiers, including confirmation.",
      "line": 122,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify report-derived coverage classifications."
    }
  ],
  "reviewed": "af942048b9f1304c843e91db45eb91922fe98453",
  "strengths": [
    "Existing scope tests cover all four buckets, content-sensitive snapshots, staging and intent-to-add invariance, index preservation, and invalid or unavailable bases.",
    "Existing Codex integration tests cover missing, empty, malformed, schema-invalid, mismatched, and stale results, including non-zero exits after valid output.",
    "Existing integration tests verify concurrent result association, process cancellation, changed-path detection, and identical shipping copies of review-scope."
  ],
  "summary": "Reviewed the complete committed range and mapped its changed behavior to existing tests and recorded verification. Helper coverage is strong, but three important workflow evaluation gaps remain, already documented as deferred in the review ledger. Tests were inspected without execution to preserve the read-only boundary."
}
```

Findings from the finished aspects, not queued:

- **F1** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:72`. The status-capture example assigns `status`, which is read-only in zsh, so it fails whatever the reviewer returned (code, errors).
- **F2** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:132`. An edit round under `--report-only` jumps to step 10 and starts another review, instead of ending `decisions-needed` (errors).
- **F3** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:132`. No test covers edit-round decisions (tests). Matches F4 of the first run, declined.
- **F4** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:47`. No test covers generic completion failures (tests). Matches F5 of the first run, declined.
- **F5** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:122`. No test covers coverage classification (tests). Matches F19 of the first run, declined.

## Result

Failed: the review did not finish, because Codex was at capacity for the `comments` aspect. No finding was fixed, and the round carries no clean verdict.
