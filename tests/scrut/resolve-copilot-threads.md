# Copilot review bodies

Tests for `resolve-copilot-threads parse-reviews`, which selects Copilot's reviews from pull request review JSON and returns each one's complete raw body for the caller to read.

Copilot files some findings in a review body instead of an inline thread. Those have no thread id, so a `reviewThreads` query cannot see them. Copilot also reshapes the layout of those bodies often, so the command never parses the layout: it passes the text through. The fixtures are Copilot review bodies in each layout observed so far.

## Every layout comes back byte for byte

Whatever the layout, the body a caller reads is exactly the body Copilot wrote. This is the property that keeps a new layout from changing what the command reports.

```scrut
$ for f in format-a format-b format-c format-d format-d-bold-votes format-d-open-findings-block format-d-zero-open-line format-d-previously-missed format-d-missed-badges format-d-moderate-labels notice-error notice-no-files; do printf '%s ' "${f}"; "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/${f}.json" | jq -c --slurpfile raw "${COPILOT_REVIEW_DATA_DIR}/${f}.json" '[.[] as $o | $raw[0][] | select(.id == $o.id) | .body == $o.body] | (length > 0 and all)'; done
format-a true
format-b true
format-c true
format-d true
format-d-bold-votes true
format-d-open-findings-block true
format-d-zero-open-line true
format-d-previously-missed true
format-d-missed-badges true
format-d-moderate-labels true
notice-error true
notice-no-files true
```

## Each review carries only API fields beside its body

Every field other than `threadLinks` and `body` comes from the REST review object itself, never from the body's layout.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-zero-open-line.json" | jq -c '.[] | del(.body)'
{"id":5446510102,"url":"https://github.com/cboone/agent-harness-plugins/pull/559#pullrequestreview-5446510102","submittedAt":"2026-10-07T18:19:39Z","commitId":"164797e9ef480c9ad96c329ad9bb15a9432bf750","threadLinks":[4210291616]}
```

## Thread links are the review comment ids the body links to

`threadLinks` is a matching hint: the ids from every `#discussion_r<id>` fragment anywhere in the body, so a concern can be matched to its thread. It is derived from GitHub's URL scheme, not Copilot's layout.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-open-findings-block.json" | jq -c '.[].threadLinks'
[4208108521,4208108618,4208108696,4208486501,4208486618,4208486683]
```

A body that links one thread twice lists it once, and a body with no links has an empty list.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"u","submitted_at":"2026-10-07T00:00:00Z","body":"See [a](https://github.com/o/r/pull/1#discussion_r42) and [b](https://github.com/o/r/pull/1#discussion_r42)."},{"id":2,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"u","submitted_at":"2026-10-07T00:00:01Z","body":"No links here."}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '[.[].threadLinks]'
[[42],[]]
```

## Reviews come back oldest first

```scrut
$ echo '[{"id":2,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"u","submitted_at":"2026-10-07T12:00:00Z","body":"later"},{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"u","submitted_at":"2026-10-07T11:00:00Z","body":"earlier"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '{ids: [.[].id]}'
{"ids":[1,2]}
```

## `--skip` leaves out reviews already read

