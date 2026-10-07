# Bugs gather

Tests for the `bugs-gather` script that `publish-report-board` bundles. It
searches one repository for its open and recently closed bugs, adds their
ZenHub state, places every open bug in a tier from the model's assessments and
the triage note, and keeps a per-repository cache so a later sync can say what
moved and which bugs need reading again.

Every call goes through `tests/fixtures/gh-stub` and `tests/fixtures/curl-stub`,
which answer from `tests/data/bugs-gather/`. The fixtures describe `acme/widgets`
(ZenHub ID 101) with 20 open bugs, built so that between them they reach every
tier, and 2 closed in the last week. The config names a test-only token
variable holding a sample value, and the Makefile unsets the real ZenHub token
variable, so no test can reach ZenHub. `bugs` takes settings (`NAME=value`) first, then the
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

Each fixture bug is built for one rule. `#24` is cosmetic and reaches Critical only
through an `escalate` entry; `#25` reaches it because the triage note confirms
it on production; `#19`'s escalate has expired, so it stays with the internal
bugs. `#16` is due 2026-11-03, beyond the 14-day window, so it stays in Ready
with its approved, green fix.

```scrut
$ tiers "${work}/scored.json"
critical: #11 #25 #10 #24
high: #14 #13 #12 #15
ready: #16/ship #18/ready-to-fix #27/in-progress #17/ready-to-fix #21/ready-to-fix #28/review
investigate: #20
lower: #19 #26
parked: #23 #29 #22
fixed: #5 #6
```

## Score prints the check-in report

```scrut
$ bugs score "${work}/config.json" "${work}/gather.json" "${assessments}" "${work}/report.json"
Triage note: 5 entries, 1 expired
    - expired: 2026-10-01T08:00-04:00 escalate #19
- Critical (4):
    - #11 [87] API v2 accepts unauthenticated writes
        public security exposure: Bug 11 in one sentence.
    - #25 [80] Opt-outs do not suppress adopted letters (set by triage: environment, evidence)
        hurting users on production: Bug 25 in one sentence.
    - #10 [77] Pledging crashes the app
        hurting users on production: Bug 10 in one sentence.
    - #24 [29] Footer link color is off
        escalated: Bug 24 in one sentence.
- High priority (4):
    - #14 [80] Relinquish erases bundle membership
        worse with every event: Bug 14 in one sentence.
    - #13 [51] Partner pages drop campaigns with null flags (unconfirmed)
        confirm on production: Bug 13 in one sentence.
    - #12 [49] Token refresh bounces users to the dashboard (in progress: the In Progress pipeline)
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
- Report: 1 to investigate, 2 lower priority, 3 parked, 2 fixed
- Changes: none recorded; the cache held no earlier score
```

## Within a tier, bugs rank by urgency score

```scrut
$ jq -r '.tiers.critical[] | "#\(.number) \(.score)"' "${work}/scored.json"
#11 87
#25 80
#10 77
#24 29
```

## Signals name their source and what each says

```scrut
$ jq -r '.tiers.critical[] | select(.number == 10 or .number == 11 or .number == 25) | "#\(.number)", (.signals[] | "  \(.source) \(.kind): \(.text)")' "${work}/scored.json"
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
#10
  assessment impact: money for the public, reach all
  assessment evidence: seen on production
  assessment workaround: no workaround
```

## A public security bug needs some evidence to reach Critical

`#11` is known from source, so it sits in Critical. With its evidence and environment `unknown`, as
for an audit nobody has run, it needs investigating instead.

```scrut
$ jq 'map(if .number == 11 then .evidence = "unknown" | .environment = "unknown" | .question = "Is the API reachable?" else . end)' "${assessments}" > "${work}/unverified.json" && bugs score "${work}/config.json" "${work}/gather.json" "${work}/unverified.json" "${work}/unverified-scored.json" > /dev/null && jq -r '[.tiers | to_entries[] | select(.value | any(.number == 11)) | .key] | first' "${work}/unverified-scored.json"
investigate
```

