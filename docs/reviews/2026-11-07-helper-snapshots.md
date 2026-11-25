# Helper snapshot review ledger

The helper snapshot launcher lands separately as #729 piece B on branch
`fix/729-helper-snapshots`.

Helper snapshot work resumed on the relayed design decision in message `75167f86-3a0b-4652-af52-ab12b12dcfea`. Implementation starts from frozen `00e115d6`, retaining the stopped records and review counts. Worker: `729-helper-snapshots`; conductor: TOOLING; profile: Codex `normal-max-default`. Verification and the remaining local order are pending.

## Evidence and launch history

The restart plant gate was verified against the frozen tree before this record was written. Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/plants-1/gate/receipt.json`. Its declared checks run and render `helper-snapshot-plants.json`. The producing runner remains the worker's complete installed **plant-defects 1.3.0** copy under `worker/helpers/plant-defects`, checked against its separate SHA-256/mode manifest before every invocation. Existing receipts remain with that copy.

The initial structural launches had no prepared prompt and reached no repository reading. TOOLING authorized corrected launches in message `a63a7ea5-348c-4b8f-a7df-b9eff1058972`, treating the malformed attempts as no review round. The corrected launches used the frozen head above, base `0c91d2cefc254ee02da8dafb31424fc93ca63f3c`, successful scope collection, nonempty prompts and SHA-256 records checked in each strict launch. Both used Codex `gpt-6.1-sol`, high effort, window `872000`, read-only, from the worktree with closed stdin and no trust-bypass flag. Raw output is preserved in the adjacent structural JSON records. The simplify aspect used its four inline cleanup angles and reported only.

## Structural loop: Nit round

| Finding                                                     | Reviewer's label | Our severity and impact                                                                              | Take or record                                                    | Review again                            |
| ----------------------------------------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | --------------------------------------- |
| A1: inherited identity is not bound to the executing bundle | important        | Important: another bundle can stamp and render evidence as the verified producer                     | Implemented under TOOLING's design call; verification pending     | Yes; changes verification behavior      |
| A2: producer-bound scope hash breaks reviewer composition   | important        | Important: identical repository inputs receive different IDs across the documented loop and reviewer | Implemented under TOOLING's design call; verification pending     | Yes; changes scope and result contracts |
| A3: remaining direct-cache helper instructions              | important        | Important: concrete instructions bypass snapshot verification and retain removable cache paths       | Take                                                              | Docs alone require no additional round  |
| A4: stale direct-Bash permission examples                   | nit              | Nit: examples no longer describe the new invocation                                                  | Take; own-change documentation                                    | Docs alone require no additional round  |
| S1: repeated invocation-identity comparison                 | suggestion       | Nit: duplicate parsing and comparison maintenance                                                    | Take; local consolidation preserving both verification boundaries | No behavioral change                    |
| S2: repeated creation-record shape assertions               | suggestion       | Nit: callers repeat checks guaranteed by the guarded parser                                          | Take; remove redundant assertions                                 | Tests only                              |

The structural loop remains open at Nit. No finding has been declared fixed by a final review. No end-state claim is made. TOOLING approved A1, A2 and the routine takes in message `d1872eae-d36f-4c3a-97a9-4f701142d6ef`. The code and documentation corrections are committed through `cd4559a8`, awaiting planted evidence and the next structural review. The next eligible round is Important after behavioral fixes, with counts preserved.

## Independent validation and remaining work

`make validate` failed in `bin/check-fixture-environments`: the new extensionless Python launcher needs named non-Bash classifications in `bin/lib/error-output-policy.json`. The captured output is `worker/validate-1.log`; the unified tool reported failure. Classification fixes are within scope. Standalone snapshot and legacy helper checks have captured output, but this record makes no receipt-backed pass claim for them.

Focused review, trims, disposable-clone Semgrep baseline, final lint without push, signed tidy and exact-tree comparison, version checking, current-main inclusion and the final locked full suite remain. No full suite has run. No PR, tag, activation, live cache change or hook change has been made. Version-bump merging remains with TOOLING after its CONDUCTOR hold check.

## Approved structural corrections

A1 binds the executing helper root to the verified copy, refuses partial or empty snapshot contexts, clears fixture context and rejects unbundled aspect references. A2 keeps repository identity independent of producer metadata at every submodule depth; scopes and aspect replies carry separate provenance, checked by validation and editing gates. Missing aspect provenance is refused by a named error in snapshot mode and remains accepted for direct legacy invocations. A3 and A4 replace remaining direct-cache commands and leave verified-launcher permissions manual. S1 consolidates the identity comparison while retaining both verification boundaries; S2 removes assertions already guaranteed by the guarded creation-record parser.

The expanded plant attempt at `4dd5774b` was refused: its cache-path mutant was stopped by the new executing-root guard before the declared release-survival assertion. Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/plants-2/gate/receipt.json`. The fix-removal mutant now removes routing and its context handoff together, reproducing the original behavior; its matcher is unchanged. The release test retains child diagnostics on a missing handshake and names both post-release execution and rendering failures as release-survival failures. The partial-context audit was completed in this same Nit fix stage before starting the Important round.

Captured failed gate output follows. No result from this attempt is credited as a plant pass.

```text
Check 1: exit 1; exited; argv ["uv", "run", "--no-project", "python", "/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/owned-helper.py", "plant-defects", "scripts/checked-plant", "run", "/Users/ctm/Work/projects/tooling/agent-harness-plugins/729-helper-snapshots/helper-snapshot-plants.json", "/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/plants-2/plants"]; cause null.
Check 2: exit 1; exited; argv ["uv", "run", "--no-project", "python", "/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/owned-helper.py", "plant-defects", "scripts/checked-plant", "render", "/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/plants-2/plants/results.json", "--ledger", "/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/plants-2/plants.md", "--status", "/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/plants-2/plant-status.md"]; cause null.
Action: exit None; not-run; refused True; cause "ValueError: check failed, incomplete or unrun"; argv ["/Users/ctm/Work/sl-vf/bin/mailbox-post", "report", "--file", "/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/plants-2/report.md"]; command cause "not attempted".
```

## Structural loop: Important round 1

The frozen round at `3f0993a4` ends **stopped: recurring defect**. Both raw reviewer reports are preserved beside this ledger. The same explicit read-only settings, frozen-base discipline and strict prompt preflight were used. Output shape and scope validation were verified against that frozen tree before recording this section: `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/important1-validation/gate/receipt.json`. A prior mailbox sentence about validation was unverified; the subsequent checked post carries this receipt.

| Finding                                                               | Reviewer label | Our severity and impact                                                  | Take or record                                | Review again                                                |
| --------------------------------------------------------------------- | -------------- | ------------------------------------------------------------------------ | --------------------------------------------- | ----------------------------------------------------------- |
| R1-A1: verifier symlink lends the snapshot identity to another caller | important      | Important: the running entry and core can still come from another bundle | Take under TOOLING structural call `3b83b14f` | Yes; caller membership changes verification behavior        |
| R1-A3: link discovery directly invokes review_scope_bin               | important      | Important: the parent shell can bypass snapshot verification             | Take under TOOLING structural call `739fc52d` | Yes; extend instruction validation with the docs correction |
| R1-S2: snapshot type assertion repeats the guarded parser             | suggestion     | Nit: the caller repeats a guaranteed shape check                         | Take the local removal                        | Tests only; no independent additional round                 |

