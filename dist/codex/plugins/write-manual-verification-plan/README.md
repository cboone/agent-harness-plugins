# Write Manual Verification Plan

Write a numbered, resumable checklist for checks run by hand, where every step says what to do, what you should see, and how to tell nothing from broken.

**Type:** Skill
**Trigger:** `/write-manual-verification-plan` (also activates automatically)

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Some checks need a person in front of a real environment: a DAW loading a plugin, an iOS simulator, a browser, a physical device, a printer. The list of those checks tends to fail in three ways. It does not say what success looks like, so the person running it cannot tell a pass from a fail. It does not separate "nothing happened, as intended" from "the thing was not running". And it lives in chat, so it is rebuilt from scratch whenever someone asks for it again, losing every result already reported.

This skill writes the checklist as a record. Every step has four parts (Setup, Action, Expected, and Null vs broken) plus a line saying why it has to be done by hand and a Result line that holds measured readings rather than ticks. Step 0 always confirms which build is under test, in every session, because an environment runs what is installed rather than what was just built. The checklist is persisted to the plan or the issue before it is shown, updated in place as results arrive in free text ("4's confirmed, skipping 5 and 6, 7 gave 1.0894"), and reprinted from that record rather than from memory. Its exclusive-resource section uses the heading convention the worktree and issue-suggestion skills already read, so a long checklist can be split across sessions around a resource.

The practice and its measured examples come from the host-verification record of an audio plugin project, where the same checklist was asked for, reprinted, and misread often enough to show exactly where each kind of step fails, and from the by-hand verification plan of a second plugin project built on the same foundation.

## Usage

```text
/write-manual-verification-plan
```

The skill also activates on its own when by-hand verification is the subject: a question about what can be verified manually, a request to walk through what to test, a request to reprint the steps, a report of partial results, or someone unsure what a step is looking for.

When the work has a plan, the checklist becomes that plan's `## Manual verification` section. Otherwise it becomes a single comment on the issue, created and later updated with the [GitHub CLI](https://cli.github.com/), which that case requires.

## Examples

- "What can I verify manually?": a checklist that starts with confirming the build, with every step's expected observation stated in a form someone who did not write the code can check
- "Walk me through what to test in REAPER": the same, written to the plan first, grouped by exclusive resource
- "4's confirmed, skipping 5 and 6, 7 gave 1.0894": readings recorded verbatim against their steps, statuses updated, and one question for anything the report does not settle
- "Please reprint the verification steps": the status table and the remaining steps, read from the record
- "Arm 2: I'm not sure exactly what I'm looking for": the step rewritten in the record, naming the output line, the value, the tolerance, and what each wrong reading means

Two companion skills are filed and not yet built: one for stamping build provenance into artifacts, which gives step 0 its strongest form, and one for writing phased build plans, whose phase gates are usually where these checklists are needed.

## Recommended Permissions

For a checklist stored on an issue, these optional rules allow the record's create, read, update, and tmpfile commands. Add them to `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": [
      "Bash(gh issue comment *)",
      "Bash(gh api repos/*)",
      "Bash(gh api --method PATCH repos/*)",
      "Bash(git diff *)",
      "Bash(mktemp -u /tmp/manual-verification-body-*)",
      "Bash(rm /tmp/manual-verification-body-*)"
    ]
  }
}
```

Review and adjust the rules to match your security preferences. The verification commands inside a checklist depend on the target project and environment.

## See Also

- [Plant Defects](../plant-defects/README.md): the same discipline for automated checks, proving an instrument can see the defect it claims to catch
- [Create Worktree](../create-worktree/README.md): claims the exclusive resources a checklist declares
- [Suggest Next Issue](../suggest-next-issue/README.md): uses declared resources to find work that can run in parallel
- [Write Formalization Roadmap](../write-formalization-roadmap/README.md): the document-structure guide this skill's shape follows
- [All plugins](../../../../README.md)
