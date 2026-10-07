# Traffic history

Tests for `bin/record-traffic`, which the `Traffic history` workflow runs daily against the `traffic-data` branch. Every `gh api` call goes to `tests/fixtures/gh-stub`, which answers from `tests/data/record-traffic/api/`.

The fixture window runs from 2026-09-28 to 2026-10-01, and each case runs on 2026-10-01, so that day is still in progress and is not counted. The listed Actions runs include one created before the window and one created on the current day; neither has a jobs response, so fetching either one fails the case.

## Help

```scrut
$ "${RECORD_TRAFFIC_BIN}" --help | head -n 1
Usage: record-traffic [--repo OWNER/REPO] [--today YYYY-MM-DD] DATA_DIR
```

## A first run records every reported day

Checkouts count once per step that ran, across attempts, so a failed checkout counts and a skipped or cancelled one does not. A Copilot agent run counts each job that ran.

```scrut
$ stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && ln -s "${GH_STUB_BIN}" "${stub_dir}/gh" \
>   && data_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && PATH="${stub_dir}:${PATH}" STUB_GH_DIR="${RECORD_TRAFFIC_DATA_DIR}" \
>     "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-10-01 "${data_dir}" \
>   && jq -c 'to_entries[] | [.key, .value]' "${data_dir}/daily.json"
["2026-09-28",{"clones":10,"clone_uniques":4,"views":2,"view_uniques":1,"ci_checkouts":0,"copilot_jobs":0}]
["2026-09-29",{"clones":40,"clone_uniques":9,"views":7,"view_uniques":3,"ci_checkouts":4,"copilot_jobs":0}]
["2026-09-30",{"clones":3,"clone_uniques":2,"ci_checkouts":0,"copilot_jobs":1}]
["2026-10-01",{"clones":22,"clone_uniques":5,"views":3,"view_uniques":1}]
```

## Referrers and paths are saved as dated snapshots

```scrut
$ stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && ln -s "${GH_STUB_BIN}" "${stub_dir}/gh" \
>   && data_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && PATH="${stub_dir}:${PATH}" STUB_GH_DIR="${RECORD_TRAFFIC_DATA_DIR}" \
>     "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-10-01 "${data_dir}" \
>   && cd "${data_dir}" && find snapshots -type f | sort && jq -c '.[0].referrer' snapshots/referrers/2026-10-01.json
snapshots/paths/2026-10-01.json
snapshots/referrers/2026-10-01.json
"github.com"
```

## The README summarizes days and weeks

The external estimate subtracts both automation counts. The current day has no estimate yet, so the weekly figure carries an asterisk.

```scrut
$ stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && ln -s "${GH_STUB_BIN}" "${stub_dir}/gh" \
>   && data_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && PATH="${stub_dir}:${PATH}" STUB_GH_DIR="${RECORD_TRAFFIC_DATA_DIR}" \
>     "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-10-01 "${data_dir}" \
>   && grep -E '^(#|\| [0-9])' "${data_dir}/README.md"
# Traffic history for cboone/agent-harness-plugins
## Reading the clone counts
## Last 14 days
| 2026-10-01 | 22 | 5 | n/a | n/a | n/a | 3 | 1 |
| 2026-09-30 | 3 | 2 | 0 | 1 | 2 | n/a | n/a |
| 2026-09-29 | 40 | 9 | 4 | 0 | 36 | 7 | 3 |
| 2026-09-28 | 10 | 4 | 0 | 0 | 10 | 2 | 1 |
## Weekly totals
| 2026-09-28 | 75 | 5 | 48* | 12 |
```

## A later run keeps older days and counted days

Days GitHub no longer reports stay as they were. A reported day takes GitHub's latest figures but keeps its automation count, so its runs are not fetched again, and an estimate below zero is floored.

