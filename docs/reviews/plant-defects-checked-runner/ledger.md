# Checked plant runner review ledger

## Current state

Structural and focused review loops ended **clean at Critical**. All taken
findings and planted boundary checks pass. The single full `make test-all` run
passed: 80 Scrut documents, 2,225 testcases, zero failures or skips, plus lint and
validation. Baseline Semgrep and explicit Python coverage have zero findings or
errors. Version checks pass for 1.1.0. Final lint and exact-tree tidy gate
publication; their observed outcomes and PR state are reported through the worker
mailbox. This ledger preserves the prepublication review and test evidence.

## Review and validation history

### Scope and review execution

Base: `origin/main`, merge base `e0ad16d5095e9c445be45bde5ef622ad8f5f45cb`.
The streamlined full local review order applies. Structural round 1 used fresh
read-only Codex exec runs, `gpt-6.1-sol`, high effort, window 872000, approval
never and web search disabled. Both processes exited zero with nonempty output.
The anti-patterns report passed its committed result-check schema and reports
complete canonical coverage. Remote metadata was verified by the calling worker.

The report-only simplify launcher attempted prompt generation before review-scope
finished writing its output. Prompt generation failed, but the shell still launched
the read-only reviewer with the explicit report-only request and no rendered scope.
That reviewer independently discovered and read the nine canonical changed files,
reported all four cleanup angles inline and returned a nonempty JSON report.
It used its own canonical-content fingerprint rather than the helper's snapshot;
helper snapshot validation is unavailable. Preserve this limitation, not a claim
of a clean simplify gate. No retry or second simplify run has occurred. Both raw
reports are stored beside this ledger. No reviewer edits were observed.

### Structural round 1 findings

Each entry records reviewer label, own severity, take/record and review-again call.

1. **Hard-linked record destinations.** Reviewer: `important`, "Sibling input forms:
   hard-linked destinations bypass input protection". Own: Important, because
   pathname-only protection allows records to overwrite a live input or each
   other through hard links. Take: reject inode aliases. Review again: yes,
   behavior changes. Fixed; awaiting structural round 2.
2. **Executable input permissions.** Reviewer: `important`, "Parallel paths:
   private copies discard executable input permissions". Own: Important, because
   copied supporting executables fail valid baseline checks. Take: preserve and
   fingerprint executable modes through restoration. Review again: yes, behavior
   changes. Fixed; awaiting structural round 2.
3. **Required green controls.** Reviewer: `important`, "Agent-prose control flow:
   mandatory runner cannot record required green controls". Own: Important;
   `references/the-plant-table.md` requires green negative controls that the
   mandatory red-only runner cannot publish. Take: resolve the contract, with a
   scope decision first. Review again: yes, behavior changes. Fixed; awaiting structural round 2.
   Recommended design: retain red-only assertion variants and add a separately
   declared green-control outcome through the same checked result gate. This
   was selected by TOOLING in the native reply recorded above and is implemented.
4. **Timeout evidence.** Reviewer: `important`, "Absent or partial data: timed-out
   steps lose captured evidence". Own: Important, because the timeout path drops
   captured diagnostics and step exit evidence. Take: retain timed-out step data
   and termination status. Review again: yes, behavior changes. Fixed; awaiting structural round 2.
5. **Fingerprint-only memory allocation.** Simplify reviewer: `suggestion`,
   "Uncited: Avoid retaining input contents during fingerprint-only checks."
   Own: Nit, an optional allocation improvement with no measured budget failure.
   Take: the snapshot helper can omit retained contents at fingerprint-only
   callers. This is a local allocation reduction. Review again with the required
   structural round; no separate round is spent on this cleanup.

No finding has been downgraded. No recurring defect has been reported. Round 1
took behavior-changing Important findings; round 2 proceeds at Important.

### Validation evidence

- `checked-plant.md`: 1/1 Scrut case passed after the fixes, running 18 unittest checks, including
  the required broken-setup publication refusal and real plant/restoration paths.
  Its guard-plant test uses the checked runner itself for six guard boundaries,
  including control verdict, executable mode, hard-link protection and timeout evidence. No hand-written plant table
  or generated success section is claimed here; test JSON was temporary.
