# Report board

Tests for the `report-board` script that `publish-report-board` bundles. It
validates board data, writes it into a page template, reads it back out of a
rendered page, and compares two syncs.

## Valid data passes validation

```scrut
$ "${REPORT_BOARD_BIN}" validate "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" 2>&1
report-board: */backlog-triage.json is valid: 7 issues in 3 lanes (glob)
```

## Render reports what it wrote

```scrut
$ page="$(mktemp -d)/board.html" && "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${page}" 2>&1
report-board: rendered 7 issues in 3 lanes to */board.html (glob)
```

## Render fills both placeholders

```scrut
$ page="$(mktemp -d)/board.html" && "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${page}" 2> /dev/null && head -n 1 "${page}" && ! grep -q __BOARD_ "${page}" && echo "no placeholders left"
<title>widgets backlog</title>
no placeholders left
```

## The embedded data survives a round trip

A later re-sync reads the previous board back out of the published page, so
what `extract` returns must be exactly what `render` was given.

```scrut
$ page="$(mktemp -d)/board.html" && "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${page}" 2> /dev/null && diff <(jq -S . "${REPORT_BOARD_DATA_DIR}/backlog-triage.json") <("${REPORT_BOARD_BIN}" extract "${page}" | jq -S .) && echo identical
identical
```

## A title that holds the data placeholder

The title and the payload both come from board data, so a title carrying the
data placeholder must not capture the data slot.

```scrut
$ dir="$(mktemp -d)" && jq '.title = "widgets __BOARD_DATA__ backlog"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" render "${dir}/data.json" "${dir}/board.html" 2> /dev/null && head -n 1 "${dir}/board.html" && diff <(jq -S . "${dir}/data.json") <("${REPORT_BOARD_BIN}" extract "${dir}/board.html" | jq -S .) && echo identical
<title>widgets __BOARD_DATA__ backlog</title>
identical
```

## Markup in the data cannot escape

The title is HTML-escaped, and a `</script>` inside any string stays inside the
data element: the page still has exactly its two closing script tags.

```scrut
$ dir="$(mktemp -d)" && jq '.title = "a <b> & \"c\"" | .summary = "</script><script>alert(1)</script>"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" render "${dir}/data.json" "${dir}/board.html" 2> /dev/null && head -n 1 "${dir}/board.html" && grep -o '</script>' "${dir}/board.html" | wc -l | tr -d ' ' && "${REPORT_BOARD_BIN}" extract "${dir}/board.html" | jq -r .summary
<title>a &lt;b&gt; &amp; &quot;c&quot;</title>
2
</script><script>alert(1)</script>
```

## Standalone output is a complete document

```scrut
$ page="$(mktemp -d)/board.html" && "${REPORT_BOARD_BIN}" render --standalone "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${page}" 2> /dev/null && head -n 3 "${page}" && tail -n 1 "${page}"
<!DOCTYPE html>
<html lang="en">
<meta charset="utf-8">
</html>
```

## Unknown board type

```scrut
$ dir="$(mktemp -d)" && jq '.board = "ci-health"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" render "${dir}/data.json" "${dir}/board.html" 2>&1
report-board: no template for board type ci-health; available: backlog-triage
[1]
```

## Missing output directory

```scrut
$ "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" /nonexistent/dir/board.html 2>&1
report-board: directory /nonexistent/dir does not exist
[1]
```

## An issue outside every lane

This is the check that catches a re-sync which forgot a newly opened issue.

```scrut
$ dir="$(mktemp -d)" && jq '.lanes[0].issues -= [107]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #107 is not in any lane; every open issue belongs to exactly one
[1]
```

## A blocker that is no longer open

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 102) | .waitingOn) = [99]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #102 waits on #99, which is not an open issue on this board; drop it if it has closed, or name it as a reference
[1]
```

## A blocked issue without a reason

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 102)) |= del(.blockedBecause)' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #102: blockedBecause is required when waitingOn is set
[1]
```

## Blockers that are not issues on the board

