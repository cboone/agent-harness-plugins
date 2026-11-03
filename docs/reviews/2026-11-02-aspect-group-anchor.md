# Aspect group anchor review ledger

## Scope and design

[Issue 716](https://github.com/cboone/agent-harness-plugins/issues/716), branch
`fix/716-aspects-group-anchor`, merge base
`2a694d7048750199ce8d292043156a6046299fd6` from `origin/main`.
Prior process-group ledger read in full. Plugin 2.3.3 to 2.3.4; generated mirrors
rebuilt from canonical sources.

The existing child-only Perl wrapper forks an idle anchor, with no job control.
The anchor holds a private inode lock and ignores TERM, INT, QUIT and HUP.
The lock authorizes group signals independently of recycled PIDs; parent
ownership still covers leaders before anchor setup. Cleanup releases an anchor
when it is the only active group member. Active members without continuity
evidence cause incomplete cancellation, without further group signals.
Bounded escalation and retained cancellation artifacts remain in place.

## Iteration checks

- Initial affected Scrut document: 89/89 passed.
- Error-output guard: 102/102 passed.
- Environment-isolation: 51/51 passed.
- Affected document on macOS Bash 3.2: 89/89 passed.
- Bash 3.2 and Bash 5 syntax checks passed; affected ShellCheck passed.
- Thermal checks report no warning. At most two Scrut documents run concurrently.
- Pinned Yarn dependencies restored with `corepack yarn install --immutable`
  because this worktree initially lacked the node_modules state file.

## Structural loop

Nit round ran anti-patterns and report-only simplify in parallel through
fresh read-only `codex exec`, gpt-6.1-sol, high effort, 872000-token window.
No PR exists; lookup supplied by the calling session. No runtime tests authorized
inside reviewers. Both exited 0 with valid nonempty schema-matching JSON and
complete coverage of the implementation at ad61bc2e. Simplify had no findings.
A process ledger was committed while reviews ran; it was outside their pinned
implementation scope and is included in the next scope capture.

| Reviewer label                                                                       | Our severity and impact                                                                                | Take or record                                                                                  | Review again          |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- | --------------------- |
| important: Stale writes: release requests leave stale group-signalling authority     | Important: a cached lock read could authorize a signal after release and group reuse                   | Take: retire authority before release and KILL; all subsequent inspections are observation only | Yes, behavior changed |
| important: Absent or partial data: failed PID publication leaves an unmanaged anchor | Important: a failed buffered write or close could leave the anchor running without a usable PID record | Take: stop and reap the known child before reporting publication failure                        | Yes, behavior changed |

Added deterministic stale-read cases for release and KILL retirement. Added a
committed Perl close-failure probe that records the anchor and requires it to
stop. Fixture release assertions now require the exact released status rather
than accepting inspection errors. First Important verification remains unrun.

## Design gate

Post-fix inspection found that stopping or terminating the wrapper between fork
and parent-side PID publication could leave an anchor holding an empty locked
file. TOOLING approved the wrapper-local readiness design in mailbox sequence
000001 at 2026-11-02 11:28:07 PM EST. Its call distinguishes this internal pipe
from the parent-helper/aspect ownership handshake prohibited for issue 715.

Implemented that call: the anchor publishes its own PID with syswrite, then
sends one readiness byte through an anonymous pipe. The wrapper waits with a
five-second alarm before exec. Failed publication, readiness or timeout stops
and reaps the known child and reports failed setup without exec. The exec
leader PID and child-only setpgid are preserved. Added injected publication,
readiness, stopped-wrapper and timeout cases. Structural loop count remains Nit;
first Important verification follows these fixes, with no fresh Nit round.

The earlier post-review focused run passed 89/90: its publication-failure test
stopped its real anchor, but treated ps's expected exit 1 for an absent PID as a
test failure. Correcting that assertion produced a 90/90 scoped pass. The
post-review error-output guard passed 102/102. The readiness implementation now
requires its own scoped verification. Thermal checks report no warning.

## Defect plants

A recorded disposable shared clone restores the old leaderless group signal
path while retaining the anchor machinery. The committed recycled-group case
must reject that signal. The affected document returned Scrut exit 50 with
88/89 passing; only the recycled-group case failed. No real target is signalled
by the ps/kill fixture.

Additional direct committed-fixture plants returned exit 1: restoring the old
wrapper without an anchor, and removing normal anchor release. The latter's
fixture exit handler released its real anchor. The implementation tree was
never mutated by these plants. Review-fix plants ran against a recorded disposable clone of b1c80c00, after
all four unmodified setup probes passed. Every mutation parsed as Bash before
execution. None ran a real Codex review.

| Plant                                          | Instrument                          | Observed result                         | Coverage                                     |
| ---------------------------------------------- | ----------------------------------- | --------------------------------------- | -------------------------------------------- |
| Remove retirement markers                      | Committed release-race fixture      | Exit 1                                  | Stale lock read after normal release         |
| Remove retirement markers                      | Committed kill-race fixture         | Exit 1                                  | Stale lock read after group KILL             |
| Remove wrapper child stop/reap on failed setup | Committed timeout fixture           | Exit 4, cancellation artifacts retained | Anchor absence checked before helper cleanup |
| Bypass readiness failure gate                  | Committed readiness-failure fixture | Exit 1                                  | No exec without acknowledgment               |
| Skip child-side PID publication                | Committed stopped-wrapper fixture   | Exit 1                                  | Publication independent of wrapper progress  |
| Remove readiness alarm                         | Committed timeout fixture           | Exit 1, outer fixture bound enforced    | Bounded setup wait                           |

The exit-4 plant temporarily retained an anchor while its injected readiness
sleep continued. Post-plant ps inspection of all recorded anchor PIDs was empty.
No recorded plant anchor remains active. The clone was restored to its original
implementation after the plants.

## First Important round and recurrence stop

Both fresh read-only runs exited 0 with valid nonempty schema-matching JSON on
pinned 673e9bac. Same model, effort and window as Nit. Report-only simplify had
no findings and is clean at Important. Anti-patterns found this recurrence:

| Reviewer label                                                                              | Our severity and impact                                                                                                                                      | Take or record                                                                                              | Review again               |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- | -------------------------- |
| important: Stale writes: readiness failure can invalidate cached group-signalling authority | Important: wrapper-side failed setup can end the anchor while cancellation retains a successful lock read, authorizing a signal to a reused leaderless group | Take pending structural call; this is the same stale signalling authority class in a separate teardown path | Stop under recurrence rule |

Loop end state: **stopped: recurring defect**. Counts remain Nit plus first
Important, with no reset. TOOLING received mailbox sequence 000002 requesting a
structural decision. A marker alone does not serialize wrapper teardown with
signal selection and delivery. The proposed direction is a private guard lock
covering both operations; it has not been implemented.

After the readiness changes, focused Scrut passed 90/90 and error-output guard
passed 102/102. The final strengthened fixtures passed the focused document
90/90 on macOS Bash 3.2. ShellCheck and Bash 3.2 syntax checks passed on affected
shell sources. At most two test jobs ran concurrently, and all thermal checks
reported no warning. The final strengthened fixtures are later than the pinned
structural scope and remain input to the pending focused aspect review.

Unrun: structural continuation after the design call; focused aspect loop;
trim; Semgrep; final lint-and-fix; designated locked full suite; tidy; final
version audit; push and PR. No published branch or PR exists.

## Single-owner structural call

TOOLING's mailbox sequence 000002 at 2026-11-02 11:40:48 PM EST rejected a guard
lock and selected one owner: only serialized helper cleanup ever ends an anchor.
Implemented that call. Only the anchor acquires the continuity lock, after fork;
a failed fork cannot briefly expose wrapper-held continuity evidence. After
acquiring the lock, the anchor survives publication/readiness failure and a
broken readiness pipe. The wrapper exits nonzero without exec, never killing or
reaping the anchor. Unknown PID metadata is reported as 0 while a held lock
still authorizes group cleanup. The helper retires signalling authority before
KILL; when only the known anchor remains, it sends that KILL immediately.
Other members retain bounded TERM-to-KILL escalation. There is no asynchronous
release path and no guard lock. External termination of the anchor is out of
scope, as TOOLING specified.

Adjusted failure tests require the failed wrapper to leave its real anchor and
helper cleanup to remove it. The stopped-wrapper case requires the actual PID
to be published while the wrapper is stopped. The ps/kill fixture keeps synthetic
signals isolated; a separate one-shot actual helper call ends its real owned
anchor, followed only by inspection, so a deliberately missing retirement marker
cannot cause repeated real signals. Single-owner plants and verification follow.
Counts remain Nit plus first Important, with resumed first Important verification.

## Single-owner verification

Resumed first Important verification: anti-patterns and report-only simplify
both exited 0 with valid complete schema-matching results on 3a675c78. Neither
found an Important defect. Structural loop end state: **clean at Important**,
after Nit and first Important with the recorded design-call continuation.

Single-owner focused document passed 90/90; error-output guard passed 102/102.
All four unmodified setup probes passed. New wrapper-side anchor-kill plants
failed publication, readiness and timeout cases with exit 1, confirming that
failed wrappers must leave the anchor alive. Retirement-release, retirement-KILL,
missing child publication and missing readiness alarm plants also returned exit 1.
The real fixture anchors ended through a single helper call followed only by
inspection. Clone restored after plants.

Added test-only cleanup registration before waiting/reading anchor metadata,
so a future setup assertion failure retains artifacts instead of forgetting a
real fixture anchor. Focused aspect review will include that strengthening.

## Focused aspect Nit round

Installed immutable 2.3.3 helper ran code, errors, tests and comments with
explicit gpt-6.1-sol/high/872000 and CLAUDE.md fallback guidance. Types omitted
because no types or schemas changed. All four exited 0 with schema-valid
nonempty replies and status ok. Before/after scope snapshots matched and no
lasting changes were found. Code had no findings.

| Reviewer label                                                                                         | Our severity and impact                                                                                          | Take or record                                                                                                                              | Review again                                                                |
| ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| suggestion: Uncited: Readiness write failures discard their underlying diagnostic                      | Nit: failure is reported but its cause is lost after stderr redirection                                          | Take: duplicate the original diagnostic handle before acquiring the anchor lock; report setup errors there and close before idling          | Yes, diagnostic behavior changed                                            |
| suggestion: Uncited: Anchor inspection errors omit the information needed to diagnose cancellation     | Nit: inspection fails safely but omits operation, path and errno                                                 | Take: report unexpected open/flock failures; keep absence and ordinary contention quiet                                                     | Yes, diagnostic behavior changed                                            |
| important: Uncited: The timeout test does not exercise a broken readiness pipe (rating 8/10)           | Important: missing SIGPIPE protection could restore asynchronous anchor termination without a regression failure | Take: synchronize a real readiness write after wrapper exit, require EPIPE and retained diagnostic, then verify the live anchor and cleanup | No for test-only edit; diagnostic edits independently require another round |
| suggestion: Uncited: The stopped-wrapper description claims an ordering the fixture does not guarantee | Nit: the fixture checked the stopped state after publication without establishing ordering                       | Take: synchronize the child on the wrapper's actual stopped state before publication                                                        | No, tests only                                                              |

Added a real open-error fixture by presenting a directory as the anchor file;
it requires inspection status 2 and the retained operation/path context. Added
broken-pipe and diagnostic plants are pending. Focused loop advances to its
first Important round because the diagnostic fixes change behavior.

## Focused first Important round and boundary checks

Code, errors, tests and comments all returned status ok, exit 0 and valid
nonempty schema-matching results. No findings. Before/after snapshots matched,
with no changed or outside-scope paths. The scope pinned the actual origin/main
merge base, 2a694d7048750199ce8d292043156a6046299fd6, through ec1e78a6.
Focused loop end state: **clean at Important**, after Nit and first Important.

Focused document passed 90/90, error-output guard 102/102, and macOS Bash 3.2
focused document 90/90. The broken-pipe fixture sets its initial SIGPIPE default
explicitly, then resumes the real write only after wrapper exit. Its three
unmodified baseline cases passed. Removing SIGPIPE protection, discarding the
original readiness diagnostic and discarding the open-error diagnostic each
returned exit 1 in committed fixtures. The final single-owner old leaderless
signal-path plant also returned exit 1. All mutations stayed in the recorded
shared clone and were restored. No Linux runtime claim is made before CI.

## Trim and version verification

One combined trim-comments/trim-text dry run used fresh read-only
Codex gpt-6.1-sol/low/872000. Exit 0, nonempty reply and all nine canonical files
classified. Took its single prose rewrite and a flag-only correction naming the
real anchor in a fixture comment. Bash minification before/after matched exactly;
all Scrut fenced blocks remained byte-identical. ShellCheck, shfmt and the
scoped Markdown check passed; the affected document then passed 90/90.

Check-versions used the actual origin/main merge base. Only
review-pr-with-codex changed: 2.3.3 to 2.3.4, a patch fix, with its generated
manifest matching. All 61 plugins are registered, and catalog entries/metadata
have no versions. PR and push identities both resolve to the public, unarchived,
nonfork cboone/agent-harness-plugins repository, default branch main.

## Baseline Semgrep

Ran Semgrep 1.180.0 in a disposable shared clone of trimmed head 3fb02a5d,
with SEMGREP_REPO_NAME=cboone/agent-harness-plugins, config auto and the actual
merge base 2a694d7048750199ce8d292043156a6046299fd6. Exit 0: 103 rules, five
scanned paths, zero findings. The tool skipped its baseline checkout because
there were no current findings; the baseline invocation itself completed.

Coverage is incomplete: about 20.2% parsed, PartialParsing across codex-aspects
lines 3-1472, and seven paths excluded by default ignores, including fixtures.
This is not a clean-scan claim. The issue-715 ledger records the standing
shell-file acceptance for this parser limitation with coverage disclosed and
ShellCheck passing. Affected ShellCheck passes here; full lint follows. No scan
substitution or parser workaround was used.

## Final lint and suite

Lint-and-fix --no-push uses the documented make lint entry point: Markdownlint,
Prettier, ShellCheck, shfmt, fixture-environment guard and actionlint, all enforced.
Global Markdown/Prettier fixers are not run because the aggregate writer can
reformat protected Scrut documents; check mode preserves the tests/AGENTS.md
rule. Edited permitted files were formatted with scoped commands during work.
No advisory-only tool is substituted for an enforced check. Final results follow.

The lint-and-fix verification completed with exit 0. All enforced make lint
checks passed; no file fixes were needed, no required check was skipped and no
advisory-only result was substituted. Markdown/Prettier remained in the recorded
check-only mode. The designated full suite follows under the requested load
wait and directory lock, SCRUT_JOBS=2.

## Full-suite outcome and publication gate

The single requested full invocation completed with exit 0. It waited for the
required pgrep matches to clear, acquired the designated tooling-full-suite.d
lock, observed no thermal warning and ran make test-all with SCRUT_JOBS=2.
All lint and repository validation steps passed, followed by **76/76 Scrut
documents passed**. This includes codex-aspects, both isolation/guard documents,
the shared Perl runner probe and the previously affected codex-exec validator.
No implementation or test changes followed this run.

This record-only update receives the last make lint before publication. The
publication gate then backs up the branch, rebuilds signed logical plan,
implementation, tests and documentation commits, and compares the complete tree
with that backup before pushing. TOOLING receives the measured tidy result and
ready PR in the mailbox; TOOLING owns merging. No Copilot review is requested,
waited for or chased.
