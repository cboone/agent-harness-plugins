# Copilot review bodies

Tests for `resolve-copilot-threads parse-reviews`, which selects Copilot's reviews from pull request review JSON and returns each one's complete raw body for the caller to read.

Copilot files some findings in a review body instead of an inline thread. Those have no thread id, so a `reviewThreads` query cannot see them. Copilot also reshapes the layout of those bodies often, so the command never parses the layout: it passes the text through. The fixtures are Copilot review bodies in each layout observed so far.

## Every layout comes back byte for byte

Whatever the layout, the body a caller reads is exactly the body Copilot wrote. This is the property that keeps a new layout from changing what the command reports.

```scrut
$ for f in format-a format-b format-c format-d format-d-bold-votes format-d-open-findings-block format-d-zero-open-line format-d-previously-missed format-d-missed-badges notice-error notice-no-files; do printf '%s ' "${f}"; "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/${f}.json" | jq -c --slurpfile raw "${COPILOT_REVIEW_DATA_DIR}/${f}.json" '[.[] as $o | $raw[0][] | select(.id == $o.id) | .body == $o.body] | (length > 0 and all)'; done
format-a true
format-b true
format-c true
format-d true
format-d-bold-votes true
format-d-open-findings-block true
format-d-zero-open-line true
format-d-previously-missed true
format-d-missed-badges true
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

## `--since` keeps reviews submitted at or after a time

The resolver passes the time of its newest earlier summary, so a run reads only the reviews no earlier run covered. A review submitted at exactly that time is kept.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --since 2026-09-18T13:00:00Z < "${COPILOT_REVIEW_DATA_DIR}/format-d-previously-missed.json" | jq -c '{ids: [.[].id]}'
{"ids":[6000000003]}
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --since 2026-09-18T13:00:01Z < "${COPILOT_REVIEW_DATA_DIR}/format-d-previously-missed.json" | jq -c '{ids: [.[].id]}'
{"ids":[]}
```

Only the form GitHub writes is accepted, because comparing the strings orders the times only when both share that form.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --since 2026-09-18 < /dev/null 2>&1
Error: Invalid --since timestamp '2026-09-18'. Expected UTC in the form YYYY-MM-DDTHH:MM:SSZ, as GitHub reports it.
[1]
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews --after 2026-09-18T13:00:00Z < /dev/null 2>&1
Error: Invalid argument '--after'. Expected '--since <timestamp>' or no arguments.
[1]
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

## A review body that is not a string is skipped, not fatal

The skip is named on stderr, and the well-formed review beside it still comes through.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/malformed-body.json" 2>&1 >/dev/null
Warning: skipping review 6000000043: its body is not a string.
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/malformed-body.json" 2>/dev/null | jq -c '{ids: [.[].id]}'
{"ids":[6000000042]}
```

## An empty body is skipped without a warning

Its inline comments, if any, are threads that `fetch` reports.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"u","submitted_at":"2026-10-07T00:00:00Z","body":""}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews 2>&1
[]
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

## parse-reviews takes only `--since`

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews extra < /dev/null 2>&1
Error: Usage: resolve-copilot-threads parse-reviews [--since <timestamp>] (reads review JSON on stdin)
[1]
```

## fetch-reviews passes `--since` through

`fetch-reviews` is exercised against `copilot-gh-stub`, installed as `gh` first on `PATH`, which answers from `tests/data/copilot-gh/`.

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" fetch-reviews o r 7 | jq -c '{ids: [.[].id]}'; rm -rf "${stub}"
{"ids":[7100]}
```

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" fetch-reviews o r 7 --since 2026-09-18T14:00:01Z | jq -c '{ids: [.[].id]}'; rm -rf "${stub}"
{"ids":[]}
```

```scrut
$ stub="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${COPILOT_GH_STUB_BIN}" "${stub}/gh" && STUB_COPILOT_GH_DIR="${COPILOT_GH_DATA_DIR}" PATH="${stub}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" fetch-reviews o r 7 extra 2>&1; echo "exit=$?"; rm -rf "${stub}"
Error: Usage: resolve-copilot-threads fetch-reviews <owner> <repo> <pr_number> [--since <timestamp>]
exit=1
```

## Help lists the review-body and audit commands

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" --help | grep -E '^  (fetch-reviews|parse-reviews|audit|parse-audit)'
  fetch-reviews <owner> <repo> <pr_number> [--since <timestamp>]
  parse-reviews [--since <timestamp>]                 Select Copilot reviews from JSON on stdin
  audit <owner> <repo> <pr_number>                    List Copilot items the fetches cannot reach
  parse-audit                                          Audit pull request JSON read from stdin
```

## The surface audit

`fetch` reads unresolved threads Copilot opened and `fetch-reviews` reads its
review bodies. `audit` lists every Copilot item on a pull request by where it
appears and reports any the two do not reach, so feedback that arrives
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

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-zero-open-line.json" | jq -c --argjson review_id 5446510102 '[.[] | select(.id == $review_id)] | last | {id, url, commitId}'
{"id":5446510102,"url":"https://github.com/cboone/agent-harness-plugins/pull/559#pullrequestreview-5446510102","commitId":"164797e9ef480c9ad96c329ad9bb15a9432bf750"}
```

A review id the result does not carry, which is what an empty review body
produces, yields an all-null object rather than nothing. The skill documents
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
$ jq -n '[{id: 1, user: {login: "copilot-pull-request-reviewer[bot]"}, html_url: "u", submitted_at: "2026-10-07T00:00:00Z", body: (("Preamble. " * 70) + "\n\nCopilot encountered an error and was unable to review this pull request.")}]' | "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -r --argjson review_id 1 '.[] | select(.id == $review_id) | .body' | awk '{ n += length($0) + 1 } END { print n; print $0 }'
775
Copilot encountered an error and was unable to review this pull request.
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
`fetch` needs GraphQL credentials, so this runs the filter over the shape that
command returns.

```scrut
$ echo '[{"id":"PRRT_a","location":"src/foo.ts:42"},{"id":"PRRT_b","location":"lib/bar.js:(no-line)"}]' | jq -c '{openThreads: length, locations: [.[].location]}'
{"openThreads":2,"locations":["src/foo.ts:42","lib/bar.js:(no-line)"]}
```

```scrut
$ echo '[]' | jq -c '{openThreads: length, locations: [.[].location]}'
{"openThreads":0,"locations":[]}
```
