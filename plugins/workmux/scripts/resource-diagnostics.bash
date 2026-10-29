#!/usr/bin/env bash
# Shared diagnostics; callers retain the original error and exit status.

function workmux_caller_harness() {
  case "${WORKMUX_CALLER_HARNESS:-}" in
    'Claude Code' | Codex)
      printf '%s' "${WORKMUX_CALLER_HARNESS}"
      ;;
    *)
      if [[ -n "${CODEX_THREAD_ID:-}" && -n "${CLAUDECODE:-}" ]]; then
        printf 'Claude Code/Codex (nested environment)'
      elif [[ -n "${CODEX_THREAD_ID:-}" ]]; then
        printf 'Codex'
      elif [[ -n "${CLAUDECODE:-}" ]]; then
        printf 'Claude Code'
      else
        printf 'unidentified harness'
      fi
      ;;
  esac
}

function workmux_resource_failure() {
  local resource="${1}"
  printf '%s: %s: access failed for %s; check the active sandbox and filesystem/socket permissions. Use the host approval flow for this command only when authorized; do not exclude bash or change user settings.\n' \
    "${SCRIPT_NAME:-workmux}" "$(workmux_caller_harness)" "${resource}" >&2
}

function workmux_diagnose_launch_failure() {
  local log_file="${1}" output log_path
  output="$(cat "${log_file}" 2> /dev/null)" || return 0

  case "${output}" in
    *'failed to create initial log file'*)
      case "${XDG_STATE_HOME:-}" in
        /*) log_path="${XDG_STATE_HOME}/workmux/workmux.log" ;;
        *) log_path="${HOME}/.local/state/workmux/workmux.log" ;;
      esac
      workmux_resource_failure "workmux log ${log_path}"
      ;;
    *'Operation not permitted'* | *'operation not permitted'* | *'Permission denied'* | *'permission denied'* | *'PermissionDenied'*)
      case "${output}" in
        *'error connecting to '*) workmux_resource_failure 'tmux socket named in the command output' ;;
        *'failed to load config:'* | *'failed to read configuration:'*)
          workmux_resource_failure 'GitHub CLI config named in the command output'
          ;;
        *) workmux_resource_failure 'resource named in the command output' ;;
      esac
      ;;
    *) ;;
  esac
  return 0
}
