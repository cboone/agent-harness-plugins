# Review Colleague PR

Review a colleague's pull request carefully and considerately from a checkout of its branch, and report a brief, read-only assessment in chat: requirements, direction, blockers, follow-ups, and questions for the author.

**Type:** Skill
**Trigger:** `/review-colleague-pr`
**Requires:** [`gh`](https://cli.github.com/) (authenticated)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Prepares you to give a colleague feedback on their pull request. The skill reads the PR's stated requirements (its description, linked issues with their parent issues and sub-issues, and any docs you point it to), the discussion so far, and the code at the PR's current head. It then prints a short report in chat. You write the actual feedback in your own words.

The report covers:

- **Verdict**: ready to approve, approve with follow-ups, needs changes, or needs a rethink
- **Summary**: what the PR actually does
- **Requirements**: gaps against what it set out to do
- **Direction**: whether it moves the codebase somewhere good
- **Before merge**: problems that would cause harm or be costly to undo if merged as it is
- **Could be follow-ups**: real but not urgent points, including clear departures from the codebase's established practice
- **Questions for the author**: unclear intent, and anything that could not be confirmed
- **Pre-existing**: problems in the code the PR touches that it did not introduce
- **Done well**: genuine strengths
- **Since your last review**: on a re-review, which of your earlier points were addressed

Empty sections are left out, and the length follows the size of the PR.

### How it reviews

The skill follows a set of principles meant to produce a fair review rather than a long one:

- **Careful**: understand intent before judging, trace every concern through the code before stating it (with `path:line` citations), keep what the PR introduced separate from what was already there, and leave out nits, taste, and anything a linter enforces.
- **Considerate**: read the author's choices charitably, treat a valid alternative approach as not a defect, respect the PR's stated scope, do not repeat points others already raised, separate what must change before merge from what can follow, credit real strengths, and comment on the code, never the person.

### What it never does

- Post, comment, review, label, or resolve anything on GitHub
- Change local project files or the checkout. Its local writes are limited to fetched Git objects, remote-tracking refs, and `FETCH_HEAD`; it never commits or pushes.
- Run tests, builds, linters, or installs (it reads CI status instead)

The skill reads reviewable PR files from fetched Git tree and blob objects. It first lists changed paths and excludes secret-bearing files, lockfiles, vendored code, and files the base branch marks as generated before retrieving patches or blobs. Issue lookups stay within the PR repository; cross-repository references from PR text are not followed. The skill does not depend on the checkout being current or clean, and it leaves local files and refs unchanged except for fetched refs and `FETCH_HEAD`. A shallow checkout stops because its history can omit part of the diff. For merged PRs, and for unmerged PRs whose head is already in the base, it first retrieves filenames through GraphQL and verifies completeness against the PR's file count. It retrieves retained GitHub patches only when every file is reviewable. Excluded files, an unclassifiable rename source, incomplete file lists, or unavailable patches stop that review before assessment.

## Usage

Check out the PR's branch, ideally in its own worktree, then run the skill from there:

```text
gh pr checkout 123           # or: workmux add --pr 123
/review-colleague-pr
/review-colleague-pr 123
/review-colleague-pr 123 https://example.com/specs/webhook-retries
/review-colleague-pr --full
/review-colleague-pr --since a1b2c3d
```

| Option           | Description                                                           |
| ---------------- | --------------------------------------------------------------------- |
| `<pr-number>`    | The PR to review; defaults to the PR for the current branch           |
| Requirement docs | URLs or pasted text after the number, read as additional requirements |
| `--full`         | Review the whole PR even if you have reviewed it before               |
| `--since <ref>`  | Treat this commit as the point of your last review                    |

If the PR's description, linked issues, and your docs say little about what the PR is for, the skill asks for more before it reads the code, rather than reviewing against a guess.

## Example

```markdown
## PR #123: Add retries to the webhook sender (@author)

**Verdict:** Needs changes. One bug to fix before merge; the rest can follow.
Reviewed `a1b2c3d` (checkout unchanged): 12 files, +340/-58. CI: 1 failing (`integration`).

**Summary.** Adds retry with exponential backoff to outgoing webhooks, with a per-endpoint attempt limit.

**Requirements.** Covers #118 except the backoff cap the issue calls for. Sources: PR description, #118.

**Direction.** Fits the existing queue abstraction, but adds a second HTTP client where the existing one would serve.

**Before merge**

1. A timeout after the request is sent triggers a retry, so the receiver gets the webhook twice (`src/sender.ts:84`).

**Could be follow-ups**

- Convention: errors are swallowed here, while every other module in `src/client/` wraps and returns them (`src/client/retry.ts:40`).

**Questions for the author**

- Is dropping the signature header on retries deliberate (`src/sender.ts:97`)?

**Done well**

- Thorough tests for the backoff schedule.
```

## How It Differs

- [Review Branch](../review-branch/README.md) evaluates your own branch, checks plan compliance when a plan is available, and normally saves a review document. Review Colleague PR evaluates someone else's pull request and saves nothing.
- [Resolve Copilot PR Feedback](../resolve-copilot-pr-feedback/README.md) acts on review feedback: it changes code and replies on GitHub. Review Colleague PR only reads.

## Recommended Permissions

GitHub access is read-only. Git fetches refs only; it does not update the branch, index, or working tree. PR and base-branch file contents come from Git objects, with retained GitHub patches used for merged PRs or a head already in the base. To allow these commands to run without individual permission prompts, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(awk *)",
      "Bash(gh api --paginate repos/*)",
      "Bash(gh api --paginate \"repos/*)",
      "Bash(gh api graphql *)",
      "Bash(gh api --hostname *)",
      "Bash(gh api user *)",
      "Bash(gh issue view *)",
      "Bash(gh pr checks *)",
      "Bash(gh pr view*)",
      "Bash(git branch --show-current)",
      "Bash(git diff *)",
      "Bash(git --literal-pathspecs diff *)",
      "Bash(git --no-pager diff *)",
      "Bash(git --no-pager --literal-pathspecs diff *)",
      "Bash(git --attr-source=* --no-pager diff *)",
      "Bash(git --attr-source=* --no-pager --literal-pathspecs diff *)",
      "Bash(git -c core.hooksPath=/dev/null fetch *)",
      "Bash(git log *)",
      "Bash(git --no-pager log *)",
      "Bash(git --no-pager --literal-pathspecs log *)",
      "Bash(git show *)",
      "Bash(git --literal-pathspecs show *)",
      "Bash(git --no-pager show *)",
      "Bash(git --no-pager --literal-pathspecs show *)",
      "Bash(git --literal-pathspecs ls-tree *)",
      "Bash(git --no-pager --literal-pathspecs ls-tree *)",
      "Bash(git --no-pager cat-file blob *)",
      "Bash(git merge-base *)",
      "Bash(git remote -v)",
      "Bash(git rev-parse *)"
    ]
  }
}
```

If the selected prior review is not an ancestor of the PR head, or that relationship cannot be established, the skill reviews the whole PR and reports the baseline limitation. It never replaces the checkout. The `gh api` rules also match write calls; the skill's ground rules, not these patterns, are what keep GitHub access read-only. Read-only GraphQL queries use POST, while REST writes and GraphQL mutations are forbidden. If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## See Also

- [Review Branch](../review-branch/README.md): review your own branch before opening a PR
- [Resolve Copilot PR Feedback](../resolve-copilot-pr-feedback/README.md): process Copilot's review comments on your PR
- [All plugins](../../README.md)
