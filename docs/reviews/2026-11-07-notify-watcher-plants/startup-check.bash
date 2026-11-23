#!/usr/bin/env bash
set -euo pipefail
exec uv run --script docs/reviews/2026-11-07-notify-watcher-plants/detector.py startup
