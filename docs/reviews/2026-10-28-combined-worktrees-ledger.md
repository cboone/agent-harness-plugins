# Combined worktrees ledger

## Authority and baseline

- Worker: `544-combined-worktrees`, conductor TOOLING. Build through ready PR; never merge.
- Go-ahead: Inbox, 2026-10-28, 7:38 PM ET, relayed in the brief.
- Issue 544 read in full; no comments. Repository active, `cboone` origin, no upstream or fork.
- `corepack yarn install --immutable`: passed.
- Current source already has combined mode in `workmux:start-issue`, replacing the former `address-issue-in-worktree`, and several-issue `address-issue`. Missing: all-issue branch identity and PR detection. Reproduce the current gap and preserve prior fixes.
- TOOLING reaffirmed scope: reproduce against current main and limit work to combined naming, reuse lookup, issue linking and regression coverage. Main already defines combined default, one worktree/session, marking each open issue, per-issue prompt composition with independent body budgets, one chain footer listing all issues, and one plan/approval gate. Those behaviors need regression coverage, not replacement.
- Refetched main still resolves to `a2e56c535ed6326cc8d531d945fbb6c627a9b335`. Executed copies of its actual launcher and composer with guarded committed stubs: two repeated issue flags produced **one** fixture worktree with both prompt bodies and `/address-issue 4523 4503`, but branch `fix/4503-verify-email` lost 4523. Repeated reuse lookup exited 1 with `--resolve-issue-branch takes no other arguments`. Evidence: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/544-main-repro-42f3_2sb`.

## Validation and plants

- Baseline regression: 1/4 passed, 3 failed. Repeated issue flags generated `fix/4503-verify-email`, dropping 4523; repeated lookup was rejected; no PR numeric-segment helper existed. Prompt budget test passed. Current instructions already combine work, so the old two-window behavior was not reproduced.
- Combined fixture: 7/7 passed after implementation. Includes one launch, both prompt bodies and truncation notices, one footer, per-body 2000-character budget, reversed-order lookup and launch reuse, bare names, duplicate removal and PR candidate identities with closing lines.
- `shellcheck` on changed scripts: passed. `make build`: passed.
- Existing launcher suite: 68/68 passed against the restored source. An earlier concurrent run was invalidated by plant rewrites (66/68 with source-reading errors); its result is superseded. Run plants separately from other source consumers.
- Restored combined suite: 8/8 passed. `make validate`: passed after adding the required fixture environment reset; routing description subsequently shortened to remove its budget warning and mirrors rebuilt.

| Planted defect                                  | Instrument                 | Measured result                                | Regression test                                         |
| ----------------------------------------------- | -------------------------- | ---------------------------------------------- | ------------------------------------------------------- |
| Drop the first combined issue while normalizing | Combined branch assertion  | Exit 2; named assertion failed (6/7 passed)    | One launch carries both issue identities and one footer |
| Halve each issue body budget                    | Body budget assertion      | Exit 2; named assertion failed (6/7 passed)    | Each issue has its own body budget                      |
| Remove the chain footer                         | Combined footer assertion  | Exit 2; named assertion failed (6/7 passed)    | One launch carries both issue identities and one footer |
| Match only the primary issue on reuse           | Reversed lookup assertion  | Exit 2; lookup and reuse failed (5/7 passed)   | Rerun finds the combined branch in either issue order   |
| Omit a numeric path segment from PR detection   | Closing identity assertion | Exit 2; closing and parser failed (5/7 passed) | PR branch detection preserves every closing identity    |

Plant logs: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/544-plants-9v_tcinc`. Every source restored after its plant. These are helper-level tests, not a live agent workflow or a published PR body.

## Review rounds

