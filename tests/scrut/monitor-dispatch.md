# Monitor restriction dispatch

These cases call the shipped, side-effect-free `merge-flow dispatch` command. No GitHub or model calls occur. The same command handles initial snapshots and resumed watches.

## Pending observations retry without a running check and stop at two ticks

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
$ state="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"observations":[{"name":"mergeability","pending":true,"diagnostic":"mergeability UNKNOWN"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare)" && first="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch)" && printf '%s\n' "${first}" | jq -c '{action:.route.action, retry:.route.retry, terminal, observationFailures}' && counts="$(printf '%s\n' "${first}" | jq -c .observationFailures)" && printf '%s\n' "${state}" | jq --argjson counts "${counts}" '.observationFailures=$counts' | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, wait, terminal, status, diagnostics}'
{"action":"read-axis","retry":true,"terminal":false,"observationFailures":{"audit":0,"mergeability":1,"review-body":0,"review-id":0,"review-metadata":0,"snapshot":0,"threads":0,"triage":0}}
{"route":null,"wait":false,"terminal":true,"status":"unavailable","diagnostics":["mergeability: mergeability UNKNOWN (two-tick observation bound)"]}
```

## An audit failure followed by success clears its shared counter

```scrut
$ state="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"observations":[{"name":"audit","pending":true,"diagnostic":"HTTP 502"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare)" && first="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch)" && printf '%s\n' "${first}" | jq -c '{action:.route.action, retry:.route.retry, terminal, observationFailures}' && counts="$(printf '%s\n' "${first}" | jq -c .observationFailures)" && printf '%s\n' "${state}" | jq --argjson counts "${counts}" '.observationFailures=$counts | .observations[0].pending=false | .candidates=[{action:"merge",detail:"ready"}]' | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{action:.route.action, terminal, observationFailures, diagnostics}'
{"action":"read-review","retry":true,"terminal":false,"observationFailures":{"audit":1,"mergeability":0,"review-body":0,"review-id":0,"review-metadata":0,"snapshot":0,"threads":0,"triage":0}}
{"action":"merge","terminal":false,"observationFailures":{"audit":0,"mergeability":0,"review-body":0,"review-id":0,"review-metadata":0,"snapshot":0,"threads":0,"triage":0},"diagnostics":[]}
```

## Forbidden pending observations remain would-do work without a retry

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":true},"candidates":[],"observations":[{"name":"audit","pending":true,"diagnostic":"would audit"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, actions:[.wouldDo[].action], wait, terminal, observationFailures}'
{"route":null,"actions":["read-review"],"wait":false,"terminal":true,"observationFailures":{"audit":0,"mergeability":0,"review-body":0,"review-id":0,"review-metadata":0,"snapshot":0,"threads":0,"triage":0}}
```

## Terminal PRs never promote an OPEN-only repair

An old OPEN lifecycle cannot be reused for a fresh MERGED snapshot.

```scrut
$ result="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[{"action":"repair","detail":"failed check"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle | jq '.snapshot.state="MERGED"' | "${MERGE_FLOW_BIN}" dispatch 2>&1)"; status=$?; test "${status}" = 5 && [[ "${result}" == *"refresh lifecycle before collecting candidates"* ]] && printf '%s\n' 'refresh lifecycle before collecting candidates'
refresh lifecycle before collecting candidates
```