An independent checked regression reproduces R1-A1 at its named `caller-path-refusal` assertion. Failed receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/caller-path-repro/gate/receipt.json`. It changes only disposable input copies, never the workspace or installed caches.

The declared expanded restart plants and green control have verified evidence at the frozen tree: `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/plants-3/gate/receipt.json`. This establishes those declared checks, not closure of the newly found caller-path gap and not final-head merge evidence. The producing bundle remains owned plant-defects 1.3.0.

TOOLING approved a mandatory explicit caller path: Python passes its own **file**; Bash passes BASH_SOURCE[0], including for sibling lookup. The shared check must establish regular nonsymlinked caller and verifier membership, resolved paths, content hashes, device and inode before sibling loads. Cover verifier symlink, direct entry symlink, parent symlink, caller-membership removal and valid controls. Another executing-identity instance requires a design decision for Chris through TOOLING.

TOOLING also approved extending existing validation rule 18 across every helper example and alias in the six skills, their references and READMEs, while permitting snapshot bootstrap. Plant old direct-cache and review_scope_bin examples as refusals, with the verified form as control. Align the scoped helper instruction. The next structural round is **Important 2**, with counts preserved.

Deferred by TOOLING: a general fixture-preflight check for redundant shape assertions is fragile and outside this brief. Record it for possible follow-up; no issue is filed. The local redundant assertion is taken without adding that general check.

## Important 1 corrective implementation

The approved caller correction now requires an explicit entry path from Python `__file__` or Bash `BASH_SOURCE[0]`. The verifier checks caller and verifier membership, nonsymlinked path components, SHA-256, modes, device and inode against the verified inventory before sibling loads. Bash sibling locators use the same source path. Regression cases cover verifier and entry symlinks, symlinked parents, hardlinked external entries, caller membership, inode replacement and valid sourced Bash callers.

The instruction audit replaces direct helper commands throughout the six consumers. Existing validation rule 18 now checks Bash fences and inline commands for direct paths and known executable aliases. Separate invocation plants remove this guard, requiring both direct-cache and alias assertions to fail while the verified command remains accepted. The existing plant preflight supports both manifests. The first copied invocation baseline failed because regular-file inputs omitted repository instruction aliases; its captured output is `worker/invocation-preflight-4.log`, and no gated plant ran from it. A copy-only setup now restores those aliases without changing live caches or the repository's aliases. Baseline and preflight outputs are unverified until receipt-backed checks are recorded.

The remaining redundant parser assertion was removed. The general redundant-assertion preflight proposal remains deferred. These changes await the declared plants and structural Important 2; no closure claim is made yet.

## Structural loop: Important round 2

The structural loop ends **clean at Important** on frozen `00e115d6`. Both anti-patterns and report-only simplify returned no findings. Completion, single JSON output, schema, recorded scope and no lasting review-input changes are covered by `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/important2-validation/gate/receipt.json`, verified against that clean tree before this entry. Raw outputs are preserved beside this ledger. The explicit Codex settings and strict frozen prompt preflight were unchanged. This is the structural review's result, not closure of the later focused findings.

## Focused loop: Nit round

The focused loop ends **stopped: recurring defect**. Code, errors, tests, comments and types ran on the same frozen head through fresh read-only Codex contexts, model `gpt-6.1-sol`, high effort and window `872000`. Prompt generation retained the captured SHA base and configured `CLAUDE.md` fallback. Every launch checked its committed clean head, nonempty prompt/schema and prompt hash in its strict call, with stdin closed and no trust-bypass flag. No repository code or tests ran inside the reviewers.

Completion/output validation and unchanged review-input scope are covered by `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/focused-nit-validation/gate/receipt.json`, verified against the clean frozen tree before recording. Raw aspect replies are preserved beside this ledger. Types returned no findings. Code and errors' conditional-source findings are one mechanism.

| Finding                                                           | Reviewer's label           | Our severity and impact                                                                                                                                 | Take or record                                                                         | Review again                                                  |
| ----------------------------------------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| F1: conditional sourcing continues after failed Bash verification | important, code and errors | Important: Bash suppresses errexit inside conditional sourcing, allowing a refused foreign caller to load sibling code and publish inherited provenance | Take only after the required design decision for the third executing-identity instance | Yes; explicit failure propagation changes behavior            |
| F2: verification refusal enters the ordinary Codex fallback       | important, errors          | Important: a rejected bundle's references can still drive review or trim fallback                                                                       | Take after the instruction recurrence decision                                         | Yes; terminal refusal changes control flow                    |
| F3: direct Git-library sourcing bypasses invocation verification  | important, comments        | Important: documented parent-shell sourcing loads a changed unguarded review-git library after prior verification                                       | Take after the instruction recurrence decision                                         | Yes; moving source/use inside verified exec changes execution |
| F4: wrapped Codex command escapes safety-setting validation       | important, code            | Important: rule 23's anchored recognizer no longer sees the wrapped command, so missing mandatory review settings are undetected                        | Take after the design gate; preserve the existing recognizer where possible            | Yes; restoring validator coverage changes behavior            |
| F5: checked-plant has no cross-bundle render regression           | important, tests           | Important: the required producer boundary lacks direct sensitivity coverage; the checked-gate regression does not cover it                              | Take after restart, including guard-removal plant and valid producer control           | Tests alone do not authorize another round                    |
| F6: validator comment omits legacy schema acceptance              | suggestion, comments       | Nit: the schema-equivalence comment hides a deliberate compatibility exception                                                                          | Take local wording after restart                                                       | Comments alone do not authorize another round                 |

F1 is the third executing-identity instance named in TOOLING's prior approval. Stop report `000014` and merged findings report `000015` went to TOOLING. TOOLING accepted the stop in message `9f4f9245-87a7-40ba-8b58-7dde2a028096`, requiring the design decision from Chris (he/him) in the Inbox. No finding was fixed, no new review started and no continuation was inferred. The same call asked for the existing plant gate to finish, this record to be committed, and the session to idle with its worktree kept.

The proposed directions are explicit terminal propagation in every Bash guard, terminal verification refusal before fallback, verified child-shell use of the Git library, and restoring mandatory-setting recognition with planted coverage. These are proposals for the decision, not implemented changes. The full focused loop retains its Nit count; any authorized behavioral corrections advance to Important. Trims, baseline Semgrep, final lint/tidy, version verification, current-main inclusion, locked full suite and ready PR remain unrun.

### Stop scope and restart evidence

TOOLING owns this stop. Affected paths are the Bash entry guards in `codex-aspects`, both `review-scope` copies and `check-edit-worktree`; the shared review/trim Codex fallback reference; both direct Git-library sourcing instructions; and recognition of the wrapped Codex command's mandatory settings. No new starts or restarts on those failing paths are authorized by this record. Corrective work resumes only through the named design and restart gate.

The proposed restart evidence is a named conditional-source refusal plant, verification-failure fallback refusal, tampered library-source refusal, wrapped-command missing-setting refusal, and checked-plant producer-mismatch refusal, each with a valid-case control. Every plant must use copied-load/fixture-validity preflight and checked-plant inside checked-gate. TOOLING records the approved structural design and the proof that every affected path rejects the invalid case and permits its valid case before lifting this stop. The prior declared plants do not substitute for those checks.

## Declared corrective plants at the stopped head

The declared snapshot and invocation plants executed and rendered on frozen `00e115d6`. Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/plants-4/gate/receipt.json`, verified against that clean tree before this entry. The gate's action posted the result to TOOLING. Its producing runner remains the owned installed plant-defects **1.3.0** copy and external SHA-256/mode manifest.

The copied-load and fixture-validity preflights ran each unchanged disposable baseline before the gated plants. The snapshot manifest covers release-mid-task cache removal/replacement, bytes and mode tampering, caller membership/inode, context forms, scope/provenance and reference boundaries with its green control. The invocation manifest removes the existing instruction guard and reaches both named direct-cache and executable-alias refusal assertions, with a verified invocation control. The disposable setup recreates instruction aliases inside the copy. Live caches were never modified.

This evidence covers those declared variants only. It does not test the newly reported conditional-source refusal, fallback handling, direct library sourcing, wrapped-command recognizer or checked-plant cross-producer sensitivity gap. It neither closes the focused findings nor lifts their stop. No final-head full suite or merge evidence is claimed.

## Approved restart: explicit guard stops

TOOLING relayed the Inbox decision at 8:14 AM EST: explicit stops at every guard, enforced by validation. The restart opens these corrections and their necessary checks through a ready PR. No tag, activation, hook or live-cache boundary is open. Current main was merged with signed commit `4555603b`; both independent fixture case additions were retained. Dependency restoration used the immutable lockfile without changing it.

The class audit covers script guards in `codex-aspects`, both `review-scope` files and `check-edit-worktree`; both generated Git-library copies and their script load sites; direct-loading instructions in the PR skill and loop reviewer reference; the canonical review/trim fallback reference; and rule 23 recognition of the wrapped command. Script guards and loads use explicit `|| exit 1`; loaded library guards use `|| return`, including partial contexts. Library callers and verifiers retain their existing complete-bundle checks. The documented child-shell loader uses this same guarded library, with no separate snapshot implementation.

Launcher refusal has reserved status 78, which is terminal even when a backend happens to return it. This preserves backend/reply fallback after successful verification. The regression changes a private snapshot between preverification and exec; backend success and backend failure remain controls. Rule 23 sees literal `codex exec` on its continuation line. The direct checked-plant producer-mismatch regression checks valid rendering and unchanged ledger/status destinations after refusal. The compatibility comment records intentional legacy replies.

The explicit guard validator checks both a missing guard and unguarded calls. Its cases cover every entry, both library copies and all script library-load sites. Restart plants use an isolated named unittest judge per mutation, with unchanged controls. Generated manifests and wrappers have dated review-fixture paths. Earlier manifests are retained with dated names; their historic receipts still refer to their old names. Every added manifest will be registered in `tests/data/checked-verdict-compatibility.json` from captured baseline, red and restored rows before the final suite.

The next focused round is Important, retaining the Nit findings and counts. No new structural round is implied; any future step 1 uses the four read-only cleanup reviewers, never the simplify selection, under interim (n). Heavy checks join once under one outer suite-lock waiter, with the gate deadline starting only after acquisition. All preflight and baseline outputs during implementation are unverified; no restart-check closure is claimed here.

## Fixture-phase audit

TOOLING directive `b674cd7b` requires the selected test body to own each red assertion. The pending heavy waiter was stopped before acquisition for this test-data correction; no gated attempt from that launch is claimed. `BodyOnlyResult` now credits an assertion only when its traceback includes the selected method and excludes fixture phases. Other assertions become errors, including subtests. Real unittest controls cover setup, teardown, cleanup, class fixtures and async fixtures with the same assertion marker; ordinary body and body-subtest assertions remain failures. A dedicated weakening plant removes this classification and must reach the named fixture-phase assertion. Both plant suites import the shared result helper from declared copied inputs. Invocation setup and unexpected process statuses raise errors.

The unchanged copied fixture-phase baseline and standalone judge controls completed in the strict call writing this entry. Their output is in the worker's `fixture-phase-preflight.log`. The historical `plants-4` red tracebacks were audited for actual selected-method frames and fixture-phase frames in that same call; the derived audit is `worker/fixture-phase-historical-audit.json` in the mailbox state. No affected historical red was identified. This audit does not turn those historical receipts into evidence for the current tree. Review counts and the next focused Important round remain unchanged. No restart closure is claimed until the new gated plants complete.

## Corrective plants before the replacement contract rule

The isolated corrective plants ran and rendered on `a8ae4b12`. Receipt `worker/resume-plants-2/gate/receipt.json` in mailbox state was verified against the clean current tree in the same strict call writing this entry. The producing runner is the unchanged owned plant-defects 1.3.0 bundle. Captured baseline, red and restored rows are registered in the compatibility fixture. A same-call ps observation found no survivors in the run's recorded process groups; the derived observation is `worker/resume-plants-2/survivors.json`.

TOOLING message `1a2016a5` replaces the fixture-phase rule with contract-only assertions. The traceback classifier is therefore being replaced with explicit non-assertion prerequisites. This completed gate is historical evidence for its tree, not closure of that replacement audit or the final restart gate. Verified receipts stand unless the audit identifies an actual prerequisite-origin credited red. Review counts remain unchanged.

## Contract-only assertion audit

The replacement rule removes `BodyOnlyResult` entirely. Both judges use plain unittest results. The shared test helper now has one operation: a false prerequisite raises `RuntimeError`. No traceback-name filtering remains. Snapshot acquisition, Git setup, copied-document anchors, artifact-read shape guards, release handshake/deadlines, child-entry and stub resolution are prerequisites, including when called inside a test body. Producer-evidence preparation and documented backend controls also use that error channel. Invocation's valid setup and unexpected validator exits already raise errors. Remaining assertions check the subject's exit status, output, identity or promised destinations. Real controls exercise prerequisite errors in bodies, subtests, fixtures, class fixtures, cleanup and async fixtures, alongside a contract assertion failure. The existing isolated fixture-phase plant now weakens the prerequisite exception type; its selected contract judge must distinguish errors from failures without inspecting traceback words.

The standalone controls and unchanged copied baseline completed in the strict call writing this entry. The latest captured red traces were inspected: helper behavior plants reach their intended refusal/survival assertions, rather than acquisition, Git, deadline or harness prerequisites. The classifier plant is historical evidence of the superseded classifier's contract, not evidence for the replacement helper. No affected credited helper-behavior red was identified. The updated plants must run again before restart closure. Review counts are unchanged, and focused Important round 1 remains next.

## Contract-only corrective plant evidence

The updated isolated corrective plants ran and rendered on `bbf22fd5`. Receipt `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/resume-plants-3/gate/receipt.json` was verified against the clean tree in the same strict call writing this entry and refreshing the compatibility captures. All invocations used the unchanged owned plant-defects 1.3.0 bundle, verified for SHA-256 and mode. The copied-load and unchanged-baseline preflights preceded the gate. The prerequisite exception-type weakening reaches the selected test's contract assertion without traceback filtering. Same-call ps inspection found no survivors in recorded groups; its derived observation is `worker/resume-plants-3/survivors.json` in mailbox state.

TOOLING relayed the class-audit and harness-evidence rules in message `186ce3c4`, effective from the next review round. Any new recurrence requires approval of the mechanism class, a full touched-file and diff audit with each site ledgered, a plant at each changed behavioral site, and claim-to-proof mapping for prose. The upcoming focused Important round retains all prior counts and must stop on recurrence. These receipts are evidence for their recorded tree; final merge evidence still requires the final PR head and current main inclusion.

