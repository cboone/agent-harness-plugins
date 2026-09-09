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