- `error-output-guard.md`: 102/102 cases passed after the correction.
- `environment-isolation.md`: 29/51 cases passed, 22 failed. The new Python
  fixture indirectly consumes Git without the required reset; the Scrut caller
  also needs that reset. Earlier cases copied a runner-import bytecode cache
  before its removal, producing additional validation failures. The cache was
  created by the new test import and removed by exact path; the test now disables
  bytecode writes before loading the runner. These are pre-review integration
  failures, not clean validation. The reset wrapper and Scrut caller reset were
  applied after TOOLING's design reply. The Python module moved under `tests/`.
- `make build`: passed; generated mirrors are committed with the implementation.
- `make validate`: initially failed on the fixture/caller reset requirement above.
  The corrected run completed with exit zero, including external manifest checks.
- Formatting: pinned Yarn dependencies restored with `corepack yarn install
--immutable`; scoped Prettier passed. `git diff --check` passed.
- Thermal read: no thermal or performance warning recorded at the observation.
- Focused aspect loop, trims, baseline semgrep, final lint-and-fix, version check,
  exact-tree tidy, full suite, push and PR: unrun. Full-suite lock not acquired.

### Structural round 2 at Important

Both fresh read-only Codex processes exited zero with nonempty JSON output.
Anti-patterns passed its schema and reports complete canonical coverage.
Report-only simplify passed the installed helper's aspect/schema and snapshot
validation against `scope-round2-final.json`, snapshot
`b4d2c90fe55b4e281b8c99b0d5a5ae5130811cb6`. Its four cleanup angles ran inline;
no independent cleanup fan-out was authorized. No lasting working-tree changes
were observed while either reviewer ran. Raw reports are stored beside this file.

1. Reviewer `important`: "Sibling input forms: new record destinations can still
   alias and overwrite each other". Own: Important, because absent case aliases
   can overwrite the ledger with status while render succeeds. Take, pending
   TOOLING's structural decision. Review again: yes, behavior changes. This is
   the recurring round-1 destination-alias class, so the loop stops here.
2. Reviewer `important`: "Absent or partial data: the documented green predicate
   publishes skipped controls". Own: Important, because unittest's `OK (skipped=1)`
   satisfies the documented green substrings. Take, pending the green-evidence
   decision. Review again: yes, validation behavior changes.
3. Reviewer `important`: "Sibling input forms: leading-dash script paths are
   interpreted as Bash options". Own: Important, because normalized declared
   filenames can fail before script execution. Take: terminate Bash options on
   both setup and check paths. Review again: yes, behavior changes.
4. Simplify reviewer `suggestion`: "Uncited: Reuse each function's ordered
   declaration list." Own: Nit, minor allocation/clarity improvement. Record
   below the active Important threshold. No edit and no additional review.

No downgrade. Round 2 ended **stopped: recurring defect**. TOOLING then chose the structural
fix above; all three takes are implemented. The next round retains the count.

The corrected environment-isolation invocation with `make -s` ran 48/51 cases.
The remaining three compare echoed nested make recipes, suppressed by inherited
silent MAKEFLAGS. A normal `make test-scrut` invocation is running to verify that
invocation diagnosis; it has not yet reported a result. The first 22-failure run
and this 3-failure run are retained as failures, never passes.

### Round 2 restart

The carried structural round 3 ran at Important. Output identity checks operate on reserved
handles for new and existing paths, not pathname spelling. The boundary test uses
the local filesystem's alias behavior and checks distinct successful outputs on
case-sensitive filesystems. Checked guard plants require the alias assertion to
fail where case aliases exist. Both setup/check Bash calls terminate options.
The green unittest example requires the exact success line and explicit skip/error
exclusions; a real skipped control is refused. The final focused rerun is pending.

Then finish the focused aspect loop, trims, baseline semgrep, lint-and-fix,
version checks and exact-tree tidy, followed by the brief's one full-suite load,
thermal and lock protocol. TOOLING merges.

### Structural round 3, second Important round

