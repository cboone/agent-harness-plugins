# Copilot review-body parsing

Tests for `resolve-copilot-threads parse-reviews`, which extracts Copilot findings from PR review bodies.

Copilot files some findings in a review body instead of an inline thread. Those have no thread id, so a `reviewThreads` query cannot see them. The fixtures are real Copilot review bodies covering every layout observed in the wild.

## Oldest layout: comments suppressed due to low confidence

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-a.json" | jq -c '[.[].findings[] | .location]'
["plugins/notify/opencode/index.ts:252"]
```

## Mid layout: suppressed comments summary

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-b.json" | jq -c '[.[].findings[] | .location]'
["src/ring_race.zig:395","src/ring_race.zig:378"]
```

## Current layout: suppressed comments heading inside review details

The `**Previously missed (1)**` subheading sits between the section heading and the first finding. It must not be parsed as a finding of its own.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-c.json" | jq -c '[.[].findings[] | .location]'
[".github/workflows/ci.yml:218",".github/workflows/ci.yml:225"]
```

## Path and line are split out of the heading

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-c.json" | jq -c '.[0].findings[0] | {path, line}'
{"path":".github/workflows/ci.yml","line":218}
```

## Overview v2 previously missed findings

Nested `Previously missed` details are body-only findings. Open thread links
and resolved findings in the same review are not emitted again.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-previously-missed.json" | jq -c '[.[] | {id, url, findings}]'
[{"id":6000000002,"url":"https://github.com/o/r/pull/1#pullrequestreview-6000000002","findings":[{"location":"src/report/render.js:197","path":"src/report/render.js","line":197,"severity":"Medium","body":"Handle null timeZone before constructing the formatter\n\nPassing null as the formatter time zone throws. Normalize null to undefined before constructing the formatter."}]},{"id":6000000003,"url":"https://github.com/o/r/pull/1#pullrequestreview-6000000003","findings":[{"location":"src/domain/report-contract.js:171","path":"src/domain/report-contract.js","line":171,"severity":"Medium","body":"Reject sparse arrays\n\nReject missing indexed elements so malformed input cannot bypass the contract."}]}]
```

## Overview v2 table findings

Each finding appended to a file-summary cell becomes a separate line-less
entry. Formatting U+200B characters are removed from the path.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":false,"findings":[{"location":"src/handlers/example.js","path":"src/handlers/example.js","line":null,"severity":"Moderate","body":"validate optional replacement values"},{"location":"src/handlers/example.js","path":"src/handlers/example.js","line":null,"severity":"Nit","body":"narrow the error documentation"}]}
```

## Overview v2 table findings survive unusual text

An item runs from its severity token to the next one. A semicolon inside the
finding text, a missing final period, an unfamiliar severity name, and an
escaped pipe must not drop or truncate a finding. After the first item, only a
token that follows the separator, a semicolon and a space, opens another, so a
severity label quoted in a finding's prose stays in its text instead of
splitting it.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-table-edge.json" | jq -c '.[0].findings[] | {location, severity, body}'
{"location":"src/parsers/split.js","severity":"Moderate","body":"split on `a; b` correctly"}
{"location":"src/parsers/split.js","severity":"Critical","body":"reject naïve input"}
{"location":"src/parsers/split.js","severity":"Nit","body":"rename the helper"}
{"location":"src/parsers/match.js","severity":"Low","body":"handle `a | b` alternation"}
{"location":"src/parsers/label.js","severity":"Moderate","body":"keep the literal Nit (1 vote): prefix intact. Low (2 votes): appears in the same sentence"}
{"location":"src/parsers/label.js","severity":"Nit","body":"trim the comment"}
```

## Overview v2 findings despite a Findings: None header

The `**Findings:** None` header can contradict the verdict. Parsed findings
come from the body sections, never from that header.

```scrut
$ jq -s 'add' "${COPILOT_REVIEW_DATA_DIR}/format-d.json" "${COPILOT_REVIEW_DATA_DIR}/format-d-previously-missed.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '[.[] | select(.reviewBody | contains("**Findings:** None")) | {id, findings: (.findings | length)}]'
[{"id":6000000001,"findings":2},{"id":6000000003,"findings":1}]
```

## Overview v2 repeated findings keep their identity

Copilot repeats an unaddressed finding in later reviews. The review ID and URL
change, but the path, line, and body that identify the finding do not, so a
prior disposition can be matched against the repeat.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-repeated.json" | jq -c '{ids: [.[].id], identities: [.[] | [.findings[] | {path, line, body}]] | unique | length}'
{"ids":[6000000008,6000000009],"identities":1}
```

