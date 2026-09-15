---
name: create-deferred-issues
description: >-
  Find the concerns a unit of work raised and set aside (in the current
  session, in TODO and FIXME markers the branch adds, in the pull request body
  and review comments, and in out-of-scope sections of the plan or issue),
  propose them as one batch for the user to trim and edit, then file the
  approved set as GitHub issues linked back to their source. Use when the user
  says "create deferred issues", "file the deferred issues", "file issues for
  the follow-ups", "file issues for everything we set aside", "file the
  out-of-scope items", "what did we defer", or asks to track the concerns the
  current work left open, often just before "/pr". Requires the gh CLI to be
  installed and authenticated.
---

# Create Deferred Issues

Collect the concerns a unit of work set aside, propose them as one batch, and file the ones the user approves.

## Why This Skill Exists

While working, an agent regularly names a concern and sets it aside: a formatter no CI job runs, a timeout far above real run lengths, a bug that belongs to another repository. Each one then waits for the user to say "file that", one round trip per concern, usually attached to the request to open the pull request. This skill gathers them in one pass and files the approved set in another.

Two rules shape everything below:

- **The proposal is never skipped.** Filing without confirmation would turn every hedge in the session into an issue, which is worse than filing nothing.
- **Under-propose.** A missed deferral costs the user one manual `/create-issue`. A wrong one costs triage, and erodes trust in every later batch.

## Options

The user may provide these options inline:

- **--dry-run**: Collect and propose, then stop. File nothing and post nothing.
- **--no-comment**: File the approved issues, but skip the summary comment on the source pull request or issue.

## Parent Continuation Contract

When another skill invokes `create-deferred-issues`, that parent skill may provide an explicit continuation block immediately after the command:

```text
Parent continuation:
- Caller: <parent skill name>
- Resume target: <parent workflow step to resume>
- On completion: <what the parent does next when issues were filed, none were found, none were approved, or this was a dry run>
- On filing failure: <what the parent does next when any approved issue failed to file>
```

Honor this block as part of the invocation, with one exception: the proposal in step 4 still stops for the user. A continuation block governs what happens after the user answers, never whether they are asked.

Final output for a parent invocation must include:

```text
Deferred issues: <filed|none found|none approved|dry run|failure>
Filed: <none|full issue URL, title, destination visibility; ...>
Summary comment: <none|URL>
Caller resume target: <target from continuation block>
```

Report `failure` when any approved issue failed to file, even if others were filed, and list the ones that were. A compound instruction from the user ("file the deferred issues, then /pr") works the same way: report, then continue to the next step without asking again.

## Workflow

### 1. Establish Context

Run independent read-only probes in parallel. Fetches mutate `FETCH_HEAD`; keep each base fetch immediately followed by recording its immutable SHA before starting another fetch.

#### Repository

```bash
git remote
git remote get-url origin | sed -E 's#^[A-Za-z][A-Za-z0-9+.-]*://([^/@]*@)?([^/]+)/#\2/#; s#^[^/@]*@([^:]+):#\1/#; s#\.git$##'
```

The first command lists remote names only. The second removes URL userinfo and SCP-style SSH usernames, preserves a port in URI authorities, converts the remote to `HOST/OWNER/NAME`, and removes a trailing `.git` before printing it, so credentials never enter the tool transcript. Never run `git remote -v` or print an unsanitized remote URL. Use this normalized origin selector in later commands and reports.

Resolve the sanitized origin identity to a repository:

```bash
gh repo view <origin-selector> --json nameWithOwner,url,visibility,isArchived,isFork,parent,hasIssuesEnabled,defaultBranchRef
```

