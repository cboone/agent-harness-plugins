# Step Format

The checklist is a document with a fixed shape, because it is read by more than one party: the person running the steps, the next session that resumes them, and the skills that look for exclusive resources in a plan. This file is the shape, part by part.

## The Document

The checklist is one section, in the plan when the work has one and in a single issue comment when it does not (`./resuming.md` covers the choice). The section always carries the same parts in the same order:

```markdown
## Manual verification

Record: this section. Results are written back here as they arrive, not left in chat.

Build under test: confirmed by step 0 at the start of every session, and named in every result.

### Exclusive resources

- `host`: steps 1 to 4, since only one worktree can have its build installed where the host loads from
- `window-server`: steps 1 to 4, since two sessions cannot both open windows and time each other's frames
- No exclusive resource: step 5, which reads a capture already on disk

### Status

| #   | Step                          | Needs    | Status  | Reading                           |
| --- | ----------------------------- | -------- | ------- | --------------------------------- |
| 0   | Confirm the build under test  | `host`   | passed  | hashes match, provenance matches  |
| 1   | The trace's position          | `host`   | passed  | +0.5000 and -0.5000, guard 0.26%  |
| 2   | The rail stops the peak       | `host`   | partial | `level-2.000` only                |
| 3   | Position holds at three rates | `host`   | pending |                                   |
| 4   | No beading along steep edges  | `host`   | pending |                                   |
| 5   | The centre row's half pixel   | none     | pending |                                   |

### 0. Confirm the build under test

- **Setup:** ...
- **Action:** ...
- **Expected:** ...
- **Null vs broken:** ...
- **Why by hand:** ...
- **Result:** ...

### 1. The trace's position

...
```

Steps 0 to 4 are adapted from fosforo's host pass for drawing the beam as oriented quads, with its recorded readings; step 5 is added to show a step that needs no resource.

The status table is what a person resuming reads first, and what a reprint leads with. Its `Reading` column is a short form of the step's `Result` line, not a replacement for it.

The `### Exclusive resources` heading is deliberate. Skills that claim resources for a worktree and skills that suggest parallel work look in plans under `docs/plans/todo/` for a heading containing "exclusive resource" and take the backticked names beneath it as the project's declared resources. Use the project's existing resource names where it has any, so a claim and a checklist name the same thing the same way.

Scope by what a step actually needs, not by what it is near. fosforo's build plan draws this line between two follow-up issues that both involve captures: one corrects arithmetic that does not depend on what was drawn, so any capture already on hand will do, while the other needs a brightness range that no existing capture contains, so it needs a fresh one and therefore the host. Only the second takes the resource.

## Numbering

Numbers are stable. The person running the checklist reports by number ("4's confirmed, 7 gave 1.0894"), and a number that moves between sessions turns a correct report into a wrong record.

- Never renumber. A step added later is appended with the next free number, even when it belongs logically between two others; say where it belongs in its Setup.
- Retire a step in place. Keep its heading and number, set its status to `retired`, and say why and where its quantity is verified instead. fosforo retired the brightness half of a sample-rate arm this way, as misdesigned, with the measurement that showed it could not have caught its defect.
- Step 0 is always the build confirmation, and it is re-run in every session rather than carried forward.

## Setup

Everything that must be true before the Action means anything, including what must be confirmed rather than assumed.

- **Begin with step 0.** "Step 0 passed this session" is the first line of every other step's Setup.
- **Name fixtures exactly, and check they exist.** A checklist rewrite in fosforo caught a step naming `sine-100-0.500.wav`, which was not a file that existed; the real one was `sine-100hz-0.5.wav`.
- **Name the setting that carries the variable, and where it lives.** "Change REAPER's **device** rate in preferences, not the files" matters because the window length is set by the negotiated device rate, so changing the files would change nothing the step measures.
- **State the build mode when the step depends on it.** One fosforo checklist needed the Debug build because the once-a-second rate line it reads is compiled out of a release build, and its Setup spelled out a build order, because the Audio Unit build silently rebuilds the CLAP as ReleaseFast.
- **Launch in the way that makes the evidence readable.** A host started from a terminal can show diagnostics that one started from the Dock cannot, and the Setup should say so rather than leave the person to discover it.

A failing Setup: "Open the plugin in REAPER." A passing one: "Step 0 passed this session. REAPER launched from a terminal with `2>&1 | grep --line-buffered fosforo`, the plugin on a stereo track, `sine-100hz-0.5.wav` on that track, device rate 48 kHz."

## Action

One thing to do, or an explicit sequence. Change one variable and hold the rest.

When a step repeats an action to accumulate an effect, say how many times and why that number. fosforo's leak step moved from ten open-and-close cycles to fifty because a leak of one object per cycle had to outgrow a host whose own object counts swung by several between samples.

