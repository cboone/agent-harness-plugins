# Review until clean: feature/611-make-review-loop-reviewer-agnostic

Base: main (b89fff26447e3f9064ce81997f5a9a1620b6106f)
Reviewer: /review-pr-with-codex --effort high (from --reviewer)
Rounds: 3 of 3
Status: stopped
Confirmation: off

## Round 1

Snapshot: 8f2082559931b796569c0ba9196863f8e2ca125e
Invocation: /review-pr-with-codex --effort high (aspects code, errors, tests, comments; types skipped, no data definition changed; simplify skipped, a Critical finding was reported)
Mode: report
Coverage: full (committed bucket, 32 files; staged, unstaged and untracked empty)

Reviewer reply, verbatim:

```text
{
  "aspect": "code",
  "findings": [
    {
      "confidence": 96,
      "detail": "Step 8 sends edit-round findings directly to address-review even though their snapshot has changed. For example, review-pr-with-codex reports findings before running simplify, which can modify the same files. Concurrent edits during a reviewer run take this branch too. The subsequent validity check only detects changes after step 5, so findings about obsolete code can reach the fixer.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Keep edit-round findings non-actionable until a new review or explicit revalidation binds them to the current snapshot.",
      "line": 132,
      "severity": "important",
      "title": "write-markdown: Snapshot validity. Edit rounds can send stale findings to the fixer."
    },
    {
      "confidence": 100,
      "detail": "Classifying every value beginning with / as a skill rejects valid shell commands using absolute executable paths. For example, --reviewer '/opt/homebrew/bin/coderabbit review --plain' is checked against available skills and reported missing instead of running the installed executable.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Resolve advertised skill or slash-command names explicitly, and classify absolute executable paths as shell commands.",
      "line": 19,
      "severity": "important",
      "title": "write-markdown: Reviewer dispatch. Absolute executable paths are misclassified as skills."
    }
  ],
  "reviewed": "8f2082559931b796569c0ba9196863f8e2ca125e",
  "strengths": [
    "Completion checks preserve raw reviewer output as evidence before transcription.",
    "Coverage reporting distinguishes full, partial and unverified reviews."
  ],
  "summary": "Reviewed the full committed scope and surrounding code against the base-revision project instructions. Two behavioral issues in the reviewer workflow should be fixed; the shell helper changes are comment-only."
}
{
  "aspect": "errors",
  "findings": [
    {
      "confidence": 97,
      "detail": "The snapshot-mismatch handler forwards an edit round's findings to step 9 even though it explicitly acknowledges that the reviewed code no longer exists. A concurrent edit or an editing reviewer can remove the reported defect, rename its file, or shift its location before returning. The later invalidation check only detects changes after step 5, so these stale findings can reach the fixer without exposing that their evidence is obsolete.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Keep findings from an edit round as historical evidence, but do not queue them for fixing until a subsequent review validates them against the current snapshot. Continue to step 10, or report unreviewed changes when the round limit is reached.",
      "line": 132,
      "severity": "important",
      "title": "write-markdown: Commands and output forward stale findings after a snapshot mismatch."
    },
    {
      "confidence": 99,
      "detail": "The ledger retains only the first lines of stderr, while line 80 requires deleting the temporary directory afterward. A CLI can print initialization or progress messages first and put the actual authentication error, network failure, or exception traceback later. The round may correctly report failure, but its only actionable diagnostic is discarded, preventing later diagnosis from the saved ledger.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Preserve complete stdout and stderr before cleanup, either in fenced ledger sections or persistent files referenced by the ledger. Terminal summaries can use excerpts, but temporary captures should be removed only after both streams are retained.",
      "line": 147,
      "severity": "important",
      "title": "write-markdown: Commands and output discard stderr diagnostics after the initial lines."
    }
  ],
  "reviewed": "8f2082559931b796569c0ba9196863f8e2ca125e",
  "strengths": [
    "Empty replies, non-zero exits, timeouts, and malformed structured output are explicitly classified as failed rounds.",
    "Reviewer substitution and automatic retries are prohibited, keeping failures visible.",
    "Raw replies are preserved separately from transcription so an empty findings list cannot establish completion by itself."
  ],
  "summary": "Reviewed the full specified change scope and surrounding error-handling rules without modifying files. Two important issues remain: stale findings can reach the fixer after snapshot movement, and saved failure evidence can omit the actual stderr diagnostic."
}
{
  "aspect": "tests",
  "findings": [
    {
      "confidence": 98,
      "detail": "Criticality: 8/10. Existing review-scope tests prove that edits move the snapshot, and codex-aspects tests detect changed paths, but neither exercises the loop's new edit-round decisions. There is no regression case for an editing reviewer returning no findings under --report-only or during confirmation past --max-rounds. Such a case would catch reporting unreviewed edits as clean, continuing beyond the cap, or invoking the fixer before the later stop condition.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Add harness-level regression cases that invoke the actual skill with deterministic editing reviewers and a recording fixer. Assert decisions-needed without fixing or reverting under --report-only, stopped after an edit at the cap, and no fixer or further review after an extra confirming round edits.",
      "line": 132,
      "severity": "important",
      "title": "tests: Behavioral coverage is missing for edit-round stop decisions."
    },
    {
      "confidence": 97,
      "detail": "Criticality: 7/10. The generic completion contract has no tests invoking review-until-clean with shell or in-session reviewers. Existing codex-aspects failure tests validate that separate helper's structured output handling; they do not exercise the loop's prose transcription path. A zero-exit reviewer with empty or error-only output, or a skill ending without a report, could be transcribed into empty findings and reported clean without any existing test failing. The examples in stop-rules.md describe checks but provide no executed regression coverage.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Add skill execution cases for empty, error-only, truncated and non-zero shell responses, plus missing and error-only skill reports. Assert failed status, no fixer invocation and preservation of failure evidence; include a completed no-findings report as the positive control.",
      "line": 47,
      "severity": "important",
      "title": "tests: Negative completion cases do not cover generic reviewer transcription."
    }
  ],
  "reviewed": "8f2082559931b796569c0ba9196863f8e2ca125e",
  "strengths": [
    "Existing scope tests cover all four buckets, content changes, staging invariance, intent-to-add invariance and preservation of the caller's index.",
    "Existing Codex integration tests cover missing, empty, malformed and mismatched results, non-zero exits after valid output, concurrent runs and cancellation.",
    "Existing tests verify that both shipping plugins retain identical review-scope helpers."
  ],
  "summary": "Reviewed the full committed diff and mapped changed behavior to existing tests. Helper coverage is strong, but the new generic loop lacks regression coverage for edit-round decisions and completion failures; tests were inspected without execution to preserve the read-only boundary."
}
{
  "aspect": "comments",
  "findings": [
    {
      "confidence": 100,
      "detail": "The option table promises that --report-only will 'change nothing', but workflow steps 4 and 8 explicitly allow editing reviewers and preserve their edits. For example, --report-only --reviewer /simplify can modify source files and finish with decisions-needed. The same stale guarantee appears in the skill's option description and stop-rules.md's statement that neither round edits anything.",
      "file": "plugins/review-until-clean/README.md",
      "fix": "Rewrite the description as: 'Run the reviewer and write the ledger without invoking the fixer. The selected reviewer may edit files; those edits remain in place and are reported as decisions-needed. With --confirm-clean, run a confirming round when the first is clean.' Update the matching skill and stop-rule descriptions.",
      "line": 84,
      "severity": "critical",
      "title": "write-markdown: Factual accuracy: Report-only is documented as preventing changes although editing reviewers remain enabled."
    },
    {
      "confidence": 100,
      "detail": "The statement that each round confirms an item list 'before anything is edited' no longer holds. Step 4 invokes editing reviewers immediately, while address-review's confirmation happens only later, if findings reach step 9. A /simplify round can therefore edit files without the promised confirmation.",
      "file": "plugins/review-until-clean/README.md",
      "fix": "Rewrite the paragraph as: 'Address Review confirms the finding list before its fix pass. Editing reviewers, such as /simplify, run before that confirmation and follow their own approval behavior. Their changes are recorded in the ledger and reviewed in another round when the round budget permits.'",
      "line": 87,
      "severity": "important",
      "title": "write-markdown: Factual accuracy: The confirmation guarantee incorrectly includes edits made by the reviewer."
    }
  ],
  "reviewed": "8f2082559931b796569c0ba9196863f8e2ca125e",
  "strengths": [
    "The completion rules clearly distinguish missing review output from a completed review with no findings.",
    "The coverage documentation explicitly distinguishes full, partial and unverified coverage.",
    "The Codex invocation reference preserves measured versions and explains the reasons behind its constraints."
  ],
  "summary": "Reviewed all changed comments and documentation, including the plan, catalog descriptions and generated mirrors, against the surrounding implementation. Two stale guarantees need correction to accurately describe editing reviewers."
}
```