- Its `nameWithOwner` is the **default target** for filing. Select the repository explicitly for every `gh` call: use `--repo` where supported, the repository argument for `gh repo view`, an object's full URL when reading it, or the repository path and host for `gh api`. Source reads use the source repository; filing and tracker searches use the candidate's destination. Without an explicit repository, `gh` prefers a remote named `upstream`, so inside a fork a bare `gh issue create` files on the project that was forked.
- If the SSH host token is an alias, resolve its configured hostname with `ssh -G <alias>` before calling `gh`. Use the resulting hostname only when it is a GitHub host for which `gh` is authenticated. If the alias cannot be resolved, or its configured host cannot be authenticated, do not fall back to bare `owner/name`, because that silently selects GitHub.com. Mark origin unavailable and require a user-provided host-qualified selector for filing. On a host other than `github.com`, write targets as `HOST/OWNER/NAME` for `--repo`, and pass `--hostname HOST` to `gh api`.
- When the normalized origin selector came from an SSH alias, replace its host with the configured hostname returned by `ssh -G <alias>` before calling `gh`. If the alias cannot be resolved, use the unavailable-origin path rather than querying the alias as though it were a GitHub hostname.
- If `git remote` lists `upstream`, resolve its URL with the same sanitizer, including SSH alias resolution, then use `gh repo view <upstream-selector> --json nameWithOwner,url` to record its canonical host and repository. If the remote cannot be resolved, treat any candidate that could name it as third-party until its identity is established. Never print its unsanitized URL.
- Keep the host and `owner/name` as separate fields for every repository. In the examples, `<target>`, `<pr-repo>`, and `<source-repo>` are host-qualified selectors where needed; `<pr-owner>/<pr-name>` and `<source-owner>/<source-name>` are the host-free API paths. Never put a hostname after `repos/`.
- `parent` has no `nameWithOwner` field. Build the parent's name from `.parent.owner.login` and `.parent.name`.
- For the rest of this workflow, a **third-party repository** is any target whose owner differs from origin's owner, plus the fork's parent and the canonical repository identified by an `upstream` remote, even when both repositories have the same owner.
- Without an `origin`, there is no default target. In a Git checkout, still scan uncommitted changes, eligible untracked text files, and local plan and review documents; skip only the committed branch range whose base cannot be established. Outside a Git checkout, scan the session and documents it names. In either case retain destinations explicitly named there, and start only candidates without a named destination unresolved. Without an ownership baseline, require approval by number unless the session establishes that the target belongs to the user.

Treat every substituted value as shell data. Use an argument-list tool when available; otherwise single-quote each literal argument and encode an embedded apostrophe as `'\''` within that argument. For example, `--search 'runner'\''s timeout'` passes one literal phrase. Backticks and `$()` in source text must never become shell substitutions. Do not use `eval` or interpolate source text into double-quoted shell source.

#### Branch

```bash
git branch --show-current
```

If the output is empty (a detached HEAD) or names the default branch, there is no committed branch range to read. Still scan uncommitted changes, eligible untracked text files, and local documents, and say that the committed range was unavailable in the proposal.

#### Pull request

```bash
gh pr list --repo <target> --head <branch> --state open --limit 100 --json number,url,title,body,baseRefName,headRepository,closingIssuesReferences
```

Keep only a PR whose `headRepository.nameWithOwner` and host match origin's full repository identity, since `--head` matches the branch name in any fork, including another repository owned by the same account. If the head repository is unavailable, report that source as unresolved rather than guessing. Empty output means there is no open PR. Do not use `gh pr view <branch>` for this: it also returns a merged PR from an earlier branch that had the same name.

When origin is a fork and no PR was found, run the same query with `--repo <parent>`. A PR found there is a read-only source: its comments yield candidates, but it never receives the summary comment.

Record the PR's full URL, repository as `<pr-repo>`, and number together. Keep these separate from the default filing target, including when the PR lives in the parent.

#### Base

If a PR was found, its `baseRefName` is the base, and the repository containing that PR owns the base branch. Resolve its repository URL with `gh repo view <pr-repo> --json url`; a PR in a fork's parent must fetch its base from that parent, even if origin has a branch with the same name. Fetch that base and record the immutable commit immediately:

```bash
git fetch <pr-base-repository-url> refs/heads/<base> --quiet
git rev-parse FETCH_HEAD
```

Use that commit as `<base-sha>` in every scan below. Otherwise read where the branch was created:

```bash
git reflog show <branch> --format='%gs'
```

The last line reads like `branch: Created from <name>`. Strip any `refs/heads/`, `refs/remotes/origin/`, or `origin/` prefix from `<name>`, then accept it as the base only if all three hold, checked in order:

1. It is not the current branch.
1. `git ls-remote --heads origin <name>` prints a line. The command exits 0 either way, so judge by its output.
1. `git merge-base --is-ancestor origin/<name> origin/<default-branch>` exits non-zero, meaning the parent branch has not already merged. Fetch both first with `git fetch origin <default-branch> <name> --quiet`.

For this no-PR fallback, otherwise the base is the default branch and its repository is origin. Fetch the selected base from its owning repository, then immediately record the fetched commit:

