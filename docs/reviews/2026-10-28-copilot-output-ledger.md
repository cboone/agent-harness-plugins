# Copilot resolver output review ledger

## Authorization and scope

The brief authorizes building through a ready PR for the resolver output and
consistency/sibling fixes. TOOLING merges. The prior seven-commit branch was read
without changing it. Corepack immutable installation passed. Origin is
`cboone/agent-harness-plugins`, active and not a fork. Both issues are in progress.

## Implementation

The summary and reply design is ported to monitor-pr. Current reviews, sibling
chains and late-round deferrals remain. Matching monitor documentation, summary
fixtures, scrut contracts and a stubbed sweep fixture are updated. The audit
helper does not parse summaries and requires no change.

## Checks

Structural loop: two rounds, clean at Important. Focused loop: four rounds, clean
at Critical, with both recurrence calls resolved by TOOLING and counts preserved.
Final trims, baseline semgrep, lint and check-versions complete. Full make
test-all passed: 34 documents, 1394 cases, zero failed or skipped. Targeted suites:
65 resolver, 10 summary/sweep/reply/policy, 8 real-history ancestry cases. All 24
effective plants detected their intended checks and restored green. Tidy and PR
publication remain.
Prose source canaries are not claims about model compliance.

## Plant table

| Planted defect                                         | Instrument                                   | Observed result                      | Regression coverage                 |
| ------------------------------------------------------ | -------------------------------------------- | ------------------------------------ | ----------------------------------- |
| Drop new-marker recognition                            | Summary filter                               | Intended test failed; restored green | resolve-copilot-threads             |
| Move table outside details                             | Summary examples                             | Intended test failed; restored green | copilot-summary-contract            |
| Ignore diff failure                                    | Sweep git stub                               | Intended test failed; restored green | copilot-summary-contract            |
| Ignore PR-body failure                                 | Sweep gh stub                                | Intended test failed; restored green | copilot-summary-contract            |
| Remove workflow-failure push gate                      | Instruction canary                           | Intended test failed; restored green | copilot-summary-contract            |
| Permit resolving a pending sibling                     | Instruction canary                           | Intended test failed; restored green | copilot-summary-contract            |
| Hide successful sweep inputs                           | Successful-read output                       | Intended test failed; restored green | copilot-summary-contract            |
| Restore resolve-only command                           | Command contract                             | Intended test failed; restored green | copilot-summary-contract            |
| Treat ancestry exit 128 as negative                    | Recovery block case                          | Intended test failed; restored green | superseded by real verify-fix tests |
| Ignore recovery fetch failure                          | Recovery block case                          | Intended test failed; restored green | superseded by real verify-fix tests |
| Ignore reply failure in subshell                       | Reply operation trace                        | Intended test failed; restored green | copilot-summary-contract            |
| Ignore resolution failure in subshell                  | Reply operation trace                        | Intended test failed; restored green | copilot-summary-contract            |
| Resolve before replying                                | Reply operation trace                        | Intended test failed; restored green | copilot-summary-contract            |
| Duplicate timing policy in templates                   | Policy canary                                | Intended test failed; restored green | copilot-summary-contract            |
| Copy policy into a reference                           | Policy canary                                | Intended test failed; restored green | copilot-summary-contract            |
| Remove step-4 policy owner                             | Policy canary                                | Intended test failed; restored green | copilot-summary-contract            |
| Require an upstream for verification                   | Real no-upstream history                     | Intended test failed; restored green | copilot-fix-ancestry                |
| Compare against unrelated upstream                     | Real unrelated-upstream history              | Intended test failed; restored green | copilot-fix-ancestry                |
| Skip missing-object PR ref fetch                       | Real shallow missing-object history          | Intended test failed; restored green | copilot-fix-ancestry                |
| Drop multiline reply payload                           | Payload-validating gh stub                   | Intended test failed; restored green | copilot-summary-contract            |
| Change reply thread target                             | Target-validating gh stub                    | Intended test failed; restored green | copilot-summary-contract            |
| Change resolution thread target                        | Target-validating gh stub                    | Intended test failed; restored green | copilot-summary-contract            |
| Ignore failed ancestry read                            | Git read-error stub after real object checks | Intended test failed; restored green | copilot-fix-ancestry                |
| Skip shallow-history completion with endpoints present | Real incomplete-history case                 | Intended test failed; restored green | copilot-fix-ancestry                |

## Remaining work

