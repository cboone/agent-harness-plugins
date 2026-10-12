# Push notification

Tests for the `push-notification` script that the `push-notification` plugin
bundles. It resolves its settings from a `KEY=value` config file and the
environment, builds an ntfy JSON publish request and posts it with `curl`.

Every send goes through `tests/fixtures/ntfy-curl-stub`, so no test reaches an
ntfy server. `pn` clears every setting the script reads from the environment,
points the config directory and `TMPDIR` at a fresh work directory, and then
applies the settings (`NAME=value`) given before the command. `pipefail` keeps
the exit status of `pn` when its output is piped through `sed` to shorten paths.

```scrut
$ set -o pipefail
> function pn() {
>   local -a settings=()
>   while [[ "${1:-}" == *=* ]]; do
>     settings+=("${1}")
>     shift
>   done
>   env -u PUSH_NOTIFICATION_BACKEND -u PUSH_NOTIFICATION_CONFIG -u NTFY_SERVER -u NTFY_TOPIC -u NTFY_TOKEN \
>     PATH="${stub_dir}:${PATH}" XDG_CONFIG_HOME="${work}/config" TMPDIR="${work}/tmp" \
>     ${settings[@]+"${settings[@]}"} "${PUSH_NOTIFICATION_BIN}" "$@"
> }
> function write_config() {
>   mkdir -p "${work}/config/push-notification"
>   cat > "${work}/config/push-notification/config"
>   chmod "${1:-600}" "${work}/config/push-notification/config"
> }
> stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
> cp "${NTFY_CURL_STUB_BIN}" "${stub_dir}/curl"
> chmod +x "${stub_dir}/curl"
> work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
> mkdir -p "${work}/tmp"
```

## Help

```scrut
$ pn --help | head -n 1
Usage: push-notification <command> [options]
```

## No command is a usage error

```scrut
$ pn 2>&1 | head -n 1
Usage: push-notification <command> [options]
[2]
```

## With nothing configured, check names the missing topic

The server falls back to ntfy.sh, but no topic is ever invented.

```scrut
$ pn check 2>&1 | sed "s|${work}|WORK|g"
config file: WORK/config/push-notification/config (not found)
backend: ntfy (default)
server: https://ntfy.sh (default)
topic: unset
token: unset
push-notification: NTFY_TOPIC is not set. Set it in WORK/config/push-notification/config or the environment.
ready: no
[3]
```

## Send refuses to run without a topic

```scrut
$ pn send --title Done 2>&1 | sed "s|${work}|WORK|g"
push-notification: NTFY_TOPIC is not set. Set it in WORK/config/push-notification/config or the environment.
[3]
```

## The config file supplies settings, and check hides the topic and token

```scrut
$ printf '%s\n' '# ntfy settings' '' 'NTFY_SERVER = https://ntfy.example.com/' 'NTFY_TOPIC="sample-topic"' "NTFY_TOKEN='tk_sample'" | write_config
> pn check | sed "s|${work}|WORK|g"
config file: WORK/config/push-notification/config (found)
backend: ntfy (default)
server: https://ntfy.example.com/ (config)
topic: set (config)
token: set (config)
ready: yes
```

```scrut
$ pn check | grep -c -e sample-topic -e tk_sample
0
[1]
```

## The environment overrides the config file

```scrut
$ pn NTFY_SERVER=https://ntfy.sh NTFY_TOKEN=tk_env check | grep -e server -e token
server: https://ntfy.sh (env)
token: set (env)
```

An empty environment variable is ignored, so it cannot clear a configured
value.

```scrut
$ pn NTFY_SERVER= NTFY_TOKEN= check | grep -e server -e token
server: https://ntfy.example.com/ (config)
token: set (config)
```

## A config file that holds a topic or token must be private

On ntfy.sh the topic name is all that guards a topic, so it needs the same
private file as the token.

```scrut
$ printf '%s\n' 'NTFY_TOPIC=sample-topic' 'NTFY_TOKEN=tk_sample' | write_config 644
> pn check 2>&1 | sed "s|${work}|WORK|g"
push-notification: WORK/config/push-notification/config holds NTFY_TOPIC or NTFY_TOKEN but is readable by others (mode 644); run: chmod 600 "WORK/config/push-notification/config"
[3]
```

```scrut
$ printf '%s\n' 'NTFY_TOPIC=sample-topic' | write_config 644
> pn check 2>&1 | sed "s|${work}|WORK|g"
push-notification: WORK/config/push-notification/config holds NTFY_TOPIC or NTFY_TOKEN but is readable by others (mode 644); run: chmod 600 "WORK/config/push-notification/config"
[3]
```

A file that holds neither can be readable by others.

```scrut
$ printf '%s\n' 'NTFY_SERVER=https://ntfy.example.com' | write_config 644
> pn NTFY_TOPIC=env-topic check | tail -n 1
ready: yes
```

## Unknown keys and malformed lines are rejected with their line number