```bash
git fetch <base-repository-url> refs/heads/<base> --quiet
git rev-parse FETCH_HEAD
```

Use that immutable commit as `<base-sha>` in every scan below. Record it before any later fetch replaces `FETCH_HEAD`; do not substitute `origin/<base>` or a local branch. Getting the base right matters: a stacked branch compared against the default branch would inherit its parent branch's markers and issue references.

#### Source issues

Collect the issues this branch addresses from all available sources, even when a PR exists:

1. The PR's `closingIssuesReferences`, when a PR was found. Preserve each reference's full URL and derive its host, repository, and number from that URL; a closing reference can name an issue in another repository. If a reference lacks its repository identity, resolve it from the PR's explicit closing text or report it as unavailable rather than assigning its number to origin.
1. Explicit source references in the PR body, including `Related to #N`. Bare references belong to `<pr-repo>`; preserve repository-qualified references and full URLs.
1. Issue numbers in the branch name (`feature/42-login`, `fix/issue-42`) and `#N` references in the branch's commit messages. When a PR exists, bare numbers belong to `<pr-repo>`; otherwise they belong to the default target only when one was established. With no PR and no default target, leave bare numbers unresolved and do not query an issue repository for them. Preserve an explicit repository or issue URL when one is supplied:

   ```bash
   git log --no-merges --format=%B <base-sha>..HEAD
   ```

References explicitly labelled as deferred follow-ups or already-filed concerns are duplicate evidence, not source issues. Deduplicate the remaining source references by host, repository, and issue number, then confirm each using its own repository:

```bash
gh issue view <n> --repo <source-repo> --json url,state,title,body
```

Drop any whose `url` contains `/pull/`, because `gh issue view` also resolves pull request numbers. Never search the tracker for source issues: a keyword match is not evidence that the branch addresses an issue.

Retain the returned URL, host, repository, and number as the source identity for body links, duplicate comparisons, and timeline reads. Equal numbers in different repositories are different issues. A failed source read is unavailable evidence, never a reason to retry the number against the filing target.

#### Source visibility

For every distinct repository supplying a PR, issue, code marker, document, or session concern, fetch and retain its canonical identity, URL, and visibility:

```bash
gh repo view <source-repo> --json nameWithOwner,url,visibility
```

Reuse origin's metadata only for sources in origin. Another repository's issue or PR needs its own lookup. Attach visibility to each source, not just to the filing destination. If a source cannot be identified or its visibility cannot be read, mark it unknown and treat its details as non-public when composing public text.

#### Labels

For the default target now, and for any other target once a candidate names it:

```bash
gh label list --repo <target> --json name,description --limit 200
```

### 2. Collect Candidates

Read `./references/deferral-signals.md` before judging any candidate. It defines a deferral, lists the phrasings and source shapes that mark one, and lists what looks like a deferral but is not.

For each candidate, record the concern in one sentence, every source it came from, and a link or location. Preserve each source's repository identity and visibility; one public source does not make another source's private details publishable.

#### Session

The conversation in context, from both sides: concerns the assistant named and set aside, and concerns the user parked. Work only from what is in context. If earlier turns were compacted into a summary, use what the summary retains and do not try to reconstruct the rest from transcript files.

#### Code markers the branch adds

```bash
git diff --name-only <base-sha>...HEAD
git diff --name-only HEAD
git ls-files --others --exclude-standard
```

The first command lists paths changed by branch commits, the second lists tracked working-tree changes, and the third lists untracked files. Before reading any diff or file contents, exclude secret-like paths (`.env`, `.env.*`, `credentials.json`, `*.pem`, `*.key`), symlinks, and binary files from all three source sets. Run the marker diff only for eligible regular text paths, then inspect only added lines matching the marker pattern. For eligible untracked files, search with a binary-skipping content search and return matching marker lines plus only the context needed to understand them. Do not read every untracked file in full, and do not inspect files without a matching marker. Report excluded source categories without their contents.

```bash
git diff --unified=0 -G '(^|[^A-Za-z0-9_])(TODO|FIXME|XXX|HACK)([^A-Za-z0-9_]|$)' <base-sha>...HEAD -- <eligible-tracked-paths>
git diff --unified=0 -G '(^|[^A-Za-z0-9_])(TODO|FIXME|XXX|HACK)([^A-Za-z0-9_]|$)' HEAD -- <eligible-working-tree-paths>
```

Three details in those commands are load-bearing:

- `-G` selects every file whose diff contains a matching line, then prints all of that file's changed lines. Re-apply the same pattern to each added (`+`) line and ignore everything else.
- For each added line, apply the marker syntax from `references/deferral-signals.md`: a marker counts only when it opens a comment or is followed by `:` or `(`. A prose mention or identifier such as `const TODO = ...` is not a marker.
- The pattern spells out its word boundaries. `\b` matches nothing under the regular expression engine git uses on macOS, so a pattern written with it returns an empty, reassuring result.
- The same boundaries keep placeholder templates such as `mktemp`'s `XXXXXX` from matching.

#### Pull request

When a PR was found:

```bash
gh pr view <n> --repo <pr-repo> --json body
gh api --paginate --hostname <pr-host> repos/<pr-owner>/<pr-name>/issues/<n>/comments --jq '.[] | {body, url: .html_url, author: .user.login}'
gh api --paginate --hostname <pr-host> repos/<pr-owner>/<pr-name>/pulls/<n>/reviews --jq '.[] | {body, url: .html_url, author: .user.login}'
gh api --paginate --hostname <pr-host> repos/<pr-owner>/<pr-name>/pulls/<n>/comments --jq '.[] | {id, in_reply_to_id, path, line, body, url: .html_url, author: .user.login, created_at, updated_at}'
```

The first returns the PR body. The three API calls return all pages of conversation comments, review bodies, and inline review comments respectively. Preserve comment IDs, reply-to IDs, and timestamps so replies can be associated with the correct finding. Look for replies that set a finding aside, and for review-feedback summaries, such as the one the `resolve-copilot-pr-feedback` skill posts, that carry a Deferred category.

#### Documents

- Plan files under `docs/plans/` and review documents under `docs/reviews/` that the branch changes or that are uncommitted or untracked:

  ```bash
  git diff --name-only <base-sha>...HEAD -- docs/plans docs/reviews
  git status --short -- docs/plans docs/reviews
  ```

  Also collect plan and review paths explicitly referenced by the session, PR, source issues, or branch commit messages, including files unchanged by this branch. Read each relevant document once and inspect its out-of-scope and follow-up sections. Review documents saved by the `review-branch` skill land in `docs/reviews/`.

- The body of each source issue, already fetched in step 1.

### 3. Filter and Deduplicate

Apply these in order.

1. **Drop what is not a deferral**, per the exclusions in `./references/deferral-signals.md`: concerns resolved later in the work, concerns the user declined, hedges with no concrete action, and the rest. When unsure whether something is a deferral at all, leave it out.
1. **Merge duplicates across sources.** A concern the session set aside and a `TODO` about the same thing become one candidate that carries both sources.
1. **Resolve each target.** Use the default target unless the deferral names another repository: an `owner/name`, a `HOST/OWNER/NAME` selector, a GitHub repository URL, or a repository the session already identified by name. For a URL, extract its host and owner/repository path, form a host-qualified selector, and use that selector for metadata, issue-list, and filing calls; never pass the full URL as `--repo`. Never guess from a vague description; propose the candidate with its target marked unresolved. Require the user to supply a destination only when neither a default nor an explicit target exists. Check each distinct resolved target:

   ```bash
   gh repo view <target> --json nameWithOwner,visibility,isArchived,hasIssuesEnabled
   ```

   Record its canonical repository identity, visibility, and third-party classification. An archived target, or one with issues disabled, moves the candidate to **Cannot file** with the reason. When origin is a fork whose issues are disabled, add that the user may retarget the item to the parent explicitly. Never retarget it yourself. If repository metadata cannot be read, keep eligibility unresolved and do not file until it can be checked.

   Load labels for this destination using step 1's label command. Do not reuse another repository's labels. For an unresolved target, skip target metadata, label lookup, and tracker search; mark it "target unresolved; not checked for duplicates" until an edit supplies the destination. Source evidence may still establish that the concern is tracked.

1. **Check disclosure in both directions.** For a public destination, compose the proposed title, description, and source context in general terms when any source is private, internal, or unknown. Omit that source's repository and service names, issue numbers and titles, branch names, links, paths, permalinks, and quotations. Use `Raised during related work.` as its context instead of a GitHub reference. State in the proposal that source details are omitted. Public summary comments must use the same publishable wording. If the concern cannot be described without exposing those details, leave the item unfileable until the user supplies publishable wording.

   A private, internal, or unknown destination must also stay out of comments or PR bodies in a public repository. Retain its full issue URL and visibility in the local report and parent handoff, but omit its identity and title from public summaries. Step 6 applies this check to each filed issue and the receiving repository before posting.

