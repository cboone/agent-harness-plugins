# Bugs gather

Tests for the `bugs-gather` script that `publish-report-board` bundles. It
searches one repository for its open and recently closed bugs, adds their
ZenHub state, places every open bug in a tier from the model's assessments and
the triage note, and keeps a per-repository cache so a later sync can say what
moved and which bugs need reading again.

Every call goes through `tests/fixtures/gh-stub` and `tests/fixtures/curl-stub`,
which answer from `tests/data/bugs-gather/`. The fixtures describe `acme/widgets`
(ZenHub ID 101) with 20 open bugs, each built to exercise one tier rule, and 2
closed in the last week. The config names a test-only token variable holding a
sample value, and the Makefile unsets the real ZenHub token variable, so no
test can reach ZenHub. `bugs` takes settings (`NAME=value`) first, then the
command. The gather time is fixed at 2026-10-15T16:00:00Z.

```scrut
$ function bugs() {
>   local -a settings=()
>   while [[ "${1:-}" == *=* ]]; do
>     settings+=("${1}")
>     shift
>   done
>   env PATH="${stub_dir}:${PATH}" \
>     STUB_GH_DIR="${BUGS_GATHER_DATA_DIR}/github" STUB_CURL_DIR="${BUGS_GATHER_DATA_DIR}/zenhub" \
>     STUB_CURL_TOKEN=sample-token BUGS_TEST_ZENHUB_TOKEN=sample-token \
>     BUGS_GATHER_NOW=2026-10-15T16:00:00Z XDG_CACHE_HOME="${work}/cache" XDG_CONFIG_HOME="${work}/config" \
>     ${settings[@]+"${settings[@]}"} "${BUGS_GATHER_BIN}" "${@}"
> }
> function config_with() {
>   jq --arg note "${BUGS_GATHER_DATA_DIR}/triage.md" ".triageNote = \$note | ${1:-.}" "${BUGS_GATHER_DATA_DIR}/config.json"
> }
> function tiers() {
>   jq -r '.tiers | to_entries[] | "\(.key): \(.value | map("#\(.number)\(if .group then "/\(.group)" else "" end)") | join(" "))"' "${1}"
> }
> stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
> cp "${GH_STUB_BIN}" "${stub_dir}/gh"
> cp "${CURL_STUB_BIN}" "${stub_dir}/curl"
> chmod +x "${stub_dir}/gh" "${stub_dir}/curl"
> work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
> config_with > "${work}/config.json"
> assessments="${BUGS_GATHER_DATA_DIR}/assessments.json"
> bugs gather "${work}/config.json" "${work}/gather.json" > /dev/null
> bugs score "${work}/config.json" "${work}/gather.json" "${assessments}" "${work}/scored.json" > /dev/null
```

## Gather reports its counts, and a first sync is a cold one

```scrut
$ bugs gather "${work}/config.json" "${work}/again.json" | sed "s|${work}|WORK|g"
acme/widgets at main 01234567: 20 open bugs, 3 with an open fix, 1 from outside reporters; 2 closed in the last 7 days
Cold sync: no usable cache at WORK/cache/report-boards/bugs/github.com/acme/widgets/gather.json, so nothing can be compared yet.
```

## Searches cover the bug labels and issue types, open and recently closed

The searches run in parallel, so the log is sorted. A comma between quoted
labels matches any of them, and each issue type runs as its own search.

```scrut
$ log="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && bugs STUB_GH_LOG="${log}" gather "${work}/config.json" "${work}/logged.json" > /dev/null && sort "${log}"
gh api graphql repository owner=acme name=widgets
gh api graphql search q=repo:acme/widgets is:issue is:closed closed:>=2026-10-08 label:"bug"
gh api graphql search q=repo:acme/widgets is:issue is:closed closed:>=2026-10-08 type:"Bug"
gh api graphql search q=repo:acme/widgets is:issue is:open label:"bug"
gh api graphql search q=repo:acme/widgets is:issue is:open type:"Bug"
```

## A bug found by both a label and its type is one bug

`#10` carries the `bug` label and the Bug type; `#26` has only the type.

```scrut
$ jq -r '.bugs[] | select(.number == 10 or .number == 26) | "#\(.number) \(.foundBy | join(", "))"' "${work}/gather.json"
#10 open-labels, open-type
#26 open-type
```

## People outside the repository count as users, and bots do not

`#20` was filed by an outside reporter, with comments from another outsider, a
bot, and a member.