## Focused review, Important round 1: stopped on fallback recurrence

The five focused aspects reviewed frozen `5d10a97e` against literal merge-base `858d11626970ae003f791cb0b0095d190fdcb436`. The documented owned `codex-aspects run` used `gpt-6.1-sol`, high effort, window 872000, read-only sandbox, approval never and web search disabled. All prompts and the schema were rendered and hashed before launch; the saved run inputs matched those bytes. The collector checks process exits, nonempty replies, helper schema validation, aspect statuses and unchanged scope. Completion receipt `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/focused-important1/validation-gate/receipt.json` was verified against the clean frozen tree in the same strict call writing this entry. Raw replies are preserved beside this ledger. Code, tests, comments and types reported no findings; errors reported the recurrence below. Runtime tests were not part of this read-only review.

| Finding                                              | Reviewer's label | Our severity and impact                                                                                                                                                                                                                             | Take or record                                                    | Review again                                                                                                                                 |
| ---------------------------------------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| F7: launcher startup failures reach backend fallback | `important`      | Important: deletion or invalidity of the launcher between preverification and exec can make uv or Python return 1 or 2 before launcher code runs. The handler terminates only for 78 and permits fallback to use the invalid snapshot's references. | Take after the required mechanism-class approval; no fix applied. | Yes if approved: correcting fallback control flow changes behavior. The next focused round would be Important round 2, with counts retained. |

This is another instance of F2's verification-failure fallback mechanism. The canonical `codex-exec.md` handler was inspected: its nonzero branch rejects only status 78, while the launcher can assign that status only after Python starts its code. No impact-label downgrade is proposed. The loop ends **stopped: recurring defect**. No trim, Semgrep, lint/tidy, push or PR follows this stop.

### Proposed class audit for TOOLING's approval

Name the class as **launcher lifecycle failures being misclassified as verified backend failures**. The audit must cover every touched file and the full diff, not only the handler site. Candidate behavioral sites are the canonical anti-pattern Codex wrapper, its generated trim consumers, `helper-snapshot`'s startup/exec/refusal boundary, review and checked-runner entry guards, and any other nonzero path that can consume snapshot references or render results. The canonical wrapper and its generated copies are the confirmed affected sites; the remaining candidate paths require the full audit before a closure claim.

The proposed correction is an explicit pinned-bundle verification before any nonzero-run fallback is allowed, with failure terminal even when the launcher cannot start. The audit must preserve valid backend and reply fallback behavior. Plant deletion and invalidity of the launcher between preverification and exec, retain the existing changed-bundle refusal plant and valid backend controls, and plant each additional changed behavioral site identified by the approved audit. Every plant uses disposable copies, contract-only assertions and checked-plant inside checked-gate under the heavy lock. List every checked site and map every touched prose claim to its test or plant. This is a proposed design, not an implemented fix or a completed class audit. TOOLING owns the decision and restart gate.

## Approved lifecycle correction: design distinction found during audit

TOOLING approved the class and restart in message `069ae673`: launcher lifecycle failures misclassified as verified backend failures. The approved re-verification guard is prepared in the canonical Codex wrapper and regenerated into both trim consumers. Contract-only tests now execute each consumer's actual block with private launcher deletion and invalidity between preverification and exec; the existing changed-bundle refusal, backend-failure and valid-reply controls remain. Separate deletion and invalidity guard-removal manifests target each changed consumer. These are prepared fixtures, not executed plant evidence. Their new compatibility captures are pending execution.

The full-file search inventory is [Launcher lifecycle class search inventory](./2026-11-08-helper-launcher-class-audit.md). It covers tracked diff membership and records every searched file and keyword site. It is not the completed class audit. Confirmed classifier sites are the canonical wrapper and the generated trim references. The shared launcher assigns status 78 only after Python starts, while entry guards terminate without a backend fallback. Other fallback mentions concern guide selection, optional dependencies, review execution modes, compatibility or historical evidence.

A design distinction remains: re-verification cannot distinguish a transient uv/Python startup failure from a backend failure when the pinned bundle stays valid and the second verification invocation succeeds. The prepared handler would still allow fallback in that case, although the approved class says every failure before launcher code runs must be terminal. This is static control-flow analysis; no probe or timed test ran for it. A per-invocation backend-start record, or equivalent positive provenance, is needed to distinguish these paths while preserving backend fallback. That is additional protocol design beyond the approved re-verification-only proposal, so corrective execution stops for TOOLING's decision. No such protocol has been implemented, no new review round has started, and Important round 2 remains next after the correction and audit are complete.

## Nonce protocol approved and prepared

TOOLING message `530ef8f1` approves positive per-invocation launcher evidence as well as pinned-bundle verification. The caller now reserves a fresh private directory and random nonce, retaining the nonce in an exclusive caller record outside the directory. `exec-recorded` writes a start marker first, verifies the bundle, runs the backend, then records its normal status and producer identity. `allow-fallback` requires the current nonce and exact status; missing, stale, foreign, malformed or non-private records are refused. A completed successful backend additionally needs a caller-classified reply-failure record. Status 78 remains terminal. The implementation remains in the shared helper; generated consumers contain no separate copy of its protocol logic.

The [full class audit](./2026-11-08-helper-launcher-class-audit.md) records each behavioral site, every touched file searched, and a claim-to-proof map. Deletion, invalidity and transient startup have independent guard-removal plants at each wrapper consumer. Shared protocol guard plants cover stale/missing evidence, privacy, freshness, nonce format, backend identity/status, signal completion, reserved status and reply records. Test prerequisites use non-assertion errors. The transient uv stub delegates real calls and supplies one real-contract nonzero startup result, with a checked own-stub path and injection marker. All mutations remain disposable and use no DEBUG instrumentation or live caches.

These are prepared changes and proof definitions. The new preflights, plants and compatibility captures have not run. No class-closure or current-head check result is claimed. The next focused round is Important round 2 after the planted proof, with all prior counts retained.

## Nonce protocol planted proof

The declared isolated plants and their renders completed on frozen `083b7bce`, including each wrapper consumer's deletion, invalidity and transient-startup case, the earlier-invocation stale-marker case, shared protocol guards and evidence-command validation. Receipt `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/nonce-plants-1/gate/receipt.json` was verified against the clean frozen tree in the same strict call writing this entry and refreshing all added compatibility rows from actual baseline, red and restored output. The copied-load and unchanged-baseline preflights ran under the same outer heavy lock before the gate. The producing checked helpers remain the owned plant-defects 1.3.0 copy, verified for SHA-256 and mode on every invocation.

The result went to TOOLING as the action of `worker/nonce-plants-1/result-post/receipt.json`, which verified the source receipt and observed recorded process groups. Its observation is `worker/nonce-plants-1/survivors.json`: no current matching groups, no unresolved groups and all original groups recorded gone. No other session's process was signalled. The class-audit site inventory and claim-to-proof map now point to this planted evidence. No final-head or full-suite merge claim is made. Focused Important round 2 follows with the retained counts; any recurrence stops that loop.

## Focused review, Important round 2: producer-boundary coverage recurrence

The requested focused aspects reviewed frozen `9f5b354a` through the same owned review-pr-with-codex 2.3.5 bundle and documented standalone entry point. Settings remained `gpt-6.1-sol`, high effort, window 872000, read-only, approval never and web search disabled. All requested aspects completed with valid output; exact prompt/schema equality and unchanged scope were checked by the prepared collector. Receipt `/Users/ctm/.local/state/codex-mailboxes/tooling/729-helper-snapshots/worker/focused-important2/validation-gate/receipt.json` was verified against the clean frozen tree in the same strict call writing this record and saving the raw replies. The replies are preserved beside this ledger with the focused-important2 prefix. Code, errors, comments and types reported no findings. Tests reported the Important coverage gap below. No runtime test was part of this review.

| Finding                                                              | Reviewer's label | Our severity and impact                                                                                                                                                                                                                                                                                                                                                                      | Take or record                                                 | Review again                                                                                                                                                      |
| -------------------------------------------------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F8: foreign scope producer rejection lacks a direct sensitivity test | `important`      | Important: `require_scope_file` enforces a distinct producer boundary, but the existing result-provenance test always supplies the current producer's scope. Removing that guard could allow validation or gate eligibility with a foreign scope and valid current-producer reply while existing tests remain green. Equal repository IDs deliberately do not prove equal producer identity. | Take after the mechanism-class audit decision; no fix applied. | Tests alone do not authorize another round. If the audit changes production behavior, counts advance from this completed Important round to Critical-only review. |

Source inspection confirms the guard exists and the test always uses `current["scope_path"]`. This is another instance of F5's missing independent cross-producer boundary sensitivity coverage. No label downgrade is proposed. The loop ends **stopped: recurring defect**; Important round 2 is consumed and is never reset. No trim, Semgrep, lint/tidy, push or PR follows this stop.

### Proposed producer-boundary class audit

Approve the class as **producer-identity enforcement boundaries lacking independent cross-bundle sensitivity coverage**. Search the full diff and every touched file for each producer check and every input it validates; ledger every site, its valid same-producer control, foreign-producer refusal test and guard-removal plant. Candidate sites include scope acceptance in aspect validation, prompting, execution, changes and both gate scope arguments; reply/result producer checks; checked receipt and plant render/verify boundaries; and the nonce protocol's recorded backend producer check. The inventory must distinguish shared predicates from separate enforcement sites and map each prose claim to its proof.

The immediate proposed correction uses the existing two captures, with otherwise valid current-producer replies and equal repository identity, to reject a foreign scope during validation and when either gate scope is foreign. Retain valid current-scope controls and plant removal of the scope producer guard. The approved audit decides the remaining sites and tests before changes are made. This is a proposal, not a completed audit. TOOLING owns the mechanism decision and restart gate. A tests-only correction ends the loop with “ended: fixes changed no behavior”; production changes would require the next Critical-only round.

## Producer class audit: status production gap found and corrected

TOOLING approved the producer-boundary class and restart in message `d5cbf067`. The [full class audit](./2026-11-08-helper-producer-class-audit.md) inventories each predicate and input, every touched file searched, controls/refusals/plants, and claim-to-proof mappings. Scope validation, prompting, execution, both gate arguments, changes and finish delegation now have direct foreign-producer sensitivity tests with equal repository identity. Receipt render and verify, plant rendering, invocation context, snapshot metadata and nonce backend producer checks have independent proof definitions too.

| Finding                                                                 | Reviewer's label                           | Our severity and impact                                                                                                                    | Take or record                                                                                                                                                                                                            | Review again                                                                                                           |
| ----------------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| F9: status producer identity absent from publication and both consumers | Class-audit finding, not reviewer-labelled | Important: another bundle's successful status could certify current-producer replies when membership matched, including cleanup rendering. | Take within the approved mechanism class: emit `helper_bundle` in aspect statuses and check it in review eligibility and cleanup rendering. Add actual cross-bundle, missing-field and direct legacy controls and plants. | Yes. This changes production behavior, so the next focused round is Critical-only; Important round 2 remains consumed. |