Exact-tree tidy; ready PR and green checks; review précis to TOOLING. No push
or PR exists at this checkpoint. Building stops at the PR; TOOLING merges.

## Structural round 1, Nit

Fresh read-only `codex exec` runs, gpt-6.1-sol/high/872000. Both exited 0,
returned non-empty valid JSON and read every canonical scoped file. No lasting
changes. Anti-pattern schema and shape validation passed. Simplify report shape
passed. Reviewer labels and assessment:

| Reviewer finding                                   | Reviewer label | Severity and disposition                                                                                         | Review again  |
| -------------------------------------------------- | -------------- | ---------------------------------------------------------------------------------------------------------------- | ------------- |
| Successful sweep reads hide both comparison inputs | important      | Important: captured data never reaches the comparing agent; take, print both inputs and assert successful output | Yes, behavior |
| Step 3 command omits promised reply                | important      | Important: resolve-only skips a required deliverable; take, use reply-and-resolve and pin command                | Yes, behavior |
| Legacy remaining-action heading named incorrectly  | nit            | Nit: take local documentation correction to Remaining Required Action                                            | No by itself  |
| Flatten summary-contract AWK parser                | nit            | Nit: take local readability change, preserving predicates                                                        | No by itself  |

The static Bash checks passed in the review. Network metadata was inaccessible
to the reviewers; this worker verified it before review. Unrun tests were listed,
not reported as clean. Continue structural round 2 at Important after fixes.

## Structural round 2, Important

Anti-patterns and report-only simplify both exited 0 with complete, valid,
non-empty results and no Important findings. All canonical files were read;
no lasting changes. The two Important findings from round 1 were corrected.
End state: clean at Important. No recurring defect found.

Additional plants: removing displayed sweep inputs failed the successful-read
contract; restoring resolve-only failed the thread-command contract. Both were
restored and all six contracts passed. The review remains read-only; full test
and validator execution belongs to this worker.

## Focused round 1, Nit

Installed review-pr-with-codex helper, gpt-6.1-sol/high/872000, read-only code,
errors, tests and comments aspects in parallel. Types omitted: no type definition
changed. All four exited 0 with valid non-empty schema-bound output. Snapshot
`505f4c817b5387e709bed1568984261648b5a259`; no lasting changes or scope movement.
The repository-local helper refused its own checkout before launching any aspect;
the installed copy supplied the required isolation.

| Reviewer finding                              | Reviewer label | Severity and disposition                                                                                                     | Review again            |
| --------------------------------------------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| Fixture uses eval                             | important      | Important: explicit Bash Important rule; take, source the extracted block from an owned temporary file                       | Yes with behavior fixes |
| Fatal ancestry errors treated as absent fix   | important      | Important: read failure could bypass workflow gate; take, distinguish exits 0 and 1 from errors and check fetch              | Yes, behavior           |
| Missing executable reply-and-resolve failures | important      | Important: missing tests for newly required boundary; take, stubbed ordering/reply failure/resolve failure tests             | No by itself            |
| Unpushed-fix recovery contradicts entry guard | important      | Important: promised recovery cannot pass entry guard; take, require earlier work to have reached PR and report unpushed work | Yes, agent behavior     |
| README overstates reply-link guarantee        | suggestion     | Nit: take local wording qualification, links where applicable                                                                | No by itself            |

These are distinct from the structural round's hidden-output and resolve-only
command defects. No recurrence. The first fixture run exposed an EXIT-trap local
variable lifetime error; fixed with a script-owned directory variable. All 13
summary, sweep, ancestry and reply contracts now pass. New stubs reject unexpected
calls and the reply fixture refuses to run unless gh resolves to its local stub.

Next: plant the new boundaries, focused round 2 at Important, then trims and
remaining publication checks. No push has occurred.

## Focused round 2, Important

All four installed-helper aspects exited 0 with complete schema-valid results,
no Important or Critical findings, and unchanged scope/tree. Snapshot
`f8382038d7a37325281c5a5d1a6642d591ca32bc`. End state: clean at Important.
The comments aspect returned two suggestions: no-op omission contradicted the
No concern example; Incorrect replies claimed an existing instruction was added.
Both assessed Nit and taken as local documentation corrections for this change's
own boundaries. No additional round: documentation only. No recurring defect.

The two fixture runner paths are registered identically in Makefile and CI,
per tests/AGENTS.md. No workflow permissions changed.

