# Review until clean: feature/611-make-review-loop-reviewer-agnostic

Base: main (b89fff26447e3f9064ce81997f5a9a1620b6106f)
Reviewer: /review-pr-with-codex --effort high (from --reviewer)
Rounds: 3 of 3
Status: stopped
Confirmation: off

This is the fourth run on this branch today; the earlier ledgers are `2026-10-12-feature-611-make-review-loop-reviewer-agnostic-until-clean.md`, `-until-clean-2.md` and `-until-clean-3.md`. Declines carried below come from the first.

## Round 1

Snapshot: ab6fb158fd3e73e66dae3d535444f889d8682357
Invocation: /review-pr-with-codex --effort high (aspects code, errors, tests, comments; types skipped, no data definition changed; simplify not selected, since the aspects were named explicitly)
Mode: report
Coverage: full (committed bucket; staged, unstaged and untracked empty)

Reviewer reply, verbatim:

```text
{
  "aspect": "code",
  "findings": [],
  "reviewed": "ab6fb158fd3e73e66dae3d535444f889d8682357",
  "strengths": [
    "Edit rounds cannot report clean or queue findings against replaced code.",
    "Completion evidence, failure diagnostics, and coverage qualifications remain explicit."
  ],
  "summary": "Reviewed the entire committed scope and surrounding behavior against the base-revision instructions. No introduced code defects or guideline violations met the reporting threshold; the change meets the project's standards for this aspect. Read-only syntax and shell-status checks passed; the full review loop was not executed."
}
{
  "aspect": "errors",
  "findings": [],
  "reviewed": "ab6fb158fd3e73e66dae3d535444f889d8682357",
  "strengths": [
    "Empty, incomplete, error-only, and unparseable structured replies explicitly fail the round.",
    "Shell execution preserves reviewer and pipeline failures, including exit-status capture under zsh.",
    "Complete stdout and stderr must be retained before temporary captures are removed.",
    "Silent reviewer substitution is prohibited, and edit rounds cannot produce a clean verdict."
  ],
  "summary": "Reviewed the complete committed scope, generated counterparts, and surrounding error-handling workflows against the base-revision instructions. No reportable defects were found; read-only syntax and failure-propagation checks passed, while the full review loop was not executed."
}
{
  "aspect": "tests",
  "findings": [
    {
      "confidence": 99,
      "detail": "Criticality: 8/10. Existing review-scope tests verify snapshot movement, and codex-aspects tests detect edits, but neither exercises the loop's edit-round decisions. Saved runs contain only report rounds. No behavioral case catches stale findings reaching address-review, unreviewed edits being reported clean, or additional reviews after an edit under --report-only. This coverage remains explicitly deferred in the ledger.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Add repeatable skill evaluations or recorded manual scenarios using an editing reviewer and a recording fixer. Verify that stale findings remain non-actionable, subsequent rounds review the new snapshot, report-only preserves edits and ends decisions-needed, and edits at the cap or during confirmation cannot produce clean.",
      "line": 132,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not exercise edit-round decisions."
    },
    {
      "confidence": 98,
      "detail": "Criticality: 8/10. Codex integration tests cover that helper's validator, and saved incomplete reviews exercise one failure case. Neither verifies arbitrary shell reviewers or in-session report transcription. An empty successful process, error-only reply, malformed structured output, missing skill report, or concealed pipeline failure could become empty findings and a false clean result without existing tests detecting it. The documented failure-injection scenarios have no recorded execution through the loop.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Exercise the actual skill with deterministic shell and in-session reviewers producing these failures, including a failing pipeline with a successful consumer. Assert failed status, preserved diagnostics, and no fixer invocation; include a completed no-findings report as a positive control.",
      "line": 47,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify generic completion failures."
    },
    {
      "confidence": 97,
      "detail": "Criticality: 7/10. Coverage now depends on interpreting the reviewer's report, but existing tests verify scope enumeration and Codex prompt construction only. Saved rounds do not exercise partial or unverified classification. A reviewer covering only working-tree changes, or naming no scope, could incorrectly yield full coverage and plain clean over unread commits. This gap also remains explicitly deferred.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Add scenarios with committed and working-tree changes whose reports cover every bucket, omit a bucket, or provide no scope information. Verify full, partial, and unverified classifications and their final qualifiers, including confirmation runs.",
      "line": 123,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify report-derived coverage classifications."
    }
  ],
  "reviewed": "ab6fb158fd3e73e66dae3d535444f889d8682357",
  "strengths": [
    "Existing scope tests cover all four buckets, content changes, staging and intent-to-add invariance, index preservation, and unavailable bases.",
    "Existing Codex integration tests cover missing, empty, malformed, schema-invalid, mismatched, and stale results, including failures after valid output.",
    "Existing integration tests verify concurrent result association, process cancellation, changed-path detection, and identical shipping copies of review-scope.",
    "Saved incomplete Codex reviews record failed status instead of presenting unfinished reviews as clean."
  ],
  "summary": "Reviewed the entire specified committed range, surrounding workflows, existing tests, and saved verification ledgers. Helper coverage is strong, but three important behavioral gaps remain in the reviewer-independent loop. Tests were inspected without execution to preserve the read-only boundary."
}
{
  "aspect": "comments",
  "findings": [
    {
      "confidence": 97,
      "detail": "The recipe includes paths appearing in only one scope read's file lists, but those lists describe change buckets rather than file existence. If f.txt has a staged change while its working copy matches HEAD, resetting its index entry removes it from the lists without changing its content. If the reviewer also edits another file, this recipe incorrectly lists f.txt among the edit round's content changes.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Rewrite as: \"Derive changed paths by comparing the before and after scope reads' tree objects with `git diff-tree -r -z --name-only <before.tree> <after.tree>`. Scope-list membership alone does not establish a content change. Record HEAD or base changes separately.\"",
      "line": 103,
      "severity": "important",
      "title": "write-markdown: Completeness: The changed-path recipe conflates scope membership with content changes."
    }
  ],
  "reviewed": "ab6fb158fd3e73e66dae3d535444f889d8682357",
  "strengths": [
    "Report-only documentation clearly distinguishes reviewer edits from the loop's fix pass.",
    "Completion rules explain why raw evidence must remain separate from transcribed findings.",
    "Snapshot documentation explicitly describes commit inputs and known detection limits."
  ],
  "summary": "Reviewed all changed comments and documentation, including generated mirrors, the plan and saved review records, against surrounding code and base-revision instructions. One changed-path description should be clarified to prevent misleading edit records."
}
```

