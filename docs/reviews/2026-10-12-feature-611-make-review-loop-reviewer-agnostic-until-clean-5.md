# Review until clean: feature/611-make-review-loop-reviewer-agnostic

Base: main (b89fff26447e3f9064ce81997f5a9a1620b6106f)
Reviewer: /review-anti-patterns (from --reviewer)
Rounds: 3 of 3
Status: stopped
Confirmation: off

This is the fifth run on this branch today; the earlier ledgers are `2026-10-12-feature-611-make-review-loop-reviewer-agnostic-until-clean.md` and `-until-clean-2.md` to `-until-clean-4.md`. No declines are carried into this run.

## Round 1

Snapshot: 2b068f9eb20acecd4570a4fd3457d54375c1a4d2
Invocation: /review-anti-patterns, default scope, `--severity nit`, no `--run-checks`; run by a general-purpose subagent following the skill, which could write and was read-only by instruction
Mode: report (snapshot unchanged when the reviewer returned; working tree clean)
Coverage: full (the reply reviewed `b89fff2..working-tree`, `complete: true`, `not_reviewed` empty; `dist/` and `.agents/` excluded as generated)

Reviewer reply: 27,030 bytes, stored in full beside this ledger as `2026-10-12-feature-611-make-review-loop-reviewer-agnostic-until-clean-5-round-1-reply.txt` because of its length. It opens with a fenced JSON block, `"status": "success"`, `"complete": true`, 18 findings, and ends with "**Result:** not clean. There are three Important findings (1-3) and fifteen Nits. `status` is success and `complete` is true."

- [x] **F1** Important. `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md:70`. The shell recipe puts the `--reviewer` value inside single quotes, so a value containing a quote ends the string early and the rest runs in the caller's shell, outside the redirects; `reviewer` ends up empty and the round reads as a failed review rather than a quoting error.
      Fixed in c7414f68.
      Evidence: reproduced under bash and zsh with a `jq '...'` pipeline value: `tostring: command not found` from the caller's shell, then status 0 and empty output.
- [x] **F2** Important. `plugins/review-until-clean/skills/review-until-clean/SKILL.md:74`. The repository default reviewer is read, without confirmation, from an `AGENTS.md` or `CLAUDE.md` that can be part of the change under review, so a branch can choose its own reviewer, for example `printf 'No findings.\n'`, and get a clean result.
      Fixed in c7414f68.
      Evidence: step 2 option 2 has no confirmation; a shell reviewer counts as finished on exit 0 and non-empty output.
- [x] **F3** Important. `plugins/review-until-clean/skills/review-until-clean/references/ledger.md:57`. An edit round's `Changed:` paths and its recorded findings have no defined format, and `address-review` treats plain bullets and numbered lists as actionable, so they enter its queue and shift the `--skip` numbering onto the wrong items.
      Fixed in c7414f68.
      Evidence: address-review's SKILL.md lists unchecked bullets and numbered lists as actionable; ledger.md:67 describes its parser too narrowly.
- [x] **F4** Nit. `references/reviewers.md:47`. "Non-empty output" does not say which stream; a reviewer that exits 0 with only stderr progress lines reads as finished.
      Fixed in c7414f68.
- [x] **F5** Nit. `references/reviewers.md:17`. The example `coderabbit review --plain` uses a flag CodeRabbit CLI 0.9.0 does not list; plain text is its default, and `--fresh` suggests the default may reuse a checkpoint across rounds.
      Fixed in c7414f68 and 20342789.
- [x] **F6** Nit. `SKILL.md:207`. The example output declines a Nit under the default Important threshold and reports `clean-with-declines`, which the stop rules call plain `clean`; predates the change.
      Fixed in c7414f68.
- [x] **F7** Nit. `references/scope-and-snapshot.md:40`. The force-add exception added to reviewers.md was not carried to scope-and-snapshot.md, SKILL.md:52 or README.md:89, which still say staging or unstaging never moves the snapshot.
      Fixed in c7414f68, e394dcfb and 20342789.
- [x] **F8** Nit. `references/ledger.md:89`. It says `review-scope --schema` enforces the location rule for reviewers that emit the schema, but nothing validates reviewer output against the schema any more.
      Fixed in c7414f68.
- [x] **F9** Nit. `plugins/review-pr-with-codex/scripts/review-scope:72`. The shared comment points review-pr-with-codex's copy to a `references/ledger.md` it does not have.
      Fixed in e394dcfb.
