# Account for every Copilot finding signal, not just the parsed ones

Addresses #536, #529, #526, #492 and #449 in part or in full. See [Related issues](#related-issues) for what each one contributes and what stays out of scope.

## Context

Copilot keeps changing the layout of its PR review bodies, and `resolve-copilot-threads parse-reviews` keeps falling behind. Each round of catch-up adds another positive-match parser or another drift exemption. None of them asks whether the whole body has been accounted for.

This plan builds on #516 and #520, both merged to `main`:

- #516 adds the `**Findings:**` count reconciliation, the resolved-round exemption, depth-one section matching (`section_summary`), and an element-vocabulary check (`has_unrecognized_element`).
- #520 adds the byte-identical copy of `resolve-copilot-threads` that `monitor-pr` runs as its feedback probe.

The two copies are identical on `main`, and `tests/scrut/repo-tooling.md` keeps them that way.

### What two samples of live reviews show

The `main` parser was run over two samples of Copilot reviews on `cboone`-authored PRs across the `cboone` and `swing-left` organizations:

- 450 reviews collected on 2026-09-23, from 80 PRs in 12 repositories;
- 320 reviews submitted between 2026-09-24 and 2026-10-06, from 100 PRs.

Every review since 2026-09-18 uses `ccr-overview-v2`. The findings fall into four groups.

**1. Findings silently lost.** Ten reviews have more finding-shaped items in the body than the parser returned, with `hasFormatDrift: false` on every one. In each case an `Open (N)` list exempted the review from drift.

| Shape                                                                                | Example                                              | Parsed |
| ------------------------------------------------------------------------------------ | ---------------------------------------------------- | ------ |
| Bold severity tokens in file-summary cells, `**Critical (1 vote):**`                 | `swing-left/votefwd#4401` review 5256528931          | 0 of 2 |
| Bold tokens after a cell's description, items separated by a period                  | `swing-left/frontend#2115` review 5423279373         | 0 of 7 |
| Period separators and `Moderate (1 vote each): X, and Y`                             | `swing-left/votefwd#4430` review 5262235124          | 2 of 3 |
| Lowercase severity after a semicolon, `...; moderate (1 vote): ...`                  | `cboone/agent-harness-plugins#549` review 5387832312 | 5 of 6 |
| A v2 `Review findings:` label followed by `- **Critical (2 votes):** <text>` bullets | `cboone/audio-lab#1` review 5387781408               | 0 of 5 |
| The same bullets under the older "Pull request overview"                             | `cboone/agent-harness-plugins#452` review 5216344437 | 4 of 7 |

The bullet form was first seen inside `ccr-overview-v2` on 2026-10-02, so it is current rather than legacy.

**2. Drift that is not a format change.** 95 of the 320 recent reviews (30%) report `hasFormatDrift: true`. Of those, 94 are `### 🔵 Needs a closer look` with `**Findings:** None`, where the only content is the lead paragraph, with no sections or with a `Resolved since last review` section only. The leads are a mix of three things:

- new findings stated only in prose, such as "Add migration-level coverage for the upgrade and lossy downgrade paths." This is #492's shape.
- restatements of threads opened in earlier rounds, such as "Address the three moderate issues involving concurrent digest delivery, retry starvation, ...". `fetch` reports those threads, or already reports them resolved.
- advisory requests for human review that name no defect, such as "Authentication and logout changes warrant final human review." This is #536's shape.

Today all three are drift. Drift is a workflow-level failure, so the resolver reports `Partial` and `monitor-pr` escalates. Review bodies are immutable, so the escalation can never clear. This is now the largest cost of the current design, larger than the silent misses.

**3. Notices that are not reviews.** Two bodies are Copilot notices rather than reviews. "Copilot encountered an error and was unable to review this pull request" and "Copilot wasn't able to review any files in this pull request" both parse with no verdict, no findings and no drift, so they read as clean. This is #449's shape.

**4. Login spelling.** REST reports Copilot's inline comments as `Copilot` (capital C), while GraphQL reports `copilot-pull-request-reviewer` and REST reviews report `copilot-pull-request-reviewer[bot]`. `fetch` reads GraphQL and is unaffected, but any new REST read must match logins case-insensitively.

### Why the current design falls behind

`hasFormatDrift` carries two meanings with different remedies:

- **The parser could not read the layout.** The remedy is a parser change, so a loud and lasting signal is right.
- **The parser read the layout, and the content is prose.** The remedy is a person or agent reading it, after which nothing is left to fix.

Merging the two makes the first too quiet and the second too loud. The first is too quiet because, to keep the second from escalating forever, the drift rule grew exemptions (`Open (N)` present, resolved-only round with the fixed lead sentence), and every exemption is a place where a partial parse goes unseen. That is how every silent miss in the table happened. The second is too loud because it escalates reviews that only needed reading, as group 2 shows.

### Intended outcome

- **Structure is reconciled mechanically.** Every finding-shaped signal in a body is matched to a parsed finding or an inline thread. Anything left over is format drift, with the line it came from.
- **Prose is routed to a reader, not to an escalation.** A non-clean verdict whose content is lead prose becomes a recovered finding that goes through the normal categorization, including a new Advisory category.
- **Notices are classified as notices**, so they never count as a clean review.
- **Format changes are noticed early** by a canary over recent reviews, before a stuck watch reveals them.

## Design

### Layer 1: signal census (`unaccounted`)

Add a census to the jq program in `do_parse_reviews` that runs independently of the parsers. It scans the raw body with patterns that do not depend on layout, sorts each signal into the body region it sits in, and reconciles each region's signals against the findings the parsers attributed to that region.

**Regions.** Each top-level `<details>` block is a region, keyed by its `<summary>` title with counts, tags and badge markup removed, using the same depth tracking as #516's `section_summary`. The text before the first `<details>` is the region `lead`. A `###` heading inside a details block opens a nested region keyed by that heading, which is how the older layout nests `### Suppressed comments (N)` inside "Review details". A `Review findings:` label, bold or plain, opens a nested region in the same way.

**Signals.** Each pattern is applied line by line, after removing U+200B and ignoring fenced blocks and inline code spans:

| Kind            | Pattern                                                                                  |
| --------------- | ---------------------------------------------------------------------------------------- |
| `vote`          | `\([0-9]+ votes?( each)?\)`, case-insensitive on the severity word, optional `**` around |
| `location`      | a line that is only `**path:line**`, or that opens with `` `path:line` ``                |
| `section-count` | a depth-one `<summary>`, or a `###` line, ending in `(N)` with `N` greater than 0        |
| `thread-link`   | a list item linking `#discussion_r<id>`                                                  |

Severity badges are not counted separately. Every observed badge sits on a thread-link item, on a `Previously missed` entry that already has a `location`, or on the `**Findings:**` line, so counting badges would only double-count.

**Accounting rules.** A signal is consumed when:

- it is a `thread-link`. That is an inline thread, which `fetch` reports.
- it sits in a region whose parsers produced at least as many findings as the region has `vote` plus `location` signals. A `( each)` vote stands for at least one finding, so the comparison is `>=`.
- it is a `section-count` whose `N` equals the region's item count: parsed findings plus `thread-link` items. This holds whatever the section is called, so a new section that lists threads, like `Open` and `Resolved since last review` do, is accounted for on its first appearance. A new section whose items the parsers cannot read is not.

Every signal left over becomes an `unaccounted` entry, `{kind, region, line, text}`, where `text` is the source line truncated to 200 characters.

**Finding provenance.** Each parser tags its findings with `source` (`suppressed`, `previously-missed`, `table`, `review-findings` or `lead`) and `region`. The census needs `region` for attribution, and `source` makes the summary table and the fixtures easier to read. Both are new, additive output fields.

The census is deliberately a counting check, not a second parser. It never extracts a finding. It only asks whether a region holds more finding-shaped things than its parsers returned. That keeps it simple enough to stay correct while the parsers change.

### Layer 2: split drift from prose (`hasFormatDrift`, `needsRead`)

Redefine the output around the two meanings:

- **`hasFormatDrift`** means the parser could not read the layout. It is true when:
  - `unaccounted` is non-empty;
  - #516's stated-count shortfall or unparseable `**Findings:**` line applies;
  - a legacy suppressed section yields no findings;
  - `reviewKind` is `unknown` (Layer 3).

  It keeps today's consequence: a workflow-level failure, `Partial`, and a `monitor-pr` escalation.

