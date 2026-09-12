# The Plant Table

The artifact that makes planting a practice rather than an anecdote.

## The four columns

| Column                          | What goes in it                                                                           |
| ------------------------------- | ----------------------------------------------------------------------------------------- |
| Planted defect                  | The exact edit, specific enough to reapply: the identifier, the value, the call removed   |
| Instrument expected to catch it | The named check, not "the test suite". Which assertion, in which file, at which line      |
| What actually happened          | The error returned, the assertion that fired, the numbers printed. Measured, not intended |
| Test that covers it now         | The test that re-runs this row, or an explicit statement that nothing does and why        |

Three columns produce a document that was true once. The fourth is what makes the rows regress.

## The fourth column is the whole point

A three-column table records that somebody once verified each row by hand, against a device or a host or a tree that no longer exists, and then wrote it down. Nothing re-ran any of it. A later refactor can make an assertion vacuous while the table goes on describing a check that no longer exists.

fosforo's shader plant table was written with three columns and the fourth was added retroactively. Adding it moved every row expressible as a synthetic readback into a test planted against the judgement in isolation rather than against a GPU, and two rows turned out not to be coverable, which the column now says out loud.

Write the fourth column as you go, and treat an empty cell as an open obligation rather than a formatting gap.

## Fill the result column with what happened

The result column records the measurement, not the prediction. This is not pedantry: on the program that produced this skill, the two differed repeatedly.

- An acceptance criterion said a defect was one "today only a hand-run harness would catch". Running the plant showed that harness catching nothing. The gap was one instrument wider than filed.
- A criterion named a specific relaxed ordering as the control arm. Planted, that ordering came back clean. Had the control been built that way it would have reported nothing, the judging script would have refused the run, and the failure would have read as a broken sanitizer rather than as the wrong defect to plant.
- Three criteria were true when they were written and wrong by the time they were run, because a neighbouring change landed first.

The rule that falls out: **an acceptance criterion written against the tree as it was can be falsified by a neighbouring change landing first**, so re-derive it against the current tree rather than executing it as written.

## Commit the check before planting against it

Plant into a tree where the check is already committed. Then reverting the plant is `git restore`, and it cannot take the check with it.

Planting first and writing the check second means the two edits are tangled in the working tree, and the revert that cleans up the plant either removes the check or leaves a partial one behind.

## Rows that must stay green

A negative control is a row whose expected result is a pass, and it belongs in the same table. Its job is to fail if a scope boundary moves.

One worked instance: a repository keeps a historical script excluded from its formatter, so that a formatting pass cannot rewrite a preserved record. The planted defect is reformatting one line of that script. The expected result is that the formatter check **stays green**, because a red result there would mean the ignore file has stopped covering the record and CI is about to demand edits to it. The same plant with the ignore path disabled flags the file, which is what proves the row is measuring the exclusion and not the formatter's silence.

Mark these rows explicitly. A reader who meets a pass in a results column with no annotation assumes the plant failed to fire.

## Rows nothing covers, and rows the compiler refuses

Both belong in the table, for different reasons.

**A row nothing covers** is a decision, not an oversight. Written down, it stops being rediscovered later as a gap that justifies an instrument which would not close it. Left out, it comes back as a proposal every few months.

**A row the compiler refuses** is a better outcome than a caught defect and still worth its line. One plant could not be applied at all because the language's unused-local rule rejected it before any check ran. That row now records why the defect is impossible rather than merely uncaught, which is a stronger claim than any test could make. The row also records what had to be added to exercise the surrounding path at all.

**A retired row** is the third case. When the claim a row asserted moves elsewhere, say so and name its successor rather than deleting the row. One plant asserted that a beam's colour did not vary across a fragment; a later change removed the colour from that stage entirely, so the row now reads as retired and points at the assertion that replaced it.

## A plant that does not compile is not a passing plant

Judge each plant on the build's exit code, not on the shape of its output.