- [x] **F10** Nit. `SKILL.md:58`. Step 1 does not say to record `tree`, which an edit round needs to list changed paths.
      Fixed in c7414f68.
- [x] **F11** Nit. `SKILL.md:115`. Step 6 prints carried declines before step 7 identifies them.
      Fixed in c7414f68.
- [x] **F12** Nit. `SKILL.md:136`. A plain `--report-only` round invalidated by a moved snapshot has no defined outcome.
      Fixed in c7414f68.
- [x] **F13** Nit. `plugins/review-until-clean/README.md:102`. The recommended permissions leave out `git diff-tree`.
      Fixed in 20342789.
- [x] **F14** Nit. `plugins/review-until-clean/README.md:41`. "Before each round" contradicts "asks once" for the `git add -N` offer.
      Fixed in 20342789.
- [x] **F15** Nit. `SKILL.md:181`. "A reviewer that pushes or posts ends the run as failed" rests only on the reviewer's own report; a push could be caught by comparing `@{u}` before and after.
      Fixed in c7414f68.
- [x] **F16** Nit. `SKILL.md:121`. Carrying declines across runs is not defined, yet the fourth run's ledger did it.
      Fixed in c7414f68.
- [x] **F17** Nit. `SKILL.md:239`. Stopping because no reviewer was found or no one answered ends without a status line.
      Fixed in c7414f68.
- [x] **F18** Nit. `docs/plans/todo/2026-10-12-make-review-loop-reviewer-agnostic.md:95`. The plan says "three invariants"; it lists four.
      Fixed in 20342789.

## Round 2

Snapshot: 35dc697d44d4dd5f49727567b934d98af860c689
Invocation: /review-anti-patterns, default scope, `--severity nit`, no `--run-checks`; run by a fresh general-purpose subagent following the skill, read-only by instruction
Mode: report (snapshot unchanged when the reviewer returned; working tree clean)
Coverage: full (`b89fff2..working-tree`, `complete: true`, `not_reviewed` empty; `dist/` and `.agents/` excluded as generated)

Reviewer reply: 19,565 bytes, stored in full beside this ledger as `2026-10-12-feature-611-make-review-loop-reviewer-agnostic-until-clean-5-round-2-reply.txt`. It opens with a fenced JSON block, `"status": "success"`, `"complete": true`, 11 findings.

- [x] **F19** Important. `SKILL.md:183`. The push check compares `@{upstream}`, which an unpushed branch does not have, so a reviewer's plain `git push` under `push.autoSetupRemote` goes unseen; pushes to other refs or tags are missed, and a `git fetch` gives a false positive.
      Fixed in b7ac4f1f.
      Evidence: this branch has no upstream and `push.autoSetupRemote` is true.
- [x] **F20** Important. `references/reviewers.md:75`. The shell snippet keeps `tmp` and `reviewer_status` in shell variables and prints nothing, but each agent Bash call is a new shell, so later steps cannot read them; the call also exits 0 whatever the reviewer did.
      Fixed in b7ac4f1f.
      Evidence: reviewers.md:69-79; nothing echoes either value.
- [x] **F21** Nit. `references/reviewers.md:84`. A quoted heredoc inside `$( )` is not literal under macOS bash 3.2: an apostrophe in a comment or an unbalanced `)` breaks it.
      Fixed in b7ac4f1f.
- [x] **F22** Nit. `references/reviewers.md:47`. A CLI that exits 1 to report findings, as linters do, always makes a failed round, and the no-wrapping advice rules out the workaround.
      Fixed in b7ac4f1f.
- [x] **F23** Nit. `plugins/review-until-clean/README.md:109`. Permission rules for a reviewer's own commands never match, because the reviewer runs inside the wrapper script.
      Fixed in b961a4df.
- [x] **F24** Nit. `references/ledger.md:57`. Edit-round fences are fixed at three backticks, and a changed path containing a newline and a fence can close one and inject a queue item.
      Fixed in b7ac4f1f.
- [x] **F25** Nit. `references/reviewers.md:182`. A full reply stored beside the ledger is left at the temporary path when step 11 moves the ledger.
      Fixed in b7ac4f1f.
- [x] **F26** Nit. `plugins/review-until-clean/README.md:33`. The README's default-reviewer and pre-push sections ignore the new confirmation rule, so a non-interactive hook without `--reviewer` fails every push.
      Fixed in b961a4df.
