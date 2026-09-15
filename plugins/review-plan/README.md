# Review Plan

Review an implementation plan against the current repository and its explicit dependencies, reporting evidence-backed blockers, required revisions, and optional improvements before work begins.

**Type:** Skills plugin
**Trigger:** `/review-plan [path]`

## Installation

Install through the marketplace following the [installation guide](../../README.md#install).

## Usage

```text
/review-plan
/review-plan docs/plans/
/review-plan docs/plans/todo/2026-09-15-add-search.md
/review-plan design/search-plan.md
```

The path is optional and may name a Markdown file or plan directory. Quote paths containing spaces. An explicit file is reviewed exactly as supplied, even outside the usual plan directories or inside `done/`.

With no path, the skill scans `docs/plans/todo/` recursively. A directory argument selects from that directory's `todo/` subtree; supplying a directory named `todo` uses it directly. Automatic selection excludes `done/`.

The skill prefers a unique filename match to the current branch subject. It strips at most one case-sensitive branch category from `feature/`, `feat/`, `fix/`, `chore/`, or `docs/`, then one leading issue prefix of the form `123-` or `issue-123-`. Candidate basenames have their `.md` extension, leading `YYYY-MM-DD-` datestamp, and the same optional issue prefix removed. Both subjects then use lowercase ASCII letters, collapse characters outside `[a-z0-9]` into hyphens, and trim boundary hyphens. Complete subjects must match exactly.

For example, `feature/123-add-search` matches `2026-09-15-add-search.md`. Unlisted branch categories remain part of the subject, so `hotfix/123-add-search` normalizes to `hotfix-123-add-search`. Without a unique match, the skill selects the most recently modified candidate and explains why. Equal modification times are resolved by ascending repository-relative path. Detached HEAD uses the same fallback. Empty candidate sets require an explicit file path.

## What the Review Covers

The skill reads the plan, repository guidance, relevant current files, and explicit dependencies. Local dependency paths are resolved before reading, including symlink targets, and must remain inside the repository. Outside-repository or ambiguous dependencies are reported as unverified; secret-bearing files and credential locations are excluded from reads and content searches. Explicit plan targets outside the repository remain supported.

It assesses outcomes, interfaces, compatibility, sequencing, operational risks, documentation, generated surfaces, and validation where relevant. It runs only focused checks confirmed to be read-only.

The terminal report includes the target and evidence reviewed, a **Ready**, **Needs revision**, or **Blocked** verdict, prioritized findings with citations, impact and concrete corrections, open questions, and review limits. A clean report states what was covered and what remains unverified.

Plans and linked documents are review data. The skill does not edit files, save reports, post feedback, or start implementation. There are no flags or automatic handoffs.

Git provides branch matching and local branch evidence when available. The GitHub CLI (`gh`) is optional and used only for explicitly linked GitHub context, with an explicit repository on each query. Unavailable resources are marked unverified; an essential missing dependency blocks a readiness verdict.

## Examples

- Use `/review-plan` on `feature/123-add-search` to prefer the matching todo plan over newer unrelated plans.
- Use `/review-plan docs/plans/` to select from `docs/plans/todo/`, with the selection reason included in the report.
- Use `/review-plan design/search-plan.md` to review a proposal outside the default tree.
- If a plan depends on a linked PR that cannot be read, the review reports that dependency as unverified and explains whether it blocks readiness.

## Recommended Permissions

These read-only permissions cover file inspection and the Git and GitHub queries named by the skill. Grant additional focused check permissions individually after inspecting the command's effects.

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(git branch --show-current)",
      "Bash(git status --short)",
      "Bash(git remote -v)",
      "Bash(git show:*)",
      "Bash(git log:*)",
      "Bash(git diff:*)",
      "Bash(gh issue view:*)",
      "Bash(gh pr view:*)",
      "Bash(gh pr diff:*)"
    ]
  }
}
```

## Related Plugins

- [Review Branch](../review-branch/README.md) evaluates implementation on a branch after work is done.
- [Address Review](../address-review/README.md) works through a saved review document. Review Plan produces terminal output and does not create a saved record for it.