Both fresh read-only Codex runs exited zero with nonempty JSON. Anti-patterns
passed its schema and read every canonical changed file; simplify passed the
installed helper's schema and snapshot validation. No working-tree changes were
observed during either run. Simplify completed four angles inline with no proposal
at Important. Raw reports are stored beside this ledger.

Reviewer `important`: "Absent or partial data: detached descendants can prevent
timeout evidence from being published". Own: Important; an escaped process group
can retain a captured pipe, so unbounded `communicate()` prevents restore and
complete failure JSON. Take: pending TOOLING's structural decision. Review again:
yes, behavior changes. This recurs from round 1's timeout-evidence class.
End state: **stopped: recurring defect**. No third output-alias instance was found.

The proposed correction captures stdout/stderr in runner-owned regular files,
uses bounded parent waits and bounded reads, and records timeout, termination and
truncation. A committed new-session descendant fixture must prove its inherited
stdio cannot prevent failure JSON; cleanup uses the PID that fixture recorded.
TOOLING resolved the stop with the native reply recorded above. The file-backed
capture fix and committed regression are implemented. The carried next
structural round is Critical-only; the separate focused aspect loop remains
unstarted and begins at Nit.

The final focused rerun failed its guard-campaign check. Its broad red exclusion
`skipped` matched nested skipped-control diagnostics from a real assertion
failure. The checked campaign recorded that row as setup-error and later rows as
unrun, and refused overall success. A test-only predicate correction is prepared
outside the tree, not applied: exclude actual unittest error headers and skip
summaries, preserving exact green success and skip/error rejection.

The normal-make environment-isolation rerun finished 49/51. Two fixture copies
saw source/mirror drift while code was changing. This is a failed validation run,
not 51/51. Run again only after build on a frozen source/generated tree.

### Current verification and next steps

The final focused document passed 1/1 Scrut case, executing 23 unittest checks.
Every guard plant uses the same checked runner and a targeted red test selection;
baseline and restored checks run the complete eleven-test guard set. The
unbounded-pipe regression launches a new-session descendant retaining stdio,
requires complete failed JSON within the supervising timeout and stops only
recorded parent/child PIDs. Output overflow is explicitly rejected. Failed
campaign iterations remain failures; no plant success ledger has been
hand-written from them.

After the committed fixture and capture changes, build completed successfully.
Run error-output guard and environment-isolation on the frozen source/generated
tree, at most two documents at once, and observe final results before edits.
Continue structural round 4 at Critical, then the separate focused aspect loop
at Nit. Trims, baseline semgrep, final lint-and-fix, version checks, exact-tree
tidy, one full suite under the brief's load/thermal/lock gate, push and ready PR
remain required. TOOLING merges.

### Structural round 4 and focused Nit review

Structural round 4's anti-patterns and report-only simplify outputs validated,
with no findings at the carried Critical threshold. Snapshot comparison found no
lasting changes. Structural loop end: **clean at Critical**. Raw Critical reports
are stored beside this ledger. The frozen-tree guard runs then completed:
error-output 102/102 and environment-isolation 51/51, both exit zero. These passes
supersede, rather than erase, the failed integration runs above.

All five focused Nit aspects, `code`, `errors`, `tests`, `comments` and `types`,
ran with the skill's explicit `gpt-6.1-sol`, high effort, window 872000, read-only,
never approvals and disabled web search. All completed with exit zero and valid
nonempty JSON; types had no findings. No aspect was omitted. Snapshot comparison
reported no lasting changes. This is a separate loop starting at Nit.

1. Code reviewer `important`, "Uncited: Ancestor Git discovery can silently skip
   private patches." Own: Important; a green control can report success without
   applying its patch under repository-local TMPDIR. Take: clear inherited Git
   overrides/config and use separate initialized Git metadata with an explicit
   private worktree. Empty templates avoid creating hooks. Review again: yes,
   behavior changes. Implementation and inside-checkout control test are pending
   focused validation.
2. Code reviewer `important`, "Uncited: Output capture permits unbounded temporary
   disk consumption." Own: Important; continuous output can consume the temporary
   volume and prevent failure JSON. Take, after TOOLING's structural decision
   below. Review again: yes, behavior changes.
