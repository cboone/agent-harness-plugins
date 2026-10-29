# Launch workmux isolation ledger

Base: `7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71` (`origin/main` merge base).
Scope: issues 436 and 528, launcher Scrut tests and socket fixture only.
Implementation checkpoint: `7737e360`.

## Stopped: review infrastructure unavailable

Both parallel step 1 reviewers reported the brief's explicit stop condition:
`timed out negotiating with the code-mode host`. No fallback or retry ran.
The reviews are incomplete, with no validated findings or clean end state.

- Anti-patterns: `gpt-6.1-sol`, high effort, 872000 context window, read-only.
  Log event: `2026-10-29T21:39:05.766334Z`.
- Report-only simplify: same settings, all four cleanup angles requested inline.
  Log event: `2026-10-29T21:39:06.858679Z`.
- Both runs stopped with TERM, exit 143. Their recorded root PIDs, 56378 and
  56377, were confirmed absent. No lasting worktree changes were found.
- The in-flight launcher document runner, PID 75267, was stopped with TERM.
  It and its Scrut child, 75494, were confirmed absent. No final pass is claimed.

## Validation

- `launch-workmux-sockets.md`: 6 cases passed with sockets available.
- `unix-socket-fixture.md`: 3 cases passed, covering Ruby creation denial,
  connection denial and unexpected error handling. Its expected exit 80 uses
  `skip_document_code: 81` so the contract assertion actually runs.
- Simulated Ruby EPERM against the socket document: 6 cases skipped, no failures.
- ShellCheck and shfmt checks passed for the fixture.
- Locked Yarn dependencies restored with network and scripts disabled.
- Prettier found ledger table formatting; the record is formatted before saving.
- `make test-all`, full launcher completion, Semgrep, later review steps,
  version checks and tidy have not completed. No push or PR exists.

Scrut suppresses captured output on native document skips, including in its JSON
renderer. The fixture emits a reason on stderr when invoked directly; the socket
document explains the reason. The runner summary only reports skipped counts.
This limitation needs assessment before considering issue 528 complete.

## Planted defects

Disposable two-case documents contained the same helpers and ambiguous-branch
case. An extracted blank expectation was removed before the measurements below.

| Planted defect                          | Instrument                    | Observed result                             | Durable coverage  |
| --------------------------------------- | ----------------------------- | ------------------------------------------- | ----------------- |
| Leave launcher temp file in private dir | Ambiguous branch cleanup case | 1 passed, 1 failed; `temp cleanup: no`      | launch-workmux.md |
| Add unrelated prompt file in parent dir | Ambiguous branch cleanup case | 2 passed; unrelated file does not interfere | Control run only  |
| Deny Unix socket creation with EPERM    | Socket availability probe     | 6 skipped; direct fixture contract passes   | Fixture document  |
| Deny Unix socket connection with EACCES | Fixture contract case         | Exit 80, no PID, socket path removed        | Fixture document  |

## Resume needs

- Resume only through TOOLING with the review-host blocker resolved or a new
  explicit instruction about the stop condition.
- Remove the unintended blank output expectation before the closing fence in
  `launch-workmux.md`'s helper block. It was introduced while moving the socket
  helpers; the extracted plant initially detected it. No fix was made after the
  mandatory review stop.
- Assess the hidden native-skip reason described above.
- Add or assess Perl fallback coverage and Ruby-unavailable contract behavior.
- Finish focused checks and the full required local review/check order, then
  tidy, push and open the ready PR. TOOLING merges; the worker never merges.

## Review findings

No validated reviewer output exists. No severity, take/record or follow-up-round
assessment can be made from the failed runs.

## Restart and first completed review round

TOOLING relayed restart authority from the approved ramp rules, Inbox "Ramp goals",
answer "Resume after the measurement". The unintended blank expectation was fixed
in `56070d06` before restarting the read-only reviews.

The first resumed anti-pattern and simplify attempts returned incomplete coverage:
an overbroad parent prompt made optional missing files and truncated reads terminal.
Corrected prompts retained those failed outputs and completed fresh read-only runs.
Neither incomplete attempt is a clean round. Completed runs used `gpt-6.1-sol`, high
effort, 872000 context window, with no lasting scope changes (tree
`c4ea474c45a33e26fcbbd8a4e24ffa29e99e1b84`). No runtime host error occurred.

