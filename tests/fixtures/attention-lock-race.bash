#!/usr/bin/env bash
# Deterministic stale observation and successor handoff for attention-log.
set -euo pipefail

function await_file() {
  local path="${1}" attempt
  for ((attempt = 0; attempt < 1000; attempt++)); do
    [[ ! -e "${path}" ]] || return 0
    command sleep 0.01
  done
  echo "attention-lock-race: missing barrier ${path}" >&2
  return 1
}

function pause_observer() {
  : > "${ATTENTION_RACE_DIR}/observed"
  await_file "${ATTENTION_RACE_DIR}/resume"
}

# BASH_ENV installs these only in the observer. Record the stale result before
# pausing, so returning it after the handoff reproduces the original race.
if [[ "${ATTENTION_RACE_OBSERVER:-}" == true ]]; then
  function kill() {
    local result=0
    builtin kill "$@" || result=$?
    if [[ "${1:-}" == -0 && "${2:-}" == "${ATTENTION_RACE_STOPPED:?}" ]]; then
      pause_observer || return 2
    fi
    return "${result}"
  }

  function find() {
    local output result=0
    output="$(command find "$@")" || result=$?
    if [[ "${1:-}" == "${ATTENTION_RACE_OWNER:?}" && -n "${output}" ]]; then
      pause_observer || return 2
    fi
    [[ -z "${output}" ]] || printf '%s\n' "${output}"
    return "${result}"
  }
fi

function successor() {
  local script="${1}" owner="${2}" barrier="${3}" token
  # shellcheck source=plugins/attention-log/scripts/owner-lock.bash
  source "${script%/*}/owner-lock.bash"
  owner_lock_reserve "${owner}" 8 || return 1
  token="${OWNER_LOCK_TOKEN:?}"
  printf '%s\n' "$$" > "${owner}"
  : > "${barrier}/successor-ready"
  await_file "${barrier}/release-successor"
  # The caller checks preservation before releasing the successor.
  owner_lock_release "${owner}" "${token}"
}

function main() {
  if [[ "${1:-}" == successor ]]; then
    shift
    successor "$@"
    return
  fi
  local script="${1}" state="${2}" kind="${3}" fixture="${BASH_SOURCE[0]}"
  local owner stopped observer_diagnostic result=0
  # shellcheck source=bin/lib/capture-child.bash
  source "${fixture%/*}/../../bin/lib/capture-child.bash"
  # Retain child PIDs after main returns so the EXIT trap can reap them.
  RACE_OBSERVER_PID=""
  RACE_SUCCESSOR_PID=""
  export ATTENTION_RACE_DIR="${state}/barriers"
  mkdir -p "${ATTENTION_RACE_DIR}" "${state}/sessions/s1.lock" "${state}/rotate.lock"
  if [[ "${kind}" == rotation ]]; then
    owner="${state}/rotate.lock/owner"
    head -c 5242880 /dev/zero > "${state}/events.jsonl"
  else
    owner="${state}/sessions/s1.lock/pid"
    printf 'request\037original\037\037Bash\n' > "${state}/sessions/s1.open"
  fi
  (exit 0) &
  stopped=$!
  wait "${stopped}"
  if [[ "${kind}" == session ]]; then
    printf '%s\n' "${stopped}" > "${owner}"
  else
    : > "${owner}"
    touch -t 200001010000 "${owner}"
  fi
  # Open the observed inode so replacement cannot reuse its identity.
  exec 7< "${owner}"
  trap ': > "${ATTENTION_RACE_DIR}/resume"; : > "${ATTENTION_RACE_DIR}/release-successor"; [[ -z "${RACE_OBSERVER_PID}" ]] || wait "${RACE_OBSERVER_PID}" || :; [[ -z "${RACE_SUCCESSOR_PID}" ]] || capture_child - --wait-log "${ATTENTION_RACE_DIR}/../successor.log" "${RACE_SUCCESSOR_PID}" || :' EXIT
  local event=PostToolUse
  [[ "${kind}" != rotation ]] || event=PermissionDenied
  printf '{"session_id":"s1","tool_name":"Bash"}' \
    | {
      observer_diagnostic=""
      capture_child observer_diagnostic --stdout "${state}/stdout" -- \
        env -u TMUX -u TMUX_PANE ATTENTION_LOG_DIR="${state}" BASH_ENV="${fixture}" \
        ATTENTION_RACE_OBSERVER=true ATTENTION_RACE_STOPPED="${stopped}" ATTENTION_RACE_OWNER="${owner}" \
        /bin/bash "${script}" hook "${event}"
      printf '%s' "${observer_diagnostic}" > "${state}/stderr"
    } &
  RACE_OBSERVER_PID=$!
  await_file "${ATTENTION_RACE_DIR}/observed"
  rm -- "${owner}"
  capture_child - --exec-log "${state}/successor.log" -- \
    /bin/bash "${fixture}" successor "${script}" "${owner}" "${ATTENTION_RACE_DIR}" &
  RACE_SUCCESSOR_PID=$!
  await_file "${ATTENTION_RACE_DIR}/successor-ready"
  : > "${ATTENTION_RACE_DIR}/resume"
  wait "${RACE_OBSERVER_PID}" || result=$?
  RACE_OBSERVER_PID=""
  [[ "${result}" == 0 && ! -s "${state}/stdout" ]] || return 1
  [[ -f "${owner}" && "$(cat "${owner}")" == "${RACE_SUCCESSOR_PID}" ]] || {
    echo 'live successor ownership was removed' >&2
    return 1
  }
  if [[ "${kind}" == rotation ]]; then
    [[ ! -e "${state}/events.jsonl.1" ]] || return 1
    tr -d '\000' < "${state}/events.jsonl" | jq -e '.event == "auto_denied"' > /dev/null
    grep -q 'observed aged rotation owner' "${state}/stderr"
  else
    [[ "$(cat "${state}/sessions/s1.open")" == $'request\037original\037\037Bash' ]] || return 1
    [[ ! -e "${state}/events.jsonl" ]] || return 1
    grep -q 'observed stale session owner' "${state}/stderr"
  fi
  : > "${ATTENTION_RACE_DIR}/release-successor"
  capture_child - --wait-log "${state}/successor.log" "${RACE_SUCCESSOR_PID}"
  RACE_SUCCESSOR_PID=""
  printf '%s: live successor preserved\n' "${kind}"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
