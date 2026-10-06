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
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-previously-missed.json" | jq -c '[.[] | {id, url, findings: [.findings[] | select(.source != "lead")]}]'
[{"id":6000000002,"url":"https://github.com/o/r/pull/1#pullrequestreview-6000000002","findings":[{"location":"src/report/render.js:197","path":"src/report/render.js","line":197,"severity":"Medium","body":"Handle null timeZone before constructing the formatter\n\nPassing null as the formatter time zone throws. Normalize null to undefined before constructing the formatter.","source":"previously-missed","region":"Previously missed"}]},{"id":6000000003,"url":"https://github.com/o/r/pull/1#pullrequestreview-6000000003","findings":[{"location":"src/domain/report-contract.js:171","path":"src/domain/report-contract.js","line":171,"severity":"Medium","body":"Reject sparse arrays\n\nReject missing indexed elements so malformed input cannot bypass the contract.","source":"previously-missed","region":"Previously missed"}]}]
```

## Overview v2 table findings

Each finding appended to a file-summary cell becomes a separate line-less
entry. Formatting U+200B characters are removed from the path.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings: [.findings[] | select(.source != "lead")]}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":false,"findings":[{"location":"src/handlers/example.js","path":"src/handlers/example.js","line":null,"severity":"Moderate","body":"validate optional replacement values","source":"table","region":"What changed in this PR"},{"location":"src/handlers/example.js","path":"src/handlers/example.js","line":null,"severity":"Nit","body":"narrow the error documentation","source":"table","region":"What changed in this PR"}]}
```

## Overview v2 table findings survive unusual text

An item runs from its severity token to the next one. A semicolon inside the
finding text, a missing final period, an unfamiliar severity name, and an
escaped pipe must not drop or truncate a finding. After the first item, only a
token that follows an item separator, a semicolon or a period and then a
space, opens another, so a severity label quoted mid-sentence in a finding's
prose stays in its text. A label right after a period cannot be told apart
from the next item, because Copilot also writes items as sentences, so it
splits: an extra finding gets read, where the opposite rule would merge two.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-table-edge.json" | jq -c '.[0].findings[] | select(.source != "lead") | {location, severity, body}'
{"location":"src/parsers/split.js","severity":"Moderate","body":"split on `a; b` correctly"}
{"location":"src/parsers/split.js","severity":"Critical","body":"reject naïve input"}
{"location":"src/parsers/split.js","severity":"Nit","body":"rename the helper"}
{"location":"src/parsers/match.js","severity":"Low","body":"handle `a | b` alternation"}
{"location":"src/parsers/label.js","severity":"Moderate","body":"keep the literal Nit (1 vote): prefix intact"}
{"location":"src/parsers/label.js","severity":"Low","body":"appears in the same sentence"}
{"location":"src/parsers/label.js","severity":"Nit","body":"trim the comment"}
```

## Overview v2 findings despite a Findings: None header

The `**Findings:** None` header can contradict the verdict. Parsed findings
come from the body sections, never from that header.

```scrut
$ jq -s 'add' "${COPILOT_REVIEW_DATA_DIR}/format-d.json" "${COPILOT_REVIEW_DATA_DIR}/format-d-previously-missed.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '[.[] | select(.reviewBody | contains("**Findings:** None")) | {id, findings: ([.findings[] | select(.source != "lead")] | length)}]'
[{"id":6000000001,"findings":2},{"id":6000000003,"findings":1}]
```

## Overview v2 repeated findings keep their identity

Copilot repeats an unaddressed finding in later reviews. The review ID and URL
change, but the path, line, and body that identify the finding do not, so a
prior disposition can be matched against the repeat.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-repeated.json" | jq -c '{ids: [.[].id], identities: [.[] | [.findings[] | select(.source != "lead") | {path, line, body}]] | unique | length}'
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
trailing carriage return that reads as drift. The count line carries the
carriage return too, so this also covers `**Findings:** None` surviving it.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"<!-- ccr-overview-v2 -->\r\n\r\n### 🟢 Approval recommended\r\n\r\nNo issues.\r\n\r\n**Findings:** None\r\n"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {verdict, hasFormatDrift}'
{"verdict":"### 🟢 Approval recommended","hasFormatDrift":false}
```

## Overview v2 open threads explain a non-clean verdict

Inline threads listed under `Open (N)` are reported by the thread fetch. A
review whose only findings are open threads has no body findings and is not
format drift.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-open-only.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings: [.findings[] | select(.source != "lead")]}'
{"verdict":"### 🟡 Changes recommended","hasFormatDrift":false,"findings":[]}
```

## Overview v2 a resolved-only round with a boilerplate lead needs nothing

Copilot pairs a non-clean verdict with `**Findings:** None` and a `Resolved
since last review (N)` section listing what the previous round closed. When
the lead paragraph is a fixed sentence that names no finding, nothing is
outstanding: the review is neither format drift nor a lead to read. A review
body never changes, so flagging it would put a signal on the pull request that
no later run can clear.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-resolved-only.json" | jq -c '.[0] | {verdict, hasFormatDrift, needsRead, findings}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":false,"needsRead":false,"findings":[]}
```

## Overview v2 an unparsed section beside a resolved one is still drift