A blocker can also be a pull request, a branch that has to merge, an issue in
another repository, or any linked page.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"pr": 12, "title": "palette API"}, {"branch": "feature/palette"}, {"ref": "example/themes#3"}, {"url": "https://example.com/spec", "label": "the color spec"}], "blockedBecause": "Needs the palette."}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is valid: 7 issues in 3 lanes (glob)
```

## Malformed blocker references

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"pr": "12"}, {"branch": "has space"}, {"ref": "themes#3"}, {"url": "http://example.com", "label": "spec"}, {"pr": 1, "branch": "x"}, "soon"], "blockedBecause": "x"}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #107: each waitingOn entry is an issue number or a reference object
  - #107: a waitingOn pr must be a pull request number
  - #107: a waitingOn branch must be a branch name
  - #107: a waitingOn ref must look like owner/repo#123
  - #107: a waitingOn url needs an https:// address with a host, and a label
  - #107: each waitingOn reference names exactly one of pr, branch, ref, or url
[1]
```

## A blocker URL with no host

`https://` followed straight by a path is not an address, and the Blocked
section would draw it as a link that reaches nothing.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"url": "https:///foo", "label": "spec"}], "blockedBecause": "x"}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #107: a waitingOn url needs an https:// address with a host, and a label
[1]
```

## A blocker URL with a port, a query, and a fragment

A blocker can point at any page, so the host is what validation requires; what
follows it is the page's own business.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"url": "https://specs.example.com:8443/a/b?v=2#top", "label": "spec"}], "blockedBecause": "x"}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is valid: 7 issues in 3 lanes (glob)
```

## A cross-repository reference to issue zero

GitHub has no issue zero, so `/issues/0` would reach nothing.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"ref": "example/themes#0"}], "blockedBecause": "x"}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #107: a waitingOn ref must look like owner/repo#123
[1]
```

## Start now rejects an issue blocked by a reference

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"pr": 12}], "blockedBecause": "x"} | .startNow += [{"issue": 107, "why": "x"}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - startNow #107 waits on PR #12 and cannot start
  - lane L1 runs one branch at a time, but startNow picks 2 of its issues: #101, #107
[1]
```

## Start now accepts only issues that can start

```scrut
$ dir="$(mktemp -d)" && jq '.startNow += [{"issue": 102, "why": "x"}, {"issue": 105, "why": "x"}, {"issue": 103, "why": "x"}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - startNow #102 waits on #101 and cannot start
  - startNow #105 is already in progress on fix/105-broken-links
  - startNow #103 shares a branch with #101; list #101 instead
  - lane L1 runs one branch at a time, but startNow picks 3 of its issues: #101, #102, #103
[1]
```

## Start now sees work in progress on a shared branch

Issue #103 rides on the branch of #101, so work on it is work on #101.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 103)).inProgress = "feature/103-columns"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - startNow #101 is already in progress on feature/103-columns, through #103 on the same branch
[1]
```

## A serial lane runs its first issue that can start

```scrut
$ dir="$(mktemp -d)" && jq '.startNow += [{"issue": 107, "why": "x"}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - startNow #107: lane L1 is serial, and #101 is the first issue in it that can start; pick that, or reorder the lane
  - lane L1 runs one branch at a time, but startNow picks 2 of its issues: #101, #107
[1]
```

## Work in progress holds a lane

Lane L2 is a head lane, and #105 is in progress in it.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 104)) |= del(.waitingOn, .blockedBecause) | .startNow += [{"issue": 104, "why": "x"}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - startNow #104: lane L2 already has #105 in progress on fix/105-broken-links, and a head lane runs one branch at a time
[1]
```

