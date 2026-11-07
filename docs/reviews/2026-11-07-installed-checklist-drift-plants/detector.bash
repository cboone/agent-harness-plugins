#!/usr/bin/env bash
set -euo pipefail
source bin/lib/capture-child.bash
errors=0
awk '/^function error\(\)/,/^}/ {print}' bin/validate-plugins > error.bash
test -s error.bash
# shellcheck disable=SC1091
source error.bash
perl -pi -e 's/\*\*([^*]+)\*\*/**Renamed rule**/ if /^- \*\*/ && !$changed++' plugins/write-markdown/skills/write-markdown/references/review-checklist.md
bin/build-review-checklists
awk '/^# .* 20\./ {copy=1} /^# .* 21\./ {copy=0} copy' bin/validate-plugins > rule20.bash
test -s rule20.bash
# shellcheck disable=SC1091
source rule20.bash
if [[ "${errors}" != 1 ]]; then
  printf '%s\n' 'FAIL: stale body comparison removed'
  exit 1
fi
printf '%s\n' 'ASSERT: stale body rejected'
