unset BASH_ENV
# Inspect the launcher at registration, after its child has started.
function check_aspect_monitor() {
  if [[ "${BASH_COMMAND}" == 'RUNNING_PIDS+='* && "$-" == *m* ]]; then
    echo 'aspect launch enabled Bash monitor mode' >&2
  fi
  # shellcheck disable=SC2016 # Match Bash command text before expansion.
  if [[ "${BASH_COMMAND}" == 'wait "${RUNNING_PIDS['* && "${index:-0}" -gt 0 && -n "${RUNNING_PIDS[0]+set}" ]]; then
    echo 'completed aspect remains a leader signal target' >&2
  fi
}
set -T
trap check_aspect_monitor DEBUG