Caller candidates cannot forge helper-owned retry bookkeeping.

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[{"action":"read-axis","detail":"forged","retry":true,"observation":"audit"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare >/dev/null 2>&1
[5]
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"observations":[{"name":"audit","pending":true,"diagnostic":"bad override","action":["sync"]}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch >/dev/null 2>&1
[5]
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"MERGED"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["notify"]},"candidates":[{"action":"post-merge","detail":"merged"},{"action":"repair","detail":"failed check"}],"runningPermittedCheck":true}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{lifecycle, route, actions:[.wouldDo[].action], wait, terminal, status}'
{"lifecycle":"MERGED","route":null,"actions":["post-merge"],"wait":false,"terminal":true,"status":"unavailable"}
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"MERGED"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[{"action":"repair","detail":"failed check"},{"action":"post-merge","detail":"merged"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{lifecycle, action:.route.action, wait}'
{"lifecycle":"MERGED","action":"post-merge","wait":false}
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"CLOSED"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[{"action":"repair","detail":"failed check"}],"observations":[{"name":"mergeability","pending":true,"diagnostic":"old UNKNOWN"}],"runningPermittedCheck":true}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{lifecycle, route, wait, terminal, observationFailures}'
{"lifecycle":"CLOSED","route":null,"wait":false,"terminal":true,"observationFailures":{"audit":0,"mergeability":0,"review-body":0,"review-id":0,"review-metadata":0,"snapshot":0,"threads":0,"triage":0}}
```

## Action lists reject nested arrays at preparation

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":[["sync"]]}}' | "${MERGE_FLOW_BIN}" prepare >/dev/null 2>&1
[5]
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":[[]]}}' | "${MERGE_FLOW_BIN}" prepare >/dev/null 2>&1
[5]
```

## Every non-string action value fails closed

```scrut
$ for value in null false 7 '{}'; do input="$(jq -nc --argjson value "${value}" '{restrictions:{noFix:false,copilotPaused:false,blockedActions:[$value]}}')"; result="$(printf '%s\n' "${input}" | "${MERGE_FLOW_BIN}" prepare 2>&1)"; status=$?; test "${status}" = 5 && test -n "${result}" || exit 1; printf '%s rejected\n' "${value}"; done
null rejected
false rejected
7 rejected
{} rejected
```

## Unknown string names fail instead of becoming permissions

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["unknown-action"]}}' | "${MERGE_FLOW_BIN}" prepare >/dev/null 2>&1
[5]
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false}}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" gate unknown-action >/dev/null 2>&1
[5]
```

## Candidate actions are strings both initially and after preparation

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[{"action":["sync"],"detail":"nested"}]}' | "${MERGE_FLOW_BIN}" prepare >/dev/null 2>&1
[5]
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false}}' | "${MERGE_FLOW_BIN}" prepare | jq '.candidates=[{action:["sync"],detail:"nested"}] | .runningPermittedCheck=false' | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch >/dev/null 2>&1
[5]
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false}}' | "${MERGE_FLOW_BIN}" prepare | jq '.candidates=[{action:[],detail:"nested"}] | .runningPermittedCheck=false' | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch >/dev/null 2>&1
[5]
```

```scrut
$ for value in null false 7 '{}' '"unknown-action"'; do input="$(jq -nc --argjson value "${value}" '{restrictions:{noFix:false,copilotPaused:false},candidates:[{action:$value,detail:"invalid"}] }')"; result="$(printf '%s\n' "${input}" | "${MERGE_FLOW_BIN}" prepare 2>&1)"; status=$?; test "${status}" = 5 && test -n "${result}" || exit 1; printf '%s rejected\n' "${value}"; done
null rejected
false rejected
7 rejected
{} rejected
"unknown-action" rejected
```

## Prepared policy lists preserve the same element contract

```scrut
$ for field in allowedActions blockedActions pausedActions; do result="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false}}' | "${MERGE_FLOW_BIN}" prepare | jq --arg field "${field}" '.policy[$field] = [["sync"]]' | "${MERGE_FLOW_BIN}" gate sync 2>&1)"; status=$?; test "${status}" = 5 && test -n "${result}" || exit 1; printf '%s rejected\n' "${field}"; done
allowedActions rejected
blockedActions rejected
pausedActions rejected
```