Nothing else in the body may go unread. A genuine resolved section and the
fixed lead sitting beside an element outside the v2 vocabulary leave
`findings` empty, so without the element check the review reads clean while
carrying content nothing parsed. The element is a census signal nothing
accounts for.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-unparsed-beside-resolved.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings: [.findings[] | select(.source != "lead")], unaccounted: [.unaccounted[] | "\(.kind) line \(.line)"]}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":true,"findings":[],"unaccounted":["element line 12"]}
```

Wrapping that element in a details block of its own does not hide it. The
check reads the element vocabulary of the whole body rather than stopping at
the top level, so an unfamiliar section rendered the way Copilot renders its
own cannot carry unread content past it. Its count is unaccounted too.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-unknown-section-block.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings, unaccounted: [.unaccounted[] | "\(.kind) line \(.line)"]}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":true,"findings":[],"unaccounted":["section-count line 13","element line 15"]}
```

Only markup counts. A placeholder such as `<out-file>` quoted in a code span
is prose, and across live reviews every element outside the vocabulary sat in
one.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"<!-- ccr-overview-v2 -->\n\n### 🟢 Approval recommended\n\nNo issues.\n\n**Findings:** None\n\n<details>\n<summary><strong>What changed in this PR</strong></summary>\n\nWrites the report with `-o \"<out-file>\"`.\n</details>"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {hasFormatDrift, unaccounted}'
{"hasFormatDrift":false,"unaccounted":[]}
```

The vocabulary is elements, not section names. Copilot has already added
`Open`, `Resolved since last review`, `Previously missed` and `What changed in
this PR` over time, so a list of known section names would report drift the
first time it ships another one, and on a resolved-only round that is an
escalation no later run can clear. `format-d-open-only.json` carries the
`What changed in this PR` shape alongside its sections and stays clean.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-resolved-only.json" | jq -c '.[0] | {hasFormatDrift}'
{"hasFormatDrift":false}
```

## Overview v2 a section summary counts only inside a details block

Copilot announces every section as a `<summary>` inside `<details>`, so the
nesting identifies one. A summary at the top level is not a section, and
honouring it would let an `Open (9)` that opens nothing absorb a stated count
of 2 and hide the shortfall.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-unnested-summary.json" | jq -c '.[0] | {verdict, hasFormatDrift}'
{"verdict":"### 🟡 Changes recommended","hasFormatDrift":true}
```

A section summary counts at one depth only, the summary of a block opened at
the top of the body. `Previously missed` nests a details block per finding, so
accepting any depth would let one of those carry a section name: a `Resolved
since last review (1)` tucked inside `What changed in this PR` would clear the
lead although the review lists no resolved section. Here the lead still needs
a read.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-nested-impersonation.json" | jq -c '.[0] | {verdict, hasFormatDrift, needsRead}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":false,"needsRead":true}
```

## Overview v2 a resolved section does not clear a lead that states findings

The same shape with a lead paragraph naming findings needs a read. Copilot
ships a resolved section on most second and later rounds, including rounds
that state their findings in prose, so presence of the section cannot stand
alone. Without the lead check this body would read as clean and the findings
would reach nobody.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-resolved-lead.json" | jq -c '.[0] | {verdict, hasFormatDrift, needsRead, findings: [.findings[] | {source, body}]}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":false,"needsRead":true,"findings":[{"source":"lead","body":"Unresolved moderate findings affect detection, reviewer exclusions, and checklist accuracy."}]}
```

## Overview v2 format drift

A non-clean verdict cannot become a clean result merely because the parser
does not recognize the finding representation. `**Findings:** None` does not
clear that, because the count reports only the inline threads Copilot opened
and so cannot rule out an unparsed layout. This body carries an element no v2
layout uses, which is drift, and the complete body remains available for
manual inspection.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-drift.json" | jq -c '.[0] | {verdict, hasSuppressedMarker, hasFormatDrift, hasReviewBody: (.reviewBody | contains("data-finding")), unaccounted: [.unaccounted[] | .kind]}'
{"verdict":"### 🔵 Needs a closer look","hasSuppressedMarker":false,"hasFormatDrift":true,"hasReviewBody":true,"unaccounted":["element"]}
```

## Overview v2 findings stated only in the lead paragraph

Copilot also pairs a non-clean verdict with `**Findings:** None` and no section
at all, stating the findings in the lead paragraph alone. The layout was read,
so this is not drift: what remains is prose. It sets `needsRead`, and the lead
becomes one finding with no location and no severity, so it reaches the reader
through the same path as every other finding. `headline` still carries the
verdict and the lead.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-headline-only.json" | jq -c '.[0] | {verdict, hasFormatDrift, needsRead, findings}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":false,"needsRead":true,"findings":[{"location":"(review overview)","path":null,"line":null,"severity":null,"body":"Unresolved moderate findings affect detection, reviewer exclusions, and checklist accuracy.","source":"lead","region":"lead"}]}
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-headline-only.json" | jq -c '.[0] | {headline}'
{"headline":"<!-- ccr-overview-v2 -->\n\n## Copilot review overview\n\n### 🔵 Needs a closer look\n\nUnresolved moderate findings affect detection, reviewer exclusions, and checklist accuracy.\n\n**Review effort:** Lite  \n**Findings:** None"}
```

## Overview v2 stated count above the inline threads listed

The stated count is the `Open (N)` thread count. A count above that number
leaves findings this command cannot account for, so it reports drift on its own,
whatever the verdict and whatever sections the body lists. The clean verdict
and an empty census isolate that path: nothing else in this body reports drift.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-count-mismatch.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings}'
{"verdict":"### 🟢 Approval recommended","hasFormatDrift":true,"findings":[]}
```

