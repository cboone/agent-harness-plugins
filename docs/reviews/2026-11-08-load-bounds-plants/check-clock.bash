#!/usr/bin/env bash
set -euo pipefail
exec uv run --no-project tests/notification_load_test.py NotificationLoadTests.test_blocked_startup NotificationLoadTests.test_reported_deliveries_after_blocked_startup
