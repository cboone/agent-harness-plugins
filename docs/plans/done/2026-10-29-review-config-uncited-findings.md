# Uncited review findings

Authorized by the tooling overnight batch, October 28, 9:16 PM ET, through a
ready PR. TOOLING merges. Scope: agent-harness-plugins issue 500 only.

1. Add an explicit `Uncited:` branch to all three review templates. Require exact
   rule names for covered findings and forbid invented citations.
1. Assign uncited findings severity by impact, sharing the Nit cap, and combine
   repeats across files when they share a fix.
1. Refresh the repository's managed review blocks, bump the plugin patch version,
   regenerate mirrors, and add prompt-contract checks with removal plants.
1. Run the full local review order, baseline Semgrep in a disposable clone,
   `make test-all`, version checks and exact-tree signed tidy. Push and open a
   ready PR, then report to TOOLING. Stop on code-mode negotiation failure.

The existing reporting templates cover the need. Routing, checklists and hooks
stay outside this change. Contract tests verify instructions, not model behavior.
