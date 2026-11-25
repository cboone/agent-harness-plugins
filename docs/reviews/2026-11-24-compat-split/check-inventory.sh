#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=bin/lib/git-environment.bash
source bin/lib/git-environment.bash

function main() (
  local checkout
  checkout="$(mktemp -d "${TMPDIR:-/tmp}/compat-inventory.XXXXXXXX")"
  trap 'rm -r -- "${checkout}"' EXIT
  mkdir -p "${checkout}/tests/data"
  jq '.historical_records = [] | .rows |= map(select(.manifest == "review-scope-plants.json"))' \
    tests/data/checked-verdict-compatibility.json > "${checkout}/tests/data/checked-verdict-compatibility.json"
  cp review-scope-plants.json "${checkout}/"
  git -C "${checkout}" init --quiet --template=
  git -C "${checkout}" add -- .
  (
    cd "${checkout}"
    uv run --no-project "${OLDPWD}/tests/check_plant_inventory.py"
  )
)

main "$@"
