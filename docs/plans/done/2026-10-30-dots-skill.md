# Dots skill

Add an explicitly invoked `dots` plugin for [issue 574](https://github.com/cboone/agent-harness-plugins/issues/574). Reply with one code block containing exactly 50 single-dot lines, without tools or surrounding text. Start at version 1.0.0 and reuse the existing Codex invocation-policy translation. No live configuration edits.

## Prior art

- Claude Code's [interactive-mode documentation](https://code.claude.com/docs/en/interactive-mode) describes Ctrl+L as redraw. The [context-preserving clear-screen request](https://github.com/anthropics/claude-code/issues/58452) explains why terminal clearing is insufficient. Neither provides the requested output.
- Codex's [invocation-policy discussion](https://github.com/openai/codex/issues/40600) distinguishes catalog visibility from explicit turn-time selection. Both need testing.
- Searches for Claude Code and Codex clear-screen, scroll-off and dots skills found shortcuts and community discussions, but no matching reusable skill. Reuse the repository generator rather than add a terminal helper.

## Work

1. Register the canonical skill, manifest and README; regenerate Codex output.
2. Test visibility, explicit invocation and rendering in an isolated live Codex session.
3. Add contract and generated-policy Scrut checks; plant count and policy defects, then restore each.
4. Complete the full local review order, lint, validation and version checks. Acquire the shared lock for one full suite at `SCRUT_JOBS=2`, retain known baseline failures, tidy and open a ready PR. TOOLING merges.

## Evidence

- Codex CLI 0.166.0, GPT-6.1-Sol at medium effort; live daemon-backed TUI session `01a18f3a-d72b-7a52-b46f-004df8e6678d`, 100×30 terminal, temporary project `/tmp/dots-574.rKrVhB/project`. Canonical frontmatter remained in the implicit catalog; generated policy withheld it while explicit `$dots` selection worked.
- The saved response was exactly one fenced block with 50 single-dot lines and no tools. All 50 rows rendered and scrolled `DOTS-BEFORE-574` out of view. This measures that CLI and terminal geometry. Raw rendering is retained in `/tmp/dots-574.rKrVhB/tui-render.json`.
- All three focused checks passed. Requesting 49 lines failed the contract and mirror checks; generating policy `true` failed its snapshot. Both plants were restored.
- The diff exceeded the small-change target, so full review ran. Final checks and known baseline failures are recorded in the [verification ledger](../../reviews/2026-10-30-dots-ledger.md).