## Known string sets still block and permit the intended actions

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["sync","repair"]}}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" gate sync | jq -c .
{"action":"sync","allowed":false,"status":"unavailable"}
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["sync","repair"]}}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" gate read-axis | jq -c .
{"action":"read-axis","allowed":true,"status":"permitted"}
```

## Review access restrictions propagate independently of mode flags

```scrut
$ policy="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["read-review"]}}' | "${MERGE_FLOW_BIN}" prepare)" && for action in triage-review classify-review process-review; do printf '%s\n' "${policy}" | "${MERGE_FLOW_BIN}" gate "${action}" | jq -c . || exit 1; done
{"action":"triage-review","allowed":false,"status":"unavailable"}
{"action":"classify-review","allowed":false,"status":"unavailable"}
{"action":"process-review","allowed":false,"status":"unavailable"}
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["read-review"]},"candidates":[{"action":"triage-review","detail":"count"},{"action":"classify-review","detail":"classify"},{"action":"process-review","detail":"fix"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, actions:[.wouldDo[].action], wait, terminal, status}'
{"route":null,"actions":["triage-review","classify-review","process-review"],"wait":false,"terminal":true,"status":"unavailable"}
```

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/blocked-review-dependency.XXXXXX")" && mkdir "${work}/bin" && cp "${GH_STUB_BIN}" "${work}/bin/gh" && chmod +x "${work}/bin/gh" && test "$(PATH="${work}/bin:${PATH}" command -v gh)" = "${work}/bin/gh" && printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["read-review"]}}' | "${MERGE_FLOW_BIN}" prepare > "${work}/state.json" && result="$(PATH="${work}/bin:${PATH}" STUB_GH_LOG="${work}/gh.log" "${RESOLVE_COPILOT_THREADS_BIN}" --watch-state "${work}/state.json" reply THREAD < /dev/null 2>&1)"; status=$?; test "${status}" = 1 && test "${result}" = 'Error: watch policy blocks process-review (unavailable)' && test ! -e "${work}/gh.log" && printf '%s\n' 'reply blocked before auth'
reply blocked before auth
```

## Triage is paused before reading or counting, initially and on resume

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":true},"triageAfter":5}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" triage | jq -c .
{"status":"paused","count":null,"needsRead":false}
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":true},"policy":{"stale":"discard"},"phase":"resume","previousTriageAfter":"never","triageAfter":5,"earlierReviewCount":null}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" triage | jq -c .
{"status":"paused","count":null,"needsRead":false}
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"triageAfter":5,"earlierReviewCount":null}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" triage | jq -c .
{"status":"needed","count":null,"needsRead":true}
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":true},"triageAfter":5,"earlierReviewCount":3}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" triage | jq -c .
{"status":"paused","count":3,"needsRead":false}
```

## Supplied optional restrictions are validated before defaulting

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":false}}' | "${MERGE_FLOW_BIN}" prepare >/dev/null 2>&1
[5]
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":null}}' | "${MERGE_FLOW_BIN}" prepare >/dev/null 2>&1
[5]
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":"sync"}}' | "${MERGE_FLOW_BIN}" prepare >/dev/null 2>&1
[5]
```

## Feedback commands enforce the same state before auth or reads

