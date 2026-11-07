#!/usr/bin/env bash
set -euo pipefail
exec uv run --no-project python docs/reviews/2026-11-07-installed-checklist-drift-plants/detector.py
