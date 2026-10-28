# Git and review chain assessment

## Build authorization and configuration

TOOLING relayed the Tier B/build go-ahead from the Inbox thread "Codex compatibility milestone 2 build", given 2026-10-27 at 5:33 PM ET. Scope includes local-only measurements, implementation including the signing fix, local review, checks and ready PR publication. No GitHub effects are authorized for evaluation fixtures.

Baseline sources were frozen from `86b9a77a` before plugin changes. Runs used Codex CLI `0.164.0`, model `gpt-6.1-sol`, low effort and the default context window. The first host probe used global configuration. Case runs used per-command overrides disabling the advertised global skills and configured plugins/MCP servers, then exposed copied source packages through local `.agents/skills` symlinks. No credential files were copied or inspected. Authentication remained with the existing Codex login. Local fixtures used throwaway SSH signing keys and bare Git remotes. No permission or network override was used in the completed runs.

## Baseline stop

Seven model invocations completed: one host probe and six baseline cases. Every invocation exited zero with a nonempty final reply. This is execution evidence, not a passing behavioral result.

| Case                | Observation                                                                                   | Assessment                         |
| ------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------- |
| Host probe 1        | Advertised names, aliased skill roots and tool metadata captured; local exec/resume help read | Observed, resume itself not tested |
| activation-commit   | Loaded local commit/Git skills and made a signed staged-only commit                           | Pass                               |
| activation-negative | Explained rebase; HEAD and staged changes preserved                                           | Pass                               |
| activation-monitor  | Login shell resolved real `gh`; guard stopped before invoking it                              | Fixture blocked                    |
| partial-pr          | Same executable mismatch, no GitHub call or publication                                       | Fixture blocked                    |
| partial-resolver    | Same executable mismatch, no GitHub call or edit                                              | Fixture blocked                    |
| partial-monitor     | Same executable mismatch, no GitHub call or edit                                              | Fixture blocked                    |

The driver verified the stub with non-login Bash, but model-generated login shells reset `PATH`. Four cases therefore did not exercise their intended boundaries. No real `gh` operation ran. The remaining three host probes, six baseline cases and all twelve final cases have not started. No plugin implementation or review loop has started.

`before-evidence.json` preserves final replies, command/exit excerpts and usage. Home and scratch prefixes are replaced with placeholders. Full event captures and isolated package snapshots remain in the recorded scratch directory in the worker's mailbox report; those may contain host-specific paths and are not committed wholesale.

Stop for TOOLING's decision: correct stub resolution in the actual model shell, verify that shell preflight before further calls, and replace the four invalid cases. Completing the original coverage would then require 32 total invocations rather than 28. Alternatively, retain the cap and explicitly reduce coverage. No additional model calls were launched after discovering the mismatch.

## Replacement authorization and comparison

TOOLING relayed authorization from the Inbox thread "Codex compatibility milestone 2 measurement", given 2026-10-27 at 6:26 PM ET: four replacement invocations, 32 total. The driver now supplies fixture-only zsh startup files through per-command `ZDOTDIR`, preserving stub PATH after login initialization. Both `/bin/zsh -c` and `/bin/zsh -lc` resolved the intended stub in a non-model preflight before the four replacement runs. No user shell configuration changed. Fixture log/auth variables are passed explicitly to the model shell; credentials remain untouched.

All **32 invocations completed**, with zero exits and nonempty replies: 4 host probes, 12 baseline cases, 4 invalid original cases and their replacements counted separately, and 12 post-adoption cases. More precisely, the original allocation is 4 probes plus 24 before/after cases (28), with 4 discarded fixture-blocked attempts added (32). No further evaluation calls remain authorized. Review and trimming calls belong to the separately authorized local review order, not these measurements.

