# shellcheck shell=bash
# Simulate an unavailable backend without exposing a live notification binary.
function command() {
  if [[ "${1:-}" == -v && "${2:-}" == alerter ]]; then return 1; fi
  builtin command "$@"
}