Read access does not imply classification permission.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/blocked-classification.XXXXXX")" && mkdir "${work}/bin" && cp "${GH_STUB_BIN}" "${work}/bin/gh" && chmod +x "${work}/bin/gh" && test "$(PATH="${work}/bin:${PATH}" command -v gh)" = "${work}/bin/gh" && printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["classify-review"]}}' | "${MERGE_FLOW_BIN}" prepare > "${work}/state.json" && for command in fetch-reviews parse-audit; do result="$(PATH="${work}/bin:${PATH}" STUB_GH_LOG="${work}/gh.log" "${RESOLVE_COPILOT_THREADS_BIN}" --watch-state "${work}/state.json" "${command}" fixture sample 1 < /dev/null 2>&1)"; status=$?; test "${status}" = 1 && test "${result}" = 'Error: watch policy blocks classify-review (unavailable)' && test ! -e "${work}/gh.log" || exit 1; printf '%s blocked before processing\n' "${command}"; done
fetch-reviews blocked before processing
parse-audit blocked before processing
```

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/paused-triage.XXXXXX")" && mkdir "${work}/bin" && cp "${GH_STUB_BIN}" "${work}/bin/gh" && chmod +x "${work}/bin/gh" && test "$(PATH="${work}/bin:${PATH}" command -v gh)" = "${work}/bin/gh" && printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":true},"triageAfter":5}' | "${MERGE_FLOW_BIN}" prepare > "${work}/state.json" && for command in fetch fetch-reviews audit parse-reviews parse-audit; do result="$(PATH="${work}/bin:${PATH}" STUB_GH_LOG="${work}/gh.log" "${RESOLVE_COPILOT_THREADS_BIN}" --watch-state "${work}/state.json" "${command}" fixture sample 1 < /dev/null 2>&1)"; status=$?; test "${status}" = 1 && test "${result}" = 'Error: watch policy blocks read-review (paused)' && test ! -e "${work}/gh.log" || exit 1; printf '%s blocked before auth\n' "${command}"; done
fetch blocked before auth
fetch-reviews blocked before auth
audit blocked before auth
parse-reviews blocked before auth
parse-audit blocked before auth
```

## Unprepared and altered policies cannot route work

Blocked writes cannot perform authentication or read reply input first.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/blocked-feedback.XXXXXX")" && mkdir "${work}/bin" && cp "${GH_STUB_BIN}" "${work}/bin/gh" && chmod +x "${work}/bin/gh" && test "$(PATH="${work}/bin:${PATH}" command -v gh)" = "${work}/bin/gh" && printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":true,"copilotPaused":false}}' | "${MERGE_FLOW_BIN}" prepare > "${work}/state.json" && for command in reply resolve reply-and-resolve; do result="$(PATH="${work}/bin:${PATH}" STUB_GH_LOG="${work}/gh.log" "${RESOLVE_COPILOT_THREADS_BIN}" --watch-state "${work}/state.json" "${command}" THREAD < /dev/null 2>&1)"; status=$?; test "${status}" = 1 && test "${result}" = 'Error: watch policy blocks process-review (unavailable)' && test ! -e "${work}/gh.log" || exit 1; printf '%s blocked before auth\n' "${command}"; done
reply blocked before auth
resolve blocked before auth
reply-and-resolve blocked before auth
```

## A blocked metadata axis cannot justify a running-check wait

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/blocked-merge.XXXXXX")" && mkdir "${work}/bin" && cp "${GH_STUB_BIN}" "${work}/bin/gh" && cp "${GIT_WORKTREE_STUB_BIN}" "${work}/bin/git" && chmod +x "${work}/bin/gh" "${work}/bin/git" && test "$(PATH="${work}/bin:${PATH}" command -v gh)" = "${work}/bin/gh" && test "$(PATH="${work}/bin:${PATH}" command -v git)" = "${work}/bin/git" && printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":true,"copilotPaused":false}}' | "${MERGE_FLOW_BIN}" prepare > "${work}/state.json" && for command in policy watch sync panes; do case "${command}" in policy|watch) action=merge ;; sync) action=sync ;; panes) action=post-merge ;; esac; result="$(PATH="${work}/bin:${PATH}" STUB_GH_LOG="${work}/gh.log" "${MERGE_FLOW_BIN}" --watch-state "${work}/state.json" "${command}" < /dev/null 2>&1)"; status=$?; test "${status}" = 1 && test "${result}" = "merge-flow: watch policy blocks ${action} (unavailable)" && test ! -e "${work}/gh.log" || exit 1; printf '%s blocked before work\n' "${command}"; done
policy blocked before work
watch blocked before work
sync blocked before work
panes blocked before work
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["read-axis"]},"candidates":[],"runningPermittedCheck":true}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, wait, terminal, status}'
{"route":null,"wait":false,"terminal":true,"status":"unavailable"}
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch >/dev/null 2>&1
[5]
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":true},"candidates":[],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare | jq '.policy.allowedActions += ["read-review"]' | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch >/dev/null 2>&1
[5]
```

