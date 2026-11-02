# Literal GitHub titles and connected issues

Implement the remaining requirements of [literal titles](https://github.com/cboone/agent-harness-plugins/issues/438) with regression coverage for [issue detection](https://github.com/cboone/agent-harness-plugins/issues/437). Authorized through a ready PR by the overnight batch go-ahead, relayed by TOOLING. TOOLING merges.

## Existing behavior and prior art

The base already single-quotes PR creation and correction titles, explains apostrophe escaping, and filters both connected-issue strategies by final `/issues/<number>` URL segments. `create-issue` moved into `use-git` and retains three double-quoted examples. Reuse `create-deferred-issues`' single-quote pattern and issue URL guard rather than add a helper. The release example uses a fixed version title, scaffold-go-cli uses fixed text, and set-up-installers interpolates a project name; these stay outside this two-issue fix.

## Changes and validation

1. Single-quote all three issue title examples and document apostrophes. Align use-git's supporting title examples with the rule. Patch-bump use-git and rebuild generated mirrors.
1. Exercise the actual skill examples with a local gh function that captures arguments. Check backticks, command substitutions, dollar variables and apostrophes. Exercise both PR detection jq filters with issue and PR URLs, query strings and fragments.
1. Plant unsafe quoting and a permissive URL filter independently and confirm the regression checks fail, then restore the source.
1. Run the full local review order: anti-patterns with report-only simplify, focused Codex aspects, trims, disposable-clone semgrep baseline, lint-and-fix without push, all tests and version checks. Record findings and round thresholds in the review ledger.
1. Tidy to logical signed commits with an exact-tree comparison, push and open one ready PR closing both issues. Report checks and review précis to TOOLING and stop.