## A deadline inside the window places a bug in High priority

`#15` is due 2026-10-20, five days after the gather.

```scrut
$ jq -r '.tiers.high[] | select(.number == 15) | "#\(.number) \(.why)"' "${work}/scored.json"
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
$ note="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '%s\n' '- 2026-10-14T09:00-04:00 snooze #23: no date' '- 2026-10-14T09:00-04:00 pin #10: a focus verb' '- 2026-10-14T09:00-04:00 set #10 severity=high: not a field' '- 2026-10-14T09:00-04:00 set #10 impact=huge: not in the set' '- 2026-10-14T09:00-04:00 park #10 until 2026-11-01: park takes no date' '- 2026-10-20T09:00-04:00 escalate #10: later than the score' '- 2026-10-14T09:00-04:00 escalate #99: not on the board' '- 2026-10-14T09:00-04:00 set #10 mitigated=yes: hotfix deployed' '* 2026-10-14T09:00-04:00 escalte #12: a star marker' '  - 2026-10-14T09:00-04:00 escalte #13: an indented entry' '- 2026-10-14T09:00-04:00 escalate #12: written once' '- 2026-10-14T09:00-04:00 escalate #12: and again' '1. 2026-10-14T09:00-04:00 escalate #14: a numbered entry' > "${note}" && config_with ".triageNote = \"${note}\"" > "${work}/bad-note.json" && bugs score "${work}/bad-note.json" "${work}/gather.json" "${assessments}" "${work}/bad-note-scored.json" | grep -E '^    - problem: '
    - problem: line 1: snooze needs an until date
    - problem: line 2: expected escalate, demote, set, snooze, park, or context: - 2026-10-14T09:00-04:00 pin #10: a focus verb
    - problem: line 3: severity is not an assessment field
    - problem: line 4: impact must be one of security, data-loss, money, access, core-flow, degraded, cosmetic, internal, unknown
    - problem: line 5: park lasts until the note changes and takes no until date; use snooze
    - problem: line 6: 2026-10-20T09:00-04:00 is later than this score
    - problem: line 8: mitigated must be true or false
    - problem: line 9: expected escalate, demote, set, snooze, park, or context: * 2026-10-14T09:00-04:00 escalte #12: a star marker
    - problem: line 10: expected escalate, demote, set, snooze, park, or context:   - 2026-10-14T09:00-04:00 escalte #13: an indented entry
    - problem: line 13: start a triage entry with -, not a number: 1. 2026-10-14T09:00-04:00 escalate #14: a numbered entry
    - problem: entry 2026-10-14T09:00-04:00 escalate #12 appears more than once
    - problem: 2026-10-14T09:00-04:00 escalate #99 names a bug outside this board
```

## A snooze ends at the start of the day after its date, in the repository time zone

At 2026-10-15T03:30Z it is still 2026-10-14 in New York, so a snooze until
2026-10-14 holds; by 2026-10-15T04:30Z the local day has turned and it has
expired.

```scrut
$ note="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '%s\n' '- 2026-10-14T09:00-04:00 snooze #10 until 2026-10-14: wait for the release' > "${note}" && config_with ".triageNote = \"${note}\"" > "${work}/snooze.json" && for at in 2026-10-15T03:30:00Z 2026-10-15T04:30:00Z; do jq --arg at "${at}" '.gatheredAt = $at' "${work}/gather.json" > "${work}/snooze-gather.json" && bugs BUGS_GATHER_NOW="${at}" score "${work}/snooze.json" "${work}/snooze-gather.json" "${assessments}" "${work}/snooze-scored.json" > /dev/null && jq -r --arg at "${at}" '"\($at): #10 \([.tiers | to_entries[] | select(.value | any(.number == 10)) | .key] | first)"' "${work}/snooze-scored.json"; done
2026-10-15T03:30:00Z: #10 parked
2026-10-15T04:30:00Z: #10 critical
```

