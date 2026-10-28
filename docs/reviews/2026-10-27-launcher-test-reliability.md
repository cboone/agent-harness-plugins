# Launcher test reliability ledger

## Authority and scope

The Inbox go-ahead at 8:54 PM ET on 2026-10-27 authorizes building through a
ready-for-review PR for launcher reliability. TOOLING merges; the worker stops
at the process gates and reports through its mailbox. Work covers detached
output collection and prompt observation for issues 439 and 397, and checking
whether generated branch rejection from issue 435 still reproduces.

Dependencies installed with `corepack yarn install --immutable`. Repository
ownership verified: `cboone/agent-harness-plugins`, active and not a fork.
Starting commit: `0c66e1d5f68a300826cd7c22cc01f6347371289f`, matching
`origin/main` at startup. The local `main` ref is older.

## Current state

Both skills now share `plugins/workmux/scripts/launch-workmux`; the earlier
two-plugin layout in the brief has been consolidated on main. The generated
Codex mirror must be rebuilt, not edited directly.

Ordinary launches now share the detached completion/status handoff and return
failure when workmux fails. The obsolete fixed-wait setting no longer changes
collection. Both skill descriptions and generated mirrors are updated. Tests
retain the prompt observation and delay prompt access to expose early removal.
The workmux patch version is 1.0.1.

## Design decision

TOOLING approved the completion wait within the original go-ahead. Ordinary
launches reuse the detached completion/status handoff and its 90-second bound,
separate process group, and existing-pane fallback. `--await-completion` keeps
its extra worktree check. Timeouts print the log so far and leave the child
running. Both skill docs describe the default wait and failure result.

No receipt line is added. The prompt stays available until the child exits;
the stub's existing observation remains, with delayed prompt access to expose
early removal. The original receipt proposal was rejected as output noise.

## Measurements

Both initial launcher runs overlapped full-suite load. Each passed 40 of 62
cases, with 22 failures. The full baseline passed 1,346 of 1,370 cases across
30 of 32 documents; the launcher and notification-tiers documents failed.
An isolated starting-main checkout passed 41 of 62 launcher cases, with 21
output failures. No captured failure rejects a generated name. Git accepts
the issue 435 sample with and without Command Line Tools selected. No naming
code changes or closure of issue 435 are warranted.

The first modified launcher run passed all 65 cases. A second run with one
added timeout assertion passed 65 of 66. Its single failure required nonempty
output before the timeout, which is not guaranteed when startup is delayed.
That test now checks the captured output against the eventual complete log,
allowing an empty prefix. Production behavior did not change for this fix.

## Local reviews

Structural loop, Nit round: anti-patterns and report-only simplify ran in
parallel through read-only Codex, model `gpt-6.1-sol`, high effort, 872000-token
window. Both exited zero with nonempty, schema-valid results; snapshots match.
Simplify found no changes. Anti-patterns found the independently reproduced
timeout assertion and stale ledger prose:

| Finding                                           | Reviewer label | Our severity                                 | Take or record                                | Review again       |
| ------------------------------------------------- | -------------- | -------------------------------------------- | --------------------------------------------- | ------------------ |
| Timeout assertion samples output before readiness | important      | Important: fails correct launches under load | Taken: compare partial output to eventual log | No: test-only edit |
| Ledger describes the baseline as current          | nit            | Nit: stale checkpoint prose                  | Taken: update state and remaining work        | No: docs-only edit |

Structural loop ended: fixes changed no behavior.

Code-review loop, Nit round: code, errors, tests, and comments ran through the
installed `review-pr-with-codex` helper, read-only, with the same model, high
effort, and window. Every aspect exited zero with schema-valid results and an
unchanged snapshot. Types were skipped because no types changed. Code,
errors, and comments found no defects. Tests found one missing assertion:

| Finding                                           | Reviewer label | Our severity                                             | Take or record                                                         | Review again       |
| ------------------------------------------------- | -------------- | -------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------ |
| Empty timeout output can hide omitted diagnostics | suggestion     | Nit: missing test of the changed timeout output boundary | Taken: synchronize a known marker before timeout and assert it exactly | No: test-only edit |

Code-review loop ended: fixes changed no behavior. The new case uses a
committed sleep stub to hold timeout polling until the log marker exists,
then a FIFO holds the child until the test releases it. Other timeout cases
also use FIFO release instead of assuming a three-second child delay exceeds
the wait. Status-file polling now waits for completion, with Scrut's document
timeout as its guard, instead of failing after a fixed number of samples.
The stub path is registered in both Makefile and CI, and each tool resolves
to its committed stub before a stubbed invocation.

## Defect plants

| Planted defect                                         | Instrument expected to catch it  | What actually happened                           | Test that covers it now                                    |
| ------------------------------------------------------ | -------------------------------- | ------------------------------------------------ | ---------------------------------------------------------- |
| Read and remove the log without waiting for completion | Delayed ordinary launch snapshot | Failed 3 of 3: missing output and retained state | Ordinary launch waits for delayed output and prompt access |
| Remove the prompt before the child reads it            | Delayed ordinary launch snapshot | Failed 3 of 3: missing prompt and launch failure | Ordinary launch waits for delayed output and prompt access |
| Ignore workmux failure                                 | Failure snapshot                 | Failed: expected exit 1, observed 0              | Ordinary launch reports workmux failure                    |