3. Tests reviewer `important`, "Uncited: Core manifest rejection rules lack negative
   regression tests." Own: Important; planned reuse depends on rejection of empty
   declarations, zero red exits and absent assertion evidence. Take: committed
   negative cases with failure JSON and unchanged-record refusal, plus plants
   weakening each guard. Review again: no, tests alone do not spend a round.
4. Tests reviewer `important`, "Uncited: Rendering tests do not independently
   challenge step completion evidence." Own: Important; aggregate success must
   not hide invalid individual step evidence. Take: corrupt completion flags and
   setup exits beneath successful aggregates, requiring unchanged-record refusal;
   plant the matching gate. Review again: no, tests alone do not spend a round.
5. Errors reviewer `suggestion`, "Uncited: Fingerprint rechecks discard filesystem
   failure diagnostics." Own: Nit; publication fails safely but loses path and
   OSError cause. Take: retain recheck diagnostics for run and rendering, with a
   regression and guard plant. Review again: yes, failure diagnostics change.
6. Comments reviewer `suggestion`, "Uncited: The diagnostic-retention claim includes
   subprocess results that are discarded." Own: Nit; successful patch-command
   output is not stored in JSON. Take: qualify the policy and reference as
   setup/check evidence, with patch failures retained in the cause. Review again:
   no, documentation only.

No downgrade. No capture or Git fix began until TOOLING's native reply at
`20261104T011233Z`: selectors drain nonblocking transports into capped owned files,
with explicit deadlines, no unbounded EOF drain, termination before reaping,
bounded parent waits and final reads. Overflow cannot satisfy a verdict. A
continuous-output test measures actual spool sizes before cleanup, and the
escaped-descendant test remains. This is the final capture design: if a later
review finds capture can again prevent complete failure JSON, stop without a
patch and TOOLING brings the issue to Chris (he/him).

The same reply authorized private Git isolation and the two test-only takes.
The Git test uses TMPDIR inside a checkout and inherited repository overrides;
its control must show the observed mutated value. A separate Git context also
handles legal colon-containing paths without depending on ceiling-list parsing.

An implementation integration take adds SHA-pinned `setup-uv` only to the new
Scrut document's CI job, pinning the locally verified uv version. The existing
Scrut action does not install uv; the new test must not depend on incidental
runner-image contents. The action commit was verified against its upstream tag.
No permissions or hook entries change. This CI behavior also warrants the next
focused Important round. The focused selector-capture rerun is pending; no new
pass is claimed yet.

### Focused Nit fixes validated

The selector-capture focused run passed 1/1 Scrut case with 27 unittest checks.
The guard campaign uses seventeen declared plants with targeted red checks and
full fifteen-test baseline/restored checks. A first Git-isolation weakening
retained the ceiling barrier and correctly failed the campaign's red requirement;
it was not accepted as a successful plant. The final weakening removes both
isolation barriers. The completed final document supersedes that failed attempt.

All Nit takes above are implemented. The capture design retains unreaped parent
identity until any group signal, caps each spool write, closes transports without
an EOF drain on failure, and bounds the final reap/read. Private Git metadata is
initialized with empty templates and explicit worktree arguments, with inherited
Git configuration/location overrides removed. No hook files are generated.
Recheck failures preserve the affected path and OSError text. The two Important
test-only additions and their gate plants are committed with these fixes.

SHA-pinned setup-uv is conditional on the new Scrut document, with uv 0.12.16;
both the action commit/tag and uv release were verified through upstream reads.
No new CI permissions or hook entries. Mirrors were regenerated. The next
focused round is Important because runtime and CI behavior changed; counts carry.

TOOLING clarified the full-suite load scan at `20261104T010202Z`: exclude agent
processes and shells wrapping agents only when their match is argument text, plus
the scan's own grep; keep every real suite/lock running command. The conservative
scratch filter records exclusions and leaves unknown matches in the wait. No
full suite or lock has started. The final full suite remains exactly one run.

### Input-kind preflight before focused Important review

