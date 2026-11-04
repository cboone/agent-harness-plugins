# Checked plant runner

Build the authorized stop-the-line correction on `feat/plant-defects-checked-runner` through a ready PR. TOOLING merges; CONDUCTOR decides whether to lift the cross-session stop. No hooks change.

## Design and prior art

Extend `plant-defects` with one bundled Python runner, invoked through `uv run`, rather than another worker-owned harness. A JSON manifest declares every variant, patch, setup/check script, expected assertion output and input file. Each variant uses private input copies, strict Bash steps, baseline green, patch validation/application, setup, assertion red, restoration and restored green. Every declared variant receives an outcome; setup errors and unrun variants fail the run. Capture diagnostics, exact exits, SHA-256 fingerprints of all declared inputs, manifest and runner, and preserved failure causes in one JSON result. Render ledger and status text only from complete successful current evidence, validating every variant independently of the aggregate flag.

The model is SL-VF's `run_prerequisite_plants.py` on main, last changed in `31644156f`. Preserve its private patch paths, all-input fingerprints, preallocated unrun rows, explicit assertion verdict, failure causes and refusal gate. Replace workstream constants, AST mutations and unittest-specific strings with declared patches, scripts and exact exit/output predicates. Private copies protect the original inputs; reconstruction and a fresh interpreter/cache validate restoration. No generic mutation enumeration or live repository mutation is needed.

[Mutmut](https://github.com/boxed/mutmut/blob/main/README.rst) provides resumable Python mutation execution and result browsing, with copied supporting files. Its language-specific mutation generation does not cover targeted external instruments. [Stryker's states](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/) distinguish pending, assertion detection, runtime and compile errors. Reuse explicit outcomes, but require every plant to reach its named assertion and restore: setup errors and timeouts never count as detection. Neither tool replaces the checked publication gate required here.

## Work and validation

1. Add runner, manifest documentation and committed regression fixtures. Require its use in the skill. Bump the new capability to 1.1.0 and regenerate mirrors.
2. Prove broken patch/setup produces `setup-error` and refuses ledger generation; prove real plants reach red, restore and reach green. Cover missing inputs, incomplete/unrun results, stale inputs, strict setup, failed restore and preserved causes. Plant against the runner's verdict and publication guards.
3. Run only affected Scrut documents plus `error-output-guard.md` and `environment-isolation.md` while iterating, at most two concurrently.
4. Run the full local review order with recorded rounds and findings; baseline semgrep in a disposable clone. Run lint and required version checks, then exact-tree signed tidy.
5. Before the one full suite, wait for the specified heavy-process scan to clear, check thermal status, acquire `~/Work/projects/.locks/tooling-full-suite.d` and run `SCRUT_JOBS=2 make test-all`. Push and open ready PR only after required checks pass. Report evidence and review précis to TOOLING by mailbox.

## Structural review decision

TOOLING's native mailbox reply at `20261104T003301Z` chose a separate green-control declaration/outcome through the same checked result and publication gate. Assertion variants remain red-only; controls must remain green, restore and confirm green, with failures blocking publication. This preserves existing skill-required negative controls without hand-written harnesses. The three other Important takes preserve executable modes in copies/fingerprints, reject hard-linked record destinations, and retain timeout diagnostics and termination evidence. Apply the committed Git-reset wrapper. Take the trivial fingerprint-only allocation reduction. Plant each new boundary and continue structural round 2 at Important.
