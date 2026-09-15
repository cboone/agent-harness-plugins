---
name: write-manual-verification-plan
description: >-
  Write a numbered, resumable checklist for the checks a human has to run by
  hand, in a DAW, a simulator, a browser, or on a device, where every step
  gives the setup, the action, the exact observation to expect, and how to
  tell "nothing happened, as intended" from "the instrument was not running".
  Use whenever by-hand verification is the subject, not only when invoked
  explicitly: (1) asked what can be verified manually, what host verification
  needs, or what to test, (2) writing the manual verification section of a
  plan or phase gate, (3) asked to list or reprint verification steps,
  (4) receiving partial results in free text, such as "4's confirmed, skipping
  5 and 6, 7 gave 1.0894", (5) someone is unsure what a step is looking for,
  (6) splitting a checklist across sessions or around an exclusive resource.
  Covers the step format, build confirmation, null-versus-broken controls,
  persisting to a plan or issue, resuming, and recording measured readings.
---

# Write Manual Verification Plan

A by-hand checklist is a record, not a message: every step says what to do and what you should see, and the checklist outlives the session that wrote it.

## When to Use

Some checks can only be made by a person in front of an environment: a DAW loading a plugin, a simulator running an app, a browser rendering a page, a physical device, a printer. The list of those checks gets asked for, produced, and then fails in three ways. It does not say what success looks like, so the person running it cannot tell a pass from a fail. It does not separate "nothing happened, as intended" from "nothing was running". And it lives in scrollback, so it is rebuilt from scratch every time someone asks for it again, losing every result already reported against it.

Use this skill when:

- Someone asks what can be verified manually, what host or device verification needs, or to be walked through what to test.
- A plan or phase gate has an acceptance criterion that only a real environment can show.
- Someone asks to list or reprint the verification steps. The checklist already exists somewhere, and the job is to find it.
- Results come back as free text against step numbers.
- Someone says they are not sure what a step is looking for. That step's Expected has failed its reader, and the fix belongs in the record.

Do not use it for a check whose quantity has no component only the environment has. That check belongs in an automated test, however important it is. And do not use it to judge whether an automated instrument can fail: that is the `plant-defects` skill, which is the same discipline pointed at automated checks.

## Core Principles

1. **Expected is an observation a person can check without having written the code.** Name where the observation appears (the output line, the pixel, the column, the field), the value, the tolerance in the units the reader sees, and what each plausible wrong reading means. "The trace should be visible" is not an Expected. "The `implies sample` value on the `highest peak` line reads +1.0889, within ±0.002" is.
1. **A null result has two readings.** "Nothing happened" is what the intended outcome looks like, and it is also what an instrument that was not running reports. Every step whose success is an absence carries a way to tell the two apart in the same run.
1. **Nothing is worth believing before the build is confirmed.** An environment runs what is installed, not what was just built. Step 0 confirms the build under test at the start of every session, and a result recorded without it is `void`.
1. **The record outlives the session.** Persist the checklist to the plan or the issue before presenting it, update that one record in place, and reprint from it. A checklist rebuilt from memory loses every result already recorded against it.
1. **Record readings, not ticks.** Where Expected is a measurement, the measured value goes into the record with its date, build, and environment. Later corrections get checked against those figures, and a tick gives them nothing to check against.
1. **Put the step where the quantity lives.** A step is by hand in principle only when what it checks passes through something only the environment has. Where it merely has not been automated yet, it is a deferral, and it links the issue that will automate it.
1. **Scope before splitting.** State up front which steps need an exclusive resource, so a long checklist can be split across sessions without invalidating itself.

## The Step

Four parts, and two lines that make the step a record:

```markdown
### 2. The rail stops the peak from climbing

- **Setup:** Step 0 passed this session. REAPER launched from a terminal, the plugin on a stereo track, and the four `level-*.wav` files below in the project.
- **Action:** Play each file, capture the plugin window, and run `scripts/measure-trace --refresh 120` on each capture.
- **Expected:** The `implies sample` value on the `highest peak` line reads +1.0000, +1.0500, +1.0889, and +1.0889 for `level-1.000`, `level-1.050`, `level-1.089`, and `level-2.000`, each within ±0.002, which is one backing pixel. The `on the rail` line appears for the last two only. If the first two match each other, the clamp fires too early; if the last two differ, it does not fire. Do not look for a flat-topped waveform: at 1.089 the clamp removes about a tenth of a pixel, and the picture correctly looks like an ordinary sine.
- **Null vs broken:** Two readings must differ and two must match, so neither a clamp that never fires nor one that always fires can pass.
- **Why by hand:** The offscreen harness draws a window it supplied itself. Only a host exercises the audio path, the ring buffer, the display link, and the compositor.
- **Result:** partial. `level-2.000` read +1.0893 and printed the rail line; three files remain.
```