The resolver passes the review ids its earlier clearing summaries record as read, so a run reads every review no earlier run settled, whenever it arrived.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --skip 6000000002 < "${COPILOT_REVIEW_DATA_DIR}/format-d-previously-missed.json" | jq -c '{ids: [.[].id]}'
{"ids":[6000000003]}
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --skip 6000000002,6000000003 < "${COPILOT_REVIEW_DATA_DIR}/format-d-previously-missed.json" | jq -c '{ids: [.[].id]}'
{"ids":[]}
```

## `--head` always keeps the newest review of the head

The newest review against the named commit comes back even when it was skipped, so every run reads what Copilot currently says about the head. An older review of the same commit stays skipped.

```scrut
$ jq '.[].commit_id = "0123456789abcdef0123456789abcdef01234567"' "${COPILOT_REVIEW_DATA_DIR}/format-d-previously-missed.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --skip 6000000002,6000000003 --head 0123456789abcdef0123456789abcdef01234567 | jq -c '{ids: [.[].id]}'
{"ids":[6000000003]}
```

```scrut
$ jq '.[].commit_id = "0123456789abcdef0123456789abcdef01234567"' "${COPILOT_REVIEW_DATA_DIR}/format-d-previously-missed.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --skip 6000000002,6000000003 --head fedcba9876543210fedcba9876543210fedcba98 | jq -c '{ids: [.[].id]}'
{"ids":[]}
```

When the newest review of the head has a body that is not a string, no older review stands in for it: nothing comes back for the head, and the warning names it even though it was skipped.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"commit_id":"0123456789abcdef0123456789abcdef01234567","submitted_at":"2026-01-01T00:00:01Z","body":"older"},{"id":2,"user":{"login":"copilot-pull-request-reviewer[bot]"},"commit_id":"0123456789abcdef0123456789abcdef01234567","submitted_at":"2026-01-01T00:00:02Z","body":{"text":"x"}}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --skip 1,2 --head 0123456789abcdef0123456789abcdef01234567 2>&1
Warning: skipping review 2: its body is not a string.
[]
```

Malformed values and unknown options fail before anything is read.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --skip 6000000002,x < /dev/null 2>&1
Error: Invalid --skip value '6000000002,x'. Expected review ids separated by commas, such as 5449428489,5449507605.
[1]
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --head main < /dev/null 2>&1
Error: Invalid --head value 'main'. Expected the full 40-character commit SHA.
[1]
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --skip < /dev/null 2>&1
Error: Missing value after --skip
[1]
```

An abbreviated SHA would never equal the full `commit_id` GitHub reports, so it is refused rather than silently dropping the head review. `--head` may be given once; repeated `--skip` values add up.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --head abc1234 < /dev/null 2>&1
Error: Invalid --head value 'abc1234'. Expected the full 40-character commit SHA.
[1]
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --head 0123456789abcdef0123456789abcdef01234567 --head 0123456789abcdef0123456789abcdef01234567 < /dev/null 2>&1
Error: --head given more than once
[1]
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --skip 6000000002 --skip 6000000003 < "${COPILOT_REVIEW_DATA_DIR}/format-d-previously-missed.json" | jq -c '{ids: [.[].id]}'
{"ids":[]}
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews extra < /dev/null 2>&1
Error: Invalid argument 'extra'. Expected '--skip <id,id,...>' or '--head <sha>'.
[1]
```

## Copilot's logins match in any case