All other audited producer checks were present; their missing sensitivity tests are prepared. The new status field is producer-owned, emitted by native validation and standalone runs through the same status constructor. Snapshot mode refuses missing or foreign status producers; direct mode retains legacy absent/null producers. The committed Codex fixture now supports the real standalone invocation flags and valid schema-shaped fixture replies, with own-path resolution checks. Rendering cleanup prompts in tests starts no model and performs no edits. No fixed-bound tests have run outside the heavy lock.

Runtime proof for this correction is pending. New manifests will be registered from actual gated baseline/red/restored captures before the final full suite. The next gate runs copied-load and unchanged-baseline preflights and every isolated plant under one outer heavy lock. Then Critical-only review and the remaining local review order follow, with counts retained. No PR, tag or activation has occurred.

## Producer class planted proof

The isolated producer-boundary plants and their renders completed on frozen `874b56a3`. Receipt `worker/producer-plants-1/gate/receipt.json` was verified against the current clean tree in the same strict call writing this record and refreshing compatibility rows from actual baseline, red and restored output. Copied-load and unchanged-baseline preflights ran before the gate under the same outer heavy lock. The owned plant-defects 1.3.0 bundle wrote and verified the receipt.

The checked result post is `worker/producer-plants-1/result-post/receipt.json`. Its checks verify the source receipt and inspect recorded process groups; the observation is `worker/producer-plants-1/survivors.json`. This is correction evidence for the frozen head, not final PR-head merge evidence. Critical-only focused round 1 follows, with the earlier Important rounds retained.

## Focused review, Critical-only round 1

The focused review of frozen `5466d23585684f71c81a480bd58bccd6fde605f3` against literal merge base `858d11626970ae003f791cb0b0095d190fdcb436` ended **clean at Critical**. The validated replies report no findings. Raw replies are saved beside this ledger with the focused-critical1 prefix. Every selected aspect ran through the owned review-pr-with-codex 2.3.5 standalone entry point, using `gpt-6.1-sol`, high effort, window 872000, read-only sandbox, approval never and web disabled. Simplify was not selected in this focused loop.

Receipt `worker/focused-critical1/validation-gate/receipt.json` verifies completion, reply schema, exact prompt/schema equality and unchanged scope. It was verified against the current clean frozen tree in the same strict call saving these replies and this entry. No runtime test ran in this review. Earlier Nit and Important counts remain consumed; no count was reset. Trims, baseline Semgrep, lint/tidy and final exact-head validation remain.

## Comment and prose trims

Both report-only trim runs completed through owned trim-comments 3.0.1 and trim-text 1.3.1 instructions with `gpt-6.1-sol`, low effort, window 872000, read-only sandbox, approval never and web disabled. The completion receipt `worker/trims-1/gate/receipt.json` was verified against clean frozen `92547634` in the same strict call saving the reports and this entry. The trim replies are on `fix/729-helper-snapshots`.

Taken: remove the script count before the invocation examples; delete a README sentence repeating the surrounding permission explanation; rewrite the direct-capture comment; delete the different-producer receipt comment and the restart-selection comment, which repeat the following operations. The overlapping direct-capture proposal uses the comment review's clearer wording. No substantive proposal was declined. Generated shared copies and prose documents were outside the comment profile; shared copies were regenerated from their classified canonical sources. No production behavior changes. Source token preservation and final required checks remain pending.

## Baseline Semgrep

Baseline Semgrep output validation completed: {"findings": 0, "errors": 0, "scanned_paths": 309}. Scan configuration p/ci, --baseline-commit 858d11626970ae003f791cb0b0095d190fdcb436, disposable shared clone, source head 8710da5f1f7cd0b770d56590e84979b361fc13cb. Checked receipt worker/semgrep-1/output-gate/receipt.json. Lint-and-fix --no-push, tidy and final exact-head gate remain. No PR, tag or activation.

The original scan launcher completed; output inspection is the check recorded here. The scan used strict JSON output and metrics off. The collector rejects any result, error or incomplete baseline marker. No full-scan-to-changed-line substitution was used.

## Final preparation

The lint-and-fix no-push workflow ran project formatting and rebuilt generated copies. Required lint and version checks are recorded in `worker/pre-suite-2/lint-gate/receipt.json`; its action writes this record and commits any formatting changes. Changed plugins and version comparisons are in `worker/pre-suite-2/versions.json`. No advisory language tools are inferred beyond project enforcement. No push occurs in this workflow.

The next steps rebuild unpublished history into signed logical commits with a backup and exact-tree comparison, then complete copied-load and unchanged-baseline preflights on that final tree under one outer heavy lock. The final suite and gated plants remain held by TOOLING until the repository load-flake stop is lifted. Final results remain external to the tree so a record commit cannot invalidate the exact-head receipt. A ready PR and its checked handoff follow only after completion.

## Merge with main

Signed merge `752c5995` combines `f5eaa963` with main at `a9bad10d`.

- The canonical plant-defects manifest uses `1.4.1`, the next patch above the branch's `1.4.0` and main's `1.3.2`. `make build` regenerated the conflicted Codex mirror. Both copies of `checked_core.py` include main's process inspection and cleanup changes and the branch's snapshot provenance.
- The compatibility fixture preserves 18 common rows, 207 branch additions and 15 main additions. The two sets of additions use distinct manifest names.
- The diff against main changes zero plugin `hooks/` paths and zero manifest `hooks` entries.

### Checks on the merged tree

- `make build`, the version and catalog check, and `make lint` each exited 0.
- The staged whitespace check exited 2 on three patch fixtures imported unchanged from main. The comparison against main for those fixtures and the whitespace check scoped to the merge resolutions each exited 0.
- `make validate` exited 2. Its fixture dependency check exited 1 and reported missing Git environment resets in `bin/build-review-checklists`, `tests/scrut/build-review-checklists.md`, `bin/validate-plugins` and `tests/fixtures/helper-invocation-setup`.
- In separate archived parent trees, `bin/check-fixture-environments` exited 1 with the same four diagnostics on `f5eaa963` and exited 0 on `a9bad10d`. The failure predates the merge.
- The Python judge, snapshot and invocation suites each exited 0 with 5, 70 and 10 tests respectively. The outer fixture reset was sourced from zsh, which reported that Bash's `compgen` was unavailable.
- The pre-existing validation failure stopped the recheck before the plant preflights and `checked-plant` runs. The final `make test-all` belongs to the merge receipt.

## Fixture environment reset and plant recheck

Commit `55c24070` sources `bin/lib/git-environment.bash` at the entry to
`bin/build-review-checklists`, `bin/validate-plugins`,
`tests/fixtures/helper-invocation-setup` and the first command in
`tests/scrut/build-review-checklists.md`. The Scrut edit is confined to that command line.

- `make build`, `make lint` and `make validate` each exited 0.
- `make test-scrut SCRUT_TEST_DIR=tests/scrut/build-review-checklists.md` exited 0 (27 cases).
- `uv run --no-project python tests/helper_snapshot_judge_test.py` exited 0 (5 tests).
- `uv run --no-project python tests/helper_snapshot_test.py` exited 0 (70 tests).
- `uv run --no-project python tests/helper_invocation_test.py` exited 0 (10 tests).
- The Python suites sourced the fixture reset from Bash under the heavy-suite lock.

The branch's plant-defects 1.4.1 runner processed 69 manifests under
the heavy-suite lock. Named red assertions exited 1 for 69 of
87 variants. Restored checks exited 0 for 70 of
87 variants. Green controls and their restores exited 0 for
68 of 69 controls.

Each row records the copied-load and baseline preflight, `checked-plant run`,
`checked-plant render` and the enclosing `checked-gate` exit. The legacy snapshot
manifest runs directly under the heavy-suite lock because its full-suite checks
can collectively exceed the gate's per-command deadline. Raw JSON receipts,
runner-rendered results and the batch exit list are in
`worker/fixture-reset.fa6goB/`.

The batch exited 1. All 68 enclosing gates exited 0, and their receipts
verified against the signed fix. The direct legacy snapshot run and render
each exited 1.

| Manifest                                                                     | Preflight | Run | Render | Gate   | Red  | Restored green | Green controls |
| ---------------------------------------------------------------------------- | --------- | --- | ------ | ------ | ---- | -------------- | -------------- |
| `2026-11-07-helper-invocation-direct-library-plants`                         | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-invocation-evidence-guard-plants`                         | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-invocation-guard-presence-plants`                         | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-invocation-library-guard-plants`                          | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-invocation-load-stop-plants`                              | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-invocation-plants`                                        | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-invocation-script-guard-plants`                           | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-invocation-wrapped-settings-plants`                       | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-backend-identity-plants`                         | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-backend-producer-plants`                         | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-backend-signal-plants`                           | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-backend-status-plants`                           | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-backend-verification-plants`                     | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-cache-path-plants`                               | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-cleanup-status-producer-foreign-plants`          | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-cleanup-status-producer-legacy-plants`           | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-cleanup-status-producer-missing-plants`          | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-conditional-source-plants`                       | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-context-producer-hash-plants`                    | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-context-producer-path-plants`                    | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-context-producer-plants`                         | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-core-producer-predicate-plants`                  | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-fixture-phase-plants`                            | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-fresh-invocation-plants`                         | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-gate-render-producer-plants`                     | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-gate-verify-producer-plants`                     | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-launcher-deletion-review-anti-patterns-plants`   | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-launcher-deletion-trim-comments-plants`          | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-launcher-deletion-trim-text-plants`              | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-launcher-invalidity-review-anti-patterns-plants` | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-launcher-invalidity-trim-comments-plants`        | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-launcher-invalidity-trim-text-plants`            | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-launcher-transient-review-anti-patterns-plants`  | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-launcher-transient-trim-comments-plants`         | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-launcher-transient-trim-text-plants`             | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-loaded-library-plants`                           | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-marker-shape-plants`                             | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-missing-backend-plants`                          | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-missing-marker-plants`                           | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-nonce-format-plants`                             | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-plant-producer-plants`                           | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-plants`                                          | 0         | 1   | 1      | direct | 1/19 | 2/19           | 0/1            |
| `2026-11-07-helper-snapshot-private-directory-plants`                        | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-private-record-plants`                           | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-reply-backend-status-plants`                     | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-reply-record-plants`                             | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-reply-record-shape-plants`                       | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-reserved-status-plants`                          | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-scope-producer-changes-after-plants`             | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-scope-producer-changes-before-plants`            | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-scope-producer-finish-after-plants`              | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-scope-producer-finish-before-plants`             | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-scope-producer-gate-after-plants`                | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-scope-producer-gate-before-plants`               | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-scope-producer-predicate-plants`                 | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-scope-producer-prompt-plants`                    | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-scope-producer-run-plants`                       | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-scope-producer-validate-plants`                  | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-snapshot-bytes-plants`                           | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-snapshot-modes-plants`                           | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-snapshot-producer-hash-plants`                   | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-snapshot-producer-version-plants`                | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-stale-marker-plants`                             | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-status-producer-emission-plants`                 | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-status-producer-foreign-plants`                  | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-status-producer-legacy-plants`                   | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-status-producer-missing-plants`                  | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-terminal-refusal-plants`                         | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |
| `2026-11-07-helper-snapshot-write-private-plants`                            | 0         | 0   | 0      | 0      | 1/1  | 1/1            | 1/1            |

