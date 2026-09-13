# New skill: plant-defects

Issue: [#345](https://github.com/cboone/agent-harness-plugins/issues/345)

## Context

Every testing skill in this catalog teaches how to write an assertion. None teaches how to find out whether an assertion can fail. The principle, stated in fosforo's verification-gaps plan and adopted by springer's build plan:

> A test asserts a property of the code. Planting a defect asserts a property of the test, and the second does not follow from the first. Where a check is an external instrument, or where its claim is an absence, the second property has a bad default answer and reading the source cannot improve it.

fosforo ran an eleven-issue program on that premise and found what writing more tests would not have surfaced: a blank readback that passed the decay checks because `nan` compares false against every bound; a shader watcher whose real `poll` was not merely untested but not compiled, so 297 of 297 tests reported green and the smoke harness reported `ok` with the defect in place; two tests believed to encode a plant that were covering something else; five memory orderings planted in a teardown gate of which only two flag under Thread Sanitizer, the filing issue having named one of the three that do not.

The outcome is a plugin, `plant-defects`, in the `code-quality` category: a manual, targeted, documented practice adjacent to mutation testing, with the plant table as a first-class artifact that regresses rather than prose about a check nobody re-runs.

The catalog has no prior art. Grepping all 51 skill bodies and every reference file for `mutation|mutant|plant|defect|false negative|vacuous|positive control|prove the test fails` returns only incidental hits: `cargo mutants` in `scaffold-rust-cli`'s gitignore template, and CI-flake language in `monitor-pr`. The nearest conceptual neighbor is one line in `write-lean-tests` ("Piecewise tests can all pass while the API still fails to compose"), which this skill cross-references rather than restates.

## Approach

Six flat reference files under `references/`, exactly as the issue prescribes, with a short SKILL.md that carries the principle, the plant-table template, the failure-class table, and a nine-step workflow. Depth goes in the references; the create-plugin convention reserves the `essential/` plus `comprehensive/` split for `write-*` style guides, so a flat topic-named set is correct here.

Two deliberate generalizations beyond the issue text:

1. **Four failure classes, not three.** The issue says "beside false negative and false positive, name structural uncoverability". ADR 0013 catalogues a fourth that the issue omits and that is the hardest to notice: an **unvisited branch**, where the code compiles in a plain build, an instrument that could reach it exists, and no arm was ever written to steer it there. Every counter it moved was read by something, so nothing looked absent. Including it.

2. **Language-agnostic, with the Zig and macOS material as cited worked examples.** The sources are Zig, Metal, and `leaks`. Downstream projects are Go, Rust, Python, Swift, and TypeScript, so each reference pairs the real measurement with the equivalent hole in other toolchains: Go build tags, Rust `#[cfg]`, C `#ifdef`, Python `if TYPE_CHECKING`, Swift `#if DEBUG`, a pytest run that collects zero items, an over-broad snapshot glob that can no longer fail.

No bundled scripts. The issue's structure block has none, so rule 18 and `tests/scrut/` stay out of scope.

## Files

### `plugins/plant-defects/.claude-plugin/plugin.json`

Alphabetized fields, `"version": "1.0.0"`, `"skills": "./skills"`, `"license": "MIT"`, author and homepage matching every sibling. Candidate keywords: `["defects", "instruments", "testing", "verification", "vacuous-passes"]`.

Canonical description, 151 characters, which fits the root README's existing 154-character column so the table needs no repadding:

> Deliberately break code to prove a test can see it: plant the defect an instrument claims to catch, confirm it goes red, and record it so it regresses.

This same string is the marketplace `description`, the first paragraph of the plugin README, and the root README's "What it does" cell, verbatim in all four places.

### `plugins/plant-defects/skills/plant-defects/SKILL.md`

Frontmatter is `name` and `description` only, the `>-` folded scalar at 2-space continuation indent, `name` equal to the directory name. The description follows the house shape: what it does, `Use whenever ... : (1) ... (N) ...`, then a `Covers ...` sentence. It fires on test-verification subjects (a coverage claim, "would I know if this broke", an acceptance criterion naming an instrument, a check that asserts an absence) and not merely on the slash command.

Body sections: the principle as a block quote, `## When to Use`, `## Core Principles`, `## The Plant Table`, `## Failure Classes`, `## Workflow`, `## Reference Navigation`, `## Relation to Mutation Testing`, `## Sources`.

The plant table template, generalized from fosforo's twelve-row instance:

| Planted defect | Instrument expected to catch it | What actually happened | Test that covers it now |
| -------------- | ------------------------------- | ---------------------- | ----------------------- |

The workflow, nine steps:

1. Name the claim and the instrument that is supposed to be asserting it.
1. Write the table first, result column empty.
1. Commit the check before planting against it, so reverting the plant does not revert the check.
1. Confirm the unmodified tree passes, and stand up a positive control.
1. Plant one defect at a time and revert between plants.
1. Record what happened, not what was expected, and confirm the assertion you named is the one that fired.
1. Plant against the judge as well as the subject: weaken each assertion in turn and confirm something still fails.
1. Convert every plant expressible as data into a test, and leave the rest as named manual obligations.
1. Record the rows nothing covers, deliberately.

### The six references

#### `./references/the-plant-table.md`

The artifact. The fourth column is what makes plants regress; fosforo added it retroactively in #92 and it changed the table's value. Result is what happened rather than what was predicted. Rows that must stay green are negative controls, as in springer's Prettier row, whose whole point is that a red result there would mean the ignore file stopped covering a historical record. Rows retired when the claim moves, and rows the compiler refuses, which is a better outcome than a caught defect and still worth its line. A plant that does not compile is not a passing plant: judge on the build's exit code, not on the shape of its output, because a grep for failures reads a compile error as a pass. Encoding a plant is not the same as covering it, the finding that twenty-two weakenings produced: two arms sat far enough outside their bound that a sibling check fired first, so weakening the arm they named changed nothing. Two rules about acceptance criteria: one that names the instrument it expects to fail is asserting something and has to be run rather than read; one written against the tree as it was can be falsified by a neighbouring change landing first.

#### `./references/ordered-assertions.md`

The order is the point. First, the positive control ran and was flagged. Second, the subject ran to completion, its output parses, and its progress counter moved. Third, the absence. A search for absence succeeds for the wrong reason when the instrument was never running. Two worked examples, both already parameterized for reuse: `race-check`, which takes the harness, both arm names, and a progress field as arguments, and whose control paid for itself on the first run when a sanitizer build linked its runtime and emitted none of its instrumentation; and `smoke-leak-check`, which asserts the harness passed, then that a report exists and parses, then the class filter, then the byte bound, with the class filter before the bound because it can say what leaked. Distinct exit codes for "nothing was measured" and "the thing is broken", which matters under `continue-on-error` where the exit code is the whole message. A control that models the defect is not the subject exhibiting it, so plant in the real primitive too. The instrument's own cost can make a control unfaithful, and the counter proving the two threads met is the only thing that would say so. Meta-plant: break the checker and confirm it fails at assertion one rather than passing.

#### `./references/vacuous-passes.md`

A check that runs on nothing passes. The catalogue, each entry a measured instance: a formatter check reporting zero files read; `actionlint` with no `shellcheck` on `PATH`, which skips every `run:` block and exits 0, where a planted `SC2086` exits 1 with it present and 0 without; a glob that matches nothing, `extend-include = ["measure-trace"]` reporting "All checks passed" over a planted unused import until `["**/measure-trace"]` fixed it; a spell-checker `extend-words` entry that suppresses nothing because the tool splits identifiers before judging them, the same failure shape twice in one branch; `nan` compared against every bound, so `0 / 0` read as a healthy fade and reported one; an assertion compiled out in the optimize mode CI actually runs; an over-broad snapshot glob that can no longer fail; a grep-based CI assertion that a rename makes vacuous, where the positive control protects the binary being readable rather than the needle still being right; and `grep ... || true` yielding an empty string, which bash reads as zero in an arithmetic context, and zero passes. The remedy is a positive control: assert a non-zero count, print the dependency's version, find the string you know is there before trusting the absence of one you hope is gone. Every null result should share a run with a positive control. The non-vacuous direction: pair each bound with an assertion in the opposite direction, so an unconditional `return 1.0` fails rather than passes.

#### `./references/structural-uncoverability.md`

The four-class table, then the third class in detail: code no test binary compiles, invisible to coverage tools because it is not merely uncovered but absent from the analyzed program. The measured case: a watcher written as `if (shader.live) struct {…} else struct {…}` where `live` folds in `!builtin.is_test`, so a test build takes the stub; the plant was applied to `poll` as it stood and `zig build test` reported 297 of 297 while the smoke harness reported `ok` with all five hot-reload arms running. Nothing caught it, so the gap was one instrument wider than the issue claimed. Causes across toolchains: comptime and const-folded branches, build tags, feature flags, `#ifdef`, build-mode branches, test-only stubs, dead-code elimination. Lazy analysis: a declaration nothing calls may not be type-checked at all, and a build manifest lists the files the compiler read rather than the declarations it checked, so the check that answers the question is a planted type error in the specific declaration. Run the suite in the mode that ships, pin the mode, and give the pin its own control, or a refactor that drops it leaves a green job testing the same mode twice. Then the fourth class, the unvisited branch, and why it is the hardest to see.

#### `./references/instrument-blindness.md`

Build the matrix rather than assuming instruments compose: defects down the side, instruments across the top, marking what each cannot see. fosforo's is six planted defects against five instruments, not six against six as the issue says, and its bottom row is covered by nothing, deliberately, because saying so is what stops it being rediscovered as a gap worth a fourth instrument. Working the table out is what led to refusing a proposed peak-RSS instrument rather than building it: it is a calibrated instrument for a defect an uncalibrated one already catches, and it is blind to the defect nothing else catches. Complementary rather than redundant, with the measurements that prove it: a leaked command queue is 137,152 bytes, under the byte bound and caught only by its class, while a leaked ring buffer carries no class at all and is caught only by the bound. Counts are not discriminators: 232 leaks and then 328 against a clean 288 that does not move, while forty megabytes went missing and the byte total moved both times, so one of those runs would have read as an improvement. A leaked texture in private storage is invisible to a malloc-heap walker and to peak RSS both, 44.1 MB to 44.3 MB while nearly two gigabytes went missing, and only an explicit counter sees it. State every tolerance with the error it must not absorb; a deliberately loose bound needs no calibration against the machine it runs on, which is exactly what the refused instrument would have needed. A counter that cannot tell two kinds apart must not claim to. And the rule that decides whether an instrument can exist at all: a sanitizer discriminates an ordering only where that ordering guards non-atomic memory, so the question is not "does it cross threads" but "what plain memory does its release make safe to touch". Five orderings planted in the real type, two flag, and the filing issue named one of the three that do not; a 2x2 with and without a payload is what proves a clean result is a fact about the subject's shape rather than about the instrument.

#### `./references/source-canaries.md`

For an ordering a single-threaded suite cannot see, where the failure is a weakening that compiles and passes and the instrument that would catch it needs a host you do not have. Read the file's own source as text at build time and assert the ordering-critical line is stated exactly as written. Three primitives, and why all three: an exact-match count, a containing count, and an order predicate. A file that states every line asked of it and quietly acquired a sixth operation satisfies every exact-match check and fails the containing count; counting cannot see two correct statements in the wrong order, and reversing a copy-then-release pair is not a crash but a picture drawn from two different compiles. Two matching properties, both answers to flaws rather than choices: match a statement trimmed, so re-indenting into an `if` is a wash rather than a failure; and treat a line whose trimmed text begins with a comment marker as not a statement, so a doc comment naming the identifier cannot break a count, and an assertion that a term appears zero times is expressible in a file whose own docstring names it twice in order to forbid it. The residual stated rather than hidden: a trailing comment is still part of its statement line. Cut the source at the test banner so a canary cannot read its own string literals and count them as code. A passing canary means the lines are unchanged, not that they are correct: it is deliberately the faster of two checks rather than the harder to fool, and a careless global replace rewrites the assertion along with the code, which is accepted because a second guard catches that. Guard the guard, with the helper's own tests asserting each property it claims and both flaws it fixed as absences. Two negative controls on the checker itself, each of which must stay green. Then the portable forms: a test that reads its own source, a lint rule, a golden file of extracted declarations, and a CI grep, with the caveat that nothing links the needle to the declaration.

### `plugins/plant-defects/README.md`

The 52-plugin template exactly, in this order:

```text
# Plant Defects
<the description paragraph, verbatim>
**Type:** Skill
**Trigger:** `/plant-defects` (also activates automatically)
## Installation      -> the one-line pointer to the marketplace install section
## What It Does
## Usage
## Examples
## See Also          -> ending with the all-plugins link
```

No `## Requirements` and no `## Recommended Permissions`: the skill runs no command of its own, and 31 of 52 plugins omit the permissions section. See Also links only to plugins that exist, namely `write-lean-tests`, `write-scrut-tests`, `set-up-ci`, and `review-branch`. The pairings with the two skills the issue names are still unbuilt, so they get a plain prose mention in the README and no link.

### Catalog registration

- `.claude-plugin/marketplace.json`: new object between `pin-everything` and `pr`, `"category": "code-quality"`, `"source": "./plugins/plant-defects"`, version matching `plugin.json`, then `metadata.version` recomputed with `bin/compute-catalog-state`. Currently `catalog-M65-m92-p155-n52`; one plugin at `1.0.0` gives `catalog-M66-m92-p155-n53`, to be confirmed from the script rather than assumed.
- `README.md`: a `Plant Defects` row after `Lint and Fix` and before `Set-Up Linters`, at 62/22/154 cell widths. No `**External tools:**` bullet, since the skill requires none. `## Contents` is heading-level navigation and is not touched.
- `bin/build-codex-marketplace` and `bin/build-opencode-mirror`, both committed, including the new `dist/opencode/skills/plant-defects` symlink.

## Corrections to the issue body

Worth recording, since the issue will be read alongside the result.

| Issue says                                              | Actually                                                                                 |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| The program plan is at `docs/plans/todo/2026-09-04-...` | It is in `docs/plans/done/`                                                              |
| A theory-of-instruments table in fosforo's `AGENTS.md`  | That phrase is an ADR 0013 heading; the matrix lives in `docs/notes/leak-instruments.md` |
| Six planted defects against six instruments             | Six against five                                                                         |
| Three failure classes                                   | Four; the fourth is the unvisited branch                                                 |
| springer states the principle in the quoted wording     | springer paraphrases it and credits fosforo; the verbatim sentence is fosforo's          |

Every measurement the issue quotes checks out: the `nan` readback, 297 of 297, the five orderings of which two flag, 44.1 MB to 44.3 MB against nearly two gigabytes, 232 and 328 against a clean 288, and the 137 KB command queue, which is 137,152 bytes exactly.

## Cross-reference hazards

Rule 19 scans `SKILL.md` and every file under `references/`, so all six references are checked.

- Do **not** add `<!-- validate-plugins: repository-paths -->`. Without it, `docs/` and `bin/` prefixes are skipped, which is what keeps the fosforo paths quoted throughout from being resolved against this repository and failing. `scripts/` and `src/` are in no prefix list and are safe either way.
- No backticked lowercase single-segment absolute path, because the checker reads `` `/tmp` `` as the skill name `tmp`.
- No backticked name adjacent to the word "skill" or "skills" unless `plugins/<name>` exists. The two skills the issue names as companions do not exist yet, so they are mentioned only in the plugin README, which this checker does not scan. The same trap applies to tool names: not "the `actionlint` skill".
- Keep every relative link in the plugin README resolvable, fragments included, since `markdownlint-rule-relative-links` fails the build on a dead `#fragment`.

## Verification

This worktree has no `node_modules`, so the Markdown half of the lint suite cannot run until Yarn installs, which is the first step rather than an afterthought.

```bash
yarn install --immutable
bin/check-cross-references plugins/plant-defects/skills/plant-defects/SKILL.md
make format
make build
make validate
make test-all
```

`make validate` is the gate that matters: rule 10 compares `metadata.version` against `bin/compute-catalog-state`, rules 15 and 16 rebuild both mirrors and fail on any drift, rule 17 caps the canonical skill description at 1024 characters and warns above 320 on the generated Codex copy, and rule 19 resolves every cross-reference. Then confirm `git status --porcelain dist/ .agents/` is empty, which is the check CI runs, and use the `check-versions` skill before opening the PR in case another branch moved a version.

Manual read-through afterwards, since a skill's prose is the product: no em dashes, no time or effort estimates, neutral terminology throughout. That last one needs attention here, because mutation-testing jargon collides with it directly: a planted defect is caught, flagged, or refused, never killed.

## Commits

1. `docs: add plan for the plant-defects skill (#345)`
1. `feat: add plant-defects skill plugin (#345)`, the plugin directory alone
1. `feat: register plant-defects in the marketplace catalog (#345)`, marketplace entry, root README row, recomputed catalog state, and both generated trees