Author preflight, Important: input fingerprinting read bytes before checking file
kind, so a declared FIFO could wait for a writer before step execution. Own:
Important, because unsupported input could prevent a complete failure result.
Take after TOOLING's native call `20261104T013328Z`: this is input validation,
separate from the standing command-capture stop. Open nonblocking, verify the
opened descriptor is regular, then read it; unsupported kinds get null
fingerprints and a preserved cause. Review again: yes, behavior changes, included
in the upcoming focused Important snapshot. No downgrade or count reset.

The updated focused Scrut run passed 1/1 case with 28 unittest checks. The
supervised FIFO check and its guard weakening join the checked campaign. The
preceding selector-tree environment-isolation run completed 51/51 and error-output
completed 102/102 before this input-only change. The final full suite will cover
the complete resulting tree. Mirrors were rebuilt after the input guard.

### Focused round 2, first Important

All five aspects completed with exit zero and valid nonempty JSON. Post-review
snapshot comparison found no lasting changes. Types and errors had no findings.
Code's output bounds and Git isolation were not reported again.

1. Code reviewer `important`, "Uncited: Materialization silently breaks accepted
   symlink relationships." Own: Important; target edits can fail to reach an
   alias-reading check in the private copy, falsely preserving green controls.
   Take: reject linked input paths rather than implement topology support.
   Review again: yes, behavior changes. This belongs to the earlier input
   representation family, so work stopped for TOOLING's structural call.
2. Tests reviewer `important`, "Uncited: Forbidden-output rejection lacks an
   independent regression test." Own: Important; ignoring exclusions can pass
   named-assertion output accompanied by ERROR or SKIP. Take: preserve required
   markers and exits while adding forbidden output, for execution and rendering;
   plant exclusion matching alone. Review again: no, test-only changes.
3. Comments reviewer `suggestion`, "Uncited: The ledger’s opening status
   contradicts its latest recorded state." Own: Nit; stale resume instructions.
   Take: replace the synopsis and label the remaining checkpoints as history.
   Review again: no, documentation only.

TOOLING's native reply `20261104T014842Z` selected regular files reached by real
relative paths, with null fingerprints and recorded refusals for symlinks or
linked components. No topology support. Leaf and directory-link cases are
supervised, and the guard is planted. A further instance in this input
representation family returns to TOOLING without a patch. Counts carry into
the second focused Important round. Focused validation of these takes is pending.

### Focused round 2 fixes validated

The final updated document passed 1/1 Scrut case with 30 unittest checks. The
checked campaign now declares twenty guard plants; baseline/restored controls
run the full eighteen-test guard set, while red checks select the named boundary.
Leaf and directory symlinks fail before execution with null fingerprints. The
independent exclusion plant preserves required markers and expected exits while
introducing forbidden output. Input representation was not expanded to topology
support. Mirrors were regenerated. The second focused Important round follows
with counts carried; no hook changes.

### Focused round 3, second Important, and author stop

All five aspects returned valid JSON with zero findings and exit zero. Snapshot
comparison confirmed no lasting scope changes. The author then found another
input-reader path: manifest parsing still called `read_text` before fingerprint
preflight, so a FIFO could prevent run completion or stale-render refusal.
Reviewer label: author preflight. Own: Important, because a failure could remain
incomplete. Take: yes. Review again: yes, behavior changes. The loop stopped for
TOOLING, rather than claiming the whole workstream clean.

TOOLING's structural call `20261104T021709Z` requires one shared nonblocking
regular-file reader for every external read, with symlinks refused. Manifest
parsing and its fingerprint must use identical bytes. The correction routes
manifest, inputs, restoration verification, result JSON and existing records
through that reader. Reserved record handles retain the existing inode checks.
An AST guard rejects other file readers, with an exact allowlist only for owned
capture spools and bounded pipe reads. Supervised regressions cover missing and
unsupported manifests and stale-render FIFO paths. The checked campaign plants
an unused parallel reader, both manifest entry paths and fingerprint divergence.
Validation is pending; the next focused round is Critical, counts carried.

### Shared-reader validation

The focused document passed 34 unittest checks in 256 seconds locally. The
stronger module-wide AST ownership check also passed its direct targeted run.
Error-output passed 102/102, and environment-isolation passed 51/51 on the frozen
shared-reader tree. These results precede the subsequent process cleanup change.