Five additional effective plants failed the intended guards: ancestry exit 128
misclassified, fetch failure ignored, reply failure ignored, resolution failure
ignored, and resolve-before-reply ordering. Original `send_reply ... || true`
plant left behavior unchanged because die exits the process; the effective plant
isolated the call in a subshell before ignoring it. Do not count the unchanged
plant as a detected defect. All 13 restored contracts passed.

Next: read-only trims, baseline semgrep, lint-and-fix, full suite, version check,
tidy, ready PR and green CI. Both review loops ended clean at Important.

## Trim pass and recurrence stop

Both read-only Codex trim runs exited 0 with non-empty replies satisfying the
file-list and proposal-table format. Model gpt-6.1-sol, effort low, window 872000.
Text classified all six scoped prose files; comments classified all three new
fixtures. No edits or checks by the trim runs; this worker applied no proposals.

The text pass flagged a second instance of the recovery contradiction corrected
in focused round 1. `Reply Templates` still says an unpushed linked commit waits
for step 8 "whichever run made it". Step 4 instead stops when earlier unpushed
work makes HEAD differ from HEAD_SHA. Following the template's recovery rule
cannot pass the entry guard, the same defect class as focused round 1's finding.

| Reviewer label             | Severity                                                   | Take or record                                                             | Review again                                                            |
| -------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Flag, no severity supplied | Important: recovery instructions contradict the entry gate | Record unresolved; stop for design decision, do not patch another instance | After conductor design call, continue existing counts; never reset them |

Recommended design decision: keep the existing entry guard; make step 4 the sole
owner of reply timing and prior-run recovery. Reply Templates should describe
format and link syntax and refer to that rule, rather than repeat recovery policy.
This stays within the brief, but the recurrence stop requires the conductor call.

The other text flag is the unqualified "every thread ... in one call" introduction
versus resolve-only retries and pending siblings. Assess Nit: nearby explicit
exceptions govern; include it in the same consolidation. No reviewer Important
or Critical label was downgraded.

Unapplied trim proposals: qualify the README sentence with a shorter decision
reply description; shorten the earlier-run introduction; remove three sentences
explaining summary-format benefits; shorten the reply-before-resolve sentence;
shorten the sweep continuation-marker comment and the GraphQL stub header.
Preserve the recovery and sibling exceptions when applying any proposal. No cut
material requires relocation. No new trim round is needed.

End state: stopped: recurring defect. All current work is committed. TOOLING owns
the design decision and restart. The worker must not continue into semgrep, lint,
tidy or publication while stopped. Raw reports remain in
`/tmp/596-reviews.MhAKB0/trim-text.md` and `trim-comments.md`; this section records
the actionable findings without depending on those temporary files.

## Conductor decision and continuation

TOOLING approved the proposed structural design in the session message: keep the
HEAD_SHA entry guard; step 4 owns prior-run timing and recovery; all other copies
point there. The existing go-ahead stands and no restart is needed. The recurrence
was not parking: TOOLING restored the in-progress labels, verified present on
both issues; leave them in place through the PR.

Step 4 now owns eligibility, earlier replies and commits, checked recovery reads
and operation failures. Step 1c, step 3, the critical command explanation, step 8,
Reply Templates, success criteria and the README refer to step 4 rather than
restate recovery policy. The summary's failure example describes the next action
through that reference. Swept every canonical Markdown file under monitor-pr,
including its references; monitor skill and checkpoint had no policy copy.

Added a source canary scanning all plugin Markdown for unique policy headings
inside step 4 and known duplicate timing/recovery formulations elsewhere. This is
practical regression coverage for the observed recurrence and copied policy, not
an arbitrary-paraphrase detector. Semantic drift remains a review obligation.
All 14 targeted contract cases pass. Accepted the prior trim's two fixture comment
rewrites, shortened the earlier-run introduction, and removed three redundant
format-benefit sentences. Preserved policy exceptions and commands.

Continue focused review at round 3, the second Important round, because the
consolidation changes documented behavior. Structural count stays at two rounds.
After that review, run the requested trims and remaining validation/publication
steps. No loop budget resets.

## Focused round 3, second Important round: recurrence stop

All four installed-helper aspects exited 0 with valid non-empty schema-bound
results. Model gpt-6.1-sol/high/872000; read-only. Snapshot
`10e2f57d86e3dd03ca27900d2fb563929b65b6f9`. Scope and tree unchanged.
Errors and comments returned no findings. Code returned one Important; tests
returned one suggestion. No findings were applied after this review.

