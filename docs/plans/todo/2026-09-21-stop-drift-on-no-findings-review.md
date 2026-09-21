# Stop review-body drift on a clean no-findings review

Addresses [issue #491](https://github.com/cboone/agent-harness-plugins/issues/491).

## Context

`resolve-copilot-threads parse-reviews` sets `hasFormatDrift` for a `ccr-overview-v2` review when the parser recovers no findings, the verdict heading is not `### 🟢 Approval recommended`, and the body lists no `Open (N)` inline threads. The rule assumes that a non-clean verdict with nothing parseable means Copilot shipped a layout the parser does not understand.

Copilot violates that assumption. On [review 5261480703](https://github.com/cboone/agent-harness-plugins/pull/471#pullrequestreview-5261480703) it paired `### 🔵 Needs a closer look` with `**Findings:** None` and a `Resolved since last review (1)` section listing the thread closed in the previous round. Nothing was outstanding, but the review reported drift.

A false positive here cannot clear. A review body is immutable, `fetch-reviews` returns every Copilot review on the pull request, and `monitor-pr` treats drift as not clean, so every later tick re-reads the same body, escalates, and records a workflow failure on a pull request with no feedback left to address.

The intended outcome: a review that reports no findings and lists only resolved items reads as clean, while a review whose stated finding count exceeds what the parser recovered still reports drift.

## Approach

Add two body signals to the jq parser in `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`, then make the v2 branch of the drift condition consult them.

### Why the stated count is not authoritative on its own

The issue proposes treating `**Findings:** None` as authoritative for any `ccr-overview-v2` body. The fixtures show that it is not. `tests/data/copilot-reviews/format-d.json` pairs `**Findings:** None` with a non-clean verdict and two real findings appended to file-summary cells, and `format-d-repeated.json` and `format-d-table-edge.json` do the same. Comparing that against `format-d-open-only.json` (`**Findings:** 2`, `Open (2)`) and `format-d-previously-missed.json` (`**Findings:** 1`, one nested finding) shows what the header counts: open inline threads and `Previously missed` entries, not the line-less findings in file-summary tables, and not resolved entries.

So the count is authoritative about a shortfall and silent about a surplus. A count above zero that recovers nothing is a real miss. `None` only means those two categories are empty, and a future layout that Copilot does not count would go silent if `None` alone cleared the signal. Recognizing the `Resolved since last review (N)` section is what actually clears the #471 body, and it clears exactly the reviews whose remaining content the parser already understands.

### Parser changes

In the jq program inside `do_parse_reviews`, beside the existing `lists_open_threads` definition:

1. `lists_resolved_threads`: `test("<summary>(<[^>]+>)*Resolved since last review \\([1-9][0-9]*\\)")`, mirroring the `lists_open_threads` pattern so the optional `<strong>` wrapper still matches. Comment it as a record of work already closed, not feedback to act on, so its links are a known section rather than a finding the parser missed.
1. `stated_finding_count`: scan for `^\\*\\*Findings:\\*\\*[[:blank:]]*(None|[0-9]+)` case-insensitively, returning `0` for `None`, the number otherwise, and `null` when the line is absent (older layouts). Document the asymmetry established above: authoritative about a shortfall, silent about a surplus.

Bind both in the per-review pipeline next to `$lists_open_threads`, guarded by `$is_v2` the same way, then replace the v2 clause of `hasFormatDrift`:

```jq
hasFormatDrift: (
  ($findings | length) == 0
  and (
    $has_suppressed_marker
    or (
      $is_v2
      and ($lists_open_threads | not)
      and (
        ($stated_findings // 0) > 0
        or (
          $verdict != "### 🟢 Approval recommended"
          and ($lists_resolved_threads | not)
        )
      )
    )
  )
),
```

`($stated_findings // 0) > 0` sends both a missing line and a stated `None` down the verdict path, so layouts that predate the header keep their current behavior. A stated count above zero reports drift regardless of which sections the body lists, which keeps the resolved-section exemption from swallowing a genuine shortfall. `lists_open_threads` continues to suppress drift first, preserving the existing contract that threads reported by `fetch` explain a non-clean verdict by themselves.

Resulting behavior:

| Body                                                         | Before | After |
| ------------------------------------------------------------ | ------ | ----- |
| Clean verdict, `Findings: None`, resolved section            | false  | false |
| Non-clean verdict, `Findings: None`, resolved section (#471) | true   | false |
| Non-clean verdict, `Findings: None`, unfamiliar markup       | true   | true  |
| Non-clean verdict, `Findings: 2`, nothing recovered          | true   | true  |
| Non-clean verdict, `Open (N)` listed                         | false  | false |
| Legacy suppressed section with no parseable findings         | true   | true  |

## Files to change

1. `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`: the two new jq definitions, the two new bindings, the rewritten `hasFormatDrift` expression, and the `Review-body findings` header comment at the top of that section, which currently describes drift as "a non-clean v2 verdict that neither structured findings nor open inline threads explain".
1. `tests/data/copilot-reviews/format-d-resolved-only.json`: new fixture reproducing the #471 body. Non-clean verdict, `**Findings:** None`, a `Resolved since last review (1)` section, no `Open` section. Follow the existing fixture shape and continue the id sequence at `6000000010`.
1. `tests/data/copilot-reviews/format-d-count-mismatch.json`: new fixture with `**Findings:** 2`, a non-clean verdict, a `Resolved since last review (1)` section, and no recoverable finding, at id `6000000011`. Pairing a stated count with a resolved section is what proves the count path overrides the new exemption.
1. `tests/data/copilot-reviews/format-d-headline-only.json`: new fixture at id `6000000012`, copied from reviews 5262190988, 5262269024 and 5262292015 on pull request #471. Non-clean verdict, `**Findings:** None`, no section at all, findings stated in the lead paragraph alone. This is the boundary the chosen rule creates, and it occurs in production, so it needs a guard against a later change that trusts `**Findings:** None` outright.
1. `tests/scrut/resolve-copilot-threads.md`: one case per new fixture, placed next to the existing `Overview v2 open threads explain a non-clean verdict` and `Overview v2 format drift` sections and following their prose-then-`scrut`-block form. `format-d-drift.json` and its case are unchanged, which is itself the regression guard for an unfamiliar layout that states no findings.
1. `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`: the `hasFormatDrift` bullet in the step 1b output contract, and the trailing clause of the `verdict` bullet, which says the verdict "drives the drift check" and is now one of three inputs. The `Format-drift rule (CRITICAL)` paragraph and the terminal-status wording stay as they are, since the meaning of a true result has not changed.
1. `plugins/resolve-copilot-pr-feedback/.claude-plugin/plugin.json`: `1.6.2` to `1.6.3`. This is a bug fix in an existing signal, so it is a patch. The plugin has no `.codex-plugin/plugin.json`, so there is no second manifest to mirror.

No `monitor-pr` change. Escalating on drift is the behavior that is wanted; this narrows what counts as drift. No root README or marketplace change, since those descriptions must match verbatim and do not state the rule.

`make build` regenerates `dist/codex/plugins/resolve-copilot-pr-feedback/` (the script, `SKILL.md` and the manifest copy). `dist/opencode/` links skills only and needs no script mirror. Do not hand-edit either tree.

## Verification

Run from the repository root:

```bash
make build
make test-scrut
make test-all
```

Confirm the parser directly against the fixtures, which is the same seam the scrut suite uses, since `fetch-reviews` needs an authenticated `gh` that the test environment does not have:

```bash
for f in format-d-clean format-d-open-only format-d-drift format-d-resolved-only format-d-count-mismatch format-d format-d-table-edge format-d-repeated format-d-previously-missed; do
  printf '%s: ' "$f"
  plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads parse-reviews \
    < "tests/data/copilot-reviews/$f.json" \
    | jq -c '[.[] | {verdict, hasFormatDrift, findings: (.findings | length)}]'
done
```

Expect `hasFormatDrift: false` for `format-d-resolved-only`, `true` for `format-d-count-mismatch`, `true` for `format-d-drift`, and no change for every other fixture.

Then confirm the real body from issue #491 clears, using the review that triggered it:

```bash
gh api repos/cboone/agent-harness-plugins/pulls/471/reviews --paginate \
  | plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads parse-reviews \
  | jq -c '.[] | select(.id == 5261480703) | {verdict, hasFormatDrift, findings: (.findings | length)}'
```

That call reads a pull request in this repository and writes nothing.

Finally, run the `check-versions` skill before opening the pull request, since another branch may have already moved this plugin's version.