### Focused round 4, Critical, stopped for structural calls

All five aspects returned valid JSON with exit zero. Snapshot comparison found
no scope changes. Comments and types reported no findings.

1. Code reviewer `important`, "Uncited: Normally exiting steps can leave
   background descendants running." Own: Important; resources can survive
   restoration. Take after TOOLING's structural call. Review again: yes. This
   is adjacent to the earlier process-lifecycle class, so the loop stopped.
   This finding does not claim transport can prevent final JSON publication.
2. Errors reviewer `suggestion`, "Uncited: The manifest consistency check discards
   filesystem failure diagnostics." Own: Nit; failure stays safe, but loses its
   filesystem cause. Take: preserve unreadable-input causes before comparing
   readable manifest bytes. Review again: yes, diagnostics change. The earlier
   failure-cause correction made this a recurrence requiring a structural call.
3. Tests reviewer `important`, "Uncited: Successful rendering lacks regression
   coverage for preserving ledger content." Own: Important; loss of surrounding
   records could evade checks. Take under the missing-own-boundary-test rule.
   Review again: no, tests only. Append, replacement and idempotence have sentinel
   checks, and replacement preservation is planted.

TOOLING's native calls `20261104T023957Z` and `20261104T024049Z` approved bounded
TERM/KILL group cleanup before restoration, preserving leader identity until
cleanup verification finishes. A live macOS probe confirmed `waitid`, `WNOWAIT`
and `WNOHANG` exist: an owned child exiting 7 was observed with
`waitid(P_PID, pid, WEXITED|WNOWAIT)` and then reaped with exit 7. The initial
post-reap proposal was corrected before implementation to prevent group-ID reuse.
Runtime availability is checked before spawning; unsupported runtimes fail.
Results record the group ID, remaining live PIDs and cleanup errors, all verified
again by rendering. Zombies do not count as live group members. Escaped sessions
remain the check's cleanup responsibility.

Targeted validation initially found macOS refuses signaling a zombie-only group;
the result failed safely and retained that cause. Cleanup now checks for live
members first, with a recheck for the exit-between-probe-and-signal case. The four
new targeted tests pass. The checked campaign adds cleanup, runtime-support,
disappearing-manifest and ledger-preservation plants. Full validation is pending.

### Focused round 5, Critical, stopped for failure causes

All five aspects returned valid JSON with exit zero and no lasting scope change.
Code, comments and types had no findings.

1. Errors reviewer `suggestion`, "Uncited: Cleanup inspection failures discard
   captured diagnostics." Own: Nit; cleanup failure safely blocks publication,
   but `str(CalledProcessError)` omits stderr. Take after TOOLING's structural
   call `20261104T025104Z`: all exception-recording boundaries now use one
   formatter retaining type, message and bounded captured stdout/stderr. An AST
   guard rejects recording caught exceptions through other paths. Independent
   inspection-failure and timeout tests exercise both text and byte diagnostics.
   The existing failure-cause variant now challenges file diagnostics, subprocess
   diagnostics and an unused parallel cause recorder. Review again: yes,
   diagnostic behavior changes. End state: stopped: recurring defect.
2. Tests reviewer `important`, "Uncited: Timeout coverage omits running parents
   whose output streams have closed." Own: Important; an unguarded parent-wait
   branch could prevent failure evidence. Take: supervised EOF-then-waitid
   timeout regression with recorded owned PID cleanup, failed JSON assertions
   and renderer refusal. Extend the existing bounded-capture variant to remove
   that deadline too, requiring both named timeout assertions. Review again:
   no, tests only. No actual capture defect was reported or observed.

The monolithic cleanup campaign was interrupted through its recorded controller
PID 23226 with TERM and exited 143. It is not a pass. TOOLING approved four
partitions at `20261104T024922Z`, including CI job setup overhead. Each declares
seven mutations through the same runner. Coverage assertions require all 28
unique names exactly once across all four partitions. The first document also
runs the behavior suite; the others run only the selected campaign. At most two
documents run concurrently. Conditional CI uv setup covers all four documents.

