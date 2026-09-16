# Branch Review: feature/343-write-realtime-audio-code

- Base: `main` (merge base: `340f3192`)
- Reviewed through: `c6e10bdf`
- Commits: 7 at the reviewed revision
- Files changed: 35 (28 added, 7 modified, 0 deleted, 0 renamed) at the reviewed revision
- Repository: `cboone/agent-harness-plugins`, not archived, with no fork or upstream remote identified

> Historical snapshot: this review assesses `c6e10bdf` and its original merge base. The resolution-status entries record later work, and the detailed findings below are superseded where those entries say they are resolved. Do not use this document as a description of the current branch head.

## Summary

At the reviewed revision, the branch adds a real-time audio writing and review skill, covering callback contracts, communication, memory ordering, verification, compatibility, event timing, and host-independent cores. It registers the plugin across the catalogs and mirrors, updates the Plant Defects companion documentation, and adds 35 evaluation cases. The integration passes all repository checks, but the required worked examples and behavioral evidence were incomplete at that revision.

## Resolution Status

- [x] R1: Recorded 12 focused evaluation summaries, corrected the detected event-fixture expectation, and moved the plan back to `todo/` while the remaining cases and retained evaluator evidence are unverified.
- [x] R2: Replaced conclusion-led input prose with opaque raw artifacts, separated control variants, added wrapper scope, and retained a valid comparison case.
- [x] R3: Added concrete worked examples to every comprehensive reference and a rule-to-evidence map for the safety-critical guidance.

## Code Quality Assessment

**Verdict: needs more work before merging.** The three findings concern the skill's instructional completeness and acceptance evidence. This branch adds prose and evaluation data, with no executable audio implementation to assess for runtime regressions.

### R1: Record behavioral evidence before declaring the plan complete