## Nothing in a head lane starts before its head

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 105)) |= del(.inProgress) | (.issues[] | select(.number == 104)) |= del(.waitingOn, .blockedBecause) | .startNow += [{"issue": 104, "why": "x"}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - startNow #104: lane L2 is a head lane, and nothing in it starts before its head, #105
[1]
```

## A serial lane passes over a branch that is better after another issue

Issue #103 rides the branch of #101 and is better after #104, so that whole
branch waits and #107 is the first issue in the lane that can start.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 103)) += {"after": [104]} | .startNow = [{"issue": 107, "why": "x"}, {"issue": 106, "why": "x"}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is valid: 7 issues in 3 lanes (glob)
```

## A lane can show more than one branch in progress

Validation accepts it, so the board shows the overlap rather than hiding it.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 101)).inProgress = "feature/101-tokenizer" | (.issues[] | select(.number == 107)).inProgress = "feature/107-color" | .startNow = [{"issue": 106, "why": "x"}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is valid: 7 issues in 3 lanes (glob)
```

## A repository URL with a query

The page appends paths such as `/issues` to the repository URL.

```scrut
$ dir="$(mktemp -d)" && jq '.repoUrl = "https://git.example.com/widgets?view=1"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - repoUrl: expected an https:// URL for the repository, such as https://github.com/owner/name
[1]
```

## A repository URL with no host

Every same-repository link on the page is built from this address.

```scrut
$ dir="$(mktemp -d)" && jq '.repoUrl = "https:///widgets"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - repoUrl: expected an https:// URL for the repository, such as https://github.com/owner/name
[1]
```

## A repository URL with a malformed port

Every same-repository link resolves against the host and port.

```scrut
$ dir="$(mktemp -d)" && jq '.repoUrl = "https://git.example.com:bad/widgets"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - repoUrl: expected an https:// URL for the repository, such as https://github.com/owner/name
[1]
```

## A repository URL with a port

A self-hosted instance can serve the repository on an explicit port.

```scrut
$ dir="$(mktemp -d)" && jq '.repoUrl = "https://git.example.com:8443/widgets"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is valid: 7 issues in 3 lanes (glob)
```

## A repository URL with no repository path

Every same-repository link appends a path to this address, so a bare host
sends all of them somewhere else.

```scrut
$ dir="$(mktemp -d)" && jq '.repoUrl = "https://git.example.com"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - repoUrl: expected an https:// URL for the repository, such as https://github.com/owner/name
[1]
```

## An issue better after another

`after` records that an issue could start now but would repeat work if it
started before another open issue lands. It is not a block.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"after": [104]}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is valid: 7 issues in 3 lanes (glob)
```

## Start now rejects an issue better after an open one

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 106)) += {"after": [104]}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - startNow #106 is better after #104 and should not start before it lands
[1]
```

## Start now rejects a pick whose branch carries a better-after issue

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 103)) += {"after": [104]}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - startNow #101 shares its branch with #103, which should wait for another open issue
[1]
```

## Malformed better-after relations

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"after": [107, 99]} | (.issues[] | select(.number == 102)) += {"after": [101]} | (.issues[] | select(.number == 103)) += {"after": [101]}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #102 waits on #101 and is also better after it; keep only waitingOn
  - #103 shares a branch with #101, so it cannot also come after it
  - #107 is better after itself
  - #107 is better after #99, which is not an open issue on this board; drop it if it has closed, or name it as a reference
[1]
```

## Waiting on and better after the same reference

A title on one entry and not the other still names the same pull request.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"pr": 12}], "blockedBecause": "x", "after": [{"pr": 12, "title": "palette"}]}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #107 waits on PR #12 and is also better after it; keep only waitingOn
[1]
```

## A better-after loop

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 105)) += {"after": [107]} | (.issues[] | select(.number == 107)) += {"after": [105]}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #105 is part of a better-after loop; break it
  - #107 is part of a better-after loop; break it
[1]
```

## Better after a reference beyond the board

`after` takes the same reference forms as `waitingOn`.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"after": [{"ref": "example/themes#3", "title": "theme tokens"}, {"pr": 12}]}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is valid: 7 issues in 3 lanes (glob)
```

## Start now rejects an issue better after a reference

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 106)) += {"after": [{"ref": "example/themes#3"}]}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - startNow #106 is better after example/themes#3 and should not start before it lands
[1]
```

## Malformed better-after references

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"after": [{"pr": "12"}, {"branch": "b", "ref": "o/r#1"}, "soon"]}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #107: each after entry is an issue number or a reference object
  - #107: an after pr must be a pull request number
  - #107: each after reference names exactly one of pr, branch, ref, or url
[1]
```

## Issues that share a branch share a lane

```scrut
$ dir="$(mktemp -d)" && jq '.lanes[0].issues -= [103] | .lanes[2].issues += [103]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #103 shares a branch with #101, but they sit in different lanes
[1]
```

## Missing and malformed fields

