# Create Deferred Issues

Scan the session, branch, and pull request for concerns set aside as out of scope, propose them as one batch, and file the approved ones as GitHub issues.

**Type:** Skill
**Trigger:** `/create-deferred-issues`
**Requires:** [`gh`](https://cli.github.com/) (authenticated)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

While working, an agent regularly names a concern and sets it aside: a formatter no CI job runs, job timeouts far above real run lengths, a bug that belongs to another repository. Each one then waits for someone to say "file that", one request per concern, usually attached to the request to open the pull request. This skill collects all of them in one pass.

It reads four sources:

1. **The session**: concerns either side of the conversation set aside.
1. **Code markers**: `TODO`, `FIXME`, `XXX`, and `HACK` lines the branch adds, including uncommitted changes and eligible untracked text files. Secret-like paths, symlinks, and binary files are excluded from untracked content reads.
1. **The pull request**: its body, conversation comments, review bodies, and inline review comments.
1. **Documents**: out-of-scope sections of plans and review documents the branch touches or the work references, and the bodies of the issues the branch addresses.

It then drops what is not really a deferral (hedges, rejected alternatives, concerns fixed later in the work, concerns you declined) and what is already tracked, which it finds through the source's cross-reference timeline and a search of the tracker. It errs toward proposing too little: a missed concern costs one manual `/create-issue`, while a wrong one costs triage.

### The proposal is not optional

Nothing is filed until you have seen the batch. Each proposed issue shows its title, target repository, labels, source, and a two-line body sketch, followed by what was already tracked and what cannot be filed. Reply with `file all`, `file 1 3`, `drop 2`, `edit 2: <change>`, or `none`. Item numbers never shift during the exchange. Editing a destination or concern repeats the affected repository, duplicate, label, and visibility checks; a material change from those checks is presented for approval before filing. This gate holds even when another skill invokes this one through a parent continuation block.

### Filing and cross-referencing

Approved issues are filed one at a time, in order. Each body is written to a temporary file, the same pattern [Create Issue](../create-issue/README.md) uses, and checked after creation. Labels come only from those the repository already has, and never from status or automation labels. When disclosure permits it, each body links back to its source pull request or issue, and one summary comment lists the publishable filings. Without a source link, duplicate checks use the destination's published concern and newest-issues listing. The local report retains every filed URL and its destination visibility.

### Repositories

Every `gh` call selects its repository explicitly. Filing defaults to the repository `origin` points at, because `gh` otherwise prefers an `upstream` remote and would file on the project you forked. Source issues and PR timelines are read in their own repositories, while duplicate searches run in each concern's resolved destination. A concern that names another repository is proposed against that repository. A repository with a different owner, including a fork's parent, is marked third-party: it is filed to only when you approve that item by number, and it never receives a summary comment. Archived repositories and repositories with issues disabled are listed as unfileable rather than attempted. Visibility is checked for every source and destination: private-source details are omitted from public titles and bodies, and private-destination references are omitted from public summary comments and PR bodies.

### Before /pr

Run it before opening the pull request. [PR](../pr/README.md) lists publishable issues filed this way under a `## Follow-ups` section and excludes every follow-up from its closing references using the full repository identity. It also checks existing commit messages and stops if one already contains a closing keyword for a follow-up.

## Usage

```text
/create-deferred-issues
/create-deferred-issues --dry-run
/create-deferred-issues --no-comment
```

| Option         | Description                                                 |
| -------------- | ----------------------------------------------------------- |
| `--dry-run`    | Collect and propose, then stop without filing or commenting |
| `--no-comment` | File the approved issues, but skip the summary comment      |

## Recommended Permissions

This skill runs git and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git remote)", "Bash(git remote *)", "Bash(ssh -G *)", "Bash(sed *)", "Bash(git branch *)", "Bash(git reflog show *)", "Bash(git ls-remote --heads *)", "Bash(git fetch *)", "Bash(git rev-parse *)", "Bash(git merge-base *)", "Bash(git diff *)", "Bash(git log *)", "Bash(git status*)", "Bash(git ls-files *)", "Bash(gh repo view *)", "Bash(gh pr list *)", "Bash(gh pr view *)", "Bash(gh issue view *)", "Bash(gh issue list *)", "Bash(gh label list *)", "Bash(gh api --paginate --hostname * repos/*/pulls/*/comments*)", "Bash(gh api --paginate --hostname * repos/*/pulls/*/reviews*)", "Bash(gh api --paginate --hostname * repos/*/issues/*/comments*)", "Bash(gh api --paginate --hostname * repos/*/issues/*/timeline*)", "Bash(gh issue create *)", "Bash(gh issue edit *)", "Bash(gh pr comment *)", "Bash(gh issue comment *)", "Bash(mktemp -u /tmp/gh-issue-body-*)", "Bash(rm -f /tmp/gh-issue-body-*)", "Bash(mktemp -u /tmp/gh-comment-body-*)", "Bash(rm -f /tmp/gh-comment-body-*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

The write rules (`gh issue create`, `gh issue edit`, and the two comment commands) are safe to allow because the skill never reaches them before you approve the batch. Leave them out if you would rather confirm each write as well. The API rules include `--hostname` so the same command shape works on GitHub.com and GitHub Enterprise hosts.

## Examples

- "file the deferred issues": scans all four sources, proposes the batch, and files what you approve
- "what did we defer?": same behavior; reply `none` to see the list without filing anything
- "file issues for the follow-ups, then /pr": files the approved batch, then opens the pull request with those issues listed under Follow-ups
- "/create-deferred-issues --dry-run": shows the batch it would propose, then stops

## See Also

- [Create Issue](../create-issue/README.md): file a single issue; this skill's filing mechanics follow its pattern
- [PR](../pr/README.md): open the pull request, listing the filed issues as follow-ups
- [Review Branch](../review-branch/README.md): its saved review documents are one of the sources read
- [Resolve Copilot PR Feedback](../resolve-copilot-pr-feedback/README.md): its summary comments record the deferred findings this skill picks up
- [Address Issue](../address-issue/README.md): work on an issue this skill filed
- [All plugins](../../README.md)