- **`needsRead`** means the layout was read, and the lead paragraph is the only place a concern can be stated. It is true for a non-green verdict when the body has no `Open (N)` threads and no parsed findings, and the lead is not one of the known no-finding sentences. This is the branch that currently reports drift through #516's unexplained-verdict rule.

When `needsRead` is true, the script also emits the lead as one finding: `{source: "lead", region: "lead", path: null, line: null, location: "(review overview)", severity: null, body: <lead paragraph>}`. This is #492's proposal. Severity stays null rather than being inferred from the verdict color.

**Known no-finding leads.** #516's exact match on "One or more issues must be addressed before approval." becomes a short allowlist, seeded from the samples. A lead on the list clears `needsRead`. A lead not on the list costs a read, never an escalation. That resolves #529: a reworded boilerplate sentence now produces a lead finding that the agent recognizes as a no-op, instead of an escalation that can never clear. The resolved-round exemption and `has_unrecognized_element` stay as #516 left them, guarding the clean path. They no longer decide drift, because prose is no longer drift.

`has_unrecognized_element` stays scoped to the resolved-round path. Applied to every v2 body, it would fire on 2 of the 320 recent reviews, where finding prose contains placeholders such as `<out-file>` and `<name>` outside code spans.

### Layer 3: review kind (`reviewKind`)

Classify each Copilot review body:

- `review`: a v2 body, or a legacy body with a verdict heading or a "Pull request overview" section.
- `error`: the "encountered an error and was unable to review" notice.
- `no-files`: the "wasn't able to review any files" notice.
- `unknown`: any other non-empty body with no v2 marker and no legacy structure.

`error` and `no-files` produce no findings and no drift, and a caller must never treat them as a clean review. `unknown` sets `hasFormatDrift`, because a body that is neither a review nor a known notice is exactly the kind of new layout this plan exists to surface. Matching the notices is case-insensitive and tolerant of surrounding whitespace, and the fixed sentences are listed in one jq constant beside the no-finding leads.

### Layer 4: parser fixes for the observed variants

These land after the census, so each fixture first shows up as `unaccounted` and then clears:

1. `table_findings` accepts:
   - a severity token in any letter case, with optional `**` around the token and between `):` and the text;
   - `( each)` after the vote count;
   - a token that follows a cell's description text, not only one at the start of the summary;
   - items separated by a period and a space, as well as by a semicolon and a space.

   It still requires the separator immediately before a severity token, so prose such as "Nit (1 vote):" inside a finding stays part of that finding.

1. A new `review_findings_bullets` parser reads `- **<Severity> (<N> votes?( each)?):** <text>` bullets in the region a `Review findings:` label opens, in v2 bodies and under the older "Pull request overview". When the text opens with a backticked path, the parser uses that path. Otherwise it reports `path: null`.

A finding with no path is new to the output contract, both here and for the lead finding. `SKILL.md` step 1c matches prior dispositions by path. For a finding with no path, the identity becomes the body excerpt alone, following the existing rule for findings with no line.

### Layer 5: input hardening (#526)

The census adds more string processing per review, which widens #526's failure. Change the per-review `select` to require `(.body | type) == "string"`. Report a skipped review on stderr with its id, rather than aborting the batch. Check the jq version in `require_jq` against the oldest release that defines two-argument `scan`, and name the version in the error.

### Layer 6: surface audit (`audit` command)

Add `resolve-copilot-threads audit OWNER REPO PR`, a read-only command that lists every Copilot-authored item on the PR by where it appears, and flags any item the typed commands do not cover:

- **Reviews**: REST `pulls/N/reviews`, as `fetch-reviews` reads them.
- **Review comments**: REST `pulls/N/comments`, grouped by `pull_request_review_id`. Each comment is checked against the GraphQL review threads, resolved threads included, by `databaseId`. A Copilot comment in no thread is `uncovered`.
- **Issue comments**: REST `issues/N/comments`. Every Copilot-authored issue comment is `uncovered`, since nothing reads that surface today. The resolver's `## Copilot Feedback Summary` comments are authored by the user, so they never match.
- **Legacy reviews needing a read**: a legacy-layout review with a non-green verdict, no parsed findings and no inline comments attached to its id. The legacy body cannot say whether its findings are inline, so only this join can set `needsRead` for it.

