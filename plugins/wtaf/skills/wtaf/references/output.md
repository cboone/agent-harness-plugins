# Output

The summary restores the user's footing. Users who ask for it have usually lost the thread, so the shape matters as much as the content: a verdict they can read in one line, the story of the work in two, and a short table they can scan.

## Style

- Lead with a bold one-sentence verdict: where this stands, in plain words.
- State the goal as a narrative (what this work is and why) before any table. A status table without the story leaves the user still asking what the overall plan is.
- Use the plan's own units (phases, steps, milestones) and names.
- Mark provenance where it matters: "measured now", "per the conversation", or "assumed".
- Omit any section with nothing in it. Never pad with "None".
- Never list every changed file, and never paste diffs or long logs.
- Use numbers, PR and issue references, and short SHAs where they help the user act.
- Follow the user's writing preferences, such as avoiding em dashes and never estimating how long work will take.

When in doubt, cut. "Summarize your summary, it's still too much detail" is the failure to avoid.

## Fast template

Fit one screen: about 25 lines.

```markdown
**<Verdict: where this stands, in one sentence.>**

**Goal:** <What this work is and why, in one or two sentences.>

| <Phase/Step> | Status      | Notes                         |
| ------------ | ----------- | ----------------------------- |
| <name>       | Done        | <PR #, SHA, or one fact>      |
| <name>       | In progress | <what remains>                |
| <name>       | Next        | <what it will produce>        |
| <name>       | Blocked     | <on what or whom>             |

**Waiting on you:** <decisions, approvals, questions still unanswered>

**Loose ends:** <uncommitted or unpushed work, items discussed but not filed, stray stash, unexpected changes>

**Next:** <one to three concrete actions>. <One-line offer, such as "Want me to start step 4?">
```

Keep the table to six rows or fewer; group finished early phases into one row. When the work has no phases (a one-off fix, an exploration), replace the table with three or four bullets.

When the user asked about something specific ("what's left in step 2?", "remind me what to verify"), answer that first and keep the rest to a line or two.

## Thorough template

The fast template, followed by these sections as they apply:

- **How we got here:** a short timeline of decisions and their reasons, from this session and earlier ones, grouped by day or phase.
- **Branch:** commits since the base, grouped by area or plan step, with ahead and behind counts against the base and the upstream.
- **Plan compliance:** each plan item marked done, partly done, or not started, with deviations and whether they were deliberate.
- **PR and reviews:** state, merge state, CI, unresolved review threads by reviewer, and approvals outstanding.
- **Issues and tracker:** the linked issue's latest discussion, milestone progress, and items still unfiled.
- **Deploys:** state per environment, for repositories that deploy.
- **Worktrees:** each sibling worktree, its branch, and how it relates to this one.
- **Health:** the command run and its result, marked as measured now.
- **Concerns:** risks, contradictions between sources, and anything that looks unexpected.

Thorough mode can run longer than a screen, but each section stays tight; prefer a table or a few bullets over paragraphs.

## Examples

A personal project, phase-based roadmap, fast mode:

```markdown
**Phase 1 is complete and merged; phase 2 is planned but not started.**

**Goal:** Build the rendering pipeline in three phases: core layout (1), styling (2), and export (3), each landing as its own PR.

| Phase       | Status  | Notes                                       |
| ----------- | ------- | ------------------------------------------- |
| 1. Layout   | Done    | PR #41 merged this morning; milestone open  |
| 2. Styling  | Next    | Plan in `docs/plans/todo/`; no issues filed |
| 3. Export   | Planned | Depends on phase 2's theme API              |

CI on `main`, latest known: green after the PR #41 merge.

**Loose ends:** The phase 1 milestone is still open with no open issues.

**Next:** Close the milestone and file phase 2's issues. Want me to draft them?
```

A team repository after a gap, fast mode:

```markdown
**Your fix shipped to production on Tuesday; the follow-up PR is approved and waiting on CI.**

**Goal:** Stop duplicate sign-ups by hashing emails before lookup (#4404), then backfill existing rows.

| Step       | Status      | Notes                                            |
| ---------- | ----------- | ------------------------------------------------ |
| Hash fix   | Done        | #4410 merged and deployed; production checked now |
| Backfill   | In progress | #4415 approved; one check pending                |
| Cleanup    | Next        | Drop the old index after backfill                |

**Waiting on you:** Confirm the backfill window with the team before merging #4415.

**Loose ends:** The index cleanup was discussed here but is not filed.

**Next:** Merge #4415 once CI passes, then file the cleanup. Want me to file it now?
```
