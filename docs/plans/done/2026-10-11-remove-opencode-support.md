# Remove OpenCode support

Issue: [#585](https://github.com/cboone/agent-harness-plugins/issues/585). Classification: chore.

## Context

OpenCode is a third generated target alongside Claude Code (canonical) and Codex CLI. Keeping it costs a mirror, a generator, CI steps, validation branches, a TypeScript port of `notify`, and harness-specific text in many skills. The catalog drops it and keeps Claude Code plus the Codex CLI mirror. Decisions taken during planning:

- `clean-up-agent-config` and `scaffold-new-repo` also lose their OpenCode coverage (audit of `opencode.json`, `~/.config/opencode/`), not just catalog-support text.
- The root README keeps a one-line note naming the last commit on `main` that shipped `dist/opencode/` (`41605e95`, current `main` head; re-check at implementation time).
- Historical plans and reviews under `docs/plans/` and `docs/reviews/` stay untouched, as do `tests/data/` fixtures that quote OpenCode as recorded data (`copilot-reviews/format-a.json`, `write-realtime-audio-code-evals/`), except the evals README instruction, which is updated to name only the Codex layout.

## Changes

### 1. Mirror, generator and build wiring

- Delete `dist/opencode/` and `bin/build-opencode-mirror`.
- `Makefile`: drop the `build` call and the "and OpenCode" help text.
- `.github/workflows/ci.yml` and `release.yml`: drop the generator call; reword the CI comment about untracked symlinks under `dist/opencode/skills/` so it still justifies `git status --porcelain` (new untracked Codex files).
- `.prettierignore` and `cli.markdownlint-cli2.jsonc`: comments name only the Codex mirror; the markdownlint comment loses the symlink-following rationale.

### 2. Validators and scrut

- `bin/check-cross-references`: drop `dist/opencode` from `UNAMBIGUOUS_PREFIXES` and `CANDIDATE_PREFILTER`.
- `bin/validate-plugins`: rule 16b and rule 21 comments name Claude Code and Codex only ("both tolerate" rather than "all three").
- `tests/scrut/validate-plugins-skills.md`, `tests/scrut/build-codex-marketplace.md`: prose only; no expected output changes.

### 3. `notify` (major: 2.5.0 to 3.0.0, `.codex-plugin` mirrored)

- Delete `plugins/notify/opencode/` and `assets/opencode.png`.
- `scripts/notify`: header and `summarizeReply` cross-reference comments, and the `OpenCode` pane-title case.
- `README.md`: remove the OpenCode section, event table, and OpenCode clauses in title, body, grouping and tmux text.
- Description in `plugin.json`, `.codex-plugin/plugin.json` if it carries one, `marketplace.json`, root and plugin READMEs: "when Claude Code or Codex CLI finishes...".

### 4. `clean-up-agent-config` (major: 1.3.3 to 2.0.0)

- `SKILL.md` (description, four tools to three, tree, tables, step 4i, OpenCode section) and both references: remove OpenCode rows, sections, symlink commands and prose; keep the general point that `AGENTS.md` is read by many tools.
- Catalog description and keywords drop OpenCode in `plugin.json`, `marketplace.json` and both READMEs.

### 5. Other skills (patch bumps; wording only, behavior unchanged for Claude Code and Codex)

- Script-locator fallbacks keep the Codex reason and drop "and OpenCode does not substitute it at all": `address-issue-in-worktree`, `create-worktree`, `monitor-pr`, `publish-report-board`, `resolve-copilot-pr-feedback`, `review-until-clean`, `triage-dependabot-prs`.
- Harness lists "(Codex CLI, OpenCode)" become "(Codex CLI)": `address-issue`, `review-dependabot-config`, `triage-dependabot-prs`, `monitor-pr` (SKILL and README), `publish-report-board` (SKILL, `artifact-mechanics.md`, README).
- `review-until-clean`: drop the OpenCode row from the default-reviewer table.
- `create-plugin`: SKILL checklist and gotchas, `skill-md.md`, `scripts.md` name only the Codex mirror.
- `scaffold-new-repo`: `references/agents-md.md` tool list.
- `wtaf`: README drops the OpenCode sentence and anchor link.

Planned versions: address-issue 1.2.1, address-issue-in-worktree 2.4.1, create-plugin 1.3.4, create-worktree 1.7.1, monitor-pr 2.1.1, publish-report-board 1.2.1, resolve-copilot-pr-feedback 2.0.1, review-dependabot-config 1.0.3, review-until-clean 1.1.2, scaffold-new-repo 1.8.5, triage-dependabot-prs 1.0.6, wtaf 2.0.1.

### 6. Documentation and agent config

- `README.md`: intro, contents links, install section, the "Using with OpenCode" section and anchor, plus a one-line removal note naming the last shipping commit.
- Root `AGENTS.md`: overview, `make build` comment, anchor rule (keep `install` and `codex-cli-known-limitations`). Re-check the 32 KiB instruction-chain budget is unaffected (it only shrinks).
- `plugins/AGENTS.md`: cross-harness hook line.
- `docs/plugin-development.md`: templates lookup sentence, hook-plugin layout tree and text (two harnesses), frontmatter table (drop OpenCode column and its evidence and measurement steps), invocation table, skill composition, cross-reference prefix table, build step, protected-anchor list.
- `.github/copilot-instructions.md`: delete the two OpenCode mirror symlink rules. `.github/instructions/dependabot.instructions.md`: "happens in Codex CLI".

### 7. Build, validate, commit

- `make build`, `make test-all`, the `check-versions` skill, and a final `grep -ri opencode` outside the excluded historical paths.
- Small signed Conventional Commits referencing `(#585)`, roughly: mirror and tooling; notify; clean-up-agent-config; remaining skills; docs and agent config; this plan.

## Follow-ups outside this repository

- `cboone/dotfiles` `.config/shell/env.sh` exports `OPENCODE_CONFIG_DIR` pointing at `dist/opencode`; it should be removed there separately.
- After merge, close #553 and #582 and check #434 and #518 for OpenCode-only parts.

## Verification

- `make build` leaves no drift; `make test-all` passes (lint, validate including cross-references rule 19, scrut).
- `grep -rIi opencode` outside `docs/plans/`, `docs/reviews/` and the recorded `tests/data/` fixtures returns only the README removal note.
- `markdownlint-rule-relative-links` confirms no link targets `#using-with-opencode`.