## Score refuses assessments that do not cover the gather

A missing assessment, one older than its bug, and one outside the closed sets
each stop the score, all listed at once.

```scrut
$ jq 'map(select(.number != 20)) + [(.[] | select(.number == 11))] | map(if .number == 23 then .reproduced = "no" else . end) | map(if .number == 21 then .updatedAt = "2026-10-01T00:00:00Z" elif .number == 22 then .impact = "severe" | .gist = "" else . end)' "${assessments}" > "${work}/bad-assessments.json" && bugs score "${work}/config.json" "${work}/gather.json" "${work}/bad-assessments.json" "${work}/bad-scored.json" 2>&1 | sed "s|${work}|WORK|g"; echo "exit ${PIPESTATUS[0]}"
bugs-gather: WORK/bad-assessments.json does not cover the gather:
  - #20: no assessment; read it
  - #21: assessed at updatedAt 2026-10-01T00:00:00Z, but the bug was updated at 2026-10-10T12:00:00Z; read it again
  - #22: impact must be one of security, data-loss, money, access, core-flow, degraded, cosmetic, internal, unknown
  - #22: gist is required
  - #23: reproduced must be true, false, or null
  - #11: assessed 2 times; keep one
exit 1
```

## Draft builds board data that lacks only its prose

Every placement, signal, and fact comes from the score, so `report-board`
rejects the draft for the summary and the Critical and High priority impacts alone.

```scrut
$ bugs draft "${work}/config.json" "${work}/gather.json" "${work}/scored.json" "${work}/board.json" | sed "s|${work}|WORK|g" && "${REPORT_BOARD_BIN}" validate "${work}/board.json" 2>&1 | grep -c '^  - ' && "${REPORT_BOARD_BIN}" validate "${work}/board.json" 2>&1 | grep '^  - ' | grep -v 'impact is required\|^  - summary: ' | wc -l | tr -d ' '
bugs-gather: drafted WORK/board.json; write summary, and impact for each Critical and High priority entry, before validating
9
0
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

## A warm score reports what entered and left Critical and High priority

```scrut
$ note="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cat "${BUGS_GATHER_DATA_DIR}/triage.md" > "${note}" && printf '%s\n' '- 2026-10-15T10:00-04:00 park #10: fixed by the hotfix deploy' '- 2026-10-15T10:00-04:00 escalate #21: the admin team is blocked' >> "${note}" && config_with ".triageNote = \"${note}\"" > "${work}/warm.json" && bugs score "${work}/warm.json" "${work}/gather.json" "${assessments}" "${work}/warm-scored.json" | grep -E '^- (Entered|Left|Moved)'
- Entered Critical or High priority: #21 ready to critical
- Left Critical or High priority: #10 critical to parked
```

## Save refuses a score from a different gather

```scrut
$ jq '.gatheredAt = "2026-10-14T16:00:00Z"' "${work}/scored.json" > "${work}/other-scored.json" && bugs save "${work}/config.json" "${work}/gather.json" "${assessments}" "${work}/other-scored.json" 2>&1 | sed "s|${work}|WORK|g"; echo "exit ${PIPESTATUS[0]}"
bugs-gather: WORK/other-scored.json was not scored from WORK/gather.json
exit 1
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
$ printf '%s\n' '{"repo": "acme", "bugLabels": [], "recentDays": 0, "zenhub": {"workspace": "ws 1", "tokenVarible": "ZH"}, "triageGit": {"gitDir": "a", "workTree": "b", "worktree": "c"}, "weights": {"impact": {"security": "high"}, "impcat": {}}, "triagenote": "triage.md"}' > "${work}/bad-config.json" && bugs gather "${work}/bad-config.json" "${work}/bad.json" 2>&1 | sed "s|${work}|WORK|g"; echo "exit ${PIPESTATUS[0]}"
bugs-gather: WORK/bad-config.json is not a valid bugs config:
  - repo: expected owner/name
  - bugLabels: expected a non-empty list of label names
  - recentDays: expected a positive whole number of days
  - weights.impact.security: expected a number
  - weights.impcat: not a weight; expected one of evidence, impact, reach, surface, pipelines, timeSensitive, mitigated, urgent, sprint, regression, outsidePerson, outsideCap, reaction, reactionCap
  - triagenote: not a config field; expected one of repo, timeZone, bugLabels, bugTypes, urgentLabels, regressionLabels, parkLabels, urgentPipelines, containerLevels, bots, recentDays, criticalWarn, readyLimit, deadlineDays, progressLabels, progressPipelines, weights, zenhub, triageNote, triageGit
  - triageGit.worktree: not a triageGit field; expected gitDir, workTree
  - zenhub.workspace: expected the workspace ID
  - zenhub.tokenVariable: expected the name of the environment variable holding the token
  - zenhub.tokenVarible: not a zenhub field; expected workspace, tokenVariable
