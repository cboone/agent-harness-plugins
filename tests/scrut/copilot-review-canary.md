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
## Resolved-round leads not on the no-finding list
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

A resolved-only round whose lead is not a known no-finding sentence costs a
read. A sentence Copilot writes word for word on two different pull requests
is boilerplate: a reworded no-finding sentence the parser list should learn,
or a fixed advisory.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" 2> /dev/null | grep -F 'need attention'
- "One or more issues need attention before approval.": 2 pull requests, for example https://github.com/o/r/pull/1#pullrequestreview-6000000035
```

Copilot restates its own lead from round to round on one pull request, so the
same sentence twice there is not boilerplate.

```scrut
$ jq '[.[] | select(.number == 5) | .reviews += (.reviews | map(.id = 6000000098))]' "${COPILOT_CANARY_DATA_DIR}/findings.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null
```

Only a resolved-only round counts. The same prose lead repeated on rounds that
list open threads is ordinary prose about those threads, and this sample is
clean.

```scrut
$ jq '[.[] | select(.number == 5 or .number == 6) | .reviews[].body |= sub("<details>\n<summary><strong>Resolved since last review"; "<details open>\n<summary><strong>Open (1)</strong></summary>\n\n- <picture><img alt=\"Low severity\"></picture> [A thread](#discussion_r9) · New\n</details>\n\n<details>\n<summary><strong>Resolved since last review")]' "${COPILOT_CANARY_DATA_DIR}/findings.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null
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

```scrut
$ echo '[{"repo":"a/b","number":1,"reviews":[1],"audit":{"uncovered":[]}}]' | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null
# Copilot review canary

Sampled 0 Copilot reviews on 1 pull request.

Nothing was analyzed: the sample holds no Copilot reviews. Check the --repo, --author and --since values.

## Pull requests the parser could not read

- a/b#1: Error: Invalid review JSON: every element must be a review object.
[2]
```

```scrut
$ jq '. + [{"repo":"a/b","number":2,"reviews":[],"audit":null,"fetchError":"gh: Not Found (HTTP 404)"},{"repo":"a/b","number":3,"reviews":[],"audit":{"error":"Error: GraphQL error while fetching threads: rate limited"}},{"repo":"a/b","number":4,"reviews":[],"audit":null}]' "${COPILOT_CANARY_DATA_DIR}/clean.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null
# Copilot review canary

Sampled 1 Copilot review on 4 pull requests.

## Pull requests whose reviews could not be fetched

- a/b#2: gh: Not Found (HTTP 404)

## Pull requests with no surface audit

- a/b#3: Error: GraphQL error while fetching threads: rate limited
- a/b#4: no audit in the sample
[2]
```

A review the parser skipped is reported from the parser's own warning, so a
malformed review cannot leave the sample smaller without a trace.

```scrut
$ jq '.[0].reviews += [{"id":7,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"y","body":12345}]' "${COPILOT_CANARY_DATA_DIR}/clean.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" 2> /dev/null | grep -F 'skipping'
- o/r#1: Warning: skipping review 7: its body is not a string.
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

## Skeletons carry layout, not prose

A skeleton replaces counts, paths, inline code, link text, badges and table
cells, and drops prose, so two reviews with the same layout produce the same
lines. Headings, comment markers, labels, italic lines and table headers are
kept as written, because their wording is the layout; on Copilot reviews they
are its own boilerplate.

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
[1]
```

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" --repo nope 2>&1
copilot-review-canary: --repo needs OWNER/REPO, got nope.
[1]
```

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" --author octocat --since yesterday 2>&1
copilot-review-canary: --since needs a YYYY-MM-DD date.
[1]
```

```scrut
$ echo '{}' | "${COPILOT_REVIEW_CANARY_BIN}" analyze 2>&1
copilot-review-canary: Invalid sample: expected an array of {repo, number, reviews, audit} objects.
[1]
```

```scrut
$ echo '[]' | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline /nonexistent/baseline.json 2>&1
copilot-review-canary: Baseline not found: /nonexistent/baseline.json
[1]
```

The canary checks the jq version itself, so a jq too old for the resolver is
named once rather than failing every pull request in turn.

```scrut
$ fake="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '#!/usr/bin/env bash\necho jq-1.6\n' > "${fake}/jq" && chmod +x "${fake}/jq" && echo '[]' | PATH="${fake}:${PATH}" "${COPILOT_REVIEW_CANARY_BIN}" analyze 2>&1; rm -rf "${fake}"
copilot-review-canary: jq 1.7 or later is required, found jq-1.6.
```
