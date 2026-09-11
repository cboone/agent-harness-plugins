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
  - #107: a waitingOn url needs an https:// address and a label
  - #107: each waitingOn reference names exactly one of pr, branch, ref, or url
[1]
```

## Start now rejects an issue blocked by a reference

```scrut
$ dir="$(mktemp -d)" && jq '(.issues[] | select(.number == 107)) += {"waitingOn": [{"pr": 12}], "blockedBecause": "x"} | .startNow += [{"issue": 107, "why": "x"}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - startNow #107 waits on PR #12 and cannot start
[1]
```

## Start now accepts only issues that can start

```scrut
$ dir="$(mktemp -d)" && jq '.startNow += [{"issue": 102, "why": "x"}, {"issue": 105, "why": "x"}, {"issue": 103, "why": "x"}]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - startNow #102 waits on #101 and cannot start
  - startNow #105 is already in progress on fix/105-broken-links
  - startNow #103 shares a branch with #101; list #101 instead
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
  - #107 is better after #99, which is not an open issue on this board; drop it
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
  - summary: expected one or two sentences
  - sync.commit: expected a commit SHA
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

## Compare two syncs

```scrut
$ "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${REPORT_BOARD_DATA_DIR}/backlog-triage-next.json"
Previous sync: main at 01234567, 2026-09-01T09:30:00-04:00
This sync: main at 89abcdef, 2026-09-08T10:15:00-04:00

- Closed: #101 parser: replace the tokenizer; #103 cli: report parse errors with columns; #105 docs: fix broken links
- Opened: #108 parser: benchmark suite
- Unblocked: #102 parser: stream large inputs; #104 parser tutorial
- Started: #106 ci: cache dependencies (feature/106-cache)
- Added to start now: #102 parser: stream large inputs; #104 parser tutorial
- Dropped from start now: #101 parser: replace the tokenizer; #106 ci: cache dependencies
- Changed lanes: #107 cli: color output (L1 to L3)
- Changed milestone: #107 cli: color output (none to Parser rewrite)
```

## Compare reads the previous board out of a rendered page

```scrut
$ page="$(mktemp -d)/board.html" && "${REPORT_BOARD_BIN}" render "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${page}" 2> /dev/null && "${REPORT_BOARD_BIN}" compare "${page}" "${REPORT_BOARD_DATA_DIR}/backlog-triage-next.json" | tail -n 1
- Changed milestone: #107 cli: color output (none to Parser rewrite)
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

## Compare with nothing changed

```scrut
$ "${REPORT_BOARD_BIN}" compare "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" | tail -n 1
- No changes to issues, blockers, lanes, or start picks.
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
$ dir="$(mktemp -d)" && jq '.issues += [{"number": 101, "title": "again", "milestone": null}] | .lanes[1].key = "L1" | .startNow += [{"issue": 106, "why": "again"}] | .contention.claims[1].issues = [107, 107]' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - issues: #101 appears more than once
  - lanes: key L1 is used more than once
  - startNow: #106 is listed more than once
  - contention cli: issues must list at least two different issue numbers
[1]
```

## Optional sections and sync fields

```scrut
$ dir="$(mktemp -d)" && jq '.repoUrl = "http://example.com/widgets" | .sync.timeZone = 5 | .sync.extra = "12 packages" | .milestones = [{"short": "x"}] | .contention.rowLabel = 7 | .contention.claims += [{"name": "docs", "issues": [1, 2], "query": 3}] | .notes.blocked = 3' "${REPORT_BOARD_DATA_DIR}/backlog-triage.json" > "${dir}/data.json" && "${REPORT_BOARD_BIN}" validate "${dir}/data.json" 2>&1
report-board: */data.json is not valid board data: (glob)
  - repoUrl: expected an https:// URL
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
