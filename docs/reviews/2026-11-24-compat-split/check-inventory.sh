#!/usr/bin/env bash
set -euo pipefail

function main() (
  local checkout path
  local -r history='docs/reviews/2026-10-28-error-output-fix-plants.json'
  checkout="$(mktemp -d "${TMPDIR:-/tmp}/compat-inventory.XXXXXXXX")"
  trap 'rm -r -- "${checkout}"' EXIT
  mkdir -p "${checkout}/tests/data" "${checkout}/docs/reviews"
  cp -- tests/checked_plant_inventory_test.py tests/checked_manifest_discovery.py "${checkout}/tests/"
  jq --arg history "${history}" \
    '.historical_records |= map(select(. == $history)) | .rows |= map(select(.manifest == "review-scope-plants.json"))' \
    tests/data/checked-verdict-compatibility.json > "${checkout}/tests/data/checked-verdict-compatibility.json"
  shopt -s nullglob
  for path in ./*.json; do
    cp -- "${path}" "${checkout}/"
  done
  if [[ -f "${history}" ]]; then
    cp -- "${history}" "${checkout}/${history}"
  fi
  PYTHONDONTWRITEBYTECODE=1 uv run --no-project "${checkout}/tests/checked_plant_inventory_test.py" -q
)

main "$@"