```scrut
$ dir="$(mktemp -d)" && jq 'del(.summary, .sync.commit) | .lanes[1].mode = "parallel"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - summary: expected text summarizing the board
  - sync.commit: expected the full commit SHA
  - lane L2: mode must be serial, head, or any
[1]
```

## A sync time that is not a real time

```scrut
$ dir="$(mktemp -d)" && jq '.sync.at = "2026-09-10T24:30:00Z"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - sync.at: expected an ISO 8601 time with a zone, such as 2026-09-10T19:43:00-04:00
[1]
```

## A sync date the calendar does not have

```scrut
$ dir="$(mktemp -d)" && jq '.sync.at = "2026-02-31T10:00:00Z"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - sync.at: 2026-02-31 is not a date on the calendar
[1]
```

## A short commit SHA

A short SHA can name more than one commit, so the board records the full one.

```scrut
$ dir="$(mktemp -d)" && jq '.sync.commit = "0123456"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - sync.commit: expected the full commit SHA
[1]
```

## A time zone that is not a zone name

```scrut
$ dir="$(mktemp -d)" && jq '.sync.timeZone = "New York"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - sync.timeZone: expected an IANA zone name, such as America/New_York
[1]
```

## A time zone the database does not have

```scrut
$ dir="$(mktemp -d)" && jq '.sync.timeZone = "Mars/Olympus_Mons"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - sync.timeZone: Mars/Olympus_Mons is not a zone in the time zone database
[1]
```

## An issue without a milestone

A `null` milestone records an issue without one; leaving the field out is a mistake.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) |= del(.milestone)' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #107: milestone is required; use null for an issue without one
[1]
```

## Invalid JSON

```scrut
$ dir="$(mktemp -d)" && printf '{' > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid JSON (glob)
[1]
```

## Unreadable data file

```scrut
$ "${REPORT_BOARD_BIN}" validate /nonexistent/data.json 2>&1
report-board: cannot read /nonexistent/data.json
[1]
```

## Extract from a page without board data

```scrut
$ dir="$(mktemp -d)" && printf '<p>hello</p>\n' > "${dir}/page.html" && "${REPORT_BOARD_BIN}" extract "${dir}/page.html" 2>&1
report-board: */page.html is neither board data nor a rendered board (glob)
[1]
```

## Extract from the unrendered template

```scrut
$ "${REPORT_BOARD_BIN}" extract "$(dirname "${REPORT_BOARD_BIN}")/../templates/backlog-triage.html" 2>&1
report-board: */templates/backlog-triage.html holds no board data; render it with report-board first (glob)
[1]
```

## Extract from a page with two documents in its data

`compare` reads only the first, so a second would be dropped without a word.

```scrut
$ dir="$(mktemp -d)" && printf '<script type="application/json" id="board-data">{"a": 1}{"b": 2}</script>\n' > "${dir}/page.html" && "${REPORT_BOARD_BIN}" extract "${dir}/page.html" 2>&1
report-board: */page.html holds more than one JSON document in its board data (glob)
[1]
```

## Compare two syncs

```scrut
$ "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${REPORT_BOARD_DATA_DIR}/backlog-triage-next.json"
Previous sync: main at 01234567, 2026-09-01T09:30:00-04:00 in America/New_York, 1 open pull request, 12 packages
This sync: main at 89abcdef, 2026-09-08T10:15:00-04:00 in America/New_York, 0 open pull requests

- Closed: #101 parser: replace the tokenizer; #103 cli: report parse errors with columns; #105 docs: fix broken links
- Opened: #108 parser: benchmark suite (waits on #102)
- Unblocked: #102 parser: stream large inputs; #104 parser tutorial
- Started: #106 ci: cache dependencies (feature/106-cache)
- Added to start now: #102 parser: stream large inputs; #104 parser tutorial
- Dropped from start now: #101 parser: replace the tokenizer; #106 ci: cache dependencies
- Changed lanes: #107 cli: color output (L1 to L3)
- Changed milestone: #107 cli: color output (none to Parser rewrite)
- Changed lane mode: L2 (head to any)
- Changed lane details: L1 (owns, note); L2 (note)
- Changed contention: claim parser removed; claim cli removed
- Reworded: summary; the startNow note
```

## Compare reads the previous board out of a rendered page

```scrut
$ page="$(mktemp -d)/board.html" && "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${page}" 2> /dev/null && "${REPORT_BOARD_BIN}" compare "${page}" "${REPORT_BOARD_DATA_DIR}/backlog-triage-next.json" | tail -n 1
- Reworded: summary; the startNow note
```

## Compare names reference blockers

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"branch": "feature/palette"}], "blockedBecause": "x"}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${dir}/data.json" | tail -n 1
- Newly blocked: #107 cli: color output (waits on branch feature/palette)
```