## Overview v2 the stated count is a severity breakdown

Copilot renders the count as one number per severity, joined by a middle dot
and each followed by a badge. `2 <medium> · 1 <low>` is three findings, and
the body lists `Open (3)`, so the totals agree and this is not drift. The
badges carry their own `width` and `height` numbers, which removing the markup
tags before summing keeps out of the total.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-severity-split.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings}'
{"verdict":"### 🟡 Changes recommended","hasFormatDrift":false,"findings":[]}
```

Summing those counts is what makes the comparison real. Here `2 <medium> · 3
<low>` totals five against `Open (3)`, so two findings are unaccounted for.
Reading only the first number would see two, find no shortfall, and report
this clean.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-severity-shortfall.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings}'
{"verdict":"### 🟡 Changes recommended","hasFormatDrift":true,"findings":[]}
```

## Overview v2 a shortfall counts even when a finding parsed

The shortfall check does not wait for an empty parse. A body stating nine
findings against `Open (1)` while yielding one `Previously missed` entry still
has a remainder the parser cannot account for, and that remainder is what the
signal exists for. Requiring an empty parse would report this clean because a
single finding happened to parse.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-shortfall-with-finding.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings: ([.findings[] | select(.source != "lead")] | length)}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":true,"findings":1}
```

## Overview v2 a count line that no longer parses is itself drift

A `**Findings:**` line whose value reads as neither `None` nor a severity
breakdown has changed shape, which is exactly what this signal is for. It
reports drift rather than degrading to the same result as a layout that never
carried the line, even though the rest of this body would otherwise be clean.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-header-drift.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings: [.findings[] | select(.source != "lead")]}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":true,"findings":[]}
```

The whole value is validated, so a trailer after an otherwise valid `None` is
unparseable too. Accepting a leading token would let a malformed line read as
zero findings, report no shortfall, and leave the unparsed section below it
unreported.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-malformed-count.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":true,"findings":[]}
```

A numeric value takes the same treatment, which a token scan would not give
it. `0 plus an unfamiliar trailer` reduces to a count of zero under any rule
that reads the leading number, and zero is the one value that can never be a
shortfall.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-zero-trailer.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":true,"findings":[]}
```

Renaming the header is the same format change seen from the other side. Every
`ccr-overview-v2` body carries a `**Findings:**` line, so its absence is a
rename rather than an older layout, and reading it as "this layout never had a
count" would report no shortfall for the renamed body. Only a body with no v2
marker reports no count and is excluded from the comparison.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-renamed-header.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings: [.findings[] | select(.source != "lead")]}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":true,"findings":[]}
```

Only the preamble is searched for that line, which is where Copilot states it
in every observed body. A rename would otherwise fall through to a `**Findings`
line quoted inside a section, and a quoted `None` reads as zero findings, which
reports no shortfall and hides the rename.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-quoted-count.json" | jq -c '.[0] | {verdict, hasFormatDrift, findings: [.findings[] | select(.source != "lead")]}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":true,"findings":[]}
```

## Overview v2 section phrases in prose do not clear a lead

Both the open-threads rule and the resolved-round rule key on a `<summary>`
announcing a non-zero count. A review of this repository quotes `Open (N)` and
`Resolved since last review (N)` in its file-summary table and prose, and a
real summary can announce zero resolved entries. None of that is a section,
so none of it clears the lead, which still needs a read. The existing
`file-summaries-mention.json` fixture records the same over-match happening
for the suppressed-comments phrase.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-phrase-mention.json" | jq -c '.[0] | {verdict, hasFormatDrift, needsRead}'
{"verdict":"### 🔵 Needs a closer look","hasFormatDrift":false,"needsRead":true}
```

## Vote-tagged layouts from live reviews

These fixtures record shapes taken from live reviews. Each yields every
finding it carries, and the census, which checks each vote tag against the
findings parsed from its line, finds nothing left over.

Bold severity tokens in file-summary cells, including one placed after the
cell's description sentence.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-bold-votes.json" | jq -c '.[0] | {hasFormatDrift, unaccounted, findings: [.findings[] | select(.source != "lead") | {location, severity, body}]}'
{"hasFormatDrift":false,"unaccounted":[],"findings":[{"location":"test/e2e/lib/browser.mjs","severity":"Critical","body":"full URLs may expose credentials in query parameters and must be redacted"},{"location":"test/e2e/beacon-test.js","severity":"Nit","body":"still launches the browser directly instead of using the shared launcher"}]}
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-bold-after-description.json" | jq -c '.[0] | {hasFormatDrift, unaccounted, findings: [.findings[] | select(.source != "lead") | {location, body}]}'
{"hasFormatDrift":false,"unaccounted":[],"findings":[{"location":"api/alerts/summarize.ts","body":"make the post and save boundary idempotent across retries"},{"location":"api/alerts/follow-up.ts","body":"make sequence updates idempotent"},{"location":"api/alerts/follow-up.ts","body":"guard every close transition with the follow-up thread"},{"location":"api/alerts/redact.ts","body":"redact credential values after every auth scheme"}]}
```

