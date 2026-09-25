# Stop rules

When the loop may report clean, when it must not, and how it ends otherwise.

## The clean rule

A round is clean when **all three** hold. Any one of them missing is not clean.

1. **The output was well formed.** The backend exited zero with a non-empty reply, the findings parsed against the schema, and, for a backend that echoes the snapshot, the `reviewed` value is the one the round started from.
1. **Nothing is left undeclined at or above the threshold.** Findings below `--severity`, and findings carried as declined, do not block.
1. **The snapshot still matches.** Recomputed at the moment of the decision, not taken from the start of the round.

Report the result with its coverage attached. A run that could not reach the untracked files in scope reports `clean, partial scope`, because a clean result that quietly covered less than the scope is the failure this whole design exists to prevent.

## Empty is not clean

A reviewer that found nothing and a reviewer that never ran produce the same thing: silence. Nothing downstream can tell them apart, so the loop refuses to read silence as success.

These are all **failed** rounds:

| What happened                                          | Why it is not clean                                                     |
| ------------------------------------------------------ | ----------------------------------------------------------------------- |
| No output at all                                       | Indistinguishable from a crash                                          |
| Output that does not parse                             | The reviewer's shape was not what was asked for; its content is unknown |
| Output that parses but does not match the schema       | Same, one step later                                                    |
| A non-zero exit, including timeouts and auth errors    | The review did not finish                                               |
| An empty reply, or one that is only an error           | Indistinguishable from a crash                                          |
| `reviewed` does not match, where the backend echoes it | Whatever was reviewed, it was not this code                             |

The last row applies only to a backend that echoes the snapshot back. Codex does, under its schema. Claude does not, and that is not a hole: the snapshot binding is enforced by the third clean rule recomputing it, not by the reviewer repeating it.

On a failed round, report what the backend actually returned, including its exit status and the first lines of its output, and stop. Do not retry silently: a backend that failed once for a reason nobody looked at will fail the same way again, and an automatic retry turns one visible failure into a slower invisible one.

### Transcription is not evidence

A backend whose output is prose has to be transcribed into findings, and that is allowed. What is not allowed is letting the transcription decide whether the review happened.

Judge emptiness on **what the backend returned**, before any transcription. A crashed reviewer and a clean reviewer both transcribe to `"findings": []`, so a transcription can never distinguish them; only the raw reply and the exit status can. Transcribing a missing, empty, or error-only reply into an empty findings list is the one move that turns a failure into a clean result.

### Proving the rule works

This is an absence claim, so it has a bad default answer: a loop that never checks will report clean forever. Check it the way `plant-defects` checks any instrument, by making the failure happen on purpose. Point the backend at a stub that exits zero and prints nothing, and confirm the run reports `failed`. Repeat with output that is not valid JSON, and with a non-zero exit. A run that reports clean against the empty stub has the bug this section is about, whatever the code says.

## Snapshot invalidation

A clean result is a statement about specific content. If the tree changes after the review and before the decision, the statement is about code that no longer exists.

Recompute the snapshot at step 8 every time. When it moved, discard the clean result, say so, and start another round if the limit allows. The usual cause is benign, such as a formatter on save or another session in the same worktree, and it is still a reason to review again rather than to assume the change was harmless.

## Convergence

Three rules keep a run from spending every round on the same disagreement:

- **Carried declines.** A finding declined in an earlier round is recorded as declined when it comes back, and does not block a clean result. `./ledger.md` covers the matching.
- **No progress stops the loop.** If a round produced findings, the fix step ran, and the snapshot did not move, then nothing changed and the next round would read the same code and return the same findings. Stop with `decisions-needed` instead of burning the remaining rounds.
- **The round limit.** Default 3. Reaching it with findings outstanding is `stopped`, with the unresolved items listed.

## Terminal statuses

| Status                | Meaning                                                         |
| --------------------- | --------------------------------------------------------------- |
| `clean`               | A clean round, with the coverage stated                         |
| `clean-with-declines` | A clean round whose remaining findings are all carried declines |
| `decisions-needed`    | Findings remain that the loop cannot resolve on its own         |
| `stopped`             | The round limit was reached with findings outstanding           |
| `failed`              | A round did not produce a usable review                         |

`failed` is not a softer `stopped`. `stopped` means the loop worked and ran out of rounds; `failed` means the loop learned nothing and its result carries no information about the code.

## What a clean result does not mean

It means one reviewer, at one effort, over one snapshot, returned no findings at or above the threshold. It is not evidence that the branch is free of defects, and the report says the former rather than implying the latter. The loop shortens the external review cycle; it does not replace it.