## Compare reports better-after changes

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"after": [104]}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${dir}/data.json" | tail -n 1
- Now better after: #107 cli: color output (after #104)
```

## Compare reports changed blockers, soft links, and progress

A change inside a relation that is still set is a change, not a non-event.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)).after = [104]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/previous.json" && jq '(.issues[] | select(.number == 107)).after = [101] | (.issues[] | select(.number == 102)).waitingOn = [104] | (.issues[] | select(.number == 105)).inProgress = "PR #9"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/current.json" && "${REPORT_BOARD_BIN}" compare "${dir}/previous.json" "${dir}/current.json" | tail -n 3
- Blockers changed: #102 parser: stream large inputs (was waiting on #101, now #104)
- Better after changed: #107 cli: color output (was after #104, now #101)
- Progress moved: #105 docs: fix broken links (fix/105-broken-links to PR #9)
```

## Compare reports a milestone whose short label changed

The matrix heads a milestone column with its short label, so a new short label
under an unchanged title is still a change the page draws.

```scrut
$ dir="$(mktemp -d)" && jq '(.milestones[0]).short = "P1"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/current.json" && "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${dir}/current.json" | tail -n 1
- Changed milestones: now Parser rewrite (P1), Documentation
```

## Compare names a blocker whose title changed

The Blocked section draws a reference blocker's title, so a change to the title
alone is still a change the page draws.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"pr": 12, "title": "packaging rewrite"}], "blockedBecause": "x"}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/previous.json" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"pr": 12, "title": "packaging rewrite, phase 2"}], "blockedBecause": "x"}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/current.json" && "${REPORT_BOARD_BIN}" compare "${dir}/previous.json" "${dir}/current.json" | tail -n 1
- Blockers changed: #107 cli: color output (was waiting on PR #12 (packaging rewrite), now PR #12 (packaging rewrite, phase 2))
```

## Compare reports titles, branches, lanes, contention, and wording

Anything the page draws differently is a change worth reporting.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"title": "cli: colored output", "sameBranchAs": 101} | .lanes[0].issues = [101, 103, 107, 102] | .lanes[2].mode = "serial" | .lanes += [{"key": "L4", "name": "Themes", "mode": "any", "issues": []}] | .contention.claims[0].issues += [107] | .notes.blocked = "x" | .startNow[0].why = "y"' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${dir}/data.json" | tail -n +4
- Retitled: #107 ("cli: color output" to "cli: colored output")
- Changed branch: #107 cli: colored output (its own branch to the branch of #101)
- Lanes added: L4 Themes
- Changed lane mode: L3 (any to serial)
- Changed lane order: L1 (now #101, #103, #107, #102)
- Changed contention: claim parser (#101, #102, #104 to #101, #102, #104, #107)
- Reworded: the blocked note; why to start #101
```

## Compare reports identity and search changes, but not key order

A reference written with its keys in another order is the same reference.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"pr": 12, "title": "palette"}], "blockedBecause": "x"}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/previous.json" && jq '.title = "gadgets backlog" | .repo = "example/gadgets" | .contention.claims[0].query = "label:parser" | (.issues[] | select(.number == 107)) += {"waitingOn": [{"title": "palette", "pr": 12}], "blockedBecause": "x"}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/current.json" && "${REPORT_BOARD_BIN}" compare "${dir}/previous.json" "${dir}/current.json" | tail -n +4
- Changed board identity: title ("widgets backlog" to "gadgets backlog"); repo ("example/widgets" to "example/gadgets")
- Changed contention: claim parser search (none to "label:parser")
```

## Compare reports a changed zone and the order of claims

The page draws the sync time in its zone, and each claim and its issues in
the order given.

```scrut
$ dir="$(mktemp -d)" && jq '.sync.timeZone = "Europe/Lisbon" | .contention.claims |= reverse | .contention.claims[1].issues = [102, 101, 104]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${dir}/data.json"
Previous sync: main at 01234567, 2026-09-01T09:30:00-04:00 in America/New_York, 1 open pull request, 12 packages
This sync: main at 01234567, 2026-09-01T09:30:00-04:00 in Europe/Lisbon, 1 open pull request, 12 packages