```scrut
$ stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && ln -s "${GH_STUB_BIN}" "${stub_dir}/gh" \
>   && data_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && cp "${RECORD_TRAFFIC_DATA_DIR}/existing/daily.json" "${data_dir}/" \
>   && PATH="${stub_dir}:${PATH}" STUB_GH_DIR="${RECORD_TRAFFIC_DATA_DIR}" \
>     "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-10-01 "${data_dir}" \
>   && jq -c '{"2026-09-20": .["2026-09-20"], "2026-09-28": .["2026-09-28"]}' "${data_dir}/daily.json" \
>   && grep -E '^\| 2026-09-28 \| 10 ' "${data_dir}/README.md"
{"2026-09-20":{"clones":5,"clone_uniques":1,"views":1,"view_uniques":1,"ci_checkouts":2,"copilot_jobs":0},"2026-09-28":{"clones":10,"clone_uniques":4,"ci_checkouts":12,"copilot_jobs":0,"views":2,"view_uniques":1}}
| 2026-09-28 | 10 | 4 | 12 | 0 | 0 | 2 | 1 |
```

## A run with every reported day counted reads no Actions runs

The first run lists the runs once and fetches the jobs of the three runs inside the window. The second run adds nothing to the log.

```scrut
$ stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && ln -s "${GH_STUB_BIN}" "${stub_dir}/gh" \
>   && data_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && export PATH="${stub_dir}:${PATH}" STUB_GH_DIR="${RECORD_TRAFFIC_DATA_DIR}" STUB_GH_LOG="${data_dir}/gh.log" \
>   && "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-10-01 "${data_dir}/out" \
>   && "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-10-01 "${data_dir}/out" \
>   && grep -c 'actions/runs' "${data_dir}/gh.log"
4
```

## Errors

A missing data directory prints the usage.

```scrut
$ "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins 2>&1 | head -n 1
Usage: record-traffic [--repo OWNER/REPO] [--today YYYY-MM-DD] DATA_DIR
```

```scrut
$ "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins > /dev/null 2>&1; echo "exit ${?}"
exit 2
```

The repository must be named, by flag or by `GITHUB_REPOSITORY`.

```scrut
$ env -u GITHUB_REPOSITORY "${RECORD_TRAFFIC_BIN}" out 2>&1
record-traffic: --repo or GITHUB_REPOSITORY must name OWNER/REPO
[1]
```

```scrut
$ "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-10-1 out 2>&1
record-traffic: --today must be YYYY-MM-DD
[1]
```

A traffic endpoint the token cannot read names the endpoint and stops before anything is written.

```scrut
$ stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && ln -s "${GH_STUB_BIN}" "${stub_dir}/gh" \
>   && data_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && PATH="${stub_dir}:${PATH}" STUB_GH_DIR="${RECORD_TRAFFIC_DATA_DIR}" STUB_GH_API_FAIL=traffic_clones \
>     "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-10-01 "${data_dir}" 2>&1; echo "exit ${?}" \
>   && find "${data_dir}" -name '*.json' -path '*snapshots*'
gh: Resource not accessible by integration (HTTP 403)
record-traffic: could not fetch repos/cboone/agent-harness-plugins/traffic/clones
exit 1
```

A failure partway through counting Actions runs leaves the daily data uncounted, so the next run tries again.

```scrut
$ stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && ln -s "${GH_STUB_BIN}" "${stub_dir}/gh" \
>   && data_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && PATH="${stub_dir}:${PATH}" STUB_GH_DIR="${RECORD_TRAFFIC_DATA_DIR}" STUB_GH_API_FAIL=actions_runs_101_jobs \
>     "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-10-01 "${data_dir}" 2>&1; echo "exit ${?}" \
>   && jq -c '[.[] | has("ci_checkouts")] | any' "${data_dir}/daily.json"
gh: Resource not accessible by integration (HTTP 403)
record-traffic: could not fetch repos/cboone/agent-harness-plugins/actions/runs/101/jobs?filter=all&per_page=100
exit 1
false
```
