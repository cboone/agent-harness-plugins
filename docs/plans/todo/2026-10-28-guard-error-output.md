# Guard error output

Extend `bin/check-fixture-environments` for the error-output guard requested in
[cboone/agent-harness-plugins issue 672](https://github.com/cboone/agent-harness-plugins/issues/672).
Its existing inventory and `make validate` wiring cover local `make test-all`
and CI without adding a competing tool.

1. Flag stderr discards and retained diagnostic redirects in repository tooling,
   shipped scripts and fixture scripts. Require `# error-output-allow: reason`
   on the parsed command line for exceptions. Use shfmt JSON ASTs for shell files
   and Scrut shell blocks; fail closed on unsupported syntax. List embedded
   operands and named non-Bash exclusions explicitly with reasons.
2. Review existing redirects, keep useful stderr live where local, and explain
   intentional probes, custom failure reports and standalone replay protocols
   inline. Record broader producer-status concerns for follow-up.
3. Cover rejection and acceptance with static samples in isolated trees. Commit
   the guard, then plant a discard and bypassing capture in actual source and
   confirm failure, restoration and passing controls. Weaken each guard rule
   and confirm the regression tests fail.
4. Run the full local review order with immutable merge-base commit, trim,
   baseline Semgrep in a disposable shared clone, lint, `make test-all`, version
   checks and signed exact-tree tidy. Integrate main before the PR and report
   conflicts. Open ready for review, wait for checks, and report to TOOLING.

Authorization: the worker brief relays the Inbox go-ahead from 2026-10-28,
7:38 PM ET, through a PR ready for review. TOOLING merges; this worker never
merges or changes installed configuration.

## Accepted tracking limits

The Inbox answer relayed by TOOLING at 10:28 AM ET on 2026-10-29 selects the
tracking design from `2a312d62` and accepts these two stream-context limits:

- `{ exec 3>/dev/null; some-command 2>&3; } 3>&1` can use a stale inherited
  descriptor-3 destination after an exec changes that descriptor.
- `command builtin exec 1>/dev/null; some-command 2>&1` can hide a persistent
  stdout change behind composed builtin prefixes.

These tracking-model limitations remain recorded and accepted under the earlier instruction. The later rare-form rule rejects both unannotated examples at their
exec construct; it does not derive persistent descriptor state. An explicit reason
can exempt that site. Ordinary variable-named commands retain tracking behavior.
The strict-reason alternative remains set aside because it requires 408 sites.

The narrowed preflight identifies two existing persistent-exec sites, below the
ten-site gate. Add reasons there, fail closed on rare literal exec-like names,
persistent exec redirections and coprocesses, and verify the boundaries with
static cases and earlier-implementation plants. Keep parser exceptions limited
to recognized syntax or AST limitations and report unexpected parser failures.