Items written as sentences, separated by a period rather than a semicolon. A
`( each)` item names several defects under one tag and stays one finding.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-sentence-items.json" | jq -c '.[0] | {hasFormatDrift, unaccounted, findings: [.findings[] | select(.source != "lead") | {location, severity, body}]}'
{"hasFormatDrift":false,"unaccounted":[],"findings":[{"location":"src/admin/Bundles.js","severity":"Critical","body":"kit requests can leave records inconsistent when the record update fails"},{"location":"src/admin/Bundles.js","severity":"Moderate","body":"empty update results are reported as success"},{"location":"src/admin/Bundles.js","severity":"Moderate","body":"missing identifiers do not refresh the table, and one path also leaves the dialog open"},{"location":"server/api/bundles.js","severity":"Moderate","body":"add an HTTP-level test that the bundle filter is preserved"}]}
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-each-item.json" | jq -c '.[0] | {hasFormatDrift, unaccounted, findings: [.findings[] | select(.source != "lead") | {location, body}]}'
{"hasFormatDrift":false,"unaccounted":[],"findings":[{"location":"src/sweep.py","body":"zero-count sweeps are accepted, and duplicate-producing sweeps are accepted"}]}
```

A lowercase severity after a semicolon, taken verbatim from a review of this
repository. The severity is reported with a capital, as Copilot titles it.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-lowercase-severity.json" | jq -c '.[0] | {hasFormatDrift, unaccounted, findings: [.findings[] | select(.path == "bin/validate-plugins") | {severity, body}]}'
{"hasFormatDrift":false,"unaccounted":[],"findings":[{"severity":"Critical","body":"preserve newline-containing JSON strings"},{"severity":"Moderate","body":"correct UTF-8 character counting"}]}
```

Vote-tagged bullets under a findings label. A backticked path that opens the
text is the finding's location, split into path and line when it carries one.
A backticked option is not a path, and a bullet that names no file reports a
null path.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-review-findings-bullets.json" | jq -c '.[0] | {hasFormatDrift, unaccounted}, (.findings[] | select(.source != "lead") | {location, path, line, severity, source})'
{"hasFormatDrift":false,"unaccounted":[]}
{"location":".github/workflows/ci.yml","path":".github/workflows/ci.yml","line":null,"severity":"Critical","source":"bullets"}
{"location":"src/lab/runner.py:41","path":"src/lab/runner.py","line":41,"severity":"Critical","source":"bullets"}
{"location":"(review body)","path":null,"line":null,"severity":"Moderate","source":"bullets"}
{"location":"(review body)","path":null,"line":null,"severity":"Moderate","source":"bullets"}
{"location":"(review body)","path":null,"line":null,"severity":"Moderate","source":"bullets"}
```

The same bullets under the older "Pull request overview", labelled
`Outstanding findings:` there, taken verbatim from a review of this repository.
The label varies, so the vote tag is what identifies a finding. These sit
beside four suppressed-section findings in the same review.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-b-overview-bullets.json" | jq -c '.[0] | {hasFormatDrift, unaccounted, bySource: (.findings | group_by(.source) | map({key: .[0].source, value: length}) | from_entries)}'
{"hasFormatDrift":false,"unaccounted":[],"bySource":{"bullets":7,"suppressed":4}}
```

The other bullet shape names its location first, with a dash of any width. A
lowercase severity is reported with a capital here too.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"### 🔵 Needs a closer look\n\nTwo findings.\n\n<details>\n<summary>Pull request overview</summary>\n\n**Review findings:**\n- `tests/audit.py:122` \u2014 Moderate (1 vote): use a scrut fence.\n- `tests/audit.py:101` - moderate (1 vote): preserve archive modes.\n</details>"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {unaccounted, findings: [.findings[] | {path, line, severity, body}]}'
{"unaccounted":[],"findings":[{"path":"tests/audit.py","line":122,"severity":"Moderate","body":"use a scrut fence."},{"path":"tests/audit.py","line":101,"severity":"Moderate","body":"preserve archive modes."}]}
```

## The census reports what no parser reads

Every parser recognizes a layout it was written for and returns nothing for
one it was not. The census is what keeps that from looking like a review with
nothing to say: every vote tag a body line carries must be matched by a
finding parsed from that line, and each line that falls short is reported in
`unaccounted` and sets `hasFormatDrift`. A tag in a paragraph, where no parser
looks, is the simplest case.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"<!-- ccr-overview-v2 -->\n\n### 🟡 Changes recommended\n\nOne finding.\n\n**Findings:** None\n\n<details>\n<summary><strong>What changed in this PR</strong></summary>\n\nThe cache helper never expires entries. Moderate (2 votes): expire entries on restart.\n</details>"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {hasFormatDrift, parsed: ([.findings[] | select(.source != "lead")] | length), unaccounted: [.unaccounted[] | {kind, region, line}]}'
{"hasFormatDrift":true,"parsed":0,"unaccounted":[{"kind":"vote","region":"What changed in this PR","line":12}]}
```

A vote tag quoted in a finding's prose cannot be told apart from an item the
parser missed, so it is reported. That is the safe direction: the cost is one
read, where the opposite rule would let a missed item through.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-table-edge.json" | jq -c '.[0] | {hasFormatDrift, unaccounted: [.unaccounted[] | "\(.kind) line \(.line)"]}'
{"hasFormatDrift":true,"unaccounted":["vote line 22"]}
```

A vote tag inside an inline code span is quoted text and does not count.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"<!-- ccr-overview-v2 -->\n\n### 🟢 Approval recommended\n\nNo issues.\n\n**Findings:** None\n\n<details>\n<summary><strong>What changed in this PR</strong></summary>\n\n| File | Summary |\n|---|---|\n| `src/a.js` | Parses `Nit (1 vote):` tags. |\n</details>"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {hasFormatDrift, unaccounted}'
{"hasFormatDrift":false,"unaccounted":[]}
```

