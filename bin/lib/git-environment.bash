#!/usr/bin/env bash
# Reset fixture Git and budget inputs before applying intentional test settings.

function reset_fixture_git_environment() {
  local variable
  while IFS= read -r variable; do
    case "${variable}" in
      GIT_* | CODEX_REFERENCE_CONTEXT_WINDOW | CODEX_ENABLED_SKILL_PERCENT | CODEX_OTHER_SKILL_RESERVE_TOKENS)
        unset "${variable}"
        ;;
      *) ;;
    esac
  done < <(compgen -e)
  export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1
  # Finish automatic maintenance before a fixture can remove its repository.
  export GIT_CONFIG_COUNT=2
  export GIT_CONFIG_KEY_0=maintenance.autoDetach GIT_CONFIG_VALUE_0=false
  export GIT_CONFIG_KEY_1=gc.autoDetach GIT_CONFIG_VALUE_1=false
}

reset_fixture_git_environment
