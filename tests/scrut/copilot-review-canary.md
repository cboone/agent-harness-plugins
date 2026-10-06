# Copilot review canary

Tests for `bin/copilot-review-canary`, which samples recent Copilot reviews and
reports layout changes the parser in `resolve-copilot-threads` has not caught
up with. Its gathering mode needs an authenticated `gh`, so these cases run
`analyze` over saved samples, which is the same analysis without the network.
Each sample is a JSON array of `{repo, number, reviews, audit}`.

The fixtures carry their own baseline, so these cases do not move when the
committed baseline in `bin/data/` is refreshed.

## A clean sample prints nothing and exits 0

Like `version-audit`, empty output means there is nothing to look at. The
sample size goes to stderr every time, so a run that looked at nothing is
never mistaken for one that found nothing.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/clean.json"
```

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/clean.json" 2>&1 > /dev/null
copilot-review-canary: sampled 1 Copilot review on 1 pull request.
```

## Each kind of change gets its own section, and exits 1

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" 2> /dev/null | grep -E '^(#|Sampled)'
# Copilot review canary
Sampled 5 Copilot reviews on 5 pull requests.
## Signals the parser left unaccounted
## Bodies that are neither a review nor a known notice
## Copilot items the fetches cannot reach
## Leads repeated across pull requests
## Layout elements not in the baseline
```

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" > /dev/null 2>&1
[1]
```

A signal the census left unaccounted is reported with its review, kind, line
and region, so it can be found without rerunning anything.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" 2> /dev/null | grep -F 'section-count'
- https://github.com/o/r/pull/1#pullrequestreview-6000000040: `section-count` at line 19, in Also worth checking: `<summary><strong>Also worth checking (2)</strong></summary>`
```

A body that is neither a review nor a known notice is reported with its text.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" 2> /dev/null | grep -F 'still reviewing'
- https://github.com/o/r/pull/1#pullrequestreview-6000000038: `Copilot is still reviewing this pull request. Findings will appear here when the review completes.`
```

A Copilot item the surface audit found out of the fetches' reach is reported
from the sample's `audit`.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" 2> /dev/null | grep -F 'issuecomment'
- https://github.com/o/r/pull/4#issuecomment-9202 (issue-comment, pull request comment): Copilot reviewed this pull request and found one issue in the release workflow.
```

## A lead repeated across pull requests is reported, one restated on a single pull request is not

Every lead that is not a known no-finding sentence costs a read. A sentence
Copilot writes word for word on two different pull requests is boilerplate: a
reworded no-finding sentence the parser list should learn, or a fixed
advisory.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" 2> /dev/null | grep -F 'need attention'
- "One or more issues need attention before approval.": 2 pull requests, for example https://github.com/o/r/pull/1#pullrequestreview-6000000035
```

Copilot restates its own lead from round to round on one pull request, so the
same sentence twice there is not boilerplate.

```scrut
$ jq '[.[] | select(.number == 5) | .reviews += (.reviews | map(.id = 6000000098))]' "${COPILOT_CANARY_DATA_DIR}/findings.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null
```

The verdict and sections around the lead do not matter. A reworded approval
sentence repeated on two pull requests is exactly the boilerplate this looks
for, and it is the commonest case, since every approval lead that is not on
the parser list is read.

```scrut
$ jq '[.[] | select(.number == 5 or .number == 6) | .reviews[].body |= (sub("### 🔵 Needs a closer look"; "### 🟢 Approval recommended") | sub("One or more issues need attention before approval\\."; "No unresolved review issues were found."))]' "${COPILOT_CANARY_DATA_DIR}/findings.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null | grep -F 'were found'
- "No unresolved review issues were found.": 2 pull requests, for example https://github.com/o/r/pull/1#pullrequestreview-6000000035
```

A lead spread over several lines is reported on one.

```scrut
$ jq '[.[] | select(.number == 5 or .number == 6) | .reviews[].body |= sub("One or more issues need attention before approval\\."; "One issue remains.\n- The cache never expires.")]' "${COPILOT_CANARY_DATA_DIR}/findings.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null | grep -F 'One issue remains'
- "One issue remains. / - The cache never expires.": 2 pull requests, for example https://github.com/o/r/pull/1#pullrequestreview-6000000035
```

## A new layout element is reported before it carries a finding

