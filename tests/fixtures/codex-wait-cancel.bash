#!/usr/bin/env bash
# Cancel at the second wait after the first aspect's PID was removed.
unset BASH_ENV
: "${CODEX_STUB_PID_DIR:?CODEX_STUB_PID_DIR is required}"

function cancel_after_waited_aspect() {
  # shellcheck disable=SC2016 # Inspect literal Bash command text before expansion.
  if [[ "${1}" != 'wait "${RUNNING_PIDS['* || "${index:-0}" != 1 ]]; then return; fi
  trap - DEBUG
  [[ -z "${RUNNING_PIDS[0]+set}" ]] || exit 1
  local attempt
  for ((attempt = 0; attempt < 50; attempt += 1)); do
    [[ -s "${CODEX_STUB_PID_DIR}/errors.pid" ]] && break
    sleep 0.1
  done
  [[ -s "${CODEX_STUB_PID_DIR}/errors.pid" ]] || exit 1
  echo 'waited aspect PID removed before cancellation'
  kill -TERM "$$"
}

set -T
trap 'cancel_after_waited_aspect "${BASH_COMMAND}"' DEBUG
