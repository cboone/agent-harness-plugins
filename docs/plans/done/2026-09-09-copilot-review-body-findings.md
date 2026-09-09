# Copilot review-body findings

Closes [#324](https://github.com/cboone/agent-harness-plugins/issues/324).

## Context

`resolve-copilot-pr-feedback` fetches `pullRequest.reviewThreads` and nothing else. When Copilot files a finding in a **review body** rather than an inline thread, the skill's `fetch` returns `[]`, the skill posts `Status: No unresolved Copilot feedback`, and real, actionable feedback goes unread. The failure is silent and reads as success, which is the worst outcome for a skill whose entire job is not missing review feedback.

Copilot does this whenever it declines to open a thread, most often on a line the latest push did not touch. It files the finding under a "suppressed comments" section instead and says so directly in the trailer (`Comments generated: 0 new`).

This is not an edge case. Scanning the last 40 PRs in `cboone/fosforo` and `cboone/agent-harness-plugins` turned up **46 Copilot reviews carrying a suppressed-comments section**. Any PR that gets more than one review can hit it, which is most of them.

Intended outcome: the skill sees these findings, treats them like any other Copilot feedback, reports every one in its summary comment, and never again claims "no feedback" without having looked.

## Design decisions

| Question                             | Decision                                                                                                                                                          |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Act on findings, or only report them | **Full treatment.** Categorize, fix, add Copilot instructions, track deferrals, report every one.                                                                 |
| Where parsing lives                  | **Script slices raw + parses structured, with a drift detector.** Marker present but zero findings means Copilot changed format; the skill reads the raw excerpt. |
| Idempotency across runs              | **Prior summary scan + verification against current code.** No new storage; a deleted or edited comment degrades to re-verification, not to a wrong answer.       |
| Tests                                | **Scrut, via a stdin-driven `parse-reviews` subcommand.** No `gh` stub needed.                                                                                    |

## What Copilot actually emits

Three layouts observed in live data. All three share the same interior shape, which is what the parser keys on.

Format A (oldest) and B (mid) differ only in the summary text:

```markdown
<details>
<summary>Comments suppressed due to low confidence (1)</summary>
<!-- or: <summary>Suppressed comments (2)</summary> -->

**plugins/notify/opencode/index.ts:252**

- `truncate()` slices to `limit` and then appends an ellipsis...

</details>
```

Format C (current) moves the section inside the `Review details` block and adds a category subheading:

```markdown
<details>
<summary>Review details</summary>

### Suppressed comments (2)

**Previously missed (1)** — in code that hasn't changed since the last review.

**src/gpu/metal/reload.zig:391**

- This expectation currently asserts...

- **Files reviewed:** 9/9 changed files
- **Comments generated:** 1
- **Review effort level:** Lite

</details>
```

Stable invariants across all three:

- The section opens on a line matching `suppressed comments` or `comments suppressed`, case-insensitive.
- It closes at `</details>`, a new `<details>`, or the `- **Files reviewed:` trailer.
- Each finding is a bold-only `**path:line**` line, followed by prose and an optional fenced context block.

## Changes

### 1. `scripts/resolve-copilot-threads`: two new subcommands

`plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`

**`fetch-reviews <owner> <repo> <pr_number>`** — `gh api --paginate repos/OWNER/REPO/pulls/N/reviews` piped through the normalizer. Verified: `gh api --paginate` merges REST array pages into one array, so no `--slurp` and no page flattening.

**`parse-reviews`** — reads that same review JSON on stdin and emits the normalized output. This is the seam that makes the parser testable without stubbing `gh`, mirroring how `plugins/create-worktree-from-issue/scripts/compose-issue-prompt` is tested today.

Output shape, one object per Copilot review that has a body:

```json
[
  {
    "id": 5035762218,
    "url": "https://github.com/cboone/fosforo/pull/54#pullrequestreview-5035762218",
    "submittedAt": "2026-08-21T18:02:11Z",
    "headline": "### 🔵 Needs a closer look\n\nThe Phase 2 plan section is internally inconsistent...",
    "hasSuppressedMarker": true,
    "suppressed": "**docs/plans/todo/...md:243**\n* This section now states...",
    "findings": [{ "location": "docs/plans/todo/...md:243", "path": "docs/plans/todo/...md", "line": 243, "body": "* This section now states..." }]
  }
]
```

`suppressed` is the verbatim slice; `findings` is the structured parse of it. Shipping both is what makes the drift detector possible.

**The jq normalizer goes inline in the bash script**, single-quoted, alongside the existing GraphQL queries. It cannot live in a sibling `.jq` file: CI runs `shellcheck -S warning bin/* plugins/*/scripts/*`, and shellcheck errors out on a `.jq` file caught by that glob (verified: SC2148 plus a parse failure). It needs the same `# shellcheck disable=SC2016` + rationale comment the GraphQL blocks carry, since `$line`/`$parts` are jq bindings, not shell variables.

**Quoting hazard to avoid:** the natural filter for Copilot's boilerplate line is `test("^\\*Once you've addressed")`, and that apostrophe terminates the single-quoted bash string. Match on `^\\*Once you` instead.

Working filter, already validated (see Verification):

```jq
def trim: sub("^[[:space:]]+"; "") | sub("[[:space:]]+$"; "");

def headline:
  split("\n")
  | (map(test("^<details>")) | index(true)) as $stop
  | (if $stop then .[0:$stop] else . end)
  | map(select(test("^\\*Once you") | not))
  | join("\n") | trim;

def suppressed_slice:
  split("\n")
  | reduce .[] as $line ({inside: false, out: []};
      if (.inside | not) and ($line | ascii_downcase | test("suppressed comments|comments suppressed"))
      then .inside = true
      elif .inside and ($line | test("^</?details>|^- \\*\\*Files reviewed:"))
      then .inside = false
      elif .inside then .out += [$line]
      else . end)
  | .out | join("\n") | trim;

def findings:
  split("\n")
  | reduce .[] as $line ({current: null, out: []};
      if $line | test("^\\*\\*[^*]+:[0-9]+\\*\\*$")
      then (if .current then .out += [.current] else . end)
        | .current = {heading: ($line | ltrimstr("**") | rtrimstr("**")), lines: []}
      elif .current != null then .current.lines += [$line]
      else . end)
  | (if .current then .out + [.current] else .out end)
  | map((.heading | split(":")) as $parts
      | {location: .heading, path: ($parts[0:-1] | join(":")), line: ($parts[-1] | tonumber), body: (.lines | join("\n") | trim)});
```

The `$` anchor on the `**path:line**` regex is load-bearing: it is what keeps Format C's `**Previously missed (1)** — in code...` subheading from being parsed as a finding.

**Dependency checks must be split.** `parse-reviews` needs `jq` only. If it inherits today's `check_dependencies`, it calls `gh auth status` and the scrut suite fails in CI, where there is no GitHub auth. Split into `require_jq` and `require_gh` (auth check included), then wire the first `case` in `main()`:

- `fetch`, `resolve`, `reply`, `reply-and-resolve`, `fetch-reviews` → both
- `parse-reviews` → `require_jq` only

**The Copilot login list must gain a `[bot]` variant.** REST and GraphQL disagree on the login, verified against `cboone/fosforo#54`:

```console
$ gh api repos/cboone/fosforo/pulls/54/reviews --jq '[.[].user.login] | unique'
["cboone", "copilot-pull-request-reviewer[bot]"]

$ gh api graphql -f query='{ ... reviewThreads ... author { login } }'
["copilot-pull-request-reviewer"]
```

`COPILOT_DIRECT_LOGINS` today holds only the unsuffixed form, so reusing it as-is would filter out **every** Copilot review and reproduce the exact bug this plan fixes. Add `copilot-pull-request-reviewer[bot]` to the list.

Also extend `usage()` with the two new commands and an example.

While in `main()`, drop the unreachable duplicate `*)` arm in the second `case` (lines 383–385) — the first `case` already dies on unknown commands.

### 2. `skills/resolve-copilot-pr-feedback/SKILL.md`

`plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`

**Step 1** (currently `### 1. Fetch ALL Unresolved Copilot Threads`, L134) becomes `### 1. Fetch ALL Unresolved Copilot Feedback`, with two fetches: the existing `fetch` and the new `fetch-reviews`. Document the new output shape and add the drift rule:

> If `hasSuppressedMarker` is `true` but `findings` is empty, Copilot changed its review-body format. Read the `suppressed` field directly and extract the findings yourself. Never treat that combination as "no findings."

Extend the existing `[]` caution (L163) to cover the new failure: `[]` from `fetch` is a statement about threads only, never about feedback.

**Step 2** (L165): keep the five categories; they apply unchanged. Add a note that review-body findings carry no `[nitpick]` prefix, so Nitpick is decided from the prose.

**Step 4** (L183): new subsection `#### Review-Body Findings (no thread)`, placed after `#### Deferred`. It states plainly that these have no thread ID, so `reply`, `resolve`, and `reply-and-resolve` do not apply and must not be attempted, and that the step 7 summary is the only reporting channel available for them. Per category: Valid → fix and record; Incorrect → add the Copilot instruction and record; Deferred → track and record; Nitpick/Outdated → record only.

**Step 6** (L277): the status rules are where the bug actually lands. Two edits.

- `No unresolved Copilot feedback` now requires **both** that `fetch` returned `[]` **and** that `fetch-reviews` surfaced no unhandled findings.
- Add: re-running `fetch-reviews` is **not** a completion check. Copilot's old review body is immutable, so a fixed finding still appears there forever. Only the thread `fetch` is expected to reach `[]`.

**Step 7** (L298): add a `Source` column (`Thread` / `Review body`) to the summary table, so a thread-less row is legible rather than implied:

```markdown
| Source      | File                | Category  | Outcome           | Action                       |
| ----------- | ------------------- | --------- | ----------------- | ---------------------------- |
| Thread      | `src/foo.ts:42`     | Valid     | Resolved          | Fixed null check             |
| Review body | `docs/plan.md:243`  | Valid     | Fixed             | Corrected phase status       |
| Review body | `src/ui.tsx:20`     | Deferred  | Tracked           | Follow-up issue filed        |
| Review body | `lib/util.js:8`     | Valid     | Previously handled | Recorded in an earlier run   |
```

`Resolved` stays reserved for rows with a real resolved thread. Review-body rows use `Fixed`, `Tracked`, `Noted`, `Previously handled`, or `Failed`. Add `review-body findings` and `previously handled` to the `Counts:` metric set (L323), keeping the omit-if-zero rule.

Update the no-op form's trigger and the **no-op summary idempotency** rule (L371) so both are conditioned on threads *and* review-body findings being empty.

**Idempotency mechanism** (new prose in step 1 or 4). Before acting on a review-body finding:

```bash
gh api repos/OWNER/REPO/issues/PR_NUMBER/comments --jq '.[] | select(.body | startswith("## Copilot Feedback Summary")) | .body'
```

Reading PR comments is already sanctioned by the existing no-op idempotency rule; only creating them is forbidden. Then:

1. If a prior summary records this `path:line` as a `Review body` row, verify against the current code before deciding. If the finding no longer applies, record `Previously handled` and change nothing. If it still applies (the earlier run deferred it, or a fix regressed), process it normally.
2. If the path matches but the line does not, treat it as a candidate and let the code check decide — line numbers drift as the file changes.
3. If nothing matches, process it normally.

The verification step is what keeps this honest: a human who edits or deletes the summary comment costs a re-verification, not a wrong answer.

**Success Criteria** (L412): add review-body findings to the completion conditions, and amend item 6 so "re-fetch confirms `[]`" is scoped to threads.

**Required Output table** (L427): add the same `Source` column; `Thread ID` is `—` for review-body rows.

### 3. READMEs

- `plugins/resolve-copilot-pr-feedback/README.md`: extend the "What It Does" paragraph (L14) to cover review-body findings, and add `Bash(gh api repos/*/issues/*/comments*)` to the Recommended Permissions allowlist (L29).
- Root `README.md` L76: only if the marketplace `description` changes. It does not need to — "Process and resolve GitHub Copilot automated PR review comments" already covers this — so leave both alone.

### 4. Tests

New `tests/scrut/resolve-copilot-threads.md`, driving `parse-reviews` over stdin. Fixtures as JSON files under `tests/data/copilot-reviews/`, built from the real bodies already captured during planning:

| Fixture              | Asserts                                                                       |
| -------------------- | ----------------------------------------------------------------------------- |
| `format-a.json`      | Oldest layout, 1 finding                                                      |
| `format-b.json`      | Mid layout, 2 findings                                                        |
| `format-c.json`      | Current layout, 2 findings, and the `Previously missed` subheading is not one |
| `no-suppressed.json` | Body with several `<details>` blocks but no section: marker false             |
| `drift.json`         | Marker true with zero structured findings, so drift surfaces                  |
| `non-copilot.json`   | Human-authored review filtered out                                            |

Plus: path and line split out of the heading, prose and fenced context preserved, headline extraction, empty array in gives `[]` out, and the `parse-reviews` arity error.

`fetch-reviews` itself is not covered: it needs an authenticated `gh`, which CI does not have. That is exactly why `parse-reviews` exists as a separate stdin-driven entry point.

Wiring, following the existing pattern exactly:

The JSON fixtures live under `tests/data/`, **not** `tests/fixtures/`. CI runs `shellcheck -S warning ... tests/fixtures/*`, and shellcheck exits non-zero on a directory caught by that glob (`openBinaryFile: inappropriate type (is a directory)`). `tests/fixtures/` holds executable stubs that are meant to be shellchecked; test data belongs beside it, not inside it.

- `Makefile`: add `RESOLVE_COPILOT_THREADS_BIN` and `COPILOT_REVIEW_DATA_DIR` to **both** `test-scrut` and `test-scrut-update`.
- `.github/workflows/ci.yml`: add the same two to the `scrut-env:` block (L52–59), using `./relative` paths.

### 5. Version and mirrors

New capability, so **minor**: `1.4.4` → `1.5.0`, in both `plugins/resolve-copilot-pr-feedback/.claude-plugin/plugin.json` and the `.claude-plugin/marketplace.json` entry. Then recompute the catalog tag and regenerate both mirrors.

## Verification

The parser design is already validated. Against 14 real Copilot review bodies pulled from live GitHub, it extracted **15 findings across 11 reviews with zero false positives**, including correct empty results for a 21KB body with `<details>` blocks and no suppressed section. Re-confirm after implementation:

```bash
# The issue's own repro. Expect 1 finding at docs/plans/todo/...:243
bash plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads fetch-reviews cboone fosforo 54

# Multi-finding, current format. Expect 2 findings in .github/workflows/ci.yml
bash plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads fetch-reviews cboone fosforo 81

# Oldest format. Expect 1 finding in plugins/notify/opencode/index.ts
bash plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads fetch-reviews cboone agent-harness-plugins 290

# No suppressed section anywhere. Expect every hasSuppressedMarker false
bash plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads fetch-reviews cboone agent-harness-plugins 325
```

Then the full local gate:

```bash
make test-scrut
shellcheck -S warning bin/* plugins/*/scripts/* tests/fixtures/*
shfmt -d bin/* plugins/*/scripts/* tests/fixtures/*
yarn lint
bin/validate-json
bin/build-codex-marketplace
bin/build-opencode-mirror
bin/compute-catalog-state   # paste result into both marketplace.json metadata.version fields
bin/validate-plugins
git diff --exit-code dist/  # must be clean after committing regenerated mirrors
```

End-to-end, the real check is running the updated skill against a PR that has a suppressed finding and confirming it no longer reports `No unresolved Copilot feedback`.

## Commits

1. `feat: fetch Copilot findings from review bodies (#324)` — script subcommands, dependency split, usage.
1. `test: cover Copilot review-body parsing (#324)` — scrut suite, fixtures, Makefile and ci.yml wiring.
1. `feat: handle review-body findings in the resolver skill (#324)` — SKILL.md and plugin README.
1. `chore: bump resolver to 1.5.0 and regenerate mirrors (#324)` — versions, catalog tag, `dist/`.
