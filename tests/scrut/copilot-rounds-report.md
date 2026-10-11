# Copilot rounds report

Tests for `bin/copilot-rounds-report`. Every `gh api graphql` call goes to `tests/fixtures/gh-stub`, which answers with `tests/data/copilot-rounds-report/graphql/copilot-rounds.json`.

The fixture holds two search pages for a search that matched four pull requests. `cboone/tool#1` appears on page one with only its first review and again on page two with all of them, as happens when results shift during pagination, so the report must count it once, from the fuller listing. That listing has four Copilot rounds: one with two new findings (High and Low), a findings-free one, one with a previously missed Medium finding and no inline comments, and an approval, with a human review between the first and second rounds. `client-org/app#7` is approved in one round, in the layout that puts a `## Copilot review overview` heading between the marker and the verdict. `cboone/tool#2` has only a human review and is left out. `client-org/app#8`, whose owner login differs in case from `--client-owner`, has a Medium finding, a review from a deleted account, a findings-free advisory round and a Copilot error notice, which is not a round.

## Setup

`stubbed` runs the script with `gh` answered by the stub from the fixture directory, or from `STUB_GH_DIR` when a case sets it, and `report` adds the owners, range and author of the baseline analysis. `variant` writes a copy of the fixture changed by a jq filter to `${work}/variant.json`, and `replay` reruns the script with `--input` on that file, whichever case wrote it.

```scrut {fail_fast: true}
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && mkdir "${work}/bin" "${work}/tmp" && ln -s "${GH_STUB_BIN}" "${work}/bin/gh" \
>   && pages="${COPILOT_ROUNDS_REPORT_DATA_DIR}/graphql/copilot-rounds.json" \
>   && args=(--owner cboone --owner client-org --since 2026-09-29 --until 2026-10-09 --author cboone) \
>   && function stubbed() { PATH="${work}/bin:${PATH}" STUB_GH_DIR="${STUB_GH_DIR:-${COPILOT_ROUNDS_REPORT_DATA_DIR}}" "${COPILOT_ROUNDS_REPORT_BIN}" "$@"; } \
>   && function report() { stubbed "${args[@]}" "$@"; } \
>   && function variant() { jq "${1}" "${pages}" > "${work}/variant.json"; } \
>   && function replay() { "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --since 2026-09-29 --input "${work}/variant.json"; } \
>   && echo ready
ready
```

## Help

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --help | head -n 1
Usage: copilot-rounds-report --owner OWNER [--owner OWNER]... --since DATE [options]
```

## The report splits client and non-client work

```scrut
$ report --client-owner client-org
# Copilot rounds report

Pull requests by cboone in cboone, client-org, created from 2026-09-29 to 2026-10-09.

Pull requests matched: 4. With a Copilot round: 3. Copilot notices in place of a review, not counted as rounds: 1.

## Rounds per pull request

| Group | PRs | Rounds | Median | Mean | p90 | 5+ rounds | Round 1 findings | Later findings | Findings-free rounds | Last round approves |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Client | 2 | 3 | 1.5 | 1.5 | 2 | 0 | 1 | 0 | 1 | 1 |
| Non-client | 1 | 4 | 4 | 4.0 | 4 | 0 | 2 | 1 | 1 | 1 |
| All | 3 | 7 | 2 | 2.3 | 4 | 0 | 3 | 1 | 2 | 2 |

## Findings per round

| Round | Reviews | Findings | Per review | High share of rated | Findings-free |
| --- | --- | --- | --- | --- | --- |
| 1 | 3 | 3 | 1.0 | 33% of 3 | 0 |
| 2 | 2 | 0 | 0.0 | n/a | 2 |
| 3 | 1 | 1 | 1.0 | 0% of 1 | 0 |
| 4 | 1 | 0 | 0.0 | n/a | 0 |

## Most rounds

