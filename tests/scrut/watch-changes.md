# Background PR change watch

## Setup refuses a missing offline fixture

Each sequence row holds PR metadata and paginated review responses. No command
can fall through to real GitHub. The sleep fixture records the chosen cadence.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut {fail_fast: true}
$ test "$("${WATCH_CHANGES_STUB_BIN}" --stub-check)" = watch-changes-offline-stub \
>   && work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && mkdir "${work}/bin" && ln -s "${WATCH_CHANGES_STUB_BIN}" "${work}/bin/gh" \
>   && ln -s "${WATCH_CHANGES_STUB_BIN}" "${work}/bin/sleep" \
>   && export PATH="${work}/bin:${PATH}" \
>   && test "$(command -v gh)" -ef "${WATCH_CHANGES_STUB_BIN}" \
>   && export WATCH_TEST_COUNT="${work}/count" WATCH_TEST_SEQUENCE="${work}/sequence" WATCH_TEST_SLEEP_LOG="${work}/sleeps" WATCH_TEST_CALLS="${work}/calls" WATCH_TEST_READ_DELAY=0 \
>   && base='{"snapshot":{"state":"OPEN","headRefOid":"aaa","headRefName":"topic","reviewDecision":"","mergeCommit":null,"mergeable":"MERGEABLE","mergeStateStatus":"CLEAN","statusCheckRollup":[{"name":"test","status":"IN_PROGRESS","conclusion":""}]},"latestReview":null,"reviews":[[]]}' \
>   && printf '%s\n' "${base}" > "${work}/baseline" \
>   && function row() { jq -c "${1}" <<< "${base}"; } \
>   && function reset_watch() { : > "${WATCH_TEST_COUNT}"; : > "${WATCH_TEST_SLEEP_LOG}"; : > "${WATCH_TEST_CALLS}"; } \
>   && function watch() { reset_watch && MERGE_FLOW_INTERVAL=0 "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" --quiet-polls 3 "$@"; } \
>   && echo offline-ready
offline-ready
```

## Check completes

```scrut
$ row ' .snapshot.statusCheckRollup[0] |= (.status="COMPLETED" | .conclusion="SUCCESS")' > "${WATCH_TEST_SEQUENCE}" && watch | jq -r '.event'
checks
```

## Check fails

```scrut
$ row '.snapshot.statusCheckRollup[0] |= (.status="COMPLETED" | .conclusion="FAILURE")' > "${WATCH_TEST_SEQUENCE}" && watch | jq -r '.event'
checks
```

## Legacy status context completes

```scrut
$ row '.snapshot.statusCheckRollup=[{context:"legacy",state:"SUCCESS"}]' > "${WATCH_TEST_SEQUENCE}" && watch | jq -r '.event'
checks
```

## Current-head Copilot review arrives

```scrut
$ row '.reviews=[[{id:3,commit_id:"aaa",user:{login:"Copilot"}}]]' > "${WATCH_TEST_SEQUENCE}" && watch | jq -r '.event'
review
```

## Head changes

```scrut
$ row '.snapshot.headRefOid="bbb"' > "${WATCH_TEST_SEQUENCE}" && watch | jq -r '.event'
head
```

## PR merges

```scrut
$ row '.snapshot.state="MERGED" | .snapshot.mergeCommit={oid:"ccc"}' > "${WATCH_TEST_SEQUENCE}" && watch | jq -c '{event,mergeCommit}'
{"event":"merged","mergeCommit":"ccc"}
```

## PR closes

```scrut
$ row '.snapshot.state="CLOSED"' > "${WATCH_TEST_SEQUENCE}" && watch | jq -r '.event'
closed
```

## Known mergeability changes

```scrut
$ row '.snapshot.mergeable="CONFLICTING"' > "${WATCH_TEST_SEQUENCE}" && watch | jq -r '.event'
mergeability
```

## Branch falls behind

```scrut
$ row '.snapshot.mergeStateStatus="BEHIND"' > "${WATCH_TEST_SEQUENCE}" && watch | jq -r '.event'
mergeability
```

## Running, queued and transient UNKNOWN changes remain quiet

Two successful unchanged polls cause only the known-end quiet event. A stale
Copilot review and another author's review cannot wake the session.

```scrut
$ row '.snapshot.mergeable="UNKNOWN" | .snapshot.mergeStateStatus="UNKNOWN" | .snapshot.statusCheckRollup[0].status="QUEUED" | .reviews=[[{id:1,commit_id:"old",user:{login:"copilot"}},{id:2,commit_id:"aaa",user:{login:"human"}}]]' > "${WATCH_TEST_SEQUENCE}" \
>   && watch --quiet-polls 2 | jq -c '{event,quietPolls}' && cat "${WATCH_TEST_COUNT}"
{"event":"quiet","quietPolls":2}
3
```

## Failed polls reach their limit and report the diagnostic

```scrut
$ row '.snapshot="FAIL"' > "${WATCH_TEST_SEQUENCE}" \
>   && MERGE_FLOW_MAX_FAILURES=2 watch | jq -c '{event,error}' && cat "${WATCH_TEST_COUNT}"
{"event":"failed","error":"2 consecutive reads failed; last error: offline PR read failed"}
2
```

## Review failures share the same consecutive failure limit

```scrut
$ row '.reviews="FAIL"' > "${WATCH_TEST_SEQUENCE}" \
>   && MERGE_FLOW_MAX_FAILURES=2 watch | jq -c '{event,error}' && cat "${WATCH_TEST_COUNT}"
{"event":"failed","error":"2 consecutive reads failed; last error: offline review read failed"}
2
```

## Success resets failures and failed polls never count as quiet

```scrut
$ { row '.reviews="FAIL"'; row '.'; row '.reviews="FAIL"'; row '.'; } > "${WATCH_TEST_SEQUENCE}" \
>   && MERGE_FLOW_MAX_FAILURES=2 watch --quiet-polls 2 | jq -c '{event,quietPolls}' && cat "${WATCH_TEST_COUNT}"
{"event":"quiet","quietPolls":2}
4
```

## Malformed responses are failed reads

```scrut
$ row '.snapshot.statusCheckRollup=null' > "${WATCH_TEST_SEQUENCE}" \
>   && MERGE_FLOW_MAX_FAILURES=1 watch | jq -c '{event,error}'
{"event":"failed","error":"1 consecutive reads failed; last error: gh pr view returned invalid check metadata"}
```

```scrut
$ row '.reviews={unexpected:true}' > "${WATCH_TEST_SEQUENCE}" \
>   && MERGE_FLOW_MAX_FAILURES=1 watch | jq -c '{event,error}'
{"event":"failed","error":"1 consecutive reads failed; last error: gh api returned invalid review metadata"}
```

## Fixed cadence and backoff are shared with merge watch

```scrut
$ { row '.snapshot="FAIL"'; row '.snapshot="FAIL"'; row '.snapshot.state="CLOSED"'; } > "${WATCH_TEST_SEQUENCE}" \
>   && reset_watch && MERGE_FLOW_INTERVAL=2 "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" | jq -r '.event' \
>   && cat "${WATCH_TEST_SLEEP_LOG}"
closed
2
4
```

## Adaptive running cadence stays internal

```scrut
$ { row '.'; row '.snapshot.state="CLOSED"'; } > "${WATCH_TEST_SEQUENCE}" \
>   && reset_watch && env -u MERGE_FLOW_INTERVAL "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" | jq -r '.event' \
>   && cat "${WATCH_TEST_SLEEP_LOG}"
closed
120
```

## Adaptive review cadence stays internal

```scrut
$ { row '.snapshot.statusCheckRollup=[]'; row '.snapshot.state="CLOSED"'; } > "${WATCH_TEST_SEQUENCE}" \
>   && row '.snapshot.statusCheckRollup=[]' > "${work}/empty-checks" \
>   && reset_watch && env -u MERGE_FLOW_INTERVAL "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/empty-checks" | jq -r '.event' \
>   && cat "${WATCH_TEST_SLEEP_LOG}"
closed
300
```

## Adaptive idle cadence stays internal

```scrut
$ row '.snapshot.statusCheckRollup=[] | .latestReview={id:3,commit_id:"aaa"} | .reviews=[[{id:3,commit_id:"aaa",user:{login:"copilot"}}]]' > "${work}/reviewed" \
>   && { cat "${work}/reviewed"; row '.snapshot.state="CLOSED"'; } > "${WATCH_TEST_SEQUENCE}" \
>   && reset_watch && env -u MERGE_FLOW_INTERVAL "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/reviewed" | jq -r '.event' \
>   && cat "${WATCH_TEST_SLEEP_LOG}"
closed
1200
```

## Failure backoff never exceeds fifteen minutes

```scrut
$ { row '.snapshot="FAIL"'; row '.snapshot.state="CLOSED"'; } > "${WATCH_TEST_SEQUENCE}" \
>   && reset_watch && MERGE_FLOW_INTERVAL=1000 "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" | jq -r '.event' \
>   && cat "${WATCH_TEST_SLEEP_LOG}"
closed
900
```

## Once honors the original lifetime without a read

```scrut
$ reset_watch && MERGE_FLOW_LIFETIME=1 watch --once --started 1 | jq -r '.event' \
>   && test ! -s "${WATCH_TEST_CALLS}" && echo no-read
expired
no-read
```

## Blocking watch clamps sleep to its remaining lifetime

Use real sleep here; the lifetime must end before a second PR read even when
the requested interval is larger than the entire lifetime.

```scrut
$ mkdir "${work}/real-sleep" && ln -s "${WATCH_CHANGES_STUB_BIN}" "${work}/real-sleep/gh" \
>   && row '.' > "${WATCH_TEST_SEQUENCE}" && reset_watch \
>   && PATH="${work}/real-sleep:/usr/bin:/bin" MERGE_FLOW_INTERVAL=10 MERGE_FLOW_LIFETIME=1 "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" | jq -r '.event' \
>   && cat "${WATCH_TEST_COUNT}"
expired
1
```

## Policy pause allows metadata observation without merge permission

```scrut
$ printf '%s\n' '{"restrictions":{"noFix":false,"copilotPaused":true}}' | "${MERGE_FLOW_BIN}" prepare > "${work}/policy" \
>   && row '.snapshot.state="CLOSED"' > "${WATCH_TEST_SEQUENCE}" && reset_watch \
>   && "${MERGE_FLOW_BIN}" --watch-state "${work}/policy" watch-changes acme widgets 7 aaa "${work}/baseline" --once | jq -r '.event'
closed
```

## Invalid baseline refuses before calling GitHub

```scrut
$ printf '%s\n' '{}' > "${work}/invalid" && reset_watch \
>   && "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/invalid" 2>&1
merge-flow: invalid change-watch baseline
Run 'merge-flow --help' for usage.
[2]
```

```scrut
$ test ! -s "${WATCH_TEST_CALLS}" && echo no-read
no-read
```

## Blocked metadata permission refuses before any offline call

```scrut
$ printf '%s\n' '{"restrictions":{"noFix":false,"copilotPaused":false,"blockedActions":["read-axis"]}}' | "${MERGE_FLOW_BIN}" prepare > "${work}/blocked" \
>   && reset_watch && "${MERGE_FLOW_BIN}" --watch-state "${work}/blocked" watch-changes acme widgets 7 aaa "${work}/baseline" --once 2>&1
merge-flow: watch policy blocks read-axis (unavailable)
[1]
```

```scrut
$ test ! -s "${WATCH_TEST_CALLS}" && echo no-read
no-read
```

## Whitespace baseline refuses before calling GitHub

```scrut
$ printf ' \n' > "${work}/invalid" && reset_watch \
>   && "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/invalid" 2>&1
merge-flow: cannot load change-watch baseline *invalid:*one baseline required* (glob)
Run 'merge-flow --help' for usage.
[2]
```

```scrut
$ test ! -s "${WATCH_TEST_CALLS}" && echo no-read
no-read
```

## Startup detects changes but spends no quiet tick

The remaining one-tick decision must wait once before returning quiet.

```scrut
$ row '.' > "${WATCH_TEST_SEQUENCE}" && watch --quiet-polls 2 --quiet-count 1 | jq -c '{event,quietPolls}' \
>   && cat "${WATCH_TEST_COUNT}" && wc -l < "${WATCH_TEST_SLEEP_LOG}" | tr -d ' '
{"event":"quiet","quietPolls":2}
2
1
```

## Queued and running Copilot observations reset quiet counts silently

A quiet observation between working observations cannot accumulate toward the
threshold. After the last working observation, two elapsed quiet polls are
needed. Superseded-head runs and older reruns cannot make the head look working.

```scrut
$ { row '.runs=[{headSha:"aaa",status:"queued"}]'; row '.runs=[{headSha:"aaa",status:"in_progress"}]'; row '.runs=[{headSha:"aaa",status:"completed"}]'; row '.runs=[{headSha:"aaa",status:"queued"}]'; row '.runs=[{headSha:"old",status:"in_progress"},{headSha:"aaa",status:"completed"},{headSha:"aaa",status:"in_progress"}]'; } > "${WATCH_TEST_SEQUENCE}" \
>   && watch --review-wait --quiet-polls 2 --quiet-count 1 | jq -c '{event,quietPolls}' \
>   && cat "${WATCH_TEST_COUNT}" && wc -l < "${WATCH_TEST_SLEEP_LOG}" | tr -d ' '
{"event":"quiet","quietPolls":2}
6
5
```

## Foreground and background share the workflow-status query

```scrut
$ row '.runs=[{headSha:"aaa",status:"queued"}]' > "${WATCH_TEST_SEQUENCE}" \
>   && printf '1\n' > "${WATCH_TEST_COUNT}" \
>   && "${MERGE_FLOW_BIN}" copilot-status acme widgets topic aaa
{"status":"queued","working":true}
```

## Missing workflow is quiet; other workflow failures are failed polls

```scrut
$ row '.runs="NO_WORKFLOW"' > "${WATCH_TEST_SEQUENCE}" \
>   && watch --review-wait --quiet-polls 1 | jq -c '{event,quietPolls}' && cat "${WATCH_TEST_COUNT}"
{"event":"quiet","quietPolls":1}
2
```

```scrut
$ row '.runs="FAIL"' > "${WATCH_TEST_SEQUENCE}" \
>   && MERGE_FLOW_MAX_FAILURES=2 watch --review-wait | jq -c '{event,error}'
{"event":"failed","error":"2 consecutive reads failed; last error: offline workflow read failed"}
```

## Leading-zero bounds are rejected before reading GitHub

```scrut
$ reset_watch && "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" --quiet-polls 08 2>&1
merge-flow: quiet bounds need canonical decimal whole numbers
Run 'merge-flow --help' for usage.
[2]
```

```scrut
$ reset_watch && "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" --quiet-polls 010 2>&1
merge-flow: quiet bounds need canonical decimal whole numbers
Run 'merge-flow --help' for usage.
[2]
```

```scrut
$ test ! -s "${WATCH_TEST_CALLS}" && echo no-read
no-read
```

## Numeric sibling parameters use the same decimal contract

```scrut
$ for option in --quiet-count --failures --merged-reads --started; do \
>   reset_watch; "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" --once "${option}" 08 > "${work}/error" 2>&1; # error-output-allow: testcase asserts retained diagnostics: Numeric sibling parameters use the same decimal contract
>   test "$?" = 2 && test ! -s "${WATCH_TEST_CALLS}" && echo "${option}: refused"; done
--quiet-count: refused
--failures: refused
--merged-reads: refused
--started: refused
```

```scrut
$ for option in MERGE_FLOW_INTERVAL MERGE_FLOW_MAX_FAILURES MERGE_FLOW_LIFETIME; do \
>   reset_watch; env "${option}=08" "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" --once > "${work}/error" 2>&1; # error-output-allow: testcase asserts retained diagnostics: Numeric sibling parameters use the same decimal contract
>   test "$?" = 2 && test ! -s "${WATCH_TEST_CALLS}" && echo "${option}: refused"; done
MERGE_FLOW_INTERVAL: refused
MERGE_FLOW_MAX_FAILURES: refused
MERGE_FLOW_LIFETIME: refused
```

## Oversized numbers refuse instead of overflowing arithmetic

```scrut
$ reset_watch && "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" --quiet-polls 1000000000000000 --once 2>&1
merge-flow: quiet bounds need canonical decimal whole numbers
Run 'merge-flow --help' for usage.
[2]
```

## Backoff clamps before multiplying large accepted bounds

```scrut
$ { row '.snapshot="FAIL"'; row '.snapshot.state="CLOSED"'; } > "${WATCH_TEST_SEQUENCE}" \
>   && reset_watch && MERGE_FLOW_INTERVAL=999999999999999 MERGE_FLOW_MAX_FAILURES=999999999990001 "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" --failures 999999999989999 | jq -r '.event' \
>   && cat "${WATCH_TEST_SLEEP_LOG}"
closed
900
```

## Empty successful workflow reads are unavailable, never quiet

```scrut
$ row '.runs="EMPTY"' > "${WATCH_TEST_SEQUENCE}" \
>   && MERGE_FLOW_MAX_FAILURES=1 watch --review-wait | jq -c '{event,error}'
{"event":"failed","error":"1 consecutive reads failed; last error: gh run list returned invalid workflow metadata"}
```

## Empty successful review reads are unavailable, never no-review

```scrut
$ row '.reviews="EMPTY"' > "${WATCH_TEST_SEQUENCE}" \
>   && MERGE_FLOW_MAX_FAILURES=1 watch | jq -c '{event,error}'
{"event":"failed","error":"1 consecutive reads failed; last error: gh api returned invalid review metadata"}
```

## The documented no-review projection freezes a usable null baseline

Execute the documented metadata command against the offline fixture rather
than copying its jq expression into the test.

```scrut
$ row '.' > "${WATCH_TEST_SEQUENCE}" && printf '1\n' > "${WATCH_TEST_COUNT}" \
>   && projection="$(awk '/^gh api --paginate --slurp repos\/OWNER\/REPO\/pulls\/PR_NUMBER\/reviews/{take=1} take && /^[`][`][`]/{exit} take{print}' "${MONITOR_SKILL_FILE}" | sed 's@repos/OWNER/REPO/pulls/PR_NUMBER/reviews@repos/acme/widgets/pulls/7/reviews@')" \
>   && test -n "${projection}" && latest="$(bash -c "${projection}")" && printf '%s\n' "${latest}" \
>   && jq --argjson latest "${latest}" '.latestReview=$latest' "${work}/baseline" > "${work}/projected-baseline" \
>   && reset_watch && MERGE_FLOW_INTERVAL=0 "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/projected-baseline" --once | jq -r '.event'
null
pending
```

## Combined workflow failures reach the fallback two-tick bound

Execute the documented combiner with successful review metadata and failed
workflow metadata. Pass the shipped dispatcher's counters through unchanged.
This pins the documented combination contract, not live model tool ordering.

```scrut
$ combiner="$(awk '/^jq -nc --argjson review_pending/{take=1} take && /^[`][`][`]/{exit} take{print}' "${MONITOR_SKILL_FILE}")" \
>   && test -n "${combiner}" \
>   && observation="$(review_pending=false workflow_pending=true review_diagnostic='' workflow_diagnostic='workflow offline' bash -c "${combiner}")" \
>   && state="$(printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"noFix":false,"copilotPaused":false},"candidates":[],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare | jq --argjson observation "${observation}" '.observations=[$observation]')" \
>   && first="$(printf '%s\n' "${state}" | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch)" \
>   && printf '%s\n' "${first}" | jq -c '{retry:.route.retry,count:.observationFailures["review-metadata"]}' \
>   && counts="$(printf '%s\n' "${first}" | jq -c '.observationFailures')" \
>   && printf '%s\n' "${state}" | jq --argjson counts "${counts}" '.observationFailures=$counts' | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -c '{terminal,status,diagnostics}'
{"retry":true,"count":1}
{"terminal":true,"status":"unavailable","diagnostics":["review-metadata: workflow offline (two-tick observation bound)"]}
```

## Missing baseline diagnostic preserves its path and cause

```scrut
$ "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/missing-baseline" --once 2>&1
merge-flow: cannot load change-watch baseline *missing-baseline:*Could not open file* (glob)
Run 'merge-flow --help' for usage.
[2]
```

## Review changes on a later page are observed

```scrut
$ row '.reviews=[[{id:1,commit_id:"old",user:{login:"copilot"}}],[{id:3,commit_id:"aaa",user:{login:"copilot"}}]]' > "${WATCH_TEST_SEQUENCE}" \
>   && watch | jq -r '.event'
review
```

## PR responses contain only the requested JSON fields

```scrut
$ row '.' > "${WATCH_TEST_SEQUENCE}" && reset_watch \
>   && "${WATCH_CHANGES_STUB_BIN}" pr view 7 --repo acme/widgets --json state
{"state":"OPEN"}
```

## Workflow responses contain only the requested JSON fields

```scrut
$ row '.runs=[{headSha:"aaa",status:"queued"}]' > "${WATCH_TEST_SEQUENCE}" && reset_watch \
>   && "${WATCH_CHANGES_STUB_BIN}" run list --repo acme/widgets --branch topic --workflow Copilot --limit 10 --json status
[{"status":"queued"}]
```

## Merge-watch review decisions need the requested decision field

```scrut
$ row '.snapshot.reviewDecision="APPROVED"' > "${WATCH_TEST_SEQUENCE}" && reset_watch \
>   && "${MERGE_FLOW_BIN}" watch acme widgets 7 aaa --once --awaited REVIEW_REQUIRED | jq -c '{event,reviewDecision}'
{"event":"decision","reviewDecision":"APPROVED"}
```

## Invalid request contract helper

The fixture itself is invoked by absolute path for negative requests. Refusal
requires its explicit contract diagnostic, not an incidental parser failure.

```scrut {fail_fast: true}
$ function rejected() { local label="${1}" code=0; shift; "${WATCH_CHANGES_STUB_BIN}" "$@" > "${work}/refusal" 2>&1 || code=$?; test "${code}" = 1 && grep -q '^offline request rejected:' "${work}/refusal" && printf '%s: refused\n' "${label}"; } \
>   && echo contract-ready # error-output-allow: testcase asserts retained diagnostics: Invalid request contract helper
contract-ready
```

## PR identity, fields and unsupported input are refused

```scrut
$ rejected pr-number pr view 8 --repo acme/widgets --json state \
>   && rejected pr-repository pr view 7 --repo acme/other --json state \
>   && rejected pr-missing-repository pr view 7 --json state \
>   && rejected pr-missing-fields pr view 7 --repo acme/widgets \
>   && rejected pr-wrong-fields pr view 7 --repo acme/widgets --json unsupported \
>   && rejected pr-empty-fields pr view 7 --repo acme/widgets --json '' \
>   && rejected pr-duplicate-fields pr view 7 --repo acme/widgets --json state,state \
>   && rejected pr-missing-value pr view 7 --repo acme/widgets --json \
>   && rejected pr-duplicate-option pr view 7 --repo acme/widgets --json state --json state \
>   && rejected pr-extra-operand pr view 7 --repo acme/widgets --json state extra \
>   && rejected pr-unsupported-option pr view 7 --repo acme/widgets --json state --unsupported
pr-number: refused
pr-repository: refused
pr-missing-repository: refused
pr-missing-fields: refused
pr-wrong-fields: refused
pr-empty-fields: refused
pr-duplicate-fields: refused
pr-missing-value: refused
pr-duplicate-option: refused
pr-extra-operand: refused
pr-unsupported-option: refused
```

## Review identities, endpoints and pagination are refused

```scrut
$ rejected reviews-repository api --paginate --slurp repos/acme/other/pulls/7/reviews \
>   && rejected reviews-pr api --paginate --slurp repos/acme/widgets/pulls/8/reviews \
>   && rejected reviews-endpoint api --paginate --slurp repos/acme/widgets/pulls/7/comments \
>   && rejected reviews-missing-pagination api --slurp repos/acme/widgets/pulls/7/reviews \
>   && rejected reviews-missing-slurp api --paginate repos/acme/widgets/pulls/7/reviews \
>   && rejected reviews-wrong-pagination api --paginate --paginate repos/acme/widgets/pulls/7/reviews \
>   && rejected reviews-duplicate-pagination api --paginate --slurp --paginate repos/acme/widgets/pulls/7/reviews \
>   && rejected reviews-extra-operand api --paginate --slurp repos/acme/widgets/pulls/7/reviews extra \
>   && rejected reviews-unsupported-option api --paginate --slurp repos/acme/widgets/pulls/7/reviews --unsupported
reviews-repository: refused
reviews-pr: refused
reviews-endpoint: refused
reviews-missing-pagination: refused
reviews-missing-slurp: refused
reviews-wrong-pagination: refused
reviews-duplicate-pagination: refused
reviews-extra-operand: refused
reviews-unsupported-option: refused
```

## Workflow identity, selection and fields are refused

```scrut
$ rejected runs-repository run list --repo acme/other --branch topic --workflow Copilot --limit 10 --json headSha,status \
>   && rejected runs-missing-repository run list --branch topic --workflow Copilot --limit 10 --json headSha,status \
>   && rejected runs-branch run list --repo acme/widgets --branch other --workflow Copilot --limit 10 --json headSha,status \
>   && rejected runs-missing-branch run list --repo acme/widgets --workflow Copilot --limit 10 --json headSha,status \
>   && rejected runs-workflow run list --repo acme/widgets --branch topic --workflow Other --limit 10 --json headSha,status \
>   && rejected runs-missing-workflow run list --repo acme/widgets --branch topic --limit 10 --json headSha,status \
>   && rejected runs-limit run list --repo acme/widgets --branch topic --workflow Copilot --limit 20 --json headSha,status \
>   && rejected runs-missing-limit run list --repo acme/widgets --branch topic --workflow Copilot --json headSha,status \
>   && rejected runs-fields run list --repo acme/widgets --branch topic --workflow Copilot --limit 10 --json unsupported \
>   && rejected runs-missing-fields run list --repo acme/widgets --branch topic --workflow Copilot --limit 10 \
>   && rejected runs-unsupported-option run list --repo acme/widgets --branch topic --workflow Copilot --limit 10 --json headSha,status --unsupported
runs-repository: refused
runs-missing-repository: refused
runs-branch: refused
runs-missing-branch: refused
runs-workflow: refused
runs-missing-workflow: refused
runs-limit: refused
runs-missing-limit: refused
runs-fields: refused
runs-missing-fields: refused
runs-unsupported-option: refused
```

## Unsupported gh operations never reach a real tool

```scrut
$ rejected unsupported-operation auth status
unsupported-operation: refused
```

## A current-head notice still uses the explicit review cadence

```scrut
$ row '.snapshot.statusCheckRollup=[] | .latestReview={id:3,commit_id:"aaa"} | .reviews=[[{id:3,commit_id:"aaa",user:{login:"copilot"}}]]' > "${work}/notice" \
>   && { cat "${work}/notice"; row '.snapshot.state="CLOSED"'; } > "${WATCH_TEST_SEQUENCE}" \
>   && reset_watch && env -u MERGE_FLOW_INTERVAL "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/notice" --review-wait | jq -r '.event' \
>   && cat "${WATCH_TEST_SLEEP_LOG}"
closed
300
```

## Running checks take priority over an explicit review wait

```scrut
$ row '.latestReview={id:3,commit_id:"aaa"} | .reviews=[[{id:3,commit_id:"aaa",user:{login:"copilot"}}]]' > "${work}/notice-running" \
>   && { cat "${work}/notice-running"; row '.snapshot.state="CLOSED"'; } > "${WATCH_TEST_SEQUENCE}" \
>   && reset_watch && env -u MERGE_FLOW_INTERVAL "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/notice-running" --review-wait | jq -r '.event' \
>   && cat "${WATCH_TEST_SLEEP_LOG}"
closed
120
```

## An interval override takes priority over an explicit review wait

```scrut
$ { cat "${work}/notice"; row '.snapshot.state="CLOSED"'; } > "${WATCH_TEST_SEQUENCE}" \
>   && reset_watch && MERGE_FLOW_INTERVAL=17 "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/notice" --review-wait | jq -r '.event' \
>   && cat "${WATCH_TEST_SLEEP_LOG}"
closed
17
```

## Unchanged completed checks and contexts remain quiet

```scrut
$ row '.snapshot.statusCheckRollup=[{name:"lint",status:"COMPLETED",conclusion:"SUCCESS"},{context:"legacy",state:"SUCCESS"}] | .latestReview={id:3,commit_id:"aaa"} | .reviews=[[{id:3,commit_id:"aaa",user:{login:"copilot"}}]]' > "${work}/completed" \
>   && cat "${work}/completed" > "${WATCH_TEST_SEQUENCE}" && reset_watch \
>   && MERGE_FLOW_INTERVAL=0 "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/completed" --quiet-polls 1 | jq -c '{event,quietPolls}' \
>   && cat "${WATCH_TEST_COUNT}"
{"event":"quiet","quietPolls":1}
2
```

## Reordered completed results remain quiet

```scrut
$ jq -c '.snapshot.statusCheckRollup |= reverse' "${work}/completed" > "${WATCH_TEST_SEQUENCE}" && reset_watch \
>   && MERGE_FLOW_INTERVAL=0 "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/completed" --quiet-polls 1 | jq -c '{event,quietPolls}' \
>   && cat "${WATCH_TEST_COUNT}"
{"event":"quiet","quietPolls":1}
2
```

## A changed completed conclusion emits an event immediately

```scrut
$ jq -c '.snapshot.statusCheckRollup[0].conclusion="FAILURE"' "${work}/completed" > "${WATCH_TEST_SEQUENCE}" && reset_watch \
>   && MERGE_FLOW_INTERVAL=0 "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/completed" --quiet-polls 1 | jq -r '.event' \
>   && cat "${WATCH_TEST_COUNT}"
checks
1
```

## Time spent reading reduces the remaining watch lifetime

The fixture delays each PR read by one second. Its sleep log must show less
than the full lifetime after the first read, without pinning scheduler timing.

```scrut
$ { row '.'; row '.snapshot.state="CLOSED"'; } > "${WATCH_TEST_SEQUENCE}" && reset_watch \
>   && WATCH_TEST_READ_DELAY=1 MERGE_FLOW_INTERVAL=30 MERGE_FLOW_LIFETIME=20 "${MERGE_FLOW_BIN}" watch-changes acme widgets 7 aaa "${work}/baseline" | jq -r '.event' \
>   && first_wait="$(head -n 1 "${WATCH_TEST_SLEEP_LOG}")" \
>   && test "${first_wait}" -gt 0 && test "${first_wait}" -lt 20 && echo elapsed-deducted
closed
elapsed-deducted
```
