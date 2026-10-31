# Copilot resolution reason review ledger

`monitor-pr` now passes GitHub resolution reasons, documents the disposition mapping, and preserves reason-free helper callers. Issue [463](https://github.com/cboone/agent-harness-plugins/issues/463). Base: `5205fada80635f7d9dd4a1967c94a256e60a99cb` (`origin/main` merge base).

## Local reviews

Full review order; no small-change exception. Every review used a fresh read-only Codex run, with `approval_policy=never`, web search disabled, explicit model/effort/window, and closed stdin. Successful exits and nonempty replies were checked; structured outputs passed validation. No Copilot review was requested or processed.

1. Structural Nit round: anti-patterns plus four simplify cleanup angles, `gpt-6.1-sol`, high, 872000. Anti-patterns completed with one finding: reviewer **nit**, “Docs drift: summary examples omit required resolution reasons”; severity **Nit**, misleading reporting examples; **taken**, examples corrected; **no further round**, documentation only. Altitude returned reviewer **suggestion**, “Pass parsed reasons directly across the internal resolution boundary”; severity **Nit**, optional refactor; **recorded**, retaining the shared command handler avoids another helper for two callers; **no further round**, no edit. Other cleanup angles found nothing. End: **ended: fixes changed no behavior**.
1. Focused Nit round: code, errors, tests and comments, same settings; all four validated, no findings. Types inapplicable: no typed interfaces changed. Before/after scope trees matched `3cca3676ba079a374afd43aba4bbc820350629cc`. End: **clean at Nit**.
1. Trims: `gpt-6.1-sol`, low, 872000, one round each. Comments: no changes. Text: three wording proposals taken, with no behavior change. The comment trim's offline ownership lookup failed; the parent had already verified repository ownership and archive status live. Every requested file was classified.
1. Semgrep: exit 0 in disposable shared clone at `8ff81777`, `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, `--config auto --baseline-commit 5205fada80635f7d9dd4a1967c94a256e60a99cb`. 131 rules, five targets, zero findings/errors/skipped rules. Seven files excluded by ignore policy, including fixtures and generated copies.

## Validation

- Summary contract Scrut: **18/18**. Existing resolver Scrut: **66/66**. Committed `gh` stub and executable-resolution guard only; no live thread mutation.
- Plants caught **3/3**, using disposable helper copies: accepting invalid reasons (one case failed), dropping combined-command forwarding (two), dropping the GraphQL input reason (two). No production source was changed for planting.
- Targeted ShellCheck and shfmt passed. Prettier applied to edited canonical prose; mirrors regenerated with `make build`.
- Versions: `monitor-pr` **3.4.1 → 3.5.0**, minor for the added helper capability; no separate canonical Codex manifest. Marketplace versions remain manifest-owned.
- `make validate`: passed, including JSON, fixture environment checks, catalog coverage, version ownership and generated mirrors.
- `lint-and-fix --no-push`: **failure** at `make lint`. Markdown, Prettier, ShellCheck and shfmt passed; `bin/check-fixture-environments --review-paths` reported six existing errors in `tests/fixtures/review-submodule-fixture` (lines 132, 133, 134 and 254). The brief names this baseline failure as outside scope, so no unrelated fix was made.
- TOOLING cleared continuation with the known lint failure recorded as baseline (mailbox message 000001, 2026-10-30 21:47 EDT).
- Full suite ran **once** after TOOLING's mailbox 000002 handoff (2026-10-30 23:13 EDT): `SCRUT_JOBS=2 make -k test-all`, exit **2**. **55/56 documents passed; 1887/1888 cases passed, one failed, zero skipped**. The only Scrut failure was `environment-isolation.md:39`, asserting the same six rooted-path fixture diagnostics named above. No branch-specific failure was found. The touched document's fail-fast setup sources `bin/lib/git-environment.bash`; the committed fixture refuses to invoke the helper unless `gh` resolves to its stub.
- The atomic full-suite lock recorded this workstream in `owner` and was released by the exit trap. JSON/plugin validation passed during the full run. Standalone `actionlint` passed, covering the lint recipe skipped after its failed prerequisite.
- Publication requires signed logical commits rebuilt from the recorded base, preserving the exact tree of `feat/463-copilot-resolution-reason-pre-tidy`. The final mailbox handoff records the tree comparison and ready PR.

The [plan](../plans/done/2026-10-30-copilot-resolution-reason.md) records the schema evidence and prior art. The schema result is also [recorded on the issue](https://github.com/cboone/agent-harness-plugins/issues/463#issuecomment-6537221970).