| Pull request | Rounds | Findings | Last verdict |
| --- | --- | --- | --- |
| cboone/tool#1 | 4 | 3 | Approval recommended |
| client-org/app#8 | 2 | 1 | Needs a closer look |
| client-org/app#7 | 1 | 0 | Approval recommended |
```

## Previously missed findings count toward severity

With the previously missed finding rated High, round 3's High share is all of it.

```scrut
$ variant '.[1].data.search.nodes[0].reviews.nodes[3].body |= sub("Medium severity"; "High severity")' \
>   && replay | grep '^| 3 '
| 3 | 1 | 1 | 1.0 | 100% of 1 | 0 |
```

## Without client owners, only the total row is reported

```scrut
$ report | grep -E '^\| (Client|Non-client|All) '
| All | 3 | 7 | 2 | 2.3 | 4 | 0 | 3 | 1 | 2 | 2 |
```

## Client owners match in any case

```scrut
$ report --client-owner CLIENT-ORG | grep '^| Client '
| Client | 2 | 3 | 1.5 | 1.5 | 2 | 0 | 1 | 0 | 1 | 1 |
```

## p90 is the nearest rank, and rounds 8 on share a row

With ten pull requests of one to ten rounds, p90 is the ninth value, not the maximum, and the `8+` row holds the six rounds from the eighth on.

```scrut
$ variant '.[1].data.search.nodes[0] as $pr
>   | [range(1; 11) as $n | $pr | .number = 100 + $n | .reviews.nodes = [range($n) as $_ | $pr.reviews.nodes[0]] | .reviews.totalCount = $n] as $prs
>   | [.[1] | .data.search.nodes = $prs | .data.search.issueCount = 10]' \
>   && replay | grep -E '^\| (All|7|8\+) '
| All | 10 | 55 | 5.5 | 5.5 | 9 | 6 | 20 | 90 | 0 | 0 |
| 7 | 4 | 8 | 2.0 | 50% of 8 | 0 |
| 8+ | 6 | 12 | 2.0 | 50% of 12 | 0 |
```

## Pinned real review bodies

Every Copilot review pinned in `tests/data/copilot-reviews/format-*.json` and `notice-*.json`, one pull request per file and with as many inline comments as findings it marks new, classifies without a warning: the older "Pull request overview" layouts have no verdict, each later layout yields its verdict, and both notices are left out. The round 1 row pins the severity count on real bodies, which leaves out badges on findings carried over from an earlier round.

```scrut
$ jq -n '[inputs as $reviews | {number: 1,
>     repository: {nameWithOwner: "pinned/\(input_filename | split("/")[-1] | rtrimstr(".json"))", owner: {login: "pinned"}},
>     reviews: {totalCount: ($reviews | length), nodes: [$reviews[] | {author: {login: .user.login}, body, comments: {totalCount: ([.body | scan("· New")] | length)}}]}}]
>   | [{data: {search: {issueCount: length, pageInfo: {hasNextPage: false}, nodes: .}}}]' \
>   "${COPILOT_REVIEW_DATA_DIR}"/format-*.json "${COPILOT_REVIEW_DATA_DIR}"/notice-*.json > "${work}/variant.json" \
>   && replay 2>&1 | grep -E '^(copilot-rounds-report|Pull requests matched|\| (1 |pinned/))' | sort
Pull requests matched: 12. With a Copilot round: 10. Copilot notices in place of a review, not counted as rounds: 2.
| 1 | 10 | 11 | 1.1 | 40% of 10 | 4 |
| pinned/format-a#1 | 1 | 0 | none (older layout) |
| pinned/format-b#1 | 1 | 0 | none (older layout) |
| pinned/format-c#1 | 1 | 1 | Approval recommended |
| pinned/format-d#1 | 1 | 0 | Needs a closer look |
| pinned/format-d-bold-votes#1 | 1 | 2 | Changes recommended |
| pinned/format-d-missed-badges#1 | 1 | 2 | Needs a closer look |
| pinned/format-d-moderate-labels#1 | 1 | 1 | Changes recommended |
| pinned/format-d-open-findings-block#1 | 1 | 3 | Changes recommended |
| pinned/format-d-previously-missed#1 | 2 | 3 | Needs a closer look |
| pinned/format-d-zero-open-line#1 | 1 | 0 | Needs a closer look |
```

A format-c review lists its new findings only as inline comments, so inline comments without a badge marked new do not warn there.

```scrut
$ jq '[{data: {search: {issueCount: 1, pageInfo: {hasNextPage: false}, nodes: [{number: 1,
>     repository: {nameWithOwner: "pinned/format-c", owner: {login: "pinned"}},
>     reviews: {totalCount: 1, nodes: [.[] | {author: {login: .user.login}, body, comments: {totalCount: 2}}]}}]}}}]' \
>   "${COPILOT_REVIEW_DATA_DIR}/format-c.json" > "${work}/variant.json" \
>   && replay 2>&1 | grep -c warning
0
[1]
```

## The search names the author, range and every owner, in creation order

```scrut
$ STUB_GH_LOG="${work}/calls.log" report > /dev/null \
>   && cat "${work}/calls.log"
gh api graphql copilot-rounds q=is:pr author:cboone created:2026-09-29..2026-10-09 owner:cboone owner:client-org sort:created-asc
```

Without `--until`, the range is open-ended and the author defaults to the authenticated user.

```scrut
$ : > "${work}/calls.log" \
>   && STUB_GH_LOG="${work}/calls.log" stubbed --owner cboone --since 2026-09-29 | sed -n 3p \
>   && cat "${work}/calls.log"
Pull requests by @me in cboone, created on or after 2026-09-29.
gh api graphql copilot-rounds q=is:pr author:@me created:>=2026-09-29 owner:cboone sort:created-asc
```

## Saved pages reproduce the same report

```scrut
$ report --save "${work}/pages.json" > "${work}/fetched.md" \
>   && "${COPILOT_ROUNDS_REPORT_BIN}" "${args[@]}" --input "${work}/pages.json" > "${work}/replayed.md" \
>   && cmp "${work}/fetched.md" "${work}/replayed.md" && echo same
same
```

## Partial results warn

A search whose pages return fewer pull requests than it matched still reports, with a warning on stderr.

```scrut
$ variant '.[].data.search.issueCount = 5' && replay 2>&1 > /dev/null
copilot-rounds-report: warning: the search matched 5 pull requests but returned 4; results may have shifted while the pages were fetched
```

The report itself says it is partial, so the gap does not live only on stderr.

```scrut
$ variant '.[].data.search.issueCount = 5' && replay 2> /dev/null | grep '^Partial'
Partial: 4 of the 5 matched pull requests were returned, so every figure below leaves some out.
```

```scrut
$ variant '.[].data.search.nodes[].reviews |= (.nodes |= map(select(.author.login != "copilot-pull-request-reviewer")) | .totalCount = (.nodes | length))' \
>   && replay 2>&1 > /dev/null
copilot-rounds-report: warning: none of the 4 pull requests had a Copilot round
```

A review whose verdict line cannot be found still counts as a round, with a warning, since that usually means Copilot changed its layout.

```scrut
$ variant '.[0].data.search.nodes[1].reviews.nodes[0].body |= sub("### [^\n]*"; "Approved.")' \
>   && replay 2>&1 > /dev/null
copilot-rounds-report: warning: 1 Copilot reviews had no recognizable verdict; check whether the review layout changed
```

Findings the report cannot count also warn: a previously missed list under another heading, or inline findings with no badge marked new.

```scrut
$ variant '.[1].data.search.nodes[0].reviews.nodes |= map(.body |= sub("Previously missed"; "Earlier missed"))' \
>   && replay 2>&1 > /dev/null
copilot-rounds-report: warning: 1 Copilot rounds list findings or badges the report could not count; check whether the review layout changed
```

```scrut
$ variant '.[].data.search.nodes[].reviews.nodes |= map(.body |= gsub("· New"; "(new)"))' \
>   && replay 2>&1 > /dev/null
copilot-rounds-report: warning: 2 Copilot rounds list findings or badges the report could not count; check whether the review layout changed
```

## Partial or missing data stops the report

A failed search stops the report rather than printing an empty one, and leaves no temporary files behind.

```scrut
$ (set -o pipefail; STUB_GH_GRAPHQL_FAIL=copilot-rounds TMPDIR="${work}/tmp" report 2>&1 | tail -n 1)
copilot-rounds-report: could not search for pull requests
[1]
```

```scrut
$ find "${work}/tmp" -mindepth 1 | wc -l | tr -d ' '
0
```

A temporary directory whose path holds a quote is still removed, and the quote never reaches the cleanup command as code.

```scrut
$ mkdir "${work}/it's" \
>   && STUB_GH_GRAPHQL_FAIL=copilot-rounds TMPDIR="${work}/it's" report > /dev/null 2>&1; \
>   find "${work}/it's" -mindepth 1 | wc -l | tr -d ' '
0
```

```scrut
$ variant '.[].data.search.issueCount = 0' && replay 2>&1
copilot-rounds-report: no pull requests matched
[1]
```

```scrut
$ variant '.[].data.search.issueCount = 1500' && replay 2>&1
copilot-rounds-report: 1500 pull requests matched, more than the 1000 GitHub search returns; split the range with --since and --until
[1]
```

```scrut
$ variant '.[1].data.search.nodes[2].reviews.totalCount = 140' && replay 2>&1
copilot-rounds-report: more reviews than the query reads (100) on client-org/app#8
[1]
```

```scrut
$ variant '.[1].errors = [{"message": "Something went wrong"}]' && replay 2>&1
copilot-rounds-report: a search page holds GraphQL errors: Something went wrong
[1]
```

```scrut
$ variant '.[1].data.search.pageInfo.hasNextPage = true' && replay 2>&1
copilot-rounds-report: the last search page says more results follow, so the search was cut short
[1]
```

```scrut
$ variant '.[1].data.search.nodes += [null]' && replay 2>&1
copilot-rounds-report: the search response does not have the shape the report reads
[1]
```

```scrut
$ variant '[]' && replay 2>&1
copilot-rounds-report: expected a non-empty array of search pages
[1]
```

```scrut
$ printf '{"data":{}}\n' > "${work}/variant.json" && replay 2>&1
copilot-rounds-report: expected a non-empty array of search pages
[1]
```

```scrut
$ (set -o pipefail; printf '[{"data":' > "${work}/variant.json" && replay 2>&1 | tail -n 1)
copilot-rounds-report: the search response is not valid JSON
[1]
```

```scrut
$ : > "${work}/variant.json" && replay 2>&1
copilot-rounds-report: the search response is empty
[1]
```

```scrut
$ cat "${pages}" "${pages}" > "${work}/variant.json" && replay 2>&1
copilot-rounds-report: expected one JSON document, got 2
[1]
```

```scrut
$ printf '[{"data":"x"}]\n' > "${work}/variant.json" && replay 2>&1
copilot-rounds-report: the search response does not have the shape the report reads
[1]
```

```scrut
$ variant '.[1].data.search.nodes[1].reviews = null' && replay 2>&1
copilot-rounds-report: the search response does not have the shape the report reads
[1]
```

```scrut
$ variant '.[1].data.search.nodes[1].reviews.nodes[0].comments = null' && replay 2>&1
copilot-rounds-report: the search response does not have the shape the report reads
[1]
```

```scrut
$ variant '.[1].data.search.issueCount = 5' && replay 2>&1
copilot-rounds-report: the search pages disagree on how many pull requests matched
[1]
```

A fetched response is saved before it is checked, so a failed search can be inspected.

```scrut
$ mkdir -p "${work}/errors/graphql" \
>   && jq '.[1].errors = [{"message": "Something went wrong"}]' "${pages}" > "${work}/errors/graphql/copilot-rounds.json" \
>   && STUB_GH_DIR="${work}/errors" report --save "${work}/failed.json" 2>&1; \
>   jq -r '.[1].errors[0].message' "${work}/failed.json"
copilot-rounds-report: a search page holds GraphQL errors: Something went wrong
Something went wrong
```

## Argument errors

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --since 2026-09-29 2>&1
copilot-rounds-report: at least one --owner is required
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone 2>&1
copilot-rounds-report: --since is required
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --since 2026-9-29 2>&1
copilot-rounds-report: --since needs a YYYY-MM-DD date, got '2026-9-29'
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --since 2026-02-30 2>&1
copilot-rounds-report: --since needs a YYYY-MM-DD date, got '2026-02-30'
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --since 2026-10-09 --until 2026-09-29 2>&1
copilot-rounds-report: --until 2026-09-29 is before --since 2026-10-09
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --since 2026-09-29 --save a.json --input b.json 2>&1
copilot-rounds-report: --save and --input cannot be combined
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --since 2026-09-29 --input "${work}/missing.json" 2>&1
copilot-rounds-report: no such input file /*/missing.json (glob)
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner 'cboone client-org' --since 2026-09-29 2>&1
copilot-rounds-report: an owner must be a single login, got 'cboone client-org'
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --author 'cboone is:merged' --since 2026-09-29 2>&1
copilot-rounds-report: --author must be a single login or @me, got 'cboone is:merged'
[1]
```