## Overview v2 clean verdict

The verified clean verdict can have no body findings while listing entries
resolved since the prior review. Those resolved entries are not actionable.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-clean.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings}'
{"verdict":"### 🟢 Approval recommended","hasFormatDrift":false,"findings":[]}
```

A CRLF body still yields the clean verdict, rather than a heading with a
trailing carriage return that reads as drift.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"<!-- ccr-overview-v2 -->\r\n\r\n### 🟢 Approval recommended\r\n\r\nNo issues."}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {verdict, hasFormatDrift}'
{"verdict":"### 🟢 Approval recommended","hasFormatDrift":false}
```

## Overview v2 open threads explain a non-clean verdict

Inline threads listed under `Open (N)` are reported by the thread fetch. A
review whose only findings are open threads has no body findings and is not
format drift.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-open-only.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings}'
{"verdict":"### 🟡 Changes recommended","hasFormatDrift":false,"findings":[]}
```

## Overview v2 format drift

A non-clean verdict cannot become a clean result merely because the parser
does not recognize the finding representation. The complete body remains
available for manual inspection.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-drift.json" | jq -c '.[0] | {verdict, hasSuppressedMarker, hasFormatDrift, hasReviewBody: (.reviewBody | contains("data-finding")), findings}'
{"verdict":"### 🔵 Needs a closer look","hasSuppressedMarker":false,"hasFormatDrift":true,"hasReviewBody":true,"findings":[]}
```

## Finding bodies keep their prose and fenced context

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-a.json" | jq -r '.[0].findings[0].body' | head -1
* `truncate()` slices to `limit` and then appends an ellipsis, so the returned string can be `limit + 1` characters long. Since the `TASK_LIMIT_*` constants are treated as strict body-length budgets elsewhere in this file, adjust truncation to keep the final length within `limit` (and handle small limits consistently).
```

The trailing context block Copilot quotes under the prose is preserved, so the body carries an opening and a closing fence.

````scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-a.json" | jq -r '.[0].findings[0].body' | grep -c '^```'
2
````

The last finding in a section stops where the section does. Closing `</details>` tags and the `Files reviewed` trailer belong to the review, not to the finding.

```scrut
$ jq -s 'add' "${COPILOT_REVIEW_DATA_DIR}/format-a.json" "${COPILOT_REVIEW_DATA_DIR}/format-b.json" "${COPILOT_REVIEW_DATA_DIR}/format-c.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '[.[] | .findings[-1].body | test("</details>|Files reviewed")]'
[false,false,false]
```

A bold location line outside a suppressed section is prose, not a finding.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"## Pull request overview\n\n**src/lib/heading.js:12**\n\nProse that names a location."}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '[.[] | {hasSuppressedMarker, findings: (.findings | length)}]'
[{"hasSuppressedMarker":false,"findings":0}]
```

## Headline captures the verdict and drops the boilerplate

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-c.json" | jq -r '.[0].headline' | head -1
### 🟢 Approval recommended
```

## A review with no suppressed section reports no marker

Its body still carries several `<details>` blocks, so this guards against a false positive on ordinary reviews.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/no-suppressed.json" | jq -c '[.[] | {hasSuppressedMarker, findings: (.findings | length)}]'
[{"hasSuppressedMarker":false,"findings":0}]
```

## A file-summaries table mentioning the phrase is not a section

Copilot opens most reviews with a table describing every changed file, so a PR that touches code about suppressed comments gets a row quoting the phrase. A section is never announced from inside a table, so table rows must not open one. This fixture is the real review Copilot left on the PR that added this command, which tripped exactly that case.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/file-summaries-mention.json" | jq -c '[.[] | {hasSuppressedMarker, findings: (.findings | length)}]'
[{"hasSuppressedMarker":false,"findings":0}]
```

## Format drift is reported, not swallowed

