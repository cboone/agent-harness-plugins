# The ledger

The document the loop writes each round, and the one it reads back.

## Why it is a file

The loop needs a record that outlives a round for three reasons: `address-review` takes a review document as its input, declined findings have to be recognizable next round, and a run that stops with work outstanding has to leave behind something a person can act on. A summary printed in the terminal does none of those.

## Location

`docs/reviews/<date>-<branch>-until-clean.md`, with the branch name sanitized the way `review-branch` sanitizes it: `/`, spaces, colons and backslashes become `-`, repeated hyphens collapse, leading and trailing hyphens are trimmed, an empty result becomes `branch`, and a detached head becomes `HEAD`.

The `-until-clean` suffix keeps the file clear of `review-branch`, which writes `<date>-<branch>.md` and overwrites it. Two skills silently overwriting each other's reviews would lose work.

Under `--no-save`, write to a temporary path and report it. Whether the ledger is committed follows the repository's own convention; this skill does not commit it and never pushes.

## Shape

```markdown
# Review until clean: <branch>

Base: <base-ref> (<base-sha>)
Reviewer: <backend>
Rounds: <n> of <max>
Status: <clean|clean-with-declines|decisions-needed|stopped|failed>

## Round 1

Snapshot: <snapshot>
Invocation: <the reviewer command that ran>
Coverage: <full | partial, and what was excluded>

- [ ] **F1** Important. `path/to/file.go:42`. Token refresh races with logout, leaving stale sessions active.
      Evidence: <the traced path, command output, or citation>
- [x] **F2** Nit. `README.md:18`. Option table and the skill disagree on the default.
      Declined: the README states the user-facing default, which is correct.

## Round 2

...
```

Each round appends a section. Earlier rounds are never rewritten, because the point of the record is what was true when the review ran.

## Findings

Every finding carries a stable identifier, a mapped severity, a location, one sentence stating the defect, and the evidence for it. Identifiers are assigned in order across the whole run, not per round, so `F7` means one thing in the document.

`address-review` reads unchecked list items as actionable and skips checked ones, block quotes and prose. The ledger uses that directly:

- **Open findings** are unchecked items, so `address-review` picks them up.
- **Fixed, declined and deferred findings** are checked items, so it leaves them alone.
- Items below `--severity` stay unchecked but are passed to `address-review` through its `--skip` option, which keeps them visible in the document without spending a round on them.

## Statuses

| Status     | Meaning                                                           |
| ---------- | ----------------------------------------------------------------- |
| Open       | Raised this round, not yet addressed                              |
| Fixed      | Changed, with the change in the working tree or a commit          |
| Declined   | Deliberately not fixed, with a reason                             |
| Deferred   | Real, out of scope for this branch, with somewhere it was filed   |
| Unresolved | The fix was attempted and did not land; the run says so and stops |

A finding leaves the loop through one of these. There is no sixth state where it quietly disappears.

## Carried declines

A declined finding is still a defect in the reviewer's eyes, so the next round raises it again. Without a rule, the loop then spends every remaining round on a question that was settled.

At the start of each round, match the new findings against the declines already in the ledger, by location and substance rather than by wording, since the reviewer will phrase it differently. A match is recorded as declined, carrying the original reason and the round it was first declined in. It does not go to `address-review`, and it does not block a clean result.

A round whose only findings at or above the threshold are carried declines is **clean-with-declines**. That is a real terminal state, not a failure: the reviewer has nothing new to say, and the open disagreements are written down.

Do not carry a decline across a change to the code it was about. If the finding's location changed in the interim, raise it fresh; the reason it was declined may no longer hold.

## What a clean ledger says

A clean run still writes its ledger, and the final section states the coverage rather than a verdict on the branch:

```markdown
## Result

No findings at or above Important from <backend> over snapshot <snapshot>, covering <coverage>.
```

One reviewer pass is a sample. The ledger records what was reviewed and by what, which is a claim that can be checked, unlike "the branch is clean".
