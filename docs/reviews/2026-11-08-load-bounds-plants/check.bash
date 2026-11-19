#!/usr/bin/env bash
set -euo pipefail
exec uv run --no-project tests/notification_load_test.py NotificationLoadTests.test_draining_snapshot_readers
