# shellcheck shell=bash
# Pause the watcher's second owner check, after its first EOF observation.
function kill() {
  if [[ "${1:-}" == -0 && "${2:-}" == "${ROLLOUT_OWNER_PID:-}" ]]; then
    local count=0 attempt count_file="${ROLLOUT_OWNER_COUNT:?}" ready_file="${ROLLOUT_OWNER_READY:?}" release_file="${ROLLOUT_OWNER_RELEASE:?}"
    if [[ -f "${count_file}" ]]; then read -r count < "${count_file}"; fi
    count=$((count + 1))
    printf '%s\n' "${count}" > "${count_file}"
    if ((count == 2)); then
      : > "${ready_file}"
      for ((attempt = 0; attempt < 150; attempt++)); do
        [[ ! -f "${release_file}" ]] || break
        /bin/sleep 0.02
      done
      ((attempt < 150)) || return 1
    fi
  fi
  builtin kill "$@"
}
