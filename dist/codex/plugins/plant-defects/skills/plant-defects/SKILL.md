---
name: plant-defects
description: >-
  Deliberately break code to prove a test can see it: plant the defect an
  instrument claims to catch, confirm it goes red, and record it so it
  regresses.
---

# Plant Defects

The discipline of deliberately breaking code to prove a test can see it.

> A test asserts a property of the code. Planting a defect asserts a property of the test, and the second does not follow from the first. Where a check is an external instrument, or where its claim is an absence, the second property has a bad default answer and reading the source cannot improve it.

## When to Use

Use this when a check's own correctness is in question rather than the code's. The three signals, in descending order of urgency:

- **The claim is an absence.** No leak, no race, no unused import, no warning, nothing left behind. A search for absence succeeds for the wrong reason when the instrument was never running.
- **The check is an external instrument.** A sanitizer, a linter, a formatter, a leak checker, a conformance validator. Its exit code answers a question you did not ask, and its silence has two readings.
- **The failure mode is a weakening rather than a break.** A release store simplified to relaxed, a tolerance widened, two correct lines put in the wrong order. Each compiles and each passes, which is what separates this from a defect the compiler already refuses.

Do not use this to re-derive coverage for ordinary code whose failure is a legible compile error or an obviously failing test. The compiler is already telling you.

## Core Principles

1. **The second property has a bad default answer.** "This test would catch that" is a claim about the test. Until it has been run against the defect it names, it is a prediction.
1. **Order the assertions.** Establish that the instrument was running, then that the subject ran and its output parses, and only then read the absence. What is invariant is that no absence is believed before the first two; which of them comes first depends on the instrument, and the strong form of the first (an arm built to fail) is not always available.
1. **Record what happened, not what was expected.** A result column filled in from the issue that filed the work is not a measurement. Several of the findings behind this skill are cases where the two differed.
1. **Encoding a plant is not the same as covering it.** A plant far enough outside a bound is caught by a sibling check, so the arm that names it is asserting only that the error had a detectable sign. Weaken each assertion in turn and confirm something still fails.
1. **A plant that does not compile is not a passing plant.** Judge on the build's exit code, not the shape of its output, or a grep for failures reads a compile error as a pass.
1. **Instruments do not compose by assumption.** Tabulate defect against instrument and mark what each one cannot see. Where a row turns out to be covered by nothing, say so deliberately rather than leaving it implicit. A matrix that covers every row is a fine outcome; the point is to measure the cells, not to manufacture a gap.

## The Plant Table

The artifact. Four columns, one row per planted defect:

| Planted defect                              | Instrument expected to catch it | What actually happened                     | Test that covers it now                 |
| ------------------------------------------- | ------------------------------- | ------------------------------------------ | --------------------------------------- |
| Divide x by `count` rather than `count - 1` | The silence check               | `TraceNotDrawn`, 959 of 960 columns lit    | `silence`, at one column dark           |
| The same, with the silence check relaxed    | The span check                  | `TraceEndsEarly`, columns 0 to 639 of 959  | `horizontalMapping`, both edges reached |
| Bind the target rather than the source      | Any of them                     | Refused by the compiler as an unused local | This spelling cannot be written         |

The fourth column is what makes the table regress rather than describing a check nobody re-runs. Without it, every row was verified once, by hand, and then written down, so a later refactor can make an assertion vacuous while the table goes on describing it.

## Failure Classes

Four, not two. The third survives every coverage mode, because the code is not in the analyzed program at all. The fourth is reported by branch or condition coverage, and by line coverage too where the untaken arm has body lines of its own; it hides from line coverage only where that arm has no lines to report.

| Class                     | What it is                                                                               | Why more tests do not help                                                              |
| ------------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| False negative            | A defect one instrument cannot see, closed by naming a second that can                   | The suite is fine; the instrument is the wrong one for this defect                      |
| False positive            | Nothing was broken and a required check said something was                               | Belongs to the check's scaffolding, not the code; no number of instruments addresses it |
| Structural uncoverability | Code that no test binary compiles, so it is absent from the analyzed program             | No test written in that suite could reach it, however it was written                    |
| Unvisited branch          | It compiles, an instrument could reach it, and no arm was ever written to steer it there | Every counter it moved was read by something, so nothing looked absent                  |

