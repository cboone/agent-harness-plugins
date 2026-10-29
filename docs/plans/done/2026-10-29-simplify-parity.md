# Simplify cleanup parity

Build through a ready PR under the 2026-10-29 12:15 PM ET Inbox go-ahead, relayed by CONDUCTOR. TOOLING owns merging. Base: main, initial HEAD `1a42b4534ac873b070130b6be16ced1cbc8f687d`.

## Prior art

Survey refreshed 2026-10-29 after the Ramp goals resume go-ahead, relayed by TOOLING. Sources were read as data, without installing or copying them.

- **Claude built-in simplify:** the supplied 2.1.312 extract provides four cleanup angles, separate review/edit stages, concrete costs, deduplication, skipped-fix reporting and inline fallback. Use those ideas in original wording; the extract does not define altitude.
- **[Toolkit code-simplifier](https://github.com/anthropics/claude-plugins-official/blob/f8c5e7a1dcb71b10cb74586224b5401f3de5db28/plugins/pr-review-toolkit/agents/code-simplifier.md):** the existing aspect's source. Retain its behavior, clarity and scope rules and attribution. Its proactive single editor does not replace the required gated workflow.
- **[gtapps/simplify](https://github.com/gtapps/simplify/blob/b1e31bd410fabc70bd05aa49df29bab3baf732ad/SKILL.md):** three read-only reviewers followed by sequential application support the stage separation. Its partial-result continuation and output repair conflict with this skill's completion checks; do not adopt them or its three-reviewer shortcut.
- **[Sentry code-simplifier](https://github.com/getsentry/skills/blob/d12f250460ffd961f549dbebf7eeb0cf4afd4c2e/skills/code-simplifier/SKILL.md):** a toolkit-derived skill with clarity and behavior-preservation examples. It supplies no independent four-angle orchestration or snapshot gate, so replacing the existing aspect adds no required capability.

Extend the existing aspect; the survey reveals no design gap requiring a scope change. CodeRabbit, review-anti-patterns and trim-comments remain excluded as design sources.

## Design

Extend only review-pr-with-codex, its generated mirror and relevant tests. Retain toolkit attribution. Add four internal read-only cleanup aspects: reuse, simplification, efficiency and altitude. Define altitude as matching abstraction levels and keeping policy separate from mechanics. Each finding identifies a concrete cost and mechanism in its detail. Cleanup is separate from correctness review and cannot satisfy the edit gate.

After the existing review and snapshot gates, collect the four cleanup results and validate their completion and snapshot before one editing stage. If independent reviewers cannot run, perform all four angles in one inline pass and disclose that fallback. Deduplicate by mechanism, retain angle attribution, and record each skipped fix with its reason. Preserve existing edit authorization, scope, snapshot checks and final validation/review.

## Verification

- Add Scrut coverage for four read-only runs, fallback disclosure, cost/mechanism instructions, deduplication, skipped fixes and gate isolation. Prompt canaries check model instructions, not model compliance.
- Commit tests before planting each boundary defect; record observed failures and restore the source after each plant.
- Full local order: parallel anti-patterns and report-only simplify; focused Codex review; comment/text trims; disposable-clone Semgrep baseline; lint-and-fix without push; exact-tree signed tidy.
- Pin each review base to a SHA. Run make test-all, version checks, push, open ready PR and wait for checks. Stop at process gates and report to TOOLING.