1. **Remove what is already tracked.** A candidate is tracked when any of these holds:
   - Its own text names an issue (`#N`, an issue URL, "tracked in", "filed as") other than the branch's source issues. Resolve a bare number in the repository the text came from; compare full repository identities and numbers, not numbers alone. If that repository is unknown, keep the reference unresolved rather than assuming the destination. Naming a source issue alone does not establish that a separate deferral is tracked.
   - An issue was filed for it earlier in this session.
   - An issue that links back to the source covers the same concern. Read the cross-references of the PR and of each source issue once, then match candidates against the list:

     ```bash
     gh api --paginate --hostname <source-host> repos/<source-owner>/<source-name>/issues/<n>/timeline --jq '.[] | select(.event == "cross-referenced") | .source.issue | select(.html_url | contains("/issues/")) | {number, title, state, url: .html_url}'
     ```

     For the PR, use its recorded host, owner, repository name, and number; for each source issue, use that issue's recorded identity. Preserve each result's full URL rather than treating its number as local to the source or destination. The endpoint accepts a pull request number too. When a filed issue can link its source, this read finds an earlier run's filings whether or not that run posted a summary comment. The list also holds every other issue that merely mentions the source, such as a related proposal, so a listed issue tracks a candidate only when it passes the same distinctive-words test as a search hit below.

   - A review document on the branch records it as filed.
   - A tracker search in the candidate's resolved destination finds it:

     ```bash
     gh issue list --repo <target> --search '<distinctive words>' --state all --limit 5 --json number,title,state,url
     ```

     Judge each hit on its distinctive words, the ones naming the specific subject, and not on generic tracker vocabulary such as `add`, `fix`, `update`, or `skill`. A clear match moves the candidate to **Already tracked**. An ambiguous one stays in the batch with a "possible duplicate of #N" note, and the user decides.

   When no source timeline link can exist (there is no source PR or issue, the destination is on another host, or disclosure rules omit its reference), use the destination issue's published title and description as the duplicate record. Search using those publishable words and also inspect the destination's newest issues directly with `gh issue list --repo <target> --state all --limit 20 --json number,title,body,url`, since the search index can lag. Read plausible matches before deciding. Retain every filed URL in the local report and session. Say in the proposal that no source timeline link is available, and disclose any failed duplicate lookup before approval; do not claim timeline-based duplicate coverage for these items.

A long batch is a sign that the filter is too loose. Apply it again before proposing.

### 4. Propose the Batch

This step is never skipped: not under `--dry-run`, not with a parent continuation block, and not because the user said "file them all" before seeing the batch.

If no candidate survived, report which sources were scanned and which were unavailable (no PR, a detached HEAD, no `origin`), then stop. With a parent continuation block, report `Deferred issues: none found` and continue per the block.

Otherwise, present the batch:

```markdown
## Deferred concerns: 2 proposed

### 1. Run shfmt in the lint workflow

- **Repository:** owner/name
- **Labels:** enhancement
- **Source:** session; TODO at `bin/release:48`
- The formatter is configured locally, but no CI job runs it, so unformatted scripts merge.
  Done when the lint workflow fails on a formatting diff.

### 2. Pin the runner image in the shared CI actions

- **Repository:** owner/ci-actions (third-party: approve by number)
- **Labels:** none fit
- **Source:** PR review comment (link)
- The shared workflow floats on the latest runner image, which changed the toolchain under this repository twice.
  Done when the image is pinned and bumped deliberately.

### Already tracked

- Lower the CI job timeouts: #88

### Cannot file

- Update the host bindings: owner/bindings is archived

Reply with `file all`, `file 1 2`, `drop 2`, `edit 2: <change>`, or `none`.
```

Rules for the proposal and for reading the reply:

- **Third-party targets** are marked on their item. `file all` never covers one; it is filed only when the reply names its number.
- **Ask in plain text**, not through a structured multiple-choice question. A batch can exceed the options such a question allows, and edits need free text.
- **Numbers are fixed** for the whole exchange. After `drop 2`, item 3 is still item 3.
- **An unambiguous approval of the whole batch** ("yes", "file them") counts as `file all`.
- **Apply drops and edits.** Before filing, revalidate any item whose destination, concern, title, proposed body, label selection, or other publishable content changed, including an unresolved target the user supplied. Repeat the affected step 3 checks: target eligibility and third-party classification, destination label lookup and selection, duplicate checks, source-to-destination visibility, and the status-label exclusion. Source identities stay attached to their original repositories; never replace them with the new destination. Reuse source timeline reads only when the sources are unchanged, and match them against the revised concern. Treat the revalidated item as a new proposal: it needs approval again whenever any check changes the content, labels, disclosure, or duplicate status.
- **Honor approval of the revised item.** If the reply only edits, or is unclear about which items it approves, present the checked revision and ask again. An edit with approval may proceed only if revalidation leaves the approved content and destination intact. If checks add a duplicate warning, change labels or source disclosure, or otherwise materially change the item, re-present it for approval. An already-tracked or unfileable item is reported in the corresponding list rather than filed. Preserve its number if the user revises it again. Reapply approval by number to third-party destinations; whole-batch approval does not cover them.
- **`none`** files nothing. Report `none approved`.

**If `--dry-run` was specified**, stop after presenting the batch. Otherwise, stop and wait for the reply.

### 5. File the Approved Set

Read `./references/batch-filing.md`, then file each approved item in proposal order, one at a time, following its title, body, label, and per-issue sequence rules. Never file in parallel.

Only file an item whose current destination is resolved and eligible, whose affected checks are complete (or whose permitted duplicate/label lookup failure was disclosed), and whose current proposal is approved. Checks or approval for an earlier version of the item do not carry over to a materially changed proposal.

If an issue fails to file, continue with the rest and report it. Before retrying a failed item, confirm it did not land after all:

```bash
gh issue list --repo <target> --state all --limit 20 --json number,title,createdAt
```

This lists the newest issues directly rather than through the search index, which can lag behind an issue created moments earlier.

### 6. Cross-Reference

When a source PR or issue exists and disclosure permits its reference, the body links it. Then post one summary comment, as described in `./references/batch-filing.md`, on the first of these that exists:

1. The open PR, when it lives in the default target.
1. The first source issue in the default target.

Before posting, compare each filed destination's visibility with the receiving repository's visibility. In a public receiver, include only issues in public destinations, with publishable titles. If either visibility is unknown, omit that issue from the comment until it can be verified. Keep private destination URLs, repository names, issue numbers, and titles in the local report only. If every entry is omitted, post nothing and explain why locally.

If neither receiver exists, post nothing and say so in the report. Never comment on a third-party repository. Skip this step under `--no-comment`, or when nothing was filed.

### 7. Report

```text
## Deferred Issues

| #   | Title                                         | Repository       | Result     |
| --- | --------------------------------------------- | ---------------- | ---------- |
| 1   | Run shfmt in the lint workflow                | owner/name       | Filed #101 |
| 2   | Pin the runner image in the shared CI actions | owner/ci-actions | Dropped    |

Already tracked: Lower the CI job timeouts (#88)
Cannot file: Update the host bindings (owner/bindings is archived)
Summary comment: <URL, or none and why>
```

Include each filed issue's full URL and destination visibility in this local report, including entries omitted from a public summary. A parent must retain that identity and check visibility before publishing a reference elsewhere.

Then suggest the next step. When no PR exists yet, suggest `/pr`, which lists publishable filed issues under a Follow-ups section of the PR body and excludes all filed follow-ups from its closing references. With a parent continuation block, give the parent output instead and continue per the block.

## Error Handling

- **`gh` missing or unauthenticated**: Instruct the user to install it from https://cli.github.com/ and run `gh auth login`, then stop.
- **No `origin`**: In a Git checkout, scan uncommitted changes, eligible untracked text files, and local plan and review documents; skip only the committed range whose base cannot be established. Keep explicitly named destinations and leave only candidates without one unresolved. Outside a Git checkout, scan the session and documents it names, retaining explicitly named destinations.
- **A duplicate search or timeline read fails**: Propose the affected candidates with a "not checked for duplicates" note.
- **The label list fails**: File without labels and report that labels were skipped.
- **An issue fails to file**: Continue with the rest, and check the newest-issues listing before any retry so a retry cannot duplicate an issue that did land.
- **The summary comment fails**: The issues stay filed. Report the failure and the list the comment would have carried.
- **A third-party target**: Never filed without approval by number, and never commented on.
