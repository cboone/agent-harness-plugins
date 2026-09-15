# Fix Copilot path-specific instructions guidance

Tracks #421.

## Context

`resolve-copilot-pr-feedback` told agents to write path-specific Copilot instructions at `.github/<name>.instructions.md`. GitHub reads those files only within or below `.github/instructions/`, so the file is never loaded. On #412 that meant instructions written to stop a recurring false finding sat unread for several review rounds.

Commit `340f3192` on this branch already fixes the three places the issue names, bumps the plugin to 1.5.2, and rebuilds both mirrors. The same commit adds `docs/plans/todo/2026-09-14-new-skill-review-in-depth.md`; that file stays, by decision.

Exploration found the same defect class in more places, and the decision is to fix every copy on this branch:

- `resolve-copilot-pr-feedback` gives an invalid `excludeAgent` value (`copilot-coding-agent`).
- `clean-up-agent-config` presents a flat `.github/<scope>.instructions.md` layout as "functionally equivalent", prefers it for one or two files, and proposes consolidating onto it. It also gives invalid `excludeAgent` values (`copilot-code-review`, `copilot-coding-agent`).
- `write-lean-code` names `.github/lean.instructions.md` once.

Facts checked against GitHub's current docs (2026-09-14):

- Path-specific files live "within or below the `.github/instructions` directory"; subdirectories are allowed. Copilot code review reads `.github/instructions/**/*.instructions.md`.
- `applyTo` takes comma-separated globs.
- `excludeAgent` accepts exactly `"code-review"` and `"cloud-agent"`.
- On GitHub.com, path-specific instructions apply only to Copilot cloud agent and Copilot code review.
- Code review reads instructions from the pull request's **head** branch, so a pushed instruction change applies to the next review of the same PR.
- Length guidance: "Limit any single instruction file to a maximum of about 1,000 lines"; "Shorter instruction files are more likely to be fully processed"; start with 10 to 20 specific instructions. No character limit is documented.

## Changes

Invoke `write-markdown` before editing. No em dashes. Every commit is signed, uses `fix:`, and ends with `(#421)`.

### 1. `resolve-copilot-pr-feedback` (stays 1.5.2, already bumped on this branch)

File: `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md`

- **`excludeAgent` sentence** (after the path-specific format block): permitted values are `"code-review"` and `"cloud-agent"`; `excludeAgent: "cloud-agent"` limits a file to code review.
- **"Keep Instructions Concise"**: attribute the length guidance to GitHub's docs (about 1,000 lines per file, shorter files more likely to be fully processed, 10 to 20 specific instructions to start) instead of the unsourced "may not read the full file". Precede it with a short "make sure the file is read" check, since location outranks length as the cause of unread instructions:
  1. The file is under `.github/instructions/` (subdirectories allowed), not directly under `.github/`.
  1. Its `applyTo` glob matches the path of the file Copilot flagged.
  1. It does not set `excludeAgent: "code-review"`.
  1. Copilot reads the PR head branch, so once pushed, the change governs the next review of the same PR. If the same finding recurs after that, re-check 1 to 3 before adding more text.
- **Incorrect-category worked example**: name `.github/copilot-instructions.md` in full for the repo-wide bullet, and point to the read check above.
- **Success Criteria**: name `.github/instructions/*.instructions.md`.
- Rebuild mirrors. Commit.

### 2. `clean-up-agent-config` (1.2.4 to 1.3.0)

Minor bump: the audit now reports flat-layout files as unread and proposes moving them, which changes behavior.

`plugins/clean-up-agent-config/skills/clean-up-agent-config/SKILL.md`:

- **Target layout**: remove the flat-layout tree and the "Both are read by Copilot" sentence; keep the nested tree and state that files directly under `.github/` are not read.
- **"What goes where" table**: `.github/instructions/*.instructions.md` only.
- **Audit file list**: keep scanning `.github/*.instructions.md`, labeled as misplaced and unread.
- **Scoped instructions analysis**: replace "Layout consistency" with a location check that flags any `*.instructions.md` directly under `.github/` as unread, and proposes `git mv` into `.github/instructions/` plus updating links to it.
- **General-file example** (`## Scoped Instructions`): link to `instructions/lean.instructions.md` and `instructions/ts.instructions.md`; drop the flat alternative.
- **4g heading and "Layout"**: a single location, `.github/instructions/<scope>.instructions.md`, with subdirectories allowed.
- **Scoped-file example**: from inside `.github/instructions/`, the back-link becomes `../copilot-instructions.md`.
- **`excludeAgent` list**: `"code-review"` gives cloud agent only, `"cloud-agent"` gives code review only, omitting it gives both. Correct the "Two agents" bullet in the Copilot notes to match (cloud agent and code review on GitHub.com), and reword the adjacent "Keep short" bullet to GitHub's documented guidance, the same way as in change 1.
- **Verification checklist and edge cases**: replace "Only one layout in use" and the mixed-layout consolidation rule with "no `*.instructions.md` directly under `.github/`; move any found".

`references/agent-instruction-files.md`:

- Comparison table file location: drop `.github/*.instructions.md`.
- Copilot section: one location. Remove the "functionally equivalent" paragraph, including the `cboone/shannon-entropy` flat-file example.
- Monorepo example: drop the flat tree; the Lean example path becomes `.github/instructions/lean.instructions.md`.

`references/agent-config-files.md`:

- `excludeAgent` example value becomes `"code-review"`, and the explanatory sentence names cloud agent and code review.

Bump `plugin.json` and the `marketplace.json` entry, recompute `metadata.version` with `bin/compute-catalog-state`, rebuild mirrors. Commit.

### 3. `write-lean-code` (1.0.3 to 1.0.4)

- `plugins/write-lean-code/skills/write-lean-code/references/comprehensive/build-infrastructure.md`: `.github/lean.instructions.md` becomes `.github/instructions/lean.instructions.md`.
- Bump versions, recompute catalog tag, rebuild mirrors. Commit.

### 4. This plan

Commit this plan file (cboone repo convention: plans stay committed). The `pr` skill moves it to `docs/plans/done/` later.

## Out of scope

- `docs/plans/done/` and `docs/reviews/`: historical records, left as written.
- Local `main` (one unpushed commit, `340f3192`, ahead of `origin/main`) and `feature/add-review-colleagues-pr-skill` (created from it): not touched. Reported in the summary.

## Verification

1. Residual scan finds no actionable guidance recommending flat paths, invalid `excludeAgent` values, or claiming that the flat and nested layouts are equivalent. The pattern below also matches the intentional `.github/lean.instructions.md` example in `agent-instruction-files.md` and its generated mirrors, which explains that the path is unread:

   ```bash
   grep -rnE '\.github/[A-Za-z0-9_-]+\.instructions\.md|copilot-coding-agent|copilot-code-review|functionally equivalent|[Ff]lat layout' plugins/ dist/ .agents/
   ```

1. `bin/check-cross-references` passes.
1. `bin/compute-catalog-state` agrees with `metadata.version` after each bump.
1. `make test-all` (lint, validate including mirror freshness, scrut) passes.
1. `check-versions` skill confirms resolve-copilot-pr-feedback 1.5.2, clean-up-agent-config 1.3.0, and write-lean-code 1.0.4 against `origin/main`.
1. `lint-and-fix` after the edits.
