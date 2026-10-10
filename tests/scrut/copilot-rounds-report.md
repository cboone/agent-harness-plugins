# Copilot rounds report

Tests for `bin/copilot-rounds-report`. Every `gh api graphql` call goes to `tests/fixtures/gh-stub`, which answers with `tests/data/copilot-rounds-report/graphql/copilot-rounds.json`.

The fixture holds two search pages for a search that matched four pull requests. `cboone/tool#1` appears on page one with only its first review and again on page two with all of them, as happens when results shift during pagination, so the report must count it once, from the fuller listing. That listing has four Copilot rounds: one with two new findings (High and Low), a findings-free one, one with a previously missed Medium finding and no inline comments, and an approval, with a human review in between. `client-org/app#7` is approved in one round, in the layout that puts a `## Copilot review overview` heading between the marker and the verdict. `cboone/tool#2` has only a human review and is left out. `client-org/app#8`, whose owner login differs in case from `--client-owner`, has a Medium finding, a review from a deleted account, a findings-free advisory round and a Copilot error notice, which is not a round.

## Setup

`stubbed` runs the script with `gh` answered by the stub, and `report` adds the owners, range and author of the baseline analysis. `variant` writes a copy of the fixture changed by a jq filter, for the cases that `replay` reads with `--input`.

```scrut {fail_fast: true}
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && mkdir "${work}/bin" "${work}/tmp" && ln -s "${GH_STUB_BIN}" "${work}/bin/gh" \
>   && pages="${COPILOT_ROUNDS_REPORT_DATA_DIR}/graphql/copilot-rounds.json" \
>   && args=(--owner cboone --owner client-org --since 2026-09-29 --until 2026-10-09 --author cboone) \
>   && function stubbed() { PATH="${work}/bin:${PATH}" STUB_GH_DIR="${COPILOT_ROUNDS_REPORT_DATA_DIR}" "${COPILOT_ROUNDS_REPORT_BIN}" "$@"; } \
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

Pull requests matched: 4. With a Copilot review: 3. Copilot notices in place of a review, not counted as rounds: 1.

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

## Without client owners, only the total row is reported

```scrut
$ report | grep -E '^\| (Client|Non-client|All) '
| All | 3 | 7 | 2 | 2.3 | 4 | 0 | 3 | 1 | 2 | 2 |
```

## p90 is the nearest rank

With ten pull requests of one to ten rounds, p90 is the ninth value, not the maximum.

```scrut
$ variant '.[1].data.search.nodes[0] as $pr
>   | [range(1; 11) as $n | $pr | .number = 100 + $n | .reviews.nodes = [range($n) as $_ | $pr.reviews.nodes[0]] | .reviews.totalCount = $n] as $prs
>   | [.[1] | .data.search.nodes = $prs | .data.search.issueCount = 10]' \
>   && replay | grep '^| All '
| All | 10 | 55 | 5.5 | 5.5 | 9 | 6 | 20 | 90 | 0 | 0 |
```

## Pinned real review bodies

Every Copilot body pinned in `tests/data/copilot-reviews/`, one pull request per file, classifies without a warning: the older "Pull request overview" layouts have no verdict, each later layout yields its verdict, and both notices are left out.

```scrut
$ jq -n '[inputs as $reviews | {number: 1,
>     repository: {nameWithOwner: "pinned/\(input_filename | split("/")[-1] | rtrimstr(".json"))", owner: {login: "pinned"}},
>     reviews: {totalCount: ($reviews | length), nodes: [$reviews[] | {author: {login: .user.login}, body, comments: {totalCount: 0}}]}}]
>   | [{data: {search: {issueCount: length, pageInfo: {hasNextPage: false}, nodes: .}}}]' \
>   "${COPILOT_REVIEW_DATA_DIR}"/format-*.json "${COPILOT_REVIEW_DATA_DIR}"/notice-*.json > "${work}/variant.json" \
>   && replay 2>&1 | grep -E '^(copilot-rounds-report|Pull requests matched|\| pinned/)' | sort
Pull requests matched: 12. With a Copilot review: 10. Copilot notices in place of a review, not counted as rounds: 2.
| pinned/format-a#1 | 1 | 0 | none (older layout) |
| pinned/format-b#1 | 1 | 0 | none (older layout) |
| pinned/format-c#1 | 1 | 1 | Approval recommended |
| pinned/format-d#1 | 1 | 0 | Needs a closer look |
| pinned/format-d-bold-votes#1 | 1 | 0 | Changes recommended |
| pinned/format-d-missed-badges#1 | 1 | 2 | Needs a closer look |
| pinned/format-d-moderate-labels#1 | 1 | 0 | Changes recommended |
| pinned/format-d-open-findings-block#1 | 1 | 0 | Changes recommended |
| pinned/format-d-previously-missed#1 | 2 | 2 | Needs a closer look |
| pinned/format-d-zero-open-line#1 | 1 | 0 | Needs a closer look |
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

```scrut
$ variant '.[].data.search.nodes[].reviews |= (.nodes |= map(select(.author.login != "copilot-pull-request-reviewer")) | .totalCount = (.nodes | length))' \
>   && replay 2>&1 > /dev/null
copilot-rounds-report: warning: none of the 4 pull requests had a Copilot review
```

A review whose verdict line cannot be found still counts as a round, with a warning, because it means Copilot changed its layout.

```scrut
$ variant '.[0].data.search.nodes[1].reviews.nodes[0].body |= sub("### [^\n]*"; "Approved.")' \
>   && replay 2>&1 > /dev/null
copilot-rounds-report: warning: 1 Copilot reviews had no recognizable verdict; check whether the review layout changed
```

## Partial or missing data stops the report

A failed search stops the report rather than printing an empty one, and leaves no temporary files behind.

```scrut
$ STUB_GH_GRAPHQL_FAIL=copilot-rounds TMPDIR="${work}/tmp" report 2>&1 | tail -n 1
copilot-rounds-report: could not search for pull requests
```

```scrut
$ STUB_GH_GRAPHQL_FAIL=copilot-rounds TMPDIR="${work}/tmp" report > /dev/null 2>&1
[1]
```

```scrut
$ find "${work}/tmp" -mindepth 1 | wc -l | tr -d ' '
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
copilot-rounds-report: a search result is not a pull request
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
$ printf '[{"data":' > "${work}/variant.json" && replay 2>&1 | tail -n 1
copilot-rounds-report: the search response is not valid JSON
```

```scrut
$ printf '[{"data":' > "${work}/variant.json" && replay > /dev/null 2>&1
[1]
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
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --since 2026-09-29 extra 2>&1 | tail -n 1
copilot-rounds-report: unexpected argument 'extra'
```

```scrut
$ "${COPILOT_ROUNDS_REPORT_BIN}" --owner cboone --since 2026-09-29 extra > /dev/null 2>&1
[1]
```
