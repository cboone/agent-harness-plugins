# Instrument Blindness

Instruments do not compose by assumption. Tabulate defect against instrument and mark what each one cannot see.

## The matrix

Planted defects down the side, instruments across the top, one cell per pair. The version below is six defects against five instruments, from a project's leak-instrument notes. Note that the first two columns are two **assertions over one report**, not two tools: the class filter matches leaked objects by class-name prefix, and the byte bound reads the same report's byte total. Naming the column after the tool rather than the assertion is a mistake, because it makes the classless-allocation row look self-contradictory:

| Planted defect                                 | Class filter | Byte bound | Buffer counter | Texture counter | Unit suite      |
| ---------------------------------------------- | ------------ | ---------- | -------------- | --------------- | --------------- |
| Command queue never released                   | yes          | no         | no             | no              | no              |
| Window buffer ring built and forgotten         | no           | no         | yes            | no              | no              |
| Accumulation pair built and forgotten          | no           | no         | no             | yes             | no              |
| Palette lookup built and forgotten             | no           | no         | no             | yes             | no              |
| A release call stops being sent, still counted | no           | no         | no             | no              | no              |
| A plain allocation this project owns           | no           | yes        | no             | no              | on tested paths |

Its opening line is the theory in one sentence: each instrument is blind to something different, and **the differences are what matter rather than how thorough each one is**.

Four conclusions the matrix produced, none of which was available from reading any instrument's documentation:

- **The heap walker sees what is on the malloc heap, and a graphics buffer's storage is not.** Two different misses get confused here, so keep them apart. A block with **no runtime class** is on the heap and the walker does find it; what misses it is the class-prefix filter, because a classless block is not printed as `<ClassName 0xADDRESS>` for the filter to match. A **buffer or private-storage texture** is a different case: its storage is not on the malloc heap at all, so the walker never sees it and nothing downstream of the walker can.
- **The byte bound is computed from the walker's own total**, which is exactly why it reaches this project's classless allocations: they are on the heap, so they are in the total even though the class filter cannot name them. And it is why it cannot reach a private-storage texture: that is not in the total at all, so nearly two gigabytes can leak without moving the bound. The bound and the class filter are therefore complementary over heap blocks, and both are blind together off the heap.
- **The counters are exact**, and they are the only instrument for either kind of texture. They cannot name which resource, which is why the message says "textures" rather than "accumulation textures": a counter that cannot tell two kinds apart must not claim to.
- **One row is covered by nothing, deliberately:** `A release call stops being sent, still counted`. A release path that decrements without releasing balances every counter and leaks storage no instrument here can see. Name the row rather than its position, since a row's position moves as the table grows and the claim then attaches to the wrong defect.

## The row nothing covers

Leave it in, and say that leaving it uncovered is the decision.

> The row nothing covers is left uncovered deliberately. Saying so is what stops it being rediscovered as a gap worth a fourth instrument.

An all-negative row with no annotation reads as an oversight, and the next person to find it proposes an instrument. An all-negative row with a sentence attached ends that conversation before it starts, or reopens it on better terms.

## Refusing an instrument

Working the matrix out is what makes a refusal arguable. One proposed instrument, a peak-resident-memory slope, was refused rather than built, and the argument is worth reusing verbatim:

> It is a calibrated instrument for a defect an uncalibrated one already catches, and it is blind to the defect nothing else catches.

Both halves came from measurement, and the instrument being compared against is a counter rather than the byte bound. The case for peak memory rested on a leaked buffer, which moves it from 47.7 MB to 57.7 MB while the heap walker reports clean. True, and not sufficient: that same buffer leak is already caught exactly by the buffer counter, so peak memory would be a calibrated way of detecting what an exact instrument already names. Then the case it was actually filed for, a leaked texture in private storage, moves peak memory from **44.1 MB to 44.3 MB while nearly two gigabytes go missing**, because shared storage is in the process's resident set and private storage is not. So it duplicates one instrument and cannot see the defect that motivated it.

The generalizable test for a proposed instrument, then, is two questions:

1. Which row of the matrix does it cover that nothing else covers?
1. Does it cover the row that motivated it?

If the answer to the first is "none" and to the second is "no", the instrument is a cost with no coverage attached. Write the refusal down, with the numbers, or it returns.

## Complementary versus redundant

Two assertions that both catch the same defect are redundant. Two that each catch what the other misses are complementary, and the difference is a measurement rather than a judgement.

The pair that establishes it here:

- A leaked command queue is **137,152 bytes**, under a one-mebibyte bound, and is caught **only by its class name**.
- A leaked history ring has **no runtime class at all**, so the class filter calls it clean, and it is caught **only by the byte bound**.

Neither subsumes the other. Dropping either one loses a defect, and the matrix is how that became visible rather than arguable.

**Note what the matrix row is keyed to, because a merged row hides a disagreement.** The first row names the command queue specifically, at 137,152 bytes and under the bound. A leaked pipeline state is class-visible in the same way and is **8,555,776 bytes**, over the bound, so it is caught twice. Writing one row for "command queue or pipeline state" would put a single value in the byte-bound cell where the two halves differ, which is the kind of quiet averaging a matrix exists to prevent. One row per defect whose cells differ.