Every direct login matches whatever its case, including `Copilot`, the form REST uses for inline comments. A `github-actions[bot]` review never matches, even with a severity tag, because that rule is for thread comments.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"submitted_at":"2026-10-07T00:00:01Z","body":"a"},{"id":2,"user":{"login":"copilot-pull-request-reviewer"},"submitted_at":"2026-10-07T00:00:02Z","body":"b"},{"id":3,"user":{"login":"Copilot"},"submitted_at":"2026-10-07T00:00:03Z","body":"c"},{"id":4,"user":{"login":"github-copilot[bot]"},"submitted_at":"2026-10-07T00:00:04Z","body":"d"},{"id":5,"user":{"login":"github-actions[bot]"},"submitted_at":"2026-10-07T00:00:05Z","body":"[nitpick] e"},{"id":6,"user":{"login":"copilot-helper"},"submitted_at":"2026-10-07T00:00:06Z","body":"f"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '{ids: [.[].id]}'
{"ids":[1,2,3,4]}
```

## Non-Copilot reviews are filtered out

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/non-copilot.json"
[]
```

## Reviews with an unusable author are skipped, not fatal

A null, absent, or malformed `user` yields no login match rather than aborting the run over one review.

```scrut
$ echo '[{"id":1,"user":null,"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"### hi"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews
[]
```

```scrut
$ echo '[{"id":1,"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"### hi"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews
[]
```

```scrut
$ echo '[{"id":1,"user":"ghost","state":"COMMENTED","submitted_at":"x","html_url":"y","body":"### hi"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews
[]
```

```scrut
$ echo '[{"id":1,"user":{"login":7},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"### hi"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews
[]
```

## A review body that is not a string is skipped, not fatal

The skip is named on stderr, and the well-formed review beside it still comes through. `audit` reports the skipped review as uncovered.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/malformed-body.json" 2>&1 >/dev/null
Warning: skipping review 6000000043: its body is not a string.
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/malformed-body.json" 2>/dev/null | jq -c '{ids: [.[].id]}'
{"ids":[6000000042]}
```

Only a Copilot review is named, and only when it is not already skipped by id: a person's review is never read, and a skipped one was settled.

```scrut
$ echo '[{"id":71,"user":{"login":"a-human-reviewer"},"body":{"text":"x"}},{"id":72,"user":{"login":"copilot-pull-request-reviewer[bot]"},"body":{"text":"y"}},{"id":73,"user":{"login":"copilot-pull-request-reviewer[bot]"},"body":{"text":"z"}}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --skip 73 2>&1 >/dev/null
Warning: skipping review 72: its body is not a string.
```

## A null or empty body comes back empty

Every Copilot review is returned, so a caller and `monitor-pr`'s metadata probe agree on which review is newest. An empty body states nothing; any findings the review has are threads that `fetch` reports.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"u","submitted_at":"2026-10-07T00:00:00Z","body":""},{"id":2,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"u","submitted_at":"2026-10-07T00:00:01Z","body":null}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews 2>&1 | jq -c '[.[] | {id, body}]'
[{"id":1,"body":""},{"id":2,"body":""}]
```

## Empty review list

```scrut
$ echo '[]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews
[]
```

## Malformed input fails with a usable message

A failed `gh` call or a hand-piped error payload would otherwise surface as an opaque jq indexing error.

```scrut
$ printf '{' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews 2>&1
Error: Invalid review JSON: could not parse input as JSON.
[1]
```

```scrut
$ echo '{"message":"Not Found"}' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews 2>&1
Error: Invalid review JSON: expected an array of review objects, got object. Pass the output of: gh api repos/OWNER/REPO/pulls/N/reviews
[1]
```

```scrut
$ echo '[1,2]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews 2>&1
Error: Invalid review JSON: every element must be a review object.
[1]
```

## fetch-reviews reads through `gh` and passes its options through

`fetch-reviews` and `fetch` are exercised against `copilot-gh-stub`, installed as `gh` first on `PATH`, which answers from `tests/data/copilot-gh/`.

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" fetch-reviews o r 7 | jq -c '{ids: [.[].id]}'; rm -rf "${stub}"
{"ids":[7100]}
```

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" fetch-reviews o r 7 --skip 7100 | jq -c '{ids: [.[].id]}'; rm -rf "${stub}"
{"ids":[]}
```

A failed read exits nonzero and names the request, so a caller never reads empty output as no reviews.

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" fetch-reviews o r 8 2>&1; echo "exit=$?"; rm -rf "${stub}"
gh: Not Found (HTTP 404)
Error: Failed to fetch reviews for o/r#8. See the gh error above for the cause.
exit=1
```

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" fetch-reviews o r 2>&1; echo "exit=$?"; rm -rf "${stub}"
Error: Usage: resolve-copilot-threads fetch-reviews <owner> <repo> <pr_number> [--skip <ids>] [--head <sha>]
exit=1
```

## fetch returns unresolved Copilot threads with their comment ids

Each comment carries its `databaseId` and `url`, which is how a review body's `threadLinks` are matched to a thread. A resolved thread and a thread a person opened are left out; a `github-actions[bot]` thread with a severity tag is Copilot's; a login matches in any case; and a thread with no line reports `(no-line)`.

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" fetch o r 8 | jq -c '.[] | {id, location, isOutdated, comments: [.comments[] | {author, databaseId, url}]}'; rm -rf "${stub}"
{"id":"PRRT_open","location":"src/cache.js:42","isOutdated":false,"comments":[{"author":"copilot-pull-request-reviewer","databaseId":8001,"url":"https://github.com/o/r/pull/8#discussion_r8001"},{"author":"cboone","databaseId":8002,"url":"https://github.com/o/r/pull/8#discussion_r8002"}]}
{"id":"PRRT_noline","location":"docs/usage.md:(no-line)","isOutdated":true,"comments":[{"author":"Copilot","databaseId":8004,"url":"https://github.com/o/r/pull/8#discussion_r8004"}]}
{"id":"PRRT_actions","location":"src/util.js:3","isOutdated":false,"comments":[{"author":"github-actions[bot]","databaseId":8006,"url":"https://github.com/o/r/pull/8#discussion_r8006"}]}
```

## Help lists the review-body and audit commands

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" --help | grep -E '^  (fetch-reviews|parse-reviews|audit|parse-audit)'
  fetch-reviews <owner> <repo> <pr_number> [--skip <ids>] [--head <sha>]
  parse-reviews [--skip <ids>] [--head <sha>]         Select Copilot reviews from JSON on stdin
  audit <owner> <repo> <pr_number>                    List Copilot items the fetches cannot reach
  parse-audit                                          Audit pull request JSON read from stdin
```

## The surface audit

`fetch` reads unresolved threads Copilot opened and `fetch-reviews` reads its
review bodies. `audit` counts every Copilot item on a pull request by where it
appears and lists any the two do not reach, so feedback that arrives
somewhere new is an entry rather than silence. `parse-audit` is the same join
over saved JSON.

When every Copilot item is reachable, nothing is reported. A summary comment
the resolver posted is not a Copilot item. The inline comment's REST login is
`Copilot`, which matches regardless of case.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit < "${COPILOT_AUDIT_DATA_DIR}/covered.json" | jq -c .
{"surfaces":{"reviews":1,"reviewComments":1,"issueComments":0},"uncovered":[]}
```

A reply inside an unresolved thread a person opened, a review comment that no
thread holds, and a comment on the pull request itself are all out of reach
of the fetch commands, and each is reported. A reply in a resolved thread is
settled, and is not.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit < "${COPILOT_AUDIT_DATA_DIR}/uncovered.json" | jq -c '.uncovered[] | {surface, reason, id}'
{"surface":"review-comment","reason":"reply in a thread Copilot did not open","id":9103}
{"surface":"review-comment","reason":"in no thread","id":9104}
{"surface":"issue-comment","reason":"pull request comment","id":9202}
```

Each entry carries a link and an excerpt, so it can be read without opening
the pull request.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit < "${COPILOT_AUDIT_DATA_DIR}/uncovered.json" | jq -c '.uncovered[0] | {url, path, excerpt}'
{"url":"https://github.com/o/r/pull/1#discussion_r9103","path":"src/cache.js","excerpt":"Yes: entries written before a restart never expire."}
```

A thread `github-actions[bot]` opened with a severity tag is one the thread
fetch treats as Copilot feedback and reports, so the audit judges its opener the
same way, body included, and does not report it a second time.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit < "${COPILOT_AUDIT_DATA_DIR}/actions-opener.json" | jq -c '{surfaces, uncovered}'
{"surfaces":{"reviews":0,"reviewComments":1,"issueComments":0},"uncovered":[]}
```

A Copilot review whose body is not a string is one `fetch-reviews` cannot
return, so the audit lists it for a read by hand.

```scrut
$ echo '{"reviews":[{"id":61,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"u61","body":{"text":"x"}},{"id":62,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"u62","body":"fine"}],"reviewComments":[],"issueComments":[],"threads":[]}' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit | jq -c .
{"surfaces":{"reviews":2,"reviewComments":0,"issueComments":0},"uncovered":[{"surface":"review","reason":"body is not a string","id":61,"url":"u61","path":null,"excerpt":""}]}
```

The input must carry all four arrays, and every element the join indexes into
must be an object, so a malformed one is named rather than reported as a raw
jq error.

```scrut
$ echo '{"reviews":[]}' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit 2>&1
Error: Invalid audit JSON: expected an object with reviews, reviewComments, issueComments and threads arrays.
[1]
```

```scrut
$ echo '{"reviews":[1],"reviewComments":[],"issueComments":[],"threads":[]}' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit 2>&1
Error: Invalid audit JSON: reviews: every element must be an object.
[1]
```

```scrut
$ echo '{"reviews":[],"reviewComments":[],"issueComments":[],"threads":[{"isResolved":false}]}' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit 2>&1
Error: Invalid audit JSON: threads: every element must be an object with a comments array of objects.
[1]
```

```scrut
$ echo '{"reviews":[],"reviewComments":[1],"issueComments":[],"threads":[]}' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit 2>&1
Error: Invalid audit JSON: reviewComments: every element must be an object.
[1]
```

```scrut
$ echo '{"reviews":[],"reviewComments":[],"issueComments":["x"],"threads":[]}' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit 2>&1
Error: Invalid audit JSON: issueComments: every element must be an object.
[1]
```

```scrut
$ echo '{"reviews":[],"reviewComments":[],"issueComments":[],"threads":[{"isResolved":false,"comments":[1]}]}' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit 2>&1
Error: Invalid audit JSON: threads: every element must be an object with a comments array of objects.
[1]
```

A login or body that is not a string inside an element reads as empty, so one
malformed comment is judged rather than aborting the join.

```scrut
$ echo '{"reviews":[],"reviewComments":[{"id":1,"user":{"login":"github-actions[bot]"},"body":5}],"issueComments":[{"id":2,"user":{"login":7},"body":null}],"threads":[]}' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit | jq -c '{surfaces, uncovered}'
{"surfaces":{"reviews":0,"reviewComments":0,"issueComments":0},"uncovered":[]}
```

`audit` itself is exercised against `copilot-gh-stub`. On pull request 7 the
only thread was opened by `github-actions[bot]` with a severity tag, so the
opener's body has to come through the thread fetch for it to count as Copilot
feedback the thread fetch reports.

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" audit o r 7 | jq -c .; rm -rf "${stub}"
{"surfaces":{"reviews":1,"reviewComments":1,"issueComments":0},"uncovered":[]}
```

A thread query that finds no such pull request fails loudly. Read as an empty
index, it would report every Copilot review comment as being in no thread.

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" audit o r 9 2>&1; echo "exit=$?"; rm -rf "${stub}"
Error: Invalid response while fetching threads for o/r#9: no such pull request.
exit=1
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit extra < /dev/null 2>&1
Error: Usage: resolve-copilot-threads parse-audit (reads pull request JSON on stdin)
[1]
```

## The copy `monitor-pr` ships runs the same way

`monitor-pr` runs this script's read-only commands in its snapshot step. A
`cmp` testcase in `repo-tooling.md` holds the two copies byte-identical; these
run the shipped file, so a copy that matches but cannot execute still fails.

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-missed-badges.json" | jq -c '{ids: [.[].id]}'
{"ids":[5449759699]}
```

## The step 3 probe filters pin their own output shapes

`monitor-pr` does not print the whole `fetch-reviews` result on every tick.
Its per-tick filter selects the one review the metadata probe named and
projects three fields, with no body text. These testcases run the filters
exactly as the skill documents them, over `parse-reviews` so no authenticated
`gh` is needed.

The metadata probe matches Copilot's logins in any case, as `fetch-reviews` does, so the two agree on which review is newest.

```scrut
$ echo '[[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"commit_id":"a","submitted_at":"x","state":"COMMENTED"},{"id":2,"user":{"login":"Copilot"},"commit_id":"b","submitted_at":"y","state":"COMMENTED"},{"id":3,"user":{"login":"a-human-reviewer"},"commit_id":"c","submitted_at":"z","state":"COMMENTED"}]]' | jq -c '[.[][] | select((.user.login? // "") as $login | ($login | type) == "string" and (["copilot-pull-request-reviewer", "copilot-pull-request-reviewer[bot]", "copilot", "github-copilot[bot]"] | any(. == ($login | ascii_downcase))))] | last | {id, commit_id, submitted_at, state}'
{"id":2,"commit_id":"b","submitted_at":"y","state":"COMMENTED"}
```

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-zero-open-line.json" | jq -c --argjson review_id 5446510102 '[.[] | select(.id == $review_id)] | last | {id, url, commitId}'
{"id":5446510102,"url":"https://github.com/cboone/agent-harness-plugins/pull/559#pullrequestreview-5446510102","commitId":"164797e9ef480c9ad96c329ad9bb15a9432bf750"}
```

A review id the result does not carry, which is what a review whose body is
not a string or a wrong id produces, yields an all-null object rather than nothing. The skill documents
this shape so a null `id` is read as an absent answer, never as a review.

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-zero-open-line.json" | jq -c --argjson review_id 6000000099 '[.[] | select(.id == $review_id)] | last | {id, url, commitId}'
{"id":null,"url":null,"commitId":null}
```

The classification filter returns the complete body, never a prefix: the text
that tells a notice from a review can sit anywhere in it. Here the notice
sentence follows more than 600 characters of other text, and comes through
whole at the end.

```scrut
$ jq -n '[{id: 1, user: {login: "copilot-pull-request-reviewer[bot]"}, html_url: "u", submitted_at: "2026-10-07T00:00:00Z", body: (("Preamble. " * 70) + "\n\nCopilot encountered an error and was unable to review this pull request.")}]' | "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c --argjson review_id 1 '[.[] | select(.id == $review_id)] | last | {id, body}' | jq -r '.id, (.body | length), (.body | split("\n") | last)'
1
774
Copilot encountered an error and was unable to review this pull request.
```

A review the result does not carry yields a null `id` and `body`, and a failed
read yields no output at all. Neither is a body to classify.

```scrut
$ echo '[]' | "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c --argjson review_id 1 '[.[] | select(.id == $review_id)] | last | {id, body}'
{"id":null,"body":null}
```

```scrut
$ printf '' | jq -c --argjson review_id 1 '[.[] | select(.id == $review_id)] | last | {id, body}'
```

The audit filter reduces `audit` to the items step 7b records as processed,
each named by its surface, because ids from different GitHub tables can
coincide. The `audited` field is what tells an empty audit from a failed one:
a failed `audit` emits nothing, and the filter then emits nothing too, so the
watch reads "not observed" rather than "nothing uncovered".

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-audit < "${COPILOT_AUDIT_DATA_DIR}/uncovered.json" | jq -c '{audited: true, items: [(.uncovered // error("no uncovered"))[] | "\(.surface):\(.id)"]}'
{"audited":true,"items":["review-comment:9103","review-comment:9104","issue-comment:9202"]}
```

```scrut
$ printf '' | jq -c '{audited: true, items: [(.uncovered // error("no uncovered"))[] | "\(.surface):\(.id)"]}'
```

An audit result missing its list is a failed probe, not an empty one: the
filter emits nothing.

```scrut
$ echo '{"surfaces":{}}' | jq -c '{audited: true, items: [(.uncovered // error("no uncovered"))[] | "\(.surface):\(.id)"]}' 2> /dev/null
[5]
```

The thread-side filter reduces `fetch` the same way, to a count plus locations.

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" fetch o r 8 | jq -c '{openThreads: length, locations: [.[].location]}'; rm -rf "${stub}"
{"openThreads":3,"locations":["src/cache.js:42","docs/usage.md:(no-line)","src/util.js:3"]}
```

```scrut
$ echo '[]' | jq -c '{openThreads: length, locations: [.[].location]}'
{"openThreads":0,"locations":[]}
```
