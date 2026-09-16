# Batch Filing

How to file the approved batch and post the summary comment. The per-issue sequence mirrors the `create-issue` skill's tmpfile pattern. Where the two ever disagree about those mechanics, `create-issue` is the source to follow.

## Title

- **Imperative and specific**: "Run shfmt in the lint workflow", not "shfmt".
- **Under 70 characters**, with no trailing period, and no type prefix unless the target repository's existing issue titles use one.
- **Pass the approved title unchanged as one literal argument.** Inside a double-quoted shell argument, a backtick, `$(...)`, or `$NAME` is expanded, so a title that names code in backticks would run that code and file a different title. Single quotes pass all of them through unchanged; encode any embedded apostrophe as `'\''`, as for labels. Do not rephrase a title after approval. If a disclosure or other validation change requires different title text, return the revised item for approval.
- **Publishable in the destination**: use the title approved after the visibility check. A public title must not identify a private or unknown source, service, repository, or finding through details omitted from its body.

## Body

Write for a reader who never saw the session.

```markdown
## Summary

<The concern: what is wrong or missing, and the evidence for it. Why it was set aside. What done looks like.>

## Context

Deferred from #<pr> (<pr title>).

<Link to the source: the review comment, a permalink to the code marker, or the plan path.>
```

- **With no PR**, the context line reads `Raised while working on #<issue>`, or names the branch when there is no source issue either.
- **Across repositories**, write `owner/name#N`, using the source's recorded repository and number. Use its full URL across hosts. A bare `#N` resolves in the target repository, not the source. Retargeting the new issue does not change the identity of the source it references.
- **For a code marker**, link a permalink using the source's recorded host and repository at a commit its remote has: `https://<source-host>/<owner>/<name>/blob/<sha>/<path>#L<line>`. Check with `git branch -r --contains <sha>` and verify that the containing remote belongs to that source. When the commit is not pushed there, write `<path>:<line>` as text rather than a link that would not resolve.
- **Link when a source exists and disclosure permits it.** A source PR or issue reference creates the timeline evidence used for duplicate detection. With no source PR or issue, or when its identity must be omitted, rely on step 3's destination search and newest-issues listing using the published concern, and retain the filed URL locally. Never invent a source reference or promise a timeline entry in these cases.
- **Summarize.** Never paste session text wholesale, and never include secrets, tokens, local absolute paths, or machine names. The target may be public even when the conversation was not.
- **Visibility overrides the context template.** When the target is public and a source is private, internal, or unknown, use `Raised during related work.` instead of `Deferred from #N`, `Raised while working on #N`, or a branch name. Omit that source's identity, service names, issue numbers and titles, links, paths, permalinks, and quotations from both title and body. No bare or qualified issue reference may reconstruct an omitted private source. Use only the generalized wording approved in the proposal.

## Labels

- **Existing labels only**, from `gh label list` for that target repository. Never create a label.
- **Prefer one type label** (`bug`, `enhancement`, `documentation`, `maintenance`, or the repository's equivalent) plus a topical label only when one obviously matches. No label is better than a poor fit.
- **Never apply status, triage-outcome, or automation-owned labels**: `in progress`, `duplicate`, `wontfix`, `invalid`, `dependencies`, or any label a workflow or bot manages.
- **Pass each name as one literal argument**, since labels may contain spaces or shell syntax. Single-quote it and encode each embedded apostrophe as `'\''`: `--label 'team'\''s area'` passes the existing label `team's area` unchanged. Do not rename an existing label to avoid quoting it.

## Per-Issue Sequence

Each step below is its own tool call, made in order.

1. Generate an unused path:

   ```bash
   mktemp -u /tmp/gh-issue-body-XXXXXX
   ```

   The `-u` flag is required. Plain `mktemp` creates an empty file at the path it prints, and the Write tool refuses to overwrite a file it has not read, so the write would fail.

1. Write the body to that exact path with the Write tool.

1. Once the Write has returned, create the issue in a separate call:

   ```bash
   gh issue create --repo <target> --title '<title>' --body-file <path> --label '<label>'
   ```

   Use the destination's recorded host-qualified selector for `<target>`. Repeat `--label` for a second label, and omit it when none fit. Never batch the Write and `gh issue create` into one message. `gh` reads the body file when it starts, so a parallel batch can open the issue with an empty body, and the command still succeeds and prints a URL.

1. Only if `gh issue create` printed an issue URL, confirm the body landed:

   ```bash
   gh issue view <issue-url> --json body --jq '.body | length'
   ```

   If the length is `0`, re-write the file with the Write tool, then run `gh issue edit <issue-url> --body-file <path>` as a separate call and check again. Never substitute a URL from an earlier item.

1. Remove the file in its own call, whether creation succeeded or failed:

   ```bash
   rm -f <path>
   ```

   Do not chain the cleanup onto `gh issue create` with an exit-status idiom such as `status=$?`. In zsh, `status` is a read-only variable, and the assignment fails in a way that reports a successful creation as a failure.

1. Record the issue number, full URL, title, host, repository, and destination visibility for the local report and parent handoff. Include it in the summary comment only when the receiving repository's visibility permits it.

**If `gh issue create` fails**, inspect the target's newest issues with `gh issue list --repo <target> --state all --limit 20 --json number,title,body,url,createdAt` and read plausible matches. An error can occur after GitHub accepted creation. If a matching issue was created by this attempt, verify and record its existing URL rather than creating another. If a match cannot be attributed to this attempt, return the concern to duplicate review. If the lookup fails or absence cannot be established, leave the item failed and do not retry automatically.

**For a label failure with no matching creation**, refresh the destination's labels and return the item to the proposal step with the proposed label change. Do not automatically remove approved labels and file. A retry requires renewed approval of the revised proposal and the main workflow's fresh pre-write checks. After approval, generate a new unique body-file path, write the approved body, create in a separate call using the approved labels, then remove the retry file in its own call. The original file was cleaned up by the normal sequence.

## Summary Comment

One comment, posted after every approved item has been attempted, listing only the issues this run filed whose identities may be published in the receiving repository. Reuse step 6's visibility check: omit private or internal destinations from a public receiver and omit entries with unknown destination or receiver visibility. If no entries can be published, skip the comment and report the omitted entries locally.

```markdown
<!-- create-deferred-issues -->

Filed follow-up issues for concerns set aside in this work:

- #101 Run shfmt in the lint workflow
- owner/ci-actions#7 Pin the runner image in the shared CI actions
```

Use a full issue URL for a destination on another host. Titles must meet the receiving repository's disclosure rules too; never copy private details from the local report into a public comment.

Use the same tmpfile sequence, with its own path:

1. `mktemp -u /tmp/gh-comment-body-XXXXXX`.
1. Write the comment body to that path.
1. In a separate call, on the PR:

   ```bash
   gh pr comment <number> --repo <receiver> --body-file <path>
   ```

   Or on the source issue:

   ```bash
   gh issue comment <number> --repo <receiver> --body-file <path>
   ```

   `<receiver>` is the host-qualified repository selector recorded for the source PR or issue, not the destination of the most recent filing.

1. `rm -f <path>`, in its own call.

A later run posts a new comment listing only what it filed, and never edits an earlier one. The marker lets a reader, or a later run, recognize the comment, but duplicate detection does not depend on it: the timeline read in the skill's step 3 finds every issue that links back to the source, whether or not a comment was posted.
