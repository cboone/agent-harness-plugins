# Monitor PR Continuation Verification

## Manual verification

Record: this section. Append dated readings to each step and update the status table in place. Confirm step 0 at the start of each session. These checks exercise skill execution, conversation retention, and scheduler tools in their actual harness; repository lint and Scrut do not observe those behaviors.

Build under test: monitor-pr 1.3.1 on `fix/monitor-pr-loop-in-codex`. Record the committed SHA, loaded skill path, artifact hashes, harness version, repository, PR number, and checkpoint transcript with each result. If another build is loaded between readings, confirm step 0 again.

### Exclusive resources

- `monitor-pr-verification-pr`: steps 1 to 4. Use a dedicated open PR in a user-owned repository, with no other monitor watch running against it. Record the actual PR URL before running a step. Keep the check and review states named in each setup observable during that step.
- No exclusive resource: step 0, which checks the loaded artifact in a fresh harness conversation.

### Status

| #   | Step                                                  | Status          | Reading                                                                   |
| --- | ----------------------------------------------------- | --------------- | ------------------------------------------------------------------------- |
| 0   | Confirm the loaded build                              | untestable here | Requires a fresh harness session loading the updated skill                |
| 1   | Resume with options and budget intact                 | untestable here | Requires a loaded foreground watch and a controlled pending PR            |
| 2   | Resume after requesting Copilot review                | untestable here | Requires a controlled PR with Copilot available but no current-head run   |
| 3   | Preserve clean-review confirmation                    | untestable here | Requires two observable reviews against one unchanged head                |
| 4   | Fall back after scheduler unavailability or rejection | untestable here | Requires scheduler availability and rejection controls in a fresh harness |

### 0. Confirm the loaded build

- **Setup:** Build the committed branch with `make build`. Identify the canonical monitor-pr skill, checkpoint reference, manifest, and generated Codex equivalents. Use canonical artifacts for Claude Code or OpenCode and generated artifacts for Codex.
- **Action:** Load those artifacts into a fresh harness conversation. Record the source and installed file hashes using `shasum -a 256`, the installed manifest version, and the skill path the harness actually reads. Ask the agent to identify the checkpoint restoration and scheduler fallback instructions from the loaded skill and reference.
- **Expected:** The installed manifest reads `1.3.1`; installed file hashes match the corresponding artifacts from this branch. The harness reads the recorded path and identifies same-conversation checkpoint restoration, retained action guards, and bounded scheduler fallback.
- **Null vs broken:** A matching disk file alone does not establish that the running conversation loaded it. Require the fresh conversation's skill-read evidence and the reference content. Missing artifacts or an older loaded instruction make dependent readings invalid.
- **Why by hand:** The harness selects and caches installed skills; repository validation checks generated files without observing what the active harness loads.
- **Result:** untestable here. 2026-09-16: the current conversation loaded monitor-pr 1.2.0 before these changes; a fresh harness session with the branch artifacts is required.

### 1. Resume with options and budget intact

- **Setup:** Step 0 passed this session. Use a foreground harness and a PR whose checks are running. Begin with `/monitor-pr PR_NUMBER --ticks 1 --rounds 4 --confirm-clean --no-fix --interval 10m`, replacing `PR_NUMBER` with the recorded PR number.
- **Action:** At the first checkpoint, record every watch-state field and the resume command. Run that command in the same conversation. At the next checkpoint, compare options and guard histories with the previous checkpoint. Repeat once by pasting the complete checkpoint and its command into a fresh conversation after confirming step 0 there.
- **Expected:** Each invocation completes one snapshot and dispatch before returning a labelled checkpoint. Both resumption paths preserve `--rounds 4`, `--confirm-clean`, `--no-fix`, `--interval 10m`, and all recorded guard histories. Each new invocation starts its foreground tick count at zero and reaches one at its checkpoint. Reports explicitly remain pending; no fixing skill, push, or review request runs under `--no-fix`.
- **Null vs broken:** Require a new GitHub snapshot in each invocation and matching pending check states, so an inactive watch cannot pass through silence. If any counter was already nonzero, it must remain so unless an ordinary documented state transition changes it. Zero initial counters alone cannot prove budget restoration; step 2 exercises nonzero state.
- **Why by hand:** Actual conversation retention, command interpretation, and selected tool calls are harness behavior, not executable logic covered by the repository's helper tests.
- **Result:** untestable here. 2026-09-16: requires a fresh foreground harness with the updated artifacts and the specified observable PR state.