## A count is not a discriminator

The sharpest single finding in the source material.

Across two runs of one planted leak the report gave **232** leaks and then **328**, against a clean count of **288** that does not move at all. So the count wandered in both directions while forty megabytes went missing, and **one of those two runs would have read as an improvement**. The byte total moved to 42.6 million both times.

Bytes are what moved; the count is noise with a leak underneath it. The general form: before using a number as a threshold, measure its run-to-run variation on an unmodified tree, and compare that variation against the size of the defect you want to detect. A metric whose noise exceeds the signal is not an instrument.

That project's own measurement: a dropped deallocation leaked **roughly 42.6 million bytes against a clean 18,816**, two thousand times the baseline, and the class filter called it clean both times it was planted. Which is the reason the byte bound exists at all.

## State a tolerance with the error it must not absorb

> A tolerance wide enough to absorb a systematic error is a tolerance that hides one.

Write the bound and its adversary in the same place. Then a later widening has to argue with the adversary rather than with a bare number.

And prefer a deliberately loose bound where looseness is the property that makes it portable. The one-mebibyte bound above sits 56 times above the observed baseline and 40 times below the smallest leak it is for, so a hosted runner's own noise has two orders of magnitude to differ by before it matters. A threshold with that much room on both sides needs no calibration against the machine it runs on, which is precisely what the refused instrument would have needed and could not have.

Quote spread as a ratio rather than a percentage, and say which. Nine runs of that baseline gave a low of 9,728 against a high of 18,816: `(max - min) / max` is 48% and `(max - min) / min` is 93%, and as a ratio it is 1.93x. Those are not the same measure, and a comment that says "a 25% spread" without saying which one has already lost the argument.

## Whether an instrument can discriminate at all

Some instruments are structurally incapable of seeing a class of defect, and knowing which is cheaper than planting blindly.

A thread sanitizer discriminates an ordering **only where that ordering guards non-atomic memory**. It builds a happens-before graph from the atomic operations it observes; it does not look for corruption. So the question to ask of a candidate is not "does it cross threads" but **"what plain memory does its release make safe to touch"**. That sorts a set of four mechanisms immediately:

| Mechanism      | The non-atomic memory it guards                             | Arm possible |
| -------------- | ----------------------------------------------------------- | ------------ |
| Ring buffer    | The sample array                                            | Yes          |
| Teardown gate  | The owner's fields, written after the close and read inside | Yes          |
| Pending update | **None.** The whole message is inside the integer           | No           |
| Pipeline swap  | Objects, not plain memory                                   | No           |

And the measurement that proves a negative is about the subject rather than about the instrument, run as a two-by-two:

| Arm                        | Payload rides alongside | Ordering | Races |
| -------------------------- | ----------------------- | -------- | ----- |
| `pending`                  | no                      | release  | 0     |
| `pending-weakened`         | no                      | relaxed  | **0** |
| `pending-payload`          | yes                     | release  | 0     |
| `pending-payload-weakened` | yes                     | relaxed  | **2** |

Row four is what makes row two mean something. The weakening **is** detectable when anything rides along, so row two is a fact about the mechanism's shape and not about the sanitizer. Without row four, row two is indistinguishable from an instrument that was not running.

## Plant every case, not the one you expect to be representative

Five orderings were planted in a teardown gate, in the real type rather than in a replica, and **only two flag**: the releasing decrement on exit, and the acquiring load in the closer's spin, which are the two halves of one edge. The other three come back clean.

Two things follow:

- **The three that come back clean are not thereby shown to be unnecessary.** They are shown to be outside what **this** sanitizer, in this configuration, against these inputs, can see. That is a different statement from being unnecessary, and it is the reason a source canary still pins all five. See `./references/source-canaries.md`.
- **Generalizing past the measurement takes the rule, not the result.** The three are outside what any happens-before sanitizer can see, but the measurement alone does not show that: the rule above does, because none of the three guards non-atomic memory and that is the only thing such a sanitizer can key on. Keep the two claims separate in the table, so a later configuration change is read against the measurement rather than against the generalization.
- **The issue that filed the work named one of the three that do not flag** as the control arm. Had the control been built that way it would have reported nothing, the judging script would have refused the run, and the failure would have read as a broken sanitizer rather than as the wrong defect to plant. This is why the plants are run rather than assumed.

## A class of defect with no instrument at all

Worth recording beside the rest, because both of these were expected to be positive controls proving a harness reached new code, and both passed:

- A texture descriptor missing its render-target usage flag.
- A pipeline compiled against the wrong pixel format.

Neither is a leak and neither is a lifecycle error. Both are bindings the API accepts and the hardware ignores. Name the class when you find one, because it will not appear in any instrument's output and it will not appear as a gap either.

## Structural guards beat instruments where one is available

One defect had a cheap structural guard that makes it impossible; another had only instruments, and the instrument that would work was a readback refused twice on its own terms. Treating those two the same way would be the mistake. Prefer, in order:

1. A construction in which the defect cannot be expressed.
1. A compile-time or load-time assertion.
1. A test that re-runs.
1. An external instrument with a positive control.
1. A named manual obligation.

Each step down costs more to keep honest. The plant table is what records which step each row is on.