| Reviewer finding                                                | Reviewer label | Severity and disposition                                                                                                              | Review again                                                              |
| --------------------------------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Recovery correctness: Check ancestry against the actual PR head | important      | Important: an unrelated upstream can falsely confirm a fix is on the PR; record unresolved and stop for recurring verification defect | A behavior fix requires the next round, now Critical-only; preserve count |
| Reply payload coverage omits decision text and target thread    | suggestion     | Nit: missing coverage of the change's own boundary; take after the stop is resolved                                                   | Test-only edits need no further round by themselves                       |

The recovery block uses `git merge-base --is-ancestor COMMIT '@{u}'`, but the
HEAD_SHA guard does not establish that the checkout's upstream identifies the
PR branch. A missing upstream fails despite a valid local PR head; an unrelated
upstream can return 0 for a fix absent from the PR. This is another configuration
path of the recovery ancestry check modified in focused round 1, which corrected
its fatal-error classification. Under the recurrence rule, stop instead of
patching this next instance.

Recommended structural decision: make the recorded PR HEAD_SHA the only ancestry
authority. The entry guard already verifies local HEAD equals it. Check required
commit objects and ancestry against that exact head with checked reads; do not
infer the PR target from an upstream or a generic fetch. Add executable regression
cases for a valid checkout with no upstream and one tracking an unrelated branch.
The same exact head should govern every earlier-fix verification site.

The tests suggestion can be closed by validating both mutations' threadId and a
multiline decision reply with a commit link in the local gh stub. It is recorded
without changing the fixture while stopped.

The consolidation's three plants each failed the intended policy canary: timing
copy in Reply Templates, copied heading in a newly created reference, and removed
step-4 policy owner. The temporary reference was removed by its exact recorded
path. Restored 14-case contracts passed. The source-canary limitation remains:
it detects known wording and copied headings, not arbitrary paraphrases.

End state: stopped: recurring defect. No push or PR. In-progress labels stay on
both issues: this is a recurrence decision, not parking. The next focused round
after a behavior fix is Critical-only, since both Important rounds are spent.
The requested fresh trims, semgrep baseline, final lint, full make test-all,
check-versions, tidy and publication remain undone.

## Authoritative-head structural call

TOOLING approved the ancestry proposal in the session message: HEAD_SHA is the
only ancestry authority; verify needed commit objects, fetch the PR head by its
ref for missing objects, never infer the target from an upstream or generic fetch.
The existing go-ahead stands. Also take the payload-testing Nit and continue at
Critical-only with the count preserved.

Extended the existing resolve-copilot-threads helper with verify-fix rather than
adding another tool. It checks objects and history, fetches the explicit
refs/pull/N/head from the PR repository when needed, verifies the fetched head
matches the recorded SHA, and returns true/false only after a successful ancestry
read. Shallow history is completed before comparison; fetch, missing-object,
moved-head and ancestry-read failures remain workflow failures. Step 4 owns this
command and directs every earlier-fix verification site to it.

Replaced mocked ancestry text-block tests with real local Git histories: no
upstream, unrelated upstream, missing reachable commit, unknown commit, failed
fetch and moved head. GitHub access resolves to a checked local stub. Registered
the runner identically in Makefile and CI. Reply stub now validates both mutation
targets and the exact multiline decision payload containing a commit link.

Targeted checks before planting: ancestry 6 passed; summary/sweep/reply/policy
10 passed; existing resolver 65 passed. ShellCheck passed on changed helpers and
fixtures after annotating literal Markdown backticks in sample reply data.
Next: commit the checks, plant the requested boundaries, then focused round 4 at
Critical-only. Structural count remains two rounds.

## Focused round 4, Critical-only

All four read-only installed-helper aspects exited 0, schema-valid and non-empty.
Model gpt-6.1-sol/high/872000. Snapshot
`ffdd614736c02d7e37ae22eec8bf223aebc3220e`; no lasting changes or scope movement.
Code, errors and comments found nothing. Tests returned two suggestions, assessed
Nit: missing fatal ancestry-read coverage and shallow history with both endpoints
present. Both are tests for this change's own boundaries and are taken. No new
code defect or recurrence was reported. End state: clean at Critical.

