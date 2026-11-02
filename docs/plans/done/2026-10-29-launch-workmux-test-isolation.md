# Launch workmux test isolation

Status: implemented and locally validated; ready-PR handoff follows.

Implement [cleanup isolation](https://github.com/cboone/agent-harness-plugins/issues/436)
and [restricted socket skips](https://github.com/cboone/agent-harness-plugins/issues/528).
Authorization: Tooling overnight batch, Oct 28, 9:16 PM ET, through a ready PR.
TOOLING owns merging.

- Use the launcher's existing `TMPDIR` support for the ambiguous-branch cleanup
  assertion. Check all launcher files in that private directory.
- Put socket discovery and ambiguity cases in a separate Scrut document, using
  Scrut's native document skip exit code. Probe creation and connection in the
  existing socket fixture. Permission and protocol restrictions skip with a
  reason; unexpected errors fail.
- Verify cleanup with unrelated files present and an intentionally retained file.
  Exercise allowed sockets and simulated creation and connection restrictions.
- Run the full local review order, baseline Semgrep in a disposable clone,
  `make test-all`, version checks and signed exact-tree tidy, then push and open
  the ready PR. Do not change plugin hooks or user configuration.

No new tool or plugin is needed. Existing launcher temp-directory support and
Scrut's document skip facility cover both issues.
