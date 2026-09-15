# Resuming

A by-hand checklist is rarely run in one sitting. The person runs two steps, reports them in a sentence, stops, and comes back later, perhaps after another commit or from another worktree. The fosforo sessions show what happens without a record: "List the verification steps here please", "Please reprint the verification steps", and "What's needed for host verification?" each rebuilt the list from scratch, and every result already reported against the earlier list had to be carried across by memory or was lost.

The record is what makes the second request cheap and keeps the results. This file covers where it lives, how to reprint from it, how to write results into it, and how to split and close it.

## Where the Record Lives

**In the plan, when the work has one.** A `## Manual verification` section in the plan under `docs/plans/todo/`. It travels with the branch, it is reviewed with the change, and its `### Exclusive resources` heading is where resource-claim and work-suggestion skills already look. fosforo's plans hold their host passes this way, with sections such as "What the host settled, arms 1 and 2" written into the plan beside the steps that produced them.

**On the issue, when there is no plan or the project does not commit plans.** One checklist comment, updated in place for the life of the checklist.

**For a phase gate that spans several issues**, in the build plan's section for that phase, with each step linking the issue whose work it verifies.

**Never:**

- A new comment or a new file per session. Two copies drift, and the second one does not have the first one's results.
- Scrollback, or a scratchpad file. Both end with the session.
- A gitignored working directory. fosforo keeps captures in a gitignored `verification/` directory, and its build plan is explicit that whatever is there is one session's working artifacts. Captures can live there; readings go in the record.

### Writing to an issue comment

Write the body to a temporary file first, using the tmpfile pattern from the `use-git` skill, rather than passing a long body inline.

Create the comment once. `gh` prints the comment's URL, which ends in `#issuecomment-` and the comment's numeric ID:

```bash
gh issue comment NUMBER --repo OWNER/REPO --body-file "$body_file"
```

Put that URL on the checklist's `Record:` line, so the next session knows which comment is the record.

Before every update, read the current body back. The person may have edited the comment on GitHub, typing results straight into it, and an update written from a stale copy would erase them:

```bash
gh api "repos/OWNER/REPO/issues/comments/COMMENT_ID" --jq .body
```

Merge the new results into what came back, then write it:

```bash
gh api --method PATCH "repos/OWNER/REPO/issues/comments/COMMENT_ID" -F body=@"$body_file"
```

Do not use `gh issue comment --edit-last`. It edits the authenticated user's most recent comment on the issue, which stops being the checklist the moment that user comments on the issue about anything else. Pass `--repo` explicitly: inside a fork with an `upstream` remote, `gh` can resolve the repository to the upstream.

## Reprinting

A request to list, reprint, or walk through the steps is a request to read the record.

