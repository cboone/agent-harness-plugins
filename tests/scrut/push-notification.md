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

## A default config path that exists but cannot be the file is an error

Only a default path that does not exist yet may be skipped. A directory in its
place, a broken symlink, or a file where a directory should be would otherwise
send to ntfy.sh without the server and token meant for it.

```scrut
$ mkdir -p "${work}/as-dir/push-notification/config"
> pn XDG_CONFIG_HOME="${work}/as-dir" NTFY_TOPIC=env-topic check 2>&1 | sed "s|${work}|WORK|g"
push-notification: WORK/as-dir/push-notification/config exists but is not a readable regular file; replace it with the config file or remove it
[3]
```

```scrut
$ mkdir -p "${work}/as-link/push-notification"
> ln -s "${work}/no-such-file" "${work}/as-link/push-notification/config"
> pn XDG_CONFIG_HOME="${work}/as-link" NTFY_TOPIC=env-topic check 2>&1 | sed "s|${work}|WORK|g"
push-notification: WORK/as-link/push-notification/config exists but is not a readable regular file; replace it with the config file or remove it
[3]
```

```scrut
$ ln -s "${work}/no-such-dir" "${work}/as-broken-link"
> pn XDG_CONFIG_HOME="${work}/as-broken-link" NTFY_TOPIC=env-topic check 2>&1 | sed "s|${work}|WORK|g"
push-notification: cannot look for WORK/as-broken-link/push-notification/config: WORK/as-broken-link is not a searchable directory
[3]
```

```scrut
$ : > "${work}/as-file"
> pn XDG_CONFIG_HOME="${work}/as-file" NTFY_TOPIC=env-topic check 2>&1 | sed "s|${work}|WORK|g"
push-notification: cannot look for WORK/as-file/push-notification/config: WORK/as-file is not a searchable directory
[3]
```

A default path under a relative `XDG_CONFIG_HOME` that does not exist is
looked up from the current directory, and the lookup ends.

```scrut
$ (cd "${work}" && pn XDG_CONFIG_HOME=no-such-relative-dir NTFY_TOPIC=env-topic check | grep "^config file")
config file: no-such-relative-dir/push-notification/config (not found)
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
$ pn STUB_CURL_LOG="${work}/curl.log" STUB_CURL_TOKEN=tk_sample send --title Done --message "Build finished" --tag ci
Sent through ntfy to https://ntfy.sh (message stub123)
```

```scrut
$ sed "s|${work}|WORK|g" "${work}/curl.log"
arg: -sS
arg: --fail-with-body
arg: --connect-timeout
arg: 10
arg: --max-time
arg: 30
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
$ : > "${work}/empty-config"
> pn NTFY_TOPIC=open-topic PUSH_NOTIFICATION_CONFIG="${work}/empty-config" STUB_CURL_LOG="${work}/no-token.log" send --title Done
Sent through ntfy to https://ntfy.sh (message stub123)
```

