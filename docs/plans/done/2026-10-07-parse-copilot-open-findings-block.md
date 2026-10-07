# Parse the Copilot open-findings block

Addresses [issue #560](https://github.com/cboone/agent-harness-plugins/issues/560).

## Context

Copilot now posts `ccr-overview-v2` review bodies that have no `**Findings:**` line. They state the open count in a `<details open>` block summarized as `<strong>N open findings</strong>`, which lists one `#discussion_r…` link per open thread. A closed `<details>` block, summarized as `<strong>N resolved since last review</strong>`, lists the earlier threads that were resolved. `resolve-copilot-threads parse-reviews` treats a missing `**Findings:**` line as a renamed header. It reports `stated_finding_count` as `"unparseable"` and sets `hasFormatDrift: true` with an empty `unaccounted` list. As a result, `monitor-pr` escalates on a review whose findings were all handled. Running the current script on review 5444232294 from #559 reproduces this: the output has `hasFormatDrift: true` and `unaccounted: []`. It also has `needsRead: true`, which is correct because the lead is prose.

**Classification:** bug fix (`fix`).

## Approach

All parser changes go in `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`. Afterward, the same file is copied byte for byte to `plugins/monitor-pr/scripts/resolve-copilot-threads`.

1. **Leading-count section titles and counts.** Extend `section_title` and `section_count` (around line 399) so that a summary whose count comes first, such as `3 open findings`, works like one whose count comes last, such as `Open (3)`. The title drops the leading number. The count is read from either position. The census in `signals` and `unaccounted` then reconciles `3 open findings` and `3 resolved since last review` against the thread links in their regions, the same way it already reconciles `Open (3)`. This adds no new rule.
2. **`section_summary` takes a pattern.** Generalize `section_summary($name)` so the caller passes the regex, including a named `count` group, while keeping the existing depth-one rule. Existing callers become `"Open \\((?<count>[0-9]+)\\)"` and `"Resolved since last review \\((?<count>[0-9]+)\\)"`. New callers are `"(?<count>[0-9]+) open findings?"` and `"(?<count>[0-9]+) resolved since last review"`.
3. **Stated count.** When the preamble has no `**Findings:**` line, the open-findings summary count becomes the stated count. A v2 body that has neither form still reports `"unparseable"`, which is drift.
4. **Open thread count.** For the open-findings layout, `open_thread_count` counts the `#discussion_r` thread links inside that depth-one block. That keeps the `stated > open` shortfall check a real comparison: the summary count against the links actually listed. `Open (N)` keeps its current behavior. `lists_open_threads` follows.
5. **Resolved exemption.** `lists_resolved_threads` also accepts `N resolved since last review`.
6. **Comments.** Update the comment blocks that claim every v2 body carries a `**Findings:**` line (near the `stated_finding_count` definition and the `$stated_findings` binding), the `section_summary`, `lists_resolved_threads` and census comments, and the header comment, so they describe both layouts.
7. **Fixture.** Add `tests/data/copilot-reviews/format-d-open-findings-block.json`, holding review 5444232294 (id, user login, state, `submitted_at`, `html_url`, `commit_id`, body), in the same shape as the existing fixtures.
8. **Scrut cases** in `tests/scrut/resolve-copilot-threads.md`, placed beside the `Open (N)` and renamed-header cases. Note that `fetch-reviews` itself cannot run in tests, so `parse-reviews` is the seam.
   - The new fixture: `hasFormatDrift: false`, `unaccounted: []`, and only the lead finding.
   - The fixture with one open-thread bullet removed (summary 3, links 2): drift.
   - The fixture with the open-findings summary renamed: drift, because neither form is present.
   - A resolved-only variant (open block removed, `0` count or none, known lead) with the `N resolved since last review` block: `needsRead: false` and no drift, matching the existing resolved-only case.
9. **Docs.** Update `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md` (shortfall bullet, census bullet, `headline` and `**Findings:** None` notes) to describe the open-findings summary as the alternative count source. Check the plugin README for the same wording.
10. **Versions.** Patch bumps: `monitor-pr` from 1.7.0 to 1.7.1 and `resolve-copilot-pr-feedback` from 1.8.0 to 1.8.1, plus any `.codex-plugin` mirrors. Then run `make build` and commit the regenerated `dist/` and `.agents/` output.
11. **Plan file.** Commit this plan with the work.

## Verification

- `diff` the two script copies to confirm they are identical.
- Run `parse-reviews` on the new fixture and confirm `hasFormatDrift: false`.
- `make test-all` (lint, validate, scrut), with every existing case still passing.
- Run the `check-versions` skill.