Login matching here compares `ascii_downcase` against the lowercased direct-login list. The list itself stays as it is.

Output: `{surfaces: {reviews, reviewComments, issueComments}, uncovered: [...], legacyNeedsRead: [review ids]}`. The pure join is exposed as `parse-audit`, which reads `{reviews, reviewComments, issueComments, threads}` on stdin, so it can be tested with fixtures, as `parse-reviews` is.

### Layer 7: agent reconciliation in `SKILL.md`

Add a step 1d, "Reconcile what the parsers could not":

1. Run `audit`. Read each `uncovered` item, then categorize and handle it as a finding with source `Uncovered <surface>`.
1. Choose the reviews in scope:
   - every review with `hasFormatDrift` or `needsRead`;
   - every id in `legacyNeedsRead`;
   - the newest review against the current head, always, because that is where a new layout first appears.
1. For each review in scope, list every concern that `headline` and `reviewBody` state, skipping file-summary rows with no signal. Match each concern to a thread from `fetch` (open or already resolved), a parsed finding, or a `Previously handled` row. Handle each unmatched concern as a finding with source `Review prose` and the most specific location the text supports, never an invented line.
1. Report every `unaccounted` entry and every `unknown` review in the step 7 summary, under a "Format drift" note with the review link, so the parser gap gets fixed.

Add an **Advisory** category to step 2: a concern that names no defect and asks for human judgment, such as "Authentication and logout changes warrant final human review". It needs no code change, is recorded as `Noted` in the summary, and is listed in the summary's opening lines so the request reaches a person. This resolves #536.

**Terminal status.**

- `hasFormatDrift` keeps today's meaning: a workflow-level failure, so the run reports `Partial`.
- `needsRead` is not a failure. Once each lead concern is matched, handled or recorded as Advisory, the run can report `Completed`.
- An `error` or `no-files` review against the current head makes the status `Failed` for that review, with the notice quoted.

### Layer 8: `monitor-pr`

The step 3 probe projects `needsRead`, `reviewKind` and `unaccounted | length` alongside the fields it projects today.

- Step 4 dispatches a `needsRead` review to the resolver once per review id, like review-body findings. A `needsRead` review that the resolver has already processed clears the axis on a `Completed` outcome and never escalates on its own.
- Drift keeps its escalation path.
- An `error` or `no-files` review against the current head never satisfies the Copilot axis. The watch requests a fresh review once per head, under the existing request guard, and escalates if the next review is also a notice. That covers #449's acceptance criteria for the decision flow. The criteria about `--confirm-clean` pairs follow from the same rule, because a notice is never a clean review.

### Layer 9: format canary

Add `bin/copilot-review-canary`, following `bin/version-audit`: it prints nothing when clean and a report otherwise. It takes `--repo OWNER/REPO` (repeatable) or `--author LOGIN --since DATE`, lists the matching PRs, runs `fetch-reviews` and `audit` over each, and reports by URL and kind every review with:

- `unaccounted` entries;
- `reviewKind: unknown`;
- `uncovered` items;
- a lead that matches no known no-finding sentence on an otherwise clean round.

The last check is the early warning #529 asks for. It also prints a structural inventory (headings, `<summary>` titles, line-start labels and list-item shapes, with counts and first-seen dates) and marks entries not seen in a committed baseline. That is how the `Review findings:` bullets would have been noticed on 2026-10-02.

The canary never writes fixtures. Turning a report into a fixture is a manual step, because reviews from private repositories must be rewritten before they enter this public repository.

The canary runs locally only, with the user's own `gh` login, and prints its report to the terminal. It has no scheduled workflow, for three reasons:

- A workflow's `GITHUB_TOKEN` reads only this repository. That sample is too thin, and most format changes so far appeared first in other repositories, several of them private.
- Reading both the `cboone` and `swing-left` repositories from a workflow would need a token for each owner, a classic token, or a GitHub App.
- A report filed as an issue here would be public, and it would name or quote PRs in private repositories.

Running it locally needs no new credential and publishes nothing. Revisit a scheduled run if local sweeps prove too infrequent to give early warning.

## Phases and files

Each phase is a separate commit or group of commits, and each leaves `make test-all` passing. Script changes go to `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads` and are copied to `plugins/monitor-pr/scripts/resolve-copilot-threads` in the same commit, so the `cmp` testcase stays green.