Plants used copies of the committed canonical helper so active reviews and
suite runs kept an unchanged subject. Each planted script passed Bash syntax
checking. The extracted cases contain the exact committed helpers and test
blocks. The unmodified delayed-output control passed both blocks. Disabling
job control also failed the process-group assertion, reporting the parent's
group instead of a separate group. The canonical helper was never planted. Restored controls passed all six blocks; explicit Bash 3.2 controls passed all eight blocks.

## Trim pass

Both read-only Codex trim runs completed once, exited zero, and returned
nonempty file classifications and complete proposals. Model `gpt-6.1-sol`, low
effort, 872000-token window. Three comment trims and three prose trims were
taken. The flagged test introduction was corrected to include timeout behavior;
a literal newline escape in this ledger was corrected. No behavior changed.

The synchronized timeout controls passed all four blocks. Removing the
timeout log-print command failed the exact known-marker assertion after the
child completed, with final status 0. An earlier corruption plant was
inconclusive because the old bounded status wait ended before that assertion;
it is not counted as evidence of prefix coverage.

## Semgrep stop

The required baseline scan ran in a disposable shared clone at `a1036f9d`:

```bash
SEMGREP_REPO_NAME=cboone/agent-harness-plugins \
  semgrep scan --config auto \
  --baseline-commit 0c66e1d5f68a300826cd7c22cc01f6347371289f \
  --json --output /tmp/439-verify.cEoZXM/semgrep.json
```

No metrics override was passed. It exited zero and reported 165 rules on seven
files with zero findings, but JSON contains a `PartialParsing` warning for
`plugins/workmux/scripts/launch-workmux`, lines 3 through 760. That is nearly
the whole helper. This scan is incomplete, not clean. The launcher passed Bash
syntax checking, but that does not substitute for Semgrep coverage.

TOOLING's 9:18 PM ET call permits proceeding if baseline parsing has the same
gap and ShellCheck passes the helper without new suppressions. The baseline
launcher alone was scanned in the isolated checkout at `0c66e1d5`, with the
same configuration, environment, and baseline flag. Semgrep exited zero,
scanned the explicit launcher target, found zero issues, and reported
`PartialParsing` over lines 3 through 774. The parser limitation predates this
branch. The full ShellCheck command reported no warning in the helper, and no
suppression was added there.

The accepted helper précis is: semgrep: 0 findings; launch-workmux partially
parsed by semgrep's Bash parser, as on main; shellcheck clean.

## Final lint

The first lint pass reported ShellCheck SC2034 in the new fixture's unused
FIFO read variable. TOOLING authorized the fixture-only correction to
`_release`; no suppression or behavior changed. The subsequent full `make
lint` passed, including ShellCheck, shfmt, Markdown, Prettier, and actionlint.
Project formatting had already exited zero with no changes. This completes
`lint-and-fix --no-push`; the fixture correction and ledger are committed, and
the push remains with the parent workflow.

Lint status: success. Unresolved or skipped: none. Check-only by project
policy: snapshots remain unchanged. Caller resume target: final tests,
version checks, tidy, and ready PR.

## Final verification

| Check                                            | Observed result                                                                                             |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| Launcher under load, final synchronized fixtures | 67 of 67 passed                                                                                             |
| Two simultaneous full Scrut runs                 | Each passed 32 documents and 1,375 of 1,375 cases                                                           |
| Final `make test-all` after the lint correction  | Passed lint, validation, and all 32 documents, 1,375 of 1,375 cases                                         |
| Launcher alone, after all full runs stopped      | 67 of 67 passed; 162.05 seconds elapsed, below the 300-second document target                               |
| `check-versions` against refreshed `origin/main` | Workmux 1.0.0 to 1.0.1; 60 manifests valid and registered; catalog version ownership and Codex parity clean |
| Canonical launcher and generated mirror          | Byte-identical                                                                                              |

The earlier parallel load runs each passed 1,373 of 1,374 cases. Their launcher
documents failed; the launcher-only run from that fixture version passed 65 of 66. The captured failure was the bounded status-file wait in the existing
worktree timeout case. Those runs preceded the FIFO/status-wait changes and
are not validation of the final fixture version.

Complete test logs:

- `/tmp/439-launcher-after-4.log`
- `/tmp/439-full-final-1.log`
- `/tmp/439-full-final-2.log`
- `/tmp/439-test-all-final.log`
- `/tmp/439-launcher-final-alone.log`

The worker-created scratch root is `/tmp/439-verify.cEoZXM`; it holds the
isolated baseline clone, review/trim captures, plant copies, and Semgrep clone.
Other worker-created logs are the explicit paths named in this ledger or the
mailbox checkpoint. Never clean them by a shared-path glob.

## Publication boundary

Local validation precedes the authorized tidy into signed feature, test, and
documentation commits. The tidy must preserve the pre-tidy tree exactly.
Publication and CI results are recorded in the PR and the TOOLING mailbox.
The worker opens ready for review and reports green checks; TOOLING merges.
The generated-name rejection from issue 435 remains open because it did not
reproduce on the starting main tree.