```scrut
$ jq -c '.bugs[] | select(.number == 20) | {outsideReporter, outsidePeople, reactions, comments, lastComment}' "${work}/gather.json"
{"outsideReporter":true,"outsidePeople":2,"reactions":4,"comments":3,"lastComment":{"author":"alice","at":"2026-10-12T09:00:00Z","outside":false}}
```

## Fix pull requests carry their draft, check, and review state

```scrut
$ jq -r '.bugs[] | select(.state == "open" and (.fixes | length) > 0) | "#\(.number) <- \(.fixes | map("#\(.number) draft=\(.isDraft) checks=\(.checks) review=\(.reviewDecision)") | join("; "))"' "${work}/gather.json"
#16 <- #40 draft=false checks=SUCCESS review=APPROVED
#27 <- #42 draft=true checks=null review=null
#28 <- #43 draft=false checks=FAILURE review=null
```

## Closed bugs record why they closed and what fixed them

```scrut
$ jq -r '.bugs[] | select(.state == "closed") | "#\(.number) \(.stateReason) fixedBy=\(.fixedBy | map(.number) | join(","))"' "${work}/gather.json"
#5 COMPLETED fixedBy=41
#6 DUPLICATE fixedBy=
```

## The ZenHub query looks up every open bug, with the token in a private file

`issueType` is a union, so its name and level come through inline fragments.
Closed bugs are not looked up. The authorization header reaches `curl` only
through a file its owner alone can read.

```scrut
$ log="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && bugs STUB_CURL_LOG="${log}" gather "${work}/config.json" "${work}/logged.json" > /dev/null && grep -c '^  i[0-9]*: issueByInfo(repositoryGhId: 101, ' "${log}" && grep -E '^ *\.\.\. on (Github|Zenhub)IssueType' "${log}" && grep '^header matches' "${log}"
20
    ... on GithubIssueType {
    ... on ZenhubIssueType {
header matches: true, mode 600
```

## ZenHub state joins each bug, and the active sprint marks its members

```scrut
$ jq -r '.zenhub.activeSprint.name, (.bugs[] | select(.zenhub != null) | "#\(.number) \(.zenhub.pipeline) sprint=\(.zenhub.sprint) level=\(.zenhub.level)")' "${work}/gather.json"
Sprint: Oct 12 - Oct 26, 2026
#10 New Issues sprint=false level=4
#11 High Priority sprint=false level=null
#12 In Progress sprint=true level=null
#21 Must Do sprint=false level=null
#29 Product Backlog sprint=false level=3
```

## Without a ZenHub workspace, the gather never calls curl

```scrut
$ jq 'del(.zenhub)' "${work}/config.json" > "${work}/no-zenhub.json" && log="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && bugs STUB_CURL_LOG="${log}" gather "${work}/no-zenhub.json" "${work}/no-zenhub-gather.json" > /dev/null && wc -c < "${log}" | tr -d ' ' && jq -c '[.zenhub, ([.bugs[] | .zenhub] | unique)]' "${work}/no-zenhub-gather.json"
0
[null,[null]]
```

## A missing ZenHub token stops the gather

```scrut
$ bugs BUGS_TEST_ZENHUB_TOKEN= gather "${work}/config.json" "${work}/no-token.json" 2>&1
bugs-gather: the ZenHub token variable BUGS_TEST_ZENHUB_TOKEN is not set
[1]
```

## A failed search stops the gather and names it

```scrut
$ bugs STUB_GH_GRAPHQL_FAIL=open-labels gather "${work}/config.json" "${work}/failed.json" 2>&1
bugs-gather: search-open-labels failed:
  gh: HTTP 502: Bad Gateway (https://api.github.com/graphql)
[1]
```

## Score places every open bug in one tier

Each fixture bug is built for one rule. `#24` is cosmetic and reaches Now only
through an `escalate` entry; `#25` reaches it because the triage note confirms
it on production; `#19`'s escalate has expired, so it stays with the internal
bugs. `#16` is due 2026-11-03, beyond the 14-day window, so it stays in Ready
with its approved, green fix.

```scrut
$ tiers "${work}/scored.json"
now: #11 #25 #10 #24
today: #14 #13 #12 #15
ready: #16/ship #18/ready-to-fix #27/in-progress #17/ready-to-fix #21/ready-to-fix #28/review
investigate: #20
later: #19 #26
parked: #23 #29 #22
fixed: #5 #6
```

