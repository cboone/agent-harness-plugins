#!/usr/bin/env bash
# Root option-like fixture operands without changing serialized scope paths.
# shellcheck source=bin/lib/git-environment.bash
source "$(dirname "${BASH_SOURCE[0]}")/../../bin/lib/git-environment.bash"

function fixture_path() {
  case "${1}" in
    -*) printf './%s' "${1}" ;;
    *) printf '%s' "${1}" ;;
  esac
}

export -f fixture_path

function require_review_shfmt() {
  command -v shfmt > /dev/null || {
    printf 'shfmt required for review operand checks\n' >&2
    return 1
  }
}

# Check constant trap and shell programs recursively without executing them.
function check_review_shell_paths() {
  local source="${1}" label="${2}" scratch script status=0
  scratch="$(mktemp -d "${TMPDIR:-/tmp}/review-path-contract.XXXXXX")" || return
  if ! shfmt --to-json -ln bash < "${source}" > "${scratch}/tree"; then
    rm -- "${scratch}/tree"
    rmdir -- "${scratch}"
    return 1
  fi
  if ! jq -f "${REPO_ROOT:?}/tests/fixtures/review-path-contract.jq" "${scratch}/tree" > "${scratch}/errors"; then
    rm -- "${scratch}/tree" "${scratch}/errors"
    rmdir -- "${scratch}"
    return 1
  fi
  jq --arg file "${label}" -r '.errors[] | "\($file):\(.line): \(.command) \(.reason)"' "${scratch}/errors" || status=1
  if ! jq -e '.errors | length == 0' "${scratch}/errors" > /dev/null; then status=1; fi
  jq -j '.scripts[] | ., "\u0000"' "${scratch}/errors" > "${scratch}/scripts" || status=1
  while IFS= read -r -d '' script; do
    printf '%s' "${script}" > "${scratch}/nested" || {
      status=1
      continue
    }
    check_review_shell_paths "${scratch}/nested" "${label} (nested)" || status=1
  done < "${scratch}/scripts"
  rm -- "${scratch}/tree" "${scratch}/scripts" "${scratch}/errors" || status=1
  if [[ -e "${scratch}/nested" ]]; then rm -- "${scratch}/nested" || status=1; fi
  rmdir -- "${scratch}" || status=1
  return "${status}"
}

function check_review_fixture_paths() {
  require_review_shfmt || return
  local file scratch status=0
  local -a files=(
    tests/fixtures/review-fixture-paths.bash
    tests/fixtures/environment-isolation
    tests/fixtures/review-submodule-fixture
    tests/scrut/build-shared-references.md
    tests/scrut/codex-aspects.md
    tests/scrut/environment-isolation.md
    tests/scrut/review-scope-submodule-consumers.md
    tests/scrut/review-scope-submodules.md
    tests/scrut/review-scope.md
  )
  if [[ $# -gt 0 ]]; then files=("$@"); fi
  scratch="$(mktemp "${TMPDIR:-/tmp}/review-path-shell.XXXXXX")" || return
  for file in "${files[@]}"; do
    case "${file}" in
      *.md)
        awk '
          BEGIN { fence = sprintf("%c%c%c", 96, 96, 96) }
          $0 ~ "^" fence "+scrut" { inside = 1; print ""; next }
          inside && $0 ~ "^" fence "+$" { inside = 0; print ""; next }
          inside && /^[$>] / { print substr($0, 3); next }
          { print "" }
        ' "${REPO_ROOT:?}/${file}" > "${scratch}" || {
          status=1
          continue
        }
        ;;
      *) cat "${REPO_ROOT:?}/${file}" > "${scratch}" || {
        status=1
        continue
      } ;;
    esac
    check_review_shell_paths "${scratch}" "${file}" || status=1
  done
  rm -- "${scratch}" || status=1
  [[ "${status}" != 0 ]] || printf 'Review fixture operands are protected.\n'
  return "${status}"
}