- [x] **F1** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:132`. No test exercises edit-round decisions (tests).
      Declined, carried from F4 of the first run: an executable harness for the skill is outside this change.
- [x] **F2** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:47`. No test verifies generic completion failures (tests).
      Declined, carried from F5 of the first run: an executable harness for the skill is outside this change.
- [x] **F3** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:123`. No test verifies coverage classification (tests).
      Declined, carried from F19 of the first run: an executable harness for the skill is outside this change.
- [x] **F4** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:103`. The changed-path recipe counts a path that only left a scope list, such as an unstaged index reset with no content change, as an edit (comments).
      Evidence: the scope lists name change buckets, not content; `git add`, `git reset` and `git add -N` move paths between them without moving the snapshot.
      Fixed in 43b131fd: changed paths come from git diff-tree over the two scope reads' trees.

## Round 2

Snapshot: 96d75404469c3e81ef31bc302327a616462bca53
Invocation: /review-pr-with-codex --effort high (aspects code, errors, tests, comments; types skipped, no data definition changed; simplify not selected, since the aspects were named explicitly)
Mode: report
Coverage: full (committed bucket; staged, unstaged and untracked empty)

Reviewer reply, verbatim:

```text
{
  "aspect": "code",
  "findings": [],
  "reviewed": "96d75404469c3e81ef31bc302327a616462bca53",
  "strengths": [
    "Edit rounds cannot report clean or send stale findings to the fixer.",
    "Raw replies and explicit coverage qualifiers preserve evidence behind review results.",
    "Shell invocation preserves failures and captures exit status correctly under zsh."
  ],
  "summary": "Reviewed the complete committed scope and surrounding behavior against the base-revision project instructions. No introduced code defects or guideline violations met the reporting threshold; the change meets the project's standards. Read-only shell syntax and failure-propagation checks passed; the full workflow was not executed."
}
{
  "aspect": "errors",
  "findings": [],
  "reviewed": "96d75404469c3e81ef31bc302327a616462bca53",
  "strengths": [
    "Empty, incomplete, malformed, and error-only replies explicitly fail the round.",
    "Complete stdout, stderr, and exit status are preserved before cleanup.",
    "Shell invocation preserves pipeline failures and captures exit status correctly in zsh.",
    "Reviewer substitution is explicit, and edit rounds cannot produce a clean verdict."
  ],
  "summary": "Reviewed the entire specified committed scope and surrounding error-handling workflows against the base-revision instructions. No reportable error-handling defects were found. Read-only syntax and status-capture checks passed; the full review loop was not executed."
}
{
  "aspect": "tests",
  "findings": [
    {
      "confidence": 99,
      "detail": "Criticality: 8/10. Existing review-scope and codex-aspects tests verify snapshot movement and changed paths, but neither exercises the loop's edit-round decisions. Recorded runs contain only report rounds. No scenario would catch stale findings reaching the fixer, unreviewed edits being reported clean, or another review starting after an edit under --report-only.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Add repeatable skill evaluations or recorded manual scenarios with an editing reviewer and a recording fixer. Verify that stale findings remain non-actionable, subsequent rounds review the new snapshot, report-only preserves edits and ends decisions-needed, and edits at the cap or during confirmation end stopped.",
      "line": 132,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not exercise edit-round decisions."
    },
    {
      "confidence": 98,
      "detail": "Criticality: 8/10. Codex integration tests cover that helper's validator, and the saved incomplete review demonstrates one correctly failed integration run. Neither verifies arbitrary shell reviewers or native-report transcription. Empty successful processes, error-only replies, malformed structured output, missing skill reports, or concealed pipeline failures could become empty findings and a false clean result without existing tests detecting it.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Exercise the actual skill with deterministic shell and in-session reviewers producing these failure signals, including a failing pipeline with a successful consumer. Assert failed status, retained diagnostics, and no fixer invocation; include a completed no-findings report as a positive control.",
      "line": 47,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify generic reviewer completion failures."
    },
    {
      "confidence": 97,
      "detail": "Criticality: 7/10. Coverage now depends on interpreting the reviewer's report, but existing tests verify scope enumeration and Codex prompt construction only. Recorded rounds exercise committed coverage without partial or unverified classification. A reviewer naming only working-tree changes, or naming no scope, could incorrectly yield full coverage and plain clean over unread commits.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Add scenarios with populated committed and working-tree buckets whose reports cover every bucket, omit a bucket, or provide no coverage information. Verify full, partial, and unverified classifications and their final qualifiers, including confirmation runs.",
      "line": 123,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify report-derived coverage classifications."
    }
  ],
  "reviewed": "96d75404469c3e81ef31bc302327a616462bca53",
  "strengths": [
    "Existing scope tests cover all four buckets, content changes, staging and intent-to-add invariance, index preservation, and unavailable bases.",
    "Existing Codex integration tests cover missing, empty, malformed, schema-invalid, mismatched, and stale results, including failures after valid output.",
    "Existing integration tests verify concurrent result association, process cancellation, changed-path detection, and identical shipping copies of review-scope.",
    "Saved incomplete Codex reviews record failed status instead of presenting unfinished reviews as clean."
  ],
  "summary": "Reviewed the complete committed scope, surrounding workflows, existing tests, and saved verification ledgers. Helper coverage is strong, but three important behavioral gaps remain in the reviewer-independent loop and are already recorded as deferred. Tests were inspected without execution to preserve the read-only boundary."
}
{
  "aspect": "comments",
  "findings": [
    {
      "confidence": 100,
      "detail": "The external-tools entry still requires a Codex or Claude backend and promises read-only execution without fix flags. The new workflow accepts any installed reviewer and permits editing reviewers, including under --report-only. Readers therefore receive obsolete requirements and a false read-only guarantee.",
      "file": "README.md",
      "fix": "Replace the entry with: “Review Until Clean: an installed reviewer skill, slash command or CLI; reviewer edits are allowed and recorded. git and jq are required for scope and snapshot computation.”",
      "line": 100,
      "severity": "critical",
      "title": "write-markdown: Factual accuracy: The root README still promises the removed read-only backends."
    },
    {
      "confidence": 100,
      "detail": "The preceding text promises an example with a three-backtick fence inside a four-backtick ledger fence. The rendered example instead shows a three-backtick ledger fence; the four-backtick fence only wraps the documentation example. Copying that example for a reply containing triple-backtick blocks defeats the demonstrated containment rule.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Show the example inside a five-backtick Markdown fence, with a four-backtick text fence around the reply and an actual three-backtick code block inside the sample reply.",
      "line": 165,
      "severity": "suggestion",
      "title": "write-markdown: Commands and output: The raw-reply example does not demonstrate its stated fence lengths."
    }
  ],
  "reviewed": "96d75404469c3e81ef31bc302327a616462bca53",
  "strengths": [
    "The report-only documentation clearly explains that reviewer edits remain in place.",
    "The snapshot reference documents commit inputs, normalization and other detection limits.",
    "Completion rules preserve raw evidence separately from transcribed findings."
  ],
  "summary": "Reviewed the complete committed scope, including documentation, script comments, saved reviews and generated copies, against surrounding implementation and base-revision guidelines. One obsolete read-only guarantee needs correction, and one documentation example could be improved."
}
```

