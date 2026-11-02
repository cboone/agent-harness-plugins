#!/usr/bin/env bash
# Exercise cleanup with deterministic process ownership and signal responses.
unset BASH_ENV
: "${SIGNAL_PROBE_CASE:?SIGNAL_PROBE_CASE is required}"
: "${SIGNAL_PROBE_LOG:?SIGNAL_PROBE_LOG is required}"
PROBE_ACTIVE=true

function ps() {
  [[ "$*" == '-axo pid=,ppid=,pgid=,stat=' ]] || return 2
  if [[ "${SIGNAL_PROBE_CASE}" == denied ]]; then
    echo 'inspection denied' >&2
    return 2
  fi
  printf '1 0 1 S\n'
  [[ "${PROBE_ACTIVE}" == true ]] || return 0
  case "${SIGNAL_PROBE_CASE}" in
    reused) printf '999999 1 999999 S\n' ;;
    pregroup) printf '999999 %s 1 T\n' "$$" ;;
    group) printf '999999 %s 999999 S\n' "$$" ;;
    orphan) printf '999998 1 999999 S\n' ;;
    *) return 2 ;;
  esac
}

function kill() {
  [[ "$#" == 3 && "${2}" == -- ]] || return 2
  printf '%s\n' "$*" >> "${SIGNAL_PROBE_LOG}"
  case "${SIGNAL_PROBE_CASE}" in
    reused) PROBE_ACTIVE=false ;;
    pregroup)
      [[ "${3}" == 999999 ]] || return 2
      if [[ "${1}" == -KILL ]]; then PROBE_ACTIVE=false; fi
      ;;
    group | orphan)
      [[ "${3}" == -999999 ]] || return 2
      PROBE_ACTIVE=false
      ;;
    *) return 2 ;;
  esac
}

# Globals are read by the production cleanup functions.
# shellcheck disable=SC2034
function run_signal_probe() {
  trap - DEBUG
  # Require ps and kill stubs before exercising production signalling.
  [[ "$(type -t ps)" == function && "$(type -t kill)" == function ]] || exit 2
  TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/signal-probe.XXXXXX")"
  : > "${SIGNAL_PROBE_LOG}"
  RUNNING_PIDS=(999999)
  RUNNING_GROUPS=(999999)
  if [[ "${SIGNAL_PROBE_CASE}" == denied ]]; then exit 0; fi
  stop_running_codex || exit 1
  case "${SIGNAL_PROBE_CASE}" in
    reused)
      [[ ! -s "${SIGNAL_PROBE_LOG}" ]] || exit 1
      printf 'reused: no signal\n'
      ;;
    pregroup)
      grep -qx -- '-TERM -- 999999' "${SIGNAL_PROBE_LOG}" || exit 1
      grep -qx -- '-KILL -- 999999' "${SIGNAL_PROBE_LOG}" || exit 1
      printf 'pregroup: PID TERM and KILL\n'
      ;;
    group | orphan)
      [[ "$(cat "${SIGNAL_PROBE_LOG}")" == '-TERM -- -999999' ]] || exit 1
      printf '%s: process group TERM\n' "${SIGNAL_PROBE_CASE}"
      ;;
    *) exit 2 ;;
  esac
  exit 0
}

# Run after every production function is defined, before its entry point.
trap 'if [[ "${BASH_COMMAND}" == '\''main "$@"'\'' ]]; then run_signal_probe; fi' DEBUG
