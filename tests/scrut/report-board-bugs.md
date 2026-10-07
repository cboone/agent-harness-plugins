# Report board: bugs boards

Tests for how `report-board` validates and compares `bugs` board data. The
fixture `bugs.json` is the board `bugs-gather draft` builds from the
`bugs-gather` test fixtures, with its summary and impacts written in: 22 bugs
for `acme/widgets`, 20 open and 2 recently closed, synced at
2026-10-15T16:00:00Z in America/New_York. Each case changes one thing with
`jq` and checks the message.

```scrut
$ function board_with() {
>   local out
>   out="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")"
>   jq "${1}" "${REPORT_BOARD_DATA_DIR}/bugs.json" > "${out}"
>   printf '%s' "${out}"
> }
> function problems() {
>   "${REPORT_BOARD_BIN}" validate "$(board_with "${1}")" 2>&1 | grep '^  - '
> }
```

## Valid data passes validation with a bugs summary

```scrut
$ "${REPORT_BOARD_BIN}" validate "${REPORT_BOARD_DATA_DIR}/bugs.json" 2>&1
report-board: */bugs.json is valid: 4 critical, 4 high priority, 20 open bugs (glob)
```

## A draft names every piece of prose still to write

`bugs-gather draft` leaves the summary and each Critical and High priority impact empty.

```scrut
$ problems '.summary = null | (.critical[], .high[]) |= (.impact = null)'
  - summary: expected text summarizing the board
  - critical #11: impact is required, who is affected and how
  - critical #25: impact is required, who is affected and how
  - critical #10: impact is required, who is affected and how
  - critical #24: impact is required, who is affected and how
  - high #14: impact is required, who is affected and how
  - high #13: impact is required, who is affected and how
  - high #12: impact is required, who is affected and how
  - high #15: impact is required, who is affected and how
```

## Every bug sits in exactly one section that matches its tier

```scrut
$ problems '.lower |= map(select(.item != 26)) | .investigate += [{item: 19, why: "x", question: "y?", signals: []}] | (.bugs[] | select(.number == 21) | .tier) = "high"'
  - ready #21: the bug is placed in high
  - investigate #19: the bug is placed in lower
  - #19 appears in more than one section
  - #26 is not in any section; every bug in the gather belongs to exactly one
```

## A Critical entry needs an escalate entry or an assessment that earns it

`#26` is a cosmetic bug with a workaround, so moving it to Critical without an
`escalate` entry breaks the rule `bugs-gather` applies.

```scrut
$ problems '.lower |= map(select(.item != 26)) | (.bugs[] | select(.number == 26) | .tier) = "critical" | .critical += [{item: 26, why: "x", action: "Fix it.", impact: "Few notice.", signals: [{source: "github", kind: "label", text: "labeled bug", at: "2026-10-10T12:00:00Z"}]}]'
  - critical #26 has neither an escalate entry nor an assessment that earns Critical
```

## A snoozed bug stays out of Critical and High priority

`#23` is snoozed through 2026-11-10 by the triage note.

```scrut
$ problems '.parked |= map(select(.item != 23)) | (.bugs[] | select(.number == 23) | .tier) = "high" | .high += [{item: 23, why: "x", action: "Fix it.", impact: "Someone.", signals: [{source: "assessment", kind: "impact", text: "degraded", at: "2026-10-10T12:00:00Z"}]}]'
  - high #23 is snoozed by 2026-10-14T09:00-04:00 snooze #23; only a later escalate brings it back
```

## A triage signal must rest on an entry still in force

The escalate on `#19` expired on 2026-10-10.

```scrut
$ problems '(.critical[] | select(.item == 24) | .signals) += [{source: "triage", kind: "escalate", text: "x", at: "2026-10-01T08:00:00-04:00", entry: "2026-10-01T08:00-04:00 escalate #19"}, {source: "triage", kind: "escalate", text: "x", at: "2026-10-01T08:00:00-04:00", entry: "2026-10-02T08:00-04:00 escalate #24"}]'
  - critical #24 signals[3]: entry 2026-10-01T08:00-04:00 escalate #19 expired on 2026-10-10
  - critical #24 signals[4]: entry 2026-10-02T08:00-04:00 escalate #24 is not in triage
```

## No signal is later than the sync

```scrut
$ problems '(.critical[0].signals[0].at) = "2026-10-16T00:00:00Z"'
  - critical #11 signals[0]: at 2026-10-16T00:00:00Z is later than sync.at
```

## No triage entry is later than the sync

```scrut
$ problems '.triage += [{id: "2026-10-16T09:00-04:00 context", at: "2026-10-16T09:00-04:00", verb: "context", target: null, until: null, text: "written after the sync"}]'
  - triage[5]: at 2026-10-16T09:00-04:00 is later than sync.at
```

## Assessments use the closed sets

