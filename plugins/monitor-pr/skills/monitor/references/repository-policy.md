# Repository policy and shared Copilot intake

Both monitor-pr skills load this reference before their workflow. It governs every
entry, including standalone resolver calls, resumed checkpoints, callbacks,
Dependabot PRs and error recovery. These rules take precedence over the default
workflow's categories, mandatory public summary, waits and merge continuation.
Stricter loaded instructions still apply. A permission gate never grants approval.

## Select policy before intake

Resolve the explicit PR repository as `OWNER/REPO` from the PR URL and verify it
with `gh repo view OWNER/REPO --json nameWithOwner`. Use the PR's base repository,
including for a fork PR, rather than the current directory or head fork. Unknown
identity stops action; no cached autonomous mode or option can override selection.

At each entry, supply `restrictions.repository` to `merge-flow prepare`, together
with the current `noFix`, independent `copilotPaused` and `blockedActions` values.
A missing repository permits metadata observation only. The helper selects
`swing-left` case-insensitively as client mode. `cboone` always pauses Copilot:
report metadata-observed arrivals and URLs to the conductor; do not read bodies,
assess, dispatch the resolver, reply or resolve. Never request or wait for a
review there. Other owners retain the default workflow under loaded restrictions.

Standalone resolver invocations prepare the same watch state as monitor calls.
Use a fresh PR metadata snapshot with number, URL, head SHA, state and draft
status. Resolve the package-relative `merge-flow` alongside the feedback helper.
Pass `--watch-state WATCH_STATE_JSON` on every helper call, even standalone;
monitor children receive and revalidate the parent's `WATCH_STATE_FILE`.
Reprepare restrictions from current instructions on resume, retaining dispositions
but clearing old action authority unless the conductor confirms it still applies.
Never use an old policy object's permissions as new authority.

## One intake for both skills

Use the existing resolver step 1 for all available feedback: `fetch`,
`fetch-reviews` and `audit`, with pagination and complete raw bodies. The monitor
step 3 probe is the same intake, not a separate client parser. In client mode,
read every unprocessed review available, including older-head feedback, rather
than requiring a review of the latest head. Recheck findings against current code.
A review ID, source URL, thread/comment ID or normalized path plus finding excerpt
identifies the source. Deduplicate body restatements of threads and retain exact
source links. Audit items outside threads and bodies receive the same assessment.

In client mode, read and verify private prior dispositions from the PR's durable
local ledger instead of public summaries. Record each review ID once, classification,
reviewed SHA, source identity, assessment and current-code verification. Immutable
body findings do not become new work because their text remains present. Preserve
unsettled findings across resumes. Notices and unclear bodies are unavailable
review evidence; report them without retries or requests. Failed, empty or partial
API results never mean no feedback. Keep existing bounded read-failure handling.

## Client assessment and round authority

Never wait for or request Copilot, including after a push, for a notice, under
`--confirm-clean` or under `--no-fix`. `--rounds`, `--triage-after`, confirmation
and `DEFER_SEVERITIES` cannot replace client policy. A successful intake with no
review means `no review available`, without claiming clean Copilot coverage.

For each finding, record four calls in the ledger and send the proposal to the
conductor: the reviewer's label verbatim; our impact severity (Nit, Important or
Critical, with a reason for a difference); take or record; and whether the
proposed edits change behavior and require another round. The worker proposes;
the conductor decides. No category, Copilot label or severity flag authorizes
edits, replies, deferral issues or resolution. Missing or conflicting decisions
stop at the conductor. No independent worker question goes to the user.

Keep one persistent Copilot loop count across pushes and resumes. Count each
arriving automatic review ID once, including each push's automatic review, even
when it reviews the same SHA. Start with one Nit round, then up to two Important
rounds, then Critical-only rounds without a cap. Advance only when the previous
round took a finding at its threshold and those fixes changed behavior. Tests,
comments or docs alone do not advance it. Take findings at threshold; below it,
take missing tests/docs for the branch's new behavior or trivial local fixes and
record the rest. The conductor decides each call. Repeated instances of a class
already fixed stop for a structural decision before severity deferral. End with
`clean at Nit`, `clean at Important`, `clean at Critical`,
`ended: fixes changed no behavior` or `stopped: recurring defect`, as warranted;
never call unavailable evidence clean. Later arrivals after an ended loop go to
the conductor for a decision, preserving the count rather than starting over.