```scrut
$ printf '%s\n' 'NTFY_TOPIC=sample-topic' 'NTFY_PASSWORD=x' | write_config
> pn check 2>&1 | sed "s|${work}|WORK|g"
push-notification: WORK/config/push-notification/config:2: unknown key NTFY_PASSWORD
[3]
```

```scrut
$ printf '%s\n' 'NTFY_TOPIC sample-topic' | write_config
> pn check 2>&1 | sed "s|${work}|WORK|g"
push-notification: WORK/config/push-notification/config:1: expected KEY=value
[3]
```

## The config file is read, never sourced

A command substitution in a value stays literal text, and nothing runs.

```scrut
$ printf '%s\n' 'NTFY_TOPIC=sample-topic' "NTFY_SERVER=https://ntfy.example.com/\$(touch ${work}/ran)" | write_config
> pn send --title Done --dry-run | jq -r .url | sed "s|${work}|WORK|g"
> test -e "${work}/ran" || echo "nothing ran"
https://ntfy.example.com/$(touch WORK/ran)/
nothing ran
```

## PUSH_NOTIFICATION_CONFIG names another config file

```scrut
$ printf '%s\n' 'NTFY_TOPIC=other-topic' > "${work}/other-config"
> chmod 600 "${work}/other-config"
> pn PUSH_NOTIFICATION_CONFIG="${work}/other-config" check | sed "s|${work}|WORK|g" | head -n 1
config file: WORK/other-config (found)
```

A path named this way must exist, or a send would fall back to ntfy.sh
without the server and token the file was meant to supply.

```scrut
$ pn PUSH_NOTIFICATION_CONFIG="${work}/missing-config" NTFY_TOPIC=env-topic send --title Done --dry-run 2>&1 | sed "s|${work}|WORK|g"
push-notification: PUSH_NOTIFICATION_CONFIG names WORK/missing-config, which is not a file; fix the path or unset it
[3]
```

## A dry run prints the request without the topic or token

```scrut
$ printf '%s\n' 'NTFY_TOPIC=sample-topic' 'NTFY_TOKEN=tk_sample' | write_config
> pn send --title "CI passed on #42" --message "All 12 checks green" --priority high --tag white_check_mark --tag ci --click https://github.com/octocat/hello-world/pull/42 --dry-run | jq .
{
  "backend": "ntfy",
  "url": "https://ntfy.sh/",
  "authorization": "bearer token (hidden)",
  "payload": {
    "topic": "(hidden)",
    "title": "CI passed on #42",
    "message": "All 12 checks green",
    "priority": 4,
    "tags": [
      "white_check_mark",
      "ci"
    ],
    "click": "https://github.com/octocat/hello-world/pull/42"
  }
}
```

## Empty fields are left out, and priority defaults to 3

```scrut
$ pn NTFY_TOPIC=sample-topic send --title Done --dry-run | jq -c '{authorization, payload}'
{"authorization":"bearer token (hidden)","payload":{"topic":"(hidden)","title":"Done","priority":3}}
```

## Priority names and numbers both map to ntfy's 1 to 5

```scrut
$ for level in min low default high urgent 1 5; do pn send --title Done --priority "${level}" --dry-run | jq -r .payload.priority; done | paste -sd ' ' -
1 2 3 4 5 1 5
```

```scrut
$ pn send --title Done --priority loud 2>&1
push-notification: --priority must be min, low, default, high, urgent or 1 to 5, not loud
[2]
```

## The message can come from stdin

```scrut
$ printf 'Line one\nLine two\n' | pn send --title Done --message - --dry-run | jq -c .payload.message
"Line one\nLine two"
```

## Non-ASCII titles and tags pass through intact

```scrut
$ pn send --title "Revisão concluída ✅" --tag "🎉" --dry-run | jq -c '.payload | {title, tags}'
{"title":"Revisão concluída ✅","tags":["🎉"]}
```

## Send validates its options before reading settings

```scrut
$ pn send --dry-run 2>&1
push-notification: send needs --title, --message or both
[2]
```

```scrut
$ pn send --title Done --click example.com 2>&1
push-notification: --click must be a URL with a scheme, such as https://
[2]
```

```scrut
$ pn send --title 2>&1
push-notification: --title needs a value
[2]
```

```scrut
$ pn send --title Done --tag "" 2>&1
push-notification: --tag needs a non-empty value
[2]
```

```scrut
$ pn send --title Done --sound bell 2>&1
push-notification: unknown send option --sound
[2]
```

## Settings are validated before sending

```scrut
$ pn NTFY_TOPIC="has spaces" send --title Done 2>&1
push-notification: NTFY_TOPIC must be 1 to 64 letters, digits, underscores or hyphens
[3]
```

```scrut
$ pn NTFY_SERVER=ntfy.sh send --title Done 2>&1
push-notification: NTFY_SERVER must start with http:// or https://
[3]
```

```scrut
$ pn PUSH_NOTIFICATION_BACKEND=pushover send --title Done 2>&1
push-notification: unknown backend pushover (known: ntfy)
[2]
```

## A send passes the token in a private header file, never as an argument