Standing Semgrep rule relayed by TOOLING from the Inbox decision at 9:39 PM ET: a baseline scan that runs to completion but only partly parses shell files counts. Record parse coverage and every unparsed file, and require ShellCheck to pass on those files. Partial parsing in any other language still stops. This exception does not cover a failed or incomplete scan. Keep the required disposable-clone baseline invocation with `--config auto --baseline-commit <merge-base>` and without `--metrics off`.

Structural Nit round, HEAD `f0f89d2e069b4b9ce23912fad01c347fb8b9d7d8`, merge base `a2e56c535ed6326cc8d531d945fbb6c627a9b335`. `review-anti-patterns` and report-only `simplify` ran in parallel, each in a fresh `codex exec`, model `gpt-6.1-sol`, effort `high`, window `872000`, built-in read-only sandbox, approvals never and web search disabled. This follows the project's explicit fresh-Codex review rule. Anti-pattern output passed its JSON/schema check and both commands exited 0. All 16 non-generated changed files read; 10 generated mirrors excluded. No PR exists, verified by the caller. Reviewer metadata lookup was unavailable inside its sandbox; the caller had already verified active, non-fork ownership.

Simplify: no findings, **clean at Nit**. Anti-patterns: two Important findings and one Nit; not clean. Before/after scope trees both `15410ba162a3ef63993a49d3871301ed46e4f995`, with no lasting changes found.

| Reviewer's label and finding                                                     | Our severity and impact                                                                                                                                         | Take or record                                                                         | Review again                                                |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `important`: Parallel paths: fan-out can reuse the same combined worktree twice  | Important: `--fan-out` for 4523 and 4503 independently resolves both to `fix/4523/4503-verify-email`, reopening one worktree twice instead of separate sessions | Take, blocked on conductor's design call. Both workmux skills need the same policy     | Yes, behavior changes; next structural round is Important 1 |
| `important`: Agent-prose control flow: resolve the new helper before invoking it | Important: unsubstituted plugin-root placeholder can invoke `/scripts/branch-issues`, losing PR issue detection in the Codex mirror                             | Take after design gate clears. Follow existing loaded-skill-relative helper resolution | Yes, agent execution behavior changes                       |
| `nit`: Docs drift: PR's recommended permissions omit branch-issues               | Nit: copied permission example does not cover the added helper                                                                                                  | Take after design gate clears; local documentation fix                                 | Docs alone do not require another round                     |

No severity downgrades, recorded defects or recurring defect classes. No fixes from this review have been applied. The structural loop is paused at the design gate, not clean. Full aspect review, trims, Semgrep baseline, final lint/test-all, check-versions, tidy and publication remain unrun. No Copilot requests.

Artifacts: `/tmp/544-reviews.qYzuEG/anti.json`, `anti.log`, `simplify.txt`, `simplify.log` and before/after scope JSON. Launcher rerun: `/tmp/544-launch-restored.log`.

## Handoff

TOOLING requested confirmation of Git's ref namespace collision. Added `combined-ref-collision`, using a fixture-owned bare repository and existing commit objects, with no worktree/window creation or source-repository ref writes. Measured both directions: `fix/4523` prevents `fix/4523/4503-slug`, and the combined child prevents `fix/4523`. `fix/4523-4503-slug` coexists with either. ShellCheck passed on this fixture. The slash naming proposal has this confirmed limitation; prefer hyphen-separated issue numbers when the conductor clears the naming/reuse design. The existing parser and lookup must both understand that format before it can replace the slash format.

TOOLING cleared the design and restart gate: both workmux skills must check duplicate resolved branches during fan-out preflight, before launch or marking; name the issues and branch and ask for distinct explicit branches. No automatic branch selection. The other two review findings are takes. Continue through the ready PR; TOOLING merges.

Implemented that policy with the existing launcher extended by `--check-fan-out-branches`, invoked by both skills. Fixed the PR helper's loaded-skill-relative resolution and permission example. Chose `fix/4523-4503-slug` to avoid the confirmed ref namespace collision, extending the leading-number parser and reuse matching together. Single-issue naming is unchanged. The combined regression document now passes 12/12 cases; changed scripts pass ShellCheck. New plants and structural Important 1 remain next.

