---
name: suggest-next-issue
description: >-
  Review all open GitHub issues in the current repository, analyze them in
  context (current branch state, recent work, project goals, dependencies), and
  recommend what to work on next with prioritized reasoning. Use when the user
  says "suggest next issue", "what should I work on next", "which issue should I
  tackle", "prioritize issues", "review open issues", "suggest an issue",
  "triage issues", or asks for help choosing between open issues. Also use
  when the user asks what can be worked on in parallel, or which issues avoid
  an exclusive resource another worktree is holding. Requires the gh CLI to be
  installed and authenticated.
---

# Suggest Next Issue

Analyze open GitHub issues and recommend what to work on next.

## Options

The user may provide these options inline:

- **label filter**: Focus on issues with a specific label (e.g., "suggest next bug" or "suggest next issue --label enhancement")
- **milestone filter**: Focus on issues in a specific milestone
- **limit**: Number of recommendations (default: 5)
- **include PRs**: Also consider open PRs needing attention (reviews, conflicts, CI failures)
- **--parallel-only**: Recommend only issues that can run beside the work already under way, excluding any whose verification needs an exclusive resource another worktree holds

Treat a request that asks for parallel-safe work in its own words as `--parallel-only`, whether or not the flag was typed: "what can I work on in parallel", "what can I start alongside this", "anything that does not need the DAW". The user asked for the restriction; requiring the flag as well would answer a question they did not ask.

## Workflow

### 1. Gather Context

Run these commands to build a complete picture:

```bash
# Open issues (with details for analysis)
gh issue list --state open --json number,title,labels,assignees,createdAt,updatedAt,comments,milestone,body --limit 100

# Recently closed issues (understand momentum)
gh issue list --state closed --json number,title,labels,closedAt --limit 10 --sort updated

# Current branches/worktrees (what's already in progress)
git worktree list
git branch --list --format='%(refname:short)'

# Current authenticated user (for assignment detection)
gh api user --jq '.login'

# Project context
gh repo view --json description,defaultBranchRef
```

If the user specified `--label` or `--milestone`, add the corresponding `--label` or `--milestone` flag to `gh issue list`.

If the user specified `--include-prs`:

```bash
gh pr list --state open --json number,title,labels,createdAt,updatedAt,isDraft,reviewDecision,statusCheckRollup
```

Also read the repo's README and any roadmap or project documentation to understand project goals.

**Read the exclusive-resource claims.** Some work cannot run in parallel because it needs a resource only one worktree can hold: a DAW, a simulator, a device, a database, a port, a shared install location. `create-worktree` and `address-issue-in-worktree` record those claims in the main worktree's `.claude/worktree-resources.local.json`. Resolve it from the first record of `git worktree list --porcelain -z`, whose `worktree` field is always the main worktree, and open the file with the Read tool:

```bash
git worktree list --porcelain -z
```

`-z` matters and is not decoration. Without it the records are newline-delimited, so a worktree path containing a newline splits across two apparent fields and the path read back is a truncation of the real one. The claim file would then be looked for somewhere that does not exist, ordinary recommendations would silently lose the resource signal, and `--parallel-only` could not apply the filter it promises. With `-z` each field ends in a NUL, which no path can contain. The bundled `manage-resource-claims` parses the same way, for the same reason.

A missing file means no claims, which is the ordinary state and not an error. Each claim carries `id`, `resource`, `worktree`, `branch`, `claimed_at`, and an optional `issue`.

**Validate the file before reading the claims.** This reads the file directly rather than through `manage-resource-claims`, so it inherits none of that script's guards, and treating malformed data as resource state would produce confident parallel-safety advice from something it has misunderstood. Require all of:

- `version` is the number `1`. It is the only version this skill knows.
- `claims` is an array.
- Every entry is an object whose `id`, `resource`, `worktree`, `branch`, and `claimed_at` are strings, with `id` lowercase hexadecimal.
- `resource`, `branch`, and `claimed_at` are non-empty and contain no whitespace, and `resource` does not start with a hyphen.
- `worktree` is non-empty and contains no control characters. Spaces are legal here and only here, because it is a path.
- `gitdir`, when the key is present, is a non-empty string containing no control characters. It is the worktree's git admin directory, and it is optional because it cannot always be resolved.
- `issue`, when the key is present, is a non-negative integer. It is optional and omitted rather than null for a worktree that did not come from an issue, so absent is normal and `"128"` as a string is not.
- No two entries name the same `resource`.

That is the same contract `manage-resource-claims` enforces, and matching it matters rather than being pedantry. A `resource` of `"logic "` would never match the `logic` an issue asks for, so the conflict would go unreported; a control character in `worktree` would not match any line of `git worktree list`, so a live claim would read as stale and be discounted. A weaker check here does not fail loudly, it gives confident advice that is wrong.