## A failed check under no-fix is reported without routing or waiting

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":true,"copilotPaused":false},"candidates":[{"action":"repair","detail":"failed check"},{"action":"request-review","detail":"missing review"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, wouldDo, wait, terminal, status}'
{"route":null,"wouldDo":[{"action":"repair","detail":"failed check"},{"action":"request-review","detail":"missing review"}],"wait":false,"terminal":true,"status":"unavailable"}
```

## DIRTY and BEHIND under no-fix cannot retain the watch

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":true,"copilotPaused":false},"candidates":[{"action":"sync","detail":"DIRTY"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, wouldDo, wait, terminal, status}'
{"route":null,"wouldDo":[{"action":"sync","detail":"DIRTY"}],"wait":false,"terminal":true,"status":"unavailable"}
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":true,"copilotPaused":false},"candidates":[{"action":"sync","detail":"BEHIND"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, wouldDo, wait, terminal, status}'
{"route":null,"wouldDo":[{"action":"sync","detail":"BEHIND"}],"wait":false,"terminal":true,"status":"unavailable"}
```

## A pause blocks review processing, waiting and merge work

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":true},"candidates":[{"action":"classify-review","detail":"new review"},{"action":"process-review","detail":"feedback"},{"action":"wait-review","detail":"review pending"},{"action":"merge","detail":"ready"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, actions: [.wouldDo[].action], wait, terminal, status}'
{"route":null,"actions":["classify-review","process-review","wait-review","merge"],"wait":false,"terminal":true,"status":"unavailable"}
```

## All restrictions apply before selecting a later permitted action

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":true,"copilotPaused":false},"candidates":[{"action":"repair","detail":"failure"},{"action":"classify-review","detail":"observation"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, actions: [.wouldDo[].action], wait, terminal}'
{"route":{"action":"classify-review","detail":"observation"},"actions":["repair"],"wait":false,"terminal":false}
```

## A running permitted check is the only remaining wait reason