```scrut
$ grep -c -e authorization -e "^header" "${work}/no-token.log"
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

When the topic occurs inside the token, or the token inside the topic, the
longer value is replaced first, so no part of either is left behind.

```scrut
$ pn NTFY_TOPIC=tk_sample NTFY_TOKEN=tk_sample_private STUB_CURL_FAIL=1 STUB_CURL_FAIL_BODY='Bearer tk_sample_private for tk_sample' send --title Done 2>&1 | head -n 1
push-notification: ntfy did not confirm the notification: Bearer (token hidden) for (topic hidden)
[1]
```

```scrut
$ pn NTFY_TOPIC=agent-tk_x-feed NTFY_TOKEN=tk_x STUB_CURL_FAIL=1 STUB_CURL_FAIL_BODY='topic agent-tk_x-feed, Bearer tk_x' send --title Done 2>&1 | head -n 1
push-notification: ntfy did not confirm the notification: topic (topic hidden), Bearer (token hidden)
[1]
```

```scrut
$ find "${work}/tmp" -mindepth 1 | wc -l | tr -d ' '
0
```

## An answer without an ntfy message id is not a confirmed send

A proxy or a misconfigured `NTFY_SERVER` can answer with HTTP success and a
page of its own. The answer itself is not printed, because a real ntfy answer
carries the topic; failure text and server errors are printed only after the
topic and token are replaced.

```scrut
$ pn STUB_CURL_RESPONSE='<html><body>Sign in</body></html>' send --title Done 2>&1
push-notification: could not read the answer from https://ntfy.sh/ as JSON (jq exited *: jq: parse error: *), so delivery is unconfirmed. Check NTFY_SERVER and any proxy in between. (glob)
[1]
```

```scrut
$ pn STUB_CURL_RESPONSE='{"id":42}' send --title Done 2>&1
push-notification: https://ntfy.sh/ answered, but not with an ntfy confirmation for this topic, so delivery is unconfirmed. Check NTFY_SERVER and any proxy in between.
[1]
```

An answer of several JSON values is not a confirmation, even when one of them
is.

```scrut
$ pn STUB_CURL_RESPONSE='{"id":"m1","event":"message","topic":"sample-topic"} {"error":"upstream unavailable","code":50301}' send --title Done 2>&1
push-notification: https://ntfy.sh/ answered with 2 JSON values instead of one, so delivery is unconfirmed. Check NTFY_SERVER and any proxy in between.
[1]
```

An otherwise valid message event for the topic still needs a non-empty string
id.

```scrut
$ for id in '"id":7,' '"id":null,' '' '"id":"",'; do
>   pn STUB_CURL_RESPONSE="{${id}\"event\":\"message\",\"topic\":\"sample-topic\"}" send --title Done > /dev/null 2>&1; echo "exit $?"
> done
exit 1
exit 1
exit 1
exit 1
```

An error object in an answer is relayed, so the cause is not lost.

```scrut
$ pn STUB_CURL_RESPONSE='{"error":"upstream unavailable","code":50301}' send --title Done 2>&1
push-notification: https://ntfy.sh/ answered with an error, so delivery is unconfirmed: upstream unavailable (code 50301)
[1]
```

An answer only counts when it is an ntfy message event for this topic, so an
error object that carries an id of its own, or a message for another topic, is
not a confirmation.

```scrut
$ for answer in '{"id":"req-1","error":"upstream unavailable"}' '{"id":"m1","event":"message","topic":"other-topic"}' '{"id":"m1","event":"open","topic":"sample-topic"}' '{"id":"m1","event":"message","topic":"sample-topic","error":"x"}'; do
>   pn STUB_CURL_RESPONSE="${answer}" send --title Done > /dev/null 2>&1; echo "exit $?"
> done
exit 1
exit 1
exit 1
exit 1
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

## Neither the topic nor the token is ever a command-line argument

A `jq` wrapper records its arguments before running the real one, and the curl
stub records its own. A send and a dry run both leave the topic and token out
of every argument list, where other users on the machine could read them.

```scrut
$ wrap_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
> printf '#!/usr/bin/env bash\nprintf "jq-arg: %%s\\n" "$@" >> "${JQ_ARG_LOG}"\nexec "%s" "$@"\n' "$(command -v jq)" > "${wrap_dir}/jq"
> chmod +x "${wrap_dir}/jq"
> args_log="${work}/args.log"
> pn PATH="${wrap_dir}:${stub_dir}:${PATH}" JQ_ARG_LOG="${args_log}" STUB_CURL_LOG="${args_log}" STUB_CURL_TOKEN=tk_sample send --title Done > /dev/null
> pn PATH="${wrap_dir}:${stub_dir}:${PATH}" JQ_ARG_LOG="${args_log}" send --title Done --dry-run > /dev/null
> grep -c '^jq-arg:' "${args_log}" | sed 's/^[1-9][0-9]*$/jq ran/'
> grep -e '^jq-arg:' -e '^arg:' "${args_log}" | grep -c -e sample-topic -e tk_sample
jq ran
0
[1]
```

## A token file that cannot be prepared stops the send

```scrut
$ pn TMPDIR="${work}/no-such-dir" STUB_CURL_LOG="${work}/no-tmp.log" send --title Done 2>&1 | grep -v '^mktemp'
push-notification: could not create a temporary directory for the authorization header
[1]
```

```scrut
$ test -e "${work}/no-tmp.log" || echo "curl not called"
curl not called
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
