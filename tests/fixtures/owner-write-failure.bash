#!/usr/bin/env bash
# Inject a PID-write failure after exclusive owner-file creation succeeds.

function printf() {
  if [[ "${LOCK_TEST_MODE:-}" == write && $# -eq 2 && "${1}" == '%s' && "${2}" == "$$" ]]; then
    echo 'injected owner write failure' >&2
    return 74
  fi
  # Preserve printf's caller-supplied format when forwarding other writes.
  # shellcheck disable=SC2059
  builtin printf "$@"
}
