# Resource claims cause ledger

## Authority and scope

- Issue: [Concurrent resource claims lose an update](https://github.com/cboone/agent-harness-plugins/issues/656).
- Go-ahead: Chris, Inbox, 2026-10-28 at 7:38 PM ET, thread "Tooling next batch, Oct 28 evening": build through a ready PR. TOOLING merges.
- Branch: `fix/656-resource-claims-cause`, based on main at `a2e56c53`.
- Full local review order required; no review rounds started.
- Nighttime checkpoint: approximately 9:45 PM ET.

## Initial evidence

Ownership verified: origin is `cboone/agent-harness-plugins`, neither archived nor a fork. Read issue body and all six comments. `corepack yarn install --immutable` passed.

The source never breaks stale locks, exits on its bounded wait timeout, reads only after acquiring the lock, and creates its temporary file beside the destination. No source cause is established yet. Existing Docker images checked locally lack jq; no software installed.

The original parallel case now validates both resource names in the final JSON before declaring success. On any missing claim or writer failure it prints each writer's status and retained output, and the final file contents. Affected Scrut document: 100 succeeded, 0 failed, 0 skipped on macOS.

The brief explicitly permits a temporary Linux CI debug job. A temporary branch-push workflow runs 1,000 pairs across ten isolated jobs against the unchanged production writer, retains Bash traces on loss, and sets TMPDIR to `/dev/shm` while claims live on the runner's normal temporary filesystem. Remove this workflow before the PR. This diagnostic push precedes local review under that explicit exception; subsequent history stays intact.

## Linux reproduction

[Baseline run](https://github.com/cboone/agent-harness-plugins/actions/runs/40789830676), diagnostic commit `757a4310`: 368 lost claims in 1,000 pairs (36.8%), zero writer errors in 2,000 writers. Per-shard losses: 46, 14, 8, 44, 30, 18, 45, 43, 54, 66. Every shard completed normally and reported losses.

The retained trace for shard 5, pair 0, shows both writers successfully executing plain `mkdir` on the identical lock path, immediately installing the EXIT trap and reading an absent claim file. Neither enters the retry body. Both serialize a single resource and return 0; final JSON holds only `logic`. This narrows the next experiment to direct competing mkdir calls, with utility versions recorded. It does not yet establish which utility behavior causes both apparent acquisitions.

## Confirmed cause and design gate

[Primitive run](https://github.com/cboone/agent-harness-plugins/actions/runs/40790111891), commit `064b86c1`, shard 1: Bash 5.3.9, `mkdir (uutils coreutils) 0.10.0`, `mv (GNU coreutils) 9.7`. Directly racing plain mkdir on one path gave 98 double-success results in 1,000 pairs. Resource-writer stress in that shard lost 48/100 claims with zero writer errors. An existing local Linux image with GNU mkdir 8.32 gave zero double-success results in 1,000 direct pairs.

The [uutils 0.10.0 source](https://github.com/uutils/coreutils/blob/0.10.0/src/uu/mkdir/src/mkdir.rs) confirms the failure: `create_single_dir` handles `Err(_) if path.is_dir()` as success without checking `config.recursive`. If both commands pass the earlier existence check, one creates the directory and the other gets a creation error, sees that directory and returns success. The current upstream source adds the missing recursive guard. No third-party issue or other write was made.

The primitive is unsafe on this runner, so the existing correct placement of read/modify/write inside the directory lock cannot serialize writers. Stale-lock removal and lock timeout do not cause this reproduction. TMPDIR is on a separate filesystem, but the source still creates its temporary file beside the destination; GNU mv is not needed to reproduce the primitive failure.

Stop: design decision required before changing the lock protocol. Proposed direction for TOOLING: retain the bounded wait and directory/owner diagnostics, but require exclusive Bash noclobber creation of the owner file before entering the critical section. Cleanup must remove only the owner's file and use rmdir, rather than recursive removal that could remove a succeeding owner. This needs a deterministic stub that reports mkdir success to both writers, including acquisition/release interleavings, and a plant restoring the old protocol. No production edit, regression implementation, review round, Semgrep, full suite, version bump or PR exists yet.

The branch has two diagnostic commits already pushed. Preserve their history; tidy must not rewrite them. The temporary workflow remains available for the post-fix Linux run and must be deleted before the PR. Next steps after a relayed design decision: implement the selected protocol, deterministic regression and plants; obtain an after-fix Linux loss rate; remove the workflow; run the full review order and required checks; open a ready PR and report to TOOLING. TOOLING merges.

## Local artifacts and processes

Created artifacts: `/tmp/656-resource-claims-ci-watch.log`, `/tmp/656-resource-claims-linux-job.log`, `/tmp/656-resource-claims-linux-baseline.log`, `/tmp/656-resource-claims-primitive-watch.log`, `/tmp/656-resource-claims-linux-primitive.log`. CI watch sessions `97541` and `85923` observe the two diagnostic runs; the first completed with exit 1 as expected. Test session `48479` and push sessions `15839`, `89019` completed. No local child processes stopped. No software installed or real user config changed.

## Approved protocol and repository sweep

TOOLING approved exclusive Bash noclobber owner-file creation, bounded wait and existing diagnostics, and owner-file removal followed by rmdir. The directory operation no longer establishes ownership. Resource claims still never automatically reclaim an owner by PID or age. This avoids a stale observer deleting a live successor; the deterministic fixture waits at a stale owner, replaces it with a live owner, resumes the waiter and verifies refusal with that owner intact. The fixture also forces false mkdir success and acquisition between owner removal and rmdir.

The uutils mkdir 0.10.0 defect is success on EEXIST without `-p`. TOOLING reports it to Chris; no upstream filing is authorized or made. The temporary workflow will be removed in its own commit before the PR.

The sweep searched mkdir, noclobber, set -C, flock, lockfile, lock, mutex, semaphore and reservation patterns across canonical scripts, skills, references, repository tools and generated Codex mirrors. Generated paths are rebuilt rather than edited.

| Surface                                               | Disposition                                                                                                                                                                                                                                                                                                                      |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| workmux resource claims                               | Fixed with exclusive owner creation, bounded wait, nonrecursive release and deterministic race tests.                                                                                                                                                                                                                            |
| publish-report-board bugs-gather cache save           | Fixed with the same protocol; regression forces false mkdir success while another owner exists.                                                                                                                                                                                                                                  |
| attention-log session and rotation locks              | TOOLING approved the owner protocol for acquisition in both locks, preserving PID/age automatic recovery. Implementation is pending the cleanup recurrence decision below. The existing reclaim race remains the known follow-up [attention-log stale-lock reclaim](https://github.com/cboone/agent-harness-plugins/issues/673). |
| notify completed directory                            | Left and reported: a persistent one-shot notification reservation, with no owner release. It shares the mkdir double-success risk, but needs its own notification deduplication regression and migration decision for existing markers.                                                                                          |
| workmux launch-workmux handoff directory              | Left and reported: a persistent completion/timeout handshake, rather than a reusable lock. It shares the mkdir double-success risk; changing it requires preserving detached child completion, timeout evidence and cleanup ownership.                                                                                           |
| review-until-clean save-ledger                        | Unchanged: reserves names using Bash noclobber, and checks existence only after reservation fails.                                                                                                                                                                                                                               |
| publish-report-board report-board output reservation  | Unchanged: exclusively reserves output names with Bash noclobber; existence checks only select another name after failure.                                                                                                                                                                                                       |
| review-scope Git index locks                          | Unchanged: Git manages its own locking inside a private temporary directory.                                                                                                                                                                                                                                                     |
| Other mkdir calls, skill/reference examples and tests | Directory preparation or deterministic fixture setup, not ownership claims. No other shell mutex found.                                                                                                                                                                                                                          |
| dist/codex and .agents mirrors                        | Canonical fixes regenerated with make build. Unfixed canonical surfaces remain identical in their mirrors.                                                                                                                                                                                                                       |

Initial affected checks after implementation: resource claims 103/103 cases; bugs-gather 86/86 cases. ShellCheck passed for both production scripts and the three fixture scripts. No review rounds started.

| Planted defect                          | Instrument expected                  | Measured result                         | Permanent test                                             |
| --------------------------------------- | ------------------------------------ | --------------------------------------- | ---------------------------------------------------------- |
| Restore mkdir-only resource acquisition | Forced false-success interleaving    | Scrut exit 50, only logic remained      | A false successful mkdir cannot admit a second owner       |
| Restore recursive resource release      | Paused release versus live successor | Scrut exit 50, successor owner missing  | Releasing a directory cannot remove a succeeding owner     |
| Restore mkdir-only cache acquisition    | Existing-owner fixture               | 85 passed, new case failed; make exit 2 | Save refuses an owner even when mkdir incorrectly succeeds |

Both production sources were restored byte-for-byte after plants. The resource false-success and release fixtures then passed with PATH selecting macOS Bash 3.2 for every Bash process. Plant artifacts: `/tmp/656-plants.IPboSq`; logs retain each named assertion failure. No plant was committed or pushed.

## Linux comparison after the fix

[After run](https://github.com/cboone/agent-harness-plugins/actions/runs/40791026703), head `7bcd5928`: the same ten shards of 100 concurrent pairs completed with 0/1,000 lost claims and zero errors in 2,000 writers. Before: 368/1,000 losses (36.8%). After: 0/1,000 (0%). This measures the tested workload, not every possible interleaving.

The direct mkdir positive-control arm still produced double success in every shard: 50, 5, 4, 6, 8, 11, 3, 8, 9, 3 per 1,000 mkdir pairs. Therefore the diagnostic workflow reports failure overall as intended; all ten resource-claim stress steps passed. That workflow is not a passing acceptance check. Full log: `/tmp/656-resource-claims-linux-after.log`. Both diagnostic watches completed.

The temporary workflow was deleted in its own signed commit before starting local review. No debug workflow will be in the PR tree.

## Local review: structural Nit round

Ran anti-patterns and report-only simplify in parallel using fresh standalone Codex contexts, gpt-6.1-sol, high effort, window 872000, read-only sandbox, approval never, web search disabled, stdin closed. Project instructions explicitly select this path for Codex workers. Both processes exited 0 with nonempty schema-valid JSON. Anti-patterns reported success and complete coverage. Snapshot `81ca85fe8c2b873bd951a7e6e1b7c467eb564115`; before/after comparison found no lasting tree or scope changes. Installed helper used because the helper refuses execution from inside the repository under review.

| Reviewer's label                                                                                    | Our severity                                                                              | Take or record                                                                                                  | Review again                                                   |
| --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| important: Docs drift: shell review guidance still endorses the disproven mkdir ownership guarantee | Important: guidance could cause a reviewer to dismiss the established concurrency failure | Take: replace the false mkdir assurance with exclusive owner-file acquisition and nonrecursive release guidance | No: documentation only                                         |
| suggestion: write-bash-scripts: Extract complex conditions into one acquisition predicate.          | Nit: duplicated expressions behave identically                                            | Take: use one try_acquire_lock predicate at the existing two attempt sites                                      | No: same attempts, retry order, errors and ownership condition |
| suggestion: write-bash-scripts: Extract complex commands to consolidate repeated barrier waits.     | Nit: fixture polling duplication                                                          | Take: consolidate the three added polling loops, retaining real sleep, bounds, messages and caller actions      | No: behavior preserved                                         |

Structural loop end: **ended: fixes changed no behavior**. No second round is authorized by the advancement rule. The focused review reads the resulting source and guidance. Types aspect is inapplicable because no type definitions changed; code, errors, tests and comments apply.

## Local review: focused Nit round

Code, errors, tests and comments ran in parallel through the installed codex-aspects helper with explicit gpt-6.1-sol/high/872000 and read-only settings. All four processes exited 0 with validated, nonempty output. The scope comparison found no lasting tree or scope changes. Raw artifacts: `/tmp/656-focused.6vvQfv`.

| Reviewer's label                                                                                             | Our severity                                                                | Take or record                                                                                                                                                                                | Review again                                                     |
| ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| important: write-bash-scripts: Checked commands: Owner-write failures leave persistent locks.                | Important: filesystem failure leaves later claim/cache writers blocked      | Take: reserve an empty owner exclusively, register cleanup before recording the PID, and remove only an empty directory after failed reservation                                              | Yes: error-path behavior changes; first Important round required |
| important: write-bash-scripts: Checked commands: Owner-file I/O failures are misreported as lock contention. | Important: storage errors lose their diagnostic and leave a lock            | Take with the preceding code finding: retain creation diagnostics, register ownership before PID write and apply the same handling to cache saving                                            | Same fix and same next round                                     |
| important: write-bash-scripts: Checked commands: Lock cleanup hides unexpected directory-removal failures.   | Important: a failed cleanup returns success and leaves a blocking directory | Take: suppress only a visible successor or a disappeared lock in a searchable parent; otherwise report the underlying error and manual-cleanup need, and propagate failure from the EXIT trap | Yes: exit status and error reporting change                      |
| suggestion: write-bash-scripts: Checked commands lacks coverage for owner-file write failures.               | Nit: missing tests for the change's own filesystem boundaries               | Take: creation, PID-write and rmdir fault cases in both writers, asserting status, diagnostic, data and lock state                                                                            | Covered by the behavior-fix round above                          |

The comments aspect found no issues. Initial I/O cases passed: claims 106/106 and cache 89/89. Fixture stubs are committed with the tests and each case verifies stub resolution. Owner-creation failure uses an actually unwritable directory; PID writing and rmdir use explicit injected failures. A parent search-permission guard and best-effort cache unlock were added after that run; final checks must cover them. The first Important round is recorded below.

I/O plant artifacts: `/tmp/656-io-plants.V54RIW`. Extracted permanent helpers and the three new fault cases from each Scrut document; unmodified controls passed 5/5 cases each. Every plant passed Bash syntax validation, ran against the real production script and was restored before the next plant. Both restored sources matched their saved copies byte-for-byte.

| Planted defect                                                    | Measured result                             | Permanent assertion                                                           |
| ----------------------------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------- |
| Omit resource empty-directory cleanup after failed owner creation | make exit 2, creation case failed           | Owner creation errors retain the filesystem diagnostic; lock must be absent   |
| Omit resource ownership cleanup registration before PID write     | make exit 2, write and cleanup cases failed | Owner write errors release the exclusively reserved file; lock must be absent |
| Return success from resource cleanup failure                      | make exit 2, cleanup case failed            | Unexpected directory cleanup errors propagate after the write; exit must be 1 |
| Omit cache empty-directory cleanup after failed owner creation    | make exit 2, creation case failed           | Save reports owner creation errors without leaving a lock                     |
| Omit cache ownership tracking before PID write                    | make exit 2, write and cleanup cases failed | Save releases its owner when PID recording fails                              |
| Return success from cache cleanup failure                         | make exit 2, cleanup case failed            | Save propagates unexpected lock-directory cleanup errors; exit must be 1      |

## Local review: first Important round and recurrence stop

All four aspects completed through the same installed helper and explicit read-only gpt-6.1-sol/high/872000 settings. Every process exited 0 and validated. Before/after scope comparison found no lasting tree or scope changes. Raw artifacts: `/tmp/656-important-one.PeIIUH`; helper session 79990 completed. No review processes remain running.

| Reviewer's label                                                                                         | Our severity                                                                     | Take or record                                                                                                                                                                                                                                                           | Review again                                                                                                                                        |
| -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| important: write-bash-scripts: Checked commands: Normal lock handoff can falsely report cleanup failure. | Important: both writers can exit 1 after a successful save during normal handoff | Stop for a structural decision. A successor can remove its owner after rmdir returned ENOTEMPTY but before the current existence check; the remaining empty directory is then misclassified as an unexpected failure. Both resource and cache cleanup share this defect. | Count persists: first Important round spent; continue only after TOOLING's decision. Another behavior fix would require the second Important round. |
| suggestion: write-bash-scripts: Checked commands: Cache cleanup lacks a successor-handoff test.          | Nit: the change's own cache handoff boundary lacks direct coverage               | Take with the approved structural fix after the stop is cleared. Resource handoff coverage does not exercise the separate cache implementation.                                                                                                                          | No separate round for a test-only addition; the behavior fix controls advancement.                                                                  |

Code reported the Important recurrence; errors and comments found no findings. Tests reported the missing cache handoff test. The recurring class is cleanup-result classification, addressed in the preceding Nit round but still incorrect for another successor interleaving. Loop end: **stopped: recurring defect**. No fix for these findings has been applied.

Design question sent to TOOLING: later filesystem observations cannot recover the errno from an earlier rmdir call. A directory used only for preparation, with owner-file exclusivity as the complete mutex, would make an empty leftover directory harmless; acquisition could prepare it with mkdir -p and release the owner file, with directory cleanup treated separately. This changes the directory-lifetime and cleanup-error policy, so it is proposed, not implemented. Retaining mandatory directory removal and exact error propagation instead needs a reliable way to distinguish ENOTEMPTY/ENOENT from genuine removal errors using that attempt's result, not another exists check. No dependency or software installation is authorized.

Resume state: local head includes the source fix, I/O regressions and plants; remote still ends at diagnostic source commit 7bcd5928. The temporary workflow remains deleted locally in its own commit. No PR exists. Trims, Semgrep baseline, final lint/full suite, version verification, tidy and publication have not run. The original Linux comparison remains 368/1,000 before and 0/1,000 after the core exclusive-owner fix, at the exact commits recorded above; it is not validation of subsequent cleanup-policy changes.

## Sweep authorization received during the stop

TOOLING confirmed the cache-save fix and expanded the acquisition fix to attention-log's session and rotation locks. Preserve their PID-and-age automatic recovery, unchanged in policy and no less safe than before; do not remove auto-recovery. TOOLING filed the existing reclaim race as [attention-log: stale-lock reclaim can remove a live successor's lock](https://github.com/cboone/agent-harness-plugins/issues/673), verified open. Cite it in the PR body as a known follow-up; this PR must not claim to fix or close it. Patch-bump every changed plugin. The existing workmux and publish-report-board bumps are already present; attention-log will need a forward patch bump from 1.0.0. The fixture plan is approved.

This sweep instruction does not decide the separate cleanup-result recurrence. No attention-log source change has been made while that structural gate remains open. Both authorizations and the existing review counts must carry into the resumed work.

## Approved structural resolution

TOOLING cleared the recurrence stop: the exclusive owner file is the complete mutex; directories are reusable preparation made with mkdir -p, and converted writers never remove them. Release unlinks only the owner file, so no later directory observation can reclassify a successful save. This applies to resource claims, cache saves and both attention-log acquisitions. The next focused review is Important 2; another cleanup or ownership interleaving finding requires a new stop. No round counts restart.

Resource claims and cache saves register cleanup after exclusive empty-file reservation and before recording the PID. Creation failures retain their diagnostic, with an ownerless preparation directory permitted to persist; failed PID recording unlinks the reserved owner. Owner-unlink errors propagate. All rmdir calls and cleanup-result classification are removed from these writers.

Attention-log uses exclusive pid/owner files for session and rotation acquisition. Its stopped-PID and age-based automatic recovery remain enabled, now observing the owner file rather than directory lifetime. The known check-then-unlink reclaim race remains [the separate attention-log follow-up](https://github.com/cboone/agent-harness-plugins/issues/673), not a closing reference. Its existing hook interface still always exits zero; low-level release returns the unlink result, and no hook registration or live config was changed. Versions: workmux 1.1.2, publish-report-board 1.3.2, attention-log 1.0.1 in both manifests.

### Reader and diagnostic audit

| Surface                                            | Owner-file interpretation                                                                                                                                |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| resource acquire_lock / try_acquire_lock           | mkdir -p prepares the directory; only noclobber reservation grants ownership. No directory-existence contention check remains.                           |
| resource held_lock_report                          | Reports the owner-file path and instructs removal of that file, rather than the directory.                                                               |
| cache acquire_save_lock timeout                    | Reports the owner file to remove; an empty save.lock directory does not block a save.                                                                    |
| attention lock_session / unlock_session            | pid is the exclusive owner, liveness input and release target; an empty session lock directory is free.                                                  |
| attention unrecorded-owner age / rotate_events age | Age checks target pid or owner, preserving recovery thresholds while excluding preparation-directory lifetime.                                           |
| attention pending / session-end readers            | Existing production readers use .open/.name files, not lock directories. The SessionEnd regression now counts files and permits preparation directories. |
| resource and attention release assertions          | Check owner-file absence, with preparation directories explicitly retained.                                                                              |
| cache listing and refusal fixtures                 | Listing includes save.lock; refusal fixtures create an owner file. Creation/write fault cases assert owner absence rather than directory removal.        |
| workmux create-worktree / start-issue guidance     | Explains persistent preparation directories and exclusive owner files; ignore globs still cover both.                                                    |
| shell review guidance / attention README           | Replace directory-removal assumptions, explain reusable preparation and link the known reclaim limitation.                                               |
| generated Codex mirrors                            | Rebuilt from canonical sources and guidance; no hand edits.                                                                                              |

### Structural regression coverage

Resource interleaving tests cover a live successor and a successor that has already released before the prior cleanup returns. A new cache fixture exercises both orders with real saves, checks both statuses, verifies the live successor's owner and validates the second writer's data across all three cache files. Both fixtures install rmdir sentinels and assert no attempt to remove the preparation directory, preventing the entire recurring error-classification path from returning.

Attention tests force mkdir success while a live session owner or fresh rotation owner exists. They assert the owner survives and protected marker/rotation work is not performed. Existing stopped-owner and aged-rotation recovery cases remain enabled. Initial affected runs: resource 107/107, cache 91/91, attention 56/56. Earlier failures were only directory-listing assertions; they were updated to the explicit new directory-lifetime contract, preserving owner and data assertions. No source behavior failure was observed in those runs.

Final plant controls extracted from the committed permanent tests passed: resource 5/5, cache 5/5, attention 3/3. Artifacts: `/tmp/656-final-plants.mP5UsB`. To verify the structurally revised source on Linux, the temporary diagnostic workflow is reinstated for one final comparison using the same ten shards of 100 pairs. It retains the branch-only trigger, read-only token and pinned checkout; it installs no software. The already-proven primitive-defect arm is omitted, so the final stress result can pass independently. Remove this workflow again in its own commit before Important 2 and the PR. Diagnostic pushes remain the brief's explicit pre-review exception; preserve pushed history.