This section lists threads, so the parser reads it correctly and the census
finds nothing wrong. It is still new, and the baseline comparison is what
makes it visible the first time it appears.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" 2> /dev/null | grep -F 'Deferred'
- `<summary><strong>Deferred (N)</strong></summary>`: 1 time, first 2026-10-06, for example https://github.com/o/r/pull/1#pullrequestreview-6000000039
```

## An incomplete sample is reported, and exits 2

Empty output has to mean the sample was read and found clean. A pull request
the parser could not read, one whose reviews could not be fetched, and one with
no surface audit each get a section of their own, ahead of everything else,
because whatever is reported below them may be missing something.

Each case below adds one cause to an otherwise clean sample, so the exit
status shows that cause alone makes the sample incomplete.

A pull request the parser could not read is listed with the parser's error.

```scrut
$ jq '. + [{"repo":"a/b","number":1,"reviews":[1],"audit":{"uncovered":[],"legacyNeedsRead":[]}}]' "${COPILOT_CANARY_DATA_DIR}/clean.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null
# Copilot review canary

Sampled 1 Copilot review on 2 pull requests.

## Pull requests the parser could not read

- a/b#1: Error: Invalid review JSON: every element must be a review object.
[2]
```

A pull request whose reviews could not be fetched is listed with the `gh` error.

```scrut
$ jq '. + [{"repo":"a/b","number":2,"reviews":[],"audit":null,"fetchError":"gh: Not Found (HTTP 404)"}]' "${COPILOT_CANARY_DATA_DIR}/clean.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null
# Copilot review canary

Sampled 1 Copilot review on 2 pull requests.

## Pull requests whose reviews could not be fetched

- a/b#2: gh: Not Found (HTTP 404)
[2]
```

A pull request whose audit failed is listed with the audit's error.

```scrut
$ jq '.[0].audit = {"error":"Error: GraphQL error while fetching threads: rate limited"}' "${COPILOT_CANARY_DATA_DIR}/clean.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null
# Copilot review canary

Sampled 1 Copilot review on 1 pull request.

## Pull requests with no surface audit

- o/r#1: Error: GraphQL error while fetching threads: rate limited
[2]
```

An audit that is missing, or that lacks the lists the resolver writes, counts
as no audit rather than as an audit that found nothing.

```scrut
$ for audit in 'null' '{}' '"oops"' '{"uncovered":[]}'; do jq --argjson audit "${audit}" '.[0].audit = $audit' "${COPILOT_CANARY_DATA_DIR}/clean.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null | grep -F 'o/r#1'; done
- o/r#1: no audit in the sample
- o/r#1: the audit has an unexpected shape
- o/r#1: the audit has an unexpected shape
- o/r#1: the audit has an unexpected shape
```

A review the parser skipped is reported from the parser's own warning, so a
malformed review cannot leave the sample smaller without a trace.

```scrut
$ jq '.[0].reviews += [{"id":7,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"y","body":12345}]' "${COPILOT_CANARY_DATA_DIR}/clean.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null
# Copilot review canary

Sampled 1 Copilot review on 1 pull request.

## Reviews the parser skipped

- o/r#1: Warning: skipping review 7: its body is not a string.
[2]
```

A named repository with no pull requests in the window is listed too, since it
contributed nothing to the sample.

```scrut
$ jq '. + [{"repo":"o/quiet","number":null,"reviews":[],"audit":null,"noPullRequests":true}]' "${COPILOT_CANARY_DATA_DIR}/clean.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null
# Copilot review canary

Sampled 1 Copilot review on 1 pull request.

## Named repositories with no pull requests in the window

- o/quiet: no pull requests in the window
[2]
```

An uncovered item with no excerpt is still reported, without a dangling colon.

```scrut
$ jq '.[0].audit.uncovered = [{"surface":"issue-comment","reason":"pull request comment","id":5,"url":"https://github.com/o/r/pull/1#issuecomment-5"}]' "${COPILOT_CANARY_DATA_DIR}/clean.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null | grep -F 'issuecomment-5'
- https://github.com/o/r/pull/1#issuecomment-5 (issue-comment, pull request comment)
```

A sample with no Copilot reviews at all says so, rather than printing nothing,
so a misspelled `--author` or an empty window does not read as clean.

```scrut
$ echo '[]' | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2>&1
copilot-review-canary: sampled 0 Copilot reviews on 0 pull requests.
# Copilot review canary

Sampled 0 Copilot reviews on 0 pull requests.

