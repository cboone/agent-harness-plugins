# Combined issue worktrees

Build through a ready PR for [issue 544](https://github.com/cboone/agent-harness-plugins/issues/544), under the Inbox go-ahead relayed by TOOLING (2026-10-28, 7:38 PM ET). TOOLING merges.

Current source already defines combined default and one shared plan. Preserve that workflow and single-issue behavior. Extend the existing launcher rather than add a launcher: repeat `--issue` and use a leading run of hyphen-separated issue numbers, for example `fix/4523-4503-verify-email`. Reuse requires every requested issue, including when their order changes. Extend PR detection to read those segments. Keep composing once per issue so each body retains its own 2000-character budget; emit one footer with every issue number. Record overlap in the shared plan. Both fan-out workflows stop during preflight when issues resolve to one branch and ask for distinct explicit branches; no automatic selection.

Reproduce the baseline's loss of secondary issue identity with committed, guarded stubs. The older two-window symptom is already covered by combined instructions and cannot truthfully be reported as reproduced on this baseline. Cover combined launch count, branch, prompt budgets, footer, reuse, single-issue behavior and PR closing lines. Commit tests before planting each defect and record measured failures.

Keep sandbox failure paths unchanged. Check the overlapping sandbox worker's merge before reviews and rebase this unpushed branch when needed. Bump changed plugin patch versions and regenerate mirrors with `make build`.

Run the full local review order, Semgrep baseline in a disposable clone, final lint and `make test-all`, version checks, exact-tree tidy, push and ready PR. Stop and report process gates to TOOLING.