A section Copilot has not shipped before is read by what it lists, not by its
name. One whose count matches the thread links it carries is accounted for the
first time it appears. One whose items nothing parses leaves its count
unaccounted.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-new-thread-section.json" | jq -c '.[0] | {hasFormatDrift, findings: ([.findings[] | select(.source != "lead")] | length), unaccounted}'
{"hasFormatDrift":false,"findings":0,"unaccounted":[]}
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-new-prose-section.json" | jq -c '.[0] | {hasFormatDrift, findings: ([.findings[] | select(.source != "lead")] | length), unaccounted: [.unaccounted[] | "\(.kind) \(.region) line \(.line)"]}'
{"hasFormatDrift":true,"findings":0,"unaccounted":["section-count Also worth checking line 19"]}
```

Two counted sections list files rather than findings and are exempt.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"<!-- ccr-overview-v2 -->\n\n### 🟢 Approval recommended\n\nNo issues.\n\n**Findings:** None\n\n<details>\n<summary>Files not reviewed (2)</summary>\n\n* **a.lock**: Generated file\n* **b.lock**: Generated file\n</details>"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {hasFormatDrift, unaccounted}'
{"hasFormatDrift":false,"unaccounted":[]}
```

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"<!-- ccr-overview-v2 -->\n\n### 🟢 Approval recommended\n\nNo issues.\n\n**Findings:** None\n\n<details>\n<summary>New files (2)</summary>\n\n* **src/a.js**\n* **src/b.js**\n</details>"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {hasFormatDrift, unaccounted}'
{"hasFormatDrift":false,"unaccounted":[]}
```

A section that lists more items than its count states is unaccounted too, not
only one that lists fewer. Either way the count and the content disagree.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"<!-- ccr-overview-v2 -->\n\n### 🟡 Changes recommended\n\nOne finding remains.\n\n**Findings:** 1\n\n<details open>\n<summary><strong>Open (1)</strong></summary>\n\n- <picture><img alt=\"Low severity\"></picture> [First](#discussion_r1) · New\n- <picture><img alt=\"Low severity\"></picture> [Second](#discussion_r2) · New\n</details>"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {hasFormatDrift, unaccounted: [.unaccounted[] | "\(.kind) \(.region) line \(.line)"]}'
{"hasFormatDrift":true,"unaccounted":["section-count Open line 10"]}
```

Location lines are reconciled against the located findings in their region,
so a region that parsed one of its two headings still reports the other. Here
the second heading carries a trailing space, which the suppressed-section
parser does not accept, and the section announces no count that would catch
it instead.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"### 🟡 Changes recommended\n\nTwo findings.\n\n<details>\n<summary>Review details</summary>\n\n### Suppressed comments\n\n**src/a.js:12**\n* Close the handle.\n\n**src/b.js:14** \n* Release the lock.\n</details>"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {hasFormatDrift, findings: [.findings[] | .location], unaccounted: [.unaccounted[] | "\(.kind) \(.region) line \(.line)"]}'
{"hasFormatDrift":true,"findings":["src/a.js:12"],"unaccounted":["location Suppressed comments line 10","location Suppressed comments line 13"]}
```

A bullet that opens with a file and line counts as a location even without a
vote tag, so a finding listed that way cannot slip past every parser.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"<!-- ccr-overview-v2 -->\n\n### 🟢 Approval recommended\n\nNo unresolved review issues were identified.\n\n**Findings:** None\n\n<details>\n<summary><strong>What changed in this PR</strong></summary>\n\nNotes:\n- `src/a.ts:12` - the trap leaks a temp file.\n</details>"}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {hasFormatDrift, unaccounted: [.unaccounted[] | "\(.kind) \(.region) line \(.line)"]}'
{"hasFormatDrift":true,"unaccounted":["location What changed in this PR line 13"]}
```

The census raises nothing on the older layouts it reads fully.

```scrut
$ jq -s 'add' "${COPILOT_REVIEW_DATA_DIR}/format-a.json" "${COPILOT_REVIEW_DATA_DIR}/format-b.json" "${COPILOT_REVIEW_DATA_DIR}/format-c.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '[.[] | {hasFormatDrift, unaccounted}]'
[{"hasFormatDrift":false,"unaccounted":[]},{"hasFormatDrift":false,"unaccounted":[]},{"hasFormatDrift":false,"unaccounted":[]}]
```

## The lead paragraph is read unless it is known to say nothing

A lead can state a new finding, restate a thread or a parsed finding, ask for
human review without naming a defect, or say nothing of concern, and only a
reader can tell which. Any lead that is not a known no-finding sentence sets
`needsRead` rather than drift, and carries the lead as one finding. A review
body never changes, so drift here would escalate a pull request on a signal
nothing can clear, where a read costs one look.

An advisory request for human review, which the resolver records as Advisory:

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-advisory-lead.json" | jq -c '.[0] | {hasFormatDrift, needsRead, findings: [.findings[] | {source, body}]}'
{"hasFormatDrift":false,"needsRead":true,"findings":[{"source":"lead","body":"Authentication and logout changes warrant final human review."}]}
```

A finding stated only in prose, taken verbatim from a review of this
repository:

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-prose-lead.json" | jq -c '.[0] | {hasFormatDrift, needsRead, findings: [.findings[] | {source, body}]}'
{"hasFormatDrift":false,"needsRead":true,"findings":[{"source":"lead","body":"A moderate cleanup-trap defect and two unresolved sandbox-path documentation gaps remain."}]}
```