A missing file is not a failure: it means no claims. Anything that fails these checks is. On a failure, make the recommendations without the resource signal and say why, naming which check failed. Do not treat a partially readable file as partially authoritative: an entry you cannot parse may be the very claim that would have changed the advice.

**Under `--parallel-only`, a failure is fatal rather than a downgrade.** That option promises every recommendation is safe to start beside the work already under way, and a claim file that cannot be read makes the held resources unknown, so nothing can be promised. Report that the claims are unreadable and that the parallel-safety filter cannot be applied, offer the ordinary recommendations instead, and let the user decide. Presenting unfiltered work as parallel-safe is the one outcome this option must never produce.

**Discount stale claims.** Read the `git worktree list --porcelain` output as whole records, and ignore any record carrying a `prunable` line: git keeps listing a worktree whose directory has been deleted and marks it that way rather than dropping it, so a removed worktree would otherwise count as live and filter out issues that are in fact parallel-safe.

A claim carrying a `gitdir` is live when that value equals the admin directory of some remaining record, which you get by running `git -C <record path> rev-parse --path-format=absolute --git-dir`. That is the identity `manage-resource-claims` uses, and it is the only one that survives both `git worktree move` and `git switch`. Skipping it marks a worktree that has had both changed as stale, and `--parallel-only` then recommends work that collides with a resource someone is holding.

For a claim with no `gitdir`, or a record whose admin directory cannot be resolved, fall back: live when some remaining record matches **either** its `worktree` path **or** its `branch`, and stale only when neither matches. Neither field identifies a worktree by itself: `git worktree move` changes the path and keeps the branch, `git switch` changes the branch and keeps the path, and a removed path can later be reused by an unrelated worktree. Matching on either errs toward reporting a resource still held, which is the right direction here, because reading a live claim as stale is what would let this skill recommend work that collides with someone.

Treat a stale claim as free, and mention it so the user can clear it. Nothing that no longer exists should keep a resource reserved.

**Read the project's declared resources too.** Read whichever of `CLAUDE.md` and `AGENTS.md` exist in the repository root, and `copilot-instructions.md` under `.github/`. Any of them may be absent, which is normal, and `CLAUDE.md` is often a symlink to `AGENTS.md`, so read the target rather than treating it as a second source. Check any plan under `docs/plans/todo/` too. A heading containing "exclusive resource" names the project's resources and, usually, what kind of work needs each one. That list is what lets an issue be matched to a resource before anyone has claimed it.

**The declared list is an aid, not the set of resources that exist.** Resource names are free strings with no registry, so a project may hold `logic` without ever declaring it. Match each issue against the union of the declared names and the names on live claims, so a held resource an issue asks for by name is caught whether or not the project wrote it down. Where no list exists at all, the live claims are the whole vocabulary, and `--parallel-only` must still exclude an issue whose body names one of them.

### 2. Identify In-Progress Work

An issue is considered in progress if **any** of the following are true:

1. **Branch or worktree match**: A branch or worktree name contains the issue number (existing behavior)
1. **"in progress" label**: The issue has a label named "in progress" (case-insensitive match on the `labels` data already fetched in step 1)
1. **Assigned to current user**: The issue's `assignees` list (already fetched in step 1) includes the authenticated username from `gh api user`

Exclude in-progress issues from recommendations, but note them in the output as "already in progress" along with how each was detected (branch, label, assignment, or a combination).

A label-only match may mean local work is complete but the related PR is still waiting to merge. Keep excluding the issue in that state. Do not recommend it again only because no matching branch or worktree is visible.

### 3. Analyze Each Issue

Evaluate each open issue (that is not already in progress) on these signals:

| Signal                | Source                                                                 | Weight |
| --------------------- | ---------------------------------------------------------------------- | ------ |
| **Priority labels**   | Labels containing "bug", "critical", "urgent", "security"              | High   |
| **Dependencies**      | Issue body references to other issues (#N, "depends on", "blocked by") | High   |
| **Resource conflict** | Issue work or verification needs an exclusive resource already held    | High   |
| **Age**               | `createdAt` field                                                      | Medium |
| **Activity**          | Number of comments, `updatedAt` recency                                | Medium |
| **Effort**            | Issue body length/complexity, scope described                          | Low    |
| **Momentum fit**      | Similarity to recently closed issues                                   | Low    |

Dependency analysis: scan each issue body for references to other issues (`#N`, "depends on #N", "blocked by #N", "after #N"). Build a dependency graph to identify:

- Issues that **unblock** other open issues (high value)
- Issues that are **blocked** by other open issues (note the blocker)

Resource analysis: match each issue against the project's declared resources from step 1. An issue whose work or verification needs a resource a live claim holds is a poor next pick even when every other signal is strong, because starting it means either waiting or taking the resource away from work already under way. Say which resource and who holds it rather than silently ranking the issue down. Under `--parallel-only`, drop such issues from the recommendations entirely and list them separately.

This is advisory. An issue is never hidden outright unless `--parallel-only` was passed, because the user may well intend to finish the holding work first and start this next.

### 4. Generate Recommendations

Present the top N issues (default 5) organized by category:

**Categories** (use whichever apply, skip empty categories):

- **Safe to Parallelize**: Issues that need no resource a live claim holds, so they can start beside the work already under way
- **Narrow Scope**: Small, well-defined issues that touch few files and carry no open dependencies
- **High Impact**: Important features, critical bugs, or heavily requested items
- **Unblocks Others**: Issues that other open issues depend on
- **Overdue**: Old issues that have been neglected (use judgment based on repo's typical issue age)

Use **Safe to Parallelize** only when at least one resource is actually held. With nothing claimed, every issue qualifies and the category says nothing.

For each recommendation, include:

1. Issue number and title text (e.g., `#23 - Fix typo in help output`). Use the `title` field from the JSON, not the issue URL.
1. Labels and age
1. What it is: a brief summary of the issue (1-2 sentences distilled from the issue body, so the user understands the scope and substance without having to open the issue)
1. Why it's recommended (1-2 sentences with specific reasoning)
1. Suggested first steps or approach (1 sentence)
1. Blockers or considerations, if any, naming the resource and its holder when one applies

### 5. Summarize In-Progress Work

After recommendations, briefly list issues detected as in progress. For each, note how it was detected: branch/worktree, "in progress" label, assignment to current user, or a combination. This gives the user a complete picture of active work, including issues that may be waiting on PR merge after local implementation is done.

Then, when any resource is claimed, list who holds what: the resource, the branch, and whether the claim is stale. This is the half of the picture the issue list cannot show, and it is what answers "what can I work on in parallel" without the user having to remember the constraint. Skip the section entirely when nothing is claimed.

### 6. Offer to Start Work

End with an offer to create a worktree for the chosen issue via the `address-issue-in-worktree` skill. Example:

```text
Ready to start on one of these? Just say "start issue #N" or pick a number from the list.
```

## Example Output

```markdown
## Suggested Next Issues

### Safe to Parallelize

1. **#31 - Document the config schema** (documentation, 5 days old)
   Write reference docs for every key the config module accepts, with defaults and env overrides.
   Touches only `docs/`, so it needs nothing the `logic` claim is holding.
   Start: Read the config module's schema and mirror it.

### Narrow Scope

2. **#23 - Fix typo in help output** (bug, 2 days old)
   The `--version` flag prints "verison" instead of "version" in the CLI help text.
   Small fix, keeps the issue count tidy.
   Start: Check the help string in the CLI entry point.

### High Impact

3. **#18 - Add dark mode support** (enhancement, 12 days old, 4 comments)
   Add a system-preference-aware dark color scheme with a manual toggle in the settings panel.
   Most-requested feature. Pairs well with the theme work done in #15.
   Start: Add CSS variables for color scheme, then add a toggle component.

### Unblocks Others

4. **#7 - Refactor config loading** (enhancement, 20 days old)
   Replace the ad-hoc JSON parsing with a centralized, schema-validated config module that supports defaults and env overrides.
   Issues #8 and #9 both depend on the new config system.
   Start: Extract config into a dedicated module with typed schema.

### Overdue

5. **#3 - Update installation docs** (documentation, 45 days old)
   The install guide still references the old `curl | bash` method; needs updating for the new package manager install flow.
   Open since v0.2. Quick update needed for current install process.
   Start: Compare current docs against actual install steps.

---

**Already in progress:**

- #14 -- feature/improve-notifications (branch)
- #16 -- fix/search-pagination (branch, assigned)
- #21 -- Add export feature (label: "in progress")
- #25 -- Fix auth timeout (assigned)

**Exclusive resources held:**

- `logic` -- feature/14-improve-notifications, claimed 2026-09-12T18:04:11Z
- `simulator` -- fix/99-old-thing (stale: that worktree no longer exists, clear it with `/create-worktree --release-resource simulator`)

#9 and #12 both need `logic` for verification, so they are better started once #14 is done.

Ready to start on one of these? Just say "start issue #N".
```

## Error Handling

- If `gh` is not authenticated, instruct the user to run `gh auth login`
- If no open issues exist, report that and suggest checking closed issues or creating new ones
- If all open issues are already in progress, report that and congratulate the user
- If the claim file is unreadable or malformed and `--parallel-only` was not asked for, say so and carry on without it. Resource awareness sharpens ordinary recommendations; it is not a precondition for making them
- If the claim file is unreadable or malformed and `--parallel-only` was asked for, do not carry on. That option promises every recommendation is safe to start beside the work under way, and unknown claims mean nothing can be promised, so report that the filter cannot be applied and offer the ordinary recommendations as a choice instead
- If `--parallel-only` leaves nothing to recommend, say which resources are held and which issues they hold back, rather than reporting an empty list
