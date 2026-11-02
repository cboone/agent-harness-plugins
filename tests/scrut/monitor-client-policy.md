# Monitor client policy

All API operations use committed stubs whose PATH selection is checked before
execution. The policy commands are pure local operations.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

## Available client feedback uses the existing complete intake

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" intake
{"reviews":1,"ids":[7100]}
{"threads":1}
{"surfaces":{"reviews":1,"reviewComments":1,"issueComments":0},"uncovered":0}
exit=0; replies=0; resolutions=0
```

## Client approval permits a fixed thread at the published head

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" fixed
true
exit=0; replies=1; resolutions=1
```

## Unapproved client rounds cannot write

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" unapproved 2>&1
Error: watch policy blocks process-review (unavailable)
exit=1; replies=0; resolutions=0
```

## A fixing commit outside the PR head cannot close a thread

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" unfixed 2>&1
Error: client fixing commit is absent from PR head
exit=1; replies=0; resolutions=0
```

## A remote head change prevents even the combined reply

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" moved 2>&1
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
```

## The independent cboone pause blocks body intake

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" paused 2>&1
Error: watch policy blocks read-review (paused)
exit=1; replies=0; resolutions=0
```

## Client selection applies before every old autonomous route

```scrut
$ printf '%s\n' '{"snapshot":{"state":"OPEN"},"restrictions":{"repository":"SWING-LEFT/r","noFix":false,"copilotPaused":false},"candidates":[{"action":"request-review","detail":"missing"},{"action":"wait-review","detail":"absent"},{"action":"confirm-review","detail":"confirmation"},{"action":"merge","detail":"ready"},{"action":"post-merge","detail":"merged"}],"runningPermittedCheck":false}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -c '{route,wait,terminal,blocked:[.wouldDo[].action]}'
{"route":null,"wait":false,"terminal":true,"blocked":["request-review","wait-review","confirm-review","merge","post-merge"]}
```

## Unknown identity permits metadata observation only

```scrut
$ printf '%s\n' '{"restrictions":{"noFix":false,"copilotPaused":false}}' | "${MERGE_FLOW_BIN}" prepare | jq -c .policy.allowedActions
["read-axis","report","escalate"]
```

## Old permissions cannot survive policy re-preparation

```scrut
$ printf '%s\n' '{"restrictions":{"repository":"acme/r","noFix":false,"copilotPaused":false}}' | "${MERGE_FLOW_BIN}" prepare | jq '.restrictions=(.policy.restrictions | .repository="swing-left/r")' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" gate process-review
{
  "action": "process-review",
  "allowed": false,
  "status": "unavailable"
}
```

## Approved round authority fails closed on a different head

```scrut
$ jq -n '{reviewId:10,snapshot:{state:"OPEN",number:7,headRefOid:("b"*40)},restrictions:{repository:"swing-left/r",noFix:false,copilotPaused:false,clientRound:{repository:"swing-left/r",authority:"sample",prNumber:7,head:("a"*40),reviewIds:[10]}}}' | "${MERGE_FLOW_BIN}" prepare > /dev/null
[5]
```

## Both entry points load the same policy before workflow instructions

```scrut
$ for name in monitor resolve-copilot-feedback; do file="${REPO_ROOT}/plugins/monitor-pr/skills/${name}/SKILL.md"; awk '/^## Repository policy first$/ {policy=NR} /^## (Core )?Workflow$/ {if (!policy || policy >= NR) exit 1; found=1} END {if (!found) exit 1}' "${file}" || exit 1; done && printf '%s\n' 'both entry points load shared repository policy first'
both entry points load shared repository policy first
```

## No-fix and explicit pauses override round authority

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" no-fix 2>&1
Error: watch policy blocks process-review (unavailable)
exit=1; replies=0; resolutions=0
```

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" explicit-pause 2>&1
Error: watch policy blocks process-review (paused)
exit=1; replies=0; resolutions=0
```

## Review-wait helper entry cannot bypass the client gate

```scrut
$ state="$(mktemp "${TMPDIR:-/tmp}/client-wait.XXXXXX")" && printf '%s\n' '{"restrictions":{"repository":"swing-left/r","noFix":false,"copilotPaused":false}}' | "${MERGE_FLOW_BIN}" prepare > "${state}" && "${MERGE_FLOW_BIN}" --watch-state "${state}" watch-changes swing-left r 7 head baseline --review-wait 2>&1; code=$?; rm "${state}"; test "${code}" = 1
merge-flow: watch policy blocks wait-review (unavailable)
```