A search that fails with no output still replaces an earlier saved file, so no stale file looks current, and the message names the file.

```scrut
$ printf 'stale\n' > "${work}/stale.json" \
>   && STUB_GH_GRAPHQL_FAIL=copilot-rounds report --save "${work}/stale.json" 2>&1 | tail -n 1; \
>   wc -c < "${work}/stale.json" | tr -d ' '
copilot-rounds-report: could not search for pull requests; /*/stale.json holds gh's output from the failed search (glob)
1
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --since 2026-09-29 --save "${work}" 2>&1
copilot-rounds-report: cannot write the --save file /* (glob)
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --since 2026-09-29 --save "${work}/missing/pages.json" 2>&1
copilot-rounds-report: cannot write the --save file /*/missing/pages.json (glob)
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner 2>&1
copilot-rounds-report: --owner needs a value
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --author --since 2026-09-29 --owner cboone 2>&1
copilot-rounds-report: --author needs a value
[1]
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --client-owner client-org --since 2026-09-29 2>&1
copilot-rounds-report: --client-owner client-org is not one of the --owner values
[1]
```

An input path that starts with `-` is read as a file, not as an option.

```scrut
$ (cd "${work}" && cp "${pages}" ./-pages.json \
>   && "${COPILOT_ROUNDS_REPORT_BIN}" "${args[@]}" --input -pages.json | sed -n 5p)
Pull requests matched: 4. With a Copilot round: 3. Copilot notices in place of a review, not counted as rounds: 1.
```

```scrut
$ (set -o pipefail; "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --since 2026-09-29 extra 2>&1 | tail -n 1)
copilot-rounds-report: unexpected argument 'extra'
[1]
```
