# Verdict compatibility split

## Baseline audit

The original compatibility test had one manifest baseline caller among 18
tracked `*-plants.json` files at `1f87b1c0`. The audit followed each of the 11
checked-runner manifests' check scripts and test dispatch. The other seven files
are historical result records without runnable baselines.

- `2026-11-05-733-load-timeouts-plants.json` needs its own manifest and the
  compatibility data to exercise its three verdict rows. The earlier baseline passed
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

Both checks call [`discover_manifests`](../../tests/checked_manifest_discovery.py).
It preserves the filesystem walk, excluded directories, JSON extension and
content predicate from `origin/main` at `1f87b1c0`. The predicate requires a JSON
object with `green`, `check` and `variants` keys. Discovery ignores candidate
decode errors and propagates file-read errors as before.

`make validate` compares the discovered set with the verdict fixture paths.
It also reads the historical records and requires each to parse as JSON and
lack the runnable manifest shape. The verdict test requires rows for every
discovered manifest and checks those rows against the recorded verdicts. Files
listed only in the fixture can be absent in the verdict test's isolated copies.
The full inventory check detects them in the repository.

## Class audit

The Nit review at `d9df1411` found one Important inventory defect and two ledger
Nits. Important round 1 at `77200883` found one recurring Important defect for
runnable historical records. The baseline audit above covers the two Nits.
This audit covers the shared discovery mechanism approved after that round.

The old test loaded its fixture at line 1074, walked and classified candidates
at lines 1075–1087, compared inventory with row paths at line 1088, and
evaluated each row at lines 1089–1092. The table groups equivalent failures
at each operation. A JSON candidate can also fail discovery by changing
encoding, losing one of the three manifest keys, or moving outside the walk.
Those changes make a listed manifest missing through the same inventory
comparison. Fixture shape errors include invalid row collections and missing,
unhashable or wrongly typed manifest keys. Missing phase, verdict, result or
expectation fields, and invalid operands inside the matcher, fail during
verdict evaluation when the old code cannot evaluate the row.

For each row, two fresh `git archive` copies used `1f87b1c0` and `eee9827b`.
Each copy ran its own test commands with a fresh interpreter and bytecode
writes disabled, then received the same input change and was restored. The
triplets are baseline, planted and restored exits. The branch columns report
the two commands independently. Plant names identify the committed patches
in [the variant directory](2026-11-24-compat-split/).

- D refers to [`tests/checked_manifest_discovery.py`](../../tests/checked_manifest_discovery.py).
- I refers to [`tests/check_plant_inventory.py`](../../tests/check_plant_inventory.py).
- V refers to [`tests/checked_plant_test.py`](../../tests/checked_plant_test.py).

| Old failure mode                                          | Branch site and line | Plant                    | Old verdict | Branch inventory | Branch verdict |
| --------------------------------------------------------- | -------------------- | ------------------------ | ----------- | ---------------- | -------------- |
| Unlisted manifest with conventional suffix                | I:26, V:1078         | `unlisted-manifest`      | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 1 → 0      |
| Unlisted manifest under a different JSON name             | I:26, V:1078         | `other-manifest`         | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 1 → 0      |
| Deleted manifest with rows still present                  | I:28                 | `deleted-manifest`       | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 0 → 0      |
| Listed path replaced with a non-manifest JSON object      | I:28                 | `invalid-manifest`       | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 0 → 0      |
| Listed file no longer decodes as JSON                     | D:21, I:28           | `malformed-manifest`     | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 0 → 0      |
| Historical record replaced with a runnable manifest       | I:23, I:26, V:1078   | `runnable-history`       | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 1 → 0      |
| All verdict rows removed for a discovered manifest        | I:26, V:1078         | `missing-verdict-rows`   | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 1 → 0      |
| Matcher reverses the exit-code comparison                 | V:1084               | `changed-legacy-verdict` | 0 → 1 → 0   | 0 → 0 → 0        | 0 → 1 → 0      |
| Compatibility fixture moved away from its required path   | I:12, V:1075         | `missing-fixture`        | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 1 → 0      |
| Compatibility fixture contains invalid JSON               | I:12, V:1075         | `malformed-fixture`      | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 1 → 0      |
| Compatibility fixture lacks the rows collection           | I:13, V:1076         | `invalid-rows`           | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 1 → 0      |
| Verdict row lacks its manifest key                        | I:13, V:1076         | `invalid-row-manifest`   | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 1 → 0      |
| Discovered manifest row lacks the phase label             | V:1082               | `invalid-verdict-phase`  | 0 → 1 → 0   | 0 → 0 → 0        | 0 → 1 → 0      |
| Verdict evaluation raises when captured stdout is missing | V:1083–1084          | `invalid-verdict-input`  | 0 → 1 → 0   | 0 → 0 → 0        | 0 → 1 → 0      |
| JSON candidate raises an I/O error on read                | D:21, I:14, V:1077   | `unreadable-json`        | 0 → 1 → 0   | 0 → 1 → 0        | 0 → 1 → 0      |