## Category-based closure cannot replace a fixing commit

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" wrong-reason 2>&1
Error: client resolution requires --reason ADDRESSED
exit=1; replies=0; resolutions=0
```

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" missing-record 2>&1
Error: client resolution requires a fixing commit
exit=1; replies=0; resolutions=0
```

## An approval for a different review cannot be reused

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" wrong-review 2>&1
jq: error (at <stdin>:*): client round authority does not match repository, open PR, head or review (glob)
policy exit=5; gh calls=0
[5]
```

## Reply-only and resolve-only operations use live client context

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" reply
reply1
exit=0; replies=1; resolutions=0
```

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" resolve
true
exit=0; replies=0; resolutions=1
```

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" moved-reply 2>&1
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
```

## Every client mutation refuses a closed PR

```scrut
$ for mode in closed-reply closed-resolve closed-combined; do "${CLIENT_POLICY_CASE_BIN}" "${mode}" 2>&1 || exit; done
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
```

## A push between reply and resolution leaves the thread open

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" moved-between 2>&1
Error: client thread does not match approved PR, review or live context
exit=1; replies=1; resolutions=0
```

## Actual thread ownership must match the approved round

```scrut
$ for mode in other-review other-pr other-repo human-thread resolved-thread missing-thread other-id other-type; do "${CLIENT_POLICY_CASE_BIN}" "${mode}" 2>&1 || exit; done
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
Error: client thread does not match approved PR, review or live context
exit=1; replies=0; resolutions=0
```

## A round approval cannot authorize automatic repair or synchronization

```scrut
$ for state in DIRTY BEHIND; do for approved in false true; do jq -n --arg state "${state}" --argjson approved "${approved}" '{snapshot:{state:"OPEN",number:7,headRefOid:("a"*40),mergeStateStatus:$state},reviewId:10,restrictions:{repository:"swing-left/r",noFix:false,copilotPaused:false,clientRound:(if $approved then {repository:"swing-left/r",authority:"sample",prNumber:7,head:("a"*40),reviewIds:[10]} else null end)},candidates:[{action:"repair",detail:"failed check"},{action:"sync",detail:$state}],runningPermittedCheck:false}' | "${MERGE_FLOW_BIN}" prepare | "${MERGE_FLOW_BIN}" lifecycle | "${MERGE_FLOW_BIN}" dispatch | jq -c --arg state "${state}" --argjson approved "${approved}" '{state:$state,approved:$approved,route,wait,blocked:[.wouldDo[].action]}' || exit; done; done
{"state":"DIRTY","approved":false,"route":null,"wait":false,"blocked":["repair","sync"]}
{"state":"DIRTY","approved":true,"route":null,"wait":false,"blocked":["repair","sync"]}
{"state":"BEHIND","approved":false,"route":null,"wait":false,"blocked":["repair","sync"]}
{"state":"BEHIND","approved":true,"route":null,"wait":false,"blocked":["repair","sync"]}
```

## Incomplete approval evidence fails before authentication

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" missing-authority 2>&1
jq: error (at <stdin>:*): invalid client round authority (glob)
policy exit=5; gh calls=0
[5]
```

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" empty-authority 2>&1
jq: error (at <stdin>:*): invalid client round authority (glob)
policy exit=5; gh calls=0
[5]
```

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" blank-authority 2>&1
jq: error (at <stdin>:*): invalid client round authority (glob)
policy exit=5; gh calls=0
[5]
```

## Another PR cannot reuse the approval even at the same head and review

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" wrong-pr 2>&1
jq: error (at <stdin>:*): client round authority does not match repository, open PR, head or review (glob)
policy exit=5; gh calls=0
[5]
```

## Another repository cannot reuse the approval

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" wrong-repository 2>&1
jq: error (at <stdin>:*): client round authority does not match repository, open PR, head or review (glob)
policy exit=5; gh calls=0
[5]
```

## Live review identity accepts GitHub BigInt representations and the Actions opener

```scrut
$ for mode in numeric-review actions-thread; do "${CLIENT_POLICY_CASE_BIN}" "${mode}" || exit; done
true
exit=0; replies=1; resolutions=1
true
exit=0; replies=1; resolutions=1
```

## Thread read errors preserve diagnostics and cannot authorize a write

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" thread-errors 2>&1
Error: client thread context unavailable: sample read error
exit=1; replies=0; resolutions=0
```

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" thread-read-failure 2>&1
sample thread read failure
Error: client thread context unavailable
exit=1; replies=0; resolutions=0
```

## An authorized no-fix reply leaves the thread open

```scrut
$ "${CLIENT_POLICY_CASE_BIN}" reply-unfixed
reply1
exit=0; replies=1; resolutions=0
```