### Legacy snapshot manifest failure

The `cache-path` variant exited 0 at baseline, 1 with its named assertion,
and 0 after restoration. The `snapshot-bytes` variant exited 0 at baseline
and after restoration. Its planted run exited 2 instead of the required 1.
It reached the named assertion, but the full suite also reported 31 fixture
errors, including valid launches rejected for a snapshot inventory mismatch.
`checked-plant` recorded a setup error and stopped before the remaining 17
variants and one green control. The isolated `snapshot-bytes` manifest passed
with red exit 1 and restored exit 0.

The four reset paths are absent from the legacy snapshot manifest's copied
inputs. The manifest and its patches were left as committed.

The legacy manifest now omits `snapshot-bytes`. Its patch makes the plant-defects
launcher hash every `README.md` as empty, which breaks the shared fixture
creation added when the suite expanded to 70 tests before the merge. The other
plugins' launchers reject the resulting inventories.

The `snapshot-bytes` variant in
`2026-11-07-helper-snapshot-snapshot-bytes-plants.json` uses the same patch and
passed in the recorded isolated run. The legacy manifest rerun is pending.

## Plant manifest reset dependency audit

Reviewed 87 `*-plants.json` files at `f5607e15`. The audit followed copied inputs,
check and setup entry points, and indirect callers of the four fixture reset
sites. Nine manifests need the reset library. The library sources no other files.

### Changed

- `2026-11-07-installed-checklist-drift-plants.json` now copies `bin/lib/git-environment.bash`.
  Its detector baseline ran once in a disposable directory with only the declared
  inputs, preserving their bytes and modes. The declared check, run with
  `bash -euo pipefail`, exited 0 and emitted both expected output lines, including
  `ASSERT: stale body rejected`. This run used neither the heavy-suite lock nor
  `checked-plant`.

### Already copies the library

The invocation manifests copy the reset library for their setup script and
the validator and checklist builder used by their fixtures.

- `2026-11-07-helper-invocation-direct-library-plants.json`
- `2026-11-07-helper-invocation-evidence-guard-plants.json`
- `2026-11-07-helper-invocation-guard-presence-plants.json`
- `2026-11-07-helper-invocation-library-guard-plants.json`
- `2026-11-07-helper-invocation-load-stop-plants.json`
- `2026-11-07-helper-invocation-plants.json`
- `2026-11-07-helper-invocation-script-guard-plants.json`
- `2026-11-07-helper-invocation-wrapped-settings-plants.json`

### No dependency on the four reset sites

- `2026-11-05-733-load-timeouts-plants.json`
- `2026-11-07-helper-snapshot-backend-identity-plants.json`
- `2026-11-07-helper-snapshot-backend-producer-plants.json`
- `2026-11-07-helper-snapshot-backend-signal-plants.json`
- `2026-11-07-helper-snapshot-backend-status-plants.json`
- `2026-11-07-helper-snapshot-backend-verification-plants.json`
- `2026-11-07-helper-snapshot-cache-path-plants.json`
- `2026-11-07-helper-snapshot-cleanup-status-producer-foreign-plants.json`
- `2026-11-07-helper-snapshot-cleanup-status-producer-legacy-plants.json`
- `2026-11-07-helper-snapshot-cleanup-status-producer-missing-plants.json`
- `2026-11-07-helper-snapshot-conditional-source-plants.json`
- `2026-11-07-helper-snapshot-context-producer-hash-plants.json`
- `2026-11-07-helper-snapshot-context-producer-path-plants.json`
- `2026-11-07-helper-snapshot-context-producer-plants.json`
- `2026-11-07-helper-snapshot-core-producer-predicate-plants.json`
- `2026-11-07-helper-snapshot-fixture-phase-plants.json`
- `2026-11-07-helper-snapshot-fresh-invocation-plants.json`
- `2026-11-07-helper-snapshot-gate-render-producer-plants.json`
- `2026-11-07-helper-snapshot-gate-verify-producer-plants.json`
- `2026-11-07-helper-snapshot-launcher-deletion-review-anti-patterns-plants.json`
- `2026-11-07-helper-snapshot-launcher-deletion-trim-comments-plants.json`
- `2026-11-07-helper-snapshot-launcher-deletion-trim-text-plants.json`
- `2026-11-07-helper-snapshot-launcher-invalidity-review-anti-patterns-plants.json`
- `2026-11-07-helper-snapshot-launcher-invalidity-trim-comments-plants.json`
- `2026-11-07-helper-snapshot-launcher-invalidity-trim-text-plants.json`
- `2026-11-07-helper-snapshot-launcher-transient-review-anti-patterns-plants.json`
- `2026-11-07-helper-snapshot-launcher-transient-trim-comments-plants.json`
- `2026-11-07-helper-snapshot-launcher-transient-trim-text-plants.json`
- `2026-11-07-helper-snapshot-loaded-library-plants.json`
- `2026-11-07-helper-snapshot-marker-shape-plants.json`
- `2026-11-07-helper-snapshot-missing-backend-plants.json`
- `2026-11-07-helper-snapshot-missing-marker-plants.json`
- `2026-11-07-helper-snapshot-nonce-format-plants.json`
- `2026-11-07-helper-snapshot-plant-producer-plants.json`
- `2026-11-07-helper-snapshot-plants.json`
- `2026-11-07-helper-snapshot-private-directory-plants.json`
- `2026-11-07-helper-snapshot-private-record-plants.json`
- `2026-11-07-helper-snapshot-reply-backend-status-plants.json`
- `2026-11-07-helper-snapshot-reply-record-plants.json`
- `2026-11-07-helper-snapshot-reply-record-shape-plants.json`
- `2026-11-07-helper-snapshot-reserved-status-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-changes-after-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-changes-before-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-finish-after-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-finish-before-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-gate-after-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-gate-before-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-predicate-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-prompt-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-run-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-validate-plants.json`
- `2026-11-07-helper-snapshot-snapshot-bytes-plants.json`
- `2026-11-07-helper-snapshot-snapshot-modes-plants.json`
- `2026-11-07-helper-snapshot-snapshot-producer-hash-plants.json`
- `2026-11-07-helper-snapshot-snapshot-producer-version-plants.json`
- `2026-11-07-helper-snapshot-stale-marker-plants.json`
- `2026-11-07-helper-snapshot-status-producer-emission-plants.json`
- `2026-11-07-helper-snapshot-status-producer-foreign-plants.json`
- `2026-11-07-helper-snapshot-status-producer-legacy-plants.json`
- `2026-11-07-helper-snapshot-status-producer-missing-plants.json`
- `2026-11-07-helper-snapshot-terminal-refusal-plants.json`
- `2026-11-07-helper-snapshot-write-private-plants.json`
- `2026-11-07-repourl-stated-check-plants.json`
- `2026-11-07-reviewer-confirmation-plants.json`
- `2026-11-08-load-bounds-clock-real-grace-clock-plants.json`
- `2026-11-08-load-bounds-lifecycle-owner-finalizer-disabled-plants.json`
- `2026-11-08-load-bounds-lifecycle-registration-diagnostic-suppressed-plants.json`
- `2026-11-08-load-bounds-readers-early-reader-1-plants.json`
- `2026-11-08-load-bounds-readers-early-reader-5-plants.json`
- `review-scope-plants.json`
- `review-validity-policy-plants.json`

### Historical results without copied inputs

- `docs/reviews/2026-10-28-error-output-exec-stream-plants.json`
- `docs/reviews/2026-10-28-error-output-fix-plants.json`
- `docs/reviews/2026-10-28-error-output-inherited-map-plants.json`
- `docs/reviews/2026-10-28-error-output-old-regex-plants.json`
- `docs/reviews/2026-10-29-error-output-parser-exception-plants.json`
- `docs/reviews/2026-10-29-error-output-rare-plants.json`
- `docs/reviews/2026-11-02-monitor-pr-client-mode-plants.json`

## Audit of caller inputs cleared by the shared reset

Round 2, finding 1. The audit covers inherited `GIT_*`,
`CODEX_REFERENCE_CONTEXT_WINDOW`, `CODEX_ENABLED_SKILL_PERCENT`,
`CODEX_OTHER_SKILL_RESERVE_TOKENS`, `HELPER_BUNDLE_IDENTITY`,
`HELPER_SNAPSHOT_PATH`, and `HELPER_SNAPSHOT_HASH`.

- `bin/build-review-checklists` reads none of these as caller inputs. Keep the reset.
- `tests/scrut/build-review-checklists.md` reads none of these as caller inputs.
  Keep the reset.
- `bin/validate-plugins` reads `CODEX_REFERENCE_CONTEXT_WINDOW`,
  `CODEX_ENABLED_SKILL_PERCENT`, and `CODEX_OTHER_SKILL_RESERVE_TOKENS` from its
  caller. Remove the reset and exempt the validator in the fixture graph's
  existing reset enforcement. The exemption preserves the budget overrides.
- `tests/fixtures/helper-invocation-setup` reads none of these as caller inputs.
  Keep the reset.

Reintroducing the reset in `bin/validate-plugins` is the plant for the
`empty-context-window` case in `tests/scrut/validate-plugins-catalog.md`.

`make test-scrut SCRUT_TEST_DIR=tests/scrut/validate-plugins-catalog.md` exited 2
with the reset in place. Scrut exited 50 with four budget cases failing,
including `empty-context-window`, which returned 0 instead of 1 and emitted
none of the three expected diagnostics.
After restoring the fix, the same command exited 0 with all 14 cases passing.
`empty-context-window` reported all three diagnostics and returned 1 as expected.

## Reset expectation audit

Round 3, finding 1. The audit covers `55c24070` and the validator exemption in
`4a9675c1`. The command below exited 0. Before the edit it found 346 matching
lines. Individual term counts can overlap.

```bash
grep -RnE 'build-review-checklists|validate-plugins|helper-invocation-setup|git-environment|check-fixture-environments' \
  tests/ docs/reviews/*-plants*
```

