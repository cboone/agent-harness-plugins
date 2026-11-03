#!/usr/bin/env bash
# Exercise cleanup with deterministic process ownership and signal responses.
unset BASH_ENV
: "${SIGNAL_PROBE_CASE:?SIGNAL_PROBE_CASE is required}"
: "${SIGNAL_PROBE_LOG:?SIGNAL_PROBE_LOG is required}"
PROBE_ACTIVE=true
PROBE_GROUP=999999
PROBE_ANCHOR=""
PROBE_STALE_ANCHOR=false
PROBE_ANCHOR_VISIBLE=true
PROBE_REAL_GROUP=false

# Simulate a lock read taken before anchor exit and a later recycled ps snapshot.
function perl() {
  if [[ "${PROBE_STALE_ANCHOR}" == true && "${1:-}" == -MFcntl=:flock ]]; then
    printf '%s\n' "${PROBE_ANCHOR}"
  elif [[ "${PROBE_ANCHOR_VISIBLE}" == false && "${1:-}" == -MFcntl=:flock ]]; then
    return 1
  else
    command perl "$@"
  fi
}

function ps() {
  [[ "$*" == '-axo pid=,ppid=,pgid=,stat=' ]] || return 2
  if [[ "${SIGNAL_PROBE_CASE}" == denied ]]; then
    echo 'inspection denied' >&2
    return 2
  fi
  printf '1 0 1 S\n'
  if [[ -n "${PROBE_ANCHOR}" && "${PROBE_ANCHOR_VISIBLE}" == true ]]; then
    printf '%s 1 %s S\n' "${PROBE_ANCHOR}" "${PROBE_GROUP}"
  fi
  [[ "${PROBE_ACTIVE}" == true ]] || return 0
  case "${SIGNAL_PROBE_CASE}" in
    reused) printf '999999 1 999999 S\n' ;;
    pregroup) printf '999999 %s 1 T\n' "$$" ;;
    group) printf '%s %s %s S\n' "${PROBE_GROUP}" "$$" "${PROBE_GROUP}" ;;
    orphan | recycled | release-race | kill-race) printf '999998 1 %s S\n' "${PROBE_GROUP}" ;;
    normal) : ;;
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
    group | orphan | normal | release-race | kill-race)
      [[ "${3}" == "-${PROBE_GROUP}" ]] || return 2
      PROBE_ACTIVE=false
      if [[ "${1}" == -KILL ]]; then PROBE_ANCHOR_VISIBLE=false; fi
      ;;
    recycled) return 2 ;;
    *) return 2 ;;
  esac
}

# End the real owned anchor with one helper call, then only inspect. Synthetic
# kills never reach real processes, even when retirement is deliberately broken.
function release_probe_anchor() {
  [[ "${PROBE_REAL_GROUP}" == true ]] || return 0
  (
    local result=0 attempt
    trap - EXIT
    unset -f ps kill perl
    read_anchor "${PROBE_GROUP}" > /dev/null || result=$?
    if ((result == 1)); then exit 0; fi
    ((result == 0)) || exit 1
    if [[ -e "${TMP_DIR}/anchor.${PROBE_GROUP}.retired" ]]; then
      rm -- "${TMP_DIR}/anchor.${PROBE_GROUP}.retired"
    fi
    signal_group KILL "${PROBE_GROUP}" || exit 1
    for ((attempt = 0; attempt < 100; attempt += 1)); do
      result=0
      read_anchor "${PROBE_GROUP}" > /dev/null || result=$?
      if ((result == 1)); then exit 0; fi
      ((result == 0)) || exit 1
      sleep 0.01
    done
    exit 1
  )
}

