# Load-proof notification and bugs-gather tests

Address the fixed wall-clock windows in notification fixtures and the early
reader exit in bugs-gather snapshots. Production notification timing stays
unchanged. Audit the mechanism throughout the test tree; fix or explicitly record each site.

1. Replace notification fixture timing with a fixture clock that advances only
   after backend readiness, and join detached jobs before observing absence.
   Keep a generous bound for unavoidable readiness waits, with diagnostics.
2. Drain bugs-gather output before selecting lines and retain the subject exit.
3. Audit sleeps, polling and deadlines throughout tests, including watchers and
   sibling pipe readers. Record each site and its contract or liveness role.
4. Keep delayed-backend and delayed-writer regression checks. Use representative
   plants for the restart check, clock barrier, draining readers, backend
   ownership, diagnostics channel and bugs-gather pipe. Register only those
   captures; audit other sites by reading.
5. Review frozen commits in the full local order. Structural review uses
   anti-patterns plus the four read-only cleanup aspects. Then focused review,
   trims, baseline Semgrep, lint, full discovery and version checks, tidy, PR.

Use the pinned checked helpers under the mailbox evidence directory for check
records. Run discovery and synthetic load only inside one outer heavy lock.
The ready PR closes both issues; TOOLING receives the précis and receipts.
Any production hook script change explicitly retains the hook-review gate.
