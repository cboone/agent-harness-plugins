#!/usr/bin/env bash
# Negative guard input, copied into a fixture tree without execution.
set -euo pipefail

output="$(printf 'captured diagnostic' 2>&1)"
printf '%s\n' "${output}"