The six requested plants all failed intended checks: adding an upstream
requirement, comparing against an unrelated upstream, skipping the PR ref fetch,
dropping reply content, changing the reply target and changing the resolve target.
Restored 6 ancestry and 10 contract cases passed. Existing resolver suite: 65 pass.

Added the two test-only takes: a checked Git stub fails merge-base with 128 after
real object reads; a shallow repository contains both endpoints with the ancestry
connection beyond its shallow boundary. Their own plants are next. Test-only edits
need no further review round. Continue to fresh trims as requested by TOOLING.

## Final trims and test sensitivity

Both fresh trim runs exited 0 with non-empty replies in the required classified-
file and proposal-table format. Read-only gpt-6.1-sol/low/872000. Text classified
all nine scoped prose files, comments all seven script/fixture files. Applied the
round-count sentence trim, two test-prose trims and two fixture header trims.
Retained the sweep-marker and real-Git-delegation comments because they explain
what each instrument verifies, not just the adjacent command.

Text flags: the step-4 reply introduction already has its eligibility and retry
exceptions in that same policy section, so it introduces no conflicting recovery
path; record as non-actionable, not a recurring defect. The current Checks and
Remaining work sections above are maintained status and were refreshed; historical
round records stay unchanged. The worker verified ownership/archive live at
continuation despite the trim sandbox's unavailable network. No cut material
needs relocation.

The two final ancestry plants were rerun only after a green eight-case baseline.
The first fixture attempt had refused its stub because Bash cached real Git;
hash -r fixed the fixture. Initial plants made against that non-green fixture do
not count as sensitivity evidence. Effective reruns: ignoring ancestry exit 128
failed its error case; skipping shallow-history completion with endpoint objects
present failed its true-ancestry case. Restored all eight passed. No production
behavior changed after the Critical-only review; only tests, comments and prose.

## Baseline scan and lint-and-fix

Semgrep scan completed in a disposable shared clone at source head 3445dca9,
comparing against origin/main merge base 06a529a3b2508b138913d6ff6f058ed4930c7fff.
Command used scan --config auto --baseline-commit, without --metrics off, with
SEMGREP_REPO_NAME=cboone/agent-harness-plugins. Exit 0, 165 rules, 10 changed
targets, zero findings, empty errors, approximately 100 percent parsed lines.
Sixteen files followed the configured ignore patterns. Test fixtures are covered
by the executable tests; do not imply Semgrep scanned every changed file.

Lint-and-fix --no-push used the project commands. Markdown/Prettier fixers stayed
in check mode because their broad globs include protected scrut files. The first
format check required four-backtick outer fences around two scrut blocks whose
commands contain triple backticks. Applied only those delimiters by hand, with no
command or expected-output change. The affected ten-case document passed again.
The recheck passed Markdown lint (736 files, zero issues), Prettier, ShellCheck,
shfmt and actionlint. No required tool was skipped. Lint fixes are committed;
final verification includes the mandatory make test-all run next.

## Final validation and publication checkpoint

Mandatory make test-all exited 0: all 34 scrut documents passed, 1394 test cases
succeeded, zero failed and zero skipped. Its lint and validation stages also
passed, including generated-mirror drift and cross-references. Test concurrency
was four documents; none were excluded. This is full-suite evidence, not a
restricted-suite substitute.

Repository check-versions workflow: default branch main verified live; refreshed
origin/main merge base remains 06a529a3b2508b138913d6ff6f058ed4930c7fff. Only
monitor-pr changed, from 3.1.0 to 3.2.0, an appropriate minor for the reporting
contract and verify-fix command. All 60 registrations match canonical plugin
directories, all manifest versions are valid, present Codex manifests match,
and marketplace entries/metadata contain no versions. Live origin/main still has
monitor-pr 3.1.0 and no drift in this plugin or the new tests. All clear.

Lint status: success. Commit: 999d593f. Unresolved or skipped: none. Check-only by
project policy: Markdown lint and Prettier; scrut files were never sent through a
write-mode formatter. Caller resume target: tidy and ready PR publication. Full
make test-all supplied the final check-mode verification, including the CI-only
validator requirements that also run locally.

The implementation plan is complete and moves to docs/plans/done. Tidy must keep
the exact tree: back up the current branch, soft-reset to the recorded merge base,
create logical signed feature, test and documentation commits, then require
`git diff --quiet <backup> HEAD` and a clean working tree. No pushed history is
rewritten. The ready PR closes both requested issues; no Copilot review is
requested or awaited, and this worker never merges.
