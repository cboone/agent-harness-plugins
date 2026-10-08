# Read Copilot review bodies as text

Supersedes [issue #567](https://github.com/cboone/agent-harness-plugins/issues/567) and [issue #568](https://github.com/cboone/agent-harness-plugins/issues/568).

## Context

`resolve-copilot-threads fetch-reviews` parses Copilot review bodies into structured findings and runs a census that reports `hasFormatDrift` whenever a layout element goes unrecognized. The skill treats drift as a workflow failure, so the resolver reports `Partial` and `monitor-pr` escalates and stops the watch.

Copilot changes its review-body layout faster than the parser can follow. On 2026-10-07 alone it shipped an open-findings `<details>` block, a bare `**0 open findings**` line, a `🧠 **Review effort:**` label, `Previously missed` entries as nested `<details>` with picture badges, two-column file tables whose cells carry `(N votes)` tags, and three-column tables with `**Moderate (1):**` labels joined by `<br>`.

Evidence from the recent run history:

- About 60 `## Copilot Feedback Summary` comments were posted across `cboone/agent-harness-plugins`, `cboone/sl-health-monitor`, `swing-left/frontend` and `swing-left/votefwd` since 2026-10-07. Nearly every `Partial` was caused only by format drift, and the failure rows say so: "Nothing was missed", "findings were settled by hand above". In every case the agent read the body and handled it correctly. The parser's alarm was the only thing that failed.
- Replaying all 87 recent Copilot reviews through the current parser, after #569, still yields drift on three of them, each a different new shape: [review 5449759699](https://github.com/cboone/agent-harness-plugins/pull/569#pullrequestreview-5449759699), [review 5449428489](https://github.com/cboone/sl-health-monitor/pull/104#pullrequestreview-5449428489) and [review 5444901015](https://github.com/cboone/sl-health-monitor/pull/93#pullrequestreview-5444901015).
- `needsRead` is true for every current-layout review, so the census already concludes "read the whole body" every time.
- `do_parse_reviews` is about 1,200 lines of jq in a 2,009-line script copied into `monitor-pr`, with a 1,672-line scrut suite and a 633-line canary. The scripts have had 50 commits since 2026-09-01.

The text of a Copilot review always says what Copilot found. The design error is treating layout recognition as a correctness gate.

## Goal

The agent reads every relevant Copilot review body as text and settles each concern it states. The script returns only facts GitHub's API exposes structurally, which do not depend on how Copilot lays out a body. "Format drift" stops existing as a failure class, so a Copilot layout change can no longer turn a finished run into `Partial` or stop a `monitor-pr` watch.

## Decisions

- Delete the review-body parser and census outright. Do not keep them as a non-gating hint.
- Return the raw review body. No preprocessing, such as stripping `<picture>` tags or the survey footer, because that couples the script to the layout again.
- Delete `bin/copilot-review-canary` and everything that exists only for it. Keep the review case corpus (`bin/validate-corpus`, `bin/materialize-case`, `docs/review-case-corpus.md`, `make validate-corpus`): it is the reviewer-comparison benchmark that issues #506, #507 and #508 build on, not part of Copilot parsing.
- Major version bumps: `resolve-copilot-pr-feedback` 1.8.2 to 2.0.0 and `monitor-pr` 1.7.2 to 2.0.0, because the `fetch-reviews` and `audit` output contracts and the `monitor-pr` probe change shape.
- Close #567 and #568 as superseded, with a comment linking this PR.
- Select reviews by id, never by time. Every summary records the reviews it read on a `Reviews read:` line, and a run reads every Copilot review that no `Completed` or `No unresolved Copilot feedback` summary lists, plus the newest review of the current head. A first draft selected by the newest summary's timestamp; review showed that misses reviews arriving mid-run, reviews after a `Partial` or `Failed` run, and the current-head review itself, so the timestamp filter is not part of the design.

## Approach

### 1. Script: `resolve-copilot-threads`

Edit `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`, then copy it byte for byte to `plugins/monitor-pr/scripts/resolve-copilot-threads`.

- **`fetch-reviews` / `parse-reviews`.** Replace `do_parse_reviews` with a small filter. Per Copilot-authored review with a non-empty string body, emit:
  - `id`, `url`, `submittedAt`, `commitId`
  - `body`: the raw body, verbatim
  - `threadLinks`: the `discussion_r<N>` comment ids the body links to, extracted by matching GitHub's comment URL fragment anywhere in the text. This is a matching hint only. It is derived from GitHub's URL scheme rather than Copilot's layout, and an empty or wrong list breaks nothing, because the agent reads the body regardless.
- **Remove** `findings`, `unaccounted`, `hasFormatDrift`, `needsRead`, `reviewKind`, `verdict`, `headline`, `suppressed`, `hasSuppressedMarker` and `reviewBody`. Notices are recognized by reading, below.
- **`--skip <id,id,...>`** on `fetch-reviews` and `parse-reviews` leaves out review ids already read, and **`--head <sha>`** always keeps the newest review of that commit, skipped or not. Both act on structured API fields, `id` and `commit_id`.
- Match Copilot logins case-insensitively in every command, return a review with a null or empty body with an empty body rather than dropping it, flatten paginated pages in `fetch-reviews`, and have `audit` list a Copilot review whose body is not a string as uncovered.
- **`fetch`.** Add each comment's `databaseId` (or URL) to the thread output, so `threadLinks` can be matched to a thread without a second query.
- **`audit` / `parse-audit`.** Drop `legacyNeedsRead`, which depends on reading headings. Keep `surfaces` and `uncovered`. Confirm no remaining audit logic inspects body layout.
- **Keep unchanged:** author detection, the non-string-body skip warning, pagination, `resolve`, `reply` and `reply-and-resolve`.
- Update `usage` and the header comments to match.

### 2. Skill: `resolve-copilot-pr-feedback`

Rewrite `skills/resolve-copilot-pr-feedback/SKILL.md` step 1 around reading, and remove every reference to parser fields.

- **Step 1b: which reviews to read.** Collect the `Reviews read:` ids from prior summaries the authenticated account posted with status `Completed` or `No unresolved Copilot feedback`, pass them as `--skip`, and pass the current head as `--head`. Carry forward every row a prior summary left `Pending` or `Failed`. A caller's `REVIEW_ID` must be among the reviews read.
- **Step 1d becomes the core step.** For each review read:
  1. Decide whether it is a review or a notice. A notice says Copilot did not review: it hit an error, or every changed file was excluded. Read the whole body before deciding. A notice in place of the current-head review is a workflow-level failure that quotes it, and its failure row names it as a Copilot notice with the review `id`, so `monitor-pr` can reclassify it. A body that is plainly neither a review nor a notice is also a workflow-level failure, quoted the same way.
  1. List every concern it states, anywhere in the body: lead paragraph, open-findings lists, previously missed entries, file-table cells, suppressed sections, or any shape Copilot adopts later. Skip text that states no finding, such as file summaries reading "no final comments".
  1. Settle each one as **Matched** (restates a thread from `fetch`, using `threadLinks` as a hint, or a prior summary row), **New** (handle as a review-body finding with the most specific location the text supports; never invent a line), **Advisory**, or **No concern**.
- **Keep** step 1c's identity rules (`path:line`, or path or location plus a verbatim excerpt). The agent now writes the `Finding` cell from the concern it extracted, so the identities stay readable on the next run.
- **Replace** the format-drift rule, the `hasFormatDrift` / `unaccounted` / `needsRead` / `lead` documentation and the drift failure rows. Nothing in a review's layout can fail the workflow.
- **Redefine `No unresolved Copilot feedback`:** `fetch` returned `[]`, a review (not a notice) exists against the current head, every review read states no concern that is not already `Previously handled`, and `audit` reported nothing `uncovered`.
- **Generalize** the `Lead findings:` summary line into a `Review concerns:` line with the same matched / new / advisory / no-concern counts across every review read.
- **Update** the Error Handling list, the Success Criteria and the common failure modes. Add one: skimming a long review body instead of listing every concern.
- Update `plugins/resolve-copilot-pr-feedback/README.md` past its catalog paragraph. That paragraph stays verbatim.

### 3. Skill: `monitor-pr`

Edit `plugins/monitor-pr/skills/monitor-pr/SKILL.md`, `references/checkpoint.md` and `README.md`.

- **Probe.** Keep the `fetch` thread count and the `audit` projection, minus `legacyNeedsRead`. On every tick, change the `fetch-reviews` projection to `{id, url, commitId}` for the selected review id. The per-tick probe carries no body text, so it stays small.
- **Classification reads the whole body.** The first time a current-head review `id` appears, the monitor fetches that review's complete raw body (`fetch-reviews` filtered to that `id`, projecting `.body` alone, never truncated) and reads all of it before recording a classification. Truncating would discard exactly the text that tells a notice apart, wherever Copilot happens to place it. The body is immutable, so one full read per review `id` is enough. Record one of three readings in the watch state:
  - **review**: Copilot reviewed the head. Dispatch per below.
  - **notice**: the body says Copilot did not review the head, for example an error, or every changed file being excluded. The existing notice retry and escalation logic applies unchanged, apart from where the classification comes from.
  - **unclear**: the body neither plainly reports a review nor plainly says no review happened. Never treat it as a review, never let it satisfy the Copilot axis, and never count it toward `--confirm-clean`. Escalate per step 9 with the review link and a short quote of what made it ambiguous, so a person decides.
- **Second check from the resolver.** The resolver reads the same body in full during its step 1d. If it concludes that a review the monitor classified as **review** is actually a notice, it says so in its local final output and in a failure row of its summary. The monitor then reclassifies that `id` as a notice and takes the notice path. A misreading in either skill therefore cannot turn a notice into a clean axis.
- **Dispatch.** Every current-head Copilot review that is not a notice goes to step 7b once per `id`. That matches current behavior, because `needsRead` is already true for every current review. Remove the findings-count and drift clauses.
- **Copilot axis clean** when step 7b processed the current-head review with `Completed` or `No unresolved Copilot feedback`, `fetch` reports no open threads, and every audit item is recorded at the current head. Remove "no format drift" everywhere, including step 7d and the escalation rules.
- **Dependabot path.** With no resolver to dispatch to, the monitor reads the current-head review's full body itself and escalates if it states any concern, or if threads or audit items exist.
- Update the checkpoint fields: the review kind becomes the recorded `review`, `notice` or `unclear` reading per review `id`, so a resumed watch neither reclassifies nor redispatches, and the drift field goes.

### 4. Canary removal

Delete:

- `bin/copilot-review-canary`
- `bin/data/copilot-review-structure.json`
- `tests/scrut/copilot-review-canary.md`
- `tests/data/copilot-canary/`

Remove the wiring in `Makefile` (lines 44 and 45), `.github/workflows/ci.yml` (lines 125 and 126), the canary sentence in the root `AGENTS.md`, and its bullet in `bin/AGENTS.md`. Check the `copilot-gh-stub` fixture and `tests/data/copilot-gh/` for canary-only data.

### 5. Other coupled surfaces

- `.github/instructions/shell.instructions.md` lines 21 to 23: remove the census and #567 rules.
- `docs/plugin-development.md` line 53 and `tests/scrut/repo-tooling.md` around line 197: describe `monitor-pr`'s use of the script without "format drift".
- Before finishing, grep for `hasFormatDrift`, `needsRead`, `unaccounted`, `legacyNeedsRead`, `reviewKind`, `ccr-overview`, `canary` and `drift` outside `docs/plans/done/`, `docs/reviews/`, `dist/` and `.agents/`. Every remaining hit should be intended, such as `monitor-pr`'s unrelated generated-tree drift.

### 6. Tests

Rewrite `tests/scrut/resolve-copilot-threads.md`:

- **Remove** every layout-parsing, census, drift, lead and needs-read case.
- **Keep, adjusted to the new shape:** non-Copilot filtering, unusable-author skip, empty list, malformed input, non-string-body skip, the jq-version check if the new filter still needs it, help text, the surface audit without `legacyNeedsRead`, the `monitor-pr` copy-identity case and the step 3 selection-filter case.
- **Add verbatim passthrough:** a fixture set of real bodies covering the layouts named in Context, plus the oldest suppressed-comments layout. For each, `body` equals the input byte for byte. This pins the property that matters: no layout can change the output.
- **Add** `threadLinks` extraction (present, absent, duplicated), `--skip` and `--head` selection, the login set, `fetch` output with comment ids, and the `fetch-reviews` failure path.
- Prune `tests/data/copilot-reviews/` and `tests/data/copilot-gh/api/*_reviews.json` to what the remaining cases use.

### 7. Versions, build and issues

- Bump both plugins to 2.0.0 in `.claude-plugin/plugin.json`. Neither has a `.codex-plugin` manifest.
- Run `make build` and commit the regenerated `dist/` and `.agents/` mirrors.
- Run the `check-versions` skill.
- After the PR opens, comment on and close #567 and #568 as superseded.

## Verification

1. `make test-all` passes. Observe the final result.
1. Replay the 87 recent reviews collected during investigation through `parse-reviews` and confirm each `body` matches the API body exactly and no output field depends on layout.
1. Run the updated resolver skill against one recent PR whose earlier summary was `Partial` only for drift, such as cboone/sl-health-monitor#104. Read-only: run steps 1 and 2 and stop before any reply, push or summary post. Confirm every concern from review 5449428489's file table is listed and settled, and that no workflow failure is recorded.
1. Desk-check `monitor-pr` dispatch against these cases. Each should reach the expected step 4 branch with no reference to drift:
   - a notice whose explanation is the whole body
   - a notice whose explanation appears only after more than 600 characters of introductory text, which must still classify as a notice
   - an ambiguous body, which must escalate and never satisfy the Copilot axis
   - a body the monitor reads as a review but the resolver reports as a notice, which must move to the notice path
   - a clean approval
   - a review with findings
1. Confirm the step 3 probe instructions never truncate the body used for classification. Add a scrut case pinning that the documented classification command returns the complete body of a long review.

## Out of scope

- The review case corpus and its tooling, which stay.
- `docs/plans/todo/2026-09-21-stop-drift-on-no-findings-review.md`, an outdated todo plan for the already closed #491. Flag it for a separate cleanup.
- Generalizing to other reviewers (#464).