- [x] **F27** Nit. `README.md:100`. The root README says reviewer edits are always reviewed again; under `--report-only` or at the cap they are not.
      Fixed in b961a4df.
- [x] **F28** Nit. `SKILL.md:244`. Empty scope, no commits and a missing fixer still stop without a terminal status.
      Fixed in b7ac4f1f.
- [x] **F29** Nit. `SKILL.md:85`. Recording the upstream ref is only in Key Conventions, not in steps 4 and 5 that need it.
      Fixed in b7ac4f1f.

Also in b7ac4f1f, at the user's request: declines carry across runs on the same branch, revising the round 1 fix for F16.

## Round 3

Snapshot: 71f010f2f48ffa4f9427a62a6ef7437af76fbcf9
Invocation: /review-anti-patterns, default scope, `--severity nit`, no `--run-checks`; run by a fresh general-purpose subagent following the skill, read-only by instruction
Mode: report (snapshot unchanged when the reviewer returned; working tree clean)
Coverage: full (`b89fff2..working-tree`, `complete: true`, `not_reviewed` empty; `dist/` and `.agents/` excluded as generated)

Reviewer reply: stored in full beside this ledger as `2026-10-12-feature-611-make-review-loop-reviewer-agnostic-until-clean-5-round-3-reply.txt`. It opens with a fenced JSON block, `"status": "success"`, `"complete": true`, 10 findings.

- [x] **F30** Important. `references/reviewers.md:104`. Comparing remote-tracking refs and tags misses a push of an existing tag and a push to a URL or a remote with no fetch refspec, yet SKILL.md promises a pushing reviewer ends the run `failed`.
      Fixed in 81b45dd0.
      Evidence: reproduced in scratch; neither push changed any listed ref.
- [x] **F31** Important. `references/reviewers.md:115`. A reviewer that amends, resets or rebases moves HEAD like a new commit and is handled as an edit round, though SKILL.md says rewriting history ends the run `failed`; no ancestry check exists.
      Fixed in 81b45dd0.
- [x] **F32** Important. `references/reviewers.md:66`. The shell runner sets no tool timeout and prints its temporary path only at the end, so a review longer than the Bash tool's default timeout is cut off and its output lost.
      Fixed in 81b45dd0.
- [x] **F33** Nit. `SKILL.md:93`. Step 5 never says to compare the refs step 4 recorded.
      Fixed in 81b45dd0.
- [x] **F34** Nit. `references/reviewers.md:117`. A concurrent fetch, such as an editor's autofetch, fails the run and is blamed on the reviewer.
      Fixed in 81b45dd0.
- [x] **F35** Nit. `plugins/review-until-clean/README.md:102`. The recommended permissions omit `git for-each-ref`.
      Fixed in 81b45dd0.
- [x] **F36** Nit. `SKILL.md:81`. Step 3's untracked-files question has no rule for a run where no one can answer.
      Fixed in 81b45dd0.
- [x] **F37** Nit. `references/scope-and-snapshot.md:41`. `git reset` of a committed ignored file holds the snapshot; only `git rm --cached`, or a reset of a force-added uncommitted file, moves it.
      Fixed in 81b45dd0.
- [x] **F38** Nit. `docs/plans/todo/2026-10-09-reduce-copilot-rounds-after-pr-opens.md:54`. An open plan still says review-until-clean has Codex and Claude backends.
      Fixed in 261343a8.
- [x] **F39** Nit. `docs/reviews/2026-10-12-feature-611-make-review-loop-reviewer-agnostic-until-clean-2.md:116`. The failed runs' not-queued findings in the -2 and -3 ledgers are plain bullets, which address-review would queue.
      Fixed in 261343a8.

## Result

Stopped at the round limit. No round was clean: round 1 raised 18 findings (3 Important), round 2 raised 11 (2 Important) and round 3 raised 10 (3 Important), all fixed. Round 3's fixes (81b45dd0, 261343a8) were made after the last review and have not been reviewed. Every round reviewed the full scope with `/review-anti-patterns`, run by a fresh subagent each round.

Several Important findings in rounds 2 and 3 were gaps in detection the earlier rounds' fixes had added, around pushes and rewritten history. Round 3's fix stops promising full detection: the skill now states that it relies on the reviewer, and keeps the remote-ref and ancestry checks as best-effort nets.
