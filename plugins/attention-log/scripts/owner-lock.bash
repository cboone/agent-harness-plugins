#!/usr/bin/env bash
# Shared owner-file reservations. Call reserve/release in checked conditions.
# Slots 8 and 9 retain open-file identity until release, independently of PID text.
# shellcheck disable=SC2034

OWNER_LOCK_TOKEN=""
OWNER_LOCK_ERROR=""
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
  listing="$(ls -diL -- "${1}" 2> /dev/null)" || return 1
  read -r OWNER_LOCK_CAPTURED_INODE _ <<< "${listing}"
  [[ "${OWNER_LOCK_CAPTURED_INODE}" =~ ^[0-9]+$ ]]
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

# Sets OWNER_LOCK_TOKEN on success and OWNER_LOCK_ERROR on failure.
function owner_lock_reserve() {
  local path="${1}" slot="${2}" diagnostic had_noclobber=false result=0
  OWNER_LOCK_ERROR=""
  OWNER_LOCK_TOKEN=""
  case "${slot}" in
    8) [[ -z "${OWNER_LOCK_TOKEN_8}" ]] || return 2 ;;
    9) [[ -z "${OWNER_LOCK_TOKEN_9}" ]] || return 2 ;;
    *)
      OWNER_LOCK_ERROR='invalid owner descriptor'
      return 2
      ;;
  esac
  [[ ! -e "${path}" && ! -L "${path}" ]] || return 1
  if ! diagnostic="$(mktemp "${path}.diagnostic.XXXXXX" 2>&1)"; then
    OWNER_LOCK_ERROR="${diagnostic}"
    return 1
  fi
  [[ ! -o noclobber ]] || had_noclobber=true
  set -o noclobber
  case "${slot}" in
    8) { exec 8> "${path}"; } 2>> "${diagnostic}" || result=$? ;;
    9) { exec 9> "${path}"; } 2>> "${diagnostic}" || result=$? ;;
    *) result=2 ;;
  esac
  [[ "${had_noclobber}" == true ]] || set +o noclobber
  OWNER_LOCK_ERROR="$(cat "${diagnostic}")" || OWNER_LOCK_ERROR='cannot read reservation diagnostic'
  if ! rm -- "${diagnostic}"; then
    echo "owner-lock: cannot remove reservation diagnostic ${diagnostic}" >&2
  fi
  ((result == 0)) || return "${result}"
  if ! owner_lock_inode "/dev/fd/${slot}"; then
    OWNER_LOCK_ERROR="cannot capture reservation identity for ${path}; manual cleanup may be required"
    echo "owner-lock: ${OWNER_LOCK_ERROR}" >&2
    owner_lock_close "${slot}"
    return 1
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

# Unlinks only the matching reservation; reports failure through OWNER_LOCK_ERROR.
# The descriptor prevents inode reuse. Reclaim's check/unlink race remains separate.
function owner_lock_release() {
  local path="${1}" token="${2}" slot inode result=0
  OWNER_LOCK_ERROR=""
  if [[ -n "${token}" && "${token}" == "${OWNER_LOCK_TOKEN_8}" && "${path}" == "${OWNER_LOCK_PATH_8}" ]]; then
    slot=8
    inode="${OWNER_LOCK_INODE_8}"
  elif [[ -n "${token}" && "${token}" == "${OWNER_LOCK_TOKEN_9}" && "${path}" == "${OWNER_LOCK_PATH_9}" ]]; then
    slot=9
    inode="${OWNER_LOCK_INODE_9}"
  else
    OWNER_LOCK_ERROR="reservation identity does not match ${path}"
    return 1
  fi
  # macOS /dev/fd reports a proxy device, so -ef is not portable here. The
  # retained descriptor prevents reuse of this inode in the preparation filesystem.
  if ! owner_lock_inode "${path}" || [[ "${OWNER_LOCK_CAPTURED_INODE}" != "${inode}" ]]; then
    OWNER_LOCK_ERROR="reservation was replaced or removed: ${path}"
    owner_lock_close "${slot}"
    return 1
  fi
  OWNER_LOCK_ERROR="$(rm -- "${path}" 2>&1)" || result=$?
  owner_lock_close "${slot}"
  return "${result}"
}
