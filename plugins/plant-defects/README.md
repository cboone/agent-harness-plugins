# Plant Defects

Deliberately break code to prove a test can see it: plant the defect an instrument claims to catch, confirm it goes red, and record it so it regresses.

**Type:** Skill
**Trigger:** `/plant-defects` (also activates automatically)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

A test asserts a property of the code. Planting a defect asserts a property of the test, and the second does not follow from the first. Where a check is an external instrument, or where its claim is an absence, the second property has a bad default answer and reading the source cannot improve it.

This skill teaches the manual, targeted, documented form of that verification: the plant table as a committed artifact with a column naming the test that covers each row, the assertion order that separates an absence from an instrument that was not running, the ways a check comes to run on nothing, code that no test binary compiles, the matrix that records what each instrument cannot see, and source canaries for orderings a single-threaded suite cannot reach.

It is adjacent to mutation testing and differs in four ways: it is targeted rather than exhaustive, it covers external instruments that no mutation operator can address, its output is a committed document rather than a run, and it records the negatives, including the rows nothing covers and the instruments deliberately not built.

Every measurement quoted in the references is real, drawn from an eleven-issue verification program in one project and the verification plan of another. Among them: a blank readback that passed the decay checks outright because a not-a-number value compares false against every bound, and a watcher whose real polling function was not merely untested but not compiled, so 297 of 297 tests reported green and the smoke harness reported `ok` with the defect in place.

## Usage

```text
/plant-defects
```

The skill also activates on its own when the subject is whether a check can fail: an assertion whose claim is an absence, reliance on an external instrument, an acceptance criterion that names an instrument it expects to fail, or the question of what a green suite actually establishes.

## Examples

- "this test passes, but would it catch the bug it is for": the nine-step workflow and the plant table
- "CI is green, is it actually checking anything": the vacuous-pass catalogue and the positive-control remedy
- "coverage says this file is fine": the four failure classes, including code absent from the analyzed program
- "should we add a memory instrument": the blindness matrix, and the argument for refusing one
- "/plant-defects": loads the full practice explicitly

Two companion skills are filed and not yet built: one for real-time audio code, whose concurrency-verification section is this method applied to memory ordering, and one for auditing CI workflows, which takes the vacuous-pass half and applies it to GitHub Actions specifically.

## See Also

- [Write Lean Tests](../write-lean-tests/README.md): the compile-time case, where piecewise tests all pass while the API fails to compose
- [Write Scrut Tests](../write-scrut-tests/README.md): snapshot assertions that widen until they can no longer discriminate
- [Set-Up CI](../set-up-ci/README.md): the CI gates these controls attach to
- [Review Branch](../review-branch/README.md): where a reviewer should be looking for a plant table
- [All plugins](../../README.md)
