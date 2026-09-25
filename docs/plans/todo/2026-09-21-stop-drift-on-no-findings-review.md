# Stop review-body drift on a clean no-findings review

Addresses [issue #491](https://github.com/cboone/agent-harness-plugins/issues/491).

## Context

`resolve-copilot-threads parse-reviews` sets `hasFormatDrift` for a `ccr-overview-v2` review when the parser recovers no findings, the verdict heading is not `### 🟢 Approval recommended`, and the body lists no `Open (N)` inline threads. The rule assumes that a non-clean verdict with nothing parseable means Copilot shipped a layout the parser does not understand.

Copilot violates that assumption. On [review 5261480703](https://github.com/cboone/agent-harness-plugins/pull/471#pullrequestreview-5261480703) it paired `### 🔵 Needs a closer look` with `**Findings:** None` and a `Resolved since last review (1)` section listing the thread closed in the previous round. Nothing was outstanding, but the review reported drift.

A false positive here cannot clear. A review body is immutable, `fetch-reviews` returns every Copilot review on the pull request, and `monitor-pr` treats drift as not clean, so every later tick re-reads the same body, escalates, and records a workflow failure on a pull request with no feedback left to address.

The intended outcome: a resolved-only round whose lead paragraph names no finding reads as clean, while a review that falls short of its own stated count, or that states its findings only in prose, still reports drift. Narrowing the signal must not reintroduce the silent miss it exists to prevent.

## Approach

Add four body signals to the jq parser in `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`, then rewrite the v2 branch of the drift condition around them.

### What the stated count actually means

The issue proposes treating `**Findings:** None` as authoritative for any `ccr-overview-v2` body. It is not. Measured across every fixture and all 13 live Copilot reviews on pull requests #471, #498, #503 and #516, the `**Findings:**` total is the `Open (N)` thread count and nothing else:

- `format-d-previously-missed.json` id 6000000002 states `1` while listing `Open (1)` **and** `Previously missed (1)`. If the count spanned both it would read `2`.
- Live review 5261421694 states `None` while listing `Previously missed (3)`; live review 5262234889 states `None` with `Previously missed (1)`.
- Every total above zero equals its `Open (N)` number, and no observed body states a total above zero without an `Open (N)` section.

So `None` rules out open inline threads and nothing else. Reading it as "this review has no findings" is unsound, and comparing the count against zero is not the invariant. Comparing it against the `Open (N)` number is.

The value is a severity breakdown rather than a single number. Copilot renders each severity as a count followed by a badge, joined by a middle dot, so review 5280564210 on #516 reads `**Findings:** 2 <picture>Medium</picture> · 1 <picture>Low</picture>` and lists `Open (3)`. The counts have to be summed; reading only the first understates any review spanning severities.

The value is validated whole rather than scanned for tokens. Removing the markup tags and then all whitespace leaves the counts and their separators alone, so a well-formed value reduces to `None` or to digits joined by the dot, and anything else is unparseable. Tag removal is also what keeps the badges' own `width` and `height` numbers out of the sum. Validating the whole value is what stops `None plus hidden text` and `0 plus hidden text` from reading as a count, either of which would satisfy the resolved-round exemption and suppress an unparsed finding.

### Why the resolved section cannot clear a review on its own

Copilot ships a `Resolved since last review (N)` section on most second and later rounds, which is exactly the steady state of the `monitor-pr` loop. Exempting on its presence alone silences the reviews the signal exists for: a body pairing that section with an unfamiliar layout, or with findings stated only in the lead paragraph, reads as clean.

The lead paragraph is what separates the two, and it separates them cleanly on every live review of #471. A review with nothing outstanding carries the fixed sentence `One or more issues must be addressed before approval.`, which is what review 5261480703 from the issue carries. Every other lead names its findings, as in `Unresolved moderate findings affect detection, reviewer exclusions, and checklist accuracy`, and those findings appear nowhere else in the body. The match is exact, so an unrecognized lead reports drift and sends the reader to `headline`.

### Parser changes

In the jq program inside `do_parse_reviews`:

1. `open_thread_count`: the `N` from the `Open (N)` summary, or `0`. Parsed rather than merely detected, so the count has something to reconcile against.
1. `lists_resolved_threads`: `test("<summary>(<[^>]+>)*Resolved since last review \\([1-9][0-9]*\\)")`, mirroring `lists_open_threads` so the optional `<strong>` wrapper still matches and `(0)` is excluded.
1. `lead_states_no_findings`: the first prose line of `headline`, matched exactly against Copilot's fixed no-findings sentence. Defined after `headline` so it can reuse it.
1. `stated_finding_count`: `0` for `None`, the sum of the severity counts when the value is a breakdown, `"unparseable"` when a `**Findings` line exists but its value is neither, and `null` when no such line exists. The binding then turns that `null` into `"unparseable"` on a `ccr-overview-v2` body, where the line is always present, so a renamed header reads as the format change it is rather than as a layout that never had a count. Only a pre-v2 body keeps `null` and is excluded from the comparison.

Then the v2 clause of `hasFormatDrift`:

```jq
| (
    if $stated_findings == null then false
    elif $stated_findings == "unparseable" then true
    else $stated_findings > $open_thread_count
    end
  ) as $stated_shortfall
...
hasFormatDrift: (
  ($is_v2 and $stated_shortfall)
  or (
    ($findings | length) == 0
    and (
      $has_suppressed_marker
      or (
        $is_v2
        and $verdict != "### 🟢 Approval recommended"
        and ($lists_open_threads | not)
        and (($lists_resolved_threads and $lead_states_no_findings) | not)
      )
    )
  )
),
```

A shortfall reports drift on its own, outside the no-findings guard, because both numbers it compares come from Copilot. Keeping it under that guard would report clean whenever any single finding parsed, even though the remainder is exactly what the signal is for. The other branches do require an empty parse, because they ask whether anything at all was recovered from a body that says there should be something: a non-clean verdict reports drift unless open threads or a resolved-only round with a boilerplate lead accounts for it.

Resulting behavior:

| Body                                                               | Before | After |
| ------------------------------------------------------------------ | ------ | ----- |
| Clean verdict, `Findings: None`, resolved section                  | false  | false |
| Non-clean verdict, boilerplate lead, resolved section (#491)       | true   | false |
| Non-clean verdict, lead states findings, resolved section          | true   | true  |
| Non-clean verdict, `Findings: None`, unfamiliar markup             | true   | true  |
| Non-clean verdict, lead states findings, no section                | true   | true  |
| Any verdict, stated total above the `Open (N)` number              | varies | true  |
| Stated total above `Open (N)`, with some findings parsed           | false  | true  |
| Any verdict, `**Findings:**` value that is neither None nor counts | varies | true  |
| v2 body whose `**Findings:**` header was renamed or removed        | varies | true  |
| Non-clean verdict, `Open (N)` listed and count matching            | false  | false |
| Section phrases quoted only in a table or prose, or `Resolved (0)` | true   | true  |
| Legacy suppressed section with no parseable findings               | true   | true  |

## Files to change

1. `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`: the four jq definitions above, their bindings plus the `$stated_shortfall` binding, the rewritten `hasFormatDrift` expression, and the `Review-body findings` header comment at the top of that section.
1. `tests/data/copilot-reviews/format-d-resolved-only.json` (id `6000000010`): the #491 body. Non-clean verdict, boilerplate lead, `**Findings:** None`, `Resolved since last review (1)`, no `Open` section. Expects `false`.
1. `tests/data/copilot-reviews/format-d-resolved-lead.json` (id `6000000013`): the same shape with a lead naming findings, taken from live review 5262269024. Expects `true`. This is the case the resolved-section exemption would otherwise silence.
1. `tests/data/copilot-reviews/format-d-count-mismatch.json` (id `6000000011`): `**Findings:** 3` against `Open (1)`, plus a resolved section, on a **clean** verdict. Expects `true`. The clean verdict isolates the shortfall path, since no other branch can report drift on an approval.
1. `tests/data/copilot-reviews/format-d-headline-only.json` (id `6000000012`): live reviews 5262190988, 5262269024 and 5262292015. Non-clean verdict, `**Findings:** None`, no section, findings in the lead alone. Expects `true`.
1. `tests/data/copilot-reviews/format-d-header-drift.json` (id `6000000014`): `**Findings**: 2` with the colon outside the bold, otherwise an exempt body. Expects `true` through the `unparseable` branch.
1. `tests/data/copilot-reviews/format-d-phrase-mention.json` (id `6000000015`): the section phrases quoted in a file-summary row and in prose, plus a real `Resolved since last review (0)` summary. Expects `true`. This is the negative control for both exemption regexes, matching why `file-summaries-mention.json` exists.
1. `tests/scrut/resolve-copilot-threads.md`: one case per fixture in the established prose-then-block form, and `hasFormatDrift` added to the `no-suppressed` and `file-summaries-mention` projections so the `$is_v2` guard is pinned.
1. `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`: the `hasFormatDrift` bullet in the step 1b output contract, and the trailing clause of the `verdict` bullet. The `Format-drift rule (CRITICAL)` paragraph and the terminal-status wording stay as they are, since the meaning of a true result has not changed.
1. `plugins/resolve-copilot-pr-feedback/.claude-plugin/plugin.json`: `1.6.2` to `1.7.0`. Not a patch: drift results move in both directions (a resolved-only round with a boilerplate lead becomes clean; a shortfall or an unparseable count line becomes drift, including on an approval, which `1.6.2` could not report), and the documented semantics of a published output field change with them.

1. `plugins/monitor-pr/scripts/resolve-copilot-threads` and `plugins/monitor-pr/.claude-plugin/plugin.json`: `monitor-pr` ships a byte-identical copy of the parser, added to main in #520 while this branch was open, and a scrut case asserts the pair matches. Copy the script across and bump `1.5.3` to `1.6.0`, matching the minor bump the other plugin took for the same helper change.

No change to the `monitor-pr` skill itself. Escalating on drift is the behavior that is wanted; this narrows what counts as drift, and only the bundled parser copy moves. No root README or marketplace change, since those descriptions must match verbatim and do not state the rule.

`make build` regenerates `dist/codex/plugins/resolve-copilot-pr-feedback/` and `dist/codex/plugins/monitor-pr/` (each script, `SKILL.md` and the manifest copy). `dist/opencode/` links skills only and needs no script mirror. Do not hand-edit either tree.

## Verification

Run from the repository root:

```bash
make build
make test-scrut
make test-all
```

Confirm the parser directly against the fixtures, which is the same seam the scrut suite uses, since `fetch-reviews` needs an authenticated `gh` that the test environment does not have:

```bash
for f in tests/data/copilot-reviews/*.json; do
  printf '%s: ' "$(basename "$f" .json)"
  plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads parse-reviews \
    < "$f" \
    | jq -c '[.[] | {verdict, hasFormatDrift, findings: (.findings | length)}]'
done
```

Expect `hasFormatDrift: false` for `format-d-clean`, `format-d-open-only` and `format-d-resolved-only`, `true` for `format-d-resolved-lead`, `format-d-count-mismatch`, `format-d-header-drift`, `format-d-phrase-mention`, `format-d-headline-only` and `format-d-drift`, and no change for every other fixture.

The exemptions are escape hatches, so confirm they are pinned rather than merely exercised. Loosening either section regex to its bare phrase, widening the resolved count to accept `(0)`, dropping the lead check, treating an unparseable count line as absent, ignoring `open_thread_count` in the comparison, subordinating the shortfall to the verdict, or dropping the `$is_v2` guard must each fail at least one case. Matching the boilerplate lead by prefix rather than in full is the one mutation the suite does not catch; a fixture for it would need a lead that opens with the same words and then says something else, which is not a shape Copilot emits.

Then confirm the real body from issue #491 clears, using the review that triggered it:

```bash
gh api repos/cboone/agent-harness-plugins/pulls/471/reviews --paginate \
  | plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads parse-reviews \
  | jq -c '.[] | select(.id == 5261480703) | {verdict, hasFormatDrift, findings: (.findings | length)}'
```

That call reads a pull request in this repository and writes nothing.

Finally, run the `check-versions` skill before opening the pull request, since another branch may have already moved this plugin's version.
