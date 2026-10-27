# Notification hook commands

## Plugin roots containing spaces

Load both hook manifests and execute every command against a local notify stub.
The stub prints its arguments and sends no notifications.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && root="${work}/plugin with spaces" && mkdir -p "${root}/scripts" \
>   && printf '%s\n' '#!/usr/bin/env bash' 'printf "%s\n" "$@"' > "${root}/scripts/notify" \
>   && chmod +x "${root}/scripts/notify" && test -x "${root}/scripts/notify" \
>   && hooks="$(dirname "${NOTIFY_BIN}")/../hooks" \
>   && jq -r '.. | .command? // empty' "${hooks}/hooks.json" "${hooks}/codex.hooks.json" > "${work}/commands" \
>   && while IFS= read -r hook_command; do \
>        CLAUDE_PLUGIN_ROOT="${root}" bash -c "${hook_command}" || exit; \
>      done < "${work}/commands"
cc-elicit
cc-permission
cc-stop
cc-turn-start
cc-question
codex-stop
codex-turn-start
codex-question
```
