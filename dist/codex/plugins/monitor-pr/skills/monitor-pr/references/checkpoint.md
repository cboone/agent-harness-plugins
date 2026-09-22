# Checkpoint and Resume

A foreground checkpoint ends an invocation while preserving the watch. Resumption requires the same conversation, or the complete checkpoint pasted into a new conversation before the resume command. A command alone in a new conversation starts a new watch; never claim to have restored state that is unavailable.

## Checkpoint Fields

Print a labelled `monitor-pr checkpoint` block with every field below, including explicit empty values for guards that have not been set. Store only watch metadata, never credentials or environment variable values.

| Field              | Contents                                                                                                                                                                                                                                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Identity           | `OWNER`, `REPO`, `PR_NUMBER`, PR URL, head and base branch names, current head SHA, and whether the author is Dependabot                                                                                                                                                        |
| Options            | Effective `--ticks`, `--rounds`, `--confirm-clean`, `--no-fix`, and `--interval` override, or `adaptive` when none was supplied                                                                                                                                                 |
| Snapshot           | All four readiness axes, individual check states, latest Copilot review ID and SHA, that review's feedback probe result (open-thread count, review-body finding count, and format-drift flag), draft state, `mergeable`, `mergeStateStatus`, and informational `reviewDecision` |
| Pacing             | Selected interval, mechanism, and completed foreground ticks for this invocation                                                                                                                                                                                                |
| Rounds             | Completed Copilot rounds and the watch's total round budget; record counted review IDs so a review seen again cannot spend another round                                                                                                                                        |
| Review request     | Requested head SHAs, consecutive quiet ticks before a request, and quiet ticks after the request for the current head                                                                                                                                                           |
| Processed feedback | Review IDs already passed to the feedback resolver, and its outcome for each                                                                                                                                                                                                    |
| Repair attempts    | Attempt counts keyed by check name, and any pending remote-moved push retry                                                                                                                                                                                                     |
| Confirmation       | Consecutive clean review count, review IDs, timestamps, and their head SHA                                                                                                                                                                                                      |
| Dependabot rebase  | Head SHAs already requested, current request SHA, quiet tick count, and any observed reply                                                                                                                                                                                      |
| Scheduled work     | Task or wakeup ID, or `none`; no scheduled continuation may remain active at a foreground checkpoint                                                                                                                                                                            |

Print the exact resume command with the explicit PR number and all effective options. For example:

```text
/monitor-pr 361 --ticks 3 --rounds 10 --confirm-clean --no-fix --interval 10m
```

Say to run that command in this conversation. For transfer to another conversation, say to paste the complete checkpoint first and verify the repository and branch there. Do not create a state file in the monitored repository automatically.

## Resume Procedure

1. Match the latest checkpoint to the resolved repository and PR. Restore all watch-state fields before classifying GitHub state. If required fields are missing, report the missing fields and ask for them; do not silently reset guards or infer that no prior action occurred.
1. Restore the effective options. A newly supplied option explicitly replaces its checkpoint value; omitted options retain their checkpoint values. A changed `--rounds` value sets the total watch budget, not additional rounds. Preserve completed rounds when comparing against it.
1. Reset only the foreground tick count for this invocation to zero. Retain the review request, counted and processed review IDs, per-check repair attempts, retry state, confirmation, and Dependabot guards. The default three-tick boundary is not a new Copilot round budget.
1. Take a fresh step 3 snapshot and count it as the first foreground tick. Never dispatch a cached readiness verdict. If the head changed, invalidate confirmation and reset the current-head quiet counters as required by the main workflow; retain histories of requested SHAs, counted and processed review IDs, and repair attempts. Those ordinary head-change transitions also apply during uninterrupted watches.
1. Resume step 4 dispatch with the restored state. A review already requested for this head is not requested again. A review already processed is not processed again. If the post-request quiet count reaches two without a review, or the feedback probe still reports open threads or format drift against an already processed review, escalate under the existing rules. A review-body finding count that stays above zero against an already processed review is expected, not an escalation. A restored outcome other than `Completed` or `No unresolved Copilot feedback` escalates on the first tick rather than waiting, since the guard prevents the review from being processed again.
1. On the next foreground limit, replace the checkpoint with updated state. On readiness or escalation, end the watch rather than emit another resumable checkpoint.
