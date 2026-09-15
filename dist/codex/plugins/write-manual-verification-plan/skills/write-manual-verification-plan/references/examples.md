# Examples

Four kinds of example, in order of how much of them is measured:

1. [Three failing steps, rewritten](#three-failing-steps-rewritten): each taken from a fosforo session where the step was misread, with the reply that showed the failure and the four-part form that works.
1. [One complete checklist](#one-complete-checklist): fosforo's host pass for drawing the beam as oriented quads, in the document template, with the readings its plan recorded.
1. [Three springer steps, restated](#three-springer-steps-restated): steps from a checklist written before the code exists, showing what each one is missing. No results, because none have been run.
1. [Other environments](#other-environments): one step each for a simulator, a browser, a device, and a printer. These are illustrations, and none of their values is a measurement.

Quoted material is condensed where the original ran long, and its punctuation follows this repository's house style.

## Three Failing Steps, Rewritten

### The rail arm: values without a location

**Before.** The walkthrough gave the arm as a criterion and a table:

> Arm 2, the rail. Level sweep at 1.000, 1.050, 1.089, 2.000. Because the centroid inverts straight to a sample value, the criterion is now clean: the implied sample should track the level and then stop.
>
> | file              | expected implied sample              |
> | ----------------- | ------------------------------------ |
> | `level-1.000.wav` | +1.0000                              |
> | `level-1.050.wav` | +1.0500                              |
> | `level-1.089.wav` | +1.0889, with the "on the rail" line |
> | `level-2.000.wav` | +1.0889, identical to 1.089          |
>
> Do not look for a flat top.

**What it produced:** "Arm 2: I'm not sure exactly what I'm looking for."

The trap was named and the values were right. What was missing was where the values appear, how close is close enough, and what a wrong value would mean.

**After:**

````markdown
### 2. The rail stops the peak from climbing

- **Setup:** Step 0 passed this session. REAPER launched from a terminal, the plugin on a stereo track, device rate 48 kHz. `level-1.000.wav`, `level-1.050.wav`, `level-1.089.wav`, and `level-2.000.wav` on that track.
- **Action:** Play each file. Capture the plugin window with `screencapture -o -x -t png -W verification/level-1.000-120hz.png`, clicking the plugin window, and run `scripts/measure-trace --refresh 120` on the capture. Repeat for each file.
- **Expected:** One line of the output decides this step:

  ```text
  highest peak     row 10.08  implies sample +1.0893
                   ^ on the rail: at or above +0.74 dBFS, amount unknowable
  ```

  The number after `implies sample` reads +1.0000, +1.0500, +1.0889, and +1.0889 for the four files in order, each within ±0.002, which is one backing pixel at 1080 rows. The `on the rail` line appears for 1.089 and 2.000 only. Rising, rising, rising, then flat. If 1.089 and 2.000 differ, the clamp is not working. If 1.000 and 1.050 match, the clamp fires too early. If 1.000 reads near 1.089, the rail moved. Ignore the `plateau width` line, and do not look for a flat-topped waveform: at 1.089 the clamp removes about a tenth of a pixel, and the picture correctly looks like an ordinary sine.

- **Null vs broken:** Two readings must differ and two must match, so neither a clamp that never fires nor one that always fires can pass.
- **Why by hand:** The offscreen harness renders a window it supplied itself. Only a host exercises the audio path, the ring buffer, the display link, and the compositor.
- **Result:** pending.
````

### The leak count: a number without a column, against a baseline the host swamps

**Before:**

> After the ten cycles above, with REAPER still running, run `heap "$(pgrep -x REAPER)" | grep -iE 'CAMetalLayer|NSView'`. Compare counts before and after another ten cycles. Flat is correct; growth of one per cycle is a leak.

**What it produced:** "4: Seems fine. 5: I'm not sure what count you mean", above a pasted page of `heap` rows with several numeric columns.

The step did not say which column is the count. And the premise was unsound: REAPER's own interface is Metal-backed, so most of the 24 to 28 `CAMetalLayer` instances were the host's. Two samples taken with its interface in different states went down, from 28 to 24 layers and from 7 to 3 views, and a comparison across states could not be read whichever way it moved.

**After:**

```markdown
### 5. Closing the editor releases its layer and its view

- **Setup:** Step 0 passed this session. REAPER running with the plugin on two tracks.
- **Action:**
  1. With every editor closed, run `heap "$(pgrep -x REAPER)" | awk '$4=="CAMetalLayer" || $4=="NSView" {print $4, $1}'` and note both numbers.
  1. Open and close one editor fifty times, ending with it closed.
  1. With every editor closed again, run the same command.
- **Expected:** The second sample's `CAMetalLayer` and `NSView` counts equal the first sample's, within ±5. A leak of one layer and one view per cycle reads +50 on each, which no host activity disguises. A small negative change is the host releasing its own objects, and is not a failure.
- **Null vs broken:** Sample in the same editor state both times: a sample with an editor open includes this plugin's own live layer and view, and makes the comparison meaningless. The count of fifty is what puts a real leak far outside the host's own swing.
- **Why by hand:** The offscreen harness measures leaks in a host it controls. Only REAPER retains the parent view on its own schedule.
- **Result:** passed. <date>, build `<commit>`, REAPER, two instances: 24 layers and 1 view after one cycle, after ten, and after twenty. A change of exactly zero, where a leak of one per cycle would have read 43 after twenty.
```

The readings are the ones the session recorded. It recorded no build identity, which step 0 now supplies, hence the placeholders. The run stopped at twenty cycles rather than fifty, and it still settles the step, because a leak would have read 43; the Result says what was actually run.

### The audio tap: failure described, success and liveness left out

**Before,** two rows of a nine-row table:

> | #   | Do this                                               | Covers                                                     | Failure looks like                           |
> | --- | ----------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------- |
> | 1   | Play audio through it, bypass and un-bypass           | `passThrough` changed signature to return the tapped slice | Audio altered, silenced, or channels swapped |
> | 2   | Click around the timeline during playback, repeatedly | `reset`, and the 256 KiB memset on the audio thread        | Clicks, pops, or a dropout on each locate    |

The same message said that REAPER "cannot confirm the tap is recording anything, or that `reset` is being called at all".

**What it produced:** "I did check 1 and 2, nothing happened (as desired)."

**After.** Step 1 borrows the null test from an earlier fosforo walkthrough, which already had a measurable Expected; the polarity control is added here. Step 2 uses the counter that session proposed as its liveness marker.

```markdown
### 1. The pass-through leaves the signal unchanged

- **Setup:** Step 0 passed this session. A project with one broadband audio item, such as a drum loop, duplicated onto a second track so both play the identical item. The plugin on track 1 only, shown enabled in the FX chain window, neither bypassed nor offline. Polarity inverted on track 2. Both tracks routed to REAPER's Master track at unity, no pan.
- **Action:** Play, and toggle the plugin's bypass several times while playing.
- **Expected:** The Master track's meter reads `-inf`, or below about -140 dBFS, with the plugin active and with it bypassed. Anything audible means `process` alters the signal.
- **Null vs broken:** Silence on the Master track is also what two muted tracks produce. Before trusting it, turn track 2's polarity inversion off: the Master track must rise to about 6 dB above either track alone, which shows both tracks are playing and the meter is reading their sum. Turn it back on and confirm the silence returns.
- **Why by hand:** Only a real host exercises its own buffer handling around `process`.
- **Result:** pending.

### 2. Transport locates do not click, and they reach `reset`

- **Setup:** Step 0 passed this session, against the Debug build with the temporary tap and reset counter, launched from a terminal so the once-a-second line is readable.
- **Action:** During playback, click to a new timeline position twenty times.
- **Expected:** No click, pop, or dropout on any locate. The once-a-second line's reset count rises by one for each locate, and its tapped-sample count rises at the device sample rate while playing, 48000 per second at 48 kHz.
- **Null vs broken:** No click is also what a locate that never reached `reset` produces. The reset count moving with each locate is what shows the memset ran; if it does not move, the step is `void`, whatever was heard.
- **Why by hand:** A dropout is audible, and no automated check here listens to a real audio thread under a real host's scheduling.
- **Result:** pending.
```

The report "I did check 1 and 2, nothing happened (as desired)" would, under these steps, prompt one question each: for step 1, whether the Master track rose when the polarity inversion was off; for step 2, whether the reset count moved.

## One Complete Checklist

fosforo's host pass for drawing the beam as oriented quads, in the document template. The readings are the ones the plan recorded, in REAPER 7.79 at the default editor on a 2x display with a 1920x1080 drawable. The source record does not supply every date, build identity, or control observation required by this template. Angle-bracketed fields show that missing metadata, including step 0's output; they are placeholders, not evidence that those confirmations happened. Replace them with same-session evidence before treating a copied checklist as verified.

````markdown
## Manual verification

Record: this section of the plan.

Build under test: confirmed by step 0 at the start of every session, and named in every result.

### Exclusive resources

- `host`: steps 0 to 4. The installed bundle belongs to whichever worktree copied last, and only one worktree verifies against a host at a time.

### Status

| #   | Step                                  | Needs  | Status  | Reading                                                  |
| --- | ------------------------------------- | ------ | ------- | -------------------------------------------------------- |
| 0   | Confirm the build under test          | `host` | passed  | provenance names this branch                             |
| 1   | The trace's position                  | `host` | passed  | +0.5000 and -0.5000, guard 0.26%                         |
| 2   | The rail stops the peak               | `host` | passed  | four files, every error under one backing pixel          |
| 3   | Position holds at 48, 96, and 192 kHz | `host` | passed  | nine captures, worst +0.4990                             |
| 4   | By eye: width, seam, and beading      | `host` | passed  | no beading                                               |
| 5   | Brightness falls with sample rate     | `host` | retired | the quantity has no host-only component; verified offscreen |

### 0. Confirm the build under test

- **Setup:** This worktree, with its branch checked out.
- **Action:** Quit REAPER, run `zig build install-clap`, then relaunch REAPER and confirm it loads the installed path below. If the host caches a different bundle, rescan or clear that entry before continuing.
- **Expected:** The output names what landed and what it replaced:

  ```text
  clap: <hash>  <path>/Fosforo.clap
  clap:   built from <branch> <commit>
  clap:   replaced <branch> <commit>
  ```

  The `built from` line names this worktree's branch and `git rev-parse --short HEAD`, and the relaunched host loads that installed path.
- **Null vs broken:** `install-clap` builds exactly what it installs, so a matching `built from` line cannot describe another worktree's bundle. Restarting and checking the loaded path connects that file to the host instance under test. A `replaced` line naming another branch is expected: it is the moment the shared install location changed hands.
- **Why by hand:** The host loads from a shared location that no automated check here installs into.
- **Result:** passed. <date>, build `<commit>` on `<branch>`, REAPER 7.79: <installed provenance output and loaded-path confirmation after relaunch>.

### 1. The trace's position

- **Setup:** Step 0 passed this session. REAPER launched with `/Applications/REAPER.app/Contents/MacOS/REAPER 2>&1 | grep --line-buffered fosforo`. `2>&1` because the log mirror writes to stderr; `--line-buffered` because otherwise the once-a-second meter arrives in bursts and reads like a stopped render loop. `sine-100hz-0.5.wav` on a stereo track.
- **Action:** Play the file, capture the plugin window, and run `scripts/measure-trace --refresh 120` on the capture.
- **Expected:** Peak and trough invert to +0.5000 and -0.5000, and the guard's off-ray fraction stays under `MAX_OFF_RAY`.
- **Null vs broken:** A trace frozen on an old frame would still read a position. The meter line must be advancing at the display rate while the capture is taken.
- **Why by hand:** The offscreen harness renders a window it supplied itself and says nothing about the audio path, the ring buffer, the display link, or the compositor.
- **Result:** passed. <date>, build `<commit>` (step 0: <loaded-build confirmation>), REAPER 7.79, default editor, 2x display, 1920x1080 drawable: +0.5000 and -0.5000, guard 0.26%; control: <meter observation during capture>. Getting there found two defects in the screenshot tool, both invisible offscreen, including a whole-column centroid that read this sine as +0.0359.

### 2. The rail stops the peak from climbing

- **Setup:** As step 1, with `level-1.000.wav`, `level-1.050.wav`, `level-1.089.wav`, and `level-2.000.wav`.
- **Action:** Play, capture, and measure each file.
- **Expected:** `implies sample` on the `highest peak` line reads +1.0000, +1.0500, +1.0889, and +1.0889, each within ±0.002, with the `on the rail` line for the last two only.
- **Null vs broken:** Two readings must differ and two must match.
- **Why by hand:** As step 1.
- **Result:** passed. <date>, build `<commit>` (step 0: <loaded-build confirmation>), REAPER 7.79, default editor, 2x display, 1920x1080 drawable. The first two peaks differ and the last two agree within ±0.002, as the control requires; readings:

  | file        | predicted | peak    | trough  | error   | on the rail |
  | ----------- | --------- | ------- | ------- | ------- | ----------- |
  | level-1.000 | +1.0000   | +0.9991 | -0.9991 | 0.44 px | no          |
  | level-1.050 | +1.0500   | +1.0504 | -1.0504 | 0.19 px | no          |
  | level-1.089 | +1.0889   | +1.0894 | -1.0895 | 0.24 px | yes         |
  | level-2.000 | +1.0889   | +1.0894 | -1.0894 | 0.24 px | yes         |

### 3. Position holds at 48, 96, and 192 kHz

- **Setup:** As step 1. Change REAPER's **device** rate in preferences, not the files: the negotiated rate sets the window length, and the files stay 48 kHz throughout.
- **Action:** At each of the three device rates, play `sine-100hz-0.5.wav` and take three captures.
- **Expected:** Every capture inverts to +0.5000, within ±0.002.
- **Null vs broken:** The rate must actually take effect. After each change, the plugin's `activated at` log line must name the new rate, since a change that did not take effect would pass at 48 kHz three times and exercise none of the three window lengths.
- **Why by hand:** The harness renders a fixed 960-sample window, so only a host exercises the window length, the ring buffer at three block sizes, and the upload path at three window lengths.
- **Result:** passed. <date>, build `<commit>` (step 0: <loaded-build confirmation>), REAPER 7.79, default editor, 2x display, 1920x1080 drawable: nine captures, every one +0.5000 or within 0.001 of it, worst +0.4990, across windows of 960, 1920, and 3840 samples; control: <activation log confirming each device rate>.

### 4. By eye: width, seam, and beading

- **Setup:** As step 1.
- **Action:** Play `sine-100hz-0.5.wav` and look along steep strokes.
- **Expected:** The beam is visibly wider and smoother than a single device pixel, with no seam at the quad's edge, and silence is flat and stable with no flicker between adjacent rows. No beading: a regular string of brighter dots along steep crossings, which would be a 2:1 ripple at the segment pitch, green 219 against 189.
- **Null vs broken:** The meter line must be advancing while looking, as in step 1, so the picture is live. Look along steep strokes, where the analysis says beading would appear, not along shallow ones where it would not. An absence seen by eye is believed here only because this effect is one an eye reliably sees.
- **Why by hand:** A brightness ripple of about 16% repeating at a fixed spatial period is exactly what an eye detects well, and it is the one question here that could not be settled by derivation.
- **Result:** passed. <date>, build `<commit>` (step 0: <loaded-build confirmation>), REAPER 7.79, default editor, 2x display, 1920x1080 drawable: no beading, so of the two analyses the plan recorded, the side-by-side one was right. Wider and smoother, no seam, silence flat and stable; control: <meter observation while inspecting steep strokes>. By eye, which is weaker than the other steps, and not weak for this claim.

### 5. Brightness falls with sample rate

- **Setup:** As step 3.
- **Action:** Read the `deposits` figure for the brightest pixel at each rate.
- **Expected:** A fall of about 1.41x from 48 to 192 kHz.
- **Null vs broken:** The scatter within a single rate must be smaller than the predicted effect.
- **Why by hand:** Retired. The density scale is a pure function of the window length and the drawable width, both of which the offscreen harness sets exactly, so it has no host-only component.
- **Result:** retired. <date>, build `<commit>`, REAPER 7.79, default editor, 2x display, 1920x1080 drawable: three captures per rate read a median of 6.80, 7.69, and 6.80 deposits, with a scatter within one rate of 1.8x against the predicted 1.41x, and the defect itself would have read `g≈249` against an observed `g≈243`, inside a scatter of ten. This method could not have caught the bug it was written for. Density is verified by a test of the pure function at 1x, 2x, and 3x, and by an offscreen measurement at both display scales.
````

## Three springer Steps, Restated

springer's build plan ends with a nine-step checklist for Logic, written before the plugin exists. It is a good list of what to check, and each step is one sentence. Three of them, restated in the four parts. None has been run, so every Result is `pending`.

### Step 8: state survives a save and reopen

**Before:** "Save the project, reopen it, and confirm every parameter returns."

```markdown
### 8. Every parameter survives a save and reopen

- **Setup:** Step 0 passed this session. Springer in the MIDI FX slot of a software instrument track. Every parameter set to a value other than its default, with the values written down or the generic parameter list captured.
- **Action:** Save the project. Close it completely, then open it again.
- **Expected:** Every parameter in the generic list reads the value it held before saving.
- **Null vs broken:** A parameter left at its default reads the same whether its state was restored or lost, so no parameter may start at its default. Closing the project completely, rather than reverting, is what makes the plugin instance be created again from saved state.
- **Why by hand:** Unit tests cover the state round-trip. Only Logic saves and restores the Audio Unit's state through its own calls, in its own order.
- **Result:** pending.
```

### Step 9: automation binds by stable identifier after a rebuild

**Before:** "Confirm the automation lane binds to the right parameters after a rebuild, which is the check that the stable-id scheme is actually working."

springer's ADR on parameter identity says why this step exists: under the script it replaces, automation bound to a parameter's position, so reordering the interface silently repointed every automation lane. Stable identifiers make reordering and insertion safe. That is also why a rebuild that leaves the parameter list alone cannot test it: position and identifier agree, so both schemes bind correctly.

```markdown
### 9. Automation binds to the same parameters after the list changes

- **Setup:** Step 0 passed this session. A project with automation lanes on at least two parameters that are not adjacent in the list, saved. Then a build that changes the parameter list's display order or inserts a parameter, which may be a temporary build made for this step, installed, and step 0 run again.
- **Action:** Reopen the project and play through the automated section.
- **Expected:** Each lane moves the parameter it named before the rebuild, and no other.
- **Null vs broken:** Step 0's second run must name a different build from its first, or this is not "after a rebuild". And the rebuild must change the list's order or contents, since a list whose positions are unchanged binds correctly under a position-based scheme too.
- **Why by hand:** A source canary can hold the identifier enum fixed. Only Logic shows what a saved project actually binds to.
- **Result:** pending.
```

### Step 5: no hung note when the trigger is released mid-strum

**Before:** "Set `Strum` to 120 ms and confirm no note hangs when the trigger is released during the strum."

The build plan names the failure precisely: a strummed voice's note-off must carry that voice's offset, or an upper voice is released before it is struck and hangs. Listening for a hung note is weak twice over: it depends on the instrument sustaining, and nobody can tell by feel whether a release landed inside 120 ms.

```markdown
### 5. Releasing the trigger mid-strum leaves no hung note

- **Setup:** Step 0 passed this session. Springer in the MIDI FX slot, followed by a Scripter MIDI FX whose script traces every event it receives. `Strum` at 120 ms.
- **Action:** Press and release one trigger key as quickly as possible. Repeat until the trace shows a release that landed inside the strum, as described below.
- **Expected:** Every note number that receives a note-on also receives a note-off after it, and the counts of note-ons and note-offs are equal.
- **Null vs broken:** The run counts only if the release landed inside the strum, which the trace shows directly: at least one note-off appears before the last note-on of that chord. If every note-on precedes every note-off, the release came after the strum finished, and the run passes whether or not note-offs carry their offsets. Run it again.
- **Why by hand:** The offline host harness covers strums spanning blocks. Only Logic runs the Audio Unit's note output under its own block sizes and timing.
- **Result:** pending.
```

## Other Environments

One step each, to show the four parts where fosforo has no precedent. Everything here is an illustration: the names, values, and tolerances are placeholders for a real project's, not measurements.

### iOS simulator

```markdown
### 3. The main screen follows the system appearance without a relaunch

- **Setup:** Step 0 passed this session: the build number on the app's About screen matches `CFBundleVersion` in the just-built app's `Info.plist`. The simulator's appearance set to light, and the app open on its main screen.
- **Action:** Run `xcrun simctl ui booted appearance dark`, then `xcrun simctl ui booted appearance light`.
- **Expected:** The main screen's background changes to the dark variant of its background colour within one second of the first command, and back to the light variant after the second, with the app still running.
- **Null vs broken:** Start from light and require both transitions. A screen that is dark at the start, or that changes only once, cannot distinguish an app that follows the appearance from one that picked it up at launch.
- **Why by hand:** The appearance change is delivered by the system to a running app; unit tests construct the view in a fixed appearance.
- **Result:** pending.
```

### Browser

This example stays `deferred` because its behavior can be automated. `<automation-issue-url>` is a placeholder: replace it with the issue filed in the target project before publishing the checklist.

```markdown
### 4. A failed save keeps the draft and says so

- **Setup:** Step 0 passed this session: the build identifier in the page footer matches the deployed commit. Developer tools open on the Network panel. A draft with text in the editor.
- **Action:** Set the Network panel's throttling to Offline, then press Save.
- **Expected:** A banner with the role `alert` reads the save-failure message, and the draft text is still in the editor.
- **Null vs broken:** The Network panel must show the save request, marked failed. If no request appears, the Save handler never ran, and a missing banner means nothing. Then set throttling back to No throttling and press Save again: the request must succeed and the banner must clear, which shows the banner tracks the save rather than appearing on its own.
- **Why by hand:** Not automated yet. An end-to-end test with network interception can cover this; track it in [Automate failed-save draft retention](<automation-issue-url>).
- **Result:** deferred. Risk: a failed save loses the draft or hides the error. Destination: [Automate failed-save draft retention](<automation-issue-url>), which will exercise both failed and successful requests.
```

### Physical device

```markdown
### 6. The accessory reconnects after the phone sleeps

- **Setup:** Step 0 passed this session: the accessory's firmware version, shown on the app's device screen, matches the build under test. The accessory paired and connected.
- **Action:** Lock the phone and leave it until the app's log records the accessory disconnecting. Then unlock it.
- **Expected:** Within 5 seconds of unlocking, the connection indicator reads Connected, with no pairing prompt.
- **Null vs broken:** The log must show a disconnect during the sleep. If the connection never dropped, reconnecting tested nothing.
- **Why by hand:** Only the real radio, and the phone's real power management, decide when the connection drops.
- **Result:** pending.
```

### Printer

```markdown
### 2. Duplex printing keeps the back page's margins

- **Setup:** Step 0 passed this session: the driver version shown in the print dialog matches the one under test. A two-sided test page with a frame drawn 5 mm inside every edge on both sides.
- **Action:** Print the page long-edge duplex to the queue under test.
- **Expected:** On the back side, the frame is fully visible, and the distance from each paper edge to the frame measures 5 mm ± 1 mm.
- **Null vs broken:** The job must appear in the completed jobs for this queue (`lpstat -W completed -o` on CUPS systems), so a page from another queue is not mistaken for this one. And a copy of the page with its frame 1 mm inside the edge, printed the same way, must visibly clip, which shows clipping would be seen on this printer and paper.
- **Why by hand:** The paper path and the printer's own imposition are physical; a rendered preview shows neither.
- **Result:** pending.
```