## Score prints the check-in report

```scrut
$ bugs score "${work}/config.json" "${work}/gather.json" "${assessments}" "${work}/report.json"
Triage note: 5 entries, 1 expired
    - expired: 2026-10-01T08:00-04:00 escalate #19
- Now (4):
    - #11 [87] API v2 accepts unauthenticated writes
        public security exposure: Bug 11 in one sentence.
    - #25 [80] Opt-outs do not suppress adopted letters (set by triage: environment, evidence)
        hurting users on production: Bug 25 in one sentence.
    - #10 [77] Pledging crashes the app
        hurting users on production: Bug 10 in one sentence.
    - #24 [29] Footer link color is off
        escalated: Bug 24 in one sentence.
- Today (4):
    - #14 [80] Relinquish erases bundle membership
        worse with every event: Bug 14 in one sentence.
    - #13 [51] Partner pages drop campaigns with null flags (unconfirmed)
        confirm on production: Bug 13 in one sentence.
    - #12 [49] Token refresh bounces users to the dashboard (in progress: in In Progress)
        affecting users on production: Bug 12 in one sentence.
    - #15 [49] Reminder batch sends twice before the send window
        due 2026-10-20: Bug 15 in one sentence.
- Ready to go, top 8 above the fold (6):
    - #16 [94] Election day counts as past (in progress: fix #40)
    - #18 [61] A test break blocks the axios security update
    - #27 [59] Callback returns 500 for invalid logins (in progress: draft fix #42)
    - #17 [47] Auth0 forces near-daily sign-outs
    - #21 [39] Admin search returns 500 for long names
    - #28 [38] Profile form sends a request per keystroke (in progress: fix #43)
- Report: 1 to investigate, 2 can wait, 3 parked, 2 recently fixed
- Changes: none recorded; the cache held no earlier score
```

## Within a tier, bugs rank by urgency score

```scrut
$ jq -r '.tiers.now[] | "#\(.number) \(.score)"' "${work}/scored.json"
#11 87
#25 80
#10 77
#24 29
```

## Signals name their source and what each says

```scrut
$ jq -r '.tiers.now[] | select(.number == 11 or .number == 25) | "#\(.number)", (.signals[] | "  \(.source) \(.kind): \(.text)")' "${work}/scored.json"
#11
  assessment impact: security for the public, reach all
  assessment evidence: found in source on production
  assessment workaround: no workaround
  zenhub pipeline: in High Priority
#25
  assessment impact: data loss for the public, reach all
  assessment evidence: reported by users on production
  assessment workaround: no workaround
  triage set: two donors reported it
```

## A deadline inside the window places a bug in Today

`#15` is due 2026-10-20, five days after the gather.

```scrut
$ jq -r '.tiers.today[] | select(.number == 15) | "#\(.number) \(.why)"' "${work}/scored.json"
#15 due 2026-10-20
```

## The triage note records its entries and flags the expired one

```scrut
$ jq -r '.triage.entries[] | "\(.id)\(if .expired then " (expired)" else "" end)"' "${work}/scored.json"
2026-10-14T09:00-04:00 escalate #24
2026-10-14T09:00-04:00 snooze #23
2026-10-14T09:05-04:00 set #25
2026-10-13T08:00-04:00 context
2026-10-01T08:00-04:00 escalate #19 (expired)
```

## Malformed triage entries are reported, not applied

```scrut
$ note="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '%s\n' '- 2026-10-14T09:00-04:00 snooze #23: no date' '- 2026-10-14T09:00-04:00 pin #10: a focus verb' '- 2026-10-14T09:00-04:00 set #10 severity=high: not a field' '- 2026-10-14T09:00-04:00 set #10 impact=huge: not in the set' '- 2026-10-14T09:00-04:00 park #10 until 2026-11-01: park takes no date' '- 2026-10-20T09:00-04:00 escalate #10: later than the score' '- 2026-10-14T09:00-04:00 escalate #99: not on the board' > "${note}" && config_with ".triageNote = \"${note}\"" > "${work}/bad-note.json" && bugs score "${work}/bad-note.json" "${work}/gather.json" "${assessments}" "${work}/bad-note-scored.json" | grep -E '^    - problem: '
    - problem: line 1: snooze needs an until date
    - problem: line 2: expected escalate, set, snooze, park, or context: - 2026-10-14T09:00-04:00 pin #10: a focus verb
    - problem: line 3: severity is not an assessment field
    - problem: line 4: impact must be one of security, data-loss, money, access, core-flow, degraded, cosmetic, internal, unknown
    - problem: line 5: park lasts until the note changes and takes no until date; use snooze
    - problem: line 6: 2026-10-20T09:00-04:00 is later than this score
    - problem: 2026-10-14T09:00-04:00 escalate #99 names a bug outside this board
```