First completed step 1 round, Nit threshold:

| Reviewer label                                                          | Assessed severity                                              | Take or record                                                           | Review again                                                          |
| ----------------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| Anti-patterns: important, connection test requires real socket creation | Important: restricted environments still fail the new contract | Take: fake server creation with a regular file before denying connection | No extra step 1 round for test-only edits; step 2 reviews final tests |
| Anti-patterns: important, Ruby wrappers bypass Perl-only fallback       | Important: supported Perl-only environments fail the new tests | Take: gate Ruby contracts and add separate Perl fallback contracts       | No extra step 1 round for test-only edits; step 2 reviews final tests |
| Simplify: suggestion, unused FIFO and temp directory                    | Nit: repeated unused setup resources                           | Take: remove only unused setup in socket document                        | No behavior change                                                    |
| Simplify: suggestion, external basename                                 | Nit: unnecessary process for known socket filename             | Take: Bash parameter expansion                                           | No behavior change                                                    |

Step 1 end: ended: fixes changed no behavior outside the tests. All four inline
simplify angles completed: reuse, altitude, efficiency and simplification.
Ruby contract now passes 4 cases; Perl contract passes 5 cases. A direct Perl-only
live-socket probe passed, and its recorded child PID 4941 was stopped and confirmed
absent.

TOOLING's design call: retain tests-only scope and native skip counts. Document
Scrut's hidden stderr limit in the socket document and PR. Surface skip reasons in
`bin/run-scrut-documents` as a follow-up, without changing that runner here.

## Focused review, Nit round

The installed `codex-aspects` helper ran code, errors, tests and comments in
parallel, read-only, at `gpt-6.1-sol` / high / 872000. Every process exited 0 and
passed schema validation. Types was inapplicable. Scope tree
`96839cca047036c0146ad2eb8f1248d243479f85` remained unchanged.

Code, errors and comments reported no findings. Tests reported one suggestion:
`write-scrut-tests: Behavioral coverage: Successful Perl fixture startup is untested.`
Assessed severity: Important after the requested lifecycle case reproduced a real
fixture failure: a second connection returned `Connection refused` (exit 61).
Take: add a separate live Perl lifecycle document and consume the availability
probe's accepted connection in both fixture backends. The probe had filled Perl's
listen backlog. Review again: yes, fixture behavior changed, so focused Important
round 2 follows. This is a new lifecycle defect, not a recurrence of the earlier
contract restrictions.

The lifecycle document passes 2 cases, verifying a live PID, a subsequent
connection, termination and socket-path cleanup. Restriction contracts remain
independent of live sockets. The Ruby-unavailable control skips its 4 contracts.
Removing the connection probe in a disposable fixture copy caused the Ruby
contract document to fail exactly its connection-denial case: 3 passed, 1 failed.
Its recorded child PID 50941 was stopped and confirmed absent.

The launcher document completed: 64 passed. Socket discovery completed: 6 passed.
The latter runner printed a nonfatal `child setpgid ... Operation not permitted`
diagnostic before its passing summary; it is retained as a runner limitation.
Version audit: no plugin source changed, no version bumps required; all 60 plugin
registrations have valid manifest-owned versions and matching optional Codex
versions. Fixed merge base remains `7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`.

## Focused review, Important round 2: recurrence stop

All four aspects completed with exit 0 and validated schemas. Scope tree
`f743be8d23f8b3014e9edfe7813d41c9275bc00d` remained unchanged. No Important or
Critical findings were reported. Code, errors and comments had no findings.

Tests label: suggestion, `write-scrut-tests: Behavioral coverage is missing for
the Ruby server lifecycle.` Assessed severity: Nit, missing coverage for the
fixture's own new fork/termination behavior. Take: required boundary coverage,
but not implemented pending the recurrence call. Review again: test-only edits
would not advance the loop. The gap repeats the earlier Perl lifecycle coverage
class, so the loop is **stopped: recurring defect** even below the Important
threshold. TOOLING received the finding and a proposed matching independent Ruby
lifecycle document, with both backends checked by cleanup plants. No scope
expansion is proposed; round counts remain Nit 1 and Important 2.