| Case                    | Baseline after fixture correction                    | Post-adoption observation                                         |
| ----------------------- | ---------------------------------------------------- | ----------------------------------------------------------------- |
| activation-commit       | Signed staged commit                                 | Signed staged commit; structured success                          |
| activation-monitor      | Bounded checkpoint; absent review remained missing   | Bounded checkpoint; review axis explicitly paused by policy       |
| activation-negative     | Explanation only                                     | Explanation only                                                  |
| partial-pr              | Missing lint skill reported                          | Explicit unavailable result before publication                    |
| partial-resolver        | Missing fixing skills reported; other fixture blocks | Same boundary observed; overall workflow remains fixture-limited  |
| partial-monitor         | Watched without reporting missing fixing skills      | Explicit unavailable result before repair/scheduling              |
| continuation-lint       | Signed commit and parent output, no push             | Structured lint success, signed commit and parent output, no push |
| continuation-merge      | Returned the unanswered choice                       | Structured needs-decision; staged and unstaged changes preserved  |
| restriction-read-only   | Preserved changes without committing                 | Exact blocked signing command reported; changes preserved         |
| restriction-unavailable | Failed required check reported                       | Structured lint failure; no commit or push                        |
| helper-cache            | Selected current helper; authentication failed       | Physical loaded-package helper selected; authentication stop      |
| review-result-failure   | Rejected failed/empty result                         | Rejected failed/empty result                                      |

Eleven final cases meet their bounded criteria. The resolver's missing-dependency boundary was observed, but its full workflow is not verified: the stub's `headRefOid` is deliberately synthetic rather than a full SHA, its final-summary write is refused, and the checkout contains staged fixture data. These conditions are preserved in both arms, not silently corrected between them. No complete feedback-resolution or live PR claim follows. Helper-cache passes its selection criterion despite the intentional authentication failure; it does not prove feedback processing.

The host probes observed signed commits and a local bare-remote push under the configured full-access policy, TMPDIR writes, literal inline options and root-alias expansion, and a completed foreground wait. Question/scheduler availability came from actual session metadata; those mechanisms and real resume behavior were not exercised. A short completed wait does not establish a maximum command timeout. Read-only behavior was measured only in the explicit restriction case. Network access and interactive approvals were not tested, since fixture runs prohibit external effects. Claude interactive parity, installed-marketplace lifecycle, live GitHub and Linux remain unverified.

`comparison-evidence.json` contains 31 records plus the original host probe in `before-evidence.json`. Relevant final replies, command exits, usage and tree/HEAD states are preserved; raw captures and source packages remain outside the repository. Baseline packages were frozen from `86b9a77a`; final packages include the canonical adapters in this branch. No model was asked to infer a pass from an empty reply.

The post-adoption packages match the adapter source committed at `37048997`. Later structural review fixes add explicit paused-policy termination and nested deferred-proposal handoff, correct authoring guidance and strengthen deterministic contract validation. Those fixes are reviewed and checked separately; they have **not** been remeasured by model cases because the 32-call cap is exhausted. The table describes the measured revision, not a new execution of those later paths.

The subsequent 7:00 PM ET structural decision replaces the competing pause/no-fix branches with one executable restriction filter in `merge-flow dispatch`. Its failed-check, DIRTY/BEHIND and pause boundaries were tested and planted without model calls. Initial/resumed model behavior and real scheduler cancellation remain unmeasured; the record does not claim an additional final-model comparison of this revision.

The follow-on structural implementation prepares one policy before axis reads, uses it for triage and every reader/action gate, and rejects malformed optional restrictions before defaulting. Its initial/resumed paused-triage cases and CLI guards are deterministic tests; they do not consume or extend the 32 model measurements. The post-adoption model table remains evidence for `37048997`, with these later changes verified separately by tests and review.

## Deterministic checks and plants

The adapter suite passed seven initial cases, then nine cases after adding driver capture checks. Disabling the contract-check call produced two failing cases; routing the loaded monitor helper to the old cache produced one failing case. Both mutations were restored and the suite passed again. Driver tests use a committed Codex stub, verify its resolved identity before running, and cover successful and missing replies without model calls. Login-shell behavior is a macOS fixture prerequisite; Linux without zsh explicitly skips those driver cases while retaining portable helper/checker coverage.

## Checks at the original stop

Pinned Yarn dependencies installed with `yarn install --immutable`. Node syntax and shellcheck checks passed for the draft driver and stub. Full deterministic coverage, planted-defect checks, review rounds, semgrep, full suite and final version validation remain pending. No clean review status or milestone acceptance is claimed.