## Expected

The part that fails most often, because it is written by someone who already knows what they are looking for. It must pass the stranger test: a person who did not write the code can tell a pass from a fail using the step alone.

A complete Expected has five things:

1. **Where the observation appears.** The output line, the field on it, the pixel, the column of a table, the panel of an inspector. Name it exactly.
1. **The value.** In numbers where there are numbers, and in words a person can check where there are not.
1. **The tolerance**, in the units the reader sees. "Within ±0.002, which is one backing pixel" lets the reader judge +1.0893 against +1.0889 without knowing where 0.002 came from.
1. **What each plausible wrong reading means.** This turns a fail into a diagnosis instead of a question.
1. **The tempting wrong observation**, when there is one. If the obvious thing to look at is not the thing that decides the step, say so.

### Failing and passing forms

From the fosforo sessions, each failing form followed by what it produced and the form that works:

- **Values without a location.** A rail arm gave four expected values and no indication of which output line produced them. The reply was "I'm not sure exactly what I'm looking for." The fix named the one line, `highest peak row 10.08 implies sample +1.0893`, and said "the number after `implies sample` is the answer".
- **A count without a column, against a baseline the environment swamps.** "Compare counts before and after another ten cycles. Flat is correct; growth of one per cycle is a leak." The reply was "I'm not sure what count you mean", above a pasted page of matching rows. The fix named the column (the first is the live instance count), extracted just the two numbers with `awk`, and replaced the absolute count with a change across fifty cycles sampled in the same editor state both times.
- **Failure described, success left implicit.** A nine-row table gave a "Failure looks like" column (clicks, pops, a dropout) and no success reading. The reply was "I did check 1 and 2, nothing happened (as desired)", which is the null-vs-broken problem in `./null-vs-broken.md`.
- **A reading the eye cannot make.** "It should look dim grey rather than black" was retired because the rendered colour is byte 5, which is black to the eye, so the step returned the same answer whether the fix had worked or not. The passing form samples the pixel with Digital Color Meter: roughly `(5, 5, 8)` means the pipeline ran and the fragment function executed, pure `(0, 0, 0)` means a layer with no presented drawable, and the host's own background colour means the view was never attached. Three readings, each mapped to a meaning.

### The decisive form

Where a raw reading is fragile, find the form of it that is not. Counting periods of a sine on screen is sensitive to phase and to a partial period at an edge; the ratio is not. "100, 200, and 400 Hz must show 2, 4, and 8 periods" survives a miscounted edge that "100 Hz shows 2 periods" does not.

### By eye

By eye is an instrument, and a legitimate one when the effect is the kind an eye is good at. fosforo's beading check asked whether a 16% brightness ripple repeating at a fixed spatial period was visible along steep strokes, and settled it by looking, with the reasoning recorded: a periodic ripple at a fixed pitch is exactly what an eye detects well. Say why the eye suffices when it is the instrument. Where it does not suffice, as with byte 5 against byte 0, sample the value instead.

### Numbers to record rather than predict

A step may exist to obtain a number nobody can yet predict. That is legitimate, and its Expected says what the number will decide rather than what it will be. fosforo's beam-as-quads plan kept a list under exactly that heading, including whether a change widened a 2:1 dwell ratio: "If materially, `white_headroom` becomes re-judgeable earlier than expected; if not, that belongs in #58 before it starts." Both outcomes lead somewhere named, and the Result is the whole point of the step.

## Null vs Broken

How to tell "nothing happened, as intended" from "the instrument was not running", or from "the conditions could not have produced a failure". Required on every step whose success is an absence, and worth a line on every other step. `./null-vs-broken.md` is the catalogue of techniques; the short form is that a step shows, in the same run, that the thing it watches was running and could have failed.

## Why by Hand

Every step says why it is not an automated test. There are two acceptable answers, and they lead to different places.

**By hand in principle.** What the step checks passes through something only the environment has: the audio path, the ring buffer, the display link, and the compositor in a real host; a real device's radio or sensor; a printer's paper path; a perceptual judgment an eye makes better than a threshold. springer's verification table puts this in a column: its Logic row reads "by hand" with "the only complete check of the MIDI FX slot" beside it, and "no" under "In CI".

**Not automated yet.** Nothing prevents an automated check, and nobody has written it. That step still goes in the checklist, but it is a deferral, and its `Why by hand` line links the issue that will automate it.

