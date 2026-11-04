# Heavy suite lock adoption review ledger

Validation complete: the required full suite passed all 77 documents and 2,238
cases, with no failures or skips. Structural review ended clean at Important;
focused review ended clean at Nit. Semgrep coverage remains incomplete under
the recorded TOOLING continuation decision.

## Scope and authorization

The worker brief authorizes building, full local review, push and a ready PR on
`feat/adopt-heavy-suite-lock`. TOOLING merges. Base:
`e0ad16d5095e9c445be45bde5ef622ad8f5f45cb` (`origin/main` merge base).
The repository is non-fork and non-archived, owned by `cboone`.

## Implementation

`bin/run-heavy-suite` delegates to the installed SL-VF heavy lock or executes
its command directly when missing. The public Scrut coordinator wraps directory
runs and delegates document execution to the moved implementation in `bin/lib/`.
`make test-all` locks lint, validation and Scrut together. Named documents and
listing remain direct. No plugin changed, so no plugin version bump is needed.

## Validation evidence

- Lock document: 17 cases passed after fixing fixture cleanup and Make's working
  directory. The tests use private suite-lock and Scrut stubs and assert their
  resolution before invoking any subject.
- Coordinator regression document: 33 cases passed.
- Environment-isolation document: 51 cases passed after the reset-order fix.
- ShellCheck of changed runner/stub scripts: passed after adding required-input
  assertions and the child-expansion comment.
- Plant observations are retained verbatim in
  `2026-11-03-heavy-suite-lock-plants.txt`. No hand-run plant verdict is claimed.
  Ten direct-runner mutations each returned raw Scrut status 50. The separate
  streams mutation is recorded separately in the same file.
- The first plant launcher used the public coordinator. The selection mutation
  caused that launcher itself to queue for the real heavy lock. Its owned
  processes were interrupted and the original source restored. Subsequent
  plant commands use `bin/run-scrut` with the Makefile fixture environment.
  The initial completed observation and later complete raw observations remain
  in the raw file; the interrupted observation has no verdict.

## Local review rounds

Structural anti-patterns plus report-only simplify: two rounds, clean at Important.
Focused Codex aspects: one round, clean at Nit.
Trims: one round, comment and prose changes only.
Baseline Semgrep: incomplete after the approved retry. Final lint and the
required full suite passed. Signed commit tidy preserves the validated tree.

### Structural Nit round

Both fresh runs used `gpt-6.1-sol`, high effort, window 872000, read-only
sandbox, approval never and web search disabled. Both exited 0 with nonempty
replies. The anti-pattern JSON passed its installed schema check and reports
complete coverage of all 15 changed files. No PR existed; ownership metadata
was verified by the parent session. The reviewer could not reach GitHub from
its sandbox and did not run mechanical checks.

| Reviewer label and finding                                                                 | Our severity                                         | Take or record                                               | Review again                                  |
| ------------------------------------------------------------------------------------------ | ---------------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------- |
| Important: Sibling input forms: an empty path runs the default suite without locking       | Important: the same full tree bypasses serialization | Take: normalize the empty path and add coverage              | Yes: changes lock selection                   |
| Important: Parallel paths: directory snapshot updates execute before taking the heavy lock | Important: a full update can overlap another suite   | Take: lock directory updates and test named updates directly | Yes: adds locking to the parallel entry point |
| Nit: Docs drift: runtime guidance points to the coordinator header's former location       | Nit: the header reference is stale                   | Take: point to the implementation header                     | No: documentation only                        |
| Validation failure: fixture input assertions precede the environment reset                 | Important: required environment validation fails     | Take: source the reset before fixture path assertions        | Yes: changes validation behavior              |

Simplify completed all four cleanup angles inline, no findings, clean at Nit
within its scope. The combined structural loop advances to Important after the
behavior fixes. No severity downgrade or design change was required. The
initial simplify launch had no prompt because its preparation command was still
running; its reply asked for a task and is not review evidence. The subsequent
report-only run received the complete prompt and reviewed all changed files.