- Changed contention: claim parser (#101, #102, #104 to #102, #101, #104); claim order (now cli, parser)
```

## Compare reports reordered blockers

The page lists what an issue waits on in the order given.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 102)).waitingOn = [101, 104]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/previous.json" && jq '(.issues[] | select(.number == 102)).waitingOn = [104, 101]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/current.json" && "${REPORT_BOARD_BIN}" compare "${dir}/previous.json" "${dir}/current.json" | tail -n 1
- Blockers changed: #102 parser: stream large inputs (was waiting on #101, #104, now #104, #101)
```

## A title on a better-after reference is not a change

The lane row links the reference without its title.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)).after = [{"pr": 12}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/previous.json" && jq '(.issues[] | select(.number == 107)).after = [{"pr": 12, "title": "palette"}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/current.json" && "${REPORT_BOARD_BIN}" compare "${dir}/previous.json" "${dir}/current.json" | tail -n 1
- No changes beyond the sync metadata.
```

## Compare reports reordered lanes

The page draws its lane sections in the order the data lists them.

```scrut
$ dir="$(mktemp -d)" && jq '.lanes |= reverse' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${dir}/data.json" | tail -n 1
- Reordered lanes: now L3, L2, L1
```

## Compare with nothing changed

```scrut
$ "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" | tail -n 1
- No changes beyond the sync metadata.
```

## Empty data

```scrut
$ dir="$(mktemp -d)" && : > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json must hold exactly one JSON document (glob)
[1]
```

## More than one document

```scrut
$ dir="$(mktemp -d)" && cat "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json must hold exactly one JSON document (glob)
[1]
```

## A top level that is not an object

```scrut
$ dir="$(mktemp -d)" && printf '[]' > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - the top level must be a JSON object
[1]
```

## A waitingOn that is not a list, on a start pick

Validation reports the shape rather than failing inside jq.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 106)) += {"waitingOn": "soon", "blockedBecause": "x"}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #106: waitingOn must be a list
[1]
```

## Branch and lane structure

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 105)) += {"sameBranchAs": 105} | (.issues[] | select(.number == 106)) += {"sameBranchAs": 99} | (.issues[] | select(.number == 107)) += {"sameBranchAs": 103} | .lanes[2].issues += [98, 106]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #105 shares a branch with itself
  - #106 shares a branch with #99, which is not in issues
  - #107 shares a branch with #103, which shares a branch with another issue; point both at the same one
  - lane L3 lists #98, which is not in issues
  - lane L3 lists #106 more than once
  - startNow #106 shares a branch with #99; list #99 instead
[1]
```

## Duplicate numbers, lane keys, picks, and claims

```scrut
$ dir="$(mktemp -d)" && jq '.issues += [{"number": 101, "title": "again", "milestone": null}] | .lanes[1].key = "L1" | .startNow += [{"issue": 106, "why": "again"}] | .contention.claims[0].issues += [101] | .contention.claims[1].issues = [107, 107] | .contention.claims += [{"name": "cli", "issues": [103, 107]}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - issues: #101 appears more than once
  - lanes: key L1 is used more than once
  - startNow: #106 is listed more than once
  - contention parser lists #101 more than once
  - contention cli: issues must list at least two different issue numbers
  - contention: claim cli is listed more than once
[1]
```

## Optional sections and sync fields

```scrut
$ dir="$(mktemp -d)" && jq '.repoUrl = "http://example.com/widgets" | .sync.timeZone = 5 | .sync.extra = "12 packages" | .milestones = [{"short": "x"}] | .contention.rowLabel = 7 | .contention.claims += [{"name": "docs", "issues": [1, 2], "query": 3}] | .notes.blocked = 3' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - repoUrl: expected an https:// URL for the repository, such as https://github.com/owner/name
  - sync.timeZone: expected an IANA zone name, such as America/New_York
  - sync.extra: expected a list of text
  - milestones[0]: expected an object with a title
  - contention.rowLabel: expected text
  - contention docs: query must be text
  - contention docs lists #1, which is not in issues
  - contention docs lists #2, which is not in issues
  - notes.blocked: expected text