- [x] **F1** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:132`. An edit round's findings go to the fixer although the snapshot they describe is gone (code, errors).
      Evidence: step 8 sends edit-round findings to step 9; the invalidation check covers only changes after step 5.
      Fixed in 57c79488: edit-round findings are recorded, never queued.
- [x] **F2** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:19`. A shell command given by absolute path, such as `/opt/homebrew/bin/coderabbit review --plain`, is classified as a skill (code).
      Evidence: the kind rule is "a value that starts with `/` is a skill or command".
      Fixed in 57c79488: a reviewer is a skill only when its first word names an available one.
- [x] **F3** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:147`. Only the first lines of stderr are kept before the temporary directory is removed, so the real diagnostic can be lost (errors).
      Evidence: "with its exit status and the first lines of stderr" and the cleanup rule in Running a reviewer.
      Fixed in 57c79488: stdout and stderr are kept in full.
- [x] **F4** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:132`. No regression test covers edit-round stop decisions (tests).
      Evidence: scrut covers review-scope and codex-aspects, not the skill's decisions.
      Declined: an executable harness for the skill is outside this change.
- [x] **F5** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:47`. No regression test covers generic completion failures for shell and skill reviewers (tests).
      Evidence: stop-rules.md describes the checks; none is executed.
      Declined: an executable harness for the skill is outside this change.
- [x] **F6** Important (reviewer: critical). `plugins/review-until-clean/README.md:84`. `--report-only` is documented as changing nothing, though an editing reviewer can still edit (comments).
      Evidence: same claim in SKILL.md options and stop-rules.md's "Neither round edits anything".
      Fixed in 57c79488 and 468a43c3: --report-only is described as skipping the fix pass.
- [x] **F7** Important. `plugins/review-until-clean/README.md:87`. "Confirm the item list before anything is edited" is false for editing reviewers, which edit before address-review runs (comments).
      Evidence: step 4 runs editing reviewers before step 9's confirmation.
      Fixed in 468a43c3: the README says address-review confirms before its fix pass, and editing reviewers act on their own terms.

## Round 2

Snapshot: c47a6524239c35f5b7f1236d7077c75397119fa5
Invocation: /review-pr-with-codex --effort high (aspects code, errors, tests, comments; types skipped, no data definition changed; simplify skipped, a Critical finding was reported)
Mode: report
Coverage: full (committed bucket; staged, unstaged and untracked empty)

Reviewer reply, verbatim:

```text
{
  "aspect": "code",
  "findings": [],
  "reviewed": "c47a6524239c35f5b7f1236d7077c75397119fa5",
  "strengths": [
    "Edit rounds cannot produce a clean verdict, and stale findings are withheld from the fixer.",
    "Coverage limits and incomplete reviewer output remain explicit in the reporting rules."
  ],
  "summary": "Reviewed the full committed scope and surrounding behavior against the applicable base-revision instructions. No introduced defects or guideline violations met the reporting threshold; the change meets the project's standards based on static review."
}
{
  "aspect": "errors",
  "findings": [
    {
      "confidence": 95,
      "detail": "The free-form reviewer command is inserted without grouping or enabling pipefail. For `reviewer --json | jq -s '{findings: [.[].findings[]]}'`, the trailing stdin redirect applies only to jq, which reads empty input and emits `{\"findings\":[]}`. Its successful exit also masks the reviewer's non-zero exit, and the reviewer's stderr bypasses the captured stderr file. A read-only reproduction returned captured_status=0 despite the reviewer returning 7 and emitting a finding. This can erase findings, omit failure diagnostics from the ledger, and produce a false clean result.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Execute the entire supplied command in a shell with pipefail, applying redirections around that invocation and capturing failure explicitly: `if bash -o pipefail -c \"${reviewer}\" < /dev/null > \"${tmp}/stdout\" 2> \"${tmp}/stderr\"; then status=0; else status=$?; fi`. Alternatively, explicitly reject compound commands and pipelines.",
      "line": 70,
      "severity": "critical",
      "title": "write-bash-scripts: Checked commands, reviewer pipelines can hide failures and erase findings."
    }
  ],
  "reviewed": "c47a6524239c35f5b7f1236d7077c75397119fa5",
  "strengths": [
    "Empty output, authentication failures, non-zero exits, and incomplete reports explicitly fail the round.",
    "Raw replies must be preserved before transcription, and silent reviewer substitutions are prohibited.",
    "Edit rounds cannot produce a clean verdict, and unreviewed changes are reported when the round limit is reached."
  ],
  "summary": "Reviewed the complete committed scope and surrounding error-handling guidance, including generated counterparts. One critical flaw in the new shell invocation can conceal reviewer failures and produce empty findings; it was reproduced without writing files."
}
{
  "aspect": "tests",
  "findings": [
    {
      "confidence": 99,
      "detail": "Criticality: 8/10. Editing reviewers are newly supported, but no test or evaluation invokes the loop with one. Existing review-scope tests verify snapshot movement, and codex-aspects tests detect edits in a separate helper; neither verifies that the loop withholds stale findings from address-review, reviews the resulting snapshot, or handles report-only and confirmation limits correctly. A regression could report unreviewed edits as clean or queue findings against replaced code.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Add harness-level evaluation cases using a reviewer that edits and returns findings. Verify that findings remain non-actionable, another round reviews the new snapshot, report-only preserves edits and reports decisions-needed, and edits during confirmation or at the round limit cannot produce clean.",
      "line": 132,
      "severity": "important",
      "title": "write-markdown: Behavioral coverage is missing for editing reviewers."
    },
    {
      "confidence": 99,
      "detail": "Criticality: 8/10. The generic completion checks now apply to arbitrary CLI and in-session reviewers, but their negative cases exist only as instructions in stop-rules.md. The existing codex-aspects failure tests exercise its own validator, which arbitrary reviewers bypass. No evaluation establishes that an exit-zero empty or error-only reply, truncated output, malformed JSON, or missing skill report produces failed rather than an empty findings list and clean.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Add executable reviewer stubs and in-session evaluation fixtures for these failure signals, plus a completed no-findings positive control. Run them through the actual skill and retain evidence of terminal status, raw-reply capture, and absence of a fix pass after failure.",
      "line": 100,
      "severity": "important",
      "title": "write-markdown: Generic reviewer completion checks lack negative evaluations."
    }
  ],
  "reviewed": "c47a6524239c35f5b7f1236d7077c75397119fa5",
  "strengths": [
    "Existing scope tests cover all four change buckets, content-sensitive snapshots, index preservation, and invalid base references.",
    "Existing Codex integration tests cover empty, missing, malformed, mismatched, and stale output, including non-zero exits after valid output.",
    "An existing integration test ensures the two shipped review-scope helpers remain identical."
  ],
  "summary": "Reviewed the complete committed scope and mapped its behavioral changes to existing tests. Two important gaps remain in evaluation of editing reviewers and generic completion checks; tests were inspected without execution to preserve the read-only constraint."
}
{
  "aspect": "comments",
  "findings": [
    {
      "confidence": 99,
      "detail": "The snapshot hashes content as Git stores it, using `git add --all --renormalize`. It cannot detect edits normalized away by Git, reverted edits, index-only changes, or writes to ignored untracked files. For example, changing an LF shell script to CRLF under text normalization can leave the snapshot unchanged despite changing executable behavior. The new mode description omits these limits, although the Codex invocation reference already documents them.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Add: \"Round mode reflects lasting changes to content as Git stores it. An unchanged snapshot does not prove that nothing was written: index-only changes, ignored untracked files, reverted edits, and changes normalized away by Git are invisible.\" Qualify the corresponding README and skill guarantees.",
      "line": 84,
      "severity": "important",
      "title": "write-markdown: Completeness: Snapshot-based mode detection omits its known blind spots."
    },
    {
      "confidence": 100,
      "detail": "This rule says evidence quoting a symlink target is withheld, but line 147 requires recording the complete reply verbatim before extracting findings. If a reviewer quotes sensitive target contents, those contents enter the ledger's raw-reply section even when omitted from the transcribed evidence.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "State: \"Before persisting any reply, redact quoted out-of-scope symlink-target contents from all fields and output streams. This exception takes precedence over verbatim capture; record that redaction occurred without retaining the withheld contents.\" Update the raw-reply rule consistently.",
      "line": 140,
      "severity": "important",
      "title": "write-markdown: Completeness: Evidence withholding conflicts with mandatory verbatim reply capture."
    },
    {
      "confidence": 100,
      "detail": "The plan says findings returned by an editing reviewer go through `address-review`. The implemented skill at step 8 and the ledger reference explicitly prohibit queueing those findings because their locations may describe the pre-edit tree. This leaves the committed planning decision contradicting the operative safety rule.",
      "file": "docs/plans/todo/2026-10-12-make-review-loop-reviewer-agnostic.md",
      "fix": "Replace the clause with: \"Any findings it also reported are recorded as notes and never queued for `address-review`; the next round reviews the resulting snapshot and raises any findings that still apply.\"",
      "line": 9,
      "severity": "important",
      "title": "write-markdown: Factual accuracy: The plan describes the opposite handling of edit-round findings."
    },
    {
      "confidence": 100,
      "detail": "The proposed search cannot return nothing: the new README, skill, and reviewer reference intentionally contain `/review-pr-with-codex --effort high` examples. Following this verification criterion would reject documentation that correctly demonstrates passing reviewer-specific options.",
      "file": "docs/plans/todo/2026-10-12-make-review-loop-reviewer-agnostic.md",
      "fix": "Rewrite as: \"Confirm no references to `backends.md` remain and no loop-level `--effort` option is documented. Reviewer-specific `--effort` options inside quoted `--reviewer` values remain valid.\"",
      "line": 93,
      "severity": "suggestion",
      "title": "write-markdown: Factual accuracy: The verification search rejects intentionally retained examples."
    }
  ],
  "reviewed": "c47a6524239c35f5b7f1236d7077c75397119fa5",
  "strengths": [
    "The README clearly explains that editing reviewers may retain changes under `--report-only` before fixer confirmation.",
    "The completion rules explain why empty output cannot establish a successful review.",
    "The Codex invocation reference preserves measured CLI versions and concrete errors alongside the rationale for each restriction."
  ],
  "summary": "Reviewed the complete committed scope, including documentation, script comments, the plan, and generated mirrors, against base-revision instructions and surrounding implementation. The documentation largely explains the new reviewer contract clearly, but snapshot limitations, conflicting evidence-retention rules, and stale plan statements should be corrected."
}
```

- [x] **F9** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:132`. No test covers editing reviewers (tests).
      Declined, carried from F4 (round 1): an executable harness for the skill is outside this change.