exit 1
```

## A config for another repository is refused

```scrut
$ mkdir -p "${work}/config/report-boards/bugs/github.com/acme" && jq '.repo = "acme/gadgets"' "${work}/config.json" > "${work}/config/report-boards/bugs/github.com/acme/widgets.json" && bugs gather acme/widgets "${work}/mismatch.json" 2>&1 | sed "s|${work}|WORK|g"; echo "exit ${PIPESTATUS[0]}"
bugs-gather: WORK/config/report-boards/bugs/github.com/acme/widgets.json is not a valid bugs config:
  - repo: the config names acme/gadgets, not acme/widgets
exit 1
```

## A configured triage note that cannot be read stops the score

Scoring without it would drop every call in it and say nothing.

```scrut
$ config_with '.triageNote = "/nonexistent/triage.md"' > "${work}/lost-note.json" && bugs score "${work}/lost-note.json" "${work}/gather.json" "${assessments}" "${work}/lost-scored.json" 2>&1
bugs-gather: cannot read the triage note /nonexistent/triage.md; fix triageNote in the config, or restore the note
[1]
```

## A mitigated bug never reaches Critical

`#10` would be Critical, but a `set` entry records that its harm has been
stopped.

```scrut
$ note="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '%s\n' '- 2026-10-14T09:00-04:00 set #10 mitigated=true: the hotfix stopped the crashes' > "${note}" && config_with ".triageNote = \"${note}\"" > "${work}/mitigated.json" && bugs score "${work}/mitigated.json" "${work}/gather.json" "${assessments}" "${work}/mitigated-scored.json" > /dev/null && jq -r '[.tiers | to_entries[] | .key as $t | .value[] | select(.number == 10) | "#10 \($t): \(.why)"] | first' "${work}/mitigated-scored.json"
#10 ready: mitigated
```

## A demote entry moves a Critical bug to High priority

`#10` earns Critical on its facts; the latest call, a demote, places it in
High priority instead, and a later escalate would bring it back.

```scrut
$ note="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '%s\n' '- 2026-10-14T09:00-04:00 demote #10: letters go out in batches, so a fix this week is soon enough' > "${note}" && config_with ".triageNote = \"${note}\"" > "${work}/demoted.json" && bugs score "${work}/demoted.json" "${work}/gather.json" "${assessments}" "${work}/demoted-scored.json" > /dev/null && jq -r '[.tiers | to_entries[] | .key as $t | .value[] | select(.number == 10) | "#10 \($t): \(.why), \([.signals[] | select(.source == "triage") | .kind] | join(", "))"] | first' "${work}/demoted-scored.json"
#10 high: demoted, demote
```

## A deadline counts from the day of the sync through the window

The sync falls on 2026-10-15 and the window is 14 days. A deadline on the day
itself or at the edge of the window places `#15` in High priority; one past
the window, or already gone, does not.

