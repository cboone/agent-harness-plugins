#!/usr/bin/env bash
# Shared owner-file reservations. Call reserve/release in checked conditions.
# Slots 8 and 9 retain open-file identity until release, independently of PID text.
# shellcheck disable=SC2034

OWNER_LOCK_TOKEN=""
OWNER_LOCK_SEQUENCE=0
OWNER_LOCK_TOKEN_8=""
OWNER_LOCK_TOKEN_9=""
OWNER_LOCK_PATH_8=""
OWNER_LOCK_PATH_9=""
OWNER_LOCK_INODE_8=""
OWNER_LOCK_INODE_9=""
OWNER_LOCK_CAPTURED_INODE=""

function owner_lock_inode() {
  local listing
  if ! listing="$(ls -diL -- "${1}" 2>&1)"; then
    echo "owner-lock: cannot inspect reservation ${1}: ${listing}" >&2
    return 1
  fi
  read -r OWNER_LOCK_CAPTURED_INODE _ <<< "${listing}"
  if [[ ! "${OWNER_LOCK_CAPTURED_INODE}" =~ ^[0-9]+$ ]]; then
    echo "owner-lock: invalid reservation inode for ${1}" >&2
    return 1
  fi
}

function owner_lock_close() {
  case "${1}" in
    8)
      exec 8>&-
      OWNER_LOCK_TOKEN_8=""
      OWNER_LOCK_PATH_8=""
      OWNER_LOCK_INODE_8=""
      ;;
    9)
      exec 9>&-
      OWNER_LOCK_TOKEN_9=""
      OWNER_LOCK_PATH_9=""
      OWNER_LOCK_INODE_9=""
      ;;
    *) return 1 ;;
  esac
}

# Reserves path $1 with unused descriptor $2 (8 or 9). Call directly in the
# shell that will release it; save OWNER_LOCK_TOKEN and retain the descriptor.
# Returns 0 on acquisition, 1 on contention, 2 on error (diagnosed on stderr).
function owner_lock_reserve() {
  local path="${1}" slot="${2}" diagnostic error had_noclobber=false result=0
  local LC_ALL=C
  export LC_ALL
  OWNER_LOCK_TOKEN=""
  case "${slot}" in
    8) [[ -z "${OWNER_LOCK_TOKEN_8}" ]] || {
      echo "owner-lock: descriptor 8 is already reserved: ${path}" >&2
      return 2
    } ;;
    9) [[ -z "${OWNER_LOCK_TOKEN_9}" ]] || {
      echo "owner-lock: descriptor 9 is already reserved: ${path}" >&2
      return 2
    } ;;
    *)
      echo "owner-lock: invalid owner descriptor for ${path}" >&2
      return 2
      ;;
  esac
  [[ ! -e "${path}" && ! -L "${path}" ]] || return 1
  if ! diagnostic="$(mktemp "${path}.diagnostic.XXXXXX" 2>&1)"; then
    echo "owner-lock: cannot create ${path}: ${diagnostic}" >&2
    return 2
  fi
  [[ ! -o noclobber ]] || had_noclobber=true
  set -o noclobber
  case "${slot}" in
    8) { exec 8> "${path}"; } 2>> "${diagnostic}" || result=$? ;;
    9) { exec 9> "${path}"; } 2>> "${diagnostic}" || result=$? ;;
    *) result=2 ;;
  esac
  [[ "${had_noclobber}" == true ]] || set +o noclobber
  error="$(cat "${diagnostic}")" || error='cannot read reservation diagnostic'
  if ! rm -- "${diagnostic}"; then
    echo "owner-lock: cannot remove reservation diagnostic ${diagnostic}" >&2
  fi
  if ((result != 0)); then
    [[ "${error}" != *': cannot overwrite existing file' ]] || return 1
    echo "owner-lock: cannot create ${path}: ${error}" >&2
    return 2
  fi
  if ! owner_lock_inode "/dev/fd/${slot}"; then
    echo "owner-lock: cannot capture reservation identity for ${path}; manual cleanup may be required" >&2
    owner_lock_close "${slot}"
    return 2
  fi
  OWNER_LOCK_SEQUENCE=$((OWNER_LOCK_SEQUENCE + 1))
  OWNER_LOCK_TOKEN="$$:${slot}:${OWNER_LOCK_SEQUENCE}"
  case "${slot}" in
    8)
      OWNER_LOCK_TOKEN_8="${OWNER_LOCK_TOKEN}"
      OWNER_LOCK_PATH_8="${path}"
      OWNER_LOCK_INODE_8="${OWNER_LOCK_CAPTURED_INODE}"
      ;;
    9)
      OWNER_LOCK_TOKEN_9="${OWNER_LOCK_TOKEN}"
      OWNER_LOCK_PATH_9="${path}"
      OWNER_LOCK_INODE_9="${OWNER_LOCK_CAPTURED_INODE}"
      ;;
    *) return 2 ;;
  esac
  return 0
}

# Unlinks only the matching reservation and diagnoses failures on stderr.
# The descriptor prevents inode reuse. Reclaim's check/unlink race remains separate.
function owner_lock_release() {
  local path="${1}" token="${2}" slot inode error result=0
  if [[ -n "${token}" && "${token}" == "${OWNER_LOCK_TOKEN_8}" && "${path}" == "${OWNER_LOCK_PATH_8}" ]]; then
    slot=8
    inode="${OWNER_LOCK_INODE_8}"
  elif [[ -n "${token}" && "${token}" == "${OWNER_LOCK_TOKEN_9}" && "${path}" == "${OWNER_LOCK_PATH_9}" ]]; then
    slot=9
    inode="${OWNER_LOCK_INODE_9}"
  else
    echo "owner-lock: reservation identity does not match ${path}" >&2
    return 1
  fi
  # macOS /dev/fd reports a proxy device, so -ef is not portable here. The
  # retained descriptor prevents reuse of this inode in the preparation filesystem.
  if ! owner_lock_inode "${path}"; then
    owner_lock_close "${slot}"
    return 1
  fi
  if [[ "${OWNER_LOCK_CAPTURED_INODE}" != "${inode}" ]]; then
    echo "owner-lock: reservation was replaced or removed: ${path}" >&2
    owner_lock_close "${slot}"
    return 1
  fi
  error="$(rm -- "${path}" 2>&1)" || result=$?
  if ((result != 0)); then
    echo "owner-lock: cannot release ${path}: ${error}" >&2
  fi
  owner_lock_close "${slot}"
  return "${result}"
}