The environment-isolation document initially returned 19 failures out of 51
cases, all with the fixture reset-order diagnostic. It is not a passing result.

After those fixes, the lock document passed all 17 cases. Three additional
fix-removal observations for empty paths, directory updates and direct named
updates returned raw Scrut status 50; complete outputs are appended to the raw
file. They carry no hand-written pass verdict.

### Structural Important round

The second anti-pattern run exited 0; its JSON passed the installed schema
check, with status success, complete true, no findings and no unread paths.
The second simplify run exited 0 with a nonempty report and no findings after
all four cleanup angles. Both used the same read-only settings as round one.
Both confirmed source closure of the prior findings. The structural loop ends
clean at Important. Mechanical checks were intentionally left to the worker.

### Focused Nit round

The installed aspect runner completed Code, Errors, Tests and Comments with
exit status 0 for each aspect. Each result was nonempty, schema-valid and matched
snapshot `5982f4d747ecdfe9b1a942c2b2ad21572b774dea`, tree
`73ea8d4a65da022f8e72769951bea37aaf745764`. All four findings arrays were empty.
Types was omitted because no type or data definitions changed. A subsequent
scope comparison reported the same tree, no scope changes and no outside-scope
paths. The focused loop ends clean at Nit.

### Trims

Two read-only dry runs used `gpt-6.1-sol`, low effort and window 872000. Both
exited 0 with classified file lists and proposal tables. Took the two comment
proposals: omit the runtime comparison to CI and the inventory of globals that
is apparent in their declarations. Took the prose proposal making the aggregate
Make probe's explanation direct. Declined changing "separate streams mutation"
to "streams mutation", because the distinction between stdout and stderr is
what that observation tests. Declined the prose run's longer rewrite of the
same globals comment in favor of the code-comment run's shorter version. No
behavior changed, and no further review round is required.

### Build and versions

`make build` completed with no generated drift. The repository check-versions
procedure used the actual `origin/main` merge base, found no changed plugins,
and checked all 61 canonical manifests against catalog membership and any
Codex manifest versions. No plugin version bump is required. ShellCheck passed
for all changed runner and stub scripts. The instruction-chain checker passed;
the repository root plus testing instructions total 10,005 bytes.

## Stop at baseline Semgrep

The real baseline scan in disposable shared clone
`/tmp/adopt-heavy-semgrep.Plbu6R/repo`, at `eff5df9e`, exited 2 before scanning
any files. The JSON contains a SemgrepError with
`BaselineHandler._get_git_status`, `git.py:368`,
`IndexError: pop from empty list`. Zero findings is not a clean scan. The raw
result is retained in `2026-11-03-heavy-suite-lock-semgrep.json`.

The installed version is Semgrep 1.180.0. Its status command allows copied
files (`--diff-filter=ACDMRTUXB`) but its parser consumes a third filename only
for rename records. The global Git setting is `diff.renames=copies`; the moved
coordinator produces a C096 record with two paths, desynchronizing that parser.
No installed tool or repository/global configuration was changed. A proposed
correction is to normalize rename detection for the disposable scan only, then
rerun the same baseline scan. It has not been applied or retried.

The mandatory baseline-scan stop was reported to TOOLING by mailbox, with a
question requesting its decision. At that stop, final lint-and-fix, the full
suite, tidy, push and PR creation were unrun. The TOOLING lock was not acquired.
The full-suite script is prepared at `/tmp/adopt-heavy-full-suite.sh`; no full
suite process was running. The worktree remains on `feat/adopt-heavy-suite-lock`.
Checked review results and trim proposals are retained in
`2026-11-03-heavy-suite-lock-review-results.json` for the continuation. Review
counts remain structural two rounds, clean at Important; focused one round,
clean at Nit; trims one round. The scan failure is not a review finding or a
new review round.

### TOOLING continuation and scan retry

