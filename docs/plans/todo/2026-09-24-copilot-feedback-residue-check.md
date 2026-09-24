# Account for every Copilot finding signal, not just the parsed ones

## Context

Copilot keeps changing the layout of its PR review bodies, and `resolve-copilot-threads parse-reviews` keeps falling behind. Each round of catch-up adds another positive-match parser or another drift exemption. None of them asks whether the whole body has been accounted for.

This plan builds on [#516](https://github.com/cboone/agent-harness-plugins/pull/516) (the `**Findings:**` count reconciliation and the resolved-round exemption) and [#520](https://github.com/cboone/agent-harness-plugins/pull/520) (the byte-identical copy of `resolve-copilot-threads` that `monitor-pr` runs as its feedback probe). The branch starts from `main` with both merged in.

### What a sample of live reviews shows

On 2026-09-23 the `main` parser was run over 450 Copilot reviews from the 80 most recently updated `cboone`-authored PRs across 12 repositories (`cboone/*` and `swing-left/*`). Every review since 2026-09-18 uses the `ccr-overview-v2` layout. Before that, reviews used the older "Pull request overview" layout with a suppressed-comments section.

The sample turned up three reviews where findings in the body were silently lost, and `hasFormatDrift` stayed `false` on all three:

1. **Bold severity tokens in file-summary cells.** `swing-left/votefwd#4401` review 5256528931 writes `**Critical (1 vote):** full URLs may expose ...`. `table_findings` expects the colon after `(1 vote)` to be followed directly by a space, so the closing `**` defeats it. The parser recovered 0 of 2 findings. Drift stayed off because the body lists `Open (2)`, and a listed open section exempts a review.
1. **Sentence separators and grouped votes.** `swing-left/votefwd#4430` review 5262235124 separates items with a period and a space rather than a semicolon and a space, and it writes `Moderate (1 vote each): X, and Y`. Three findings were folded into the body of one, and the `each` form matches no severity token at all.
1. **Bullet findings in the older overview.** `cboone/agent-harness-plugins#452` review 5216344437 lists seven `- **Moderate (2 votes):** ...` bullets with no path under "Pull request overview". Only the four findings in the suppressed section were parsed.

Two further observations:

- Twelve older-layout reviews have a non-green verdict, no body findings and no inline comments. For example, `swing-left/frontend#1838` review 5215168360 says "Production GA4 activation and deployed ingestion checks remain outstanding". The only finding is in the lead paragraph. The v2 equivalent already reports drift through #516.
- REST reports Copilot's inline comments as `Copilot` (capital C), while GraphQL reports `copilot-pull-request-reviewer` and REST reviews report `copilot-pull-request-reviewer[bot]`. `fetch` reads GraphQL, so it is unaffected today, but any new REST read must match logins case-insensitively.

### Why the current design falls behind

Drift is defined as "the parsers found nothing, and nothing else explains the verdict". It therefore fires only when a review yields nothing at all. A partial parse turns it off, and so does an `Open (N)` list, and that is exactly how the new variants appear. #516 adds one reconciliation, the stated `**Findings:**` count against `Open (N)`. But that count covers inline threads only, so it cannot see findings in table cells, bullets or prose.

### Intended outcome

A layered check in which every finding-shaped signal in a review body must be matched by something the tooling or the agent accounts for. Anything left over is reported, with the line it came from, instead of being dropped. The parsers still do the extraction. The new layers make a parser gap loud instead of silent.

## Design

Five layers, from most to least mechanical. Layers 1 and 4 are what would have caught every miss above. Layers 2, 3 and 5 give earlier warning of a new layout.

### Layer 1: signal census (`unaccounted`)

Add a census to the jq program in `do_parse_reviews` that runs independently of the parsers. It scans the raw body with patterns that do not depend on layout, sorts each signal into the body region it sits in, and reconciles the signals in each region against the findings the parsers attributed to that region.

**Regions.** Each `<details>` block is a region, keyed by its `<summary>` title with counts, tags and badge markup removed. The text before the first `<details>` is the region `lead`. A `###` heading inside a details block opens a nested region keyed by that heading, which is how the older layout nests `### Suppressed comments (N)` inside "Review details".

**Signals:**

| Kind            | Pattern (applied line by line, after removing U+200B)                     |
| --------------- | ------------------------------------------------------------------------- |
| `vote`          | `\([0-9]+ votes?( each)?\)`, with optional surrounding `**`               |
| `severity`      | a `<img ... alt="<Word> severity"` badge                                  |
| `location`      | a line that is only `**path:line**`, or that opens with `` `path:line` `` |
| `section-count` | a `<summary>` or `###` line ending in `(N)` with `N` greater than 0       |
| `thread-link`   | a list item linking `#discussion_r<id>`                                   |

**Accounting rules.** A signal is consumed when:

- it is a `thread-link`, or a `severity` badge on the same list item as one. These are inline threads, which `fetch` reports.
- it sits in a region whose parser produced at least as many findings as that region has `vote` plus `location` signals. A `( each)` vote counts as at least one finding, so `>=` is the comparison.
- it is the `**Findings:**` line's badges, which #516's `stated_finding_count` already reconciles.
- it is a `section-count` whose `N` equals the number of items the region yielded: parsed findings for finding regions, and `thread-link` items for `Open` and `Resolved since last review`. Any other titled count is unaccounted. That makes a new section such as `Deferred (2)` loud on its first appearance.

Every signal left over becomes an `unaccounted` entry, `{kind, region, line, text}`, where `text` is the source line truncated to 200 characters. `hasFormatDrift` becomes the existing #516 expression `or (unaccounted | length) > 0`. The #516 branches stay unchanged. The census adds to them and does not replace them, because the lead-paragraph and stated-count checks cover prose, which has no signal to count.

**Finding provenance.** Each parser tags its findings with `source` (`suppressed`, `previously-missed`, `table` or `overview-bullets`) and `region`. The census needs `region` for attribution, and `source` makes the summary table and the fixtures easier to read. Both are new, additive output fields.

The census is deliberately a counting check, not a second parser. It never tries to extract a finding. It only asks whether a region contains more finding-shaped things than its parser returned. That keeps it simple enough to stay correct while the parsers keep changing.

### Layer 1b: parser fixes for the observed variants

These land after the census, so that each fixture first shows as `unaccounted` and then clears:

1. `table_findings` accepts an optional `**` before the severity word and between `):` and the text, accepts `( each)` after the vote count, and splits items at a period and a space as well as at a semicolon and a space. It still requires the separator to come immediately before a severity token, so prose such as "Nit (1 vote):" inside a finding stays part of that finding.
1. A new `overview_bullet_findings` parser reads `- **<Severity> (<N> votes?):** <text>` bullets inside the "Pull request overview" region of the older layout. These findings have no path, so they report `path: null`, `line: null` and `location: "(review body)"`.

A finding with no path is new to the output contract. `SKILL.md` step 1c matches prior dispositions by path. For a finding with no path, the identity becomes the review-body excerpt alone, following the existing rule for findings with no line.

### Layer 2: structural fingerprint (`unrecognizedStructure`)

Reduce each structural line to a skeleton, and compare it with an allowlist kept as a jq constant in the script. The structural lines are HTML comment markers, `#` headings, `<summary>` titles, `**Label:**` keys at the start of a line, and table header rows. Skeletons strip counts, paths, badge markup and link text. In the 450-review sample the distinct skeletons came to about 30, listed below under Verification.

Output an `unrecognizedStructure` array of `{skeleton, line}`. Only these unknown kinds set drift:

- an HTML comment marker, such as a future `<!-- ccr-overview-v3 -->`;
- a `<summary>` title;
- a `###` heading that is not a verdict.

These are rare and stable, and each one is a new container that could hold findings. Unknown bold labels, bullet shapes and headings inside prose are reported but do not set drift, because Copilot's prose uses them freely. Setting drift for them would reintroduce the permanent false-positive loop that #516 fixed.

### Layer 3: surface audit (`audit` command)

Add `resolve-copilot-threads audit OWNER REPO PR`, a read-only command that lists every Copilot-authored item on the PR by where it appears, and flags any item the typed commands do not cover:

- **Reviews**: REST `pulls/N/reviews`, as `fetch-reviews` reads them.
- **Review comments**: REST `pulls/N/comments`, grouped by `pull_request_review_id`. Each comment is checked against the GraphQL review threads, resolved threads included, by `databaseId`. A Copilot comment in no thread is `uncovered`.
- **Issue comments**: REST `issues/N/comments`. Every Copilot-authored issue comment is `uncovered`, since nothing reads that surface today. The resolver's own `## Copilot Feedback Summary` comments are authored by the user, so they never match.
- **Reviews needing a read**: a review with a non-green or null verdict, no parsed findings, no `Open (N)` and no inline comments attached to its id. This is the older layout's prose-only shape, which the body alone cannot distinguish from a review whose findings are all inline.

Login matching for this command compares `ascii_downcase` against the lowercased direct-login list. The list itself stays as it is, so `fetch` and `parse-reviews` are unchanged.

Output: `{surfaces: {reviews, reviewComments, issueComments}, uncovered: [...], reviewsNeedingRead: [review ids]}`. Both lists empty means every Copilot item on the PR is reachable through `fetch` and `fetch-reviews`.

### Layer 4: agent reconciliation in `SKILL.md`

Add a step 1d, "Reconcile what the parsers could not":

1. Run `audit`. Treat each `uncovered` item as a finding with source `Uncovered <surface>`: read it, categorize it and handle it.
1. Choose the reviews in scope: every review with `hasFormatDrift`, non-empty `unaccounted` or unknown-structure entries, every id in `reviewsNeedingRead`, and the newest review against the current head.
1. For each review in scope, list every concern that `headline` and `reviewBody` state, skipping file-summary rows that carry no signal. Match each concern to a thread from `fetch`, a parsed finding, or a `Previously handled` row. Handle each unmatched concern as a finding with source `Review prose` and the most specific location the text supports, never an invented line.
1. Report every `unaccounted` and `unrecognizedStructure` entry in the step 7 summary, under a "Format drift" note with the review link, so the parser gap gets fixed.

Terminal status keeps today's meaning: drift is a workflow-level failure, so a run that reconciled drift by hand reports `Partial`. That is intentional, because it is what brings a parser gap to the user. The step 1d scope list keeps the reading bounded. The newest review is always read, because that is where a new layout first appears.

### Layer 5: format canary

Add `bin/copilot-review-canary`, following `bin/version-audit`: it prints nothing when clean and a report otherwise. It takes `--repo OWNER/REPO` (repeatable) or `--author LOGIN --since DATE`, lists the matching PRs, runs `fetch-reviews` and `audit` over each, and reports every review with `unaccounted`, drift-setting `unrecognizedStructure`, `uncovered` or `reviewsNeedingRead` entries, by URL and kind. It never writes fixtures. Turning a report into a fixture is a manual step, because reviews from private repositories must be rewritten before they enter this public repository.

Add a weekly `.github/workflows/copilot-review-canary.yml`, modeled on `version-audit.yml`, that runs the canary over this repository with `GITHUB_TOKEN` and opens or updates one labeled issue. Reading other repositories, including the private `swing-left` ones, needs a token with wider scope. See Open questions.

## Phases and files

Each phase is a separate commit or group of commits, and each leaves `make test-all` passing.

### Phase 0: prerequisites

1. #516 and #520 are merged to `main`. The two copies of `resolve-copilot-threads` then differ: #520 copied the script before #516 changed it, and `tests/scrut/repo-tooling.md` checks that they are byte-identical. Whichever PR merges second syncs `plugins/monitor-pr/scripts/resolve-copilot-threads` and bumps `monitor-pr`.
1. Rebase this branch onto `main`, which drops the two merge commits this branch currently carries.

### Phase 1: fixtures that fail first

Add fixtures to `tests/data/copilot-reviews/`, using the existing JSON shape and `6000000xxx` ids:

1. `format-d-bold-votes.json`: the #4401 shape with bold severity tokens in two table rows and a matching `Open (2)`. The text is synthetic, because `swing-left/votefwd` is private.
1. `format-d-sentence-items.json`: the #4430 shape with period separators and a `(1 vote each)` item. The text is synthetic.
1. `format-b-overview-bullets.json`: review 5216344437 from #452, copied verbatim because this repository is public. It has seven overview bullets and four suppressed findings.
1. `format-b-prose-only.json`: an older-layout non-green verdict whose only concern is in the lead. The text is synthetic, based on the `frontend#1838` shape.
1. `format-d-unknown-section.json`: a v2 body with an invented `<summary><strong>Deferred (2)</strong></summary>` section, to pin the `section-count` and fingerprint rules.
1. `format-e-unknown-marker.json`: a `<!-- ccr-overview-v3 -->` body that is otherwise clean.
1. `format-d-each-overcount.json`: a negative control. A `(1 vote each)` item that parses into two findings must not be reported as unaccounted.

Add scrut cases to `tests/scrut/resolve-copilot-threads.md` asserting the current (`main`) projections, so the gaps are recorded as failing behavior before any fix.

### Phase 2: census

1. `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`: region splitting, the signal kinds, accounting, the `unaccounted` field, `source` and `region` on findings, and the drift expression. Update the header comment of the review-body section.
1. Scrut: the first four Phase 1 fixtures now report `hasFormatDrift: true` with the expected `unaccounted` kinds, and every existing fixture's projections are unchanged except for the new fields.
1. Use the `plant-defects` skill to confirm the census cannot pass trivially: dropping each signal kind, dropping `( each)`, changing `>=` to `>`, and ignoring regions must each fail at least one case.

### Phase 3: parser fixes

1. `table_findings` changes and `overview_bullet_findings`, as in Layer 1b.
1. Scrut: `format-d-bold-votes`, `format-d-sentence-items` and `format-b-overview-bullets` now parse fully and report `unaccounted: []`. `format-b-prose-only` still reports drift, because prose is Layer 4's job.

### Phase 4: fingerprint

1. The skeleton allowlist and `unrecognizedStructure`, with the drift rule scoped as in Layer 2.
1. Scrut: `format-d-unknown-section` and `format-e-unknown-marker` report drift. An unknown bold label in prose is reported but does not set drift.

### Phase 5: surface audit

1. The `audit` command and its GraphQL thread-id read. `parse-reviews` stays free of GitHub access. The command's pure part, which joins already-fetched JSON, is exposed as `parse-audit`, reading `{reviews, reviewComments, issueComments, threads}` on stdin, so it can be tested with fixtures, as `parse-reviews` is.
1. Fixtures under `tests/data/copilot-audit/`: a PR with a thread-less Copilot comment, a PR with a Copilot issue comment, and the prose-only review with no inline comments. Register the directory in both `Makefile` `SCRUT_ENV` and the CI `scrut-env` list.
1. Update the `usage()` text and the command validation in `main`.

### Phase 6: skill and monitor-pr

1. `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`: the step 1b output contract (`unaccounted`, `unrecognizedStructure`, `source`, `region`, findings with no path), the new step 1d, the step 1c identity rule for findings with no path, the `Review prose` and `Uncovered <surface>` sources in the step 7 table, and the permitted-operations list (`audit` is a read).
1. Sync `plugins/monitor-pr/scripts/resolve-copilot-threads` from the resolver copy. The `monitor-pr` step 3 probe already projects `hasFormatDrift`, which now includes the census and fingerprint, so its dispatch logic needs no change. Update its prose where it lists what drift means, and note in its README that drift can now fire on partially parsed reviews.
1. Plugin versions: `resolve-copilot-pr-feedback` takes a minor bump from whatever #516 leaves (new command and new output fields; drift results change on some existing bodies). `monitor-pr` takes a minor bump because its probe's drift signal widens. Run the `check-versions` skill before opening the PR.
1. `make build` to regenerate `dist/codex/` for both plugins.

### Phase 7: canary

1. `bin/copilot-review-canary`, with `jq` and authenticated `gh` as requirements, added to `bin/list-shell-scripts` coverage and documented in `bin/AGENTS.md` next to `version-audit`.
1. Scrut coverage that drives the canary against a stubbed `gh` in `tests/fixtures/`, and prints a report for a drift fixture and nothing for a clean one.
1. `.github/workflows/copilot-review-canary.yml`, with remote `uses:` pinned to full SHAs with version comments, `permissions: {contents: read, issues: write, pull-requests: read}`, a concurrency group and a timeout.
1. Mention the canary in the root `CLAUDE.md` tooling paragraph, next to `bin/version-audit`, as a weekly audit that is not a merge gate.

## Verification

Run from the repository root:

```bash
make build
make test-all
```

**Census calibration against live data.** Recreate the 450-review sample locally, outside the repository, and run the new parser over it. The acceptance bar:

- #4401, #4430 and #452 report `unaccounted` entries before Phase 3 and none after it.
- Every other review's `hasFormatDrift` is unchanged from the #516 parser, or each change is explained in the PR body by review URL and kind.
- `unrecognizedStructure` entries that set drift appear only on reviews that really have a new container.

Record the counts in the PR body. Never include body text from private repositories.

**Skeleton allowlist seed.** Seed the allowlist from the 2026-09-23 inventory, which found these skeletons:

- `<!-- ccr-overview-v2 -->`, `## Copilot review overview`, the three verdict headings, `### Suppressed comments (N)`, `### Files not reviewed (N)`, `### New files (N)`, `### Added files: N`
- `<summary>` titles: `Open`, `Resolved since last review`, `Previously missed`, `What changed in this PR`, `Files not reviewed`, `Pull request overview`, `File summaries`, `Review details`, `Comments suppressed due to low confidence`, `Suppressed comments`, and the badge-plus-title form nested inside `Previously missed`
- labels: `**Review effort:**`, `**Findings:**`, `**Changes:**`, `**Review findings:**`, `**Files reviewed:**`, `**Comments generated:**`, `**Review effort level:**`

Headings that Copilot quoted from the files under review (for example `# Branch Review Evidence`) appear inside prose or fenced blocks, and are excluded by the rule that only lines outside fences count, not by the allowlist.

**Live probes.** After Phase 5, run `audit` against #530, #521 and #520 in this repository and confirm that `uncovered` and `reviewsNeedingRead` are empty, or explained. These calls read and write nothing.

**Mutation checks.** Phase 2 lists the census mutations. Also confirm that removing the drift-setting kinds from the fingerprint rule, or dropping `( each)` support from `table_findings`, fails at least one case.

## Open questions

1. **Canary scope.** `GITHUB_TOKEN` reads only this repository. Covering `cboone/*` and `swing-left/*` in the scheduled workflow needs a fine-grained PAT stored as a secret, with read access to pull requests in those repositories. The alternative is to run the canary locally for cross-repository coverage. Recommendation: ship the workflow for this repository only, and run the cross-repository sweep locally until the need for a PAT is clear.
1. **Unknown-structure strictness.** Layer 2 sets drift only for new markers, `<summary>` titles and non-verdict `###` headings. If calibration shows those are noisier than the sample suggests, fall back to reporting them without setting drift, and rely on the census alone for drift.
1. **Drift permanence in `monitor-pr`.** Review bodies are immutable, so a review that sets drift sets it for good, and `monitor-pr` escalates once per review id after a clearing outcome. That is the intended loud path, but a wider detector means more escalations until a parser catches up. Calibration is the guard. A per-review acknowledgment recorded in the summary comment is possible later if the escalations prove disruptive. It is out of scope here.
