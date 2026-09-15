# Null vs Broken

A null result has at least three readings. Nothing happened because the change works. Nothing happened because the thing being watched was not running. Nothing happened because the conditions could not have produced a failure. A step whose success is an absence must separate the first reading from the other two, in the same run, or its pass means nothing.

This is the part of a by-hand checklist that is always missing, and it is the same discipline the `plant-defects` skill teaches for automated checks: establish that the instrument was running, then that the subject ran, and only then believe the absence. A person at a keyboard is an instrument too, and "I saw nothing wrong" is its absence.

## The Failure, as It Happens

A fosforo session produced a nine-row table of things to try in REAPER, each with a "Failure looks like" column: clicks, pops, a dropout, audio altered or silenced. The same message said, further down, that REAPER "cannot confirm the tap is recording anything, or that `reset` is being called at all. Both are invisible without a reader." The reply was:

> I did check 1 and 2, nothing happened (as desired).

Both readings of that sentence were available, and the checklist gave no way to choose. The session did the right thing afterwards: it recorded the run against a hash-confirmed build, named what the run covered, and deferred the rest with the risk each item would have covered. But the pass on item 2 rests on an absence of clicks during a locate, with nothing showing that the locate reached the code that could have clicked.

The techniques below are the ways to close that gap, each with the measured case it comes from.

## Techniques

### A liveness marker that witnesses the subject

Put something in the run that shows the thing under test was running: a log line, a counter, a meter, an indicator.

fosforo's editor prints a once-a-second `rendering at N Hz` line in Debug builds, so a picture that stops changing can be told from a render loop that stopped. For the audio tap above, the fix proposed was a temporary counter reported through that same line, reading something like `rendering at 60 Hz, 48000 samples tapped, 2 resets`, which turns "the transport locate fired `reset`" from an assumption into an observation and shows the tap advancing at exactly the sample rate.

Two rules about markers:

- **The marker must witness the subject, not a neighbour.** The same walkthrough told the person to expect `activated at 48000 Hz, up to 512 frames` at launch. That line proves `activate` ran. It says nothing about whether the tap wrote a sample, and a step that treated it as liveness for the tap would pass with the tap disconnected.
- **The marker must not change what it witnesses.** The walkthrough also warned against putting a log call in `reset` or `process`: the Debug `stderr` mirror is a write syscall, both are audio-thread callbacks, and a write there breaks the real-time rule in the one build where it is tempting. A counter shared with the render thread needs synchronization: use an atomic verified to be lock-free on the target, or an equivalent bounded, non-blocking single-producer handoff. A plain shared counter can introduce a data race, and a lock can block the audio callback. Keep allocation, locks, and logging off that callback; read a synchronized snapshot and print the line from the render thread. If no safe handoff is available, record the missing instrumentation instead.

When no marker exists and none can be added, the step says it cannot separate the readings. That is a finding, not a formality, and it usually becomes a small piece of instrumentation work.

### Check the transition that must change

An absence at the start of something is weak evidence. A change at its end is strong. One fosforo checklist tested liveness on the stop rather than the start: with a sine playing, stop the transport, and the trace must return to flat within about 20 ms plus a refresh period. A frozen window keeps showing the sine indefinitely, so this fails loudly, where "it appeared quickly" does not. Toggling it half a dozen times makes a single lucky frame irrelevant.

Look for the version of a step where the correct outcome is something visibly happening, and prefer it.

### A positive control first

Before trusting a reading of "absent", show the same instrument reading "present" in the same session.

fosforo's question was whether an Audio Unit installed as a symlink is registered at all. Logic's own scan log, `~/Library/Caches/AudioUnitCache/Logs/AUScan*.plist`, was the only instrument that could see the component, and it read 60 Audio Units with the component present as a copy, 59 with it absent as a symlink, and 60 again when the copy was restored. The control earned its place on the first attempt: that attempt read 59 for the copy as well, because the registrar had not settled before Logic was relaunched, and only the restored-copy reading showed the first number was worthless. The checklist line that came out of it is an instruction, not an observation: give the registrar time to settle before relaunching Logic.

The copy, symlink, copy sequence is also a plant in a manual session: a deliberate, reversible removal of the thing being looked for, with the reading required to move and then move back. Where a manual step can plant its defect that cheaply, it should.

### Conditions under which a failure is possible

A clean result means something only when the conditions could have produced a dirty one.

fosforo's multi-instance test ran fifteen instances, the most Logic will put on one track, every editor open, audio playing, and the buffer at 64 samples rather than the default. The record says why the last part is what makes it a test: at a default buffer, a pass-through plus a clear-to-grey renderer has so much headroom that no arrangement of instances could fail, and a clean run would say nothing at all. At 64 samples the audio callback owes a block roughly every 1.3 to 1.5 ms, while fifteen display links present something near 1800 frames per second between them. Logic reported no System Overload, which is an explicit dialog there rather than a judgment made by ear.

Two things to copy from that: choose the stressing setting on purpose and say why it stresses, and prefer a failure signal the environment raises explicitly over one a person has to notice.

### A discriminating reading where the eye cannot discriminate

When the correct and the broken outcomes look the same, measure the difference instead of looking for it.