Author preflight corrected the stale-render reader mutation to preserve its
actual file mode. A failed baseline in that test now raises a framework error,
which cannot count as red. The earlier campaign's stale-render claim is not used
as evidence for this boundary. The corrected partitions must establish it.
The three new formatter/EOF targeted tests pass; complete partition validation
remains pending. The next focused round is Critical, counts carried.

### Partition validation and focused round 6, Critical

All four documents passed on the common-formatter tree: partition 1 ran 41 tests;
the other documents each ran one campaign test. Elapsed local document times at
two concurrently were 251, 230, 250 and 251 seconds. The corrected stale-render
plant is included in these results, with successful baseline required before the
FIFO boundary. Each partition verifies all four groups cover 28 unique variant
names exactly once. Existing monolithic/intermediate runs remain superseded.

All five focused aspects completed with exit zero and valid nonempty JSON.
Snapshot comparison found no lasting scope changes. Code, errors, comments and
types had no findings. Tests reported two takes:

1. Reviewer `important`, "Uncited: Input path containment lacks negative
   regression coverage." Own: Important; weakening normalization could escape
   private input materialization. Take: existing absolute and parent-traversing
   inputs must fail with normalization diagnostics, before materialization,
   without changing sources or records. Extend the manifest-validation variant
   to weaken normalization and require this named assertion too. Review again:
   no, tests only.
2. Reviewer `important`, "Uncited: Process cleanup tests do not exercise
   TERM-to-KILL escalation." Own: Important; TERM-ignoring descendants could
   survive without an independent regression. Take: an owned child installs
   TERM ignore before reporting readiness, then redirects both streams. Assert
   it is gone, its leader reaped, and cleanup succeeded. The cleanup variant now
   removes only KILL escalation, so TERM handling alone cannot satisfy the test.
   Recorded-PID cleanup handles the deliberate weakening. Review again: no,
   tests only.

Both targeted tests pass. The updated suite has 43 primary tests and a 31-test
baseline/restored guard set, still 28 variants across four partitions. Only
partitions 1 and 3 contain changed guard variants; rerun them before the final
full suite. No production behavior changed in these takes. The active Critical
threshold had no findings, and test-only takes do not advance the loop. End
state: clean at Critical. No findings were downgraded or left unresolved.

### One trim round

`trim-comments` and `trim-text` ran in parallel through fresh read-only Codex exec,
`gpt-6.1-sol`, low effort, window 872000, approvals never and web disabled. Both
exited zero with nonempty replies that classified every requested file and read
past prompt setup. Raw replies are preserved as `trim-comments.txt` and
`trim-text.txt`. Comments proposed no changes. All five prose proposals were
taken in the runner reference: active subjects, shorter repeated wording and one
split instruction. No policy, code, fenced example or historical evidence
changed. There were no declined or incomplete proposals. Source comments were
unchanged, so no comment-token or AST equivalence check was needed. No additional
trim round will run. Updated campaign partition validation remains pending.

### Final affected campaign reruns

Updated partitions 1 and 3 passed after the test-only takes: the primary document
ran 43 tests and the other ran its campaign test. Elapsed local document times
at two concurrently were 256 and 231 seconds. The other two partitions already
passed and have no changed guard variants; the final full suite will run all four
with the common 31-test baseline/restored set. No source behavior changed after
focused review round 6.

### Baseline Semgrep

Semgrep 1.180.0 ran in an owned disposable `git clone --shared` at head
`2fbe1170`, with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, two jobs and
baseline `e0ad16d5095e9c445be45bde5ef622ad8f5f45cb`. The standard `p/default`
baseline scan ran 85 applicable rules on 50 files. The extensionless runner also
received an explicit baseline scan with all 242 Python rules from that same
configuration and `--scan-unknown-extensions`. Both exited zero, with zero
findings, empty error lists and complete reported parsing. Default exclusions
include test and generated paths; the production runner has explicit Python
coverage. No full-scan/changed-line substitute was used. `semgrep.json` preserves
coverage, config fingerprint and outcomes.

