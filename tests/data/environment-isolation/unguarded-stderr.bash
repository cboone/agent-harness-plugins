#!/usr/bin/env bash
# Negative guard input, copied into a fixture tree without execution.
set -euo pipefail

printf 'captured diagnostic\n' 2> captured-error.log