| Search term                  | Lines | Verdict                                                                                                                                                                                                                                     |
| ---------------------------- | ----: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `build-review-checklists`    |    13 | The builder and checklist Scrut document no longer produce missing-reset diagnostics in the copied tree. The checklist copy, directive and error expectations still hold. The installed-checklist drift detector still finds stale content. |
| `validate-plugins`           |    37 | The fixture graph now exempts the validator. Its budget, catalog, skill and Codex command expectations still hold. The cross-reference directive fixtures still use the same syntax.                                                        |
| `helper-invocation-setup`    |     3 | The preparation and preflight references still name the correct setup script. The invocation manifests include the reset library. Their assertions concern validator behavior after setup.                                                  |
| `git-environment`            |   287 | Three copied-tree diagnostics are obsolete. The remaining guard diagnostics still apply. Other Scrut and plant source commands load the unchanged library. The fixture-context plant still targets its helper-variable reset.               |
| `check-fixture-environments` |    11 | All three hostile-budget validation snapshots still report a clean guard. The error-output fixture still checks its synthetic samples, and the Claude schema fixture stubs the guard.                                                       |

### Scrut expectations

- `environment-isolation.md` retains exit 1 and the sole
  `bin/build-shared-references` diagnostic for `guard-copy-execution`. The
  diagnostics for the four-backtick fence, Scrut runner, corpus fixture, new
  Git consumer (missing and late resets), corpus wrapper and registered corpus
  consumer still hold. So do the clean `guard-copy-only` case and the context,
  percentage and reserve validation snapshots.
- `build-review-checklists.md` retains the copy/removal summary and file list
  after the first case's new setup command. Its directive rejection and four
  builder-prefixed error expectations still hold.
- `validate-plugins-catalog.md`, `validate-plugins-skills.md` and
  `validate-plugins-codex-exec.md` retain their validator expectations. The
  catalog's direct budget cases still exercise caller overrides.
- `check-cross-references.md` retains its directive and path expectations.
  `repo-tooling.md` references the validator suites in its introduction.
- The other `git-environment` Scrut hits source the unchanged library. The two
  Scrut samples under `tests/data/` also source it. Neither sample has a changed
  output expectation.

Each document ran directly with `make test-scrut SCRUT_TEST_DIR=<file>`.
The paths below are relative to `tests/scrut/`.

| File                             | Make exit | Passed |
| -------------------------------- | --------: | -----: |
| `environment-isolation.md`       |         0 |     51 |
| `build-review-checklists.md`     |         0 |     27 |
| `validate-plugins-catalog.md`    |         0 |     14 |
| `validate-plugins-skills.md`     |         0 |     23 |
| `validate-plugins-codex-exec.md` |         0 |      5 |
| `claude-validation.md`           |         0 |      8 |
| `error-output-guard.md`          |         0 |    102 |
| `check-cross-references.md`      |         0 |     42 |
| `repo-tooling.md`                |         0 |     26 |

`make lint` and `make validate` both exited 0.

### Plant assertions

- The helper snapshot `*-check` hits load the unchanged library before their
  assertions. The snapshot fixture setup verdict and the
  `test_fixture_launcher_clears_context` assertion still correspond to that
  library's behavior.
- The invocation preflight ran the copied setup and all 10 invocation tests.
  `PYTHONDONTWRITEBYTECODE=1 uv run --no-project python tests/helper_snapshot_preflight.py 2026-11-07-helper-invocation-plants.json`
  exited 0 and printed `ASSERTION verdict: helper-invocations: pass`.
- `git apply --check` exited 0 for each of `instruction-guard.patch`,
  `evidence-guard.patch`, `guard-validator.patch`, `fixture-context.patch` and
  `remove-body-comparison.patch`. The contexts still target the same
  predicates. The existing helper plant verdicts were inspected in source.
- The installed-checklist drift detector still has its copied reset library
  via `e5d2db0d`. Running its manifest's checker directly with those inputs
  exited 0 and printed `ASSERT: stale body rejected`. Applying its existing
  patch made the checker exit 1 with `FAIL: stale body comparison removed`.
- The heavy-suite record hit is a captured environment command. Its helper
  references are historical, with no current output assertion.

### Copied Git consumer plant

The full `environment-isolation.md` run passed all 51 cases. The plant ran
the unchanged `guard-copy-execution` block alone in a disposable source copy
using `make test-scrut SCRUT_TEST_DIR=tests/scrut/environment-isolation.md`.
Removing the builder's reset added the `bin/build-review-checklists`
diagnostic alongside the expected shared-reference diagnostic. Scrut exited
50 and Make exited 2. Restoring the builder byte for byte made Scrut and Make
exit 0.

## Merge and patch replay on November 24

Signed merge `435c9519` joined `4386ca1a` and `origin/main` at `1f87b1c0`
without conflicts. The merge brought in #778's load-timeout fixture inputs and
three refreshed patches. The five review-scope patches now apply to the digest
after the introduction of the `repository_identity` jq filter. Each patch
preserves its previous mutation.

The original prediction's `measure-plant.py` replayed the manifest checks in
disposable copies. Command logs, input fingerprints, elapsed times and assertion
matches are in the worker mailbox's `predict-2026-11-24b/` directory.

| Manifest                                   | Baseline exit (elapsed) | Patch checks exiting 0 |
| ------------------------------------------ | ----------------------- | ---------------------- |
| `review-scope-plants.json`                 | 0 (7.448 s)             | 6/6                    |
| `2026-11-05-733-load-timeouts-plants.json` | 1 (2.249 s)             | 45/45                  |

| Review-scope plant | Mutation                                                           | Named red assertion                               | Red exit (elapsed) | Restored exit (elapsed) |
| ------------------ | ------------------------------------------------------------------ | ------------------------------------------------- | ------------------ | ----------------------- |
| `base-tip`         | Add the moving base tip to the repository digest.                  | `FAIL: unrelated base advance preserves snapshot` | 1 (0.972 s)        | 0 (7.267 s)             |
| `head`             | Drop HEAD from the repository digest.                              | `FAIL: HEAD invalidates snapshot`                 | 1 (3.514 s)        | 0 (8.232 s)             |
| `merge-base`       | Drop the merge base from the repository digest.                    | `FAIL: merge base invalidates snapshot`           | 1 (3.863 s)        | 0 (7.253 s)             |
| `membership`       | Drop the index identity and replace membership with an empty list. | `FAIL: membership invalidates snapshot`           | 1 (5.444 s)        | 0 (7.503 s)             |
| `head-judge`       | Drop HEAD and bypass the fixture's scope assertion.                | `FAIL: head round consumer`                       | 1 (2.956 s)        | 0 (7.121 s)             |

The unchanged `base-message` control exited 0 (7.986 s) with
its patch applied and 0 (6.937 s) after restoration.

The load-timeout manifest's declared inputs omit 69 of the manifests expected
by `test_existing_manifest_normal_verdicts_are_preserved`. Each of the three
incoming variants had red and restored exits of 1 with the declared inputs.
None matched its named red predicate or its restored green predicate.

A disposable replay supplied the missing manifest inventory and the files read
by the static detector audit. The first attempt exited 1 (40.938 s)
after including `tests/fixtures/notification-clock.bash` as an input. Its
presence in the input list registered the notification clock as a load-timeout
detector. The corrected replay supplied 140 supplemental files and the
baseline exited 0 (40.739 s). The repository manifest still declares
its original inputs from the merge.

| Incoming load-timeout plant        | Named red assertion                                                  | Red exit (elapsed) | Restored exit (elapsed) |
| ---------------------------------- | -------------------------------------------------------------------- | ------------------ | ----------------------- |
| `unknown-final-state-accepted`     | `FAIL: test_inspection_failure_retains_subprocess_diagnostics`       | 1 (2.224 s)        | 0 (40.922 s)            |
| `kill-reserve-consumed`            | `FAIL: test_inspection_failure_retains_subprocess_diagnostics`       | 1 (2.201 s)        | 0 (40.765 s)            |
| `reconciliation-accepts-live-work` | `FAIL: test_reconciliation_refuses_survivors_and_unknown_identities` | 1 (38.895 s)       | 0 (40.613 s)            |

## Merge of the split compatibility checks on November 24

Signed merge `62ef99af` joined `b650952a` and `origin/main` at `f855ab29`.
Git merged the compatibility data automatically. The existing branch rows and
the incoming inventory and verdict rows passed the inventory unit test and
`tests/scrut/checked-inventory.md` with exit 0. No fixture rows needed editing.
The marketplace and versions matched for all 61 plugins.

### Scoped manifest inventory

The comparison used `git diff --name-only origin/main...HEAD`. The claimed
set includes every committed runnable manifest that the branch adds or
changes, and any manifest with a changed declared input or patch target.
Patch targets were read with Git's patch parser. The per-manifest reasons
and concrete paths are in the worker mailbox's
`predict-2026-11-24c/manifest-scope.json`.

There are 82 claimed manifests and zero unclaimed runnable manifests.
Historical JSON records do not meet the runnable manifest shape.

<details>
<summary>Claimed manifests</summary>