[1]
```

## A blocking loop

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [102], "blockedBecause": "x"} | (.issues[] | select(.number == 102)).waitingOn += [107]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #102 is part of a blocking loop; break it
  - #107 is part of a blocking loop; break it
[1]
```

## Better after an issue on the same branch

Issue #103 ships on the branch of #101, so #101 cannot come after it.

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 101)) += {"after": [103]}' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - #101 shares a branch with #103, so it cannot also come after it
  - startNow #101 is better after #103 and should not start before it lands
[1]
```

## Render refuses a directory as the output

```scrut
$ dir="$(mktemp -d)" && "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${dir}" 2>&1
report-board: * is a directory; name the page file to write (glob)
[1]
```

## The rendered page follows the umask

```scrut
$ page="$(mktemp -d)/board.html" && (umask 022 && "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${page}" 2> /dev/null) && ls -l "${page}" | cut -c1-10
-rw-r--r--
```

## A umask that denies even the owner

The page still renders, and like any new file under that umask, it has no permissions.

```scrut
$ page="$(mktemp -d)/board.html" && (umask 0777 && "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${page}" 2> /dev/null) && ls -l "${page}" | cut -c1-10
----------
```

## A data file whose name starts with a dash

```scrut
$ dir="$(mktemp -d)" && cp "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${dir}/-data.json" && (cd "${dir}" && "${REPORT_BOARD_BIN}" validate -data.json 2>&1)
report-board: ./-data.json is valid: 7 issues in 3 lanes
```

## A symlink to the script still finds the templates

```scrut
$ dir="$(mktemp -d)" && ln -s "${REPORT_BOARD_BIN}" "${dir}/report-board" && "${dir}/report-board" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${dir}/board.html" 2>&1
report-board: rendered 7 issues in 3 lanes to */board.html (glob)
```

## A template missing a placeholder

The render stops before writing anything.

```scrut
$ dir="$(mktemp -d)" && mkdir "${dir}/scripts" "${dir}/templates" && cp "${REPORT_BOARD_BIN}" "${dir}/scripts/" && printf '<title>x</title>\n' > "${dir}/templates/backlog-triage.html" && "${dir}/scripts/report-board" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${dir}/board.html" 2>&1; ls "${dir}"
report-board: */backlog-triage.html is missing the __BOARD_TITLE__ or "__BOARD_DATA__" placeholder (glob)
scripts
templates
```

## Extract from a page inside a host skeleton

An Artifact read returns the page wrapped in the host's own document.

```scrut
$ dir="$(mktemp -d)" && "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${dir}/page.html" 2> /dev/null && { printf '<!doctype html><html><head></head><body>\n'; cat "${dir}/page.html"; printf '</body></html>\n'; } > "${dir}/wrapped.html" && "${REPORT_BOARD_BIN}" extract "${dir}/wrapped.html" | jq -r .title
widgets backlog
```

## Render usage error

```scrut
$ "${REPORT_BOARD_BIN}" render only-one.json 2>&1 | head -n 1
report-board: render takes a data file and an output path
```

## Compare usage error

```scrut
$ "${REPORT_BOARD_BIN}" compare only-one.json 2>&1 | head -n 1
report-board: compare takes the previous board and the current data
```

## Help

```scrut
$ "${REPORT_BOARD_BIN}" --help | head -n 1
Usage:
```

## Missing command

```scrut
$ "${REPORT_BOARD_BIN}" 2>&1 | head -n 1
report-board: a command is required
```

## Missing command exit code

```scrut
$ "${REPORT_BOARD_BIN}" > /dev/null 2>&1
[2]
```

## Unknown command

```scrut
$ "${REPORT_BOARD_BIN}" frobnicate 2>&1 | head -n 1
report-board: unknown command: frobnicate
```

## Unknown command exit code

```scrut
$ "${REPORT_BOARD_BIN}" frobnicate > /dev/null 2>&1
[2]
```
