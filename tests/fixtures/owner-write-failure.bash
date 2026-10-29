#!/usr/bin/env bash
# Inject a PID-write failure after exclusive owner-file creation succeeds.

function printf() {
  if [[ "${LOCK_TEST_MODE:-}" == write && $# -eq 2 && ("${1}" == '%s' || "${1}" == '%s\n') && "${2}" == "$$" ]]; then
    echo 'injected owner write failure' >&2
    return 74
  fi
  # Preserve printf's caller-supplied format when forwarding other writes.
  # shellcheck disable=SC2059
  builtin printf "$@" || return "$?"
  if [[ "${LOCK_TEST_MODE:-}" == handoff && "${LOCK_TEST_ROLE:-}" == second && $# -eq 2 && "${1}" == '%s' && "${2}" == "$$" ]]; then
    touch "${LOCK_TEST_BARRIER:?}/second-owned"
    local attempt
    for ((attempt = 0; attempt < 200; attempt++)); do
      [[ ! -e "${LOCK_TEST_BARRIER}/release-second" ]] || return 0
      "${LOCK_TEST_REAL_SLEEP:?}" 0.05
    done
    echo 'second cache owner barrier timed out' >&2
    return 1
  fi
}

function echo() {
  if [[ "${LOCK_TEST_REPORT_ORDER:-}" == true && "$*" == *'owner-lock: cannot release '* ]]; then
    if ! grep -q '"event":"auto_denied"' "${ATTENTION_LOG_DIR:?}/events.jsonl"; then
      touch "${LOCK_TEST_DIRECTORY:?}/reported-before-append"
    fi
  fi
  builtin echo "$@"
}