Review Nit findings above are historical. All three are taken in this implementation; no downgrade or recurrence. The full aspect review, trims, Semgrep baseline, final lint/test-all, check-versions, tidy and publication remain pending. No push or PR exists.

Fetched `origin/main` remains the original base; no overlapping sandbox PR was open or merged at the resume check. Recheck before continuing review if it lands. Sandbox error paths remain unchanged.

## Design-fix validation

- New plants ran separately from all other source consumers. Logs: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/544-hyphen-plants-h3rpe88k`.
- Disabled duplicate detection: fan-out preflight assertion failed, 11/12 passed, exit 2.
- Removed hyphen normalization: combined and bare branch assertions failed, 10/12 passed, exit 2.
- Removed leading-number-run reuse matching: lookup, launch reuse and fan-out resolution cases failed, 9/12 passed, exit 2.
- Stopped PR extraction after the first number: closing identities and parser cases failed, 10/12 passed, exit 2.
- Every source restored after its plant. Restored suite passed 12/12; make validate passed. Structural Important 1 is next.

## Structural Important 1

HEAD `822501fc8ec793c8e05cf05a7bbff08de4a9f2f4`, base `a2e56c535ed6326cc8d531d945fbb6c627a9b335`. Anti-patterns and report-only simplify ran in parallel with the same explicit high-effort `gpt-6.1-sol`, 872000-token window and built-in read-only sandbox. Both exited 0. Anti-pattern JSON passed its result checker: complete, no findings, nothing unreviewed. Simplify reported no findings or observations. Caller supplied verified repository/PR metadata; remote API access inside the reviewers remained unavailable.

Before/after scope tree `5b379a197e2924bec0f7aee1b9b3ebee5a3cfbec` matched, with no lasting changes found. **Structural loop: clean at Important.** No further structural round is due. Artifacts are `anti-important-1.*`, `simplify-important-1.*` and `important-1-{scope,after}.json` under `/tmp/544-reviews.qYzuEG`.

Next: independent PR aspect Nit round, code/errors/tests/comments. Types skipped because no type or schema definitions changed. Simplify remains report-only in the completed structural loop, not an editing pass.

## PR aspect Nit round

HEAD `bc359e5f`, same merge base. Four aspects ran in parallel through the installed `review-pr-with-codex` 2.1.4 helper, model `gpt-6.1-sol`, effort `high`, window `872000`, built-in read-only sandbox. The repository-local helper first refused execution before any reviewer started; the installed copy was verified executable and byte-identical. All four actual aspect runs exited 0 and passed the helper's result validation. Types skipped because no type/schema definition changed. Before/after scope tree `49f642f36115fe4e459c1dce4336b23d1a6b706a` matched; no lasting changes found.

| Reviewer's label and finding                                                                         | Our severity and impact                                                                                                                                                     | Take or record                                                                         | Review again                                        |
| ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `important`: write-scrut-tests: Combined reuse tests do not prove every issue is required.           | Important: both fixtures used only a last-issue distractor, so checking only the first requested issue still passed. The combined all-issue boundary lacked a negative case | Take: add first-issue-only lookup and launch rejection, then plant first-only matching | No: production behavior is unchanged; test-only fix |
| `suggestion`: write-scrut-tests: Explained tests: Remove the stale repeated-flag defect description. | Nit: present-tense baseline history contradicted the fixed behavior; no runtime impact                                                                                      | Take: describe distinct issue preservation instead                                     | No: documentation-only fix                          |

Code and errors had no findings. No Critical findings, severity downgrades or recurring defect classes. PR loop ends after the takes: **ended: fixes changed no behavior**. No extra aspect round is due. Artifacts: `pr-nit-out/`, `pr-nit-run.json`, and `pr-nit-{scope,after}.json` under `/tmp/544-reviews.qYzuEG`. New negative-case verification and plant are pending; then trims and the remaining checks.

## Final negative case and trims

- Before planting, combined suite passed 13/13. First-only reuse mutation failed exactly the new negative case: 12/13 passed, exit 2. Source restored, then suite passed 13/13 again. Log: `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/544-first-only-plant-vcj5i9oq/result.log`.
- One comment-trim and one prose-trim dry run, in parallel through fresh Codex exec sessions: `gpt-6.1-sol`, low effort, window `872000`, built-in read-only, approvals never, web search disabled. Both exited 0 with the required classified-file lists and complete proposals.
- Comments: no changes proposed. Prose: accepted all three meaning-preserving edits, one redundant helper-location phrase and two sentence splits for phase-1 resume instructions. Conditions, exceptions, paths and commands preserved. No product behavior changed; no additional review round is due.
- Trim artifacts: `trim-comments.*` and `trim-text.*` under `/tmp/544-reviews.qYzuEG`.

## Semgrep baseline

Disposable shared clone: `/tmp/544-semgrep.dlc9vU/repo`, head `66a1eff773e527c9248f2720e80708646dda65f6`, baseline `a2e56c535ed6326cc8d531d945fbb6c627a9b335`, `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`. Ran `semgrep scan --config auto --baseline-commit a2e56c535ed6326cc8d531d945fbb6c627a9b335 --json --output /tmp/544-semgrep.dlc9vU/result.json`, without a metrics override.

Completed successfully, exit 0: 131 rules, 14 targets, zero findings, approximately 73.3% parsed lines. Fifteen changed files were excluded by the configured ignore patterns. The sole partial-parsing path was Bash file `plugins/workmux/scripts/launch-workmux`, reported range lines 3 through 831. No other language had partial parsing. ShellCheck passed on that exact file inside the clone, and it is byte-identical to the worker's source. This completed scan counts under the relayed shell-only exception. JSON and log retained at `/tmp/544-semgrep.dlc9vU/{result.json,scan.log}`. No full-scan substitute was used.

## Final validation plan

Apply `lint-and-fix --no-push` using project check commands. Markdown auto-fix and Prettier write commands reach protected Scrut files and historical plan snapshots, so those writers are downgraded to check mode under the skill's protected-path rule. Changed source prose and shell formatting have already been applied deliberately. `make test-all` runs the documented `make lint` prerequisites, validation and all Scrut documents. Fix any findings in scope by hand; no push from lint. Then record results, check versions, run final lint on the recorded tree, tidy into signed logical commits with exact-tree comparison, and publish the ready PR.

## Final validation results

- `SCRUT_JOBS=4 make test-all`: exit 0. Lint and validation passed; all 43 Scrut documents, 1677 testcases, passed with zero failures or skips. Includes combined 13/13 and existing launcher suites. Log: `/tmp/544-test-all.log`. Tested HEAD `b4b5aac8`; subsequent edits are this record only.
- Check-versions skill: remote default `main`, merge base `a2e56c535ed6326cc8d531d945fbb6c627a9b335`. Forward patch bumps as requested: `address-issue` 1.3.1 to 1.3.2, `pr` 1.11.0 to 1.11.1, `workmux` 1.1.1 to 1.1.2. Marketplace coverage and version ownership passed; generated metadata agrees. Patch level follows the brief's restored-behavior scope.
- Refetched main before publication preparation: still the same base, active public non-fork repository. No overlapping sandbox change has landed, so no rebase is required.
- Lint workflow: all required tools ran, no fixes needed, no push. Markdown write commands were check-only by protected-path policy; no required check was skipped. Final lint will verify this recorded tree before tidy.
- Tidy plan: back up as `fix/544-combined-worktrees-pre-tidy`, reset softly to the verified merge base, rebuild as feature, tests and process-doc signed commits, then require exact tree equality with the backup. Publication follows only after that check; TOOLING merges.