- [x] **F10** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:100`. Generic completion checks lack negative tests (tests).
      Declined, carried from F5 (round 1): an executable harness for the skill is outside this change.
- [x] **F8** Important (reviewer: critical). `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:70`. A reviewer given as a pipeline escapes the redirects: stdin closes only for the last command, its exit status hides the reviewer's, and the reviewer's stderr is not captured (errors).
      Evidence: reproduced read-only; a reviewer exiting 7 with a finding, piped through `jq -s`, captured status 0 and an empty findings list.
      Fixed in bc71a402: the value runs under bash -o pipefail -c; a stub exiting 7 through jq now reports status 7.
- [x] **F11** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:84`. Mode detection does not state the snapshot's blind spots: index-only changes, ignored files, reverted edits and changes Git normalizes away (comments).
      Evidence: review-pr-with-codex's invocation.md documents the same limits for the same digest.
      Fixed in bc71a402: the snapshot blind spots are stated under Report rounds and edit rounds.
- [x] **F12** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:140`. Withholding a symlink target's contents conflicts with recording the reply verbatim (comments).
      Evidence: the symlink rule withholds such evidence; Recording the raw reply requires the complete reply.
      Fixed in bc71a402: symlink target contents are redacted before any reply is saved.
- [x] **F13** Important. `docs/plans/todo/2026-10-12-make-review-loop-reviewer-agnostic.md:9`. The plan still says an editing reviewer's findings go through address-review (comments).
      Evidence: step 8 and ledger.md now forbid queueing them.
      Fixed in b473703d.
- [x] **F14** Nit (reviewer: suggestion). `docs/plans/todo/2026-10-12-make-review-loop-reviewer-agnostic.md:93`. The plan's verification grep for `--effort` cannot come back empty, since reviewer examples keep it (comments).
      Evidence: README, SKILL.md and reviewers.md quote `/review-pr-with-codex --effort high`.
      Fixed in b473703d.

## Round 3

Snapshot: abea0b84f97e876065652267e21af1955f80168f
Invocation: /review-pr-with-codex --effort high (aspects code, errors, tests, comments; types skipped, no data definition changed; simplify skipped, a Critical finding was reported)
Mode: report
Coverage: full (committed bucket; staged, unstaged and untracked empty)

Reviewer reply, verbatim:

```text
{
  "aspect": "code",
  "findings": [
    {
      "confidence": 100,
      "detail": "A valid reviewer value such as `LC_ALL=C coderabbit review --plain` is classified as a shell command, but this check runs `command -v LC_ALL=C`, which fails because an assignment is not an executable. Step 2 consequently reports the installed reviewer as unavailable and stops. A read-only Bash check confirmed that the assignment-token preflight fails while an environment-prefixed command executes successfully.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Make availability checking handle leading shell assignments and quoting, or defer executable availability to the captured invocation instead of requiring its first word to resolve.",
      "line": 28,
      "severity": "important",
      "title": "write-bash-scripts: Command checks reject valid environment-prefixed reviewers."
    }
  ],
  "reviewed": "abea0b84f97e876065652267e21af1955f80168f",
  "strengths": [
    "Editing rounds cannot produce a clean verdict, and their findings are kept out of the fixer queue.",
    "Partial and unverified coverage remain explicit in the final result."
  ],
  "summary": "Reviewed the full committed scope and surrounding behavior against the applicable base-revision instructions. One confirmed compatibility bug should be fixed in the shell-reviewer availability check."
}
{
  "aspect": "errors",
  "findings": [
    {
      "confidence": 98,
      "detail": "The reviewer value runs as a Bash script, but pipefail preserves a pipeline failure only until another command succeeds. A value that runs a reviewer pipeline followed by cleanup can therefore hide authentication failures, crashes, or failed output processing. Reproduced read-only: `bash -o pipefail -c 'false | cat; printf \"Review completed: no findings\\n\"'` prints a completion report and exits 0. The loop can accept this as clean, with no failed status to explain that the review never completed.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Run the script with `bash -e -o pipefail -c \"${reviewer}\"`, and capture its status in an explicit outer if/else so caller errexit cannot skip diagnostic recording. Keep cleanup outside the reviewer script. Update the explanation to distinguish pipeline status from the final script status.",
      "line": 71,
      "severity": "critical",
      "title": "write-bash-scripts: Checked commands, a later successful command can hide reviewer failure."
    }
  ],
  "reviewed": "abea0b84f97e876065652267e21af1955f80168f",
  "strengths": [
    "Empty, truncated, malformed, and error-only replies explicitly fail instead of becoming empty findings.",
    "Raw diagnostics retain the exit status and complete stdout and stderr before capture cleanup.",
    "Reviewer failures prohibit silent substitution, and edit rounds cannot receive a clean verdict."
  ],
  "summary": "Reviewed the complete supplied changes and surrounding error-handling workflows, including the generated counterparts. One reproducible shell-status masking defect must be fixed before merging."
}
{
  "aspect": "tests",
  "findings": [
    {
      "confidence": 98,
      "detail": "Criticality: 8/10. Existing review-scope tests establish snapshot movement, and codex-aspects tests detect edits, but neither exercises the loop's new edit-round decisions. A regression could report clean immediately after reviewer edits, queue findings against replaced code, or mishandle edits during report-only and confirmation runs.",
      "file": "plugins/review-until-clean/skills/review-until-clean/SKILL.md",
      "fix": "Add repeatable harness scenarios, or recorded manual verification if no harness exists, for edit-plus-findings, editing at the round cap, report-only editing, and editing during confirmation. Assert changed-path recording, exclusion of stale findings from the fixer, and the required terminal statuses.",
      "line": 132,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not exercise edit-round decisions."
    },
    {
      "confidence": 98,
      "detail": "Criticality: 8/10. The generalized completion checks have no behavioral verification. Existing codex-aspects failure tests cover that helper's structured-output path, not arbitrary shell pipelines or in-session skills. The new failure examples in stop-rules are instructions rather than tests; accepting an empty successful process or losing an upstream pipeline failure could therefore produce a false clean result unnoticed.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Exercise the actual skill with shell stubs returning empty output, malformed output, and a non-zero upstream pipeline status followed by a successful consumer, plus skills returning missing or incomplete reports. Assert failed status, retained failure evidence, and no fixer invocation.",
      "line": 47,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify native reviewer completion failures."
    },
    {
      "confidence": 96,
      "detail": "Criticality: 7/10. Coverage now depends on interpreting the reviewer's native report, but existing tests only verify scope enumeration and Codex prompt construction. No scenario checks a report covering only uncommitted work while committed changes exist, or a completed report naming no scope. A regression could silently promote partial or unverified coverage to full and report plain clean over unread changes.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Add scenarios with populated committed and working-tree buckets and reports describing full coverage, an omitted bucket, and no coverage information. Assert the ledger classification and final coverage qualifier, including during confirmation.",
      "line": 113,
      "severity": "important",
      "title": "write-scrut-tests: Behavioral coverage does not verify report-derived coverage classifications."
    }
  ],
  "reviewed": "abea0b84f97e876065652267e21af1955f80168f",
  "strengths": [
    "Existing review-scope integration tests cover all four buckets, content changes, index preservation, and unavailable bases.",
    "Existing codex-aspects tests cover missing, empty, malformed, schema-invalid, and mismatched results, including failures after valid output.",
    "Existing Codex tests verify concurrent result association, process cancellation, and changed-path detection."
  ],
  "summary": "Reviewed the complete committed range and mapped changed behavior to existing tests. Helper coverage is strong, but three important gaps remain in behavioral verification of the new reviewer-independent workflow. Tests were inspected rather than executed to preserve the read-only constraint."
}
{
  "aspect": "comments",
  "findings": [
    {
      "confidence": 100,
      "detail": "The claim that the snapshot sees content changes “and nothing else” omits two inputs: review-scope hashes HEAD and the resolved merge base alongside the working-tree tree. Committing already-reviewed content can therefore move the snapshot without changing any file content, producing an edit round with no changed paths.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/reviewers.md",
      "fix": "Rewrite as: “The snapshot binds HEAD, the resolved merge base and Git-normalized working-tree content. HEAD or merge-base changes also move it, even when no file content changed; record those changes explicitly.”",
      "line": 93,
      "severity": "important",
      "title": "write-markdown: Factual accuracy: The snapshot description omits its commit and merge-base inputs."
    },
    {
      "confidence": 100,
      "detail": "The clean rule now has four conditions, but the confirmation section still says the confirming round must satisfy “all three clean rules.” This leaves the confirmation instructions referring to the previous contract.",
      "file": "plugins/review-until-clean/skills/review-until-clean/references/stop-rules.md",
      "fix": "Rewrite the confirmation sentence as: “The pair completes when the confirming round satisfies every condition in the clean rule and its snapshot is the one the first round reviewed.”",
      "line": 9,
      "severity": "suggestion",
      "title": "write-markdown: Long-term value: The confirmation instructions retain the former clean-rule count."
    },
    {
      "confidence": 100,
      "detail": "Although this comment block now describes arbitrary reviewers, its later paragraph still says “the Claude backend has no schema” and refers to checks covering “every backend.” The named backend was removed by this change. The same stale paragraph remains in the paired review-pr-with-codex helper.",
      "file": "plugins/review-until-clean/scripts/review-scope",
      "fix": "Replace the paragraph ending with: “The schema is only half the defense: reviewers whose replies are transcribed also need the location checks documented in review-until-clean's ledger reference.” Update both canonical helpers and regenerate their mirrors.",
      "line": 55,
      "severity": "suggestion",
      "title": "write-bash-scripts: Function comments: The schema rationale still references the removed Claude backend."
    }
  ],
  "reviewed": "abea0b84f97e876065652267e21af1955f80168f",
  "strengths": [
    "The report-only documentation clearly explains that reviewer edits are retained and reported.",
    "The raw-reply guidance explains why completion evidence must remain separate from transcribed findings.",
    "The Codex invocation notes preserve measured CLI versions and concrete failure messages."
  ],
  "summary": "Reviewed the full committed scope, including documentation, script comments, the plan and generated copies, against surrounding code and base-revision instructions. The rewrite is generally clear, with one incomplete snapshot description and two stale references to correct."
}
```

- [x] **F17** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:132`. No test exercises edit-round decisions (tests).
      Declined, carried from F4 (round 1): an executable harness for the skill is outside this change.
