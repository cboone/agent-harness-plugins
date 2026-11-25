# Verdict compatibility split

## Baseline audit

The original compatibility test had one manifest baseline caller among 18
tracked `*-plants.json` files at `1f87b1c0`. The audit followed each of the 11
checked-runner manifests' check scripts and test dispatch. The other seven files
are historical result records without runnable baselines.

- `2026-11-05-733-load-timeouts-plants.json` needs its own manifest and the
  compatibility data to exercise its three verdict rows. Its baseline passed
  in 38.216 s with only the remaining declared inputs and that single manifest.
  The ten other manifests served the inventory. The detector inputs also fed
  the load-timeout baseline's audit of detector waits. The isolated copy no
  longer audits the notification reader detectors' waits. The full-checkout
  audit still covers those waits.
- `2026-11-24-779-verdicts-plants.json` adds a second caller. Its baseline
  exercises the three verdict rows for `review-scope-plants.json` in a
  single-manifest copy.

The eight manifests added by PR 778 were removed from that input list.

- `2026-11-07-installed-checklist-drift-plants.json`
- `2026-11-07-repourl-stated-check-plants.json`
- `2026-11-07-reviewer-confirmation-plants.json`
- `2026-11-08-load-bounds-clock-real-grace-clock-plants.json`
- `2026-11-08-load-bounds-lifecycle-owner-finalizer-disabled-plants.json`
- `2026-11-08-load-bounds-lifecycle-registration-diagnostic-suppressed-plants.json`
- `2026-11-08-load-bounds-readers-early-reader-1-plants.json`
- `2026-11-08-load-bounds-readers-early-reader-5-plants.json`

`review-scope-plants.json` and `review-validity-policy-plants.json` were also
removed. The supporting inputs removed were the installed-checklist
check and detector, the repository-URL check, the reviewer-confirmation check,
the three load-bounds check scripts, and `tests/notification_load_test.py`.

## Inventory and verdict checks

`make validate` runs the inventory validator in the pull-request CI job. It
compares tracked JSON objects with `green`, `check` and `variants`, plus all
tracked `*-plants.json` paths, against verdict fixture paths and the explicit
historical records. The CI index represents the checked-out commit.
The existing checked-plant Scrut document runs the verdict test, which evaluates
recorded phases for the listed manifests present in its checkout and requires
each to parse as a JSON object with those three keys.

## Defect proofs

Each phase ran the manifest's check script with
`bash -euo pipefail -- <check script>` in a disposable copy. The inventory
script set up a separate miniature Git checkout and staged a new manifest for
each red phase. The verdict variants copied only `review-scope-plants.json`.
Each variant used a fresh Python cache and a restored copy for its final green
phase. These are direct measurements without a heavy lock.

| Variant                            | Named assertion                               | Baseline exit and time | Red exit and time | Restored exit and time | Variant elapsed |
| ---------------------------------- | --------------------------------------------- | ---------------------- | ----------------- | ---------------------- | --------------- |
| Unlisted manifest                  | Validator names `unlisted-plants.json`        | 0 in 0.119 s           | 1 in 0.122 s      | 0 in 0.113 s           | 0.390 s         |
| Manifest under another filename    | Validator names `other-manifest.json`         | 0 in 0.182 s           | 1 in 0.132 s      | 0 in 0.113 s           | 0.473 s         |
| Inventory equality in verdict test | Single manifest fails inventory equality      | 0 in 0.236 s           | 1 in 0.236 s      | 0 in 0.239 s           | 0.755 s         |
| Inverted expected verdict          | Single manifest fails named verdict subtests  | 0 in 0.235 s           | 1 in 0.236 s      | 0 in 0.250 s           | 0.768 s         |
| Listed manifest replaced with `{}` | Verdict test names `review-scope-plants.json` | 0 in 0.274 s           | 1 in 0.235 s      | 0 in 0.235 s           | 0.791 s         |

In a disposable clone, staging `unlisted-plants.json` made `make validate` exit
2 in 0.03 s with the named path. After removing that specimen from the clone's
index and checkout, the command exited 0 in 50.03 s.

## Proposed gate

[plant-gate.json](2026-11-24-compat-split/plant-gate.json) budgets 21 s for the
inventory manifest, 39 s for the verdict manifest, and 3 s for the final
`true` action. The execution reserve leaves one third of each configured limit
for command execution. The command budget reserves 3 s for launcher and
supervision overhead plus four times the measured elapsed time for that
manifest, rounded up to whole seconds before multiplying by three. The action
takes less than 0.01 s and gets a 1 s execution allowance.

The five variants took 3.176 s together. The 36 Git fingerprint commands took
1.434 s in the original preflight using alternate indexes. With 5 s for runner,
journal and launcher overhead, the predicted elapsed gate time is about 10 s
before lock wait. Declared step deadlines sum to 243 s, including the runner's
36 fixed 5 s Git steps. Schema, Bash syntax, input paths and nested limits were
validated statically with exit 0.

## Checks

| Command                                                                                                      | Exit |
| ------------------------------------------------------------------------------------------------------------ | ---- |
| `corepack yarn install --immutable`                                                                          | 0    |
| `make lint`                                                                                                  | 0    |
| `make validate`                                                                                              | 0    |
| `make test-scrut SCRUT_TEST_DIR=tests/scrut/checked-plant.md`                                                | 0    |
| `uv run --no-project tests/check_plant_inventory.py`                                                         | 0    |
| `bash -euo pipefail -- docs/reviews/2026-11-05-733-load-timeouts-plants/check.sh` in the declared-input copy | 0    |
| `git diff --check` and `git diff --cached --check`                                                           | 0    |

The two focused Python tests exited 0 with the plant runner and detached fixture
paths exported.

```bash
uv run --no-project --python 3.13 tests/checked_plant_test.py \
  RunnerTests.test_present_manifests_preserve_normal_verdicts \
  RunnerTests.test_verdict_code_matches_main -q
```
