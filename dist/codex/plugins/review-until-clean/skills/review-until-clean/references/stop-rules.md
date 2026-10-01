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

## Confirming a clean result

A single clean round is the default finish. It is also the weakest point in the clean rule, because a reviewer's output varies between runs over identical code: a round that found nothing is not proof that there is nothing to find. Under `--confirm-clean`, the loop requires two consecutive clean rounds instead.

1. **The first clean round does not end the run.** Record it in the ledger with its snapshot, then start a confirming round at step 1 with the same backend and the same coverage. There is no fix pass between the two, because there is nothing to fix.
1. **The pair completes when the confirming round is clean under all three clean rules and its snapshot is the one the first round reviewed.** Report both rounds and the snapshot they share.
1. **Any snapshot movement resets the pair**, whatever its source: a fix, a formatter, another session. Check it at the start of the confirming round, not only at its decision: compare the snapshot step 1 reports with the one the first round recorded. A tree changed between the two rounds would otherwise let a clean review of different content complete the pair. When they differ and a round is left in the budget, the round is an ordinary round over the new snapshot, so its clean result is again only the first of two. When none is left, the extra-round rule below applies, and `--report-only` follows the last paragraph of this section.
1. **A confirming round that turns up findings resets the pair too.** Within the budget, those findings go through steps 7 and 9 like any other round's. The extra round past the cap, described below, never reaches step 9: its findings are recorded and the run stops. Findings that match carried declines do not count against the confirmation, since they do not block a clean round either.
1. **A failed confirming round is `failed`**, never a confirmation. Empty is not clean in the second round any more than in the first.

**The confirming round counts against `--max-rounds`, with one exception.** When a round is left in the budget, the confirming round uses it, like any other round. When the first clean round used the last round, the confirming round runs anyway, as one round past the cap. That extra round is a review only: if it turns up findings, they are not fixed, and the run ends `stopped` with them listed. It also runs only to confirm: if the snapshot moved after the last clean round, it does not run, and the run ends `stopped` with that reason. Without the exception, a run whose first clean round lands on the last round could never be confirmed.

The terminal status follows the same table as an unconfirmed run: `clean-with-declines` when either round of the pair relied on carried declines, and `clean` otherwise. Coverage still applies, so a confirmed pair that did not reach the untracked files is `clean, partial scope`.

Under `--report-only`, the confirming round still runs when the first round is clean and the snapshot has not moved since. Neither round edits anything. `--report-only` has no round budget, so the cap rules above do not apply to it and it never reports `stopped`:

- **The confirming round turns up findings.** The run reports them exactly as a `--report-only` run reports a first round with findings.
- **The snapshot moved before the confirming round.** The confirming round does not run. The run reports the first round's clean result as unconfirmed, says the tree changed after it, and records `Confirmation: unconfirmed` in the ledger.

## Convergence

Three rules keep a run from spending every round on the same disagreement:

- **Carried declines.** A finding declined in an earlier round is recorded as declined when it comes back, and does not block a clean result. `./ledger.md` covers the matching.
- **No progress stops the loop.** If a round produced findings, the fix step ran, and the snapshot did not move, then nothing changed and the next round would read the same code and return the same findings. Stop with `decisions-needed` instead of burning the remaining rounds.
- **The round limit.** Default 3. Reaching it with findings outstanding is `stopped`, with the unresolved items listed. A confirming round under `--confirm-clean` counts against it, except that one may run past the cap to confirm a clean last round, per [Confirming a clean result](#confirming-a-clean-result).

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

It means one reviewer, at one effort, over one snapshot, returned no findings at or above the threshold. Under `--confirm-clean` it means that reviewer did so twice in a row, which narrows the variance between runs without changing what kind of claim it is. It is not evidence that the branch is free of defects, and the report says the former rather than implying the latter. The loop shortens the external review cycle; it does not replace it.