A reworded no-findings sentence. The known sentences are matched whole, so a
reword is not on the list and costs a read, never an escalation.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-reworded-boilerplate.json" | jq -c '.[0] | {hasFormatDrift, needsRead, findings: [.findings[] | {source, body}]}'
{"hasFormatDrift":false,"needsRead":true,"findings":[{"source":"lead","body":"One or more issues need attention before approval."}]}
```

Every known sentence clears a resolved-only round, including the
`No unresolved <kind> issues ...` family with any one-word kind.

```scrut
$ for s in "One or more issues must be addressed before approval." "No unresolved review issues were identified." "No unresolved blocking issues were identified." "No unresolved review issues remain." "No unresolved correctness issues were identified."; do jq --arg s "${s}" '.[0].body |= sub("One or more issues must be addressed before approval."; $s)' "${COPILOT_REVIEW_DATA_DIR}/format-d-resolved-only.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0].needsRead'; done
false
false
false
false
false
```

A known sentence must be the whole lead. One followed by a finding, in prose or
as a bullet, is read, and the finding travels in the lead's body. A prefix
match here would clear the round and lose the finding without a signal.

```scrut
$ jq '.[0].body |= sub("approval\\."; "approval. The cache never expires entries.")' "${COPILOT_REVIEW_DATA_DIR}/format-d-resolved-only.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {needsRead, findings: [.findings[] | {source, body}]}'
{"needsRead":true,"findings":[{"source":"lead","body":"One or more issues must be addressed before approval. The cache never expires entries."}]}
```

```scrut
$ jq '.[0].body |= sub("approval\\."; "approval.\n- **Rollback:** the down migration drops the users table.")' "${COPILOT_REVIEW_DATA_DIR}/format-d-resolved-only.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {needsRead, findings: [.findings[] | {source, body}]}'
{"needsRead":true,"findings":[{"source":"lead","body":"One or more issues must be addressed before approval.\n- **Rollback:** the down migration drops the users table."}]}
```

A known sentence clears only a round that lists a resolved section. Without
one, the sentence that says issues remain is read rather than trusted.

```scrut
$ jq '.[0].body |= sub("(?s)<details>.*"; "")' "${COPILOT_REVIEW_DATA_DIR}/format-d-resolved-only.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {hasFormatDrift, needsRead}'
{"hasFormatDrift":false,"needsRead":true}
```

An approval whose lead is a known sentence needs nothing. An approval whose
lead names something, even a nit, is read: the verdict does not decide it.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-clean.json" | jq -c '.[0] | {verdict, needsRead, findings}'
{"verdict":"### 🟢 Approval recommended","needsRead":false,"findings":[]}
```

```scrut
$ jq '.[0].body |= sub("No unresolved correctness issues were identified."; "No blocking issues were identified; only a minor documentation nit remains.")' "${COPILOT_REVIEW_DATA_DIR}/format-d-clean.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {verdict, needsRead, findings: [.findings[] | {source, body}]}'
{"verdict":"### 🟢 Approval recommended","needsRead":true,"findings":[{"source":"lead","body":"No blocking issues were identified; only a minor documentation nit remains."}]}
```

A lead beside parsed findings is read too, because it can name a defect none
of them does. It arrives after them, and step 1d of the resolver matches each
of its concerns to what parsed.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d.json" | jq -c '.[0] | {needsRead, sources: [.findings[] | .source], lead: ([.findings[] | select(.source == "lead") | .body][0])}'
{"needsRead":true,"sources":["table","table","lead"],"lead":"A moderate validation issue and a documentation nit remain unresolved."}
```

The lead ends where the first details block starts, including an `Open`
section opened with `<details open>`, so its thread list never leaks into the
headline or the lead.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-open-only.json" | jq -c '.[0] | {needsRead, headlineHasOpenList: (.headline | test("Open \\(")), lead: ([.findings[] | select(.source == "lead") | .body][0])}'
{"needsRead":true,"headlineHasOpenList":false,"lead":"Two inline issues remain unresolved."}
```

## Copilot notices that are not reviews

Copilot posts two notices through the review API. Neither has a verdict or a
finding, which is exactly what a clean review looks like, so `reviewKind` is
what tells a caller the review did not happen.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/notice-error.json" | jq -c '.[0] | {reviewKind, verdict, hasFormatDrift, needsRead, findings: (.findings | length)}'
{"reviewKind":"error","verdict":null,"hasFormatDrift":false,"needsRead":false,"findings":0}
```

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/notice-no-files.json" | jq -c '.[0] | {reviewKind, verdict, hasFormatDrift, needsRead, findings: (.findings | length)}'
{"reviewKind":"no-files","verdict":null,"hasFormatDrift":false,"needsRead":false,"findings":0}
```