```scrut
$ problems '(.bugs[] | select(.number == 20) | .assessment) |= (.impact = "severe" | .mitigated = "no" | .gist = "")'
  - #20: assessment.impact must be one of security, data-loss, money, access, core-flow, degraded, cosmetic, internal, unknown
  - #20: assessment.mitigated must be true or false
  - #20: assessment.gist is required
```

## Ready groups, questions, and reasons are checked

```scrut
$ problems '(.ready[] | select(.item == 21) | .group) = "ship" | (.ready[] | select(.item == 18) | .group) = "soon" | (.investigate[0].question) = null | (.lower[0].reason) = ""'
  - ready #18: group must be one of ship, review, in-progress, ready-to-fix
  - ready #21 is grouped as ship but names no fix pull request
  - investigate #20: question is required, what to learn first
  - lower #19: reason is required
```

## Closed bugs belong in fixed, and open ones never do

```scrut
$ problems '(.bugs[] | select(.number == 5) | .tier) = "lower" | (.bugs[] | select(.number == 26) | .tier) = "fixed"'
  - #5 is closed, so its tier is fixed
  - #26 is open, so it cannot be in fixed
  - lower #26: the bug is placed in fixed
  - fixed #5: the bug is placed in lower
```

## A closed bug's fixes and reason have the shapes the page draws

```scrut
$ problems '(.bugs[] | select(.number == 5)) |= (.fixedBy = "41" | .stateReason = 3)'
  - #5: fixedBy must be a list of pull request numbers
  - #5: stateReason must be text or null
```

## Triage entries follow the note grammar

```scrut
$ problems '.triage += [{id: "wrong", at: "2026-10-14T09:00-04:00", verb: "snooze", target: 21, until: null, text: "x"}, {id: "2026-10-14T09:00-04:00 pin #21", at: "2026-10-14T09:00-04:00", verb: "pin", target: 21, text: "x"}, {id: "2026-10-14T09:00-04:00 set #21", at: "2026-10-14T09:00-04:00", verb: "set", target: 21, until: null, fields: {impact: "huge", severity: "high"}, text: "x"}]'
  - triage[5]: id must be "2026-10-14T09:00-04:00 snooze #21"
  - triage[5]: snooze needs an until date
  - triage[6]: verb must be escalate, demote, set, snooze, park, or context
  - triage[7]: impact must be one of security, data-loss, money, access, core-flow, degraded, cosmetic, internal, unknown
  - triage[7]: severity is not an assessment field
```

## A bugs board needs its time zone

```scrut
$ problems 'del(.sync.timeZone)'
  - sync.timeZone: required on a bugs board, because triage until dates count in its local days
```

## Compare reports nothing when the board is unchanged

```scrut
$ "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/bugs.json" "${REPORT_BOARD_DATA_DIR}/bugs.json"
Previous sync: main at 01234567, 2026-10-15T16:00:00Z in America/New_York, ZenHub workspace ws123, closed bugs from the last 7 days
This sync: main at 01234567, 2026-10-15T16:00:00Z in America/New_York, ZenHub workspace ws123, closed bugs from the last 7 days

- No changes beyond the sync metadata.
```

## Compare reports what entered and left Critical and High priority, and what else moved

The current board parks `#10`, escalates `#21`, opens `#30`, closes `#28`,
confirms `#13` on production, and rewords the summary.

```scrut
$ current="$(board_with '
>   .triage += [{id: "2026-10-15T10:00-04:00 park #10", at: "2026-10-15T10:00-04:00", verb: "park", target: 10, until: null, text: "fixed by the hotfix"}]
>   | .critical |= map(select(.item != 10)) | .parked += [{item: 10, reason: "parked: fixed by the hotfix"}] | (.bugs[] | select(.number == 10) | .tier) = "parked"
>   | .ready |= map(select(.item != 21 and .item != 28)) | .critical += [{item: 21, why: "escalated", action: "Fix it.", impact: "Admins.", signals: [{source: "triage", kind: "escalate", text: "x", at: "2026-10-15T10:00:00-04:00", entry: "2026-10-15T10:05-04:00 escalate #21"}]}] | (.bugs[] | select(.number == 21) | .tier) = "critical"
>   | .bugs += [{number: 30, title: "A new bug", state: "open", tier: "investigate", assessment: {}}] | .investigate += [{item: 30, why: "x", question: "y?"}]
>   | (.bugs[] | select(.number == 28)) |= (.state = "closed" | .tier = "fixed") | .fixed += [{item: 28, verify: false}]
>   | (.bugs[] | select(.number == 13) | .assessment) |= (.environment = "production" | .evidence = "user-report")
>   | .summary = "A new summary."
> ')" && "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/bugs.json" "${current}"
Previous sync: main at 01234567, 2026-10-15T16:00:00Z in America/New_York, ZenHub workspace ws123, closed bugs from the last 7 days
This sync: main at 01234567, 2026-10-15T16:00:00Z in America/New_York, ZenHub workspace ws123, closed bugs from the last 7 days

- Entered Critical: #21 Admin search returns 500 for long names (ready to critical)
- Left Critical: #10 Pledging crashes the app (now parked)
- New bugs: #30 A new bug (investigate)
- Closed: #28 Profile form sends a request per keystroke
- Assessment changed: #13 Partner pages drop campaigns with null flags (environment unknown to production, evidence code-reading to user-report)
- Triage added: 2026-10-15T10:00-04:00 park #10
- Reworded: summary
```

