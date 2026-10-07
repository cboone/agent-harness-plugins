# Traffic history

Tests for `bin/record-traffic`, which the `Traffic history` workflow runs daily against the `traffic-data` branch. Every `gh api` call goes to `tests/fixtures/gh-stub`, which answers from `tests/data/record-traffic/api/` or from a variant of it a case writes.

The fixture window runs from 2026-09-28 to 2026-10-01, and each case that fetches data runs with `--today 2026-10-01`, so that day is still in progress and is not counted. The listed Actions runs include one created before the window and one created on the current day; neither has a jobs response, so fetching either one fails the case. Run 103, created at 23:59:59 UTC, checks that runs are dated in UTC, and run 101 appears on both pages of the listing, as it does when a new run shifts the pages while they are fetched.

## Setup

`record` runs the script against an API directory, and `api_variant` copies the fixture API directory so a case can change one response. The stub ignores the query string and the `--paginate` and `--slurp` flags, so the cases that depend on them assert the logged calls.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && mkdir "${work}/bin" && ln -s "${GH_STUB_BIN}" "${work}/bin/gh" \
>   && function record() { local api="${1}"; shift; PATH="${work}/bin:${PATH}" STUB_GH_DIR="${api}" "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-10-01 "$@"; } \
>   && function api_variant() { local dir; dir="$(mktemp -d "${work}/api.XXXXXX")"; cp -R "${RECORD_TRAFFIC_DATA_DIR}/api" "${dir}/"; printf '%s\n' "${dir}"; } \
>   && echo ready
ready
```

## Help

```scrut
$ "${RECORD_TRAFFIC_BIN}" --help | head -n 1
Usage: record-traffic [--repo OWNER/REPO] [--today YYYY-MM-DD] DATA_DIR
```

## A first run records every reported day

Checkouts count once per step that ran, across attempts and pages of jobs, so a failed checkout counts and a skipped or cancelled one does not, and post-job checkout cleanup steps do not count at all. Run 101, listed twice, counts once. A `dynamic` run counts each job that ran.

```scrut
$ record "${RECORD_TRAFFIC_DATA_DIR}" "${work}/first" \
>   && jq -c 'to_entries[] | [.key, .value]' "${work}/first/daily.json"
["2026-09-28",{"clones":10,"clone_uniques":4,"views":2,"view_uniques":1,"ci_checkouts":0,"dynamic_jobs":0}]
["2026-09-29",{"clones":40,"clone_uniques":9,"views":7,"view_uniques":3,"ci_checkouts":4,"dynamic_jobs":0}]
["2026-09-30",{"clones":3,"clone_uniques":2,"ci_checkouts":0,"dynamic_jobs":1}]
["2026-10-01",{"clones":22,"clone_uniques":5,"views":3,"view_uniques":1}]
```

## Referrers and paths are saved as dated snapshots

```scrut
$ (cd "${work}/first" && find snapshots -type f | sort && jq -c '.[0].referrer' snapshots/referrers/2026-10-01.json)
snapshots/paths/2026-10-01.json
snapshots/referrers/2026-10-01.json
"github.com"
```

## The README summarizes days and weeks

The external estimate subtracts both automation counts. The current day has no estimate yet, so the weekly automation and external figures carry an asterisk. A day GitHub reported no views for shows `n/a` in the view columns.

```scrut
$ grep -E '^(#|\| [0-9])' "${work}/first/README.md"
# Traffic history for cboone/agent-harness-plugins
## Reading the clone counts
## Latest 14 days on record
| 2026-10-01 | 22 | 5 | n/a | n/a | n/a | 3 | 1 |
| 2026-09-30 | 3 | 2 | 0 | 1 | 2 | n/a | n/a |
| 2026-09-29 | 40 | 9 | 4 | 0 | 36 | 7 | 3 |
| 2026-09-28 | 10 | 4 | 0 | 0 | 10 | 2 | 1 |
## Weekly totals
| 2026-09-28 | 75 | 5* | 48* | 12 |
```

## The Actions calls name the range, the pages and every attempt

The run listing covers the uncounted days widened by one day on each side, and each jobs call asks for every attempt. Only runs created on the counted days have their jobs fetched.

```scrut
$ STUB_GH_LOG="${work}/calls.log" record "${RECORD_TRAFFIC_DATA_DIR}" "${work}/logged" \
>   && grep 'actions/runs' "${work}/calls.log"
gh api --paginate --slurp repos/cboone/agent-harness-plugins/actions/runs?created=2026-09-27..2026-10-01&per_page=100
gh api --paginate --slurp repos/cboone/agent-harness-plugins/actions/runs/101/jobs?filter=all&per_page=100
gh api --paginate --slurp repos/cboone/agent-harness-plugins/actions/runs/102/jobs?filter=all&per_page=100
gh api --paginate --slurp repos/cboone/agent-harness-plugins/actions/runs/103/jobs?filter=all&per_page=100
```

A second run on the same day finds every completed day counted and reads no Actions runs.

```scrut
$ : > "${work}/calls.log" \
>   && STUB_GH_LOG="${work}/calls.log" record "${RECORD_TRAFFIC_DATA_DIR}" "${work}/logged" \
>   && grep -c 'actions/runs' "${work}/calls.log"
0
[1]
```

## A later run keeps older days and counted days

Days GitHub no longer reports stay as they were. A reported day takes GitHub's latest figures but keeps its automation count, and an estimate below zero is floored.

```scrut
$ mkdir "${work}/later" && cp "${RECORD_TRAFFIC_DATA_DIR}/existing/daily.json" "${work}/later/" \
>   && record "${RECORD_TRAFFIC_DATA_DIR}" "${work}/later" \
>   && jq -c '{"2026-09-14": .["2026-09-14"], "2026-09-28": .["2026-09-28"]}' "${work}/later/daily.json"
{"2026-09-14":{"clones":5,"clone_uniques":1,"views":1,"view_uniques":1,"ci_checkouts":2,"dynamic_jobs":0},"2026-09-28":{"clones":10,"clone_uniques":4,"ci_checkouts":12,"dynamic_jobs":0,"views":2,"view_uniques":1}}
```

The daily table stops at the 14 latest days, and the weekly table covers every week, newest first, with no asterisk on a week whose days are all counted. 2026-09-20 is a Sunday, so it belongs to the week of 2026-09-14.

```scrut
$ sed -n '/^## Latest/,/^## Weekly/p' "${work}/later/README.md" | grep -E '^\| 2026' | sed -n '1p;$p'
| 2026-10-01 | 22 | 5 | n/a | n/a | n/a | 3 | 1 |
| 2026-09-18 | 5 | 1 | 2 | 0 | 3 | 1 | 1 |
```

```scrut
$ sed -n '/^## Weekly/,$p' "${work}/later/README.md" | grep -E '^\| 2026'
| 2026-09-28 | 75 | 17* | 38* | 12 |
| 2026-09-21 | 35 | 14 | 21 | 7 |
| 2026-09-14 | 35 | 14 | 21 | 7 |
```

## A week with an uncounted clone day carries an asterisk

Here GitHub reports clones only for the current day, while two completed days have views and are counted. The counted days do not hide the uncounted one.

```scrut
$ api="$(api_variant)" \
>   && jq '.clones |= map(select(.timestamp | startswith("2026-10-01")))' "${RECORD_TRAFFIC_DATA_DIR}/api/traffic_clones.json" > "${api}/api/traffic_clones.json" \
>   && record "${api}" "${work}/views-only" \
>   && sed -n '/^## Weekly/,$p' "${work}/views-only/README.md" | grep -E '^\| 2026'
| 2026-09-28 | 22 | 4* | 0* | 12 |
```

## A day with Actions runs in progress is left for a later run

```scrut
$ api="$(api_variant)" \
>   && jq '(.[].workflow_runs[] | select(.id == 101) | .status) = "in_progress"' "${RECORD_TRAFFIC_DATA_DIR}/api/actions_runs.json" > "${api}/api/actions_runs.json" \
>   && record "${api}" "${work}/pending" 2>&1 \
>   && jq -c 'map_values(has("ci_checkouts"))' "${work}/pending/daily.json"
record-traffic: leaving 2026-09-29 uncounted until its Actions runs complete
{"2026-09-28":true,"2026-09-29":false,"2026-09-30":true,"2026-10-01":false}
```

## Empty traffic records nothing and reads no Actions runs

```scrut
$ api="$(api_variant)" \
>   && echo '{"count": 0, "uniques": 0, "clones": []}' > "${api}/api/traffic_clones.json" \
>   && echo '{"count": 0, "uniques": 0, "views": []}' > "${api}/api/traffic_views.json" \
>   && STUB_GH_LOG="${work}/empty.log" record "${api}" "${work}/empty" \
>   && jq -c . "${work}/empty/daily.json" && grep -c 'actions/runs' "${work}/empty.log"
{}
0
[1]
```

## Errors

Omitting `DATA_DIR` prints the usage and exits 2.

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
$ env -u GITHUB_REPOSITORY "${RECORD_TRAFFIC_BIN}" "${work}/unused" 2>&1
record-traffic: --repo or GITHUB_REPOSITORY must name OWNER/REPO
[1]
```

```scrut
$ "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --verbose "${work}/unused" 2>&1
record-traffic: unknown option: --verbose
[1]
```

`--today` must be a real date in the expected form.

```scrut
$ "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-10-1 "${work}/unused" 2>&1
record-traffic: --today must be a valid YYYY-MM-DD date
[1]
```

```scrut
$ "${RECORD_TRAFFIC_BIN}" --repo cboone/agent-harness-plugins --today 2026-02-30 "${work}/unused" 2>&1
record-traffic: --today must be a valid YYYY-MM-DD date
[1]
```

A `daily.json` that is not one JSON object stops the run before anything is fetched.

```scrut
$ mkdir "${work}/corrupt" && printf '{}\n{}\n' > "${work}/corrupt/daily.json" \
>   && record "${RECORD_TRAFFIC_DATA_DIR}" "${work}/corrupt" 2>&1 | sed "s#${work}#WORK#"
record-traffic: WORK/corrupt/daily.json is not a single JSON object
```

A traffic endpoint the token cannot read names the endpoint and stops before any traffic data or snapshot is saved.

```scrut
$ STUB_GH_API_FAIL=traffic_clones record "${RECORD_TRAFFIC_DATA_DIR}" "${work}/denied" 2>&1; echo "exit ${?}"; [[ -e "${work}/denied" ]] || echo "nothing written"
gh: Resource not accessible by integration (HTTP 403)
record-traffic: could not fetch repos/cboone/agent-harness-plugins/traffic/clones; the token needs Administration read access for traffic and Actions read access for runs
exit 1
nothing written
```

A runs listing in an unexpected shape, here one page without the `--slurp` array around it, stops the run and leaves the days uncounted, so the next run tries again.

```scrut
$ api="$(api_variant)" \
>   && jq '.[0]' "${RECORD_TRAFFIC_DATA_DIR}/api/actions_runs.json" > "${api}/api/actions_runs.json" \
>   && record "${api}" "${work}/unslurped" 2>&1; echo "exit ${?}"; jq -c '[.[] | has("ci_checkouts")] | any' "${work}/unslurped/daily.json"
record-traffic: unexpected response from repos/cboone/agent-harness-plugins/actions/runs?created=2026-09-27..2026-10-01&per_page=100
exit 1
false
```

A listing that holds fewer runs than its total, as when GitHub's 1000-run limit cuts it short, stops the run the same way.

```scrut
$ api="$(api_variant)" \
>   && jq '.[0].total_count = 1500' "${RECORD_TRAFFIC_DATA_DIR}/api/actions_runs.json" > "${api}/api/actions_runs.json" \
>   && record "${api}" "${work}/truncated" 2>&1; echo "exit ${?}"; jq -c '[.[] | has("ci_checkouts")] | any' "${work}/truncated/daily.json"
record-traffic: listed 5 of 1500 runs for 2026-09-27..2026-10-01; GitHub lists at most 1000 runs per query
exit 1
false
```

A failure partway through counting leaves every day uncounted as well.

```scrut
$ STUB_GH_API_FAIL=actions_runs_101_jobs record "${RECORD_TRAFFIC_DATA_DIR}" "${work}/partial" 2>&1; echo "exit ${?}"; jq -c '[.[] | has("ci_checkouts")] | any' "${work}/partial/daily.json"
gh: Resource not accessible by integration (HTTP 403)
record-traffic: could not fetch repos/cboone/agent-harness-plugins/actions/runs/101/jobs?filter=all&per_page=100; the token needs Administration read access for traffic and Actions read access for runs
exit 1
false
```

## Cleanup

```scrut
$ rm -rf "${work}"
```