A body that announces suppressed comments but uses an unrecognized interior layout yields a true marker with no structured findings. Callers must fall back to the raw `suppressed` slice rather than concluding there is no feedback.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/drift.json" | jq -c '[.[] | {hasSuppressedMarker, findings: (.findings | length)}]'
[{"hasSuppressedMarker":true,"findings":0}]
```

Legacy suppressed-section drift also sets the broader drift signal.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/drift.json" | jq -c '[.[] | {hasSuppressedMarker, hasFormatDrift, findings: (.findings | length)}]'
[{"hasSuppressedMarker":true,"hasFormatDrift":true,"findings":0}]
```

The slice keeps the line that announced the section, so a caller reading it can see what opened it.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/drift.json" | jq -r '.[0].suppressed' | head -1
### Suppressed comments (1)
```

## An announced section with no interior still reports drift

`hasSuppressedMarker` is computed from the body, not from the slice contents. Deriving it from the slice would report `false` whenever a section is announced but captures no interior lines, silently disarming the drift detector in exactly the case it exists to catch.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/empty-section.json" | jq -c '[.[] | {hasSuppressedMarker, findings: (.findings | length)}]'
[{"hasSuppressedMarker":true,"findings":0}]
```

Even then the slice is non-empty, because the announcing line is retained.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/empty-section.json" | jq -r '.[0].suppressed'
### Suppressed comments (1)
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

## parse-reviews takes no arguments

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews extra < /dev/null 2>&1
Error: Usage: resolve-copilot-threads parse-reviews (reads review JSON on stdin)
[1]
```

`fetch-reviews` is not exercised here: it requires an authenticated `gh`, which the test environment does not have. `parse-reviews` is the seam that makes the parsing testable without one.

## Help lists the review-body commands

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" --help | grep -E '^  (fetch-reviews|parse-reviews)'
  fetch-reviews <owner> <repo> <pr_number>            Fetch Copilot review-body findings
  parse-reviews                                        Normalize review JSON read from stdin
```

## The copy `monitor-pr` ships parses the same way

`monitor-pr` runs this script's read-only commands in its snapshot step, to see
whether a current-head Copilot review left findings or format drift before it
decides whether to dispatch to `resolve-copilot-pr-feedback`. A `cmp` testcase
in `repo-tooling.md` holds the two copies byte-identical; these two run the
shipped file, so a copy that matches but cannot execute still fails.

They also pin the two answers the watch reads. A clean review yields no
findings and no drift, which is the only shape that lets the Copilot axis pass.

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-clean.json" | jq -c '.[0] | {hasFormatDrift, findings: (.findings | length)}'
{"hasFormatDrift":false,"findings":0}
```

A drift-only review yields no findings either, and the watch must not read that
zero as clean. `hasFormatDrift` is what separates the two.

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-drift.json" | jq -c '.[0] | {hasFormatDrift, findings: (.findings | length)}'
{"hasFormatDrift":true,"findings":0}
```

## The step 3 selection filter pins its own output shape

`monitor-pr` does not read the whole `fetch-reviews` result. It selects the one
review the metadata probe named and projects four fields, because the raw result
carries every Copilot review on the PR with its complete body and the watch
prints this on every tick. These testcases run the filter exactly as the skill
documents it, over `parse-reviews` so no authenticated `gh` is needed.

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-clean.json" | jq -c --argjson review_id 6000000004 '[.[] | select(.id == $review_id)] | last | {id, url, hasFormatDrift, findings: (.findings | length)}'
{"id":6000000004,"url":"https://github.com/o/r/pull/1#pullrequestreview-6000000004","hasFormatDrift":false,"findings":0}
```

A review id the result does not carry, which is what an empty review body
produces, does **not** yield `null`. jq builds the object from `null` anyway, and
`.findings | length` over an absent review is `0` rather than an error. The skill
documents this shape so a reader does not mistake the all-null object for a
review that parsed cleanly: a null `hasFormatDrift` is an absent answer, not
`false`.

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-clean.json" | jq -c --argjson review_id 6000000099 '[.[] | select(.id == $review_id)] | last | {id, url, hasFormatDrift, findings: (.findings | length)}'
{"id":null,"url":null,"hasFormatDrift":null,"findings":0}
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
