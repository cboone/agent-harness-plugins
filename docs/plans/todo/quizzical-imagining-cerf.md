# 2026-02-17 Add Issue Status Management

## Context

Several skills in this repository interact with GitHub issues but none manage issue status transitions. When `create-worktree-from-issue` starts work on an issue, the issue remains untouched — no assignment, no label, no signal that someone is working on it. Similarly, `suggest-next-issue` detects in-progress work only by checking for matching branches/worktrees, missing issues that were claimed via labels or assignment outside this toolchain.

This plan adds lightweight, universally-compatible status management using self-assignment and an "in progress" label — no GitHub Projects setup required.

## Skills Reviewed

| Skill                       | Interacts with issues?                   | Needs changes?                                     |
| --------------------------- | ---------------------------------------- | -------------------------------------------------- |
| create-worktree-from-issue  | Yes — finds and starts work on issues    | **Yes** — add status transitions                   |
| suggest-next-issue          | Yes — lists and recommends issues        | **Yes** — enhance in-progress detection            |
| pr                          | Yes — references issues in PR body       | No — GitHub handles close-on-merge via "Closes #N" |
| commit                      | Yes — references issues from branch name | No — no status management needed                   |
| resolve-copilot-pr-feedback | No — operates at PR level                | No                                                 |
| create-worktree             | No — general task worktrees              | No                                                 |

## Changes

### 1. create-worktree-from-issue SKILL.md — Add "Mark Issue In Progress" step

**File:** `plugins/create-worktree-from-issue/skills/create-worktree-from-issue/SKILL.md`

Insert a new **step 2** between the current "1. Find the Issue" and "2. Build the Branch Name". Renumber all subsequent steps (current 2→3, 3→4, 4→5, 5→6).

**New step 2 content:**

- Skip if the issue is closed (the skill already warns about closed issues)
- Self-assign: `gh issue edit NUMBER --add-assignee @me`
- Add label: `gh issue edit NUMBER --add-label "in progress"`
- Both commands are idempotent — safe to re-run
- Failures warn but never block worktree creation (best-effort)

**Update to step 6 (Report Success):** Add a bullet noting the issue was marked in progress.

**Update to Error Handling section:** Add a bullet about status-marking failures being non-blocking.

### 2. suggest-next-issue SKILL.md — Enhance in-progress detection

**File:** `plugins/suggest-next-issue/skills/suggest-next-issue/SKILL.md`

**Enhance step 2 (Identify In-Progress Work):** Expand the definition of "in progress" from just branch/worktree matching to include:

1. Has a corresponding branch or worktree (existing behavior)
1. Has an "in progress" label (new)
1. Is assigned to the current user (new — use `gh api user --jq '.login'` to get username)

Note: The `gh issue list` command in step 1 already fetches `labels` and `assignees` fields, so no extra API call is needed for those. Only one new call: `gh api user --jq '.login'`.

**Update step 5 (Summarize In-Progress Work):** Note how each issue was detected (branch, label, or assignment).

**Update example output (line 146):** Add examples showing label- and assignment-detected in-progress issues.

### 3. Version bumps

These are additive enhancements (new behavior layered onto existing workflows), warranting **patch** bumps:

| File                                                            | Field                                | Old   | New   |
| --------------------------------------------------------------- | ------------------------------------ | ----- | ----- |
| `plugins/create-worktree-from-issue/.claude-plugin/plugin.json` | version                              | 1.1.4 | 1.1.5 |
| `plugins/suggest-next-issue/.claude-plugin/plugin.json`         | version                              | 1.0.1 | 1.0.2 |
| `.claude-plugin/marketplace.json` line 94                       | version (create-worktree-from-issue) | 1.1.4 | 1.1.5 |
| `.claude-plugin/marketplace.json` line 178                      | version (suggest-next-issue)         | 1.0.1 | 1.0.2 |

Marketplace `metadata.version` stays at `1.6.0` (no plugins added or removed).

## Files Modified (6 total)

1. `plugins/create-worktree-from-issue/skills/create-worktree-from-issue/SKILL.md`
1. `plugins/suggest-next-issue/skills/suggest-next-issue/SKILL.md`
1. `plugins/create-worktree-from-issue/.claude-plugin/plugin.json`
1. `plugins/suggest-next-issue/.claude-plugin/plugin.json`
1. `.claude-plugin/marketplace.json`

## Verification

- [ ] Step numbers in create-worktree-from-issue are sequential 1–6 after insertion
- [ ] `gh issue edit` commands use correct flags (`--add-assignee @me`, `--add-label "in progress"`)
- [ ] suggest-next-issue step 2 references data already fetched in step 1 (no redundant API calls)
- [ ] `gh api user --jq '.login'` is correct syntax for getting authenticated username
- [ ] Versions match between each plugin.json and its marketplace.json entry
- [ ] Marketplace metadata.version unchanged at 1.6.0
- [ ] Status marking documented as best-effort / non-blocking
- [ ] Closed issues excluded from "mark in progress" step
