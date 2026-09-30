# Review until clean: feature/add-fast-option-to-colleague-review

Base: `origin/main` (`d8a752663392fccc9c8e6158ca6b47535b230b87`)
Reviewer: Claude Code (`/code-review`), then Codex CLI (first run); Codex CLI (second run)
Rounds: first run 2 of 3; second run 3 of 3
Status: stopped

## Round 1

Snapshot: `fb656c316e783e2abe830bf7d5c728e5c6035323`
Invocation: `claude -p '/code-review medium d8a752663392fccc9c8e6158ca6b47535b230b87...HEAD' --disallowed-tools Edit Write NotebookEdit Bash`
Coverage: partial. Claude reported that it could not run `git diff` and read only the canonical `SKILL.md`, plugin `README.md`, and `plugin.json`. The full committed range was not reviewed.

Reviewer reply, verbatim:

```text
I found two issues, both in the skill's instruction text. The session had no shell, so I couldn't run `git diff`. I read the files the plan says this branch changes instead: `SKILL.md`, the plugin `README.md` and `plugin.json`. The version bump to `1.1.0` and the Codex mirror both look consistent.

1. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:366`: The fast-mode example contradicts step 6. It lists the missing #118 backoff cap only under Requirements, and its Before merge list and verdict count just the one bug. Step 6 says a core requirement left unmet belongs in Before merge, and fast mode only reports core requirement gaps. Suppose a PR's only problem is a missing core requirement. A model copying this example would leave Before merge empty and return "No blockers found" when the answer should be "Needs changes".
2. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:314`: The rules for keeping the fast-mode Requirements line conflict. Step 7 keeps it only "when sources were skipped". Line 44 and step 6 (line 306) say to keep a source-coverage line in fast mode whether or not any source was skipped. On a PR where every source was read and nothing is missing, the two rules disagree, so the coverage line will appear in some runs and not others.
```

- [x] **F1** Important. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:366`. The report example omits a missing core requirement from Before merge and understates the verdict.
      Evidence: the fast example names the missing #118 backoff cap under Requirements, while step 6 defines a core requirement left unmet as a Before merge concern. The thorough example and README repeat the same mismatch.
      Fixed: added the missing cap to both skill examples and the README example, and updated the verdict counts.
- [x] **F2** Important. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:314`. The fast Requirements coverage rule disagrees about whether a line is required when no source was skipped.
      Evidence: line 44 and step 6 request a coverage line even without a gap; step 7 requires one only when sources were skipped.
      Fixed: the fast Requirements coverage line is now required when sources were skipped, including when the requirements read appear met.

Round 1 was partial because the Claude backend could not run `git diff` with shell access denied. Codex CLI is selected for the next round to cover all four scope buckets in a read-only sandbox.

## Round 2

Snapshot: `3d994f54f32b2c52fda1158476ba9e97eef1c4fc`
Invocation: `codex exec --sandbox read-only --ephemeral --output-schema <temporary schema> -o <temporary findings> <full-scope prompt> < /dev/null`
Coverage: none. The command exited 1 before it could review the scope. It produced no findings file.

Backend output, verbatim:

```text
WARNING: proceeding, even though we could not create PATH aliases: Operation not permitted (os error 1)
Reading additional input from stdin...
Error: failed to initialize in-process app-server client: Operation not permitted (os error 1)
```

## Result

Review-until-clean status: `failed`. F1 and F2 from the partial Claude round were fixed. The Codex round did not produce a review, so the current snapshot has no full-scope clean result.

The Claude backend's committed-diff coverage defect is tracked in [issue #538](https://github.com/cboone/agent-harness-plugins/issues/538).

## Round 3

Second run, round 1 of 3.

Snapshot: `4bb5d025b66f477dcae8f00dc6094c6ae3c213a6`
Invocation: `codex exec --sandbox read-only --ephemeral --output-schema <temporary schema> -o <temporary findings> <full-scope prompt> < /dev/null` (`codex-cli 0.159.2`)
Coverage: full. The committed range `d8a75266...52ec37c8` is the whole scope; the staged, unstaged, and untracked buckets are empty. Codex exited 0, the findings file validated against the schema, and `reviewed` matched the snapshot.

