# General Inbox thread subjects

## Scope and authority

The relayed go-ahead covers the subject wording, patch bump, generated mirror,
local checks and a PR ready for review. TOOLING owns merging. No live config changes.
The brief selects the small-change path in the shared project rules.

The skill now requires an explicit single-line plain-text subject naming the
whole piece of work, with a lasting example and the reason to avoid the default.
The meaning matches step 1 of the shared Inbox reference at sl-vf `9b73daf9`.
The plugin README has no duplicate subject guidance; the plugin has no references.
The patch version changes from `1.0.0` to `1.0.1`.

## Review round 1

- Base: `8eb906ea718c36324755f8e11712c12fe19d5daf`, the merge base with `origin/main`.
- Reviewed head: `e1be9b53`; snapshot: `62ca2233bd04fe1c9ed05562ca25d4b020c510ad`.
- Entry point: installed `review-pr-with-codex` helper, standalone `codex exec`.
- Settings: `gpt-6.1-sol`, high effort, 872000-token window, read-only sandbox.
- Code and comments aspects ran in parallel; both exited 0 with valid JSON and
  empty findings. Reviewer labels, severity, disposition and review-again calls:
  none, because there were no findings.
- Errors, tests and types skipped: no executable logic, error handling, tests or
  types changed. Simplify not selected. Structural review, separate trims and
  Semgrep replaced by this round under the authorized small-change path.
- Before/after tree: `1fa9cf79b3526d4cbf1c3477225b4d7e1556cf96`.
  No lasting changes found; scope unchanged.
- The code aspect could not query GitHub in its sandbox. The worker independently
  confirmed the repository is active and has no fork parent before editing.
- End state: clean at Nit. No design calls or planted defects were needed for
  this wording-only change.

## Validation

- Corepack immutable install and `make build`: passed.
- Check-versions: forward patch bump, all 60 marketplace entries registered,
  manifest-only version ownership and matching optional Codex manifests passed.
- `lint-and-fix --no-push` uses the documented `make lint` and `make validate`
  check commands, first through `make test-all`, then as final verification.
  Markdownlint, Prettier and shfmt run check-only by project policy: the shared
  rules prohibit reformatting Scrut files, and generated copies cannot be edited
  directly. ShellCheck, actionlint and the repository validators have no fixer.
  No lint fixes were needed. Final results and tidy verification belong in the
  worker's mailbox handoff.