The pause does not block an otherwise permitted check repair.

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":true},"candidates":[{"action":"process-review","detail":"feedback"},{"action":"repair","detail":"failure"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, wait, terminal}'
{"route":{"action":"repair","detail":"failure"},"wait":false,"terminal":false}
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":true,"copilotPaused":true},"candidates":[{"action":"sync","detail":"BEHIND"},{"action":"repair","detail":"failure"},{"action":"request-review","detail":"missing"}],"runningPermittedCheck":true}' | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, wait, terminal, status}'
{"route":null,"wait":true,"terminal":false,"status":null}
```

## Initial and resumed snapshots use identical filtering

```scrut
$ snapshot='{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":true,"copilotPaused":true},"candidates":[{"action":"sync","detail":"DIRTY"},{"action":"repair","detail":"failure"}],"runningPermittedCheck":false}'; initial="$(printf '%s\n' "${snapshot}" | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch)" && resumed="$(printf '%s\n' "${snapshot}" | jq '.phase="resumed"' | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch)" && test "${initial}" = "${resumed}" && printf '%s\n' "${resumed}" | jq -c '{route, wait, terminal, status}'
{"route":null,"wait":false,"terminal":true,"status":"unavailable"}
```

## Additional host blocks are applied without silent fallback

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["sync"]},"candidates":[{"action":"sync","detail":"host read-only"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route, wait, terminal, status}'
{"route":null,"wait":false,"terminal":true,"status":"unavailable"}
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false,"unknown":true},"candidates":[],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch >/dev/null 2>&1
[5]
```

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[{"action":"unknown","detail":"unrecognized"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare 2>/dev/null | "${MERGE_FLOW_BIN}" lifecycle 2>/dev/null | "${MERGE_FLOW_BIN}" dispatch >/dev/null 2>&1
[5]
```

## audit read boundary

```scrut
$ state="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"observations":[{"name":"audit","pending":true,"diagnostic":"HTTP 502"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare)" \
>   && first="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch)" \
>   && printf '%s\n' "${first}" | jq -e --arg name 'audit' --arg action 'read-review' '.route.action==$action and .route.retry==true and .route.observation==$name and .observationFailures[$name]==1 and .terminal==false' \
>   && next="$(printf '%s\n' "${state}" | jq --argjson counts "$(printf '%s\n' "${first}" | jq -c .observationFailures)" '.observationFailures=$counts')" \
>   && printf '%s\n' "${next}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'audit' '.route==null and .wait==false and .terminal==true and .status=="unavailable" and .diagnostics==[($name+": HTTP 502 (two-tick observation bound)")]' \
>   && printf '%s\n' "${next}" | jq '.observations[0].pending=false' | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'audit' '.observationFailures[$name]==0 and .diagnostics==[]'
true
true
true
```

## mergeability read boundary

```scrut
$ state="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"observations":[{"name":"mergeability","pending":true,"diagnostic":"HTTP 502"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare)" \
>   && first="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch)" \
>   && printf '%s\n' "${first}" | jq -e --arg name 'mergeability' --arg action 'read-axis' '.route.action==$action and .route.retry==true and .route.observation==$name and .observationFailures[$name]==1 and .terminal==false' \
>   && next="$(printf '%s\n' "${state}" | jq --argjson counts "$(printf '%s\n' "${first}" | jq -c .observationFailures)" '.observationFailures=$counts')" \
>   && printf '%s\n' "${next}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'mergeability' '.route==null and .wait==false and .terminal==true and .status=="unavailable" and .diagnostics==[($name+": HTTP 502 (two-tick observation bound)")]' \
>   && printf '%s\n' "${next}" | jq '.observations[0].pending=false' | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'mergeability' '.observationFailures[$name]==0 and .diagnostics==[]'
true
true
true
```

## review-body read boundary

```scrut
$ state="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"observations":[{"name":"review-body","pending":true,"diagnostic":"HTTP 502"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare)" \
>   && first="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch)" \
>   && printf '%s\n' "${first}" | jq -e --arg name 'review-body' --arg action 'read-review' '.route.action==$action and .route.retry==true and .route.observation==$name and .observationFailures[$name]==1 and .terminal==false' \
>   && next="$(printf '%s\n' "${state}" | jq --argjson counts "$(printf '%s\n' "${first}" | jq -c .observationFailures)" '.observationFailures=$counts')" \
>   && printf '%s\n' "${next}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'review-body' '.route==null and .wait==false and .terminal==true and .status=="unavailable" and .diagnostics==[($name+": HTTP 502 (two-tick observation bound)")]' \
>   && printf '%s\n' "${next}" | jq '.observations[0].pending=false' | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'review-body' '.observationFailures[$name]==0 and .diagnostics==[]'
true
true
true
```

## review-id read boundary

```scrut
$ state="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"observations":[{"name":"review-id","pending":true,"diagnostic":"HTTP 502"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare)" \
>   && first="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch)" \
>   && printf '%s\n' "${first}" | jq -e --arg name 'review-id' --arg action 'read-review' '.route.action==$action and .route.retry==true and .route.observation==$name and .observationFailures[$name]==1 and .terminal==false' \
>   && next="$(printf '%s\n' "${state}" | jq --argjson counts "$(printf '%s\n' "${first}" | jq -c .observationFailures)" '.observationFailures=$counts')" \
>   && printf '%s\n' "${next}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'review-id' '.route==null and .wait==false and .terminal==true and .status=="unavailable" and .diagnostics==[($name+": HTTP 502 (two-tick observation bound)")]' \
>   && printf '%s\n' "${next}" | jq '.observations[0].pending=false' | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'review-id' '.observationFailures[$name]==0 and .diagnostics==[]'
true
true
true
```

## review-metadata read boundary

```scrut
$ state="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"observations":[{"name":"review-metadata","pending":true,"diagnostic":"HTTP 502"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare)" \
>   && first="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch)" \
>   && printf '%s\n' "${first}" | jq -e --arg name 'review-metadata' --arg action 'read-axis' '.route.action==$action and .route.retry==true and .route.observation==$name and .observationFailures[$name]==1 and .terminal==false' \
>   && next="$(printf '%s\n' "${state}" | jq --argjson counts "$(printf '%s\n' "${first}" | jq -c .observationFailures)" '.observationFailures=$counts')" \
>   && printf '%s\n' "${next}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'review-metadata' '.route==null and .wait==false and .terminal==true and .status=="unavailable" and .diagnostics==[($name+": HTTP 502 (two-tick observation bound)")]' \
>   && printf '%s\n' "${next}" | jq '.observations[0].pending=false' | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'review-metadata' '.observationFailures[$name]==0 and .diagnostics==[]'
true
true
true
```

## snapshot read boundary

```scrut
$ state="$(printf '%s\n' '{"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"observations":[{"name":"snapshot","pending":true,"diagnostic":"HTTP 502"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare)" \
>   && first="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" dispatch)" \
>   && printf '%s\n' "${first}" | jq -ec '{lifecycle,route,wait,terminal,status,diagnostics}'
{"lifecycle":null,"route":null,"wait":false,"terminal":true,"status":"failure","diagnostics":["snapshot: HTTP 502"]}
```

## threads read boundary

```scrut
$ state="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"observations":[{"name":"threads","pending":true,"diagnostic":"HTTP 502"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare)" \
>   && first="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch)" \
>   && printf '%s\n' "${first}" | jq -e --arg name 'threads' --arg action 'read-review' '.route.action==$action and .route.retry==true and .route.observation==$name and .observationFailures[$name]==1 and .terminal==false' \
>   && next="$(printf '%s\n' "${state}" | jq --argjson counts "$(printf '%s\n' "${first}" | jq -c .observationFailures)" '.observationFailures=$counts')" \
>   && printf '%s\n' "${next}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'threads' '.route==null and .wait==false and .terminal==true and .status=="unavailable" and .diagnostics==[($name+": HTTP 502 (two-tick observation bound)")]' \
>   && printf '%s\n' "${next}" | jq '.observations[0].pending=false' | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'threads' '.observationFailures[$name]==0 and .diagnostics==[]'
true
true
true
```

## triage read boundary

```scrut
$ state="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"observations":[{"name":"triage","pending":true,"diagnostic":"HTTP 502"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare)" \
>   && first="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch)" \
>   && printf '%s\n' "${first}" | jq -e --arg name 'triage' --arg action 'read-review' '.route.action==$action and .route.retry==true and .route.observation==$name and .observationFailures[$name]==1 and .terminal==false' \
>   && next="$(printf '%s\n' "${state}" | jq --argjson counts "$(printf '%s\n' "${first}" | jq -c .observationFailures)" '.observationFailures=$counts')" \
>   && printf '%s\n' "${next}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'triage' '.route==null and .wait==false and .terminal==true and .status=="unavailable" and .diagnostics==[($name+": HTTP 502 (two-tick observation bound)")]' \
>   && printf '%s\n' "${next}" | jq '.observations[0].pending=false' | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -e --arg name 'triage' '.observationFailures[$name]==0 and .diagnostics==[]'
true
true
true
```

## Registry iteration covers every declared kind

A new registry entry must provide an executable action and explicit retryability. The enum test derives its inputs from the shipped registry, so adding an unhandled kind fails.

```scrut
$ state='{"restrictions":{"noFix":false,"copilotPaused":false}}' \
>   && registry="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" observation-kinds)" \
>   && printf '%s\n' "${registry}" | jq -e 'length==8 and all(.[]; (.action=="read-axis" or .action=="read-review") and (.retryable|type)=="boolean" and (.diagnostic|type)=="string")' \
>   && for name in $(printf '%s\n' "${registry}" | jq -r 'keys[]'); do input="$(printf '%s\n' "${state}" | jq --arg name "${name}" '.+{snapshot:{state:"OPEN"},candidates:[],runningPermittedCheck:false,observations:[{name:$name,pending:true,diagnostic:""}]}')"; result="$(printf '%s\n' "${input}" | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch)" || exit 1; printf '%s\n' "${result}" | jq -e --arg name "${name}" --argjson kind "$(printf '%s\n' "${registry}" | jq -c --arg name "${name}" '.[$name]')" 'if $kind.retryable then .route.action==$kind.action and .route.detail==($name+": "+$kind.diagnostic) and .observationFailures[$name]==1 else .status=="failure" and .route==null and .wait==false and .lifecycle==null and .diagnostics==[($name+": "+$kind.diagnostic)] end' >/dev/null || exit 1; printf '%s covered\n' "${name}"; done
true
audit covered
mergeability covered
review-body covered
review-id covered
review-metadata covered
snapshot covered
threads covered
triage covered
```

## Invalid metadata without an explicit failed read still rejects

```scrut
$ printf '%s\n' '{"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" dispatch >/dev/null 2>&1
[5]
```

## Every compound read gate blocks retry bookkeeping

```scrut
$ raw='{"restrictions":{"noFix":false,"copilotPaused":false}}' \
>   && registry="$(printf '%s\n' "${raw}" | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" observation-kinds)" \
>   && for name in triage threads review-id review-body audit; do for gate in $(printf '%s\n' "${registry}" | jq -r --arg name "${name}" '.[$name].requires[]'); do input="$(printf '%s\n' "${raw}" | jq --arg name "${name}" --arg gate "${gate}" '.restrictions.blockedActions=[$gate] | .+{snapshot:{state:"OPEN"},candidates:[],runningPermittedCheck:false,observations:[{name:$name,pending:true,diagnostic:"blocked read"}]}')"; result="$(printf '%s\n' "${input}" | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch)" || exit 1; printf '%s\n' "${result}" | jq -e --arg name "${name}" '.route==null and .wait==false and .terminal and .observationFailures[$name]==0 and .wouldDo[0].observation==$name' >/dev/null || exit 1; printf '%s %s blocked\n' "${name}" "${gate}"; done; done
triage triage-review blocked
triage classify-review blocked
threads classify-review blocked
review-id classify-review blocked
review-body classify-review blocked
audit classify-review blocked
```

## Sync requires post-merge permission independently of sync permission

Blocking notification keeps sync itself eligible while making post-merge work unavailable. Both Git and GitHub resolve to committed logging stubs, so a rejection after either runs fails this boundary.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/blocked-sync-prerequisite.XXXXXX")" \
>   && fixture_dir="$(dirname "${COPILOT_ANCESTRY_CASE_BIN}")" \
>   && mkdir "${work}/bin" \
>   && cp "${fixture_dir}/copilot-ancestry-git-stub" "${work}/bin/git" \
>   && cp "${fixture_dir}/copilot-ancestry-gh-stub" "${work}/bin/gh" \
>   && test "$(PATH="${work}/bin:${PATH}" command -v git)" = "${work}/bin/git" \
>   && test "$(PATH="${work}/bin:${PATH}" command -v gh)" = "${work}/bin/gh" \
>   && printf '%s\n' '{"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["notify"]}}' | "${MERGE_FLOW_BIN}" prepare > "${work}/state.json" \
>   && "${MERGE_FLOW_BIN}" gate sync < "${work}/state.json" | jq -e '.allowed==true' \
>   && result="$(PATH="${work}/bin:${PATH}" "${MERGE_FLOW_BIN}" --watch-state "${work}/state.json" sync acme widgets main 1111111111111111111111111111111111111111 2>&1)"; status=$?; test "${status}" = 1 && test "${result}" = 'merge-flow: watch policy blocks post-merge (unavailable)' && test ! -e "${work}/bin/git-calls" && test ! -e "${work}/bin/gh-calls" && printf '%s\n' 'post-merge blocked before Git and GitHub work'
true
post-merge blocked before Git and GitHub work
```
