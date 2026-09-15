# Batch Filing

How to file the approved batch and post the summary comment. The per-issue sequence mirrors the `create-issue` skill's tmpfile pattern. Where the two ever disagree about those mechanics, `create-issue` is the source to follow.

## Title

- **Imperative and specific**: "Run shfmt in the lint workflow", not "shfmt".
- **Under 70 characters**, with no trailing period, and no type prefix unless the target repository's existing issue titles use one.
- **No backticks.** Issue titles do not render Markdown, and inside a double-quoted shell argument a backtick starts command substitution, so the title that reaches GitHub would not be the one written.
- **Single-quoted** on the command line. Rephrase a title that would need an apostrophe rather than escaping it.

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
- **Across repositories**, write `owner/name#N`. A bare `#N` resolves in the target repository, not the source.
- **For a code marker**, link a permalink at a commit the remote has: `https://github.com/<owner>/<name>/blob/<sha>/<path>#L<line>`. Check with `git branch -r --contains <sha>`. When the commit is not pushed, write `<path>:<line>` as text rather than a link that would not resolve.
- **The source link is load-bearing.** It puts the new issue on the source's timeline, which is how a later run recognizes it as already tracked.
- **Summarize.** Never paste session text wholesale, and never include secrets, tokens, local absolute paths, or machine names. The target may be public even when the conversation was not.
- **Visibility.** When the target is public and the source repository is private, leave out every link, path, permalink, and quotation from the source repository, and describe the concern in general terms.

## Labels

- **Existing labels only**, from `gh label list` for that target repository. Never create a label.
- **Prefer one type label** (`bug`, `enhancement`, `documentation`, `maintenance`, or the repository's equivalent) plus a topical label only when one obviously matches. No label is better than a poor fit.
- **Never apply status, triage-outcome, or automation-owned labels**: `in progress`, `duplicate`, `wontfix`, `invalid`, `dependencies`, or any label a workflow or bot manages.
- **Single-quote each name**, since labels may contain spaces: `--label 'good first issue'`.

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
   gh issue create --repo <owner/name> --title '<title>' --body-file <path> --label '<label>'
   ```

   Repeat `--label` for a second label, and omit it when none fit. Never batch the Write and `gh issue create` into one message. `gh` reads the body file when it starts, so a parallel batch can open the issue with an empty body, and the command still succeeds and prints a URL.

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

1. Record the issue number, URL, title, and repository for the report and the summary comment.

**If `gh issue create` fails on a label**, list the target's newest issues (`gh issue list --repo <owner/name> --state all --limit 20 --json number,title,createdAt`) to confirm nothing was created, then file again without `--label` and report which labels were skipped.

## Summary Comment

One comment, posted after every approved item has been attempted, listing only the issues this run filed:

```markdown
<!-- create-deferred-issues -->

Filed follow-up issues for concerns set aside in this work:

- #101 Run shfmt in the lint workflow
- owner/ci-actions#7 Pin the runner image in the shared CI actions
```

Use the same tmpfile sequence, with its own path:

1. `mktemp -u /tmp/gh-comment-body-XXXXXX`.
1. Write the comment body to that path.
1. In a separate call, on the PR:

   ```bash
   gh pr comment <number> --repo <owner/name> --body-file <path>
   ```

   Or on the source issue:

   ```bash
   gh issue comment <number> --repo <owner/name> --body-file <path>
   ```

1. `rm -f <path>`, in its own call.

A later run posts a new comment listing only what it filed, and never edits an earlier one. The marker lets a reader, or a later run, recognize the comment, but duplicate detection does not depend on it: the timeline read in the skill's step 3 finds every issue that links back to the source, whether or not a comment was posted.
