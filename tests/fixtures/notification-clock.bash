#!/usr/bin/env bash
# Loaded by the fixture copy before main; detached jobs remain owned here.
NOTIFY_TEST_CHILDREN=()
NOTIFY_TEST_DIAGNOSTICS=""
if [[ -n "${NOTIFY_TEST_LOG:-}" ]]; then
  NOTIFY_TEST_DIAGNOSTICS="$(mktemp "${NOTIFY_TEST_LOG}.diagnostics.XXXXXX")" || return 2
  export NOTIFY_TEST_RUN="${NOTIFY_TEST_DIAGNOSTICS}"
  exec 7>> "${NOTIFY_TEST_DIAGNOSTICS}" # error-output-allow: descriptor 7 owns fixture diagnostics; standard streams stay live
fi

function disown() { NOTIFY_TEST_CHILDREN+=("$!"); }

function notification_finish() {
  local result=$? child child_status
  for child in ${NOTIFY_TEST_CHILDREN[@]+"${NOTIFY_TEST_CHILDREN[@]}"}; do
    child_status=0
    wait "${child}" || child_status=$?
    if ((child_status != 0)); then
      printf 'notification-clock: detached notifier %s exited %s\n' "${child}" "${child_status}" >&2
      if [[ "${child_status}" == 2 ]]; then result=2; elif [[ "${result}" == 0 ]]; then result="${child_status}"; fi
    fi
  done
  if ((result != 0)) && [[ -n "${NOTIFY_TEST_DIAGNOSTICS}" && -s "${NOTIFY_TEST_DIAGNOSTICS}" ]]; then
    cat "${NOTIFY_TEST_DIAGNOSTICS}" >&2 || result=2
  fi
  exit "${result}"
}

function notification_owner_interrupt() {
  if [[ -z "${NOTIFY_TEST_OWNER_PID}" ]]; then
    # Defer cancellation across launch until the first PID registration.
    NOTIFY_TEST_PENDING_SIGNAL="${1}"
  else
    printf 'notification-clock: owner interrupted %s\n' "${1}" >&7
    exit "${1}"
  fi
}

function notification_register_backend() {
  [[ "${1}" =~ ^[1-9][0-9]*$ ]] || {
    NOTIFY_TEST_OWNER_FAILURE=2
    return 2
  }
  if [[ -z "${NOTIFY_TEST_OWNER_PID}" ]]; then
    NOTIFY_TEST_OWNER_PID="${1}"
    if [[ -n "${NOTIFY_TEST_REGISTRATION:-}" ]]; then
      if ! printf '%s\t%s\n' "${1}" "${NOTIFY_TEST_BACKEND_PATH:?}" 2>&7 >> "${NOTIFY_TEST_REGISTRATION}"; then # error-output-allow: owned descriptor retains probe errors without moving backend ownership into a capture subshell
        printf 'notification-clock: cannot record backend registration at %s\n' "${NOTIFY_TEST_REGISTRATION}" >&7
        NOTIFY_TEST_OWNER_FAILURE=2
        return 2
      fi
    fi
    if ((NOTIFY_TEST_PENDING_SIGNAL != 0)); then notification_owner_interrupt "${NOTIFY_TEST_PENDING_SIGNAL}"; fi
  fi
  [[ "${NOTIFY_TEST_OWNER_PID}" == "${1}" ]] || {
    NOTIFY_TEST_OWNER_FAILURE=2
    return 2
  }
}

# Tick only after backend readiness. Other sleeps advance without real delay.
function sleep() {
  [[ "${1}" == 1 && -n "${pid:-}" ]] || return 0
  if [[ "${NOTIFY_TEST_FAIL_READY:-}" == 1 ]]; then
    echo 'notification-clock: injected readiness failure' >&7
    return 2
  fi
  local deadline=$((SECONDS + 120))
  while [[ "${NOTIFY_TEST_PAUSE_READY:-}" == 1 || ! -f "${NOTIFY_TEST_RUN:?}.${pid}.ready" ]] && kill -0 "${pid}" 2> /dev/null; do # error-output-allow: fixture readiness checks its own registered backend
    if ((SECONDS >= deadline)); then
      printf 'notification-clock: backend %s not ready before liveness bound\n' "${pid}" >&7
      return 2
    fi
    if [[ "${NOTIFY_TEST_PAUSE_READY:-}" != 1 && -f "${NOTIFY_TEST_RUN:?}.${pid}.starting" && ! -f "${NOTIFY_TEST_RUN:?}.${pid}.released" ]]; then
      : > "${NOTIFY_TEST_RUN:?}.${pid}.released"
      printf 'run\n' > "${NOTIFY_TEST_RUN:?}.${pid}.start"
    fi
    "${NOTIFY_TEST_REAL_SLEEP:?}" 0.02
  done
  printf '%s\n' "${pid}" >> "${NOTIFY_TEST_LOG:?}.ticks"
}