# Globals are read by the production cleanup functions.
# shellcheck disable=SC2034
function run_signal_probe() {
  trap - DEBUG
  # Require ps and kill stubs before exercising production signalling.
  [[ "$(type -t ps)" == function && "$(type -t kill)" == function ]] || exit 2
  TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/signal-probe.XXXXXX")"
  : > "${SIGNAL_PROBE_LOG}"
  if [[ "${SIGNAL_PROBE_CASE}" == inspect ]]; then
    mkdir "${TMP_DIR}/anchor.999999"
    local result=0
    read_anchor 999999 2> "${SIGNAL_PROBE_LOG}" || result=$? # error-output-allow: fixture asserts retained inspection context and status
    [[ "${result}" == 2 ]] || exit 1
    grep -Fq -- "open anchor ${TMP_DIR}/anchor.999999: " "${SIGNAL_PROBE_LOG}" || exit 1
    printf 'inspect: anchor open error retained\n'
    exit 0
  fi
  case "${SIGNAL_PROBE_CASE}" in
    group | orphan | normal | recycled | release-race | kill-race)
      run_in_group /usr/bin/true &
      PROBE_GROUP=$!
      PROBE_REAL_GROUP=true
      RUNNING_PIDS=("${PROBE_GROUP}")
      RUNNING_GROUPS=("${PROBE_GROUP}")
      trap 'if release_probe_anchor; then RUNNING_GROUPS=(); RUNNING_PIDS=(); cleanup; else echo "retained probe artifacts in ${TMP_DIR}" >&2; exit 4; fi' EXIT
      wait "${PROBE_GROUP}" || exit 1
      PROBE_ANCHOR="$(read_anchor "${PROBE_GROUP}")" || exit 1
      # Check the real anchor before relying on the synthetic ps snapshot.
      [[ "$(command ps -p "${PROBE_ANCHOR}" -o pgid= | tr -d ' ')" == "${PROBE_GROUP}" ]] || exit 1
      ;;
    *) : ;;
  esac
  RUNNING_PIDS=()
  if [[ "${SIGNAL_PROBE_CASE}" == pregroup ]]; then RUNNING_PIDS=(999999); fi
  RUNNING_GROUPS=("${PROBE_GROUP}")
  if [[ "${SIGNAL_PROBE_CASE}" == denied ]]; then exit 0; fi
  if [[ "${SIGNAL_PROBE_CASE}" == recycled ]]; then
    release_probe_anchor || exit 1
    PROBE_ANCHOR=""
    if [[ -e "${TMP_DIR}/anchor.${PROBE_GROUP}.retired" ]]; then
      rm -- "${TMP_DIR}/anchor.${PROBE_GROUP}.retired"
    fi
    local result=0
    signal_group TERM "${PROBE_GROUP}" || result=$?
    [[ "${result}" == 2 && ! -s "${SIGNAL_PROBE_LOG}" ]] || exit 1
    RUNNING_GROUPS=()
    printf 'recycled: no signal without anchor continuity\n'
    exit 0
  fi
  if [[ "${SIGNAL_PROBE_CASE}" == release-race || "${SIGNAL_PROBE_CASE}" == kill-race ]]; then
    # First retire a real anchor, then present a stale successful lock read.
    PROBE_ACTIVE=false
    if [[ "${SIGNAL_PROBE_CASE}" == kill-race ]]; then
      PROBE_ACTIVE=true
      SIGNAL_PROBE_CASE=orphan
      signal_group KILL "${PROBE_GROUP}" || exit 1
      SIGNAL_PROBE_CASE=kill-race
    else
      signal_group TERM "${PROBE_GROUP}" || exit 1
    fi
    release_probe_anchor || exit 1
    PROBE_ACTIVE=true
    PROBE_STALE_ANCHOR=true
    : > "${SIGNAL_PROBE_LOG}"
    local result=0
    signal_group KILL "${PROBE_GROUP}" || result=$?
    PROBE_STALE_ANCHOR=false
    [[ "${result}" == 2 && ! -s "${SIGNAL_PROBE_LOG}" ]] || exit 1
    RUNNING_GROUPS=()
    printf '%s: retired group never signalled\n' "${SIGNAL_PROBE_CASE}"
    exit 0
  fi
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
      [[ "$(cat "${SIGNAL_PROBE_LOG}")" == "$(printf '%s\n' "-TERM -- -${PROBE_GROUP}" "-KILL -- -${PROBE_GROUP}")" ]] || exit 1
      release_probe_anchor || exit 1
      printf '%s: process group TERM, anchor KILL\n' "${SIGNAL_PROBE_CASE}"
      ;;
    normal)
      [[ "$(cat "${SIGNAL_PROBE_LOG}")" == "-KILL -- -${PROBE_GROUP}" ]] || exit 1
      [[ -e "${TMP_DIR}/anchor.${PROBE_GROUP}.retired" ]] || exit 1
      release_probe_anchor || exit 1
      printf 'normal: anchor ended through helper\n'
      ;;
    *) exit 2 ;;
  esac
  exit 0
}

# Run after every production function is defined, before its entry point.
trap 'if [[ "${BASH_COMMAND}" == '\''main "$@"'\'' ]]; then run_signal_probe; fi' DEBUG
