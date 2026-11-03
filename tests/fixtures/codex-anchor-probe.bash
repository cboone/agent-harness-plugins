#!/usr/bin/env bash
# Exercise real anchor setup failures without launching Codex.
unset BASH_ENV
: "${SCRUT_GROUP_PROBE_MODE:?probe mode is required}"
: "${SCRUT_GROUP_PROBE_PID:?probe pid file is required}"
: "${SCRUT_GROUP_PROBE_LOG:?probe log is required}"
ANCHOR_PROBE_GROUP=""

function cleanup_anchor_probe() {
  local parent state
  trap - EXIT
  if [[ -n "${ANCHOR_PROBE_GROUP}" ]]; then
    # A failed stopped-wrapper assertion must still resume its owned child.
    read -r parent state < <(command ps -p "${ANCHOR_PROBE_GROUP}" -o ppid=,stat=) || true
    if [[ "${parent:-}" == "$$" && "${state:-}" == *T* ]]; then
      kill -CONT "${ANCHOR_PROBE_GROUP}" || true
    fi
  fi
  cleanup
}

# Globals are consumed by production cleanup.
# shellcheck disable=SC2034
function run_anchor_probe() {
  local attempt state result=0 anchor message
  trap - DEBUG
  TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/anchor-probe.XXXXXX")"
  trap cleanup_anchor_probe EXIT
  run_in_group /usr/bin/touch "${TMP_DIR}/executed" > "${TMP_DIR}/setup.log" 2>&1 & # error-output-allow: fixture checks the retained setup diagnostic and status
  ANCHOR_PROBE_GROUP=$!
  RUNNING_PIDS=("${ANCHOR_PROBE_GROUP}")
  RUNNING_GROUPS=("${ANCHOR_PROBE_GROUP}")
  if [[ "${SCRUT_GROUP_PROBE_MODE}" == anchor-stopped ]]; then
    for ((attempt = 0; attempt < 50; attempt += 1)); do
      anchor="$(read_anchor "${ANCHOR_PROBE_GROUP}")" || anchor=0
      if [[ "${anchor}" != 0 ]]; then break; fi
      sleep 0.1
    done
    [[ "${anchor}" != 0 && "${anchor}" == "$(cat "${SCRUT_GROUP_PROBE_PID}")" ]] || exit 1
    state="$(command ps -p "${ANCHOR_PROBE_GROUP}" -o stat=)" || exit 1
    [[ "${state}" == *T* && ! -e "${TMP_DIR}/executed" ]] || exit 1
    stop_running_codex || exit 1
    message='anchor-stopped: published while wrapper stopped, bounded cleanup'
  else
    for ((attempt = 0; attempt < 80; attempt += 1)); do
      state="$(command ps -p "${ANCHOR_PROBE_GROUP}" -o stat=)" || true
      if [[ -z "${state}" || "${state}" == *Z* ]]; then break; fi
      sleep 0.1
    done
    if ((attempt == 80)); then
      echo 'wrapper exceeded setup bound' >&2
      exit 1
    fi
    wait "${ANCHOR_PROBE_GROUP}" || result=$?
    unset 'RUNNING_PIDS[0]'
    [[ "${result}" != 0 && ! -e "${TMP_DIR}/executed" ]] || exit 1
    case "${SCRUT_GROUP_PROBE_MODE}" in
      anchor-publish) grep -q '^codex-aspects: anchor pid:' "${TMP_DIR}/setup.log" || exit 1 ;;
      anchor-ready)
        grep -q '^codex-aspects: anchor readiness failed' "${TMP_DIR}/setup.log" || exit 1
        grep -q '^codex-aspects: anchor readiness: No space left on device' "${TMP_DIR}/setup.log" || exit 1
        ;;
      anchor-timeout | anchor-brokenpipe) grep -q '^codex-aspects: anchor readiness timed out' "${TMP_DIR}/setup.log" || exit 1 ;;
      *) exit 2 ;;
    esac
    if [[ "${SCRUT_GROUP_PROBE_MODE}" == anchor-brokenpipe ]]; then
      : > "${SCRUT_GROUP_PROBE_LOG}.resume"
      for ((attempt = 0; attempt < 30; attempt += 1)); do
        if grep -q '^ready write returned EPIPE$' "${SCRUT_GROUP_PROBE_LOG}"; then break; fi
        sleep 0.1
      done
      grep -q '^ready write attempted$' "${SCRUT_GROUP_PROBE_LOG}" || exit 1
      grep -q '^ready write returned EPIPE$' "${SCRUT_GROUP_PROBE_LOG}" || exit 1
      grep -q '^codex-aspects: anchor readiness: Broken pipe' "${TMP_DIR}/setup.log" || exit 1
    fi
    # Failed setup leaves the anchor to the helper, including unpublished PIDs.
    [[ -s "${SCRUT_GROUP_PROBE_PID}" ]] || exit 1
    anchor="$(cat "${SCRUT_GROUP_PROBE_PID}")"
    state="$(command ps -p "${anchor}" -o stat=)" || true
    [[ -n "${state}" && "${state}" != *Z* ]] || exit 1
    read_anchor "${ANCHOR_PROBE_GROUP}" > /dev/null || exit 1
    stop_running_codex || exit 1
    message="${SCRUT_GROUP_PROBE_MODE}: setup failed, no exec, anchor stopped"
  fi
  [[ -s "${SCRUT_GROUP_PROBE_PID}" ]] || exit 1
  anchor="$(cat "${SCRUT_GROUP_PROBE_PID}")"
  state="$(command ps -p "${anchor}" -o stat=)" || true
  [[ -z "${state}" || "${state}" == *Z* ]] || exit 1
  printf '%s\n' "${message}"
  exit 0
}

trap 'if [[ "${BASH_COMMAND}" == '\''main "$@"'\'' ]]; then run_anchor_probe; fi' DEBUG