Two plants in one campaign did not compile, and a grep over the output for failure text read both as passes. The distinction between "the check did not fire" and "the check never ran" is exactly the distinction this whole practice exists to preserve, and at the level of a single plant it is the build's status that preserves it.

The same applies to a plant that fires for the wrong reason. Confirm the assertion you named is the one that failed. In one campaign an arm's pin was deliberately made vacuous and the suite still failed, at a different test: the arm was redundant with the assertion beside it, so weakening one always left the other. The plant fired, and it established nothing about the arm it was aimed at.

## Encoding a plant is not the same as covering it

Once a row has a test in the fourth column, the test itself is an unverified claim. Weaken it and confirm something still fails.

Twenty-two weakenings applied one at a time to already-written tests found:

- **Two vacuity holes**, and the sharper one had been passing for two issues. Two checks divided a measured peak by a first peak nothing validated. A blank readback gives `0 / 0`, and `nan > 0.02 * want` is **false**, so a run in which nothing was drawn at all read as a healthy fade and reported one.
- **One reported hole that was not one.** The old spelling was planted back and the test written for it passed, which proved the test asserted nothing rather than that the hole existed.
- **Two arms that survived their own weakening.** One plant sat at 0.01 of full scale, which is 2.4 times a whole backing pixel, so widening a twentieth-of-a-pixel bound twentyfold changed no verdict; the arm was asserting only that the error had a detectable sign. It now sits at 0.001, between the two bounds. The other sat one byte off a palette value, which a neighbouring per-pixel loop refuses anyway, so removing the dedicated check traded one fault for another instead of letting a wrong result through. It is now five levels off.
- **One arm that cannot fire at all**, a defensive branch refused by an earlier guard. An unreachable defensive arm is worth its line; an unreachable one that reads as reachable is not.

Both surviving arms looked like tests of the thing they named and were tests of something weaker. This is the tolerance rule one level up: a tolerance wide enough to absorb a systematic error hides one, and so does a plant far enough outside a bound to be caught by something else.

## State every tolerance with the error it must not absorb

Write the bound and the defect it exists to refuse in the same sentence. A bound with no stated adversary drifts wider at every failure until it absorbs the thing it was for.

## A worked table

The shape to aim for, abridged from a twelve-row original. Note the annotated rows.

| Planted defect                                   | Instrument expected to catch it | What actually happened                          | Test that covers it now                                         |
| ------------------------------------------------ | ------------------------------- | ----------------------------------------------- | --------------------------------------------------------------- |
| Swap two scale factors in the vertex stage       | The level check                 | `LevelMisplaced`, 0.250 read as 0.27366         | `level`, at this exact value                                    |
| Negate the vertical axis                         | The level check                 | `LevelMisplaced`, 0.250 read as -0.24897        | The same test, third value                                      |
| The same, with the level and rail checks skipped | The symmetry check              | `TraceInverted`, +0.5 sits 121.5 below centre   | `symmetry`, which separates a negated axis from an uneven clamp |
| Drop the clamp                                   | The saturation check            | `RailMisplaced`, rail on row 0, expected 4.9    | `saturation`                                                    |
| A beam colour that varies across the fragment    | The one-colour ray check        | `BeamNotOneColour`, worst deviation 0.28152     | **Retired.** The stage no longer carries the colour             |
| Bind the target rather than the source texture   | Any of them                     | The unused-local rule refuses it before any run | **Not coverable, and the better outcome**                       |

Two things the original records underneath, both of which came from doing this rather than predicting it: one defect is caught twice and the broad net fires first, so reaching the second check required relaxing the first, and both are worth keeping because the second is the one that stays decisive if the first ever becomes ambiguous; and a uniform change to the beam's colour is invisible to the ray check by construction, since the check takes its reference from the brightest lit pixel rather than from a restated literal. The second is a limit, stated rather than closed, and the table is where it became visible.