### Phase 1: fixtures that fail first

Add fixtures to `tests/data/copilot-reviews/`, using the existing JSON shape and unused `6000000xxx` ids. Text from private repositories is rewritten, keeping only the structure.

1. `format-d-bold-votes.json`: bold tokens in two table rows, with a matching `Open (2)`. Synthetic text, based on the `votefwd#4401` shape.
1. `format-d-bold-after-description.json`: bold tokens after a cell description, items separated by a period. Synthetic text, based on the `frontend#2115` shape.
1. `format-d-sentence-items.json`: period separators and a `(1 vote each)` item. Synthetic text, based on the `votefwd#4430` shape.
1. `format-d-lowercase-severity.json`: review 5387832312 from #549, copied verbatim, since this repository is public.
1. `format-d-review-findings-bullets.json`: a v2 `Review findings:` label with five bullets, one `(1 vote each)`. Synthetic text, based on the `audio-lab#1` shape.
1. `format-b-overview-bullets.json`: review 5216344437 from #452, verbatim.
1. `format-d-advisory-lead.json`: the #536 body from the issue, with `Resolved since last review (2)`.
1. `format-d-prose-lead.json`: the #492 body from review 5261449073 on #489, verbatim.
1. `format-d-reworded-boilerplate.json`: a resolved-only round whose lead rewords the fixed sentence.
1. `notice-error.json` and `notice-no-files.json`: the two Copilot notices, verbatim. Neither carries repository content.
1. `notice-unknown.json`: a non-empty body with no v2 marker and no legacy structure.
1. `format-d-new-thread-section.json`: an invented `<summary><strong>Deferred (2)</strong></summary>` section whose items are thread links. Expects no drift.
1. `format-d-new-prose-section.json`: the same section, with prose items and no thread links. Expects drift.
1. `format-d-each-overcount.json`: a negative control. A `(1 vote each)` item that parses into two findings must not be reported as unaccounted.
1. `malformed-body.json`: one valid v2 review and one review with `"body": 12345` (#526).

Add scrut cases to `tests/scrut/resolve-copilot-threads.md` that assert today's projections, so the gaps are recorded before any fix.

### Phase 2: hardening and census

1. The body-type guard and the jq version check (Layer 5).
1. Region splitting, the signal kinds, accounting, `unaccounted`, and `source` and `region` on findings (Layer 1). The census adds to the existing drift expression at this phase. Nothing is removed yet.
1. Scrut: the six group-1 fixtures report `hasFormatDrift: true` with the expected `unaccounted` kinds. `format-d-new-prose-section` reports drift, and `format-d-new-thread-section` does not. Every existing fixture's projections are unchanged except for the new fields.
1. Use the `plant-defects` skill to confirm the census cannot pass trivially. Each of these mutations must fail at least one case: dropping a signal kind, dropping `( each)`, changing `>=` to `>`, ignoring regions, counting signals inside code spans.

### Phase 3: parser fixes

1. The `table_findings` changes and `review_findings_bullets` (Layer 4).
1. Scrut: the six group-1 fixtures now parse fully and report `unaccounted: []`.

### Phase 4: drift split and review kind

1. `needsRead`, the lead finding, the no-finding lead allowlist, and the narrowed `hasFormatDrift` (Layer 2). Then `reviewKind` (Layer 3).
1. Scrut:
   - `format-d-advisory-lead`, `format-d-prose-lead` and `format-d-reworded-boilerplate` report `needsRead: true`, a `lead` finding and `hasFormatDrift: false`.
   - The notices report their kinds, and `notice-unknown` reports drift.
   - Existing fixtures that #516 marks as drift only through the unexplained-verdict rule move to `needsRead`. List each one in the commit message.
1. Mutation checks: dropping the allowlist, treating `needsRead` as drift, and dropping the `unknown` kind each fail a case.

### Phase 5: surface audit

1. The `audit` and `parse-audit` commands, and the GraphQL thread-id read (Layer 6). `parse-reviews` stays free of GitHub access. Update `usage()` and the command validation in `main`.
1. Fixtures under `tests/data/copilot-audit/`: a thread-less Copilot comment, a Copilot issue comment, and a legacy prose-only review with no inline comments. Register the directory in the `Makefile`'s `SCRUT_ENV` and in CI's `scrut-env` list.

### Phase 6: skills

1. `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`:
   - the step 1b output contract: `unaccounted`, `needsRead`, `reviewKind`, `source`, `region`, findings with no path, and the narrowed `hasFormatDrift`;
   - the new step 1d, and the Advisory category in step 2;
   - the step 1c identity rule for findings with no path;
   - the `Review prose`, `Uncovered <surface>` and `lead` sources in the step 7 table, and the terminal-status rules from Layer 7;
   - `audit` in the permitted-operations list, as a read.
1. `plugins/monitor-pr/skills/monitor-pr/SKILL.md` and `references/checkpoint.md`: the probe projection, the dispatch rule, the notice rule and the escalation table (Layer 8). The README notes the new fields.
1. Plugin versions: `resolve-copilot-pr-feedback` from `1.7.0`, and `monitor-pr` from `1.6.1`. Both are minor bumps, following #516's precedent: new commands and fields, and drift results that move in both directions. Run the `check-versions` skill before opening the PR.
1. `make build` to regenerate `dist/codex/` for both plugins.

### Phase 7: canary

1. `bin/copilot-review-canary`, requiring `jq` and an authenticated `gh`. Include it in `bin/list-shell-scripts` coverage, and document it in `bin/AGENTS.md` next to `version-audit`. Commit the structural baseline as `tests/data/copilot-review-structure.json`. It holds skeletons only, never body text.
1. Scrut coverage that runs the canary against a stubbed `gh` in `tests/fixtures/`. It must print a report for a drift fixture and for an unseen skeleton, and nothing for a clean one.
1. Mention the canary in the root `CLAUDE.md` tooling paragraph, next to `bin/version-audit`, as a local audit that is neither scheduled nor a merge gate.

## Verification

Run from the repository root:

```bash
make build
make test-all
```

**Calibration against live data.** Recreate both samples locally, outside the repository, and run each phase's parser over them. The acceptance bar:

- the ten group-1 reviews report `unaccounted` entries after Phase 2, and none after Phase 3;
- after Phase 4, `hasFormatDrift` is true only for reviews with a structural cause. Each one is listed in the PR body by URL and cause. The 94 lead-only reviews move to `needsRead`;
- the two notices classify as `error` and `no-files`.

Record the counts in the PR body. Never include body text from private repositories.

**Live probes.** After Phase 5, run `audit` against #549, #530 and #520 in this repository, and confirm that `uncovered` and `legacyNeedsRead` are empty or explained. These calls read and write nothing.

## Related issues

| Issue | Relationship                                                                                                                                                                             |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| #536  | Resolved by Layers 2 and 7: an advisory lead is `needsRead`, handled as Advisory, and no longer escalates.                                                                               |
| #529  | Resolved by Layers 2 and 9: a reworded boilerplate lead costs a read rather than an unclearable escalation, and the canary reports the reword.                                           |
| #492  | Resolved by Layer 2: the lead becomes a recovered finding with `source: lead`. Unlike the issue's suggestion, `hasFormatDrift` stays false, because `needsRead` now carries that signal. |
| #526  | Resolved by Layer 5.                                                                                                                                                                     |
| #449  | Resolved in the parser and in `monitor-pr`'s decision flow by Layers 3 and 8.                                                                                                            |
| #464  | Out of scope. The census, `reviewKind` and `audit` are shaped so a later multi-reviewer skill can reuse them for each bot, but nothing here generalizes past Copilot.                    |
| #463  | Independent. Resolution reasons attach to thread resolution, which this plan does not change.                                                                                            |

Close #536, #529, #492 and #526 from the PR. #449 can close too, once its regression scenario is in place in the scrut suite.

## Decisions

1. **Canary scope (2026-10-06).** The canary is local-only, with no scheduled workflow, for the reasons given under Layer 9.

## Open questions

1. **Advisory reach.** An Advisory concern is recorded and surfaced, but it does not block. If such leads should hold `monitor-pr` short of ready until a person acknowledges them, that is a separate escalation rule. This plan does not add it.
1. **Restated threads.** A lead that restates earlier threads is matched against `fetch` by the agent in step 1d. If calibration shows these dominate `needsRead`, a later change could match thread titles mechanically. This plan leaves the matching to the agent, because the leads paraphrase freely.
