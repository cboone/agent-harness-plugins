# Isolate Python plant bytecode

Fix [the stale-bytecode plant issue](https://github.com/cboone/agent-harness-plugins/issues/678) with guidance in the existing skill, which ships no helper. No live configuration changes.

## Prior art

- [mutmut's pytest harness](https://github.com/boxed/mutmut/blob/main/src/mutmut/runners/harness.py) runs tests under a separate `mutants` directory. Keep the isolation principle, without adding a mutation runner.
- [Cosmic Ray's restoration context](https://github.com/sixty-north/cosmic-ray/blob/master/src/cosmic_ray/util.py) restores source bytes in `finally`; that function does not clear bytecode. Source restoration alone is insufficient here.
- [pytest's assertion rewriting guidance](https://pytest.org/en/stable/how-to/assert.html#assertion-rewriting-caches-files-on-disk) supports disabling bytecode writes. Adopt that option, with explicit existing-cache handling and post-restoration cleanup.

## Implementation and verification

1. Add Python cache precautions before the workflow's plant step, covering write suppression, disposable prefixes, scoped cleanup and fresh interpreter runs. Bump `plant-defects` from 1.0.4 to 1.0.5 and regenerate mirrors.
1. Add a standalone standard-library regression test, run with `uv run --no-project tests/fixtures/plant-defects-bytecode.py`. Pin equal source size and timestamps rather than racing the clock. Cover contaminated bytecode, cleanup and both prevention options. No Python runtime is declared in the repository's Scrut setup; keep this check manual rather than adding a CI dependency for prose guidance.
1. Use the small-change review path: one Codex round for this bounded tooling fix, including its regression test. Then run `lint-and-fix --no-push`, `make test-all` without quiet flags, `check-versions`, signed logical-commit tidy with identical-tree verification, push and open a ready PR. The known base lint failure at `tests/fixtures/review-submodule-fixture` stays outside scope. TOOLING merges.