TOOLING's native mailbox decisions, sequences 000001 and 000002, written
2026-11-03 at 10:52:36 PM EST and 10:53:42 PM EST, opened the continuation.
The first requested one full non-shared clone retry and allowed continuation
with an explicit tool gap, citing the standing CI-only Semgrep decision. The
second approved `diff.renames=true` for the disposable scan only. No global or
worktree configuration changes were authorized or made. No upstream report
was filed.

The shared clone was clean. Its rename-only diff listed no rename, mode-only
or submodule entries. A full clone created with `git clone --no-local` contained
the fixed merge base. The same baseline command then ran there with only
`GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=diff.renames`, and
`GIT_CONFIG_VALUE_0=true` added for that command.

The retry exited 0, with zero findings and 10 targets scanned, but its JSON
reports PartialParsing in `bin/lib/run-scrut-documents` for existing `${!:-}`
syntax. This is incomplete coverage, not a clean Semgrep result. The command
used the real baseline flag and no substitute full scan. The result is retained
in `2026-11-03-heavy-suite-lock-semgrep-retry.json`. The PR must name both the
initial copy-record parser failure and the remaining partial parse. Continuation
to lint, the single full suite and the ready PR follows TOOLING's decision.

## Final lint plan

All selected tools are enforced by the repository Makefile, package scripts,
agent instructions and CI: Markdownlint and Prettier; ShellCheck and shfmt;
Actionlint; JSON, fixture-environment, plugin and generated-mirror validators.
Prettier fixes are scoped to the branch's plan, ledger and testing instructions;
shfmt fixes are scoped to changed scripts. Scrut documents are check-only under
the project rule that forbids reformatting them. `make lint validate` is the
recorded check command. No inferred-only advisory tools are required. The lint
skill runs without push; the parent then runs the required full suite and tidy.

### Lint-and-fix result

Scoped Prettier and shfmt completed. `make lint validate` exited 0, including
Markdownlint (886 files, no issues), Prettier, ShellCheck, shfmt, Actionlint,
fixture-environment checks, JSON and plugin validation, and Claude plugin
validation. The validator's existing workmux installation-line advice was
nonblocking and left outside scope. No source behavior changed during lint.
The first formatting attempt lacked Yarn's node_modules state file;
`corepack yarn install --immutable` restored it without a lockfile change, and
the formatting and full lint/validation commands then completed successfully.

Lint status: success. Check-only by project policy: Scrut documents, never
reformatted. Advisory tools: none. Unresolved local check: Semgrep remains
incomplete under the recorded TOOLING continuation decision. Caller resume:
run the required full suite once, tidy the identical tree, push and open the
ready PR. No push was performed by the lint skill.

## Required full suite

The one required full suite completed with exit 0, from this worktree:

```bash
~/Work/sl-vf/bin/suite-lock run heavy -- env SCRUT_JOBS=2 make test-all
```

The driver first acquired `~/Work/projects/.locks/tooling-full-suite.d` and
checked `pmset -g therm`, which reported no recorded thermal or performance
warning. It then queued on the machine-wide heavy lock. No `pgrep` wait was
used. Both owned locks were released at completion.

The full target passed lint and validation, then all 77 Scrut documents:
2,238 cases succeeded, zero failed, zero skipped. This also exercised the
aggregate and directory-runner nesting under the real heavy lock without a
deadlock. The local raw log is `/tmp/adopt-heavy-full-suite.log`; it includes
other lock-holder diagnostics and is not published. Only the measured totals
are retained here. No second full-suite run was started.

## Tidy and publication

The unpublished branch is backed up as
`feat/adopt-heavy-suite-lock-pre-tidy`, then rebuilt from the fixed base as
signed logical commits: plan, implementation with tests, and documentation with
review evidence. Final tree comparison with that backup is recorded in the
TOOLING handoff. The plan's link to a private reference was removed before tidy,
so the public branch contains only the required local command contract.

The PR-body trim retained the validation gap and all verification claims,
shortening only the summary. No related issue matched the branch-slug search,
so the PR has no closing reference. TOOLING merges; this worker stops at the
ready PR and handoff.