### 2. Resume after requesting Copilot review

- **Setup:** Step 0 passed this session. Use a dedicated PR with passing checks, no current-head Copilot review, and no queued or running Copilot workflow. The session's test scope permits review requests on that PR. Run `/monitor-pr PR_NUMBER --ticks 2 --rounds 4 --interval 2m`. If Copilot starts automatically or finishes before the checkpoint, record the changed state and repeat this setup with a suitable PR state.
- **Action:** Record the checkpoint after the two quiet ticks and the explicit review request. Resume the reported command while no review is visible. Inspect the tool transcript, requested-SHA history, post-request quiet count, counted review IDs, processed feedback IDs, and round count. After a review arrives, checkpoint and resume once more to check that its ID is retained.
- **Expected:** The initial transcript contains exactly one `gh pr edit` review request for that head SHA. The resumed watch does not repeat it. Two further quiet ticks without a review lead to escalation; a queued or running current-head Copilot run instead resets quiet waiting and continues. A completed review consumes one round, and seeing its ID again does not consume another. Already processed review IDs remain recorded across the next resume.
- **Null vs broken:** Verify the current-head Copilot workflow and review probes in every tick. Absence of a second request is valid only if the first request is recorded and the resumed dispatch ran. A working Copilot run cannot test the quiet escalation branch; record which branch the observations exercised.
- **Why by hand:** The real harness must retain action guards across replies and respond to independently changing GitHub review and workflow state.
- **Result:** untestable here. 2026-09-16: no controlled verification PR or fresh foreground harness was established in this remediation session.

### 3. Preserve clean-review confirmation

- **Setup:** Step 0 passed this session. Use a dedicated PR with passing checks, one clean current-head Copilot review, and no findings from either inline threads or review bodies. The session's test scope permits a confirming review request. Run `/monitor-pr PR_NUMBER --ticks 1 --rounds 4 --confirm-clean --interval 2m`.
- **Action:** Record the first clean review's ID, timestamp, SHA, round count, confirming request, and checkpoint. Resume before the confirming review arrives. Then resume after a second clean review becomes visible against the unchanged head.
- **Expected:** The first invocation reports confirmation `1/2` and returns a checkpoint rather than readiness. Resuming while the second review is absent preserves the first review and does not request another confirmation. After the second clean review, the terminal report includes two distinct IDs or timestamps against the same head and satisfies the Copilot axis. If the head changes, confirmation resets and the old pair cannot qualify.
- **Null vs broken:** Check both feedback sources and compare actual review IDs and SHAs. Re-reading one review twice cannot count as two confirmations. A second review with findings exercises remediation rather than clean readiness; record that outcome instead of marking this step passed.
- **Why by hand:** The harness must preserve a confirmation across invocation boundaries while distinguishing two asynchronous reviews of identical code.
- **Result:** untestable here. 2026-09-16: requires a fresh loaded harness and the specified sequence of current-head reviews.

### 4. Fall back after scheduler unavailability or rejection

- **Setup:** Step 0 passed this session. Use a pending PR. Prepare one Claude session where `ScheduleWakeup` is absent, one where the scheduler explicitly rejects a wakeup, and one scheduled-task-capable Codex session where task creation is rejected. Record the actual tool availability or rejection evidence. No existing scheduled watch may remain active for the PR.
- **Action:** In each session run `/monitor-pr PR_NUMBER --ticks 2 --no-fix --interval 2m`. Observe the selected mechanism, the first snapshot and dispatch, the active wait, the second snapshot and dispatch, and the checkpoint. Run its resume command in that same conversation.
- **Expected:** Each session announces foreground fallback and completes two snapshot-and-dispatch ticks in the active invocation. It returns a checkpoint after tick two, preserves `--no-fix` on resume, and makes no readiness claim while the PR is pending. Scheduling failures do not produce a promise to resume after a response. No pending scheduled continuation remains alongside the foreground loop.
- **Null vs broken:** A prose claim that scheduling is unavailable does not qualify; retain the tool list or rejection result. Require the second snapshot after the wait, so a wait followed by a final response without dispatch cannot pass. Report each of the three environments separately.
- **Why by hand:** Scheduler tool exposure, rejection responses, and active-turn continuation are properties of the actual harness and its tool policy.
- **Result:** untestable here. 2026-09-16: the current environment does not provide the three fresh harness configurations needed for these readings.