A body that is neither a review nor a known notice is a layout nothing here
reads, so it is drift.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/notice-unknown.json" | jq -c '.[0] | {reviewKind, verdict, hasFormatDrift, findings: (.findings | length)}'
{"reviewKind":"unknown","verdict":null,"hasFormatDrift":true,"findings":0}
```

Every older layout still reads as a review.

```scrut
$ jq -s 'add' "${COPILOT_REVIEW_DATA_DIR}/format-a.json" "${COPILOT_REVIEW_DATA_DIR}/format-b.json" "${COPILOT_REVIEW_DATA_DIR}/format-c.json" "${COPILOT_REVIEW_DATA_DIR}/no-suppressed.json" "${COPILOT_REVIEW_DATA_DIR}/drift.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '[.[] | .reviewKind] | unique'
["review"]
```

Each mark of review structure is enough on its own: a heading, an overview or
review-details section, or a suppressed-comments section.

```scrut
$ for body in '### Reviewed changes\n\nText.' '## Pull request overview\n\nText.' '<details>\n<summary>Review details</summary>\n\nText.\n</details>' 'Comments suppressed due to low confidence (1)'; do printf '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"html_url":"y","body":"%s"}]' "${body}" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0].reviewKind'; done
"review"
"review"
"review"
"review"
```

A real review that quotes a notice is still a review. Review structure is
checked before the notice text, so a review of a change to this command, which
quotes that text in its file summary, keeps its findings rather than being
taken for a notice.

```scrut
$ jq '.[0].body |= sub("\\| File \\| Summary \\|"; "| File | Summary |\n|---|---|\n| `docs/notices.md` | Documents the \"Copilot encountered an error and was unable to review\" notice. |\n| File | Summary |")' "${COPILOT_REVIEW_DATA_DIR}/format-b-overview-bullets.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {reviewKind, quotesNotice: (.reviewBody | test("unable to review")), parsed: ([.findings[] | select(.source != "lead")] | length)}'
{"reviewKind":"review","quotesNotice":true,"parsed":11}
```

```scrut
$ jq '.[0].body |= sub("Two inline issues remain unresolved."; "Two inline issues remain; one concerns the wasn'"'"'t able to review any files notice.")' "${COPILOT_REVIEW_DATA_DIR}/format-d-open-only.json" | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {reviewKind}'
{"reviewKind":"review"}
```

## A review body that is not a string is skipped, not fatal

A review whose body is not a string is skipped rather than aborting the run,
so every well-formed review beside it still parses.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/malformed-body.json" 2> /dev/null | jq -c '[.[].id]'
[6000000042]
```

The skip is named on stderr, with the review id, so it is never silent.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/malformed-body.json" 2>&1 > /dev/null
Warning: skipping review 6000000043: its body is not a string.
```

## A jq too old for the filter is named

The filter needs jq 1.7 or later. An older jq would fail it as a compile error
that names neither the version nor the cause.

```scrut
$ fake="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '#!/usr/bin/env bash\necho jq-1.6\n' > "${fake}/jq" && chmod +x "${fake}/jq" && echo '[]' | PATH="${fake}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews 2>&1; rm -rf "${fake}"
Error: jq 1.7 or later is required, found jq-1.6. Install it: https://jqlang.github.io/jq/download/
```

jq 1.7 itself passes, and so does a version string that does not read as
`jq-MAJOR.MINOR`, such as another implementation's, since the check cannot
tell what it supports. Each stand-in answers only `--version`, so these cases
look only for the version error.

```scrut
$ for version in jq-1.7 jq-1.7.1 "gojq 0.12.16" jq-master; do fake="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '#!/usr/bin/env bash\necho "%s"\n' "${version}" > "${fake}/jq" && chmod +x "${fake}/jq" && echo '[]' | PATH="${fake}:${PATH}" "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews 2>&1 | grep -c 'or later is required'; rm -rf "${fake}"; done
0
0
0
0
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

It is still a location line nothing parsed, though, so the census reports it
rather than letting it pass as prose. A location heading Copilot moved out of
its section would look exactly like this.

```scrut
$ echo '[{"id":1,"user":{"login":"copilot-pull-request-reviewer[bot]"},"state":"COMMENTED","submitted_at":"x","html_url":"y","body":"## Pull request overview\n\n**src/lib/heading.js:12**\n\nProse that names a location."}]' | "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews | jq -c '.[0] | {hasFormatDrift, unaccounted: [.unaccounted[] | "\(.kind) \(.region) line \(.line)"]}'
{"hasFormatDrift":true,"unaccounted":["location lead line 3"]}
```

## Headline captures the verdict and drops the boilerplate

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-c.json" | jq -r '.[0].headline' | head -1
### 🟢 Approval recommended
```

## A review with no suppressed section reports no marker

Its body still carries several `<details>` blocks, so this guards against a false positive on ordinary reviews.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/no-suppressed.json" | jq -c '[.[] | {hasSuppressedMarker, hasFormatDrift, findings: (.findings | length)}]'
[{"hasSuppressedMarker":false,"hasFormatDrift":false,"findings":0}]
```

## A file-summaries table mentioning the phrase is not a section

Copilot opens most reviews with a table describing every changed file, so a PR that touches code about suppressed comments gets a row quoting the phrase. A section is never announced from inside a table, so table rows must not open one. This fixture is the real review Copilot left on the PR that added this command, which tripped exactly that case.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/file-summaries-mention.json" | jq -c '[.[] | {hasSuppressedMarker, hasFormatDrift, findings: (.findings | length)}]'
[{"hasSuppressedMarker":false,"hasFormatDrift":false,"findings":0}]
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

## Help lists the review-body and audit commands

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" --help | grep -E '^  (fetch-reviews|parse-reviews|audit|parse-audit)'
  fetch-reviews <owner> <repo> <pr_number>            Fetch Copilot review-body findings
  parse-reviews                                        Normalize review JSON read from stdin
  audit <owner> <repo> <pr_number>                    List Copilot items the fetches cannot reach
  parse-audit                                          Audit pull request JSON read from stdin