```scrut
$ for deadline in 2026-10-14 2026-10-15 2026-10-29 2026-10-30; do jq --arg d "${deadline}" 'map(if .number == 15 then .deadline = $d else . end)' "${assessments}" > "${work}/deadline.json" && bugs score "${work}/config.json" "${work}/gather.json" "${work}/deadline.json" "${work}/deadline-scored.json" > /dev/null && jq -r --arg d "${deadline}" '"\($d): " + ([.tiers | to_entries[] | .key as $t | .value[] | select(.number == 15) | $t] | first)' "${work}/deadline-scored.json"; done
2026-10-14: ready
2026-10-15: high
2026-10-29: high
2026-10-30: ready
```

## A fixed bug that was on production carries a reminder to verify it

Reuse keeps the last assessment of a closed bug, and save keeps it in the
cache, so every sync in the window knows the fix went to production.

```scrut
$ cache="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && jq '. + [{number: 5, updatedAt: "2026-10-01T12:00:00Z", environment: "production", evidence: "user-report", surface: "signed-in", impact: "core-flow", reach: "some", workaround: "none", cause: "known", timeSensitive: false, deadline: null, mitigated: false, reproduced: null, gist: "Verify email returns 500.", nextStep: "Fix it.", question: null}]' "${assessments}" > "${work}/with-closed.json" && bugs XDG_CACHE_HOME="${cache}" save "${work}/config.json" "${work}/gather.json" "${work}/with-closed.json" "${work}/scored.json" 2> /dev/null && for sync in first second; do bugs XDG_CACHE_HOME="${cache}" reuse "${work}/config.json" "${work}/gather.json" "${work}/verify-reused.json" > /dev/null && bugs XDG_CACHE_HOME="${cache}" score "${work}/config.json" "${work}/gather.json" "${work}/verify-reused.json" "${work}/verify-scored.json" > /dev/null && bugs XDG_CACHE_HOME="${cache}" save "${work}/config.json" "${work}/gather.json" "${work}/verify-reused.json" "${work}/verify-scored.json" 2> /dev/null && jq -r --arg sync "${sync}" '"\($sync): " + (.tiers.fixed | map("#\(.number) verify=\(.verify)") | join(", "))' "${work}/verify-scored.json"; done
first: #5 verify=true, #6 verify=false
second: #5 verify=true, #6 verify=false
```

## A cache file that cannot be read is named, not taken for a first sync

```scrut
$ cache="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && mkdir -p "${cache}/report-boards/bugs/github.com/acme/widgets" && printf 'not json' > "${cache}/report-boards/bugs/github.com/acme/widgets/assessments.json" && bugs XDG_CACHE_HOME="${cache}" reuse "${work}/config.json" "${work}/gather.json" "${work}/corrupt-reused.json" 2>&1 | head -2 | sed -e "s|${cache}|CACHE|g" -e "s|${work}|WORK|g"
bugs-gather: ignoring CACHE/report-boards/bugs/github.com/acme/widgets/assessments.json: it is unreadable or was written by another version of bugs-gather
bugs-gather: reused 0 cached assessments in WORK/corrupt-reused.json
```

## Bugs ZenHub does not track are listed, and the gather goes on

```scrut
$ bugs gather "${work}/config.json" "${work}/listed.json" 2>&1 > /dev/null | head -3
bugs-gather: these bugs have no ZenHub state, so they carry no pipeline, sprint, or container level:
  - #13: Issue not found
  - #14: Issue not found
```

## ZenHub returning no state for any bug stops the gather

A wrong workspace or repository ID answers every lookup with an error, and a
board ranked without any ZenHub state would mislead.

