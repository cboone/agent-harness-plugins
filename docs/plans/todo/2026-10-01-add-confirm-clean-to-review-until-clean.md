# Add `--confirm-clean` to review-until-clean

## Context

A reviewer's output varies between runs over identical code, so one clean round is a sample, not proof. `monitor-pr` already handles this with `--confirm-clean` (two consecutive clean Copilot reviews against the same head; any push resets the pair). `review-until-clean` has no equivalent. Add the same opt-in option, keeping a single clean round as the default.

## Semantics

- **Off by default.** Without the flag, behavior is unchanged.
- **Two consecutive clean rounds against the same snapshot.** The first clean round (including `clean-with-declines`) does not end the run. Run a confirming round from step 1 with the same backend, same coverage choice, no fix pass in between. The pair completes only if step 8 finds the second round clean and the snapshot unchanged from the first.
- **The confirming round always runs**, even when the first clean round used the last of `--max-rounds` (user decision). It uses a round from the budget when one is left; otherwise it runs as one round past the cap. If it turns up findings and rounds remain, fix them and the count resets to zero. The round past the cap is review-only: step 8 records its findings and ends `stopped` without reaching the fixer, and it does not run at all if the snapshot moved after the last clean round, which also ends `stopped` (the status table covers both cases).
- **Snapshot check at the start of the confirming round.** Compare its starting snapshot with the first clean round's; a mismatch resets the pair, and the round is an ordinary round while the budget allows.
- **Any snapshot movement resets the pair**, whatever its source (fix, formatter, another session). Step 8's existing invalidation rule already discards that round; the confirmation count also returns to zero.
- **Terminal status:** statuses do not change. `clean-with-declines` if either round of the pair relied on carried declines, else `clean`. The report and ledger name both rounds and their shared snapshot so the confirmation is visible. Coverage rules unchanged (`partial scope` still applies).
- **With `--report-only`:** still no edits. If the first round is clean and the snapshot has not moved, run the confirming round too; otherwise stop after one round. It has no round budget and never reports `stopped`: a moved snapshot leaves the clean result unconfirmed, and confirming-round findings are reported like a first round's.
- **Failed rounds:** unchanged. A confirming round with empty or unparseable output ends `failed`, never confirmed.

## Changes

1. `plugins/review-until-clean/skills/review-until-clean/SKILL.md`
   - Options: add `--confirm-clean`, phrased like `monitor-pr`'s ("Require two consecutive clean rounds rather than one ...").
   - Step 8: after "If the round is clean, go to step 11", branch: under `--confirm-clean` and the first clean round of a pair, record it and start the confirming round at step 1 instead. Mention the reset.
   - Step 10: note the confirming round is exempt from `--max-rounds`.
   - Step 11 / Example Output: show a confirmed run (e.g., `Round 3 of 3 (confirming 2/2)` and a status line noting confirmation by rounds 2 and 3).
   - Error Handling: add "the confirming round finds something".
2. `references/stop-rules.md`: new `## Confirming a clean result` section (why, the pair rule, reset rule, budget exemption, status mapping); adjust the round-limit bullet in Convergence and the "What a clean result does not mean" section to mention two passes.
3. `references/ledger.md`: header gains `Confirmation: <off | rounds N and M over snapshot X | unconfirmed>`; round sections mark a confirming round; Result section names both rounds.
4. `plugins/review-until-clean/README.md`: usage synopsis, option table row, an explanatory paragraph under "What it reports" modeled on `monitor-pr`'s README, and an example line.
5. `plugins/review-until-clean/.claude-plugin/plugin.json`: `1.0.0` -> `1.1.0` (new capability; no `.codex-plugin` manifest exists). Catalog description unchanged.
6. `make build` to regenerate `dist/` and `.agents/` mirrors; commit them.

No script changes: `review-scope` already supplies the snapshot that the pair is bound to, so no scrut changes are needed.

Load `write-markdown` before the Markdown edits. Commit at logical boundaries with signed Conventional Commits (`feat:` for the skill, `chore:` for the version and mirrors, `docs:` for the plan).

## Verification

- `make build`, then `make test-all` (lint, validate incl. cross-references, scrut); observe the final result.
- Run the `check-versions` skill.
- Read the rendered SKILL.md flow end to end for the three paths: default (one clean round ends), confirmed (two clean rounds, same snapshot), and reset (confirming round finds something; and when no rounds remain, ends `stopped`).