```

## The surface audit

`fetch` reads unresolved threads Copilot opened and `fetch-reviews` reads its
review bodies. `audit` lists every Copilot item on a pull request by where it
appears and reports any the two do not reach, so feedback that arrives
somewhere new is an entry rather than silence. `parse-audit` is the same join
over saved JSON, which is what these cases run, since `audit` needs an
authenticated `gh`.

When every Copilot item is reachable, nothing is reported. A summary comment
the resolver posted is not a Copilot item. The inline comment's REST login is
`Copilot`, which matches regardless of case.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit < "${COPILOT_AUDIT_DATA_DIR}/covered.json" | jq -c .
{"surfaces":{"reviews":1,"reviewComments":1,"issueComments":0},"uncovered":[],"legacyNeedsRead":[]}
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

An older-layout body cannot say whether its findings are inline. A review whose
first heading is not the approval verdict, with nothing parsed, is accounted
for when inline comments are attached to it, and otherwise only its prose can
say what it found, so it is listed for a read. A clean older review is never
listed.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit < "${COPILOT_AUDIT_DATA_DIR}/legacy-prose.json" | jq -c '{legacyNeedsRead}'
{"legacyNeedsRead":[6100000003]}
```

An older body with no heading at all cannot say it was clean, so it is listed
too. An older body whose findings parsed, and a v2 body, which states its own
findings and leads, are accounted for by other means and are not.

```scrut
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit < "${COPILOT_AUDIT_DATA_DIR}/legacy-filters.json" | jq -c '{legacyNeedsRead}'
{"legacyNeedsRead":[6100000006]}
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
$ "${RESOLVE_COPILOT_THREADS_BIN}" parse-audit extra < /dev/null 2>&1
Error: Usage: resolve-copilot-threads parse-audit (reads pull request JSON on stdin)
[1]
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
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-unparsed-beside-resolved.json" | jq -c '.[0] | {hasFormatDrift, findings: ([.findings[] | select(.source != "lead")] | length)}'
{"hasFormatDrift":true,"findings":0}
```

## The step 3 selection filter pins its own output shape

`monitor-pr` does not read the whole `fetch-reviews` result. It selects the one
review the metadata probe named and projects seven fields, because the raw
result carries every Copilot review on the PR with its complete body and the
watch prints this on every tick. These testcases run the filter exactly as the
skill documents it, over `parse-reviews` so no authenticated `gh` is needed.

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-clean.json" | jq -c --argjson review_id 6000000004 '[.[] | select(.id == $review_id)] | last | {id, url, reviewKind, hasFormatDrift, needsRead, findings: (.findings | length), unaccounted: (.unaccounted | length)}'
{"id":6000000004,"url":"https://github.com/o/r/pull/1#pullrequestreview-6000000004","reviewKind":"review","hasFormatDrift":false,"needsRead":false,"findings":0,"unaccounted":0}
```

A review that needs a read carries its lead as one finding, so the watch
dispatches it to the resolver like any other review-body finding, with no
separate rule.

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-advisory-lead.json" | jq -c --argjson review_id 6000000033 '[.[] | select(.id == $review_id)] | last | {id, url, reviewKind, hasFormatDrift, needsRead, findings: (.findings | length), unaccounted: (.unaccounted | length)}'
{"id":6000000033,"url":"https://github.com/o/r/pull/1#pullrequestreview-6000000033","reviewKind":"review","hasFormatDrift":false,"needsRead":true,"findings":1,"unaccounted":0}
```

A notice reads exactly like a clean review on every field but one. The watch
must check `reviewKind` before it treats zero findings and no drift as clean.

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/notice-error.json" | jq -c --argjson review_id 6000000036 '[.[] | select(.id == $review_id)] | last | {id, url, reviewKind, hasFormatDrift, needsRead, findings: (.findings | length), unaccounted: (.unaccounted | length)}'
{"id":6000000036,"url":"https://github.com/o/r/pull/1#pullrequestreview-6000000036","reviewKind":"error","hasFormatDrift":false,"needsRead":false,"findings":0,"unaccounted":0}
```

A review id the result does not carry, which is what an empty review body
produces, does **not** yield `null`. jq builds the object from `null` anyway, and
`length` over an absent field is `0` rather than an error. The skill documents
this shape so a reader does not mistake the all-null object for a review that
parsed cleanly: a null `hasFormatDrift` is an absent answer, not `false`.

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-reviews < "${COPILOT_REVIEW_DATA_DIR}/format-d-clean.json" | jq -c --argjson review_id 6000000099 '[.[] | select(.id == $review_id)] | last | {id, url, reviewKind, hasFormatDrift, needsRead, findings: (.findings | length), unaccounted: (.unaccounted | length)}'
{"id":null,"url":null,"reviewKind":null,"hasFormatDrift":null,"needsRead":null,"findings":0,"unaccounted":0}
```

The audit filter reduces `audit` to the ids step 7b records as processed. The
`audited` field is what tells an empty audit from a failed one: a failed
`audit` emits nothing, and the filter then emits nothing too, so the watch
reads "not observed" rather than "nothing uncovered".

```scrut
$ "${MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN}" parse-audit < "${COPILOT_AUDIT_DATA_DIR}/uncovered.json" | jq -c '{audited: true, uncovered: [.uncovered[].id], legacyNeedsRead}'
{"audited":true,"uncovered":[9103,9104,9202],"legacyNeedsRead":[]}
```

```scrut
$ printf '' | jq -c '{audited: true, uncovered: [.uncovered[].id], legacyNeedsRead}'
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