1. **Write before reading.** If the conversation holds results that are not yet in the record, write them in first.
1. **Check for staleness.** Compare the build named in the most recent results with the current tree. A step whose Expected depends on code changed since then is marked for re-running before it is shown; see [When the Build Changes](#when-the-build-changes).
1. **Lead with the status table**, so the person sees what is done before what is left.
1. **Print the remaining steps in full**, grouped by exclusive resource, with step 0 first because it is re-run every session.
1. **Summarize finished steps by their reading**, not by repeating the whole step, unless the person asks for them.

If the reprint was asked for because a step was unclear, the fix goes into the record before the reprint, not into the reprint alone. Otherwise the next reprint brings the unclear wording back.

## Parsing Free-Text Results

Results arrive as a sentence against step numbers. Take this one:

> 4's confirmed, skipping 5 and 6, 7 gave 1.0894

| Fragment           | Step | Status                                                                                      | Recorded                                                        |
| ------------------ | ---- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| "4's confirmed"    | 4    | `passed`, if step 4's Expected is an observation that "confirmed" can affirm; otherwise ask | "confirmed", verbatim                                           |
| "skipping 5 and 6" | 5, 6 | `deferred`                                                                                  | The reason and destination; ask once if neither can be inferred |
| "7 gave 1.0894"    | 7    | Derived by comparing 1.0894 with step 7's Expected and tolerance                            | "1.0894", verbatim, against the prediction                      |

The rules behind that table:

- **Record verbatim, then derive the status.** The person's words and numbers go into the Result line as given. The status is a judgment made from them, and it can be revisited; the reading cannot be recovered if it was paraphrased.
- **Attach date, build, and environment to every result.** The build comes from this session's step 0. If step 0 has not been run this session, record the reading, ask for step 0 now, and let the reading stand only if step 0 confirms the build and nothing was installed in between. Otherwise the reading is `void`.
- **Check each number against its tolerance, not against the printed prediction.** +1.0893 against a predicted +1.0889 with a tolerance of ±0.002 is a pass, and the record keeps both numbers.
- **Ask about everything unsettled in one message**, one precise question per step, so the person answers once.
- **A step number that does not exist, or a result that fits a different step better, is a question, not a guess.**

## Reports That Do Not Settle a Step

Some reports are real results that still do not decide the step. Each has a fixed response.

**"Seems fine."** fosforo received "4: Seems fine." for a step that asked the person to open two instances' editors at once and gave no Expected at all, so "seems fine" was the most the step allowed. Where a step's Expected is an observation in words and the report affirms it, record `passed` with the report verbatim. Where the Expected is a number, keep the step `pending` or `partial` and ask for the number.

**"Nothing happened (as desired)."** Ask whether the step's null-vs-broken evidence was seen: the liveness marker, the positive control, the stressing condition. If it was, record `passed` with both the absence and the evidence. If the step had no such evidence, or the person did not see it, record what they observed, set the status to `void`, and write what would confirm it, which is usually a marker to add. `./null-vs-broken.md` has the techniques.

**"I'm not sure what I'm looking for."** The step is defective, not the person. Rewrite its Expected in the record, then answer by pointing at the rewritten step. Re-read anything already reported against the old wording under the new Expected: fosforo's heap counts, from two samples taken with REAPER's interface in different states, could not be read under any wording, so they are `void`, and the rewritten protocol is what ran next.

**A reading outside tolerance.** Record `failed` with the reading. Before concluding the code is wrong, check that step 0 held and that the step's null-vs-broken line held, because a wrong build or an instrument artifact produces out-of-tolerance readings too. fosforo's screenshot tool reported a sine at +0.5000 as +0.0359, which reads as silence, because it took a centroid over a whole column and so averaged the persistence trail rather than the beam. The defect was in the instrument, and the reading was what found it.

**A reading that shows the prediction was wrong while the code was right.** Keep both numbers, correct the Expected in place, and say the reading corrected it. fosforo's beam-as-quads plan has a section called "Three predictions in this plan were wrong", and that section is worth more than the predictions were.

## When the Build Changes

Every result is tied to the build it was measured on. When a session resumes on a different build:

1. Step 0 names the new build.
1. For each `passed` step, check whether the changes between its build and the new one touch what the step covers, for example with `git diff --stat OLD..NEW -- PATHS`, where `PATHS` are the files the step exercises.
1. If they do, set the step back to `pending`, keep the earlier Result line as history, and add why: "passed on `OLD`; re-run, since `NEW` changed the clamp".
1. If they do not, the result stands, and the record says it was carried forward and why.

Do not mix readings from two builds in one multi-reading step without saying which reading came from which build.

## Deferring

A deferral is a decision, and it belongs on the record with its reasons. After "That's a lot of testing. Let's save it for later in the phases. I did check 1 and 2", the fosforo plan recorded a section titled "What was run in REAPER, and what was deliberately deferred". It named the build the run used, "the Debug build at `bbeab3c26442`, hash-confirmed against `zig-out`", then described what the two checks covered, then gave a table of what was deferred and what each item would cover:

| Deferred                                 | What it would cover                                                     |
| ---------------------------------------- | ----------------------------------------------------------------------- |
| 32- or 64-frame blocks, and 96 kHz       | The `reset` memset against the tightest deadline and at double the size |
| Ten or more device changes, watching RSS | `activate`/`deactivate` on `c_allocator`, which no test reaches         |
| A `--release=fast` pass                  | The build that ships, where every assertion above is gone               |

Those are three of its six rows. The introduction to the table explains why deferring was sound: "None of it guards a risk this issue introduces on its own, which is why it can wait, but the list should not evaporate."

For every deferred step, record:

- **The risk it covers**, so the deferral can be judged later.
- **Its destination:** a named later phase in a plan, or an issue, filed now or linked if it exists. A deferral without a destination is an omission with a label on it.
- **Why it can wait**, when the answer is not obvious from the risk.

## Splitting Across Sessions

The `### Exclusive resources` heading is what lets a checklist split without invalidating itself.

- **Split by resource.** One session takes all the steps for one resource. Steps that need no exclusive resource can run in any session, including while another worktree holds the resource.
- **Run step 0 in every session.** Each session's results carry its own build.
- **Claim the resource where the project records claims.** When worktrees claim resources, as the `create-worktree` skill's `--resource` option does, the session that holds the claim is the one that runs that resource's steps.
- **Write results before a session ends.** The status table is the handoff, and a session that ends with results only in its scrollback has handed off nothing.

## Closing

A checklist is closed when every row of its status table is terminal: `passed`; `failed` with a fix or an issue; `deferred` with a destination; `untestable here` with a reason; or `retired` with where its quantity is verified instead. `pending`, `partial`, and `void` rows are run again or deferred, never dropped.

Leave the record in place. Later corrections get checked against its figures: fosforo's verification runs are quoted with their numbers in its issues, and those numbers are what a later fix is measured against. Where the checklist gates a pull request or an issue, summarize the closed status table there and link the record.
