# Submodule snapshot ledger

## Scope and authority

Issue: [Submodule snapshot coverage](https://github.com/cboone/agent-harness-plugins/issues/523).
Go-ahead: Inbox, Tooling next batch, pick 4, 2026-10-28 9:16 AM ET.
Build through a ready PR; TOOLING merges. Base: actual merge base with `origin/main`.

## Reproduction and design

Current main reproduced identical snapshots across two dirty submodule edits when a parent file also differed. The unstaged bucket listed the submodule. Without the parent edit, the existing tree consistency guard failed instead.

Both canonical review-scope copies now collect initialized child scopes recursively and extend the parent working-tree buckets. Uninitialized empty checkouts expose only the gitlink; populated checkouts without Git metadata fail. Child failures retain stderr. Git tree objects remain local to each repository; codex-aspects compares recursive trees in those repositories. No other canonical snapshot helper uses the temporary-index pattern (source search).

## Validation

Corepack immutable dependency installation passed. Initial ten recursive Scrut cases passed; existing scope suite passed all 48 cases after preserving the race stub's argument positions. ShellCheck findings in new fixture code corrected. Boundary plants removed recursive inputs for edit, staged-only, untracked, moved HEAD and nested cases; each intended fixture assertion failed. Separate plants for initialization, nested tree comparisons, nested prompt commands and stderr propagation also failed their checks. All plants restored; remaining checks pending.

## Plant table

| Boundary                     | Plant                            | Expected check     | Result |
| ---------------------------- | -------------------------------- | ------------------ | ------ |
| Working-tree content         | Omit child records               | Edit case          | Caught |
| Child index                  | Omit child index from snapshot   | Staged-only case   | Caught |
| Untracked content            | Omit child untracked files       | Untracked case     | Caught |
| HEAD                         | Omit recursive child HEAD record | HEAD case          | Caught |
| Recursion                    | Omit nested records              | Nested case        | Caught |
| Uninitialized checkout       | Report initialized               | Uninitialized case | Caught |
| Recursive mutation reporting | Skip child tree comparisons      | Mutation reporting | Caught |
| Tool failures                | Discard child stderr             | Failure case       | Caught |

## Historical review evidence, not completed rounds

Attempted structural Nit round: standalone Codex runs (`gpt-6.1-sol`, high, window 872000, read-only sandbox) failed before reading because the external capture directory was not trusted. No override or silent retry used. Native Codex fallback (`gpt-6.1-sol`, high, fresh contexts) reviewed production, tests and docs separately, with simplify in parallel. Read-only protection was instructional, not sandbox-enforced. All assigned groups reported complete, but their instruction-only access did not satisfy the required read-only sandbox. These subagent reports are evidence only and do not count as a structural round.

| Reviewer label                                                                          | Our severity                                           | Take or record                                                                    | Review again                 |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------ | --------------------------------------------------------------------------------- | ---------------------------- |
| Important: Parallel paths, committed gitlink changes honor ignore settings              | Important, a real committed change can report empty    | Take: explicit override and committed regression                                  | Yes, scope behavior changes  |
| Important: Sibling input forms, staged-deleted gitlinks lose recursive content coverage | Important, consecutive internal edits reuse a snapshot | Take: union of real and disk index gitlinks, deduplicated                         | Yes, digest coverage changes |
| Important: Parallel paths, edit-path instructions omit recursive trees                  | Important, edit reports omit reviewer changes          | Take: recursive comparisons and initialization transitions in reviewers reference | No, prose only               |
| Nit: Tests that cannot fail, parent-only disk equality                                  | Nit, child disk equality is unasserted                 | Take: compare child tree too                                                      | No, tests only               |
| Nit: simplify, validate parent disk before bucket extension                             | Nit, unnecessary list copy                             | Take: move unchanged consistency check before extension                           | No, behavior preserved       |

The production addendum belongs to the same evidence collection, before fixes. All evidence-driven takes applied. Added regressions for committed ignore settings, retained staged-deleted checkouts and populated uninitialized checkouts. The first disk-enumeration plant was syntactically invalid and discarded; the corrected valid plant reached the intended false assertion. Omitted committed override also reached false. A child disk-hashing plant failed the strengthened staged-only assertion; weakening only that assertion made the defect pass, identifying its necessary coverage. No completed sandboxed structural round is credited for these subagent results.
Focused Codex review: pending.
Comment and prose trims: pending.
Semgrep baseline scan: pending.
Final lint, full tests, version audit and signed exact-tree tidy: pending.

## Stop: recurring ignore-settings coverage defect

Structural Important round, 2026-10-28 4:38 PM ET: report-only simplify completed in a fresh standalone Codex run (`gpt-6.1-sol`, high, window 872000, read-only sandbox), exit 0 and nonempty valid JSON. The raw report is `2026-10-28-submodule-snapshot-important-simplify.json` beside this ledger. The trusted existing Git checkout was used as the review working directory; no override flag was added.

- **Reviewer label:** Important, “Keep deleted submodules visible in rendered review diffs”.
- **Our severity:** Important. When the last submodule and checkout are deleted, the current recursive records are empty. `render_scope` consequently omits `--ignore-submodules=none`, so `diff.ignoreSubmodules=all` hides the committed deletion from the command handed to the reviewer even though the scope lists it.
- **Take or record:** Record unfixed at the required recurrence gate. This is another ignore-settings coverage defect after the first round fixed committed-bucket collection.
- **Review again:** Pending TOOLING's structural design decision and restart go-ahead. Proposed direction: make rendered diff overrides independent of current submodule presence, with a deleted-last-submodule fixture and a plant that removes the override.

End state: **stopped: recurring defect**. No push or PR. TOOLING decides the structural fix; the worker has not applied it.

All 14 submodule Scrut cases passed after the first-round fixes. The original 48-case scope suite passed before those fixes; the final full suite remains pending. New plants caught omitted committed overrides, omitted disk-index enumeration, child index content substituted for disk content, and dropped populated-checkout refusal. The invalid first disk-enumeration plant was discarded and replaced with a syntactically valid plant that reached the intended assertion. The staged-only assertion's negative control showed that weakening child-tree equality admits the planted defect.

The unfinished Important anti-pattern reviewer was terminated at the recurrence stop by its recorded PID 20082. The runner (execution session 30116) completed with `anti 143` and `simplify 0`; neither PID 20082 nor its recorded children 20166, 20167, 20168, 20169, 20170 and 30522 remained. The anti-pattern output is incomplete and is not clean. Logs and statuses remain under `/tmp/523-reviews/important/`. No background command remains. Focused review prompts were prepared under `/tmp/523-reviews/focused/`, but no focused reviewer was launched. Trims, Semgrep baseline scan, final lint-and-fix, make test-all, version audit, exact-tree tidy, push and PR remain pending.

## TOOLING correction: sandboxed structural rerun

TOOLING directed the worker to reject instruction-only subagent reviews as rounds and rerun structural review with Codex's built-in read-only sandbox. The earlier subagent findings above are evidence only. The later standalone simplify run was sandboxed, but its paired anti-pattern review was cancelled, so it was not a completed structural round either. Earlier round and recurrence labels remain historical evidence; the unfinished code finding remains unfixed pending TOOLING's decision.

The original failed command was the handwritten `/tmp/523-reviews/run-structural`, not an installed helper invocation. It used `codex exec --cd /tmp/523-reviews --sandbox read-only` with no trust-check override and failed with `Not inside a trusted directory and --skip-git-repo-check was not specified.` Both processes exited 1 before reviewing.

Verified installed sources: `review-anti-patterns` 1.1.4, `skills/review-anti-patterns/references/codex-exec.md`, prescribes `--cd` at the Git root; `review-pr-with-codex` 2.1.4, `scripts/codex-aspects`, runs scratch workdirs with `--skip-git-repo-check`. The worker incorrectly substituted the capture directory for the anti-patterns reference's Git working directory. No real trust configuration was read or changed.

The corrected paired Nit rerun uses the installed skill/aspect instructions, the existing Git checkout at `/Users/ctm/Development/agent-harness-plugins` as working directory, and external capture files. Both runs explicitly use `gpt-6.1-sol`, high effort, window 872000, `--sandbox read-only`, approval `never`, disabled web search and closed stdin. No trust-check or sandbox override is used. Simplify is report-only; no editing simplify helper is invoked. Production code stayed unchanged during this correction. Results are recorded below.

## Completed sandboxed structural Nit round

Both standalone reviewers completed with exit 0. Anti-patterns 1.1.4 returned a nonempty single JSON value passing its installed `result-check.jq`, with `status: success`, `complete: true` and no unread paths. Report-only simplify returned a nonempty JSON reply passing the installed 2.1.4 `codex-aspects validate` check, including aspect identity and the exact captured snapshot. Before/after scope comparison reported `scope_changed: false`, `changed: []` and `outside_scope: []`: no lasting changes found. The Git working directory resolved the startup problem without any trust or sandbox override. No subagents ran for this corrected round.

Raw replies are committed beside this ledger as `2026-10-28-submodule-snapshot-sandboxed-anti.json` and `2026-10-28-submodule-snapshot-sandboxed-simplify.json`. The runner recorded `anti 0` and `simplify 0`; execution session 85636 completed. PIDs 63807 and 63808 are absent. No review command remains running.

| Reviewer label                                                                    | Our severity                                                                                                                          | Take or record                                                                                                            | Review again                     |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| Important: Parallel paths, deleted submodules lose rendered diff ignore override  | Important, listed committed/staged deletions can be hidden from the reviewer                                                          | Record unfixed at TOOLING's existing design gate; require rendering overrides independently of current submodule presence | Yes, behavior changes when fixed |
| Important: Parallel paths, retained checkout scopes fail consumer path validation | Important, supported retained/embedded checkout scopes cannot reach prompt, changes or gate because module/ contains a trailing slash | Record unfixed for the same collection-to-consumer design decision; require end-to-end retained/embedded scope tests      | Yes, behavior changes when fixed |
| Nit: Docs drift, edit-round prose says staging does not move snapshots            | Nit, pre-existing paragraph contradicts semantic-index snapshot behavior                                                              | Take when the fix work resumes; prose correction is local                                                                 | No, prose only                   |
| Suggestion: write-bash-scripts, consolidate identical scenario branches           | Nit, duplicate fixture mutations                                                                                                      | Take when the fix work resumes; combine deleted/edit and prompt/changes arms                                              | No, behavior preserved           |

These are the first completed sandboxed paired structural Nit results. Earlier instruction-only subagent reports remain evidence only, not rounds. The previous cancelled anti-pattern run is incomplete, not clean; the isolated completed simplify run is not a completed pair. No clean threshold is claimed. The earlier design gate remains pending TOOLING's decision; this review-correction go-ahead did not authorize resolving it or pushing. Production code is unchanged by the corrected review.

The sandboxed reviewer did not execute repository tests or plants; its runtime checks remain unverified. Its failed GitHub metadata request reflects sandbox networking, not a repository-state conclusion: the worker's outside-sandbox read in this turn confirmed the repository is not archived and is not a fork. Existing test/plant evidence above remains valid for its recorded snapshots. Final checks and the PR remain pending.

## TOOLING design decision and resumed fixes

TOOLING authorized unconditional submodule-visible diff options and call-local `diff.ignoreSubmodules` overrides from one shared policy for both helper copies and prompt renderers. The completed sandboxed pair is structural Nit round 1; the next pair is Important round 1. Any further ignore-settings instance stops the loop again. All later reviews run as standalone Codex in the built-in read-only sandbox from the Git checkout.

PID 20082 had already been terminated and its incomplete output is not counted. Its completed replacement sandboxed anti-patterns reply is preserved and all four findings are taken into Nit round 1. The implementation uses the existing shared-reference builder to distribute `review-git.bash`; both scope copies and codex-aspects consume its policy. Retained embedded directory paths are normalized and rendered as recursive directory scope; edit reports recognize directory coverage. Snapshot prose is corrected, and duplicate fixture mutations are consolidated. Last-submodule deletion and retained-checkout consumer tests added. Validation: 15 submodule cases, 48 existing scope cases, 82 aspect cases and 10 shared-copy cases pass. The last-submodule fixture executes the rendered committed diff with inherited ignore-all settings. Omitting both rendered policy overrides left the collector assertion true but failed exactly at the missing module in the executed reviewer command. Restored policy reproduces the passing fixture. Retained-checkout tests now exercise prompt generation and mutation scope. Recursive scope validation rejects child path escapes; weakening the child path check lost that intended rejection. All plants restored, clean tree before review.

Structural Nit round 1 takes are applied. Review again is required for the shared policy, retained directory consumer handling and recursive scope validation; prose and fixture simplification alone require no extra round. Structural Important round 1, including report-only simplify, is next.

## Structural Important round 1: design decision required

Both standalone reviewers completed with exit 0 using the required Git checkout cwd and built-in read-only sandbox. Anti-patterns passed the installed JSON checker with complete coverage and no unread paths. Report-only simplify passed the installed aspect validator and returned zero findings. Before/after comparison reported unchanged snapshot, no changed disk paths and no outside-scope edits. Execution session 87085 completed; reviewer PIDs 26981 and 26983 completed. Raw replies are committed as `2026-10-28-submodule-snapshot-important1-anti.json` and `2026-10-28-submodule-snapshot-important1-simplify.json`.

| Reviewer label                                                                  | Our severity                                                                                    | Take or record                                                                                                                                     | Review again                                                             |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Important: Parallel paths, committed submodule content classified outside scope | Important, editing an internal file actually shown in the review diff is incorrectly prohibited | Take pending structural design approval: derive exact prefixed membership from parent gitlink transitions, including staged and nested transitions | Yes, behavior changes                                                    |
| Important: Parallel paths, symlink discovery omits recursive untracked paths    | Important, a child link can reach a reviewer without link-only annotation                       | Take with the design fix: consume captured recursive scope paths and inspect directory scope without following links                               | No for prose alone; the behavioral membership fix requires another round |

No further ignore-settings instance was reported. These findings concern precise gitlink-content membership and recursive link discovery, distinct from the fixed ignore-setting policy and trailing-slash validation defects. The shared diff policy remains unchanged. The new membership calculation requires a structural design decision, so implementation stops at that gate. The proposed design is `2026-10-28-submodule-gitlink-membership-design.md` beside this ledger. No fixes for these new findings have been applied, and no clean threshold is claimed. The next structural review after behavior-changing fixes is Important round 2; counts do not reset.

Additional validation before this round: macOS `/bin/bash` 3.2 passed syntax checks and the nested, staged-only and removed-last-submodule fixture scenarios, with `/bin` before Homebrew in PATH for recursive helper execution. The restored shared policy passed the removed-last-submodule scenario after the omission plant. Prior affected suites remain green for their recorded snapshot. No push or PR; focused review, trims, Semgrep baseline, final lint/test-all/version checks and tidy remain pending.

## TOOLING latest instruction: paired Nit round 1 after the shared-policy fix

TOOLING reiterated that the stopped anti-pattern reviewer is incomplete and does not count, and explicitly directed a whole structural Nit round 1, both aspects sandboxed, after the ignore-settings structural fix. This latest instruction governs the next run. The shared policy fix is already committed in `1ba17562`, with the omission plant and affected suites recorded above. No production code changes are needed to repeat that fix.

A fresh paired Nit round 1 is being run on the fixed code using the installed anti-patterns 1.1.4 and aspect instructions from 2.1.4, standalone Codex from the existing Git checkout, built-in read-only sandbox, no trust override, `gpt-6.1-sol`, high effort and window 872000. Earlier labels and results remain historical evidence; the stopped run is never credited. The prior completed run labelled Important 1 remains preserved as evidence of its two outstanding findings, rather than being used to bypass this explicitly requested Nit round. Its proposed gitlink-membership design remains pending TOOLING's decision and unapplied. No clean result is inferred from any earlier evidence. Results recorded below.

## Requested fixed-code structural Nit round 1: completed

The full paired run on the applied shared-policy fix completed: anti-patterns exit 0, report-only simplify exit 0. Anti-patterns passed the installed 1.1.4 JSON checker with `complete: true` and no unread paths. Simplify passed the installed 2.1.4 aspect validator, including the exact reviewed snapshot, and returned no findings. Before/after scope comparison showed `scope_changed: false`, `changed: []` and `outside_scope: []`. No lasting changes found. Both ran in Codex's built-in read-only sandbox from the existing Git checkout without trust or sandbox overrides. Execution session 86704 completed; reviewers 46731 and 46735 completed. Raw replies are preserved as `2026-10-28-submodule-snapshot-postfix-nit1-anti.json` and `2026-10-28-submodule-snapshot-postfix-nit1-simplify.json`.

| Reviewer label and finding                                                               | Our severity                                                                      | Take or record                                                                                                                  | Review again                                                       |
| ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `important`: Parallel paths, gitlink diffs expose child files absent from editable scope | Important, legitimate edits to files actually reviewed are reported outside scope | Take pending the existing TOOLING gitlink-membership design decision; no implementation yet                                     | Yes, behavior-changing membership fix                              |
| `important`: Parallel paths, symlink discovery omits recursive untracked paths           | Important, recursive untracked links can miss their required link-only annotation | Take with the proposed captured-path discovery fix; no implementation yet                                                       | No for prose alone; membership behavior will require another round |
| `nit`: Docs drift, digest test explanation describes the opposite index strategy         | Nit, inaccurate existing test explanation                                         | Record as pre-existing and outside the branch's changed lines; the reviewer confirms the same sentence exists at the merge base | No, no edit                                                        |

No further ignore-settings instance was reported. The first two findings confirm the already recorded, unfixed design concerns rather than a new instance of a fixed class. Report-only simplify is clean at Nit; the paired loop has Important findings and no overall clean threshold is claimed. Under the latest explicit counting instruction, this completed fixed-code pair is structural Nit round 1; the next round after approved behavior-changing fixes is Important round 1. The stopped original anti-pattern review remains incomplete and never counts, and the instruction-only subagent reports remain evidence only. The outstanding design proposal is `2026-10-28-submodule-gitlink-membership-design.md`; no approval was inferred from the rerun instruction. No push or PR. No background reviewer remains.

## TOOLING addendum: one file-path contract through every consumer

TOOLING authorized taking the round's other findings with the ignore-policy fix: retained and embedded checkouts must emit reviewable file paths, never directory entries, and prompt, changes, validation and gate must consume exactly that contract. This opens the pending membership/discovery implementation under the same concern. Edit-round prose and fixture consolidation were already fixed. After these fixes the next paired review is structural Important round 1, standalone and sandboxed from the Git checkout.

The collector now records recursive file inventories, replaces aggregate untracked repositories with their individual files, and expands exact committed/staged/unstaged gitlink transitions into prefixed child paths. Shared policy supplies all diff flags, including stable raw-record/no-rename handling. Unavailable required initialized-child objects fail with Git diagnostics. Consumers no longer grant directory-wide membership; initialized paths are explicit, and uninitialized gitlinks remain pointer metadata. Symlink discovery uses captured recursive paths. End-to-end retained/deleted fixtures and additional precise-membership, nested, embedded and symlink cases exercise prompt, validation, changes and gate. Validation and required omission/trailing-entry plants pending.

## File-contract validation and plants

The implementation in `47413a22` and `6d047434` applies TOOLING's path contract and the pending membership/discovery findings. The collector expands retained/embedded repositories into a recursive `files` inventory, with no directory entries in untracked scope. Shared validation requires untracked paths to belong to that inventory. End-to-end fixtures exercise prompt rendering, aspect validation, changes and gate, including initialized/uninitialized nested entries, committed/staged gitlink paths, unrelated-file rejection and missing-object diagnostics. The staged case uses an index gitlink different from the actual checkout and asserts both staged and unstaged memberships.

Passing checks: 15 original submodule cases; 48 original scope cases; 82 aspect cases; 8 consumer cases, including 12 malformed-entry rejection probes across all four consumers. The final frozen consumer document completed in 57.83 seconds locally. One earlier consumer run was discarded because editing the fixture while it was being read caused an EOF parse failure after its assertions; syntax checks passed and the frozen full rerun passed. No failed run is counted as passing. Bash 3.2 syntax and committed/staged consumer cases passed.

The mutation checks execute the exact committed Scrut cases, copied without assertion changes into an external one-case document. A positive control passes before mutation and after restoration. All source and generated shared-policy copies are restored, with a clean tree before recording this section.

| Boundary                     | Actual plant                                                                                          | Scrut result | Guard confirmed                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------- | ------------ | ---------------------------------------------------------------------------- |
| Last-submodule visibility    | Omit both overrides from the shared rendered command                                                  | Exit 50      | Collector assertion passes, executed reviewer diff omits the required module |
| File-only scope              | Keep the aggregate module/ entry instead of file expansion                                            | Exit 50      | Prompt's shared scope validator rejects the emitted trailing-slash entry     |
| Precise gitlink membership   | Omit recursive immutable gitlink expansion                                                            | Exit 50      | Committed child-file membership assertion returns false                      |
| Recursive symlink annotation | Replace the actual documentation snippet's captured-path enumeration with parent-only Git enumeration | Exit 50      | Required child-link JSON annotation is absent                                |
| Uniform inventory validation | Remove the common untracked-minus-files check                                                         | Exit 50      | The consumer rejection contract fails; restoring it passes all 12 checks     |

The original four plants were repeated against the final contract and all remained red at their intended boundaries. Restored control passed. The prose Nit and fixture consolidation remain applied. Structural Important round 1 with report-only simplify is next, using fresh standalone Codex in the built-in read-only sandbox from the Git checkout. Any further ignore-settings instance stops the loop again.

## File-contract structural Important round 1

Both standalone read-only reviewers completed with exit 0. Anti-patterns passed its installed checker with complete coverage and no unread paths; simplify passed the installed aspect validator with no findings. Scope comparison reported unchanged snapshot and no lasting changes. Execution session 64568 completed. Raw replies are `2026-10-28-file-contract-important1-anti.json` and `2026-10-28-file-contract-important1-simplify.json`.

| Reviewer label                                                                     | Our severity                                                                   | Take or record                                                            | Review again          |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------- | --------------------- |
| `important`: Sibling input forms, gitlink-to-symlink replacements abort collection | Important, a legitimate native Git type change cannot reach review             | Take: treat a replacement as parent symlink content without traversing it | Yes, behavior changes |
| `important`: Untrusted data in commands, option-like submodule paths reach cd/find | Important, legitimate initialized or uninitialized checkout paths are rejected | Take: use one absolute child path for all filesystem operations           | Yes, behavior changes |

No further ignore-settings instance. The first defect is a valid type transition rejected by the collector, distinct from the previously fixed omission of recursive untracked link annotations; the second is option parsing of checkout paths. Both are within the approved path contract and require local implementation fixes, not a new design gate. Fixes and consumer regressions are being applied. The next paired structural round is Important round 2. No clean threshold is claimed for round 1.

## Important round 1 input-form fixes validated

The fixes in `d3e5aa21` use an absolute checkout path throughout collection and treat current non-directory replacements as parent content. Parent components are checked before descending, so a replaced parent directory cannot redirect an old indexed gitlink into another repository. Consumer regressions cover symlink targets that are Git repositories, target-content changes that must not move the snapshot, link-text changes, regular-file replacements, ancestor replacements and initialized/uninitialized option-like checkout paths.

All 11 consumer cases and 15 original submodule cases pass. The consumer document completed in 93.74 seconds locally. Bash 3.2 passed the ancestor-replacement and option-like initialized/uninitialized cases. Git's deinit filters option-like paths, so the fixture constructs the empty checkout directly using only its own recorded files; the helper must still collect and consume that state. A separate native probe confirmed the rendered committed diff includes the initialized option-like checkout's actual file content.

Exact committed Scrut cases were planted: removing the direct symlink guard, removing the parent-component guard, restoring relative cd, and restoring relative find each produced Scrut exit 50 with valid shell syntax. The restored initialized/uninitialized control passed. All plants are restored and the worktree is clean before this record. Structural Important round 2 is next; the following behavior-changing round, if required, is Critical-only under the round sequence. Any further ignore-settings instance still stops the loop.

## Structural Important round 2: stopped on recurring operand handling

Both standalone reviewers completed with exit 0 from the Git checkout in the built-in read-only sandbox. Anti-patterns passed its installed checker with complete coverage and no unread paths. Report-only simplify passed the installed aspect validator with zero findings. Before/after snapshot was unchanged, with no changed paths or outside-scope edits. Execution session 28856 and reviewers 57356/57357 completed. Raw replies are `2026-10-28-file-contract-important2-anti.json` and `2026-10-28-file-contract-important2-simplify.json`.

- **Reviewer label:** `important`, “Untrusted data in commands: recursive symlink discovery passes option-like paths to readlink”.
- **Our severity:** Important. A newly supported checkout named `-vendor` can contain an untracked link, and the discovery snippet passes `-vendor/new-link` directly to `readlink`. It is interpreted as options, so discovery fails before annotation. The standalone system-tool probe returned an illegal-option error. Although the operand form predates the change, this branch rewrites the snippet and makes the recursive input form reachable.
- **Take or record:** Take pending the mandatory recurrence decision. The same option-like operand class was fixed for cd/find in Important round 1 and now appears in readlink. No fix is applied at this gate.
- **Review again:** Only if the approved fix changes production behavior; the next structural threshold is Critical-only, since Nit 1 and both Important rounds are used. An instructions/tests-only fix does not require another round under the no-behavior-change rule.

End state: **stopped: recurring defect**. No further ignore-settings instance was reported. The design brief is `2026-10-28-recursive-path-operand-design.md` beside this ledger: one rooted filesystem-operand invariant across collectors, consumers and prose, preserving canonical relative JSON paths, with a combined option-like checkout/untracked-link regression and omission plant. No new tool is proposed.

The existing separate cases passed but did not cover their combination. Existing 11 consumer and 15 original submodule cases and the recorded plants remain passing evidence for their snapshots; this review result is not clean. No background reviewer remains. No push or PR. Focused review, trims, baseline Semgrep, final lint/test-all/version checks and tidy remain pending.

## TOOLING structural call: one authoritative membership builder

TOOLING classified gitlink editable-membership drift and the earlier trailing-slash mismatch as one collection-to-consumer class, approved the child-transition direction, and required the exact calculation in shared review-git.bash. Every consumer must use that list, with one contract assertion across fixtures and a plant for each drifting consumer. Missing initialized-child objects must fail with diagnostics, never fetching or initializing. The next requested structural round is Important 2; a third instance of the collection/consumer class stops for consideration of the out-of-scope fallback.

The shared library now owns exact transition expansion, recursive inventory/local-bucket union, canonical membership construction and reading. Membership records contain one relative path and its bucket labels; compatibility bucket arrays and empty are generated views, validated against the records. The actual digest hashes that same array and stores its canonical JSON record as an unreferenced Git blob. Prompt descriptors, validation status, changes acceptance, gate and link discovery use the common reader. Gate also checks before/after membership and status membership. The source and both harness mirrors remain aligned.

The rooted operand direction is implemented through shared link discovery, replacing the duplicated documentation loop. Prompts use that same discovery for all member links, including tracked replacements, and do not duplicate link annotations in the untracked-file section. The combined -vendor/untracked-link fixture passes, including Bash 3.2. A single contract assertion compares actual stored digest membership, serialized scope, helper reader, prompt descriptor, validation, accepted paths, gate and discovery for every fixture; expected error fixtures validate their initial successful state. Record equality uses canonical JSON key ordering after an initial byte-comparison assertion reported semantically equal objects as different.

Before the final status-binding step, targeted suites passed 12 consumer, 15 submodule, 82 aspect and 48 scope cases. Contract drift plants and final validation pending. Versions advance to review-until-clean 3.3.0 and review-pr-with-codex 2.2.0 for the canonical membership and bundled transport API. No push or PR.

## Canonical membership contract validated

The centralized implementation is committed in 5a703b05. One builder in the shared library expands immutable gitlink transitions, recurses through captured initialized checkouts and unions child-local bucket records. Snapshot hashing and serialized scope read the same membership file; compatibility aliases and empty are generated views. Every consumer uses the shared reader. Gate binds validation-status membership and before/after membership. The prompt references canonical records and uses common rooted link descriptions, including tracked replacements; no relative captured path reaches readlink.

Passing targeted checks: 12 consumer fixtures, 15 original submodule fixtures, 82 aspect cases and 48 scope cases. The single reused contract assertion runs for every fixture, including initial successful states of expected-error cases. It reads the actual stored digest blob, checks canonical record equality and compares path sets across serialized scope, reader, prompt descriptor, validation, changes acceptance, gate and discovery. A changed membership with a reused snapshot string is rejected by the gate. The combined option-like checkout/untracked-link case passes under macOS Bash 3.2.

The same committed stable-fixture Scrut contract case was used for every drift plant. A positive control passed before mutation. Valid mutations independently changed digest membership, serialized output membership, the prompt descriptor, changes acceptance, validation's view, gate's view, discovery's view and the common reader. Each returned Scrut exit 50; restored control passed. The gate plant specifically dropped child paths, so the reused-snapshot membership-change probe detected an admission error rather than just metadata formatting. All source and generated policy copies are restored; clean tree before recording.

The pending collection/consumer structural design is implemented under TOOLING's call. The next specifically requested review remains structural Important round 2. No count is reset. Any third collection/consumer mismatch stops for the out-of-scope-fallback decision; any further ignore-settings instance also stops. All reviews remain standalone Codex, built-in read-only sandbox, Git checkout cwd, no trust override. No push or PR.

## Canonical structural Important round 2: historical guidance design gate

Both standalone reviewers completed with exit 0 in the built-in read-only sandbox from the Git checkout. Anti-patterns passed the installed checker, complete coverage and no unread paths. Simplify passed the installed aspect validator with no findings. Before/after snapshot was unchanged, with no changed or outside-scope paths. Execution session 9750 and reviewers 54552/54554 completed. Raw replies: `2026-10-28-canonical-important2-anti.json` and `2026-10-28-canonical-important2-simplify.json`.

- **Reviewer label:** `important`, “Parallel paths: recursive reviews omit historical submodule instructions”.
- **Our severity:** Important. Recursive code paths are reviewed, but applicable child historical instructions are looked up in the outer repository and omitted; the reviewer is simultaneously told not to use live checkout instructions.
- **Take or record:** Take pending a required trust-policy design decision. No downgrade and no implementation at this gate. The common membership sets still agree; this finding concerns the repository/revision context of derived historical guidance, not an observed third membership-set mismatch.
- **Review again:** Yes if guide-resolution production behavior changes. Preserve the used round counts and TOOLING's explicit continuation decision; the default next structural threshold is Critical-only.

Proposed design: `2026-10-28-submodule-historical-guidance-design.md`. Resolve each child guide in its own object database at the gitlink selected by the trusted parent baseline, recursively. Never silently treat current child HEAD as trusted, since committed instruction changes may themselves be under review. A child absent from that trusted parent path has no historical child trust established; inheritance and explicit reporting are proposed instead of guessing. One shared resolver and generic reviewer context must cover both harnesses.

No further ignore-settings instance or path-set drift was reported. Stop at the design gate, with no overall clean claim. No active reviewer, push or PR. The central membership implementation and recorded contract tests/plants remain intact. Focused review, trims, Semgrep baseline, final lint/test-all/version verification and tidy remain pending.

## TOOLING stale-message counting correction

TOOLING clarified that the 4:41 PM ET message was stale: the completed sandboxed Nit round 1 and Important round 1 stand; the extra Nit rerun must not count. That rerun had already completed before this correction arrived, so there is no live process from it to terminate. Its captured `anti 0` and `simplify 0` remain evidence only, explicitly excluded from the count. Recorded PIDs are not signalled after completion or reused as a reason to start another run.

Accepted progression follows the corrected instruction: completed sandboxed Nit 1, completed Important 1, the approved 5:15 PM ET one-list membership implementation, then Important 2. The 5:15 implementation is already committed in 5a703b05 with its contract/drift-plant record in 1c8e2861. Important 2 then completed in `/tmp/523-reviews/canonical-important2/` with both exits 0, validated replies and unchanged reviewed snapshot. No production/test/manifest/generated files differ between that reviewed commit and the current recorded state; only process records were added. No further review is launched for the stale instruction and no new round budget is created. Other completed intervening reports remain historical evidence, with no claim of a fresh Important allowance.

The active stop is still the new historical-child-guidance trust-policy design gate from Important 2, documented above and sent to TOOLING. The correction does not approve that separate design. No source fix is applied, no reviewer is active, and no push or PR exists.

## Consolidated TOOLING instruction governs counts and continuation

TOOLING supplied one consolidated instruction replacing earlier queued messages where they differ: the first completed sandboxed pair is Nit 1; the pair with the gitlink-membership and recursive-symlink findings is Important 1; the subsequent rerun is evidence only. Preserve those accepted rounds and do not use superseded labels to claim another allowance.

The approved design is the gitlink-membership proposal plus the 5:15 PM ET one-list requirement. That implementation is already present in 5a703b05: one shared builder/reader, exact initialized-child transitions, child-local bucket union, common consumers, actual digest-blob contract and independent drift plants. Missing initialized-child objects fail diagnostically without fetch/init. Targeted passing results and eight red/restored-green plants are recorded above. No source reimplementation or schema change is needed for the consolidated direction.

A fresh specifically requested structural Important 2 is run on this committed implementation, both report-only aspects through standalone Codex from the Git checkout, built-in read-only sandbox, no override, gpt-6.1-sol/high/872000. Earlier rerun output, including the historical-guidance concern, is retained as evidence only for this instruction. The separate historical-guidance design is not implicitly approved by the membership call. A third collection-to-consumer mismatch stops the loop for TOOLING's fallback decision. Results recorded below; no push or PR.

## Accepted consolidated Important round 2 completed

Both standalone reviewers exited 0 with the required read-only sandbox and Git working directory. Anti-patterns passed the installed result checker with complete coverage and no unread paths. Report-only simplify passed the installed aspect/snapshot validator with zero findings. Before/after scope comparison reported unchanged snapshot, no changed paths and no outside-scope edits. Execution session 91488 and recorded reviewers 42657/42659 completed. Raw replies: `2026-10-28-consolidated-important2-anti.json` and `2026-10-28-consolidated-important2-simplify.json`.

This is the accepted Important 2 under TOOLING's consolidated instruction. Nit 1 and Important 1 stand as specified there; intervening reruns remain evidence, never a fresh budget. No further structural round is started at this gate.

- **Reviewer label:** `important`, “Parallel paths: recursive reviews omit historical submodule instructions”.
- **Our severity:** Important, because required child review checks can be omitted while a review reports success.
- **Take or record:** Take pending the existing historical-guidance trust-policy decision. The approved membership proposal is fully implemented; its approval does not select trusted child instruction revisions. No fix is applied by guessing current child HEAD.
- **Review again:** Yes if the approved resolution changes guide-loading production behavior; the default next threshold is Critical-only, preserving counts.

This confirms the previously recorded design concern. The canonical path-set contract remains passing, and no third membership-set mismatch or further ignore-settings instance was reported. The existing proposal `2026-10-28-submodule-historical-guidance-design.md` derives child trust from the parent's baseline gitlink, recursively, across both harnesses; missing objects fail without fetch/init. The design gate remains closed until TOOLING chooses that policy or another. No reviewer remains active. No push or PR. Later focused review, trims, baseline Semgrep, final checks and tidy remain pending.

## TOOLING count-only confirmation

TOOLING confirmed that the round described as running is structural Important 2 because the gitlink/symlink pair was Important 1. The round had already finished when this confirmation arrived: both exits 0, anti-patterns complete with one Important historical-guidance finding, simplify with no findings, and unchanged scope. Its accepted Important 2 label above is unchanged. No process is stopped or restarted for this count-only instruction.

Continuation is conditional, not an automatic extra round: if an approved fix takes an Important or Critical finding and changes behavior, the next structural threshold is Critical-only. A clean Important 2 would end clean at Important; this completed round is not clean because the historical-guidance finding remains at its separate design gate. A third collection-to-consumer mismatch still stops. No new source authorization is inferred from this count correction.

## TOOLING final count correction: Critical round 1

TOOLING clarified that the round finding the input-form defects was Important 2, and the subsequent completed round is Critical-only round 1. This explicit correction governs. Both completed reviewers exited 0, replies validated, and scope was unchanged. Anti-patterns reported one Important historical-guidance issue and no Critical findings; simplify reported none.

The historical-guidance finding is recorded below threshold, without implementation. Its reviewer label and our Important severity remain unchanged. The proposed resolver remains an unimplemented follow-up, not a blocker under this Critical-only threshold. No Critical finding was taken and no behavior changed, so the structural loop ends **clean at Critical**. The separate design ask is withdrawn for this workstream under TOOLING's direction to continue. No new structural round is started. Third collection-to-consumer mismatch stop remains applicable to any further explicitly authorized structural work.

Next: focused review loop and the remaining local order. Counts for that separate loop start at its Nit round, not a reset of the structural loop.

## Focused Nit round 1

All five applicable aspects completed in parallel as standalone read-only Codex, gpt-6.1-sol/high/872000. All process exits 0 and installed aspect/snapshot validation passed; before/after scope was unchanged. Raw replies are the focused-nit1 code/errors/tests/comments/types JSON files beside this ledger. Types found no issues.

| Reviewer label                                                          | Our severity                                                              | Take or record                                                                                          | Review again          |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | --------------------- |
| `important`: historical child guidance omitted (code/errors duplicate)  | Important, same known issue                                               | Record without fixing under the explicit Critical-round disposition; no new design ask from a duplicate | No edit               |
| `important`: inventory rejection tests fail for alias mismatch          | Important, removed inventory validation could remain undetected           | Take: encode matching canonical membership/views in negative inputs                                     | No, tests only        |
| `important`: recursive stability lacks during-collection mutation test  | Important, a removed child comparison could remain undetected             | Take: committed exported Git function mutates child index after first capture; marker verifies event    | No, tests only        |
| `important`: recursive path-write failures may return partial success   | Important, incomplete changed/outside lists can be reported as successful | Take: both printf appends explicitly fail with path/output diagnostics                                  | Yes, behavior changes |
| `suggestion`: clarify finding syntax versus scope membership validation | Nit, factual contract wording                                             | Take local prose correction                                                                             | No, prose only        |

New exact Scrut boundary cases passed before planting. Omitting shared inventory validation, recursive child comparison, changed-path append guard and initialization append guard each produced exit 50. The transition fixture includes a later successful child, proving the failure cannot be hidden by subsequent success. Restored recursive-error control passed; all mutants restored. The Git/printf stubs are committed with the fixture and verify their function resolution before use. ShellCheck findings in the test code were corrected. The production write-error fix requires focused Important round 1 next. Structural loop remains clean at Critical; its counters do not reset.

## Focused Important round 1 and loop end

All five standalone read-only aspects completed with exits 0, installed schema/snapshot validation passed, and the reviewed scope was unchanged. Raw replies are focused-important1 code/errors/tests/comments/types JSON beside this ledger. The first postcheck included this run's newly copied report artifacts; those five created files were removed, the original reviewed snapshot was recaptured exactly, and artifacts were copied back only after the successful check. No reviewer/source edit was attributed to that recording-order mistake.

Tests found no new Important or Critical gaps. Code/errors/types and comments repeat the known historical-guidance issue, with reviewer important and our Important severity unchanged. It remains recorded without fixing under the explicit user disposition; no downgrade or new design ask is inferred. No other finding was taken and no behavior changed in this round.

Focused loop: **ended: fixes changed no behavior**. The Nit-round code and boundary-test fixes were reviewed by this round; known recorded guidance remains disclosed, so this is not an unqualified clean claim. Structural loop remains **clean at Critical**. Next are one read-only trim round, baseline Semgrep, final checks and tidy.

## Trim round

Both standalone read-only trim runs completed with exits 0 using gpt-6.1-sol/low/872000 from the Git checkout. Replies include Files classified and complete proposal tables; source was clean before applying proposals. Applied the embedded-entry comment, both repository-root comments, fixture comment and one validator prose rewrite. Rejected the first library-header replacement because it describes only Git options while the module also owns canonical membership; retained the sourced-library boundary. No behavior changed. Raw tables are committed as comment/prose trim proposal text beside this ledger. No second trim round.

## Semgrep baseline stop

The required scan ran in a disposable shared clone of branch head, with SEMGREP_REPO_NAME=cboone/agent-harness-plugins, config auto, the actual origin/main merge base and default metrics. Command exited 0 and reported zero findings, but the JSON has two PartialParsing errors: bin/build-shared-references (parameter expansion containing a pipe pattern) and plugins/review-pr-with-codex/scripts/codex-aspects (reported span covers its script body). Coverage is incomplete; this is not a passing security scan. Summary diagnostics are committed beside this ledger. No full-scan/changed-line substitute or metrics override was used.

The baseline command was semgrep scan --config auto --baseline-commit 4b473c00e6ad3bb935f204eb7807aaa554b91c57 --json --output /tmp/523-semgrep-results.json, executed in the shared clone recorded in /tmp/523-semgrep-location, with stdout/stderr in /tmp/523-semgrep.log. Full JSON and version output remain under /tmp/523-semgrep-results.json and /tmp/523-semgrep-version. Semgrep's no-current-findings optimization skipped a separate baseline-side scan; the requested baseline option was supplied, and parser errors still prevent acceptance.

Stop at the required baseline-completion gate and report to TOOLING. Do not rewrite valid unrelated Bash merely to satisfy an unsupported parser without a decision, install software, weaken the scan, or describe zero findings as complete. No background command remains. Final lint-and-fix, make test-all, check-versions, exact-tree tidy, push and PR remain pending. Structural loop is clean at Critical; focused loop ended: fixes changed no behavior, with the known Important guidance issue explicitly retained. The single trim round is complete with applied meaning-preserving proposals.

The final status check found one regenerated shared-policy comment copy omitted from the trim commit's staging list. It matches the canonical library exactly and is committed now; no behavior changed. The Semgrep clone scanned trim head 4f00913a before subsequent process-record commits and this generated-comment-only commit. These additions do not resolve its parser errors, and no clean-scan claim is made. The owned worktree is left clean at the gate.

## Approved rooted-operand audit and continuation

TOOLING approved the recursive-path-operand design: canonical relative strings remain data; each filesystem operation uses a separately derived absolute or dot-prefixed operand. Shared link discovery and the combined initialized -vendor/untracked-link/Bash-3.2 fixture already satisfy the behavioral fix. Remaining repeated absolute joins in transition object lookups and prompt file checks are now derived once per path. The pending Semgrep parser gate is not waived by this call.

Audit: collector parent-component tests use the absolute current prefix; checkout Git/cd/find operations use child_repo; transition object reads and recursive descent use child_repo; shared discovery uses operand for lstat/readlink; prompt untracked type checks use operand; changes recursion receives an absolute repo/path once per child; historical Git-tree lookups keep relative object paths only as literal pathspec data after --, with an absolute repository operand. Root/temporary/helper locations come from trusted absolute Git roots or mktemp values. Reviewer prose calls shared --symlinks and contains no direct filesystem operation on captured relative names. Both canonical copies and both harness mirrors share this policy.

The approved combined fixture executes the actual documentation snippet through all consumers. A specific omission plant changes shared operand from repo/path to the raw relative path; the -vendor/new-link case must fail. Source and JSON paths remain canonical relative strings. Next requested structural run is Critical-only round 1, followed by the remaining order at preserved focused-loop counts. Any further option-like operand instance stops again.

## Nighttime checkpoint

At 9:45 PM ET, the approved rooted-operand audit is committed as 3170b73a. Build and ShellCheck passed. The exact combined option-like checkout/untracked-link Scrut case passed; replacing the shared rooted operand with the relative string failed with exit 50 and visible readlink diagnostics; restoration passed. The same combined fixture passed again under macOS Bash 3.2 with /bin first on PATH. All mutant edits are restored.

No new structural round was started. Next is the requested standalone read-only structural Critical-only round 1, then the focused loop at its preserved counts and the remaining order. Another option-like operand instance stops again. The Semgrep PartialParsing stop remains unresolved and prevents treating the baseline scan as green. Final lint-and-fix, make test-all, check-versions, tidy, push, PR and CI remain pending. No background commands remain; no push or PR occurred. Nighttime stop reported to TOOLING for parking.

## Count clarification received after nighttime stop

The next requested structural round is labeled **structural Critical-only**, never Important 2. Only Critical findings are taken. Important and Nit findings receive the four separate calls, remain unfixed, and are included in the final review précis. If no Critical finding is taken, or fixes change no behavior, the structural loop ends clean at Critical. The separate focused review-pr-with-codex loop starts at its own Nit round under the latest explicit instruction; previously completed focused reports remain evidence and their findings/fixes remain recorded.

The issue behind shared canonical membership was found in the accepted structural Important round 1, the pair reporting gitlink child paths outside editable scope and omitted recursive symlink discovery. Both reviewer labels were Important and both were assessed Important: legitimate edits to reviewed child files were prohibited, and recursive untracked links could reach review without required link-only annotation. TOOLING then grouped the collection/consumer mismatch with the earlier trailing-slash defect and required one shared membership builder and reader. The subsequent duplicate rerun is evidence only.

No reviewer is currently running. The nighttime stop remains in effect; this count clarification does not launch another run or waive the Semgrep parsing gate.

## TOOLING disposition: historical child guidance follow-up

- **Reviewer's label:** Important, omitted historical child guidance.
- **Our severity:** Important. Omission lowers review quality without serious harm on a reachable path, so it does not meet Critical severity.
- **Take or record:** Recorded, not taken, under TOOLING's explicit disposition. The trust-policy decision and existing design brief are tracked in [the historical submodule guidance follow-up](https://github.com/cboone/agent-harness-plugins/issues/674). No implementation belongs in this branch, and this is not a membership-set recurrence.
- **Review again:** No behavior changes from this disposition. With no Critical finding taken, structural review ends **clean at Critical**.

The PR body must name the historical-guidance issue as a known follow-up that the PR does not close. Next is the separate focused review-pr-with-codex loop at its own Nit round, then the remaining local order. The nighttime stop remains recorded; no reviewer is launched by this record-only update. The unresolved Semgrep parsing gate remains applicable.

## Authoritative consolidated structural disposition

TOOLING's consolidated instruction replaces every earlier count message. The completed structural run counts as Critical-only. It took no Critical finding, so the structural loop is **clean at Critical**. No other structural rerun is authorized or will be launched. All lower-threshold findings retain their four-call dispositions above; historical child guidance is Important, recorded and not taken, tracked in the known follow-up at https://github.com/cboone/agent-harness-plugins/issues/674. The PR must cite that follow-up without closing it.

No structural run is active when this instruction arrives. Earlier text calling for another structural Critical-only round is superseded. The next review is the focused review-pr-with-codex loop from its own Nit round, then the remaining order. The nighttime stop and unresolved Semgrep parsing gate remain recorded.

## Updated overnight cutoff

TOOLING confirmed the consolidated disposition and set the standing cutoff: commit, record and report by 9:40 PM ET; TOOLING parks the worker at 9:45 PM ET and resumes it after 8 AM ET. The worker is already stopped with committed changes and no running review. Resume requires TOOLING's restart. Next is focused Nit; structural review remains clean at Critical with no rerun. Semgrep PartialParsing still requires resolution before the remaining final gates.

## Authorized final checks before tidy

TOOLING lifted the nighttime stop, reported the Semgrep parsing decision pending in the Inbox thread "Semgrep partial parsing", and explicitly authorized lint-and-fix --no-push, make test-all and check-versions before stopping at tidy. These checks completed successfully against source HEAD 5e80ad5d; no source or generated file changed.

Lint-and-fix status: **no-op**, lint status **success**, fixes commit **none**, unresolved/skipped **none**. Markdownlint and Prettier ran in check mode to preserve protected Scrut snapshots and generated copies under repository policy. ShellCheck, shfmt and Actionlint passed; repository JSON/plugin validation passed. The full make test-all invocation repeated all checks as final verification and exited 0. All **42 Scrut documents passed**, including both recursive submodule documents and the scope/aspect suites. Full logs are /tmp/523-final-lint.log, /tmp/523-final-validate.log and /tmp/523-final-test-all.log.

The repository check-versions skill passed against the freshly fetched origin/main merge base 4b473c00e6ad3bb935f204eb7807aaa554b91c57. Changed plugins: review-until-clean 3.2.0 to 3.3.0 and review-pr-with-codex 2.1.4 to 2.2.0, minor capability bumps. All 60 plugin directories match catalog coverage; all manifest versions are valid, present Codex manifests agree, and marketplace metadata/entries carry no duplicate version state. Structured report remains /tmp/523-final-version-report.json.

Stop **before tidy**, as explicitly directed. No backup/reset/tidy, push or PR performed; no background commands remain. Semgrep PartialParsing is still unresolved and is not reported green. Structural review remains clean at Critical, historical guidance is recorded Important with its known follow-up, and the requested focused Nit round remains pending under the latest consolidated instruction. No other structural rerun will launch. Report these results to TOOLING and await its decision/next gate.

## Semgrep shell partial-parsing standing rule applied

TOOLING relayed the standing tooling-project rule from the 9:39 PM ET Inbox decision: a completed baseline scan counts when partial parsing affects only shell files, provided coverage and affected files are recorded and ShellCheck passes on those files. Other-language partial parsing still stops. The completed Semgrep 1.180.0 baseline scan had zero findings, approximately 75.9 percent parsed lines, and PartialParsing only in bin/build-shared-references (lines 58-59 and 78-79) and plugins/review-pr-with-codex/scripts/codex-aspects (body beginning at line 3). Targeted ShellCheck on both files passed again with exit 0. The scan therefore counts under the standing rule; its incomplete shell parse coverage remains disclosed, not represented as full coverage.

The requested focused Nit round runs before tidy/publication. All five applicable aspects (code, errors, tests, comments and types) use standalone Codex gpt-6.1-sol/high/872000 in the built-in read-only sandbox from the trusted Git checkout. No structural rerun. Canonical helper prompts capture the current membership contract; output schema and validation are retained. Historical guidance remains recorded Important, not taken, under the explicit follow-up disposition.

## Final focused Nit round and disposition

All five standalone read-only Codex runs completed with exit 0 and schema-valid nonempty replies. Installed review-pr-with-codex 2.1.4 rendered and validated the prompts/results; the initial canonical renderer refused its own checkout and no reviewer launched through it. That refusal was corrected using the installed helper, with no trust or sandbox override. All runs used gpt-6.1-sol/high/872000 from the trusted Git checkout. Before/after scopes matched, with no lasting changes found; reports were copied into the repository only after that check. Raw results are final-focused-nit code/errors/tests/comments/types JSON beside this ledger.

| Reviewer's label                                                  | Our severity                                                              | Take or record                                                                                         | Review again           |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------- |
| important: historical child guidance (code/errors/types)          | Important, omitted mandatory child context lowers review quality          | Record, not taken under TOOLING's explicit disposition; follow-up 674                                  | No edits               |
| important: historical child-guidance test gap (tests)             | Important, same known unresolved behavior                                 | Record with follow-up 674, without implementing its trust policy                                       | No edits               |
| important: historical child-guidance documentation gap (comments) | Important, documentation does not surface that known limitation           | Record with follow-up 674 under the explicit no-implementation disposition; disclose in PR             | No edits               |
| important: status-membership rejection coverage (tests)           | Important, the gate's authorization boundary lacked a negative regression | Take tests for mismatched and absent successful-status membership, preserving identical scopes/results | No, test-only changes  |
| suggestion: files inventory wording (comments)                    | Nit, path strings were described as if they carried link metadata         | Take precise wording; link text is returned by --symlinks                                              | No, prose-only changes |

The reused fixture contract now rejects both mismatched and missing status membership for every successful fixture. Exact combined Scrut control passed, omission of the status guard returned exit 50, restored control passed, and a separate mutant admitting only missing membership returned exit 50. Both production mutations are restored. No new production behavior changed, so the focused loop **ended: fixes changed no behavior**. No extra round is launched. Structural remains **clean at Critical**. The branch trim round was already completed; PR-body trim preserved headings, code spans, issue references, closing/follow-up sections and checklist states while removing routine review-status prose and suite counts.

Final checks are repeated after these test/prose edits before tidy. The Semgrep standing rule has resolved the shell-only parsing stop. No structural rerun, historical-guidance implementation or label change is included.

## Final publication checks and tidy authorization

The post-focused make test-all invocation exited 0: all 42 Scrut documents passed, with zero failed/skipped cases. Its lint, JSON/plugin and generated-copy checks all passed. Full log: /tmp/523-post-focused-test-all.log. Lint-and-fix --no-push remains successful with no additional formatting fixes or skipped required checks. Version checks were repeated after fetch and remain clear against the same actual origin/main merge base, with both intended minor bumps and all 60 catalog entries consistent.

TOOLING explicitly authorized applying the shell-only Semgrep rule, then final checks, tidy, push and a ready-for-review PR. All preceding gates are satisfied. Tidy retains a pre-tidy backup and rebuilds signed implementation, test and documentation commits; exact tree equality is required before push. Historical guidance follow-up 674 remains open and must appear in the PR body without a closing keyword. Copilot is paused; no request or wait is authorized. TOOLING merges; this worker never merges.

## Publication and main integration stop

Ready-for-review PR: https://github.com/cboone/agent-harness-plugins/pull/675. Tidy produced three valid signed commits and exact tree equality with fix/523-review-snapshot-submodules-pre-tidy. Stored PR body, head and non-draft status were verified; historical guidance follow-up 674 is cited without closing it. GitHub reported conflicts with newer main and no checks registered.

The merge of origin/main a2e56c53 is uncommitted. Its sole CI conflict is resolved with main's Make-based Scrut job, preserving the merged fixture registration. The owned fixture and two new documents source main's Git-environment reset. Integration validation now fails on retained diagnostics in the owned fixture and on textual Git-consumer classification in build-shared-references, build-review-checklists, validate-plugins and their Scrut callers. The shared-library copy reference is propagated as execution by the inherited static checker. No unrelated generator or checker was changed.

Stop for TOOLING's scope/design decision before broadening the validator fix. Exact failures and state are in the conductor question/checkpoint. No live commands; no merge commit or integration push yet. Pre-integration full tests passed; integrated tests and CI are not claimed green. This ledger entry remains uncommitted with the pending merge, since a partial commit during merge is not available.

## Signed main integration continuation and validator stop

TOOLING explicitly requires a signed merge of origin/main, preserving pushed history, and a focused Critical-only round on the merged tree before final checks/push. The pending merge remains uncommitted because the previously reported checker scope decision is unresolved. No rebase, force push or PR reopen is used.

The owned fixture integration is now concrete: Git-environment reset occurs first, retained child diagnostics use capture_child and remain visible, and expected rejection snapshots include those diagnostics. Both affected integrated suites passed through main's checked runner: 17 submodule cases and 15 consumer cases, zero failed/skipped. ShellCheck on the fixture and git diff --check passed. Logs: /tmp/523-integrated-submodules.log and /tmp/523-integrated-consumers.log.

Remaining check-fixture-environments failures require resets in bin/build-shared-references, bin/build-review-checklists, bin/validate-plugins and the build-shared-references/build-review-checklists Scrut documents. Its textual reference closure treats the shared library's copy-table entry as execution and propagates the classification. The fixture capture failure is fixed. No checker or unrelated generator change has been made. TOOLING has the scope question; no active command remains. The newly ordered Critical-only reviews, fresh baseline scan, integrated full checks and push remain pending resolution of that named scope stop.

## TOOLING checker scope authorization

TOOLING authorized a narrow checker refinement in its own commit: literal shared-reference copy data must not imply execution by build-shared-references, while real execution references retain reset requirements. Positive and negative plants are required. No environment resets are added to unrelated tools. Complete the signed main merge with the already validated owned fixture integration, then commit the checker refinement separately. The known checker failure remains explicit until that commit is validated. Next is one focused Critical-only round on the merged tree, followed by remaining scans/checks and push; stop if checker scope grows.

## Narrow copy-reference checker fix

The signed main merge is b8538eb6. The checker refinement is seven production lines: only literal source|copy entries inside build-shared-references' SHARED_REFERENCES array are excluded from execution-reference tracing. Dynamic entries and execution references outside the table still enter the graph. No unrelated tool receives an environment reset. The branch-owned shared-reference Scrut fixture now follows the merged test-entry reset convention.

Two committed fixture cases cover copy-only data (pass) and a real execution of that same Git-consuming library by the copier without a reset (fail, including indirect callers). Exact Scrut control passed. Omitting the literal-data exclusion failed with exit 50; suppressing library execution references failed with exit 50; restored control passed. An initial positive mutation suppressed only one canonical path and was ineffective because the same basename exists in both copies; the corrected plant suppresses both and goes red. The first test control also exposed the need for explicit pipefail before sort, now present so the positive case checks the failing status as well as diagnostics. All mutants are restored. Repository checker and targeted ShellCheck pass.

The checker fix is committed independently of the signed merge. Next is the explicitly requested focused Critical-only round on this merged tree, using five standalone read-only Codex aspects. Historical guidance remains Important, recorded and not taken under follow-up 674. No additional structural run is launched under the latest integration instruction. Fresh baseline Semgrep under the shell rule and final full checks follow.

## Merged-tree focused Critical-only round

All five standalone read-only aspects completed with exit 0, valid schema/nonempty replies and unchanged scope. Installed helper version 2.1.4 rendered and validated; Codex gpt-6.1-sol/high/872000 ran from the trusted Git checkout with no sandbox/trust override. No lasting changes found. Raw merged-focused-critical code/errors/tests/comments/types JSON is beside this ledger, copied only after the unchanged-snapshot check.

| Reviewer's label                                                 | Our severity                                                            | Take or record                                                             | Review again |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------ |
| important: omitted historical child guidance (code/errors/types) | Important, review quality is reduced without serious harm               | Record, not taken; existing follow-up 674 and explicit TOOLING disposition | No edits     |
| important: historical child-guidance tests (tests)               | Important, same known unresolved guidance behavior lacks child fixtures | Record with follow-up 674, without implementing its trust policy           | No edits     |
| important: historical child-guidance documentation (comments)    | Important, shipped reference does not state that known limitation       | Record with follow-up 674; PR body discloses the follow-up                 | No edits     |

No Critical finding and no behavior changes. Focused round ends **clean at Critical**, with the Important findings explicitly retained. No further round is launched. The narrow checker change received no additional finding. Fresh baseline Semgrep and integrated final checks follow before the non-force push.

## Fresh merged-tree Semgrep baseline

Semgrep 1.180.0 completed with exit 0 and zero findings against merge base a2e56c535ed6326cc8d531d945fbb6c627a9b335, in disposable shared clone /tmp/523-semgrep-merged.zsnrt0py/repo of e7d6dc59. Command: SEMGREP_REPO_NAME=cboone/agent-harness-plugins semgrep scan --config auto --baseline-commit a2e56c535ed6326cc8d531d945fbb6c627a9b335 --json --output /tmp/523-semgrep-merged.zsnrt0py/results.json. No metrics suppression, exclusions or full-scan substitute.

The scan ran 131 rules on 57 files and parsed approximately **77.3 percent** of lines. PartialParsing affects only shell files: bin/build-shared-references (58-59 and 78-79) and plugins/review-pr-with-codex/scripts/codex-aspects (body from line 3). Targeted ShellCheck passed on both with exit 0. No other parsing error was reported. The scan counts under the explicit shell-only partial-parsing rule, with incomplete shell parse coverage disclosed. Concise diagnostics are merged-semgrep-diagnostics.json beside this ledger; full output/log remains in the disposable scan directory. Integrated lint-and-fix --no-push, make test-all and version checks follow. Pushed history remains intact; no further tidy rewrite is performed.

## Integrated final checks and push

The integrated make test-all command exited 0: all **44 Scrut documents passed**, with no failed/skipped testcases. Full output is /tmp/523-merged-final-test-all.log. This includes the narrow checker's positive/negative cases, shared reference generation, recursive submodule/consumer fixtures, historical scope/aspect checks and inherited main suites. Lint-and-fix --no-push completed successfully: no additional source formatting fixes, no unresolved/skipped required checks; Markdownlint/Prettier remained check-only for protected snapshots/generated files, ShellCheck/shfmt/Actionlint passed, and repository validators/build consistency passed.

The repository check-versions skill was repeated after fetching origin/main. Against actual merge base a2e56c535ed6326cc8d531d945fbb6c627a9b335, intended bumps remain review-until-clean 3.2.0 to 3.3.0 and review-pr-with-codex 2.1.4 to 2.2.0. All 60 catalog entries/directories, valid manifest versions and present Codex manifest copies agree, with no marketplace duplicate version state. Structured evidence: /tmp/523-merged-version-report.json.

The signed main merge and separate narrow checker fix preserve published history. No further tidy rewrite is performed. Push is authorized by TOOLING's through-PR instruction; PR 675 is ready for review and cites follow-up 674. CI and mergeability will be observed after the push. Copilot remains paused and TOOLING alone merges. The final review précis must include retained Important guidance findings and the shell parse-coverage limit.

## CI stop: recurring option-like operand in fixture

CI run 40808118209 on pushed head 606deef13cf03f8e444c0c9f156e71526af664c7 completed with 44 passing checks and two failed documents. The recursive consumer case symlink-option fails at the fixture ln call: link_path is -vendor/new-link and ln passes it directly as an operand. Linux ln reports unexpected argument -e. The macOS run passed, so local success did not establish fixture portability. Failed-job output: /tmp/523-ci-failures.log.

- **Reviewer's label:** CI failure, recursive option-like checkout/untracked symlink fixture.
- **Our severity:** Important. Required CI and the combined boundary regression cannot complete on Linux; no new production harm is established.
- **Take or record:** Take pending the explicit operand recurrence decision. Stop under TOOLING's standing rule; no fix is applied. Proposed narrow direction is a rooted fixture filesystem operand while retaining relative JSON strings.
- **Review again:** A fixture-only correction changes no production behavior; preserve completed review counts and TOOLING's continuation decision. Overall state is **stopped: recurring defect**.

The other failed document is manage-resource-claims.md at its parallel-claims case: expected resource=logic is missing, while resource=simulator remains. This branch does not change resource-claims production code or that testcase. Report the observation to TOOLING for its owning workstream; no cause or flaky classification is inferred and no fix/retry is applied.

The CI watch has ended; no background process remains. Keep the PR open and ready for review but explicitly failing checks. This record is committed locally without a retry push at the stopped gate.