- [x] **F5** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:132`. No test exercises edit-round decisions (tests).
      Declined, carried from F4 of the first run.
- [x] **F6** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:47`. No test verifies generic completion failures (tests).
      Declined, carried from F5 of the first run.
- [x] **F7** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:123`. No test verifies coverage classification (tests).
      Declined, carried from F19 of the first run.
- [x] **F8** Important (reviewer: critical). `README.md:100`. The root README's external-tools entry still requires a `codex` or `claude` backend and promises both run read-only with no fix flag (comments).
      Evidence: the loop now takes any reviewer and allows editing reviewers.
      Fixed in fd0c2726.
- [x] **F9** Nit (reviewer: suggestion). `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:165`. The fence-sizing example says it shows a three-backtick reply fence inside a four-backtick ledger fence, but shows the ledger fence at three (comments).
      Fixed in fd0c2726.

## Round 3

Snapshot: 05d964a5aab820966eafb4c3c8456bf981c4a3c9
Invocation: /review-pr-with-codex --effort high (aspects code, errors, tests, comments; types skipped, no data definition changed; simplify not selected, since the aspects were named explicitly)
Mode: report
Coverage: full (committed bucket; staged, unstaged and untracked empty)

Reviewer reply, verbatim:

```text
{
  "aspect": "code",
  "findings": [],
  "reviewed": "05d964a5aab820966eafb4c3c8456bf981c4a3c9",
  "strengths": [
    "Edit rounds cannot report clean or queue findings against replaced code.",
    "Raw replies and explicit coverage qualifiers preserve evidence behind each result."
  ],
  "summary": "Reviewed the full committed scope and surrounding code against the base-revision project instructions. No introduced defects or guideline violations met the reporting threshold; the change meets the project's standards. Read-only shell syntax and failure-propagation checks passed; the full review loop was not executed."
}
{
  "aspect": "errors",
  "findings": [],
  "reviewed": "05d964a5aab820966eafb4c3c8456bf981c4a3c9",
  "strengths": [
    "Missing, empty, incomplete, and error-only reviewer replies explicitly fail the round.",
    "Exit status and complete stdout and stderr are preserved before cleanup.",
    "Shell execution preserves pipeline failures without silently substituting reviewers.",
    "Edit rounds and invalidated snapshots cannot produce a clean verdict."
  ],
  "summary": "Reviewed the complete specified commit range, applicable base-revision instructions, and surrounding error-handling workflows. No reportable defects were found; read-only syntax and shell-status checks passed, but the full review loop was not executed."
}
{
  "aspect": "tests",
  "findings": [
    {
      "confidence": 99,
      "detail": "Criticality: 8/10. Existing review-scope tests verify snapshot movement, and codex-aspects tests detect changed paths, but neither exercises the loop's edit-round decisions. Recorded runs contain only report rounds. A regression could queue findings against replaced code, report unreviewed edits as clean, or continue after an edit under --report-only. This coverage remains explicitly deferred.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Add repeatable skill evaluations or recorded manual scenarios with an editing reviewer. Verify stale findings remain non-actionable, subsequent rounds review the new snapshot, report-only ends decisions-needed without reverting, and edits at the cap or during confirmation cannot produce clean.",
      "line": 132,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage is missing for edit-round decisions."
    },
    {
      "confidence": 98,
      "detail": "Criticality: 8/10. Codex integration tests exercise that helper's validator, and saved incomplete reviews demonstrate one failure path. Neither covers arbitrary shell reviewers or in-session report transcription. Empty successful output, error-only replies, malformed structured output, or missing skill reports could become empty findings and a false clean result. The documented failure-injection scenarios have no recorded execution through the loop.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Exercise the actual skill with deterministic shell and in-session reviewers producing these failures, including a failing pipeline with a successful consumer. Verify failed status, preserved diagnostics, and no fixer invocation; include a completed no-findings report as a positive control.",
      "line": 47,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify generic completion failures."
    },
    {
      "confidence": 97,
      "detail": "Criticality: 7/10. Coverage now depends on interpreting the reviewer's report, but existing tests verify scope enumeration and Codex prompt construction only. Saved rounds do not exercise partial or unverified coverage. A reviewer covering only working-tree changes, or naming no scope, could incorrectly yield full coverage and plain clean over unread commits. This coverage also remains deferred.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Add scenarios with committed and working-tree changes whose reports cover every bucket, omit a bucket, or provide no coverage information. Verify full, partial, and unverified classifications and their final qualifiers, including confirmation runs.",
      "line": 123,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify report-derived coverage classifications."
    }
  ],
  "reviewed": "05d964a5aab820966eafb4c3c8456bf981c4a3c9",
  "strengths": [
    "Existing scope tests cover all four buckets, content changes, staging and intent-to-add invariance, index preservation, and unavailable bases.",
    "Existing Codex integration tests cover missing, empty, malformed, schema-invalid, mismatched, and stale results, including non-zero exits after valid output.",
    "Existing integration tests verify concurrent result association, process cancellation, changed-path detection, and identical shipping copies of review-scope.",
    "Saved incomplete Codex reviews retain failed status rather than claiming a clean result."
  ],
  "summary": "Reviewed the complete committed scope, surrounding workflows, existing tests, and saved verification ledgers. Helper coverage is strong, but three important behavioral gaps remain in the reviewer-independent loop and are documented as deferred. Tests were inspected without execution to preserve the read-only boundary."
}
{
  "aspect": "comments",
  "findings": [
    {
      "confidence": 99,
      "detail": "The index-only exception omits changes to which ignored paths are tracked. working_tree_digest copies the real index specifically to include tracked ignored files. Adding an existing ignored file to that index changes the tree and snapshot without changing file bytes, so this paragraph incorrectly predicts a report round.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Replace “a change only to the index” with “ordinary staging or unstaging that preserves the set of paths covered by the digest”, and add: “Index changes that add or remove tracked ignored paths can change the digest without changing file bytes.” Regenerate the mirror.",
      "line": 99,
      "severity": "important",
      "title": "write-markdown: Factual accuracy: The index-only exception omits changes to tracked-path membership."
    }
  ],
  "reviewed": "05d964a5aab820966eafb4c3c8456bf981c4a3c9",
  "strengths": [
    "The report-only documentation clearly distinguishes reviewer edits from the loop’s fix pass.",
    "Raw-output preservation and fence sizing explain both their purpose and failure cases.",
    "The saved ledgers explicitly report incomplete reviews as failed."
  ],
  "summary": "Reviewed the complete committed scope, including documentation, script comments, plans, review ledgers and generated mirrors, against surrounding implementation and base-revision instructions. The documentation is generally clear, with one snapshot exception that needs qualification."
}
```

- [x] **F10** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:132`. No test exercises edit-round decisions (tests).
      Declined, carried from F4 of the first run.
- [x] **F11** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:47`. No test verifies generic completion failures (tests).
      Declined, carried from F5 of the first run.
- [x] **F12** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:123`. No test verifies coverage classification (tests).
      Declined, carried from F19 of the first run.
- [x] **F13** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:99`. "A change only to the index leaves the snapshot where it was" is false when the change adds or removes a tracked ignored path, such as `git add -f` on an ignored file (comments).
      Evidence: review-scope seeds its digest from the real index so that force-added ignored files are covered.
      Fixed in 52c9a046.

## Result

Stopped at the round limit. F13's fix (52c9a046) was made after the last review, together with a new rule in step 6 to print every finding before acting on it, and neither has been reviewed. No round was clean: each raised one or two new findings, all fixed (F4, F8, F9, F13), alongside the three test-harness gaps carried as declines from the first run. Every round reviewed the full scope, which held only committed changes, with `/review-pr-with-codex --effort high`; the code and errors aspects reported no findings in any round.