```scrut
$ empty="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${BUGS_GATHER_DATA_DIR}/zenhub/workspace.json" "${empty}/" && bugs STUB_CURL_DIR="${empty}" gather "${work}/config.json" "${work}/no-state.json" 2>&1 | head -2; echo "exit ${PIPESTATUS[0]}"
bugs-gather: ZenHub returned no state for any of the 20 open bugs, so the workspace or the repository is wrong:
  - #10: Issue not found
exit 1
```

## A ZenHub error inside a lookup stops the gather

An error on a field, such as a permission problem on the blocking issues, is
not an untracked issue, and dropping its state would hide it.

```scrut
$ bugs STUB_CURL_ERROR="Not authorized to read blockingIssues" gather "${work}/config.json" "${work}/field-error.json" 2>&1
bugs-gather: ZenHub returned errors:
  Not authorized to read blockingIssues (at i0.blockingIssues)
[1]
```

## A failed ZenHub request stops the gather

```scrut
$ bugs STUB_CURL_FAIL=1 gather "${work}/config.json" "${work}/zenhub-down.json" 2>&1 | head -2; echo "exit ${PIPESTATUS[0]}"
bugs-gather: the ZenHub request failed:
  curl: (22) The requested URL returned error: 500
exit 1
```

## A search GitHub cut short stops the gather

GitHub search stops at 1000 results and then reports no further page, so the
gather compares what it collected with what the search counted.

```scrut
$ capped="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp -R "${BUGS_GATHER_DATA_DIR}/github/." "${capped}/" && jq 'map(.data.search.issueCount = 1240)' "${BUGS_GATHER_DATA_DIR}/github/graphql/search-open-labels.json" > "${capped}/graphql/search-open-labels.json" && bugs STUB_GH_DIR="${capped}" gather "${work}/config.json" "${work}/capped.json" 2>&1
bugs-gather: the open-labels search returned 19 of 1240 issues; GitHub search stops at 1000, so narrow bugLabels or bugTypes, or run gather again if the bugs changed while it read them
[1]
```

## A search that comes back without a count stops the gather

```scrut
$ uncounted="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp -R "${BUGS_GATHER_DATA_DIR}/github/." "${uncounted}/" && jq 'map(del(.data.search.issueCount))' "${BUGS_GATHER_DATA_DIR}/github/graphql/search-open-labels.json" > "${uncounted}/graphql/search-open-labels.json" && bugs STUB_GH_DIR="${uncounted}" gather "${work}/config.json" "${work}/uncounted.json" 2>&1
bugs-gather: the open-labels search came back without a result count, so its results cannot be trusted
[1]
```

## ZenHub lists cut short are listed, and the gather goes on

```scrut
$ cut="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${BUGS_GATHER_DATA_DIR}/zenhub/"*.json "${cut}/" && jq '.sprints.pageInfo = {hasNextPage: true}' "${BUGS_GATHER_DATA_DIR}/zenhub/101-12.json" > "${cut}/101-12.json" && bugs STUB_CURL_DIR="${cut}" gather "${work}/config.json" "${work}/cut.json" 2>&1 > /dev/null | grep -A1 'ZenHub cut'
bugs-gather: ZenHub cut these lists short, so a sprint or a blocking issue past the cut is missing:
  - #12: sprints
```

## An archived repository stops the gather

```scrut
$ archived="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp -R "${BUGS_GATHER_DATA_DIR}/github/." "${archived}/" && jq '.data.repository.isArchived = true' "${BUGS_GATHER_DATA_DIR}/github/graphql/repository-widgets.json" > "${archived}/graphql/repository-widgets.json" && bugs STUB_GH_DIR="${archived}" gather "${work}/config.json" "${work}/archived.json" 2>&1
bugs-gather: acme/widgets is archived; its bugs cannot change, so there is nothing to sync
[1]
```

## Problems with the triage note travel into the draft, which validation refuses

The malformed note above scores, but the board built from that score cannot
validate until the note is fixed.