After the conductor's decision, one go-ahead from the user per Copilot round
covers its agreed fixes, push, short factual replies and fixed-thread resolutions.
Record its exact source, PR, review IDs, starting head and agreed scope. A generic
monitor invocation, plan approval or old round is insufficient. In prepared
restrictions, `clientRound` is null until that go-ahead; once received it contains
`repository`, `authority` (the source), `prNumber`, full `head` and numeric
`reviewIds`. The approved repository identity must match the resolved target.
The helper rejects missing fields and a snapshot with a different PR or head.
Set watch-state `reviewId` to the selected review; the helper requires it to be
in the authorized IDs before processing.
A new review is another round and needs its own go-ahead. After the authorized
push, refresh the PR head, verify it equals the published commit, and reprepare
with that head using the same authority for remaining replies/resolutions only.
An unexpected remote head invalidates authority; stop and report.

## Apply decisions within the existing resolver steps

Use the existing categorization and fix-validation steps under the conductor's
calls and the round go-ahead. Their default automatic category actions do not
apply in client mode:

| Existing step                     | Client behavior                                                                                                                                                                     |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Preconditions and dependencies    | Read-only assessment needs no fixing skills or clean tree; require both before authorized edits.                                                                                    |
| Categories and sibling checks     | Assess every category privately; no automatic instruction edits, issue filing, replies or closure. Propose description/instruction changes to the conductor.                        |
| Fix, consistency, review and lint | Execute only the agreed scope; use the project's local review order and persistent per-reviewer rounds. Record failures and stop each loop as required.                             |
| Push                              | Use only the current round's go-ahead; preserve push validity checks. No automatic sync-and-retry on a moved remote.                                                                |
| Replies                           | Short factual text only: the fixing commit, or why a finding was left. No templates that add praise, agreement or a public design discussion.                                       |
| Resolve and recover               | Resolve only a finding with a verified fixing commit in the fresh PR head, using `ADDRESSED`. Leave unfixed Nit, Incorrect, Deferred and merely obsolete threads open for the user. |
| Final summary and no-op recovery  | Persist the ledger and report to the conductor. Never post a PR summary, even on failure or a no-op. A public comment is never required for client completion.                      |

Before client resolution, record `fixedThreads[THREAD_ID]` as the fixing commit
in watch state. The helper requires `--reason ADDRESSED`, checks commit ancestry
and rereads the remote OPEN state and head immediately before every mutation,
including between a combined reply and resolution. The live thread must belong
to the approved repository, PR and selected review, remain unresolved, and have
a Copilot opener. Missing or mismatched target evidence blocks the write. Each mutation uses one
validated state snapshot, and each resolution checks its fixing commit against
that snapshot's head before the live query. A category
alone cannot provide that evidence. An earlier fix may qualify after verification.
For no-fix findings use reply alone under round authority, and leave the thread
open. Verify post-write state and record actual results separately from intent.
After an uncertain write, inspect before retrying; do not duplicate a reply.

CI repairs, branch synchronization, bot rebase posts, issue filing and description
updates are outside the Copilot round's authority. Diagnose and propose them to
the conductor under their own gates. The policy blocks monitor's automatic sync
and repair routes for clients; hand those proposals off rather than bypass it.
Dependabot branches still receive no direct push.

## Readiness and handoff

Client readiness uses checks, PR state and mergeability from the same snapshot.
Copilot is optional coverage: all feedback actually read must have a recorded
assessment and conductor decision, with any outstanding round gate reported.
Open recorded findings remain open; do not use zero open threads or a public
summary URL as the readiness condition. An unfinished authorized fix or a failed
required read prevents a readiness claim. Missing reviews do not cause waiting.

At readiness stop at the draft decision. Cancel scheduling and merge watches,
report draft state, head, checks, mergeability including `BLOCKED`, human review
state, available or unavailable Copilot coverage, open findings, round counts and
end states, actions performed, commits, checks run and the exact closed gate.
Send one summary to the conductor and save it in the PR ledger. No summary PR
comment, reviewer request, draft-ready offer, approval watch, merge offer,
auto-merge, merge or suggested next steps. If a merge is observed before this
handoff, report it to the conductor for branch cleanup; never enter default step
8's sync or peer-notification paths. A client report uses the parent contract's
operational status separately from review-loop end states.