Statuses are `pending`, `passed`, `failed`, `partial`, `void`, `deferred`, `untestable here`, and `retired`. Numbers are stable: the person reports results by number, so a step is never renumbered, new steps are appended, and a retired step keeps its number with the reason. `./references/step-format.md` has the full document template and the rules for each part and status.

## Workflow

1. **Look for the checklist before writing one.** Check the active plan under `docs/plans/todo/` for a `## Manual verification` section, and the issue for a checklist comment. If one exists, resume from it with `./references/resuming.md`. A request to list or reprint the steps is a request to find the record, never to regenerate it.
1. **Decide what belongs by hand.** List the candidate checks, then move every one whose quantity has no environment-only component into an automated test, or into an issue for one. Write `Why by hand` for each step that stays.
1. **Write step 0: confirm the build under test.** Use the strongest confirmation the project has: a provenance marker read from the installed artifact, a hash compared against the fresh build, or the version the environment displays. Say which one was used, and say so when it is weak.
1. **Scope the resources.** Under an `### Exclusive resources` heading, list each resource as a backticked name with the steps that need it, and name the steps that need none. Keep each resource's steps contiguous.
1. **Write each step in four parts.** Setup, Action, Expected, Null vs broken. Apply the stranger test: someone who did not write the code can tell a pass from a fail using the step alone.
1. **Confirm each step can fail.** The expected effect must be larger than the reading's scatter, and the conditions must be ones under which a defect would show. A step that reads the same whether or not the change works is redesigned or removed, not run. See `./references/null-vs-broken.md`.
1. **Persist, then present.** Write the checklist to its record first, then show the person this session's steps, step 0 first.
1. **Record results as readings.** Map each free-text report onto its step, record the reading verbatim with date, build, and environment, and ask one precise question about any step a report does not settle. Never mark a step `passed` on a report that lacks its Expected observation or skips its null-vs-broken check.
1. **Close out.** Every step ends `passed`, `failed` with its fix or issue, `deferred` with its destination, `untestable here` with its reason, or `retired` with where its quantity is verified instead. A `pending`, `partial`, or `void` step is run again or deferred, never dropped.

## Reference Navigation

**Start here:**

- `./references/step-format.md`: the document template, each of the four parts and two record lines with a failing and a passing form, numbering, step 0, and the status vocabulary

**By situation:**

- `./references/null-vs-broken.md`: telling an intended absence from an instrument that was not running, with a measured case for each technique
- `./references/resuming.md`: where the record lives, reprinting, parsing free-text results, reports that do not settle a step, deferring, and splitting across sessions
- `./references/examples.md`: three failing steps rewritten, one complete checklist with its recorded readings, and steps for a simulator, a browser, a device, and a printer

## Related Skills

- `plant-defects`: the same discipline for automated instruments. Where a manual session can plant the defect a step looks for, cheaply and reversibly, it should.
- `create-worktree`, `address-issue-in-worktree`, and `suggest-next-issue`: each reads a heading containing "exclusive resource" in a plan under `docs/plans/todo/` and takes the backticked names beneath it as the project's declared resources, so the checklist's scope section feeds resource claims and parallel-work suggestions directly.
- `use-git`: the tmpfile pattern for writing a checklist to an issue comment.

## Sources

The practice and every measurement quoted in these references come from two of the author's projects:

- `cboone/fosforo`: `docs/notes/host-verification.md`, on why a host loads what is installed and how to confirm it; the host passes recorded in `docs/plans/done/2026-09-01-draw-the-beam-as-oriented-quads.md`, `docs/plans/done/2026-07-29-cvdisplaylink-render-loop-and-resize-seam.md`, and `docs/plans/done/2026-08-19-tap-the-audio-thread-into-the-history-buffer.md`; and the working sessions behind them, in which a by-hand checklist was asked for, reprinted, and misread often enough to show exactly where it fails
- `cboone/springer`: the verification program table in its build plan, which marks the Logic row as by hand with a reason, and the nine-step by-hand checklist that ends the same plan