- `2026-11-05-733-load-timeouts-plants.json`
- `2026-11-07-helper-invocation-direct-library-plants.json`
- `2026-11-07-helper-invocation-evidence-guard-plants.json`
- `2026-11-07-helper-invocation-guard-presence-plants.json`
- `2026-11-07-helper-invocation-library-guard-plants.json`
- `2026-11-07-helper-invocation-load-stop-plants.json`
- `2026-11-07-helper-invocation-plants.json`
- `2026-11-07-helper-invocation-script-guard-plants.json`
- `2026-11-07-helper-invocation-wrapped-settings-plants.json`
- `2026-11-07-helper-snapshot-backend-identity-plants.json`
- `2026-11-07-helper-snapshot-backend-producer-plants.json`
- `2026-11-07-helper-snapshot-backend-signal-plants.json`
- `2026-11-07-helper-snapshot-backend-status-plants.json`
- `2026-11-07-helper-snapshot-backend-verification-plants.json`
- `2026-11-07-helper-snapshot-cache-path-plants.json`
- `2026-11-07-helper-snapshot-cleanup-status-producer-foreign-plants.json`
- `2026-11-07-helper-snapshot-cleanup-status-producer-legacy-plants.json`
- `2026-11-07-helper-snapshot-cleanup-status-producer-missing-plants.json`
- `2026-11-07-helper-snapshot-conditional-source-plants.json`
- `2026-11-07-helper-snapshot-context-producer-hash-plants.json`
- `2026-11-07-helper-snapshot-context-producer-path-plants.json`
- `2026-11-07-helper-snapshot-context-producer-plants.json`
- `2026-11-07-helper-snapshot-core-producer-predicate-plants.json`
- `2026-11-07-helper-snapshot-fixture-phase-plants.json`
- `2026-11-07-helper-snapshot-fresh-invocation-plants.json`
- `2026-11-07-helper-snapshot-gate-render-producer-plants.json`
- `2026-11-07-helper-snapshot-gate-verify-producer-plants.json`
- `2026-11-07-helper-snapshot-launcher-deletion-review-anti-patterns-plants.json`
- `2026-11-07-helper-snapshot-launcher-deletion-trim-comments-plants.json`
- `2026-11-07-helper-snapshot-launcher-deletion-trim-text-plants.json`
- `2026-11-07-helper-snapshot-launcher-invalidity-review-anti-patterns-plants.json`
- `2026-11-07-helper-snapshot-launcher-invalidity-trim-comments-plants.json`
- `2026-11-07-helper-snapshot-launcher-invalidity-trim-text-plants.json`
- `2026-11-07-helper-snapshot-launcher-transient-review-anti-patterns-plants.json`
- `2026-11-07-helper-snapshot-launcher-transient-trim-comments-plants.json`
- `2026-11-07-helper-snapshot-launcher-transient-trim-text-plants.json`
- `2026-11-07-helper-snapshot-loaded-library-plants.json`
- `2026-11-07-helper-snapshot-marker-shape-plants.json`
- `2026-11-07-helper-snapshot-missing-backend-plants.json`
- `2026-11-07-helper-snapshot-missing-marker-plants.json`
- `2026-11-07-helper-snapshot-nonce-format-plants.json`
- `2026-11-07-helper-snapshot-plant-producer-plants.json`
- `2026-11-07-helper-snapshot-plants.json`
- `2026-11-07-helper-snapshot-private-directory-plants.json`
- `2026-11-07-helper-snapshot-private-record-plants.json`
- `2026-11-07-helper-snapshot-reply-backend-status-plants.json`
- `2026-11-07-helper-snapshot-reply-record-plants.json`
- `2026-11-07-helper-snapshot-reply-record-shape-plants.json`
- `2026-11-07-helper-snapshot-reserved-status-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-changes-after-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-changes-before-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-finish-after-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-finish-before-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-gate-after-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-gate-before-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-predicate-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-prompt-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-run-plants.json`
- `2026-11-07-helper-snapshot-scope-producer-validate-plants.json`
- `2026-11-07-helper-snapshot-snapshot-bytes-plants.json`
- `2026-11-07-helper-snapshot-snapshot-modes-plants.json`
- `2026-11-07-helper-snapshot-snapshot-producer-hash-plants.json`
- `2026-11-07-helper-snapshot-snapshot-producer-version-plants.json`
- `2026-11-07-helper-snapshot-stale-marker-plants.json`
- `2026-11-07-helper-snapshot-status-producer-emission-plants.json`
- `2026-11-07-helper-snapshot-status-producer-foreign-plants.json`
- `2026-11-07-helper-snapshot-status-producer-legacy-plants.json`
- `2026-11-07-helper-snapshot-status-producer-missing-plants.json`
- `2026-11-07-helper-snapshot-terminal-refusal-plants.json`
- `2026-11-07-helper-snapshot-write-private-plants.json`
- `2026-11-07-installed-checklist-drift-plants.json`
- `2026-11-07-repourl-stated-check-plants.json`
- `2026-11-07-reviewer-confirmation-plants.json`
- `2026-11-08-load-bounds-clock-real-grace-clock-plants.json`
- `2026-11-08-load-bounds-lifecycle-owner-finalizer-disabled-plants.json`
- `2026-11-08-load-bounds-lifecycle-registration-diagnostic-suppressed-plants.json`
- `2026-11-08-load-bounds-readers-early-reader-1-plants.json`
- `2026-11-08-load-bounds-readers-early-reader-5-plants.json`
- `2026-11-24-779-inventory-plants.json`
- `2026-11-24-779-verdicts-plants.json`
- `review-scope-plants.json`
- `review-validity-policy-plants.json`

</details>

### Caller results and stop

Each listed Scrut document ran as `make test-scrut SCRUT_TEST_DIR=tests/scrut/<file>`.
The numbers are process exits. The expanded tracked-file caller search,
blocked path list, individual logs and direct-command exits are in the
worker mailbox's `predict-2026-11-24c/` directory.

| Scrut document                |      Exit |
| ----------------------------- | --------: |
| `base-resolution.md`          |         0 |
| `bugs-gather.md`              |         0 |
| `build-codex-marketplace.md`  |         0 |
| `build-review-checklists.md`  |         0 |
| `build-shared-references.md`  | 2, then 0 |
| `check-cross-references.md`   |         0 |
| `checked-inventory.md`        |         0 |
| `checked-timeout-budgets.md`  |         2 |
| `codex-aspects.md`            |         0 |
| `environment-isolation.md`    |         0 |
| `helper-invocations.md`       |         0 |
| `repo-tooling.md`             |         0 |
| `review-scope-validity.md`    |         0 |
| `validate-plugins-catalog.md` |         0 |
| `validate-plugins-skills.md`  |       143 |

The shared-reference fixture initially missed the two canonical snapshot
sources. Adding them and asserting all 19 copies restored all 11 tests.

| Direct check                                   | Exit |
| ---------------------------------------------- | ---: |
| Inventory unit test                            |    0 |
| Snapshot judge unit test                       |    0 |
| Split inventory fixture in the full checkout   |    1 |
| Split inventory copy setup, first attempt      |  127 |
| Split inventory fixture in its declared copy   |    0 |
| Split verdict fixture                          |    0 |
| CI Scrut document inventory                    |    0 |
| CI generated-mirror check in a disposable copy |    0 |
| `bin/validate-json`                            |    0 |
| `bin/check-fixture-environments`               |    0 |
| `uv run --script bin/check-review-validity.py` |    0 |
| `bin/validate-plugins` with the CI environment |    0 |
| `bin/validate-claude-plugins`                  |    0 |
| `make lint`                                    |    0 |
| `make validate`                                |    0 |
| Launch boundary assertion on `origin/main`     |    0 |
| Launch boundary assertion on the merged tree   |    1 |

The inventory fixture assumes its manifest's copied inputs. The full checkout
contains additional manifests that the fixture deliberately filters out of its
expected rows. The first copy attempt shadowed zsh's path variable and failed
before running the fixture. The declared-input retry passed.

The timeout-budget caller found a cross-issue contract conflict. The existing
audit requires one guarded process launch boundary in the plant scripts.
The snapshot launcher's verified helper invocation and plain `exec` replace the
launcher process, while `exec-recorded` waits for the backend to record its
status. The audit flags lines 148, 226 and 309 in `helper-snapshot`.
The focused assertion passed on `f855ab29` and failed on the merged tree.
Changing the deadline or process semantics, or narrowing the guard to exclude
the snapshot launcher, requires a decision on the existing supervision contract.

The caller run stopped at that failure and interrupted the in-flight
`validate-plugins-skills.md` run. Some other caller documents also execute
commands excluded by the run limits. Their paths are in
`blocked-scrut-paths.txt`. The ordered caller phase is incomplete, so plant
replays, gate proposals and gate dry runs remain pending. The scoped
receipt prediction is unverified.

## Piece A verification

The code split is based on `origin/main` at `f855ab29`. The historical
review and prediction sections above describe the combined work. This
section records the checks on the Git environment reset.

The tracked-path search used every file in
`git diff --name-only origin/main...HEAD` and searched separately for
`make validate`, the Makefile's fixture entry points, and the scripts that
source the reset. A's standalone fixtures keep the nine shared-reference
copies present on main. The added shared-reference sources and corresponding
19-copy expectations belong to the launcher.

### Caller reruns after restoring the reset library

The named documents ran as
`make test-scrut SCRUT_TEST_DIR=tests/scrut/<file>.md`.
`run-scrut-documents.md` used an absent lock path. The temporary copy of
`heavy-suite-lock.md` used private stubs and omitted the aggregate target
case that invokes `make test-all`.

`checked-gate-plants*.md`, `checked-plant-guards-*.md`,
`checked-gate.md`, `checked-plant.md` and `checked-python.md` were held
under the runner exclusions. They have no rerun exits. The load-timeout
baseline was held for the same reason. The fixture setup probes below ran
before the review removed `tests/fixtures/helper-invocation-setup` from
piece A. The snapshot plants that use it belong to piece B.

| Scrut document                        | Exit | Seconds |
| ------------------------------------- | ---- | ------- |
| `anti-pattern-edit-worktree.md`       | 0    | 2.19    |
| `backlog-gather.md`                   | 0    | 5.41    |
| `base-resolution.md`                  | 0    | 4.97    |
| `bash-empty-lists.md`                 | 0    | 0.49    |
| `bugs-gather.md`                      | 0    | 38.62   |
| `build-codex-marketplace.md`          | 0    | 1.17    |
| `build-review-checklists.md`          | 0    | 2.68    |
| `build-shared-references.md`          | 0    | 0.81    |
| `chain-adapters.md`                   | 0    | 2.17    |
| `check-cross-references.md`           | 0    | 3.43    |
| `checked-inventory.md`                | 0    | 0.18    |
| `checked-timeout-budgets.md`          | 0    | 29.42   |
| `claude-validation.md`                | 0    | 4.69    |
| `codex-aspects.md`                    | 0    | 69.73   |
| `codex-cleanup.md`                    | 0    | 5.09    |
| `codex-failure-rollouts.md`           | 0    | 31.43   |
| `combined-worktrees.md`               | 0    | 4.11    |
| `copilot-fix-ancestry.md`             | 0    | 3.00    |
| `copilot-summary-contract.md`         | 0    | 2.79    |
| `default-branch-fallback.md`          | 0    | 0.29    |
| `environment-isolation.md`            | 0    | 278.97  |
| `error-output-guard.md`               | 0    | 120.08  |
| `git-worktree-stub.md`                | 0    | 0.46    |
| `launch-workmux-options.md`           | 0    | 3.23    |
| `launch-workmux-remote.md`            | 0    | 3.16    |
| `launch-workmux-sockets.md`           | 0    | 2.96    |
| `launch-workmux.md`                   | 0    | 32.10   |
| `manage-resource-claims.md`           | 0    | 61.62   |
| `merge-flow.md`                       | 0    | 5.30    |
| `monitor-client-policy.md`            | 0    | 11.64   |
| `monitor-dispatch.md`                 | 0    | 5.44    |
| `notification-failures.md`            | 0    | 3.74    |
| `notification-hooks.md`               | 0    | 0.33    |
| `notification-load.md`                | 0    | 15.65   |
| `notification-sounds.md`              | 0    | 18.49   |
| `notification-tiers.md`               | 0    | 10.25   |
| `notifications.md`                    | 0    | 44.80   |
| `owner-call-contract.md`              | 0    | 0.63    |
| `progress-model.md`                   | 0    | 0.98    |
| `refusal-classifier-contract.md`      | 0    | 5.42    |
| `repo-tooling.md`                     | 0    | 4.66    |
| `report-board-bugs.md`                | 0    | 2.43    |
| `report-board-head-freeing.md`        | 0    | 1.44    |
| `report-board.md`                     | 0    | 14.85   |
| `resolve-copilot-threads.md`          | 0    | 3.81    |
| `review-corpus.md`                    | 0    | 18.63   |
| `review-scope-disk-metadata.md`       | 0    | 3.60    |
| `review-scope-raw.md`                 | 0    | 12.23   |
| `review-scope-sparse.md`              | 0    | 4.30    |
| `review-scope-submodule-consumers.md` | 0    | 104.59  |
| `review-scope-submodules.md`          | 0    | 107.92  |
| `review-scope-validity.md`            | 0    | 7.45    |
| `review-scope.md`                     | 0    | 18.06   |
| `run-scrut-documents.md`              | 0    | 8.88    |
| `rust-toolchain-audit.md`             | 0    | 1.82    |
| `validate-plugins-catalog.md`         | 0    | 214.63  |
| `validate-plugins-codex-exec.md`      | 0    | 74.89   |
| `validate-plugins-skills.md`          | 0    | 343.78  |
| `watch-changes.md`                    | 0    | 12.32   |
| `workmux-sandbox.md`                  | 0    | 81.17   |
| `heavy-suite-lock.md` (stub cases)    | 0    | 3.438   |