function kill() {
  if [[ "${NOTIFY_TEST_OWNER_ACTIVE:-}" != 1 ]]; then
    builtin kill "$@"
    return
  fi
  if [[ "${1:-}" == -0 ]]; then
    notification_register_backend "${2}" || return 2
    builtin kill "$@"
    return
  fi
  if [[ "${1:-}" != -KILL && "${1:-}" != -TERM && "${1:-}" != -INT ]]; then
    builtin kill "$@"
    return
  fi
  [[ "${NOTIFY_TEST_OWNER_PID}" == "${2}" ]] || {
    NOTIFY_TEST_OWNER_FAILURE=2
    return 2
  }
  NOTIFY_TEST_STOP_SIGNAL="${1}"
  builtin kill "$@" 2>&7 || return # error-output-allow: owned descriptor retains probe errors without moving backend ownership into a capture subshell
  if [[ "${1}" == -KILL ]]; then
    NOTIFY_TEST_OBSERVED_EXIT=0
    wait "${2}" || NOTIFY_TEST_OBSERVED_EXIT=$?
  fi
}

function notification_publish_backend() {
  if [[ "${NOTIFY_TEST_FAIL_OBSERVATION:-}" == 1 ]]; then
    echo 'notification-clock: injected observation failure' >&7
    return 2
  fi
  printf '%s %s %s\n' "${NOTIFY_TEST_STOP_SIGNAL}" "${NOTIFY_TEST_OBSERVED_EXIT}" "${NOTIFY_TEST_CLEANUP_EXIT}" >> "${NOTIFY_TEST_LOG:?}.backend" || return 2
  if [[ -n "${NOTIFY_TEST_OBSERVATION:-}" ]]; then
    printf '%s %s %s\n' "${NOTIFY_TEST_STOP_SIGNAL}" "${NOTIFY_TEST_OBSERVED_EXIT}" "${NOTIFY_TEST_CLEANUP_EXIT}" > "${NOTIFY_TEST_OBSERVATION}" || return 2
  fi
}

# Finalize every exit before publishing; cleanup cannot rewrite observed success.
function notification_owner_finish() {
  local result=$?
  trap - EXIT
  trap '' HUP INT TERM
  if ((result == 0 && NOTIFY_TEST_OWNER_FAILURE != 0)); then result="${NOTIFY_TEST_OWNER_FAILURE}"; fi
  if ((result == 0 && NOTIFY_TEST_PENDING_SIGNAL != 0)); then result="${NOTIFY_TEST_PENDING_SIGNAL}"; fi
  NOTIFY_TEST_CLEANUP_EXIT=none
  if [[ -n "${NOTIFY_TEST_OWNER_PID}" ]]; then
    if [[ -z "${NOTIFY_TEST_OBSERVED_EXIT}" ]]; then
      if builtin kill -0 "${NOTIFY_TEST_OWNER_PID}" 2> /dev/null; then # error-output-allow: owned backend existence selects cleanup
        NOTIFY_TEST_OBSERVED_EXIT=running
        if ! builtin kill -KILL "${NOTIFY_TEST_OWNER_PID}" 2>&7; then # error-output-allow: owned descriptor retains probe errors without moving backend ownership into a capture subshell
          echo 'notification-clock: cannot stop owned backend' >&7
          ((result != 0)) || result=2
        fi
        NOTIFY_TEST_CLEANUP_EXIT=0
        wait "${NOTIFY_TEST_OWNER_PID}" || NOTIFY_TEST_CLEANUP_EXIT=$?
      else
        NOTIFY_TEST_OBSERVED_EXIT=0
        wait "${NOTIFY_TEST_OWNER_PID}" || NOTIFY_TEST_OBSERVED_EXIT=$?
      fi
    fi
    if ((result == 0)) && [[ "${NOTIFY_TEST_OBSERVED_EXIT}" =~ ^[0-9]+$ && "${NOTIFY_TEST_OBSERVED_EXIT}" != 0 ]]; then
      if [[ "${NOTIFY_TEST_STOP_SIGNAL} ${NOTIFY_TEST_OBSERVED_EXIT}" != "-KILL 137" ]]; then
        printf 'notification-clock: backend exited %s\n' "${NOTIFY_TEST_OBSERVED_EXIT}" >&7
        result="${NOTIFY_TEST_OBSERVED_EXIT}"
      fi
    fi
    if ! notification_publish_backend; then
      echo 'notification-clock: cannot publish backend observation' >&7
      ((result != 0)) || result=2
    fi
  fi
  exit "${result}"
}

function run_alerter() {
  exec 2>&7 # error-output-allow: owner diagnostics are replayed by notification_finish
  if ! declare -F notification_original_run_alerter > /dev/null; then
    echo 'notification-clock: original backend function is unavailable' >&7
    return 2
  fi
  NOTIFY_TEST_OWNER_ACTIVE=1
  NOTIFY_TEST_OWNER_PID=""
  NOTIFY_TEST_OWNER_FAILURE=0
  NOTIFY_TEST_PENDING_SIGNAL=0
  NOTIFY_TEST_STOP_SIGNAL=none
  NOTIFY_TEST_OBSERVED_EXIT=""
  trap 'notification_owner_finish 2>&7' EXIT # error-output-allow: owned descriptor retains probe errors without moving backend ownership into a capture subshell
  trap 'notification_owner_interrupt 129' HUP
  trap 'notification_owner_interrupt 143' TERM
  case "${NOTIFY_TEST_INTERRUPT_BEFORE_REGISTER:-}" in
    "") ;;
    129 | 143) notification_owner_interrupt "${NOTIFY_TEST_INTERRUPT_BEFORE_REGISTER}" ;;
    *)
      echo 'notification-clock: invalid deferred interruption' >&7
      return 2
      ;;
  esac
  notification_original_run_alerter "$@"
}