**Put the step where the quantity lives.** Before writing a step, ask whether the quantity it checks has any component that only the environment has. If it does not, the step does not belong in the checklist however important the quantity is. fosforo learned this from a sample-rate arm designed to check a density scale by reading brightness in a host. The density is a pure function of the window length and the drawable width, both of which the offscreen harness sets exactly, so it had no host-only component. In the host, the predicted effect was a 1.41x fall and the scatter within a single rate was 1.8x, so "this method could not have caught the bug it was written for". Density was verified where it lives, by a pure function's test and an offscreen measurement, and the host arm kept only the half that did have a host-only component: the trace's position through the audio path.

## Result

Readings, not ticks. A Result line carries a status, then the date, the build, the environment, and the reading, verbatim as reported:

```markdown
- **Result:** partial. <date>, build `<commit>` (step 0: hashes match), REAPER 7.79 at the default editor on a 2x display: `level-2.000` read +1.0893 against a predicted +1.0889, with the rail line. `level-1.000`, `level-1.050`, and `level-1.089` remain.
```

- **Keep prediction and reading together.** "+1.0893 against a predicted +1.0889" is checkable later; "passed" is not.
- **Append rather than overwrite across sessions.** A step run in two sessions has two dated lines, most recent last, so a result is never separated from the build it was measured on.
- **When a prediction was wrong and the code was right**, keep both numbers and correct the Expected in place, saying that the reading is what corrected it.
- **Multi-reading steps get a table.** fosforo's rail arm recorded predicted, peak, trough, error in pixels, and whether the rail line printed, one row per file.

## Step 0: Confirm the Build Under Test

An environment loads what is installed, not what was just built, and nothing connects the two but a copy someone has to remember to make. Where several worktrees or branches share one install location, the installed build belongs to whichever copied last. The failure is silent and reads as a pass: fosforo once "verified" a branch that added a resizable editor against an installed build whose `can_resize` returned false, where the window edge could not be dragged and nothing happening was the only available outcome.

So every checklist starts with step 0, and every session starts by running it. The confirmation, strongest first:

1. **A provenance marker read from the installed artifact**, naming the branch and commit that built it. This answers "whose build is this?" with nothing else in hand, including for a build this worktree did not make.
1. **A hash of the installed artifact compared against the one just built.** Two identical hashes mean the environment is loading the branch under test. This only works when this worktree has a build to compare against.
1. **A version or build number the environment displays**, in an About box, a settings screen, a page footer, or a `--version` line, provided the build under test changes it.
1. **A modification time.** Weak: it invites an inference instead of ending the question. Use it only when nothing else exists, and say in the Result that it is what was used.

Step 0's Expected names both halves: the identity of the build under test (branch and commit, or hash), and the identity read from the installed artifact, which must match. Its Null vs broken is that a comparison against a file that does not exist is not a match: when this worktree built nothing, a hash check has nothing to compare against, and only a provenance marker still answers.

Where a project has no provenance stamping at all, say that in step 0's `Why by hand` line and use the weakest confirmation available. Stamping provenance into builds is separate work, and worth an issue.

Re-run step 0 after anything that could change the installed build: an install from another worktree, a rebuild, a switch of branch. A result recorded without a step 0 from the same session is `void`.

## Status Vocabulary

One vocabulary, so a resumed checklist reads the same in every session.

| Status            | Meaning                                                                                                          | The Result line carries                                          |
| ----------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `pending`         | Not yet run                                                                                                      | Nothing yet                                                      |
| `passed`          | The Expected observation was seen, and the null-vs-broken check held in the same run                             | The reading, date, build, and environment                        |
| `failed`          | Something other than the Expected observation was seen                                                           | The reading, and the fix or the issue it went to                 |
| `partial`         | Some readings of a multi-reading step are in                                                                     | Which readings are in and which remain                           |
| `void`            | It ran and establishes nothing: wrong build, instrument not running, or conditions under which it could not fail | Why, and what running it again needs                             |
| `deferred`        | Deliberately not run now                                                                                         | The risk it covers, and where it goes: a later phase or an issue |
| `untestable here` | Cannot be run in the environment available                                                                       | Why, and what environment could run it                           |
| `retired`         | Withdrawn: misdesigned, or its quantity has no component only this environment has                               | Why, and where the quantity is verified instead                  |

`passed`, `failed` with a destination, `deferred` with a destination, `untestable here` with a reason, and `retired` with a reason are terminal. `pending`, `partial`, and `void` are not: a checklist is closed only when none of them remain.

`void` is the status fosforo needed most and had no word for. A fifteen-instance load test there was run twice before it counted, and both runs were void: the first ran against a bundle another worktree built, and the second against a build in which the Audio Unit never started its display link, so it measured fifteen idle instances. Neither was a failure, and neither was a pass, and recording either as one would have been wrong.

`untestable here` is not a failure of effort. fosforo recorded dragging an editor across two displays of different backing scale as "untestable on this hardware", which is a finding about the environment, and it tells the next session what hardware would close it.