```scrut
$ bugs draft "${work}/bad-note.json" "${work}/gather.json" "${work}/bad-note-scored.json" "${work}/bad-note-board.json" > /dev/null && jq '.summary = "x" | (.critical[], .high[]) |= (.impact = "x")' "${work}/bad-note-board.json" > "${work}/bad-note-filled.json" && "${REPORT_BOARD_BIN}" validate "${work}/bad-note-filled.json" 2>&1 | grep -c '^  - triage note: '; echo "exit ${PIPESTATUS[0]}"
12
exit 1
```

## A suspected cause or a failed reproduction needs investigating

`#21` has a known cause and sits in Ready to go; a suspected cause, or a
report that it would not reproduce, moves it to Needs investigation.

```scrut
$ for change in '.cause = "suspected"' '.reproduced = false'; do jq "map(if .number == 21 then ${change} | .question = \"What fails?\" else . end)" "${assessments}" > "${work}/trigger.json" && bugs score "${work}/config.json" "${work}/gather.json" "${work}/trigger.json" "${work}/trigger-scored.json" > /dev/null && jq -r '[.tiers | to_entries[] | .key as $t | .value[] | select(.number == 21) | "#21 \($t): \(.why)"] | first' "${work}/trigger-scored.json"; done
#21 investigate: cause suspected
#21 investigate: not reproduced
```

## Save keeps a closed bug's cached assessment even when it is not given one

```scrut
$ cache="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && bugs XDG_CACHE_HOME="${cache}" save "${work}/config.json" "${work}/gather.json" "${work}/with-closed.json" "${work}/scored.json" 2> /dev/null && bugs XDG_CACHE_HOME="${cache}" save "${work}/config.json" "${work}/gather.json" "${assessments}" "${work}/scored.json" 2> /dev/null && jq -r '[.[] | select(.number == 5) | "#5 kept: \(.environment)"] | first // "#5 lost"' "${cache}/report-boards/bugs/github.com/acme/widgets/assessments.json"
#5 kept: production
```

## Cache files of the wrong shape are named and set aside

A scored cache without tiers, or an assessments cache whose entries carry no
bug number, would otherwise reach the filters.

```scrut
$ cache="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && dir="${cache}/report-boards/bugs/github.com/acme/widgets" && mkdir -p "${dir}" && printf '[{"foo": 1}]' > "${dir}/assessments.json" && printf '{"version": 2}' > "${dir}/scored.json" && { bugs XDG_CACHE_HOME="${cache}" reuse "${work}/config.json" "${work}/gather.json" "${work}/shape-reused.json" 2>&1 > /dev/null; bugs XDG_CACHE_HOME="${cache}" score "${work}/config.json" "${work}/gather.json" "${assessments}" "${work}/shape-scored.json" 2>&1 > /dev/null; } | sed "s|${cache}|CACHE|g"
bugs-gather: ignoring CACHE/report-boards/bugs/github.com/acme/widgets/assessments.json: it is unreadable or was written by another version of bugs-gather
bugs-gather: ignoring CACHE/report-boards/bugs/github.com/acme/widgets/scored.json: it is unreadable or was written by another version of bugs-gather
```

## Labels or fixes GitHub cut short are listed, and the gather goes on

```scrut
$ capped="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp -R "${BUGS_GATHER_DATA_DIR}/github/." "${capped}/" && jq 'map((.data.search.nodes[] | select(.number == 12) | .labels.pageInfo) = {hasNextPage: true})' "${BUGS_GATHER_DATA_DIR}/github/graphql/search-open-labels.json" > "${capped}/graphql/search-open-labels.json" && bugs STUB_GH_DIR="${capped}" gather "${work}/config.json" "${work}/labels-cut.json" 2>&1 > /dev/null | grep -A1 'GitHub cut'; echo "exit ${PIPESTATUS[0]}"
bugs-gather: GitHub cut these lists short, so a label or a fix past the cut is missing:
  - #12: labels
exit 0
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