| Direct caller or probe  | Exit | Seconds |
| ----------------------- | ---- | ------- |
| `reset-probe`           | 0    | 0.039   |
| `helper-fixture-setup`  | 0    | 0.016   |
| `helper-fixture-repeat` | 0    | 0.016   |
| `shell-inventory`       | 0    | 0.125   |
| `ci-scrut-inventory`    | 0    | 0.043   |
| `fixture-environments`  | 0    | 11.525  |
| `fixture-review-paths`  | 0    | 0.98    |
| `inventory-unit`        | 0    | 0.068   |
| `ci-mirrors`            | 0    | 2.819   |

The CI mirror probe generated the checklists and mirrors in a disposable
Git checkout and checked for drift. The reset probe confirmed that Git and
budget inputs are cleared and the three inherited helper variables persist.

The following baseline checks ran directly in copies of their declared
inputs. All declared output assertions matched.

| Manifest baseline                                                                 | Exit | Seconds |
| --------------------------------------------------------------------------------- | ---- | ------- |
| `2026-11-07-installed-checklist-drift-plants.json`                                | 0    | 0.267   |
| `2026-11-07-repourl-stated-check-plants.json`                                     | 0    | 2.589   |
| `2026-11-07-reviewer-confirmation-plants.json`                                    | 0    | 0.267   |
| `2026-11-08-load-bounds-clock-real-grace-clock-plants.json`                       | 0    | 5.116   |
| `2026-11-08-load-bounds-lifecycle-owner-finalizer-disabled-plants.json`           | 0    | 6.62    |
| `2026-11-08-load-bounds-lifecycle-registration-diagnostic-suppressed-plants.json` | 0    | 6.66    |
| `2026-11-08-load-bounds-readers-early-reader-1-plants.json`                       | 0    | 0.208   |
| `2026-11-08-load-bounds-readers-early-reader-5-plants.json`                       | 0    | 0.213   |
| `review-scope-plants.json`                                                        | 0    | 6.902   |
| `review-validity-policy-plants.json`                                              | 0    | 0.338   |

### Plant scope and direct replay results

The content-based inventory found 13 runnable manifests. Scope is the
intersection of the working tree diff against `origin/main` and each
manifest's declared inputs or the manifest path itself. One manifest is
claimed. `2026-11-07-installed-checklist-drift-plants.json` is edited and
declares the changed `bin/build-review-checklists` as an input.

`bin/lib/git-environment.bash` matches `origin/main`. The other mentions of
the three helper variables are in historical review records.

The 12 unclaimed runnable manifests are:

- `2026-11-05-733-load-timeouts-plants.json`
- `2026-11-07-repourl-stated-check-plants.json`
- `2026-11-07-reviewer-confirmation-plants.json`
- `2026-11-08-load-bounds-clock-real-grace-clock-plants.json`
- `2026-11-08-load-bounds-lifecycle-owner-finalizer-disabled-plants.json`
- `2026-11-08-load-bounds-lifecycle-registration-diagnostic-suppressed-plants.json`
- `2026-11-08-load-bounds-readers-early-reader-1-plants.json`
- `2026-11-08-load-bounds-readers-early-reader-5-plants.json`
- `2026-11-24-779-inventory-plants.json`
- `2026-11-24-779-verdicts-plants.json`
- `review-scope-plants.json`
- `review-validity-policy-plants.json`

There are no new manifests in piece A. The compatibility inventory
therefore kept its current rows. The inventory unit and Scrut checks
both passed.

The replay tables below record the checks before restoring the reset library.
Each completed replay ran the declared check in a copy of only the
manifest inputs, checked and applied the patch against a private Git
directory, then rematerialized the original bytes and modes and repeated
the check. The expected assertion matched for each recorded red exit.
An exit 0 for the middle phase marks a declared green control.

| Manifest baseline                                                                 | Exit | Seconds |
| --------------------------------------------------------------------------------- | ---- | ------- |
| `2026-11-07-installed-checklist-drift-plants.json`                                | 0    | 0.419   |
| `2026-11-07-repourl-stated-check-plants.json`                                     | 0    | 3.097   |
| `2026-11-07-reviewer-confirmation-plants.json`                                    | 0    | 0.35    |
| `2026-11-08-load-bounds-clock-real-grace-clock-plants.json`                       | 0    | 5.931   |
| `2026-11-08-load-bounds-lifecycle-owner-finalizer-disabled-plants.json`           | 0    | 7.085   |
| `2026-11-08-load-bounds-lifecycle-registration-diagnostic-suppressed-plants.json` | 0    | 6.843   |
| `2026-11-08-load-bounds-readers-early-reader-1-plants.json`                       | 0    | 0.513   |
| `2026-11-08-load-bounds-readers-early-reader-5-plants.json`                       | 0    | 0.505   |
| `review-scope-plants.json`                                                        | 0    | 8.41    |
| `review-validity-policy-plants.json`                                              | 0    | 0.552   |

| Declaration                          | Patch check | Planted exit | Seconds | Restored exit | Seconds |
| ------------------------------------ | ----------- | ------------ | ------- | ------------- | ------- |
| `body-comparison-removed`            | 0           | 1            | 0.41    | 0             | 0.411   |
| `ignore-explicit-url`                | 0           | 1            | 0.864   | 0             | 2.685   |
| `keep-trailing-slash`                | 0           | 1            | 3.619   | 0             | 3.322   |
| `old-alternative-suppression`        | 0           | 1            | 0.547   | 0             | 2.783   |
| `absent-workflow-disabled`           | 0           | 50           | 0.325   | 0             | 0.337   |
| `bootstrap-review-promise`           | 0           | 50           | 0.295   | 0             | 0.322   |
| `codex-activation-overclaim`         | 0           | 50           | 0.33    | 0             | 0.365   |
| `copilot-activation-overclaim`       | 0           | 50           | 0.314   | 0             | 0.314   |
| `instruction-files-overclaim`        | 0           | 50           | 0.328   | 0             | 0.359   |
| `old-codex-wording`                  | 0           | 50           | 0.322   | 0             | 0.302   |
| `old-copilot-wording`                | 0           | 50           | 0.312   | 0             | 0.298   |
| `readme-review-promise`              | 0           | 50           | 0.317   | 0             | 0.295   |
| `report-partitions-omitted`          | 0           | 50           | 0.311   | 0             | 0.33    |
| `wording-control`                    | 0           | 0            | 0.309   | 0             | 0.297   |
| `workflow-inspection-omitted`        | 0           | 50           | 0.31    | 0             | 0.317   |
| `real-grace-clock`                   | 0           | 1            | 33.915  | 0             | 5.245   |
| `owner-finalizer-disabled`           | 0           | 1            | 6.04    | 0             | 7.003   |
| `registration-diagnostic-suppressed` | 0           | 1            | 7.514   | 0             | 6.387   |
| `early-reader-1`                     | 0           | 1            | 0.5     | 0             | 0.51    |
| `early-reader-5`                     | 0           | 1            | 0.52    | 0             | 0.594   |
| `base-message`                       | 0           | 0            | 7.148   | 0             | 9.186   |
| `base-tip`                           | 0           | 1            | 0.982   | 0             | 8.005   |
| `head`                               | 0           | 1            | 3.046   | 0             | 6.953   |
| `head-judge`                         | 0           | 1            | 2.761   | 0             | 8.391   |
| `membership`                         | 0           | 1            | 5.961   | 0             | 7.741   |
| `merge-base`                         | 0           | 1            | 4.426   | 0             | 7.455   |
| `differing-copy`                     | 0           | 1            | 0.242   | 0             | 0.601   |
| `duplicate-wording`                  | 0           | 1            | 0.241   | 0             | 0.557   |
| `encoding-error`                     | 0           | 1            | 0.647   | 0             | 0.509   |
| `helper-quoted-test`                 | 0           | 1            | 0.234   | 0             | 0.576   |
| `helper-ref`                         | 0           | 1            | 0.229   | 0             | 0.559   |
| `negated-policy`                     | 0           | 0            | 0.576   | 0             | 0.605   |
| `terminal-status`                    | 0           | 1            | 0.237   | 0             | 0.617   |
| `traversal-error`                    | 0           | 1            | 0.507   | 0             | 0.524   |

The `2026-11-05-733-load-timeouts-plants.json` check calls both restricted
runners through its unit tests. All 44 assertion patches and its one
control patch passed `git apply --check` in copied inputs. The baseline,
red and restored phases remain unverified.

### Piece A review round

Applied one Important finding and two Nits from the review of `81f91498`.
The branch search exited 1 with zero fixture references in the searched
paths. The `find` status finding follows the fixture to piece B.

Replayed the claimed checklist drift manifest in copies of its declared
inputs. Its check exited 0 on the baseline, 1
with `body-comparison-removed` applied and 0 after restoring
the original inputs. All declared assertions matched. Git initialization,
patch check and patch application each exited 0.

### Proposed gate

[The gate manifest](2026-11-24-git-environment-reset/gate.json) retains the
existing deadlines. The schema, execution plan, input paths, plant
declarations and wrapper syntax validated with exit 0. The light checks
used the exact manifest argv from the repository root. The plant wrapper
used an inert `uv` stub to check dispatch to the declared manifest and its
variant names.

| Gate check                         | Dry-run exit | Seconds                   | Deadline seconds |
| ---------------------------------- | ------------ | ------------------------- | ---------------- |
| `make lint`                        | 0            | 20.450                    | 52               |
| `make validate`                    | 0            | 49.872                    | 110              |
| Checklist drift dispatch (stubbed) | 0            | 0.205                     | 121              |
| `make test-all`                    | Held         | 1,380 (prior measurement) | 2100             |
| `/usr/bin/true`                    | 0            | 0.003                     | 3                |

The predicted total is **1,455.2 s** before lock wait. It uses
0.869 s for the direct checklist drift replay in place of
stubbed dispatch time, and 3.956 s from the prior
isolated fingerprint probe. The deadline total is **2,666 s**,
including 56 fixed fingerprint steps. The full suite and gate verdict
remain unverified.

Historical caller and timing logs are in `/tmp/729a-trim-work`. The review
round logs, exact argv and measurements are in `/tmp/729a-review.IMrBemc3`.