Nothing was analyzed: the sample holds no Copilot reviews. Check the --repo, --author and --since values.
[2]
```

## Gathering through gh

These cases run the gathering mode against `copilot-gh-stub`, installed as
`gh` first on `PATH`, which answers from `tests/data/copilot-gh/`. Pull
request 7 there is healthy, 8 has no reviews to fetch, and 9 points its thread
query at a pull request that does not exist. Each failure is recorded in the
sample rather than dropping the pull request, and the report says what could
not be seen.

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${COPILOT_REVIEW_CANARY_BIN}" --repo o/r --repo o/quiet --since 2026-10-01 --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null; echo "exit=$?"; rm -rf "${stub}"
# Copilot review canary

Sampled 2 Copilot reviews on 3 pull requests.

## Named repositories with no pull requests in the window

- o/quiet: no pull requests in the window

## Pull requests whose reviews could not be fetched

- o/r#8: gh: Not Found (HTTP 404)

## Pull requests with no surface audit

- o/r#9: Error: Invalid response while fetching threads for o/r#9: no such pull request.
exit=2
```

`--save` writes the gathered sample, with each failure recorded in its entry.

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${COPILOT_REVIEW_CANARY_BIN}" --repo o/r --since 2026-10-01 --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" --save "${stub}/sample.json" > /dev/null 2>&1; jq -c '.[] | {number, reviews: (.reviews | length), fetchError, audit: (if .audit == null then null elif .audit.error then "error" else "ok" end)}' "${stub}/sample.json"; rm -rf "${stub}"
{"number":7,"reviews":1,"fetchError":null,"audit":"ok"}
{"number":8,"reviews":0,"fetchError":"gh: Not Found (HTTP 404)","audit":null}
{"number":9,"reviews":1,"fetchError":null,"audit":"error"}
```

A repository that cannot be read stops the run before sampling, rather than
quietly contributing nothing, because the search the listing uses answers an
unknown repository with an empty list.

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${COPILOT_REVIEW_CANARY_BIN}" --repo o/r --repo o/missing --since 2026-10-01 2>&1; echo "exit=$?"; rm -rf "${stub}"
GraphQL: Could not resolve to a Repository with the name 'o/missing'. (repository)
copilot-review-canary: Cannot read repository o/missing. See the gh error above for the cause.
exit=3
```

## Skeletons carry layout, not prose

A skeleton replaces counts, paths, inline code, link text, badges and table
cells, and drops prose, so two reviews with the same layout produce the same
lines. Headings, comment markers, labels, italic lines, table headers, section
summaries without a badge and details tags are kept as written, because their
wording is the layout; on Copilot reviews they are its own boilerplate.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" skeletons < "${COPILOT_CANARY_DATA_DIR}/clean.json" | jq -r '.skeletons[]'
## Copilot review overview
### 🟢 Approval recommended
**Findings:**
**Review effort:**
- [badge] [TITLE](#thread)
<!-- ccr-overview-v2 -->
</details>
<details>
<summary><strong>Resolved since last review (N)</strong></summary>
```

```scrut
$ printf '[{"repo":"o/r","number":1,"reviews":[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"y","submitted_at":"2026-10-06T00:00:00Z","body":"| File | Summary |\\n|---|---|\\n| `src/secret-name.js` | Handles the private thing. **Moderate (2 votes):** fix it. |\\n| other/path.md | Docs. |\\n- `src/a.ts:12` - the trap leaks a temp file."}],"audit":null}]' | "${COPILOT_REVIEW_CANARY_BIN}" skeletons | jq -r '.skeletons[]'
- `CODE` TEXT
| --- |
| File | Summary |
| PATH | TEXT |
| PATH | TEXT | with (N votes)
```

## Usage errors

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" 2>&1
copilot-review-canary: Name at least one --repo, or an --author. Use 'copilot-review-canary --help' for usage.
[3]
```

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" --repo nope 2>&1
copilot-review-canary: --repo needs OWNER/REPO, got nope.
[3]
```

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" --author octocat --since yesterday 2>&1
copilot-review-canary: --since needs a YYYY-MM-DD date.
[3]
```

```scrut
$ echo '{}' | "${COPILOT_REVIEW_CANARY_BIN}" analyze 2>&1
copilot-review-canary: Invalid sample: expected an array of {repo, number, reviews, audit} objects.
[3]
```

```scrut
$ echo '[]' | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline /nonexistent/baseline.json 2>&1
copilot-review-canary: Baseline not found: /nonexistent/baseline.json
[3]
```

The canary checks the jq version itself, so a jq too old for the resolver is
named once rather than failing every pull request in turn.

```scrut
$ fake="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '#!/usr/bin/env bash\necho jq-1.6\n' > "${fake}/jq" && chmod +x "${fake}/jq" && echo '[]' | PATH="${fake}:${PATH}" "${COPILOT_REVIEW_CANARY_BIN}" analyze 2>&1; rc=$?; rm -rf "${fake}"; (exit "${rc}")
copilot-review-canary: jq 1.7 or later is required, found jq-1.6.
[3]
```
