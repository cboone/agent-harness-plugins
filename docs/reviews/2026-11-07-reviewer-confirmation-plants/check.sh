#!/usr/bin/env bash
set -euo pipefail
export REPO_ROOT="${PWD}" NO_COLOR=1
bash bin/run-scrut test tests/scrut/review-config-reporting.md