"It should look dim grey rather than black" was retired in fosforo because the rendered clear colour is byte 5, which is black to the eye, so the step returned the same answer whether the fix had worked or not. The measurement that replaced it sampled a screenshot of the editor in Logic: `RGB(5,4,8)` across the drawable, against `RGB(38,38,38)` for Logic's own chrome. The shader writes `(0.02, 0.02, 0.03)` into an 8-bit drawable, which is byte `RGB(5,5,8)`, so the match is exact to within PNG compression. The decisive detail is the blue channel sitting two or three above red and green, mirroring the shader's 0.03 against 0.02: an unrendered layer is `RGB(0,0,0)`, and a host background is neither.

A good Expected of this kind names all three readings: what the working case reads, what the not-running case reads, and what the environment's own background reads.

### An effect larger than the scatter

A step can only see an effect bigger than the variation between repeated readings. Measure the scatter, compare it to the predicted effect, and move the step if the effect loses.

fosforo's sample-rate arm was meant to check a density scale by reading brightness at three device rates, three captures per rate. The predicted effect was a 1.41x fall. The scatter within a single rate was 1.8x. Worse, the defect itself would have read `g≈249` against an observed `g≈243`, six byte levels apart, inside an observed scatter of ten. The record's conclusion: "this method could not have caught the bug it was written for. It is the wrong instrument rather than a noisy one." The quantity was verified where it lives instead, by a test of the pure function and an offscreen measurement with no dwell, no free-running phase, and no byte quantization.

Take repeated readings whenever a reading is free-running, and write the number of repeats into the Action.

### A change across controlled cycles, sampled in matching state

When the environment's own activity swamps an absolute count, measure a change across a controlled number of repetitions, and sample in the same state both times.

A fosforo leak step asked for object counts from `heap` before and after ten editor cycles. REAPER's own interface is Metal-backed, so most of the 24 to 28 `CAMetalLayer` instances in the pasted output were the host's, and the counts went down between two samples taken in different interface states. The protocol that replaced it:

1. Extract only the two numbers: `heap "$(pgrep -x REAPER)" | awk '$4=="CAMetalLayer" || $4=="NSView" {print $4, $1}'`
1. With the editor closed, take a baseline.
1. Open and close the editor fifty times, ending with it closed.
1. With the editor closed again, sample.

Fifty cycles, because a leak of one layer and one view per cycle then reads +50 each, which no host churn disguises, while a change of ±5 either way is noise. Matching state, because sampling once with the editor open and once with it closed puts this project's own live objects into the comparison. The reading that came back was 24 layers and 1 view after one cycle, after ten, and after twenty: a change of exactly zero, where a leak of one per cycle would have read 43 after twenty.

### The pipe that makes a running thing look stopped

The path from the environment to the person's eyes is part of the instrument, and it can fail in ways that read exactly like the subject failing.

fosforo reads its host diagnostics by launching REAPER from a terminal and filtering for its own lines. Both details in that pipe are load-bearing, and each fails differently:

- **`2>&1`.** The plugin's log mirror writes to stderr, so a bare `| grep fosforo` filters stdout and lets every one of the plugin's own lines through unfiltered. The pipe appears to do nothing.
- **`--line-buffered`.** `grep` block-buffers when its output is not a terminal, so the once-a-second meter arrives in bursts minutes apart, which reads exactly like a render loop that has stopped.

Put the exact command in the Setup, and put the reason for each flag next to it, so nobody simplifies it.

### An instrument whose null is not evidence

Some instruments cannot see the subject at all, and their silence is about themselves.

On the macOS version fosforo recorded, `auval` and `AudioComponentFindNext` both enumerated only Apple's built-in components, while Logic saw every installed Audio Unit, including fosforo's. A null result from either is not evidence that the component failed to register. springer's verification table carries the same row forward: `auval -v aumi Sprg Ctmn`, "probably nothing", "no" under "In CI". A step that uses such an instrument says what it cannot see, or the step uses a different instrument.

### The wrong build

A result against a build other than the one under test is `void`, and the way it goes wrong is by nothing happening. fosforo once "verified" a branch that added a resizable editor against an installed build whose `can_resize` returned false, so the window edge could not be dragged, and nothing happening was the only available outcome. Step 0 exists for this, and `./step-format.md` describes it. It belongs here too because a wrong build is the null result with the most convincing disguise: every step reads as a clean pass.

## Portable Forms

The fosforo cases are a DAW, a GPU, and macOS tooling. The same moves in other environments, as illustrations rather than measurements:

| Environment   | A null result that could be broken               | What separates the readings                                                                                                                                           |
| ------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Browser       | No error banner after submitting a form          | The network panel shows the request left, with its status; a fixture known to fail shows the banner in the same session                                               |
| iOS simulator | No crash after sending the app to the background | The app's own log line for the lifecycle event appears in `xcrun simctl spawn booted log stream --predicate 'subsystem == "com.example.app"'`                         |
| Device        | No reconnect prompt after the device wakes       | Evidence the device actually slept, such as a gap in its log timestamps, before the absence of a prompt is believed                                                   |
| Printer       | No clipping at the page edge                     | The job appears in the completed queue (`lpstat -W completed -o` on CUPS systems), and a page with a mark placed at the edge proves clipping would show on this paper |
| CLI or server | No error output after a configuration reload     | The process reports the new configuration's identifier, or a deliberately invalid configuration produces the error in the same session                                |

In each row, the right column is a liveness marker, a positive control, or both. A step whose right column is empty is not ready to run.