- [x] **F18** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:47`. No test verifies reviewer completion failures (tests).
      Declined, carried from F5 (round 1): an executable harness for the skill is outside this change.
- [x] **F15** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:28`. The availability check runs `command -v` on the first word, so `LC_ALL=C coderabbit review --plain` is reported missing (code).
      Evidence: reproduced read-only; `command -v LC_ALL=C` fails while the command itself runs.
      Fixed in d336dfbc: leading NAME=value words are skipped, and exit 127 is a missing reviewer.
- [x] **F16** Important (reviewer: critical). `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:71`. `pipefail` covers one pipeline, so a later successful command in the value hides a failed review (errors).
      Evidence: `bash -o pipefail -c 'false | cat; printf "Review completed: no findings\n"'` exits 0.
      Fixed in d336dfbc: the value runs under bash -e -o pipefail in an explicit if/else; the reproduction now exits 1.
- [x] **F19** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:113`. No test verifies coverage classification from the reviewer's report (tests).
      Evidence: scrut covers scope enumeration and Codex prompts only.
      Declined: an executable harness for the skill is outside this change, as for F4 and F5.
- [x] **F20** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:93`. "The snapshot sees content changes and nothing else" omits HEAD and the merge base, so a commit with no content change still moves it (comments).
      Evidence: review-scope digests head, base and the tree.
      Fixed in d336dfbc.
- [x] **F21** Nit (reviewer: suggestion). `plugins/review-until-clean/skills/review-until-clean/references/stop-rules.md:9`. The confirmation section still says "all three clean rules"; there are four (comments).
      Fixed in d336dfbc.
- [x] **F22** Nit (reviewer: suggestion). `plugins/review-until-clean/scripts/review-scope:55`. The schema comment's later paragraph still names "the Claude backend" and "every backend", in both helper copies (comments).
      Fixed in 2280fd4a, in both helper copies.

## Result

Stopped at the round limit. Round 3's fixes (F15, F16, F20, F21 and F22) were made after the last review and have not been reviewed. No round was clean: round 1 raised 7 findings, round 2 raised 5 new ones and 2 carried declines, and round 3 raised 6 new ones and 2 carried declines. All findings were fixed except F4, F5 and F19, which were declined because they need an executable harness for the skill. Every round reviewed the full scope, which held only committed changes, with `/review-pr-with-codex --effort high`.