The registry CLI configuration download timed out before any scan; curl then
fetched the same official configuration successfully. No scan was called clean
while unavailable. Pre-suite lint subsequently found formatting in fifteen raw
review JSON files; Prettier corrected whitespace only. Reviewer labels and values
are unchanged. The lint/validation rerun completed with exit zero. Existing CLI advice did not
change its successful verdict.

### Version check before full suite

The repository `check-versions` workflow confirms default branch `main` and the
unchanged fixed merge base. Only `plant-defects` has canonical plugin changes:
1.0.5 to 1.1.0 is a forward minor capability bump. Marketplace coverage and version
ownership pass; source Codex manifests, where present, agree with their Claude
manifests, and the generated plant-defects manifest agrees. No hooks file or
manifest hooks entry changed. Final tidy must retain this exact tree.

### Full-suite load-gate pause

The single waiting command did not acquire the tooling lock or start tests.
Its prescribed process scan continued to match real SL-VF heavy-suite-lock runs
and queued runs. TOOLING proposed using the machine-wide queue instead at
`20261104T032406Z` and asked to stop the waiting command. Its owned controller
PID 78647 was verified and stopped with TERM; it exited 143. Before stopping,
checks confirmed neither `full-suite.log` nor the tooling lock existed.

The proposed replacement changes the direct brief's required ordering, which
first waits for the specified `pgrep` scan to clear. The worker requested a
relayed user exception before replacing that ordering. No queued replacement
command has run, and the once-only full suite remains unrun. This is a load-gate
pause, not a test pass or a code-review finding. No outside process was stopped.

### Conductor scheduling amendment

At `20261104T032527Z`, TOOLING clarified it authored the worker brief and amended
its scheduling procedure. Suite scheduling is operational, within the already
open full-suite authorization. The amendment replaces the argv-based wait with
the existing machine-wide heavy-suite queue, preserving serialization with
SL-VF suites and the local two-job limit. No additional user gate remains.

The amended command takes `~/Work/projects/.locks/tooling-full-suite.d`, checks
`pmset -g therm`, then runs, from this worktree:

```bash
~/Work/sl-vf/bin/suite-lock run heavy -- env SCRUT_JOBS=2 make test-all
```

The owned tooling lock releases when the command exits. Heavy dispatch was
verified in the existing `suite-lock` source: it delegates to the process-held
heavy lock, without Compose teardown. The runner has no third-party Python
dependencies. No outside process is stopped or lock overridden. The stopped
argv-gate command never ran the suite; the queued command remains its single
full-suite run. Thermal warnings still hold the run and must be reported.

### Single full-suite outcome

Under the conductor-amended queue, `make test-all` completed with exit zero:
80 Scrut documents, 2,225 testcases succeeded, zero failed and zero skipped.
The script's exit file and observed process exit both report zero. The heavy
helper reported release, and the wrapper released its owned tooling lock.
No thermal or performance warning was reported at admission. No second full-suite
run was started.

All four checked-runner documents passed in that run: partitions 2, 3 and 4 took
245, 241 and 256 seconds; the primary 43-test document took 285 seconds. The
31-test baseline/restored guard set and 28 declared variants ran through all four
partitions. The prescribed output and environment guards are included in the
full pass. A pre-existing validator-skills document took 313 seconds locally;
the five-minute target is specified for Ubuntu, whose CI result is separate.
No runtime ceiling was raised.

### Final lint invocation

`lint-and-fix --no-push` is the final local check before tidy and publication.
Markdownlint runs in check mode: the documented `make format` wrapper invokes
`markdownlint-cli2 --fix` over all Markdown, including completed plans, whereas
`docs/AGENTS.md` says not to rewrite historical completed plans while formatting
current documentation. The lint skill requires the safe check-mode downgrade.
Prettier also stays in check mode: its broad fix command includes Scrut files,
which the loaded workspace instructions say never to reformat. Its ignore file
already protects completed plans and generated mirrors, but not Scrut snapshots.
Shfmt alone retains safe fix mode, using the repository's shell-script list. `make lint validate` verifies all required formatting, shell,
workflow, fixture, JSON and plugin checks. No enforced check is omitted.
