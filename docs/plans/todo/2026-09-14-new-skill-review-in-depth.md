# New skill: review-in-depth, an aggressive review before external review

Tracks #425 (phase 1) and #426 (phase 2).

## Context

Automated and human reviewers keep finding defects after a pull request opens, one or two per round, and every fix pushed in response starts another round. An analysis of six recent branches in this repository (2026-09-14) measured the pattern; the numbers below are the evidence for building this skill, not material for the skill itself.

| Branch shape                | External review rounds | Findings | Present at the first review | Created during review (fix-induced, drift, edge-case expansion) | False positives |
| --------------------------- | ---------------------- | -------- | --------------------------- | --------------------------------------------------------------- | --------------- |
| Narrow change, strong tests | 5                      | 11       | 7                           | 4                                                               | 0               |
| Script plus docs, 6k lines  | 33                     | 89       | 17                          | 59                                                              | 3               |
| Scaffold skill              | 41                     | 94       | 26                          | 46                                                              | 5               |
| Prose reference skill       | 15                     | 80       | 33                          | 35                                                              | 0               |
| Script, template, docs      | 46                     | 171      | 37                          | 99                                                              | 18              |
| Two skills plus five others | 25                     | 163      | 48                          | 63                                                              | 36              |

Four observations generalize beyond this repository and shape the design:

1. **One review pass is a sample, not a verdict.** Repeated reviews of identical code surfaced new findings, and the external reviewer itself runs an ensemble of independent passes. A single local read will miss what a second, differently aimed read finds.
1. **Most findings fall into a small set of repository-independent classes**: a restated fact drifting from its source, a universal promise that some path breaks, an option that does not reach every step, an input the contract never addressed, a failure path that skips cleanup, an unpaginated collection, a claim about an external tool that was never checked, a test that cannot reach the code it covers.
1. **The way findings are fixed creates the next round's findings.** Fixing the flagged instance while its siblings remain, and hardening against ever-less-likely inputs instead of narrowing the promise, each produced more findings than they closed.
1. **An external round is expensive and a local pass is not.** Each external round measured about $5 to $9 of agent tokens at API list prices plus $0.38 (Lite) to $2.10 (Balanced) of Copilot credits, and every push restarts the review. A local pass needs no push.

Existing skills do not cover this:

| Skill                         | What it does                                          | Why it is not this                                                                                                                                         |
| ----------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `review-branch`               | Summarizes the branch and evaluates it                | A report, not a fix-it pass; it says "Do not invent hypothetical problems" and skims large diffs, which is exactly the posture that leaves findings behind |
| `final-review-pass` (#371)    | Hygiene before `pr`: leftovers, conventions, commits  | Aimed at polish and plan state, not at defect classes; it should call this skill, not absorb it                                                            |
| Claude Code's bundled review  | Correctness and cleanup review of a diff              | Claude Code only, and it has no restatement map, class sweep, or remedy discipline                                                                         |
| `lint-and-fix`                | Runs linters and formatters                           | Mechanical; does not read for meaning                                                                                                                      |
| `plant-defects`               | Proves a test or instrument can see a defect          | Complementary: the tests lens hands off to it when a check's ability to fail is in question                                                                |
| `resolve-copilot-pr-feedback` | Processes external review feedback after the PR opens | Reactive; this skill runs before the first external review                                                                                                 |

**Intended outcome:** `/review-in-depth` runs before a branch meets any external reviewer. It maps what the change touches and restates, sends several independently aimed passes over it, verifies every candidate finding, fixes verified defects across their whole class, re-reviews its own fixes, and reports what it changed, what it left alone, and what needs a decision. It works in any repository, in any language, under Claude Code, Codex CLI, and OpenCode.

## Design decisions

These were settled with the user before implementation. They are load-bearing; do not quietly revisit them during it.

| Decision             | Choice                                                                                                                                                                            |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name                 | `review-in-depth`                                                                                                                                                                 |
| Relationship to #371 | Separate plugin. `final-review-pass` invokes it as its first step through a parent continuation contract, so "final review pass, then `/pr`" gets it without a second instruction |
| Posture              | Generate liberally, verify strictly. Candidates may be hypotheses; only verified findings reach the fix step                                                                      |
| Passes               | Independent lens passes. Fan out to fresh-context workers where the harness supports subagents; run them sequentially otherwise                                                   |
| Default mode         | Find, verify, fix, commit without pushing. `--report-only` stops after triage                                                                                                     |
| Remedy order         | Remove or narrow the promise, document the limit, fix, defer with a tracked issue, decline with a reason. Hardening is not the default response to an unlikely input              |
| Re-review            | A focused pass over the fix diff, capped by `--max-passes` (default 2)                                                                                                            |
| User decisions       | Batched into one question after triage: splitting scope, changing documented behavior, removing a feature                                                                         |
| Reviewer notes       | Proposed in the report, written to the repository's reviewer-instruction files only on confirmation                                                                               |
| Persistence          | Terminal report by default; `--save` writes the ledger to `docs/reviews/` in a form `address-review` can consume                                                                  |
| Category             | `code-review`                                                                                                                                                                     |
| Phasing              | Phase 1 (prompt-only skill) and phase 2 (review-history calibration script) ship as separate PRs                                                                                  |

## Approach

### Phase 1: plugin `plugins/review-in-depth/` at `1.0.0`

Skill-only, no bundled script in this phase. One reference file per lens keeps each worker's brief small: a worker loads the review map, its own lens, and the files it was assigned, never the whole catalog or the conversation.

```text
plugins/review-in-depth/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── review-in-depth/
        ├── SKILL.md
        └── references/
            ├── review-map.md
            ├── fan-out.md
            ├── verification.md
            ├── triage.md
            ├── ledger.md
            ├── lens-restatement-drift.md
            ├── lens-promises.md
            ├── lens-options-and-paths.md
            ├── lens-inputs-and-contract.md
            ├── lens-failure-and-state.md
            ├── lens-collections-and-limits.md
            ├── lens-external-facts.md
            ├── lens-tests-and-evidence.md
            ├── lens-security.md
            ├── lens-conventions.md
            └── lens-scope-and-surface.md
```

Draft `plugin.json` description, kept under the 320-character Codex preference that rule 17 warns on:

```text
Aggressively review a branch before external review: map what the change restates, run independent lens passes, verify every finding, fix defects across their whole class, and re-review the fixes.
```

### `SKILL.md` workflow

#### Options

- **--base `<ref>`**: compare against this ref instead of the merge base with the default branch
- **--since `<ref>`**: focused mode; review only the commits after `<ref>`, with the fix-review lenses (used for the re-pass and by callers after a fix batch)
- **--report-only**: stop after triage; change nothing
- **--lenses `<list>`**: run a subset of lenses
- **--max-passes `<n>`**: cap the focused re-passes (default 2)
- **--save**: write the ledger to `docs/reviews/`

#### Step 1. Resolve scope

Find the base and merge base the way `review-branch` does. List changed files and classify each as source, test, documentation, configuration, or generated. Detect generated files from the repository itself: `linguist-generated` in `.gitattributes`, paths the agent config names as generated or mirrored, and generated-file headers. Generated files are not reviewed line by line, but the map records their sources so the drift lens can confirm they were regenerated.

#### Step 2. Build the review map

The map turns "read carefully" into things a lens can check one by one. Detail lives in `./references/review-map.md`. Six inventories:

1. **Changed surfaces**: every changed file, plus the unchanged callers, callees, and referrers of what changed. External reviewers flag unchanged code next to a change, so the map includes it.
1. **Restatements**: every place that restates a fact the change touched. Usage and help text, READMEs, examples, permission and configuration allowlists, copied or mirrored code, prose descriptions of a contract, fixtures, counts, and changelogs. Each entry pairs a source with its restatements.
1. **Options and modes**: every flag, environment variable, configuration key, and mode the change adds or touches, with every step, early exit, and output that should honor it.
1. **Promises**: every universal or quantified claim in changed text, comments, messages, and names. Found by searching for words like "every", "all", "any", "only", "always", "never", "cannot", "guarantees", and literal counts.
1. **External facts**: every claim about a tool, API, file format, platform, or version the change relies on.
1. **Inputs and contract**: each input source (arguments, files, environment, network responses, user data), where it is validated, and what the documentation says is supported.

The map also names the conventions sources the repository defines: agent config files, contributing guides, linter configuration, and any reviewer-instruction files. Reviewers cite these, so the conventions lens reads them.

#### Step 3. Plan coverage

Assign every changed non-generated file to the lenses that apply to it, so that each file is read in full by at least one lens and cross-file lenses receive the restatement and option inventories. Partition large branches across workers with overlap at the boundaries. Choose lenses from the branch's composition: a documentation-only branch does not need the concurrency part of the failure lens, and a script with no network calls does not need the collections lens. `./references/fan-out.md` holds the rules and the worker brief template.

#### Step 4. Run the lens passes

Each lens pass reads its assigned files whole and returns candidate findings in the ledger schema. Candidates may be hypotheses; each carries the check that would confirm or refute it.

Where the harness supports subagents, run the passes in parallel as fresh-context workers given only the map, the lens reference, and the file list. That keeps each pass independent and keeps cost down, because it avoids re-reading a long implementation conversation on every turn. Where it does not, run the passes one after another from the same brief. The skill says which mechanism it used.

| Lens                   | The question it answers                                                                                                                   |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Restatement drift      | Does every restatement in the map still agree with its source after this change, including generated copies and fixtures?                 |
| Promises               | Is every universal or quantified claim true on every path, including error paths and the empty and single-item cases?                     |
| Options and paths      | Does every option and mode reach every step, early exit, cleanup, and output that should honor it?                                        |
| Inputs and contract    | Is the supported input set stated, validated at one boundary, and consistent with what the code accepts? Which plausible input breaks it? |
| Failure and state      | Do early exits clean up? Are writes atomic, retries idempotent, locks and shared state safe, exit codes and messages accurate?            |
| Collections and limits | Are collections paginated, limits and truncation detected, ordering and first-match assumptions justified?                                |
| External facts         | Is every claim about a tool, API, format, or platform backed by running it or by a primary source?                                        |
| Tests and evidence     | Do tests reach the new branches, fail when the behavior breaks, and run isolated from the ambient environment?                            |
| Security               | Quoting and injection, path traversal and symlinks, secrets, permissions, and trust in external content                                   |
| Conventions            | Does the change follow the repository's own written rules and the idiom of the files it edits?                                            |
| Scope and surface      | Does the branch mix unrelated changes, duplicate a contract that should have one source, or add surface its value does not justify?       |

Each lens reference covers the question, search recipes that work in any language, the misses that recur, the false positives that recur, and the remedies that usually fit.

#### Step 5. Merge candidates

Union every pass's candidates with no vote threshold, since recall is the point of this stage. Merge duplicates by location and substance, and keep the lens names of every pass that raised a candidate.

#### Step 6. Verify

`./references/verification.md` defines what counts as verified: a reproduced failure, a command's actual output, a primary source for an external fact, or a traced path with file and line citations. Each candidate ends as **Verified**, **Refuted**, or **Unverifiable**. Refuted candidates are dropped with a one-line reason. Unverifiable ones go to the report's questions and are never fixed on speculation. Claims about external tools are verified on the platforms the project supports, because that is where false positives concentrate.

#### Step 7. Triage

`./references/triage.md` covers:

- **Severity**: critical (security, data loss, wrong result on a documented input), moderate (wrong behavior on a plausible input, documentation contradicting behavior, a new branch no test reaches), low (wording, an input outside the documented contract).
- **Class sweep**: name the defect pattern, search for it across every surface the map lists and then the whole repository, and attach every sibling to the finding. A finding is not triaged until its class has been searched.
- **Remedy order**: remove or narrow the promise, document the limit, fix, defer with a tracked issue, decline with a reason. A remedy that adds an option, input path, or restated fact updates the map, so the focused re-pass examines it.
- **User decisions**: remedies that split scope, change documented behavior, or remove a feature are collected and asked as one question after triage, not one at a time.

#### Step 8. Fix

Unless `--report-only` is set, fix each verified finding and its siblings together. Regenerate derived artifacts, run the project's own checks with exit statuses preserved, and commit in logical groups following the repository's commit conventions. Never push. `lint-and-fix` runs with `--no-push` through its parent continuation contract.

#### Step 9. Re-review the fixes

Run a focused pass over the fix commits (`--since` the pre-fix head) with the restatement drift, promises, options and paths, failure and state, and conventions lenses, then verify and triage as before. Repeat while a pass yields a verified finding of moderate or higher severity, up to `--max-passes`. Remaining low-severity findings are recorded as declined or deferred, not fixed in a further loop.

#### Step 10. Report

`./references/ledger.md` defines the ledger schema and the report:

- A summary table of findings by lens, severity, remedy, and status.
- What changed, commit by commit.
- What was deliberately left alone, each with its reason.
- Decisions needed, and questions from unverifiable candidates.
- Proposed reviewer notes: verified facts a reviewer is likely to misread, and inputs declared outside the contract. These are proposed for the repository's reviewer-instruction files if it has any, and written only on confirmation.
- Deferred items, ready for `create-deferred-issues` (#350) once it exists.
- Coverage: which lenses ran over which files, and by which mechanism. A clean result is reported as "no verified findings from these lenses", never as proof the branch is defect-free.
- A structured status line for callers: `Review-in-depth status: clean`, `fixed`, `decisions-needed`, or `failed`.

#### Error handling

- No commits on the branch: report and stop.
- No subagent support: run passes sequentially and say so.
- Project checks fail after a fix: revert that fix group, record the finding as unresolved, and continue with the rest.
- Verification cannot run a command (missing tool, platform mismatch): mark the candidate Unverifiable, never Verified.
- Very large branch: partition by the scope and surface lens's grouping and report the partition. Never fall back to skimming.

### `plugins/review-in-depth/README.md`

The opening paragraph matches the marketplace `description` verbatim. After it come Installation (a one-line pointer to the root install section), What It Does, the lens table, Usage with the options, how it relates to `review-branch`, `final-review-pass`, `plant-defects`, and `resolve-copilot-pr-feedback`, and See Also ending with the all-plugins link. No external tool is required; `gh` is optional and only phase 2 uses it.

### Phase 2: calibrate from review history (separate PR, #426)

External reviewers repeat themselves within a repository, so the lenses can be weighted by what this repository's reviewers have flagged before, without hard-coding any repository's specifics.

- A bundled `plugins/review-in-depth/scripts/review-history` (Bash, `gh`, `jq`) fetches review comments and review bodies from the last N merged PRs, including collapsed sections that list findings not posted inline, from every reviewer, human or automated. It emits normalized JSON lines of PR, reviewer, path, and body. With no `gh` or no GitHub remote it prints nothing and exits zero.
- `SKILL.md` gains `--calibrate [n]`, which runs the script before step 2 and clusters the output into the lens classes. The map records the recurring clusters as extra checks for their lens.
- Scrut coverage in `tests/scrut/review-history.md` against `tests/fixtures/gh-stub`, extending the stub only if its endpoint-to-file mapping cannot serve these calls. Register any binary path in the `Makefile` `SCRUT_ENV` block and the matching `scrut-env` list in `.github/workflows/ci.yml`. Apply the `write-bash-scripts` and `write-scrut-tests` skills.
- `${CLAUDE_PLUGIN_ROOT}/scripts/review-history` referenced per rule 18, with the documented fallback for harnesses that do not substitute the placeholder.

### Follow-ups, not part of this plan

Tracked as separate issues:

- #427: `final-review-pass` (#371) invokes `review-in-depth` as its first step.
- #428: `resolve-copilot-pr-feedback` and `monitor-pr` run `review-in-depth --since` over a fix batch before pushing (extends #406).
- #429: one shared path for writing reviewer notes, feeding the deferral instruction flow (#407) and the location fix (#421).
- #430: `pr` gains an opt-in flag that runs the review before opening the PR.

### Repository bookkeeping (both phases)

1. Set the plugin manifest version to `1.0.0` (phase 2 bumps minor); the manifest is the only SemVer authority.
1. Register the plugin in `.claude-plugin/marketplace.json`, alphabetically, category `code-review`.
1. Add a row to the Code Review table in the root `README.md` using the marketplace `description` verbatim, with trigger `/review-in-depth`.
1. Regenerate `dist/codex/` and `dist/opencode/` with `bin/build-codex-marketplace` and `bin/build-opencode-mirror`.
1. Keep every `./references/...` path resolvable, and declare any illustrative path with a `validate-plugins: ignore` comment.
1. Use the `check-versions` skill before opening each PR.

## Verification

### Mechanical

- `make test-all` passes, including `bin/validate-plugins` rules 17 (description length), 18 (script references, phase 2), and 19 (cross-references).
- The generated trees match source.

### Behavioral: does it actually find things

This is the real uncertainty, and CI cannot answer it. Record every result in this plan's done copy.

1. **Planted-defect control.** In a scratch repository outside this one, make a small multi-file change in two languages and plant one defect per lens: a stale restatement, a false universal promise, an option skipped by an early exit, an unvalidated plausible input, a cleanup skipped on an error path, an unpaginated read, a wrong claim about a tool flag, a test that cannot reach its branch, an unquoted interpolation, a violated written convention, and an unrelated change riding along. Run `--report-only`. Every lens must report and verify its plant. Record a plant table of lens, plant, reported, and verified, following `plant-defects`.
1. **Backtest on history.** Pick at least five PRs with long external-review loops from at least two repositories. Check out the first commit the external reviewer saw and run `--report-only`. Compare against the reviewer's later findings on code that already existed at that commit. Measure recall, precision after verification, verified findings the reviewer never raised, and the run's token cost. Initial bar: recall of 60% or more, precision of 80% or more. Revisit the bar after the first backtest rather than tuning to it.
1. **Forward trial.** Run `review-in-depth` before `/pr` on the next several branches of real work. Record external review rounds and findings per round against the baseline table in Context.
1. **Dogfood.** Run `review-in-depth` on its own branch before opening each phase's PR.

## Risks

- **Cost.** Several passes cost more agent tokens than one. The controls are fresh-context workers, lens selection by branch composition, and re-passes scoped to the fix diff. The backtest measures cost against the external rounds a run removes.
- **Portability.** No skill in this repository fans out to subagents today. Codex CLI and OpenCode get the sequential path, and the mirrored text must read correctly for both.
- **Over-fixing.** Aggressive generation invites growing surface in response to unlikely inputs. The verification gate, the remedy order, and the map update on every remedy are the controls; the forward trial watches for branches growing during review.
- **A clean local result is a sample too.** The report states coverage instead of claiming the branch is clean.
- **Overlap with #371.** Defect classes stay here; leftovers, commit hygiene, and plan state stay in `final-review-pass`.

## Out of scope

- Changing `review-branch`, which stays a report.
- Wiring the skill into `pr`, `monitor-pr`, `resolve-copilot-pr-feedback`, or `final-review-pass` (follow-ups above).
- Choosing or configuring an external reviewer, or its effort level.
- Any repository-specific lens content. Repository specifics arrive only through the map, the conventions lens, and phase 2 calibration.

## Commits

Phase 1:

1. `feat: add the review-in-depth plugin skeleton and catalog entry`
1. `feat: add the review-in-depth workflow, map, and fan-out references`
1. `feat: add the review-in-depth lens references`
1. `feat: add verification, triage, and ledger references`
1. `docs: add the review-in-depth README and root catalog row`
1. `chore: regenerate the Codex and OpenCode mirrors`

Phase 2:

1. `feat: add the review-history script with scrut coverage`
1. `feat: calibrate review-in-depth lenses from review history`
1. `chore: bump review-in-depth and regenerate the mirrors`
