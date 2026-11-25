#!/usr/bin/env bash
set -euo pipefail

function main() {
  export CHECKED_PLANT_BIN="${PWD}/plugins/plant-defects/scripts/checked-plant"
  export CHECKED_PLANT_DETACHED_BIN="${PWD}/tests/fixtures/checked-plant-detached.py"
  uv run --no-project --python 3.13 tests/checked_plant_test.py \
    RunnerTests.test_present_manifests_preserve_normal_verdicts -q
}

main "$@"
