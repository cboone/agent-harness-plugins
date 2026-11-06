#!/usr/bin/env bash
set -euo pipefail
export CHECKED_PLANT_BIN="${PWD}/plugins/plant-defects/scripts/checked-plant"
export CHECKED_GATE_BIN="${PWD}/plugins/plant-defects/scripts/checked-gate"
export CHECKED_PLANT_DETACHED_BIN="${PWD}/tests/fixtures/checked-plant-detached.py"
export CHECKED_GIT_DELAY_BIN="${PWD}/tests/fixtures/checked-git-delay"
uv run --no-project --python 3.13 tests/checked_plant_test.py \
  RunnerTests.test_inspection_failure_retains_subprocess_diagnostics \
  RunnerTests.test_git_budget_and_execution_plan \
  RunnerTests.test_verdict_code_matches_main \
  RunnerTests.test_existing_manifest_normal_verdicts_are_preserved -q
uv run --no-project --python 3.13 tests/checked_gate_test.py \
  GateTests.test_pipeline_timeout_and_capture_bound -q
uv run --no-project --python 3.13 tests/checked_timeout_budget_test.py -q
echo 'inspection, pipeline and budget checks completed'
