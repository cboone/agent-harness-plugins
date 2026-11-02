# Pause readers before they claim delivery so the test controls the race.
set -T

function rollout_claim_boundary() {
  # shellcheck disable=SC2016,SC2154
  if [[ "${BASH_COMMAND}" == ': > "${marker}"' ]]; then
    if [[ "${ROLLOUT_CLAIM_ERROR:-}" == true ]]; then
      # Remove the fixture's empty preparation directory so claim creation fails.
      rmdir "${marker%/*}"
      return
    fi
    [[ "${ROLLOUT_SKIP_READY:-}" != "${ROLLOUT_READER:?}" ]] || exit 7
    local release
    printf '%s\n' "${ROLLOUT_READER:?}" > "${ROLLOUT_CLAIM_BARRIER:?}/ready"
    IFS= read -r -t 30 release < "${ROLLOUT_CLAIM_BARRIER}/${ROLLOUT_READER}"
    [[ "${release}" == go ]]
  fi
}

trap rollout_claim_boundary DEBUG
