#!/usr/bin/env bash
# Source through BASH_ENV to cancel immediately before launch registration.
unset BASH_ENV
: "${CODEX_STUB_PID_DIR:?CODEX_STUB_PID_DIR is required}"

function cancel_before_registration() {
  case "${1}" in
    'RUNNING_PIDS+=('*)
      trap - DEBUG
      local attempt stub group
      for ((attempt = 0; attempt < 50; attempt += 1)); do
        [[ -s "${CODEX_STUB_PID_DIR}/code.pid" ]] && break
        sleep 0.1
      done
      stub="$(cat "${CODEX_STUB_PID_DIR}/code.pid")"
      group="$(ps -p "${stub}" -o pgid= | tr -d ' ')"
      [[ "${group}" == "${stub}" ]] || exit 1
      echo "launch boundary reached with isolated group"
      kill -TERM "$$"
      ;;
    *) ;;
  esac
}

# Function tracing makes DEBUG reach cmd_run on Bash 3.2 as well as newer Bash.
set -T
trap 'cancel_before_registration "${BASH_COMMAND}"' DEBUG