- [x] **F3** Important. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:37`. The fast Requirements gate skips issue comments when earlier sources state what the PR must do, which is looser than the plan's acceptance-criteria rule.
      Evidence: the fast table row reads comments, parent issues, and sub-issues only when the PR and closing-issue bodies "do not state what the PR must do"; the plan's Requirements row says "only when those sources do not state acceptance criteria". A goal-only title such as "Improve login" passes the looser gate, so acceptance criteria stated in issue comments are never read.
- [x] **F4** Important. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:42`. Fast mode can leave installation or configuration instructions unread in a PR that also changes code.
      Evidence: lines 38 and 42 require complete reads of low-risk documentation only when it holds the sole substantive change. A README prescribing an unsupported configuration value beside a correct code change goes unread, and the verdict can still be "No blockers found".
      Fixed in `f4408477`: fast mode now reads installation, configuration, and upgrade instructions as substantive in both the table and the reading rule, and the README says the same.

F3 fixed in `f4408477`: the fast gate now reads the other sources only when earlier sources do not state acceptance criteria, and says a goal or title alone is not acceptance criteria. The README matches.

## Round 4

Second run, round 2 of 3.

Snapshot: `1c8dbec9b57a941b8573df9508e460f6fcc6f8ed`
Invocation: `codex exec --sandbox read-only --ephemeral --output-schema <temporary schema> -o <temporary findings> <full-scope prompt> < /dev/null` (`codex-cli 0.159.2`)
Coverage: full. The committed range `d8a75266...f4408477` is the whole scope; the other buckets are empty. Codex exited 0, the findings file validated, and `reviewed` matched the snapshot.

- [x] **F5** Important. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:42`. Fast mode can skip changed snapshots and fixtures that serve as test expectations when code also changed.
      Evidence: the fast reading rule reads tests but lets low-risk assets such as snapshots go unread when another substantive file changed (lines 38 and 42), so an updated snapshot that accepts a regression can pass CI unseen while the verdict is "No blockers found".
      Fixed in `5119a1a9`: tests now include the snapshots, golden files, and fixtures they assert against, in the table, the reading rule, and the README.

## Round 5

Second run, round 3 of 3.

Snapshot: `610663c0b848379d8e53dbc32fca87048154b148`
Invocation: `codex exec --sandbox read-only --ephemeral --output-schema <temporary schema> -o <temporary findings> <full-scope prompt> < /dev/null` (`codex-cli 0.159.2`)
Coverage: full. The committed range `d8a75266...5119a1a9` is the whole scope; the other buckets are empty. Codex exited 0, the findings file validated, and `reviewed` matched the snapshot.

- [x] **F6** Important. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:37`. Fast mode skips issue comments once the PR or closing-issue bodies state some acceptance criteria, so a core criterion added later in a comment is never checked.
      Evidence: the fast Requirements row skips comments when earlier sources state acceptance criteria; step 6 treats an unmet core requirement as a Before merge concern, but a criterion in a skipped comment never reaches that assessment. The skipped source is disclosed, but the verdict can still be "No blockers found".
      Declined: skipping comments once acceptance criteria are stated is the fast-mode trade-off the plan chose, and the skipped source is disclosed under Requirements. Thorough mode reads every source.
- [x] **F7** Important. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:42`. Fast re-reviews can leave unread a low-risk file that an earlier point is about, so they cannot report whether that point was addressed.
      Evidence: the fast reading exception reads low-risk files only when they hold the sole substantive change, while re-review requires reporting the status of each earlier point (lines 297 and 308), with no exception for files those points concern.
      Fixed in `853db72b`: a fast re-review now reads the complete diff of any file an earlier point concerns, in the table, the reading rule, and the README.

## Result of the second run

Second run: three rounds, each with full coverage of the committed scope and valid Codex output bound to its snapshot. F3, F4, and F5 were fixed in `f4408477` and `5119a1a9`. The round limit was reached with F6 and F7 open, so there is no clean result for snapshot `610663c0b848379d8e53dbc32fca87048154b148`.

F6 questions the fast-mode trade-off itself: skipping comments once acceptance criteria appear is the plan's design, and it is disclosed under Requirements. After the run, F6 was declined to keep that trade-off. F7 was fixed in `853db72b` with a narrow exception: on a re-review, fast mode reads the files that earlier points concern.