## A snooze ends at the start of the day after its date, in the repository time zone

At 2026-10-15T03:30Z it is still 2026-10-14 in New York, so a snooze until
2026-10-14 holds; by 2026-10-15T04:30Z the local day has turned and it has
expired.

```scrut
$ note="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '%s\n' '- 2026-10-14T09:00-04:00 snooze #10 until 2026-10-14: wait for the release' > "${note}" && config_with ".triageNote = \"${note}\"" > "${work}/snooze.json" && for at in 2026-10-15T03:30:00Z 2026-10-15T04:30:00Z; do jq --arg at "${at}" '.gatheredAt = $at' "${work}/gather.json" > "${work}/snooze-gather.json" && bugs BUGS_GATHER_NOW="${at}" score "${work}/snooze.json" "${work}/snooze-gather.json" "${assessments}" "${work}/snooze-scored.json" > /dev/null && jq -r --arg at "${at}" '"\($at): #10 \([.tiers | to_entries[] | select(.value | any(.number == 10)) | .key] | first)"' "${work}/snooze-scored.json"; done
2026-10-15T03:30:00Z: #10 parked
2026-10-15T04:30:00Z: #10 now
```

## Score refuses assessments that do not cover the gather

A missing assessment, one older than its bug, and one outside the closed sets
each stop the score, all listed at once.

```scrut
$ jq 'map(select(.number != 20)) | map(if .number == 21 then .updatedAt = "2026-10-01T00:00:00Z" elif .number == 22 then .impact = "severe" | .gist = "" else . end)' "${assessments}" > "${work}/bad-assessments.json" && bugs score "${work}/config.json" "${work}/gather.json" "${work}/bad-assessments.json" "${work}/bad-scored.json" 2>&1 | sed "s|${work}|WORK|g"
bugs-gather: WORK/bad-assessments.json does not cover the gather:
  - #20: no assessment; read it
  - #21: assessed at updatedAt 2026-10-01T00:00:00Z, but the bug was updated at 2026-10-10T12:00:00Z; read it again
  - #22: impact must be one of security, data-loss, money, access, core-flow, degraded, cosmetic, internal, unknown
  - #22: gist is required
```

## Reuse on a cold cache lists every open bug to read

```scrut
$ bugs reuse "${work}/config.json" "${work}/gather.json" "${work}/reused.json" | sed "s|${work}|WORK|g"
bugs-gather: reused 0 cached assessments in WORK/reused.json
Read these bugs and add their assessments: #10 #11 #12 #13 #14 #15 #16 #17 #18 #19 #20 #21 #22 #23 #24 #25 #26 #27 #28 #29
```

## Save stores the cache, and a warm gather reports that nothing moved

```scrut
$ bugs save "${work}/config.json" "${work}/gather.json" "${assessments}" "${work}/scored.json" 2>&1 | sed "s|${work}|WORK|g" && ls "${work}/cache/report-boards/bugs/github.com/acme/widgets" && bugs moved "${work}/config.json" "${work}/gather.json"
bugs-gather: saved the cache in WORK/cache/report-boards/bugs/github.com/acme/widgets
assessments.json
gather.json
scored.json
Previous gather: 2026-10-15T16:00:00Z
This gather: 2026-10-15T16:00:00Z

- Nothing moved.
```

## Reuse on a warm cache keeps every assessment that still matches its bug

`#12` changed after it was read, so it alone needs reading.

```scrut
$ jq '(.bugs[] | select(.number == 12) | .updatedAt) = "2026-10-15T15:00:00Z"' "${work}/gather.json" > "${work}/changed.json" && bugs reuse "${work}/config.json" "${work}/changed.json" "${work}/warm-reused.json" | sed "s|${work}|WORK|g"
bugs-gather: reused 19 cached assessments in WORK/warm-reused.json
Read these bugs and add their assessments: #12
```

## Moved reports new bugs, closures, comments, and fix changes

