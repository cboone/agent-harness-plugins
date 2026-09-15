# New skill: write-manual-verification-plan

Issue: [#351](https://github.com/cboone/agent-harness-plugins/issues/351)

## Context

Automated checks run on every push. The rest of verification, whatever a DAW, a simulator, a browser, a device, or a printer has to show a person, is a list an agent writes in chat. In fosforo that list went wrong in three distinct ways, and each one is on the record in the transcripts:

- **It did not say what success looks like.** The rail arm gave four expected values, but not which output line produced them, so the reply was "Arm 2: I'm not sure exactly what I'm looking for." The follow-up answer is the template for this skill: it named the one line (`highest peak row 10.08 implies sample +1.0893`), gave the tolerance in units the reader sees (±0.002, one backing pixel), said which wrong reading means which fault, and named the trap (do not look for a flat top). A heap step said "the count" without naming the column. The absolute number was also swamped by the host's own Metal layers, and the fix was a change measured over 50 open-close cycles, sampled in the same editor state both times, so that +50 dominates ±5 of noise.
- **It could not tell a null result from a broken one.** "I did check 1 and 2, nothing happened (as desired)", in reply to a table whose own footnote said REAPER "cannot confirm the tap is recording anything, or that `reset` is being called at all." Elsewhere, "it should look dim grey rather than black" was retired because byte 5 is black to the eye, so that step returned the same answer whether the fix had worked or not. Two runs of a fifteen-instance load test were voided: one ran against a bundle another worktree built, and the other against a build whose display link never started.
- **It was not persisted.** "List the verification steps here please", "Please reprint the verification steps", and "What's needed for host verification?" all rebuilt the list from scratch. Where a list did get written back into the plan, it held state properly. The beam-as-quads plan records **Done**, **Partly done**, and a measured table per arm, including one arm retired as misdesigned.

The outcome is a `write-manual-verification-plan` plugin in the `writing` category. It is a document-structure guide for a by-hand checklist whose steps each carry Setup, Action, Expected, and Null vs broken. The checklist is persisted to the plan or the issue, resumed from free-text partial results, and scoped by exclusive resource.

The catalog has no prior art. A grep for `manual verification|by hand|verify manually` across every skill body turns up only incidental uses of "by hand". The nearest neighbour is `plant-defects`, which is the same discipline applied to automated instruments, and it is already cross-referenced from there as "run by hand, as a row in the plant table".

## Approach

**Flat references, exactly the four the issue names**, with SKILL.md in `write-formalization-roadmap`'s shape: When to Use, Core Principles, the artifact's schema, Workflow, Reference Navigation, Sources. `create-plugin` permits either a flat set or the `essential/` plus `comprehensive/` split for a `write-*` skill; the issue prescribes flat, and four topic files do not need two reading modes.

**Language- and environment-agnostic, with fosforo as the cited worked source.** Every measurement quoted is real and attributed. Steps for a simulator, a browser, a device, or a printer are marked as illustrative and carry no invented readings.

Four design decisions go beyond the issue text:

1. **Two record lines beside the four parts.** `Why by hand` carries the issue's design note that a step that cannot be automated in principle says so and why, while one merely not automated yet links the issue that defers it. `Result` holds readings rather than ticks.
1. **A fixed status vocabulary**, so a resumed checklist reads the same in every session: `pending`, `passed`, `failed`, `partial`, `void`, `deferred`, `untestable here`. `void` is the one fosforo needed and had no word for: a run that happened and says nothing, whether against the wrong build, with the instrument not running, or under conditions that could not fail.
1. **Step 0 is always "confirm the build under test", re-run at the start of every session.** A result recorded without it is `void`. This is the build-confirmation habit the issue attributes to `stamp-build-provenance` (#341). That skill is filed and not yet built, so the step describes the habit on its own terms and degrades to the weakest confirmation a project has, saying plainly that it is weak.
1. **Scoping uses the convention three skills already read.** `create-worktree`, `address-issue-in-worktree`, and `suggest-next-issue` look in `docs/plans/todo/` for a heading containing "exclusive resource" and take the backticked names under it as the project's declared resources. The checklist's `### Exclusive resources` heading therefore makes it machine-readable to the resource-claim workflow with no change to those skills.

No bundled scripts, so rule 18 and `tests/scrut/` are out of scope.

## Files

### `plugins/write-manual-verification-plan/.claude-plugin/plugin.json`

Alphabetized fields, `"version": "1.0.0"`, `"skills": "./skills"`, `"license": "MIT"`, with author, homepage, and repository matching every sibling. Keywords: `["checklists", "manual-testing", "planning", "resumable", "verification"]`.

The canonical description is 153 characters. That exactly fits the Writing table's current column, so the table needs no repadding:

> Write a numbered, resumable checklist for checks run by hand, where every step says what to do, what you should see, and how to tell nothing from broken.

The same string appears verbatim in four places: `plugin.json`, the marketplace `description`, the plugin README's first paragraph, and the root README's "What it does" cell.

### `plugins/write-manual-verification-plan/skills/write-manual-verification-plan/SKILL.md`

Frontmatter carries `name` and `description` only, as a `>-` folded scalar, under 1024 characters. The description follows the house shape: what the skill does, then `Use whenever ... : (1) ... (N) ...`, then `Covers ...`. It fires on the six situations in the evidence:

1. Asked what can be verified manually, or what host or device verification needs, or to walk through what to test.
1. Writing the by-hand section of a plan or a phase gate.
1. Asked to list or reprint verification steps.
1. Receiving partial results in free text.
1. Someone is unsure what a step is looking for.
1. Splitting a checklist across sessions or around an exclusive resource.

The body has these sections:

- `# Write Manual Verification Plan`, with a one-line summary.
- `## When to Use`, plus when not to: a check with no environment-only component belongs in an automated test.
- `## Core Principles`, seven of them:
  1. Expected is an observation a person can check without having written the code.
  1. A null result has two readings, and the step must separate them.
  1. Nothing is worth believing before the build is confirmed.
  1. Persist before presenting, update in place, and reprint from the record, never from memory.
  1. Record readings, not ticks.
  1. Put a step where the quantity lives.
  1. Scope before splitting.
- `## The Step`, with the four parts, the two record lines, and the status vocabulary, in a compact template.
- `## Workflow`, nine steps:
  1. Look for an existing checklist first, in the plan's `## Manual verification` section or the issue's checklist comment, and resume from it if one exists.
  1. Decide what belongs by hand, and record `Why by hand` for each step.
  1. Write step 0.
  1. Scope the resources.
  1. Write each step in four parts.
  1. Confirm each Expected outruns the noise and that a failure is possible under the stated conditions.
  1. Persist, then present.
  1. Record results as readings.
  1. Close out, so every step ends in a terminal status and nothing is silently dropped.
- `## Reference Navigation`
- `## Sources`

### The four references

#### `./references/step-format.md`

The artifact in full, covering:

- **The document template.** A `## Manual verification` section containing a build line, a record-location line, `### Exclusive resources`, a `### Status` table (#, Step, Needs, Status, Reading), then one `### N. Title` per step with its six bulleted lines.
- **Numbering rules.** Numbers are stable, because the person reports results by number. Never renumber. Append new steps at the end, and retire a step in place with its reason.
- **Each part, with a failing and a passing form taken from the evidence:**
  - Setup includes what must be confirmed first: the build, the environment, and the fixture.
  - Action is one thing to do.
  - Expected locates the observation (which output line, which pixel, which column), states the value and a tolerance in the units the reader sees, maps each plausible wrong reading to its cause, and names any tempting but wrong observation. fosforo's "do not look for a flat top" is the model.
  - Null vs broken is summarized here, and `./references/null-vs-broken.md` covers it in depth.
- **Multi-reading steps.** A table of predicted values with a column for the measured value. "Numbers to record rather than predict" is a legitimate step, where the expected value is unknown and the reading is the point.
- **Why by hand.** Put an arm where the quantity lives. fosforo's density arm had no host-only component and so could never have added anything in a host: its predicted 1.41x effect sat inside a 1.8x scatter. The step states what only the environment has. Examples are the audio path and compositor, a real DAW's buffer handling, and a spatially periodic ripple that an eye is good at. springer's verification table marks its Logic row "not in CI, by hand", with a reason. "Not automated yet" is a deferral with an issue link.
- **Step 0 in detail.** Compare the installed artifact's hash against the fresh build, read a provenance marker if the project stamps one, or read the version or build number where the environment displays it. Re-run it each session. Say which confirmation was used, and say when it is weak.
- **Status vocabulary**, with the rule for each terminal state.

#### `./references/null-vs-broken.md`

The part the issue says is always missing. Each technique is paired with its measured fosforo instance, followed by portable forms:

- **A liveness marker in the same run.** fosforo's once-a-second `rendering at N Hz` line, and the instrumented counter proposed for the audio tap (`48000 samples tapped, 2 resets`). When no marker exists, the step says it cannot separate the two readings, and the checklist offers to add one.
- **Check the transition that must change.** Liveness is checked on the stop, not the start: a frozen window keeps showing the sine indefinitely, so the check fails loudly where "it appeared quickly" does not.
- **A positive control first.** Logic's scan log read 60 Audio Units with the copy, 59 with the symlink, and 60 again. A first attempt read 59 for the copy as well, because the registrar had not settled, and only the control caught that.
- **Conditions under which failure is possible.** Fifteen instances at a 64-sample buffer. At the default buffer no arrangement of instances could fail, so a clean run would say nothing.
- **A discriminating reading where the eye cannot discriminate.** `RGB(5,4,8)`, against an unrendered `RGB(0,0,0)` and the host chrome's `RGB(38,38,38)`, with the blue channel sitting above red and green as the decisive detail.
- **An effect larger than the scatter**, and moving the check when it is not. The defect would have read `g≈249` against an observed `g≈243`, inside a scatter of ten.
- **A change over controlled cycles, sampled in matching state**, when the environment's own objects swamp an absolute count.
- **The pipe that makes a running thing look stopped.** Without `2>&1`, the pipe appears to do nothing. Without `--line-buffered`, the meter arrives in bursts minutes apart, which reads exactly like a render loop that has stopped.
- **An instrument whose null is not evidence.** `auval` cannot see the component at all.
- **The wrong build, where nothing happening was the only available outcome.** A resizable editor was "verified" against a build whose `can_resize` returned false.
- **A cheap plant inside a manual session.** fosforo's NaN pair: with the guard removed the check reads `TraceNotFlat`, and with the guard in place it passes at 0.00000. This is where the reference points to the `plant-defects` skill.
- **Portable forms**, marked illustrative: a network-panel request or console marker in a browser, a log stream predicate in a simulator, a serial log or indicator on a device, and a job ID in the print queue.

#### `./references/resuming.md`

- **Where the record lives.** Use the active plan's `## Manual verification` section when the work has a plan. Otherwise use one checklist comment on the issue, updated in place. The comment URL is recorded in the checklist, and the body goes through the tmpfile pattern from the `use-git` skill: `gh issue comment NUMBER --body-file FILE` to create it, then `gh api --method PATCH repos/OWNER/REPO/issues/comments/ID -F body=@FILE` to update it. `--edit-last` is not used, because it edits the wrong comment once anyone has commented since. There is one living record, never a copy per session.
- **Reprinting.** Reprint from the record, never from memory or scrollback. Remaining steps go first, grouped by resource, and step 0 is always included.
- **Parsing free text.** "4's confirmed, skipping 5 and 6, 7 gave 1.0894" maps to 4 `passed`, 5 and 6 `deferred` (ask for the reason only when none can be inferred), and 7's reading compared against its Expected, with the status derived from the comparison. The reading is recorded verbatim, with date, build, and environment.
- **Reports that do not settle a step.** "Seems fine" against a numeric Expected keeps the step `pending` and asks for the number. "Nothing happened (as desired)" asks whether the liveness marker showed. If it could not have shown, the step becomes `void`, and the record says what would confirm it. "I'm not sure what I'm looking for" means the step is defective, so the fix goes into the record and not only into chat.
- **Predictions that were wrong.** When the code is right and the prediction was not, the reading stands and the Expected is corrected with both values kept.
- **A build that changes between sessions.** Every result is tied to its build. A later commit that touches what a passed step covers marks that step for re-running. One that does not leaves it standing.
- **Deferral as a decision on the record.** "That's a lot of testing, let's save it for later" becomes `deferred` for each remaining step, with the risk each would have covered and where it goes: a later phase or a filed issue.
- **Splitting across sessions** by resource, with step 0 per session.
- **Closing.** The final status table, where every row is in a terminal state and every `deferred` or `failed` row carries its destination.

#### `./references/examples.md`

1. **The three failures, rewritten.** Each has a before and after drawn from the transcripts: the rail arm, the heap count, and the "nothing happened" pair from the audio tap.
1. **One complete checklist.** fosforo's beam-as-quads host pass, restated in the template with its real recorded readings. That covers arm 1 at ±0.5000 and 0.26%, the arm 2 rail table, arm 3's position readings and retired density half, and arm 4 by eye with the reason an eye suffices.
1. **springer's nine-step Logic checklist, three steps restated.** None of the rewrites needs domain detail that the springer plan does not give:
   - Step 8, save and reopen: parameters must be set away from their defaults first, or a lost state reads identically.
   - Step 9, automation after a rebuild: Setup confirms the rebuild actually changed the installed build.
   - Step 5, strum release: a MIDI monitor counts note-ons against note-offs instead of listening for a hung note.
1. **One illustrative step each** for an iOS simulator, a browser, a physical device, and a printer, labelled illustrative, showing the four parts in environments with no fosforo precedent.

### `plugins/write-manual-verification-plan/README.md`

The sibling template, in this order:

```text
# Write Manual Verification Plan
<the description paragraph, verbatim>
**Type:** Skill
**Trigger:** `/write-manual-verification-plan` (also activates automatically)
## Installation      -> the one-line pointer to ../../README.md#install
## What It Does
## Usage
## Examples
## See Also          -> ending with the all-plugins link
```

- **No `## Requirements` and no `## Recommended Permissions`.** The skill needs no tool of its own. `gh` is used only when the record lives on an issue, which Usage states in prose.
- **See Also** links only to plugins that exist: Plant Defects, Create Worktree, Suggest Next Issue, and Write Formalization Roadmap. The two unbuilt companions, `stamp-build-provenance` (#341) and `write-phased-build-plan` (#347), get a prose mention without a link, as `plant-defects` did for its unbuilt companions.

### Catalog registration

- **`.claude-plugin/marketplace.json`:** a new object between `write-lean-tests` and `write-markdown`, with `"category": "writing"`, `"source": "./plugins/write-manual-verification-plan"`, and a version matching `plugin.json`. Then recompute `metadata.version` with `bin/compute-catalog-state`. It is currently `catalog-M70-m103-p156-n57`, and one plugin at `1.0.0` should give `catalog-M71-m103-p156-n58`, to be confirmed from the script rather than assumed.
- **`README.md`:** a `Write Manual Verification Plan` row between Write Formalization Roadmap and Write Markdown. There is no `**External tools:**` bullet, and `## Contents` is untouched.
- **Mirrors:** run `bin/build-codex-marketplace` and `bin/build-opencode-mirror`, and commit both generated trees.

## Notes on the issue body

- **The two voided runs are not both provenance failures.** fosforo's display-link plan records that the first ran against another worktree's bundle, and the second against a build whose display link never started. The provenance plan counts both as path collisions. The skill uses the first as the build-confirmation example and the second as a null-vs-broken example, which is what that record describes.
- **The shape comes from `write-formalization-roadmap` and the file layout from the issue.** That skill's `essential/` plus `comprehensive/` split is not copied, as discussed under Approach.

## Cross-reference hazards

Rule 19 scans `SKILL.md` and every file under `references/`.

- **Do not add `<!-- validate-plugins: repository-paths -->`.** The fosforo and springer `docs/` and `scripts/` paths quoted throughout must stay unresolved against this repository.
- **No backticked single-segment absolute paths.**
- **No backticked unbuilt skill name beside the word "skill".** `stamp-build-provenance` and `write-phased-build-plan` appear only in the plugin README, which the checker does not scan, or in plain prose. `plant-defects`, `create-worktree`, `address-issue-in-worktree`, `suggest-next-issue`, and `use-git` all exist.
- **Keep every relative link in the plugin README resolvable**, fragments included.

## Verification

This worktree has no `node_modules`, so Yarn installs first.

```bash
yarn install --immutable
bin/check-cross-references plugins/write-manual-verification-plan/skills/write-manual-verification-plan/SKILL.md
make format
make build
make validate
make test-all
git status --porcelain dist/ .agents/
```

`make validate` is the gate that matters:

- **Rule 10** compares `metadata.version` against `bin/compute-catalog-state`.
- **Rules 15 and 16** rebuild both mirrors and fail on drift.
- **Rule 17** caps the canonical description at 1024 characters, and warns when the generated Codex copy exceeds 320.
- **Rule 19** resolves every cross-reference.

Run the `check-versions` skill before the PR.

A manual read-through follows, because a skill's prose is the product:

- **No em dashes, no estimates, neutral terminology.** Watch for "dead" and "kill" in DAW and process language: a note hangs, a process is stopped.
- **Every fosforo figure quoted matches its source document.**
- **Every non-fosforo example is marked illustrative.**

## Commits

1. `docs: add plan for the write-manual-verification-plan skill (#351)`
1. `feat: add write-manual-verification-plan skill plugin (#351)`, the plugin directory alone
1. `feat: register write-manual-verification-plan in the marketplace catalog (#351)`, covering the marketplace entry, the root README row, the recomputed catalog state, and both generated trees
