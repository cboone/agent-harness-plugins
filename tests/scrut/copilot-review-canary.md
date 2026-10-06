# Copilot review canary

Tests for `bin/copilot-review-canary`, which samples recent Copilot reviews and
reports layout changes the parser in `resolve-copilot-threads` has not caught
up with. Its gathering mode needs an authenticated `gh`, so these cases run
`analyze` over saved samples, which is the same analysis without the network.
Each sample is a JSON array of `{repo, number, reviews, audit}`.

The fixtures carry their own baseline, so these cases do not move when the
committed baseline in `bin/data/` is refreshed.

## A clean sample prints nothing

Like `version-audit`, empty output means there is nothing to look at.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/clean.json"
```

## Each kind of change gets its own section

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" | grep -E '^(#|Sampled)'
# Copilot review canary
Sampled 5 Copilot reviews on 4 pull requests.
## Signals the parser left unaccounted
## Bodies that are neither a review nor a known notice
## Copilot items the fetches cannot reach
## Resolved-round leads not on the no-finding list
## Layout elements not in the baseline
```

A signal the census left unaccounted is reported with its review, kind, line
and region, so it can be found without rerunning anything.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" | grep -F 'section-count'
- https://github.com/o/r/pull/1#pullrequestreview-6000000040: `section-count` at line 19, in Also worth checking: `<summary><strong>Also worth checking (2)</strong></summary>`
```

A body that is neither a review nor a known notice is reported with its text.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" | grep -F 'still reviewing'
- https://github.com/o/r/pull/1#pullrequestreview-6000000038: `Copilot is still reviewing this pull request. Findings will appear here when the review completes.`
```

A Copilot item the surface audit found out of the fetches' reach is reported
from the sample's `audit`.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" | grep -F 'issuecomment'
- https://github.com/o/r/pull/4#issuecomment-9202 (issue-comment, pull request comment): Copilot reviewed this pull request and found one issue in the release workflow.
```

## A recurring resolved-round lead is reported, a one-off is not

A resolved-only round whose lead is not a known no-finding sentence costs a
read. A sentence Copilot repeats word for word is boilerplate: a reworded
no-finding sentence the parser list should learn, or a fixed advisory.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" | grep -F 'need attention'
- "One or more issues need attention before approval.": 2 reviews, for example https://github.com/o/r/pull/1#pullrequestreview-6000000035
```

Most such leads are prose findings that never repeat, so one seen once is not
reported.

```scrut
$ jq '[.[] | select(.number == 5) | .reviews |= .[0:1]]' "${COPILOT_CANARY_DATA_DIR}/findings.json" | "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json"
```

## A new layout element is reported before it carries a finding

This section lists threads, so the parser reads it correctly and the census
finds nothing wrong. It is still new, and the baseline comparison is what
makes it visible the first time it appears.

```scrut
$ "${COPILOT_REVIEW_CANARY_BIN}" analyze --baseline "${COPILOT_CANARY_DATA_DIR}/baseline.json" < "${COPILOT_CANARY_DATA_DIR}/findings.json" | grep -F 'Deferred'
- `<summary><strong>Deferred (N)</strong></summary>`: 1 time, first 2026-10-06, for example https://github.com/o/r/pull/1#pullrequestreview-6000000039
```

## Skeletons carry layout, never content

A skeleton replaces counts, paths, link text, badges and prose, so two reviews
with the same layout produce the same lines and a baseline built from private
repositories quotes nothing from them.

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
$ printf '[{"repo":"o/r","number":1,"reviews":[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"y","submitted_at":"2026-10-06T00:00:00Z","body":"| File | Summary |\\n|---|---|\\n| `src/secret-name.js` | Handles the private thing. **Moderate (2 votes):** fix it. |\\n| other/path.md | Docs. |"}],"audit":null}]' | "${COPILOT_REVIEW_CANARY_BIN}" skeletons | jq -r '.skeletons[]'
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