## Compare reports a changed identity

```scrut
$ "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/bugs.json" "$(board_with '.title = "gadgets bugs"')" | grep '^- Changed board identity'
- Changed board identity: title (widgets bugs to gadgets bugs)
```

## Render draws a bugs board from its own template

```scrut
$ page="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/board.html" && "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/bugs.json" "${page}" 2>&1 | sed 's|to .*/board.html|to PAGE|' && head -n 1 "${page}" && grep -c 'Bug triage · ' "${page}" && ! grep -q __BOARD_ "${page}" && echo "no placeholders left"
report-board: rendered 4 critical, 4 high priority, 20 open bugs to PAGE
<title>widgets bugs</title>
1
no placeholders left
```

## The embedded bugs data survives a round trip

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/bugs.json" "${dir}/board.html" 2> /dev/null && jq -S . "${REPORT_BOARD_DATA_DIR}/bugs.json" > "${dir}/rendered.json" && "${REPORT_BOARD_BIN}" extract "${dir}/board.html" | jq -S . > "${dir}/extracted.json" && diff "${dir}/rendered.json" "${dir}/extracted.json" && echo identical
identical
```

## A board with nothing in Critical still validates and renders

An empty section draws its heading and one line, so an empty Critical reads as a
finding.

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && jq '.lower += [.critical[] | {item, reason: "cleared"}] | (.bugs[] | select(.tier == "critical") | .tier) = "lower" | .critical = []' "${REPORT_BOARD_DATA_DIR}/bugs.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" render "${dir}/data.json" "${dir}/board.html" 2>&1 | sed 's|to .*/board.html|to PAGE|'
report-board: rendered 0 critical, 4 high priority, 20 open bugs to PAGE
```

## Problems with the triage note keep the board from validating

`bugs-gather draft` carries them as `triageProblems`; a board published over
them would drop the calls they belong to without a word.

```scrut
$ problems '.triageProblems = ["line 4: expected escalate, demote, set, snooze, park, or context: - 2026-10-14T09:00-04:00 escalte #10: typo"]'
  - triage note: line 4: expected escalate, demote, set, snooze, park, or context: - 2026-10-14T09:00-04:00 escalte #10: typo; fix the note and score again
```

## A triage signal must rest on an entry with its verb, about its bug

```scrut
$ problems '(.critical[] | select(.item == 24) | .signals) += [{source: "triage", kind: "escalate", text: "x", at: "2026-10-13T08:00:00-04:00", entry: "2026-10-13T08:00-04:00 context"}, {source: "triage", kind: "snooze", text: "x", at: "2026-10-14T09:00:00-04:00", entry: "2026-10-14T09:00-04:00 snooze #23"}, {source: "triage", kind: "context", text: "x", at: "2026-10-13T08:00:00-04:00", entry: "2026-10-13T08:00-04:00 context"}]'
  - critical #24 signals[3]: entry 2026-10-13T08:00-04:00 context is a context entry, but the signal says escalate
  - critical #24 signals[4]: entry 2026-10-14T09:00-04:00 snooze #23 is about #23, not #24
  - critical #24 signals[5]: entry 2026-10-13T08:00-04:00 context names no bug
```

## A park entry keeps a bug out of Critical and High priority too

```scrut
$ problems '.triage += [{id: "2026-10-14T10:00-04:00 park #14", at: "2026-10-14T10:00-04:00", verb: "park", target: 14, until: null, text: "not worth fixing"}]'
  - high #14 is parked by 2026-10-14T10:00-04:00 park #14; only a later escalate brings it back
```

## The fields the page draws are required

```scrut
$ problems '(.bugs[] | select(.number == 21) | .assessment.nextStep) = null | (.ready[0].why) = "" | (.investigate[0].why) = null'
  - #21: assessment.nextStep is required
  - ready #16: why is required
  - investigate #20: why is required, what is not yet known
```

## Invalid data exits with status 1

The cases above read the problem lines through `grep`, which hides the exit
status, so this one checks it directly.

```scrut
$ "${REPORT_BOARD_BIN}" validate "$(board_with '.summary = null')" > /dev/null 2>&1
[1]
```

## A demoted bug stays out of Critical

```scrut
$ problems '.triage += [{id: "2026-10-14T10:00-04:00 demote #10", at: "2026-10-14T10:00-04:00", verb: "demote", target: 10, until: null, text: "soon enough"}]'
  - critical #10 is demoted by 2026-10-14T10:00-04:00 demote #10; only a later escalate brings it back
```