## Workflow

1. **Name the claim and the instrument.** Write down which check is supposed to be asserting the property, in the form "if X broke, Y would fail".
1. **Write the table first**, with the result column empty. Filling it in later is the work.
1. **Commit the check before planting against it**, so reverting the plant reverts the plant and not the check it was testing.
1. **Confirm the unmodified tree passes, and stand up a positive control.** See `./references/ordered-assertions.md`. If nothing can be made to fail on purpose, fall back to a marker proving the instrument produced output, and record that the weaker form is what you have.
1. **Plant one defect at a time**, revert between plants, and prefer the real code over a replica. A control that models the defect is not the subject exhibiting it.
1. **Record what happened**, and confirm the assertion you named is the one that fired rather than a neighbour catching it first.
1. **Plant against the judge as well as the subject.** Weaken each assertion and confirm something still fails. This is the step that finds arms which look like tests of the thing they name and are tests of something weaker.
1. **Convert every plant expressible as data into a test**, so it regresses. Leave the rest as manual obligations with a named home rather than as prose.
1. **Write down the rows nothing covers.** Saying so is what stops the gap being rediscovered later as an argument for an instrument that would not close it.

## Reference Navigation

**Start here:**

- `./references/the-plant-table.md`: the artifact, its four columns, and the rules about rows that stay green, rows nothing covers, and acceptance criteria
- `./references/ordered-assertions.md`: positive control, then progress or parse, then absence, with two worked judging scripts

**By symptom:**

- `./references/vacuous-passes.md`: a check that runs on nothing passes, and the catalogue of ways that happens
- `./references/structural-uncoverability.md`: the four failure classes, and code that no test binary compiles
- `./references/instrument-blindness.md`: tabulating defect against instrument, complementary versus redundant assertions, and refusing an instrument
- `./references/source-canaries.md`: asserting a file's own source text when the behaviour cannot be reached

## Relation to Mutation Testing

Mutation testing is the automated form of the same idea and is the right tool where one exists for the language, with `cargo-mutants`, `mutmut`, `Stryker`, and `PIT` among the mature ones. This practice differs in four ways, and the differences are the reason it is worth doing by hand even where a tool is available.

- **Targeted rather than exhaustive.** A mutation tester enumerates syntactic mutations. Here you plant the exact defect an instrument claims to catch, including defects no mutation operator generates: a wrong build mode, a glob that matches nothing, a relaxed memory ordering, a missing release call.
- **It covers external instruments.** A mutation tester judges a test suite. Nothing enumerates mutations that a leak checker, a sanitizer, or a conformance validator is supposed to notice.
- **The output is a durable document.** A surviving-mutation report is a run. A plant table is committed, reviewed, and cited, and its fourth column ties each row to the test that now re-runs it.
- **It records the negatives.** A plant that nothing catches, a plant the compiler refuses, and an instrument deliberately not built are all findings worth their rows.

Converting the plants that can be expressed as data into ordinary tests is the affordable share of mutation testing, and it is the right destination for most rows.

## Sources

The practice and every measurement quoted in these references come from two of the author's projects:

- `cboone/fosforo`: the eleven-issue verification-gaps program in `docs/plans/done/2026-09-04-close-the-verification-gaps-in-the-test-suite.md`, the plant table in `docs/plans/done/2026-08-29-verify-the-shader-offscreen-against-the-constants.md`, the source-canary module `src/canary.zig`, the judging scripts `scripts/race-check` and `scripts/smoke-leak-check`, the instrument matrix in `docs/notes/leak-instruments.md`, and ADRs 0013 and 0016
- `cboone/springer`: the verification program table in its build plan, and the ADRs that make planting an acceptance criterion rather than a formality

Related plugins in this catalog: `write-lean-tests` for the compile-time API regression case, `write-scrut-tests` for snapshot assertions that can stop discriminating, `set-up-ci` for the gates these controls are attached to, and `review-branch`, where a plant table is what a reviewer should be looking for.