The `malformed-history` variant exercises the new requirement that a historical
entry parse. The old verdict test stayed at exit 0 in all three phases. The
`inventory-in-verdict-test` variant reintroduces full inventory equality in
the isolated verdict test and exercises the partial-checkout contract.

## Declared variants and gate

Each declared variant ran its Bash check directly in a disposable copy of the
manifest's inputs. The red phase followed successful Git initialization,
patch validation and application. The restored phase used a fresh copy of
the input bytes. Every red phase produced its manifest's named diagnostic.

| Variant                     | Baseline exit | Planted exit | Restored exit | Total elapsed |
| --------------------------- | ------------- | ------------ | ------------- | ------------- |
| `unlisted-manifest`         | 0             | 1            | 0             | 0.150 s       |
| `other-manifest`            | 0             | 1            | 0             | 0.152 s       |
| `deleted-manifest`          | 0             | 1            | 0             | 0.143 s       |
| `invalid-manifest`          | 0             | 1            | 0             | 0.146 s       |
| `malformed-manifest`        | 0             | 1            | 0             | 0.146 s       |
| `runnable-history`          | 0             | 1            | 0             | 0.144 s       |
| `missing-verdict-rows`      | 0             | 1            | 0             | 0.146 s       |
| `changed-legacy-verdict`    | 0             | 1            | 0             | 0.237 s       |
| `missing-fixture`           | 0             | 1            | 0             | 0.235 s       |
| `malformed-fixture`         | 0             | 1            | 0             | 0.240 s       |
| `invalid-rows`              | 0             | 1            | 0             | 0.239 s       |
| `invalid-row-manifest`      | 0             | 1            | 0             | 0.249 s       |
| `invalid-verdict-phase`     | 0             | 1            | 0             | 0.249 s       |
| `invalid-verdict-input`     | 0             | 1            | 0             | 0.234 s       |
| `unreadable-json`           | 0             | 1            | 0             | 0.231 s       |
| `malformed-history`         | 0             | 1            | 0             | 0.145 s       |
| `inventory-in-verdict-test` | 0             | 1            | 0             | 0.231 s       |

[plant-gate.json](2026-11-24-compat-split/plant-gate.json) sets deadlines of
24 s for the inventory manifest, 36 s for the verdict manifest and 3 s for
the final `true` action. The variant totals were 1.172 s and 2.144 s,
respectively. Each deadline is three times the sum of the 3 s launcher
allowance and four times the measured variant total rounded up to a whole
second. The final action measured 0.003 s and has a 1 s execution allowance.

The predicted elapsed gate time is 9.8 s before any lock wait.
It combines the direct variant and action measurements, the prior 1.434 s
measurement for 36 Git fingerprint commands with alternate indexes, and
5 s allowed for supervision, journaling and launch overhead. The gate's
declared step deadlines sum to 243 s, including the 36 fixed 5 s fingerprint
steps. Static validation checked the gate and variant schemas, Bash syntax,
declared inputs and nested limits. The prediction is based on direct probes.

## Checks

| Command or probe                                                            | Exit |
| --------------------------------------------------------------------------- | ---- |
| `make lint`                                                                 | 0    |
| `make validate`                                                             | 0    |
| `make test-scrut SCRUT_TEST_DIR=tests/scrut/checked-plant.md`               | 0    |
| `uv run --no-project tests/check_plant_inventory.py`                        | 0    |
| Focused unit command below, in the checkout and the load-timeout input copy | 0    |
| Direct paired and declared-variant verification                             | 0    |
| Static gate, variant and deadline validation                                | 0    |

```bash
export CHECKED_PLANT_BIN="${PWD}/plugins/plant-defects/scripts/checked-plant"
export CHECKED_PLANT_DETACHED_BIN="${PWD}/tests/fixtures/checked-plant-detached.py"
uv run --no-project --python 3.13 tests/checked_plant_test.py \
  RunnerTests.test_present_manifests_preserve_normal_verdicts \
  RunnerTests.test_verdict_code_matches_main -q
```