```scrut
$ jq '(.bugs[] | select(.number == 12)) |= (.lastComment = {author: "dave", at: "2026-10-15T15:00:00Z", outside: true} | .updatedAt = "2026-10-15T15:00:00Z") | (.bugs[] | select(.number == 28) | .fixes[0].checks) = "SUCCESS" | (.bugs[] | select(.number == 21)) |= (.state = "closed" | .stateReason = "COMPLETED") | .bugs += [{number: 30, title: "A new bug", state: "open", author: "erin", outsideReporter: true, labels: ["bug"], fixes: [], reactions: 0, updatedAt: "2026-10-15T15:30:00Z", lastComment: null, zenhub: null}]' "${work}/gather.json" > "${work}/moved.json" && bugs moved "${work}/config.json" "${work}/moved.json"
Previous gather: 2026-10-15T16:00:00Z
This gather: 2026-10-15T16:00:00Z

- New bugs:
    - #30 A new bug (by @erin, outside reporter)
- Closed:
    - #21 Admin search returns 500 for long names (completed)
- New comments:
    - #12 Token refresh bounces users to the dashboard (@dave, outside)
- Fix changed:
    - #28 Profile form sends a request per keystroke (#43 success, no review)
```

## A warm score reports what entered and left Now and Today

```scrut
$ note="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cat "${BUGS_GATHER_DATA_DIR}/triage.md" > "${note}" && printf '%s\n' '- 2026-10-15T10:00-04:00 park #10: fixed by the hotfix deploy' '- 2026-10-15T10:00-04:00 escalate #21: the admin team is blocked' >> "${note}" && config_with ".triageNote = \"${note}\"" > "${work}/warm.json" && bugs score "${work}/warm.json" "${work}/gather.json" "${assessments}" "${work}/warm-scored.json" | grep -E '^- (Entered|Left|Moved)'
- Entered Now or Today: #21 ready to now
- Left Now or Today: #10 now to parked
```

## Save refuses a score from a different gather

```scrut
$ jq '.gatheredAt = "2026-10-14T16:00:00Z"' "${work}/scored.json" > "${work}/other-scored.json" && bugs save "${work}/config.json" "${work}/gather.json" "${assessments}" "${work}/other-scored.json" 2>&1 | sed "s|${work}|WORK|g"
bugs-gather: WORK/other-scored.json was not scored from WORK/gather.json
```

## A repository with no config uses the defaults

Named as `OWNER/NAME` with no config file, the gather searches the `bug` label
and the Bug type and skips ZenHub.

```scrut
$ log="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && bugs STUB_GH_LOG="${log}" gather acme/widgets "${work}/default.json" > /dev/null && grep -c ' search ' "${log}" && jq -c '.zenhub' "${work}/default.json"
4
null
```

## An invalid config lists every problem

```scrut
$ printf '%s\n' '{"repo": "acme", "bugLabels": [], "recentDays": 0, "zenhub": {"workspace": "ws 1"}, "weights": {"impact": {"security": "high"}}}' > "${work}/bad-config.json" && bugs gather "${work}/bad-config.json" "${work}/bad.json" 2>&1 | sed "s|${work}|WORK|g"
bugs-gather: WORK/bad-config.json is not a valid bugs config:
  - repo: expected owner/name
  - bugLabels: expected a non-empty list of label names
  - recentDays: expected a positive whole number of days
  - weights: expected numbers, grouped as the defaults are
  - zenhub.workspace: expected the workspace ID
  - zenhub.tokenVariable: expected the name of the environment variable holding the token
```

## A config for another repository is refused

```scrut
$ mkdir -p "${work}/config/report-boards/bugs/github.com/acme" && jq '.repo = "acme/gadgets"' "${work}/config.json" > "${work}/config/report-boards/bugs/github.com/acme/widgets.json" && bugs gather acme/widgets "${work}/mismatch.json" 2>&1 | sed "s|${work}|WORK|g"
bugs-gather: WORK/config/report-boards/bugs/github.com/acme/widgets.json is not a valid bugs config:
  - repo: the config names acme/gadgets, not acme/widgets
```

## Usage errors

```scrut
$ bugs score "${work}/config.json" 2>&1 | head -1
bugs-gather: score takes a repository, a gather file, an assessments file, and an output path
```

```scrut
$ bugs frobnicate 2>&1 | head -1
bugs-gather: unknown command: frobnicate
```

```scrut
$ bugs gather not-a-repo "${work}/x.json" 2>&1
bugs-gather: expected OWNER/NAME or a config file, not not-a-repo
[1]
```