The stub logs every curl argument, the body read from stdin, and whether the
header file it was given holds the expected header and its mode.

```scrut
$ log="${work}/curl.log"
> pn STUB_CURL_LOG="${log}" STUB_CURL_TOKEN=tk_sample send --title Done --message "Build finished" --tag ci
> sed "s|${work}|WORK|g" "${log}"
Sent through ntfy to https://ntfy.sh (message stub123)
arg: -sS
arg: --fail-with-body
arg: -X
arg: POST
arg: -H
arg: Content-Type: application/json
arg: -H
arg: @WORK/tmp/push-notification.*/authorization (glob)
arg: --data-binary
arg: @-
arg: https://ntfy.sh/
body: {"topic":"sample-topic","title":"Done","message":"Build finished","priority":3,"tags":["ci"]}
header matches: true, mode 600
```

The temporary directory that held the header file is removed afterwards.

```scrut
$ find "${work}/tmp" -mindepth 1 | wc -l | tr -d ' '
0
```

## Without a token there is no authorization header

```scrut
$ log="${work}/no-token.log"
> : > "${work}/empty-config"
> pn NTFY_TOPIC=open-topic PUSH_NOTIFICATION_CONFIG="${work}/empty-config" STUB_CURL_LOG="${log}" send --title Done > /dev/null
> grep -c -e authorization -e "^header" "${log}"
0
[1]
```

## A rejected send exits 1, relays the server's answer, and removes the token file

```scrut
$ pn STUB_CURL_FAIL=1 send --title Done 2>&1
push-notification: ntfy did not confirm the notification: {"code":40101,"http":401,"error":"unauthorized"}
curl: (22) The requested URL returned error: 401
[1]
```

```scrut
$ find "${work}/tmp" -mindepth 1 | wc -l | tr -d ' '
0
```

A failure body that echoes the topic or token back has both replaced before
it is relayed.

```scrut
$ pn STUB_CURL_FAIL=1 STUB_CURL_FAIL_BODY='{"error":"rejected","topic":"sample-topic","auth":"Bearer tk_sample"}' send --title Done 2>&1
push-notification: ntfy did not confirm the notification: {"error":"rejected","topic":"(topic hidden)","auth":"Bearer (token hidden)"}
curl: (22) The requested URL returned error: 401
[1]
```

```scrut
$ find "${work}/tmp" -mindepth 1 | wc -l | tr -d ' '
0
```

## An answer without an ntfy message id is not a confirmed send

A proxy or a misconfigured `NTFY_SERVER` can answer with HTTP success and a
page of its own. The answer is never printed, because a real ntfy answer
carries the topic.

```scrut
$ pn STUB_CURL_RESPONSE='<html><body>Sign in</body></html>' send --title Done 2>&1
push-notification: https://ntfy.sh/ answered with something other than JSON, so delivery is unconfirmed. Check NTFY_SERVER and any proxy in between.
[1]
```

```scrut
$ pn STUB_CURL_RESPONSE='{"id":42}' send --title Done 2>&1
push-notification: https://ntfy.sh/ answered without an ntfy message id, so delivery is unconfirmed. Check NTFY_SERVER and any proxy in between.
[1]
```

A real answer names the topic, and the confirmation leaves it out.

```scrut
$ pn send --title Done | grep -c sample-topic
0
[1]
```

## The environment's server, topic and token are the ones sent

```scrut
$ log="${work}/env-send.log"
> pn NTFY_SERVER=https://ntfy.env.example NTFY_TOPIC=env-topic NTFY_TOKEN=tk_env STUB_CURL_TOKEN=tk_env STUB_CURL_LOG="${log}" send --title Done > /dev/null
> grep -e '^arg: https' -e '^body' -e '^header' "${log}"
arg: https://ntfy.env.example/
body: {"topic":"env-topic","title":"Done","priority":3}
header matches: true, mode 600
```

## A dry run never calls curl

```scrut
$ log="${work}/dry-run.log"
> pn STUB_CURL_LOG="${log}" send --title Done --dry-run > /dev/null
> test -e "${log}" || echo "curl not called"
curl not called
```

## A request that cannot be built is not sent

A `jq` that fails stands in for any failure while the request is prepared.
The send stops with exit 1, a dry run does not report success, and curl is
never called.

```scrut
$ jq_fail_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
> printf '#!/usr/bin/env bash\nexit 1\n' > "${jq_fail_dir}/jq"
> chmod +x "${jq_fail_dir}/jq"
> log="${work}/broken-jq.log"
> pn PATH="${jq_fail_dir}:${stub_dir}:${PATH}" STUB_CURL_LOG="${log}" send --title Done 2>&1
push-notification: could not build the ntfy request
[1]
```

```scrut
$ pn PATH="${jq_fail_dir}:${stub_dir}:${PATH}" send --title Done --dry-run 2>&1
push-notification: could not build the ntfy request
[1]
```

```scrut
$ test -e "${work}/broken-jq.log" || echo "curl not called"
curl not called
```