**Priority: P2.** Location: [assessment.md](../../tests/data/write-realtime-audio-code-evals/assessment.md), lines 5 and 9; [completion gates](../plans/todo/2026-09-14-new-skill-write-realtime-audio-code.md#implementation-sequence-and-completion-gates), lines 344 and 345.

The assessment explicitly records no evaluator runs and marks `RTAC-001` through `RTAC-030`, including generated-layout discovery and navigation, unverified. Nevertheless, commit `672e91de` moved the plan to `done/`. Gates 7 and 8 require observed behavioral outcomes and completion of the required checks before that move. The passing repository checks establish packaging and formatting, but do not establish that an agent selects the right references, produces the expected recommendation, or respects a read-only request.

Run the supported recommendation and navigation evaluations in fresh contexts and retain the evaluated revision, harness/model, selected references, outputs, action traces, and assessments. Where a particular tool or host is unavailable, record that limitation for the affected case, as the plan permits. Keep the plan pending until the applicable gates are satisfied or its completion criteria are explicitly revised. A blanket pending entry provides no evidence that the available evaluations were attempted.

### R2: Supply raw artifacts and independent evaluation variants

**Priority: P2.** Location: [inputs.json](../../tests/data/write-realtime-audio-code-evals/inputs.json), especially lines 28 through 40, 53 through 60, and 113 through 120; [evaluation procedure](../../tests/data/write-realtime-audio-code-evals/README.md), lines 7 and 14.

The procedure promises minimal raw artifacts without suspected conclusions, but every `artifact` is a prose synopsis. For example, `RTAC-011` tells the evaluator that callbacks exceed the interval without supplying timing records, and `RTAC-012` states that a truncated preset publishes partially initialized state without supplying a parser or state fixture. These inputs can test agreement with a described problem, but cannot establish the planned ability to discover it from evidence or produce reproducible traces.

Independent cases are also combined: `RTAC-006` combines missing subject instrumentation with a missed control; `RTAC-008` combines loading context with an unmarked worker; `RTAC-023` combines VST3 curves with AUv3 ramps. The three runtime-control outcomes required by the plan are not preserved as three standalone variants; `RTAC-007` covers only an unrelated loading failure. `RTAC-019` also omits the target wrapper revision needed to apply its version-specific expectation.

Add minimal source, build configuration, logs, serialized inputs, or event/timing records appropriate to each case. Keep conclusions exclusively in the assessment criteria, supply version scope where it matters, and split independent failure modes and control outcomes into stable variants. Retain valid comparison cases so the evaluation can distinguish appropriate acceptance from blanket rejection.

### R3: Complete the required worked examples

**Priority: P2.** Location: [events-and-timing.md](../../plugins/write-realtime-audio-code/skills/write-realtime-audio-code/references/comprehensive/events-and-timing.md), lines 31 through 33; [verifying-concurrency.md](../../plugins/write-realtime-audio-code/skills/write-realtime-audio-code/references/comprehensive/verifying-concurrency.md), lines 44 through 46; [required worked examples](../plans/todo/2026-09-14-new-skill-write-realtime-audio-code.md#required-worked-examples), lines 349 through 359.

Several sections give assignments to the downstream reader where the plan requires completed examples. The entire deterministic-trace section says to build traces, without providing events, offsets, queue capacity, accepted/rejected outputs, or resulting states. The verification section is a walkthrough template, without an instantiated publication control, prohibited-operation control, malformed-input case, or diagnostic record. The memory-ordering examples likewise leave index encoding, wraparound, and the selected language model to the reader; the core-boundary table describes controls without showing an enforcement mechanism that rejects them.

The AUv2 permutation and ownership-state table are useful concrete starting points. Complete the seven-reference example requirements with explicit assumptions, state transitions, work/capacity bounds, failure outcomes, and claim-specific checks. Provide the event and automation traces and actual control definitions. Label pseudocode and source-derived results accurately, and claim execution only when an observed result is retained. The plan allows small examples and conditional tool support; it does not require executable helpers in the published plugin.

### Strengths

- The entry point selects references by task and explicitly distinguishes review, planning, and implementation authority.
- The guide addresses callback callees, lifecycle entries, workers, failed queue submissions, final destruction, and storage reuse. These are more useful review boundaries than a list of prohibited functions alone.
- It separates race evidence, instrument sensitivity, protocol correctness, and deadline measurements, and preserves the distinction between recorded project experiments and general requirements.
- The standalone positive-control explanation and local reference links avoid a hard dependency on the companion plugin.
- Plugin metadata, catalog descriptions, companion patch version, and generated mirrors agree. No new dependency, workflow, executable helper, or Scrut registration is needed for this prose-only plugin.

### Completeness and source fidelity

No TODO, FIXME, or stub-code markers were found in the new plugin. The visible unfinished work is the pending assessment and the example templates described above.

The plan also calls for a rule-to-evidence ledger and supporting source sections beside safety-critical rules. The branch retains a broad evidence table in the plan and bibliographies in the references, but no explicit mapping from published rules to precise source sections and worked cases. Several planned details were condensed away, including transport validity flags and in-block transport events, MIDI-derived parameter recording flags, and distinctions between parameter/port rescan flags. Include these in the remaining fidelity pass, or document a deliberate scope decision; the branch records no such decision.

## Plan Compliance

Plan: [2026-09-14-new-skill-write-realtime-audio-code.md](../plans/todo/2026-09-14-new-skill-write-realtime-audio-code.md).

**Verdict: partial compliance.** Three of the eight top-level completion gates are done (37.5%); five are partially done. This counts complete gates, not the proportion of prose written. Every gate has some implementation, but behavioral execution is an unstarted subtask in the committed assessment.

### Completion gates

| Gate | Status         | Evidence and remaining work                                                                                                                                                    |
| ---- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1    | Done           | Five plan commits establish the scope, source revisions, technical corrections, acceptance scenarios, and completion requirements.                                             |
| 2    | Partially done | All seven references exist and cover their principal subjects. Required worked examples and the precise rule-to-evidence mapping remain incomplete; see R3.                    |
| 3    | Partially done | Thirty stable IDs, separate criteria, a procedure, and a living assessment exist. Raw artifacts, independent variants, and some required control outcomes are missing; see R2. |
| 4    | Partially done | Entry point, ten checklist groups, README, local routing, and authority boundaries are present. Installed standalone and generated-harness behavior remains unverified.        |
| 5    | Done           | The new plugin, manifest, catalog entry, README row, catalog state, and generated outputs land together in `672e91de`.                                                         |
| 6    | Done           | Companion status, related link, patch version, catalog state, and generated outputs land together in `c6e10bdf`.                                                               |
| 7    | Partially done | Repository lint, validation, mirror freshness, and all 402 Scrut cases pass. No behavioral run, output assessment, or behavior-driven revision is recorded; see R1.            |
| 8    | Partially done | The assessment honestly records unverified scope, but has no execution evidence and the plan was archived before the required gates were complete; see R1.                     |

### Reference and example coverage

- **Callback rules:** budget, buffer formats and aliases, output completion, lifecycle, notification costs, teardown, and numerical hazards are covered. The setup/process/retire table remains generic, without a selected buffer configuration and its actual outcomes.
- **Ownership:** the SPSC table identifies both synchronization directions and excludes extra producers. Full-capacity, submission/destruction, and retirement policies remain instructions to select a policy rather than an instantiated example.
- **Memory semantics:** vocabulary, relaxed-value uses, publication/reuse edges, object validity, and hardware distinctions are covered. The worked protocol lacks a chosen language edition, state encoding, wraparound argument, and concrete lifetime assumptions.
- **Verification:** the claim/evidence matrix, three control classifications, sanitizer/model limits, loaded-plugin/worker scope, and timing records are covered. Concrete control walkthroughs and recorded outcomes are missing.
- **Compatibility:** identity, state schema, failed-load preservation, and delayed reactivation are covered. The AUv2 permutation is explicit; transactional parser fixtures and a pending-to-active host notification trace are missing.
- **Events:** time domains, targeting, pending obligations, VST3 interpolation, AUv3 ramps, modulation, and smoothing domains are covered. The promised event and automation traces are absent.
- **Core boundaries:** layer responsibilities, dependency versus signature checks, arithmetic semantics, and adapter validation are covered. The required failing dependency and signature examples are absent.

### Deviations and fidelity concerns

- Replacing raw evaluation inputs with problem synopses and combining independent variants weakens the evidence required by the plan. This is an undocumented approach deviation.
- Replacing worked examples with templates is an undocumented reduction in the planned instructional depth.
- Moving the plan to `done/` before behavioral checks is a completion-order violation with a practical effect: the repository presents pending acceptance work as archived work.
- The companion documentation change, evaluation directory, and mirror regeneration are all planned scope. No unrelated feature expansion was found.
- Omitting a new Scrut suite for the prose itself is consistent with the plan. Existing Scrut checks validate repository tooling; they cannot substitute for the separate behavioral evaluations.

## Changes by Area

- **Audio guidance:** `plugins/write-realtime-audio-code/` adds the manifest, README, entry point, essential checklist, and seven comprehensive references.
- **Evaluation assets:** `tests/data/write-realtime-audio-code-evals/` adds requests, criteria, execution instructions, and the pending assessment.
- **Catalog and distribution:** `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `README.md`, `dist/codex/`, and the OpenCode skill symlink register and distribute the new plugin.
- **Companion and planning:** the Plant Defects README and manifest, their Codex copies, and the dated plan record the relationship and implementation scope.

## File Inventory

### Added files: 28

This inventory is the net diff from `340f3192` to `c6e10bdf`. Later additions and moves, including the rule-to-evidence map, `artifacts.json`, and this saved review, are outside that range.

The following 11 relative paths were added under both `plugins/write-realtime-audio-code/` and `dist/codex/plugins/write-realtime-audio-code/`, accounting for 22 files:

```text
.claude-plugin/plugin.json
README.md
skills/write-realtime-audio-code/SKILL.md
skills/write-realtime-audio-code/references/essential/checklist.md
skills/write-realtime-audio-code/references/comprehensive/audio-thread-rules.md
skills/write-realtime-audio-code/references/comprehensive/events-and-timing.md
skills/write-realtime-audio-code/references/comprehensive/lock-free-buffers.md
skills/write-realtime-audio-code/references/comprehensive/memory-ordering.md
skills/write-realtime-audio-code/references/comprehensive/parameters-and-state.md
skills/write-realtime-audio-code/references/comprehensive/the-pure-core-seam.md
skills/write-realtime-audio-code/references/comprehensive/verifying-concurrency.md
```

The remaining six additions are:

```text
dist/opencode/skills/write-realtime-audio-code
docs/plans/done/2026-09-14-new-skill-write-realtime-audio-code.md
tests/data/write-realtime-audio-code-evals/README.md
tests/data/write-realtime-audio-code-evals/assessment-criteria.md
tests/data/write-realtime-audio-code-evals/assessment.md
tests/data/write-realtime-audio-code-evals/inputs.json
```

### Modified files: 7

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
README.md
plugins/plant-defects/.claude-plugin/plugin.json
plugins/plant-defects/README.md
dist/codex/plugins/plant-defects/.claude-plugin/plugin.json
dist/codex/plugins/plant-defects/README.md
```

No files are deleted or renamed in the net diff. The plan was created and later moved within the branch, so it counts as an addition relative to the merge base. This newly saved review is outside the reviewed commit range.

## Notable Changes

- `write-realtime-audio-code` starts at `1.0.0`; `plant-defects` changes from `1.0.0` to `1.0.1`.
- At the reviewed revision, catalog state changes from `catalog-M70-m103-p156-n57` to `catalog-M71-m103-p157-n58` and passes the catalog validation rule.
- The Codex builder substitutes the shorter catalog description into discovery frontmatter; the skill body is preserved. The OpenCode entry is the expected symlink to the canonical skill.

## Validation and Review Limits

- `make test-all` completed successfully: Markdown and formatting checks, ShellCheck, shfmt, actionlint, JSON/plugin validation, and 402 Scrut cases across eight documents, with no failures or skips.
- Plugin validation includes catalog agreement, description limits, cross-references, and freshness of both generated mirrors. The generated metadata and description rewrite were also inspected directly.
- `git diff --check 340f3192..HEAD` passed. The working tree was clean before saving this review.
- Source spot checks confirmed the pinned [CLAP latency rule](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/ext/latency.h), [CLAP event semantics](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/events.h), and the AUv2 ordering discrepancy between the [wrapper header](https://github.com/free-audio/clap-wrapper/blob/1cca996e96f29ab2be7ae9f8cfe532bbc92e1dd6/include/clapwrapper/auv2.h) and [implementation](https://github.com/free-audio/clap-wrapper/blob/1cca996e96f29ab2be7ae9f8cfe532bbc92e1dd6/src/wrapasauv2.cpp#L421).
- The VST3 curve description matches [Steinberg's parameter-queue documentation](https://steinbergmedia.github.io/vst3_doc/vstinterfaces/classSteinberg_1_1Vst_1_1IParamValueQueue.html). Notification and instrumentation caveats match the checked [JUCE AsyncUpdater](https://docs.juce.com/master/classjuce_1_1AsyncUpdater.html), [RealtimeSanitizer](https://clang.llvm.org/docs/RealtimeSanitizer.html), and [Function Effect Analysis](https://clang.llvm.org/docs/FunctionEffectAnalysis.html) documentation.
- Canonical new content and the plan were read; generated duplicates were checked through the builders' freshness validation and direct inspection of their transformations. These checks did not execute an audio host, sanitizer control, model checker, or fresh-context skill evaluation, and do not change the behavioral cases' unverified status.

The review-branch skill supplied the review and completion-gate assessment workflow. The write-markdown skill supplied the saved document's formatting and targeted lint-fix checks.

To address the findings, run:

```text
/address-review docs/reviews/2026-09-15-feature-343-write-realtime-audio-code.md
```
