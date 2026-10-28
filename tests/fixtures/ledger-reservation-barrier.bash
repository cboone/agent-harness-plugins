# Pause both writers before either attempts its first reservation.
set -T

function ledger_reservation_barrier() {
  # The command is literal; these variables are save-ledger function locals.
  # shellcheck disable=SC2016,SC2154
  if [[ "${BASH_COMMAND}" == ': > "${dest}"' && "${dest}" == "${directory}/${stem}.md" ]]; then
    printf '%s\n' "${LEDGER_WRITER:?}" > "${LEDGER_BARRIER:?}/ready"
    local release
    IFS= read -r release < "${LEDGER_BARRIER:?}/${LEDGER_WRITER:?}"
    [[ "${release}" == go ]]
  fi
}

trap ledger_reservation_barrier DEBUG
