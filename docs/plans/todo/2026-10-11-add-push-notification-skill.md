# Add the push-notification skill (#602)

## Context

No skill in the catalog can send a notification that reaches a phone. `notify` is a macOS hook that shows local `alerter` banners, so it cannot be called by an agent or another skill, and its banners never reach remote or cloud sessions. Issue #602 asks for a general-purpose skill that sends pushes through ntfy, with the transport behind a small interface so other backends can be added later. Decisions made while planning: the plugin and skill are both named `push-notification`, the configuration is a `KEY=value` file, and the request is a JSON publish built with `jq`.

## Design

### Helper: `plugins/push-notification/scripts/push-notification`

This is a Bash script that follows `write-bash-scripts` and stays compatible with macOS Bash 3.2. It uses the same header, `usage`, `die` and `main` layout as `plugins/triage-dependabot-prs/scripts/dependabot-prs`.

- **Commands:**
  - `send --title T [--message M | --message -] [--priority min|low|default|high|urgent] [--tag TAG]... [--click URL] [--dry-run]`. With `--message -`, the body is read from stdin.
  - `check`, which reports the resolved backend, server, topic and the source of each value (config, env or default). For the topic and token it reports only "set" or "unset", never the value, because on a public server the topic name is the only thing that protects it.
- **Backend interface:** the script normalizes every field first, then dispatches to `backend_<name>_check` and `backend_<name>_send`, which receive the normalized fields as globals or arguments. The interface is documented in the script header: the fields, the priority vocabulary, the exit codes, and what a backend must never print. The only backend that ships is `ntfy`. The `PUSH_NOTIFICATION_BACKEND` key or environment variable selects it, defaulting to `ntfy`. An unknown backend exits with a usage error.
- **Configuration:** the file is `${XDG_CONFIG_HOME:-$HOME/.config}/push-notification/config`, and a `PUSH_NOTIFICATION_CONFIG` path overrides that location. A line-by-line parser reads it and never sources it. It accepts only allowlisted keys (`PUSH_NOTIFICATION_BACKEND`, `NTFY_SERVER`, `NTFY_TOPIC`, `NTFY_TOKEN`) and skips comments and blank lines. An environment variable of the same name overrides each key. `NTFY_SERVER` defaults to `https://ntfy.sh`. `NTFY_TOPIC` has no default: when it is missing, the script exits 3 with setup instructions and never invents a topic. If the file holds `NTFY_TOKEN` while it is readable by group or others, the script refuses to run and says to `chmod 600` it.
- **Token handling (`handle-secrets`):** the token is written to a header file inside a `mktemp -d` directory under `umask 077`, as `Authorization: Bearer …`, and passed to curl with `-H @FILE`, which follows the pattern in `plugins/publish-report-board/scripts/bugs-gather:874`. A trap removes the directory on exit. The token never appears in argv, stdout, stderr or `--dry-run` output.
- **Request:** `jq -n` builds `{topic, title, message, priority, tags, click}` and pipes it to `curl -sS --fail-with-body -X POST "$NTFY_SERVER" --data-binary @-`. Priority names map to ntfy's 1 to 5. Empty fields are omitted. `--dry-run` prints the URL and the JSON payload with the topic hidden and without the token, and sends nothing. The topic reaches `jq` through the environment, not its argument list.
- **Exit codes:** 0 when sent, 1 when the send failed (curl error or HTTP failure, with the server's message relayed on stderr), 2 for a usage error, and 3 when the backend is not configured.
- **Requirements:** `curl` and `jq`. When either is missing, the script fails with an install hint.

### Skill: `plugins/push-notification/skills/push-notification/SKILL.md`

- The frontmatter has a routing description that opens with the action, names its triggers ("notify me when this finishes", "ping my phone", "send a push notification") and points to `notify` for local macOS banners. It also has an `argument-hint`, because the skill has an `## Options` section.
- It invokes `bash "${CLAUDE_PLUGIN_ROOT}/scripts/push-notification" …`. For harnesses that do not substitute the placeholder (Codex CLI), it gives a package-relative fallback: the script is at `../../scripts/push-notification` relative to the directory holding this `SKILL.md`, which also holds in the `dist/codex` mirror.
- **Workflow:** run `check`. If the backend is not configured, report what is missing using `./references/setup.md` and stop. Otherwise compose the message, send it, and report the result. A send failure is reported and is never retried in a loop.
- **Content rules:** lead with the outcome, keep it short enough to read on a lock screen (a title of about 50 characters, a body of one or two short lines), add a click URL when a PR, run or session link exists, and choose priority by urgency: `default` for a completion, `high` when a session is blocked waiting on input, and `urgent` only when the user asked for it.
- **Privacy rule:** anyone who knows a topic name on the public server can read it. Never include secrets, tokens, client names or private repository details unless the user's configured server is self-hosted or access-controlled, and the user has said such content is acceptable. Otherwise use generic wording plus a click URL, since the link needs authentication of its own to open.
- **Called by other skills:** a short "Calling from another skill" section gives the exact command form and the `Status:` continuation result described in `docs/plugin-development.md`. No other skill is changed in this PR.
- **Reference `references/setup.md`:** covers choosing a hard-to-guess topic, the config file example, mode 600, environment overrides for cloud sessions, subscribing in the ntfy app, and access tokens on a self-hosted server.

### Registration and docs

- `plugins/push-notification/.claude-plugin/plugin.json` at version `1.0.0`. There is no `.codex-plugin`, because the plugin has no hooks.
- `plugins/push-notification/README.md`: an opening paragraph that matches the catalog description verbatim, a `**Requires:**` line for curl and jq, a configuration summary, a `## Recommended Permissions` JSON block, and a link to `../../README.md#install`.
- `.claude-plugin/marketplace.json`: a new entry with category `agents`.
- Root `README.md`: a row in the Agents table and an External tools bullet.
- `docs/plugin-development.md`: add `push-notification` to the list of skills that bundle a `scripts/` directory.
- `make build` to regenerate `dist/` and `.agents/`.

### Tests

- `tests/fixtures/ntfy-curl-stub`: records argv (to show that the token is absent), the header file's contents check and mode, and the JSON body on stdin into `STUB_CURL_LOG`. `STUB_CURL_FAIL=1` simulates an HTTP failure.
- `tests/scrut/push-notification.md`: help output; missing topic (exit 3 with setup text); config parsing (comments, unknown key rejected, env override, the file is not sourced); a token file readable by others is refused; `check` never prints the token; `--dry-run` payload shape, priority mapping and omission of empty fields; a message read from stdin; non-ASCII title and tags; a send through the stub (no token in argv, header file mode 600, the temporary directory removed afterwards); HTTP failure gives exit 1; an unknown backend gives exit 2.
- Register `PUSH_NOTIFICATION_BIN` and `NTFY_CURL_STUB_BIN` in both the Makefile `SCRUT_ENV` and the CI `scrut-env` list.

## Commits

Each is GPG-signed and references `#602`: the plan rename; `feat: add push-notification helper script and tests`; `feat: add push-notification skill, README and catalog entry`; `chore: regenerate mirrors`, if `make build` output is kept separate.

## Verification

1. `make lint`, `make validate` (check the Codex skill inventory budget line), `make build` with no diff left afterwards, then `make test-all`, observing the final result.
1. Do a manual `--dry-run` against a scratch config, and confirm with `ps` during a stubbed send that the token is absent from argv.
1. Optionally send one live push to a throwaway ntfy.sh topic, only with the user's go-ahead, since it publishes to a public server.
1. Run the `check-versions` skill before the PR.

## Out of scope

Action buttons, attachments, scheduled delivery, other backends, changes to `notify`, and wiring `monitor-pr` or `review-until-clean` to the new skill. These can be follow-up issues.
