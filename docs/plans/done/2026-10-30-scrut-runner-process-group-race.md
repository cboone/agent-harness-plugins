# Scrut runner process-group race

## Scope and evidence

Fix [the macOS runner failure](https://github.com/cboone/agent-harness-plugins/issues/697)
on `fix/697-scrut-runner-setpgid`, based on
`5205fada80635f7d9dd4a1967c94a256e60a99cb`. Keep tool stderr, exit status and
group cancellation intact. No live configuration changes. TOOLING owns merging.

The warning comes from Bash's child before exec, not its parent after exec.
A native probe on macOS 26.7.1, Darwin 25.6.0, ran 1,000 forks with concurrent
parent and child `setpgid` calls: 16 child calls returned `EPERM`, two parent
calls returned `EPERM`, and 63 parent calls returned `ESRCH` after child exit.
Every child observed its intended group. Neither arm used exec. Delaying the
child serialized the calls; both succeeded.

## Prior art and design decision

- [Bash job control](https://raw.githubusercontent.com/apple-oss-distributions/bash/main/bash-3.2/jobs.c)
  sets the group in both processes, reports child failures and ignores parent
  failures. The runner currently uses this behavior and suppresses all startup
  stderr only on its parallel path.
- [Python subprocess](https://github.com/python/cpython/blob/main/Modules/_posixsubprocess.c)
  sets the group in the child before exec and propagates setup failures.
- [Go process setup](https://go.dev/src/syscall/exec_bsd.go)
  also performs group setup in the child and reports setup errors through a pipe.

TOOLING approved child-only setup through Perl's core POSIX module after the
reproduction. Perl already runs in the mirror builder and test fixtures.
This avoids filtering stderr. A Bash-only alternative required startup-log
filtering, group validation and additional synchronization. Native interposition
would also add compiler-dependent test machinery; it remains evidence only.

Restore `SIGINT` and `SIGQUIT` defaults in the Perl child before exec. Bash
ignores both for asynchronous commands without job control; native probes
confirmed the original runner preserved defaults while the first child-only
implementation passed ignored dispositions into Scrut. TOOLING approved the
signal restoration, regression and plant before the final full run.

## Implementation and verification

1. Apply the chosen design to single and parallel launches. Retain genuine
   setup errors and every tool diagnostic.
2. Add deterministic regression coverage and commit it before planting the
   original defect. Record the plant's measured failure and restored pass.
3. Run only affected Scrut documents while iterating, `SCRUT_JOBS=2` at most.
   Use the full local review order: the regression coverage exceeds the
   small-change limit. Record every round and finding.
4. Run required formatting, lint, validation, version checks and exact-tree
   tidy. Repository tooling has no plugin version of its own; bump any plugin
   whose canonical content actually changes.
5. Acquire `~/Work/projects/.locks/tooling-full-suite.d`, record this worker in
   `owner`, and release only the owned lock in an EXIT trap. Run `make test-all`
   once with `SCRUT_JOBS=2`, immediately before push. Record the known baseline
   fixture lint and environment-isolation failures separately.
6. Push, open a ready PR, and send TOOLING the review and validation précis.

## Result

Implementation, deterministic coverage and seven plants are complete. Both
review loops ended clean at Important after one Nit and two Important rounds.
The complete corrected-tree run passed 55 of 56 documents, with only the known
environment-isolation fixture failure. TOOLING accepted that failure, the known
lint failure and the documented pre-existing Semgrep parser limit. Signed tidy
and ready PR publication are the remaining handoff steps.
