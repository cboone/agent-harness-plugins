#!/usr/bin/env bash
# Capture child output, replay failures, and preserve nonzero child status.
# Store text in VARIABLE (- discards it); --stdout separates the stdout stream.
# --replace normalizes paths, --replay-stdout prints reports, and --error-prefix
# retains validator context. A successful child with an unwritable result returns 2.
# Background exec-log launches retain the child's PID; wait-log reaps and replays.
# A completion callback can print structured results before failure diagnostics.

function capture_child() {
  if [[ $# -lt 2 || ("${1}" != - && (! "${1}" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ || "${1}" == __capture_*)) ]]; then
    echo 'capture_child: a result variable and command are required' >&2
    return 2
  fi
  local __capture_target="${1}" __capture_stdout='' __capture_from='' __capture_to=''
  local __capture_replay=false __capture_prefix='' __capture_buffer __capture_attributes __capture_status=0
  local __capture_mode=command __capture_log='' __capture_pid='' __capture_complete='' __capture_error_stdout=false
  local __capture_stdout_prefix='' __capture_line
  local __capture_callback_status=0 __capture_read_status=0
  shift
  while [[ $# -gt 0 ]]; do
    case "${1}" in
      --stdout)
        __capture_stdout="${2:?Missing stdout destination}"
        shift 2
        ;;
      --exec-log)
        __capture_mode='exec'
        __capture_log="${2:?Missing output log}"
        shift 2
        ;;
      --wait-log)
        __capture_mode='wait'
        __capture_log="${2:?Missing output log}"
        __capture_pid="${3:?Missing child PID}"
        shift 3
        ;;
      --on-complete)
        __capture_complete="${2:?Missing completion callback}"
        shift 2
        ;;
      --error-stdout)
        __capture_error_stdout=true
        shift
        ;;
      --error-stdout-prefix)
        __capture_error_stdout=true
        __capture_stdout_prefix="${2:?Missing report prefix}"
        shift 2
        ;;
      --replace)
        __capture_from="${2:?Missing replacement source}"
        __capture_to="${3?Missing replacement text}"
        shift 3
        ;;
      --replay-stdout)
        __capture_replay=true
        shift
        ;;
      --error-prefix)
        __capture_prefix="${2?Missing error prefix}"
        shift 2
        ;;
      --)
        shift
        break
        ;;
      *) break ;;
    esac
  done
  [[ "${__capture_mode}" == wait || $# -gt 0 ]] || {
    echo 'capture_child: a command is required' >&2
    return 2
  }
  if [[ "${__capture_mode}" == exec ]]; then
    [[ "${__capture_target}" == - && -z "${__capture_complete}${__capture_stdout}" ]] || {
      echo 'capture_child: exec-log requires a discarded result and no callback' >&2
      return 2
    }
    exec "$@" > "${__capture_log}" 2>&1
  fi
  [[ "${__capture_stdout}" != - ]] || __capture_stdout=/dev/fd/3
  if [[ "${__capture_mode}" == wait ]]; then
    [[ "${__capture_pid}" =~ ^[1-9][0-9]*$ ]] || {
      echo 'capture_child: invalid child PID' >&2
      return 2
    }
    wait "${__capture_pid}" || __capture_status=$?
    __capture_buffer="$(cat "${__capture_log}")" || __capture_read_status=$?
    ((__capture_status != 0 || __capture_read_status == 0)) || __capture_status=2
  elif [[ -n "${__capture_stdout}" ]]; then
    __capture_buffer="$("$@" 2>&1 > "${__capture_stdout}")" || __capture_status=$?
  else
    __capture_buffer="$("$@" 2>&1)" || __capture_status=$?
  fi
  if [[ -n "${__capture_from}" ]]; then
    __capture_buffer="${__capture_buffer//"${__capture_from}"/${__capture_to}}"
  fi
  if [[ -n "${__capture_complete}" ]]; then
    "${__capture_complete}" "${__capture_status}" || __capture_callback_status=$?
  fi
  if [[ "${__capture_replay}" == true || ("${__capture_error_stdout}" == true && "${__capture_status}" -ne 0) ]]; then
    if [[ -n "${__capture_stdout_prefix}" && -n "${__capture_buffer}" ]]; then
      while IFS= read -r __capture_line; do
        if [[ "${__capture_line}" == "${__capture_stdout_prefix}"* ]]; then
          printf '%s\n' "${__capture_line}"
        else
          printf '%s\n' "${__capture_line}" >&2
        fi
      done <<< "${__capture_buffer}"
    else
      [[ -z "${__capture_buffer}" ]] || printf '%s\n' "${__capture_buffer}"
    fi
  elif ((__capture_status != 0)); then
    if [[ -n "${__capture_prefix}" ]]; then
      printf '%s%s\n' "${__capture_prefix}" "${__capture_buffer//$'\n'/ }" >&2
    elif [[ -n "${__capture_buffer}" ]]; then
      printf '%s\n' "${__capture_buffer}" >&2
    fi
  fi
  ((__capture_status != 0 || __capture_callback_status == 0)) || __capture_status="${__capture_callback_status}"
  if [[ "${__capture_target}" != - ]]; then
    __capture_attributes="$(declare -p "${__capture_target}" 2> /dev/null)" || __capture_attributes=''
    __capture_attributes="${__capture_attributes#declare -}"
    __capture_attributes="${__capture_attributes%% *}"
    if [[ "${__capture_attributes}" == *r* ]] || ! printf -v "${__capture_target}" '%s' "${__capture_buffer}" 2> /dev/null; then
      printf 'capture_child: cannot store output in %s\n' "${__capture_target}" >&2
      ((__capture_status != 0)) || __capture_status=2
    fi
  fi
  return "${__capture_status}"
} 3>&1