The Perl cleanup plant removed termination unlink in a disposable fixture copy.
Its lifecycle document reported 1 passed, 1 failed, confirming cleanup sensitivity.

## Recurrence design call and closure

TOOLING selected the proposed structural closure: independent Ruby and Perl
lifecycle documents with the same live-PID, subsequent-connection, TERM and
socket-removal contract. Each skips independently for unavailable runtimes or
sockets. The Ruby counterpart passes 2 cases. Both backends also have matching
creation-denied, connection-denied and unexpected-error contracts. Their
connection-denied cases replace server creation with a regular file, so the
contracts work where real sockets are blocked. Runtime availability guards keep
one missing runtime from breaking the other's coverage. Unexpected-error exit
values differ by interpreter (Ruby 1, Perl 22); both are explicitly asserted and
neither is the skip code.

The call changes no scope, product behavior, security or cost. Round counts stay
Nit 1 and Important 2. The remaining fix changes tests only, so no new focused
round is required. Focused review end: **clean at Important**, after the recorded
recurrence stop and conductor decision. No Important or Critical finding remains.

## Trims and lifecycle plant completion

One read-only `trim-comments` run and one `trim-text` run completed with exit 0,
nonempty replies and complete eligible-file lists, using `gpt-6.1-sol` / low / 872000. No host error occurred. Comments proposed no changes. Prose proposed
three rewrites: two local wording reductions were taken; moving a socket-skip
condition before its action was declined because the existing action-first
wording is clearer. No facts, code fences or ledger evidence changed.

Ruby's cleanup plant removed termination unlink from a disposable fixture copy.
Its lifecycle document reported 1 passed, 1 failed, matching the Perl plant.
Both normal lifecycle documents pass 2 cases each. The recurrence closure is
complete; no worker or reviewer process remains active.

## Semgrep baseline

Semgrep 1.180.0 ran in a disposable shared clone of `b999fe8c`, comparing with the
fixed merge base using `SEMGREP_REPO_NAME=cboone/agent-harness-plugins` and
`semgrep scan --config auto --baseline-commit <base> --json`. Metrics remained at
the tool default. The initial scan completed with 47 rules, 2 documentation
paths, no findings and no errors; its default ignore policy excluded all 7 test
paths. That result did not establish fixture coverage.

A second baseline scan in the same clone added an empty-policy `.semgrepignore`
there only, replacing the built-in test exclusions. All 9 changed paths were
scanned with 51 rules, no findings, no errors and approximately 100% parsed lines.
The branch's files and configuration were unchanged. This remained a baseline
scan, not a full scan matched to changed lines. Artifacts were recorded under
`436-semgrep.CqrvQY` in the session temporary directory. ShellCheck passes for the
changed fixture; no parser-gap exception was needed.

## Final formatting and bootstrap validation

The required `lint-and-fix --no-push` work used the repository's `make format`.
It completed successfully, changing only an extra blank line outside a socket
snapshot fence. No unrelated file changed. The first `make test-all` passed lint
but stopped at fixture-environment validation: the extracted socket document
needed the original document's Git-environment bootstrap. Added that bootstrap;
`make validate` now passes all JSON, fixture-environment and plugin checks.
The socket document also passes its Prettier check. This test-only setup fix
requires no additional review round. The full suite is rerun after this fix.

## Final local result

`SCRUT_JOBS=4 make test-all` completed with exit 0: 57 documents,
1839 cases passed, zero failed and zero skipped. Markdown/Prettier, ShellCheck,
shfmt, actionlint, JSON, fixture-environment and plugin validation all passed.
The known notify concurrency case passed locally; no unrelated fix was made.
No plugin source, hook, manifest, generated mirror or user configuration changed.

Review end states: structural loop ended with test-only fixes; focused loop clean
at Important after TOOLING's recorded recurrence decision; both trims completed.
Semgrep's inclusive baseline completed without findings or errors. Version audit
requires no bump. Signed exact-tree tidy and ready-PR handoff follow these checks;
TOOLING owns merging. The runner summary's hidden skip reason remains a follow-up,
as directed, rather than a change in this branch.
