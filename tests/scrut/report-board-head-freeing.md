# Head freeing counts

Execute the rendered template with a minimal DOM. Capture the lane model and
rendered wording. Preserve row states as an independent assertion.

## Setup

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" &&
> dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" &&
> function render_board() {
>   local result render_status
>   if result="$("${REPORT_BOARD_BIN}" render --standalone "${1}" "${2}" 2>&1)"; then
>     return 0
>   else
>     render_status=$?
>     printf '%s\n' "${result}" >&2
>     return "${render_status}"
>   fi
> }
```

## Companion ordering keeps the successor queued

```scrut
$ render_board "${REPORT_BOARD_DATA_DIR}/head-freeing.json" "${dir}/board.html" &&
> node "${REPORT_BOARD_EXECUTE_BIN}" "${dir}/board.html" "${REPORT_BOARD_DATA_DIR}/head-freeing.json"
{"freedAfter":0,"thenOneMore":false,"states":[[1,"now"],[3,"blocked"],[4,"queued"]]}
```

## Companion ordering satisfied by the head frees the branch

```scrut
$ jq '.issues[2].after = [1]' "${REPORT_BOARD_DATA_DIR}/head-freeing.json" > "${dir}/head.json" &&
> render_board "${dir}/head.json" "${dir}/board.html" &&
> node "${REPORT_BOARD_EXECUTE_BIN}" "${dir}/board.html" "${dir}/head.json"
{"freedAfter":1,"thenOneMore":true,"states":[[1,"now"],[3,"blocked"],[4,"queued"]]}
```

## A companion hard blocker does not prevent its root from starting

```scrut
$ jq '.issues[2] |= (del(.after) + {waitingOn:[{pr:90}],blockedBecause:"Needs PR 90."})' "${REPORT_BOARD_DATA_DIR}/head-freeing.json" > "${dir}/hard.json" &&
> render_board "${dir}/hard.json" "${dir}/board.html" &&
> node "${REPORT_BOARD_EXECUTE_BIN}" "${dir}/board.html" "${dir}/hard.json"
{"freedAfter":1,"thenOneMore":true,"states":[[1,"now"],[3,"blocked"],[4,"blocked"]]}
```

## A hard-blocked companion still queues its branch through soft ordering

```scrut
$ jq '.issues[2] += {waitingOn:[{pr:91}],blockedBecause:"Needs PR 91."}' "${REPORT_BOARD_DATA_DIR}/head-freeing.json" > "${dir}/both.json" &&
> render_board "${dir}/both.json" "${dir}/board.html" &&
> node "${REPORT_BOARD_EXECUTE_BIN}" "${dir}/board.html" "${dir}/both.json"
{"freedAfter":0,"thenOneMore":false,"states":[[1,"now"],[3,"blocked"],[4,"blocked"]]}
```

## An admitted head companion satisfies successor ordering

```scrut {fail_fast: true}
$ jq '.issues[2].after = [2] | .issues += [{number:2,title:"Head companion",milestone:null,sameBranchAs:1,progress:null,affinity:{owner:null,kind:null,tier:null,reasons:[]}}] | .lanes[0].issues = [1,2,3,4]' "${REPORT_BOARD_DATA_DIR}/head-freeing.json" > "${dir}/admitted.json" &&
> render_board "${dir}/admitted.json" "${dir}/board.html" &&
> node "${REPORT_BOARD_EXECUTE_BIN}" "${dir}/board.html" "${dir}/admitted.json"
{"freedAfter":1,"thenOneMore":true,"states":[[1,"now"],[3,"blocked"],[4,"queued"],[2,"now"]]}
```

## A blocked head companion cannot satisfy successor ordering

```scrut
$ jq '.issues[3] += {waitingOn:[{pr:91}],blockedBecause:"Needs PR 91."}' "${dir}/admitted.json" > "${dir}/blocked.json" &&
> render_board "${dir}/blocked.json" "${dir}/board.html" &&
> node "${REPORT_BOARD_EXECUTE_BIN}" "${dir}/board.html" "${dir}/blocked.json"
{"freedAfter":0,"thenOneMore":false,"states":[[1,"now"],[3,"blocked"],[4,"queued"],[2,"blocked"]]}
```
