---
name: create-deferred-issues
description: >-
  Scan the session, branch, and pull request for concerns set aside as out of
  scope, propose them as one batch, and file the approved ones as GitHub issues.
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
Filed: <none|#N title (owner/name), ...>
Summary comment: <none|URL>
Caller resume target: <target from continuation block>
```

Report `failure` when any approved issue failed to file, even if others were filed, and list the ones that were. A compound instruction from the user ("file the deferred issues, then /pr") works the same way: report, then continue to the next step without asking again.

## Workflow

### 1. Establish Context

Everything in this step is read-only. Run independent commands in parallel.

#### Repository

```bash
git remote get-url origin
git remote -v
```

Resolve the origin URL to a repository:

```bash
gh repo view <origin-url> --json nameWithOwner,visibility,isArchived,isFork,parent,hasIssuesEnabled,defaultBranchRef
```

- Its `nameWithOwner` is the **default target**. Pass a target explicitly as `--repo` on every `gh` call in this skill. Without `--repo`, `gh` picks the base repository itself and prefers a remote named `upstream`, so inside a fork a bare `gh issue create` files on the project that was forked.
- If `gh` cannot resolve the URL (an SSH host alias such as `git@work-github:owner/name.git`, for example), take `owner/name` from the URL's path and run `gh repo view` with that instead. On a host other than `github.com`, write targets as `HOST/OWNER/NAME` for `--repo`, and pass `--hostname HOST` to `gh api`.
- `parent` has no `nameWithOwner` field. Build the parent's name from `.parent.owner.login` and `.parent.name`.
- For the rest of this workflow, a **third-party repository** is any target whose owner differs from origin's owner, plus the fork's parent and the repository an `upstream` remote points at, whoever owns them.
- With no `origin`, or outside a git repository, there is no default target. Scan only the session, and start every candidate's target as unresolved.

#### Branch

```bash
git branch --show-current
```

If the output is empty (a detached HEAD) or names the default branch, there is no branch work to read. Scan only the session and the documents it names, and say so in the proposal.

#### Pull request

```bash
gh pr list --repo <target> --head <branch> --state open --json number,url,title,body,baseRefName,headRepositoryOwner,closingIssuesReferences
```

Keep only a PR whose `headRepositoryOwner.login` is origin's owner, since `--head` matches the branch name in any fork. Empty output means there is no open PR. Do not use `gh pr view <branch>` for this: it also returns a merged PR from an earlier branch that had the same name.

When origin is a fork and no PR was found, run the same query with `--repo <parent>`. A PR found there is a read-only source: its comments yield candidates, but it never receives the summary comment.

#### Base

If a PR was found, its `baseRefName` is the base. Otherwise read where the branch was created:

```bash
git reflog show <branch> --format='%gs'
```

The last line reads like `branch: Created from <name>`. Strip any `refs/heads/`, `refs/remotes/origin/`, or `origin/` prefix from `<name>`, then accept it as the base only if all three hold, checked in order:

1. It is not the current branch.
1. `git ls-remote --heads origin <name>` prints a line. The command exits 0 either way, so judge by its output.
1. `git merge-base --is-ancestor origin/<name> origin/<default-branch>` exits non-zero, meaning the parent branch has not already merged. Fetch both first with `git fetch origin <default-branch> <name> --quiet`.

Otherwise the base is the default branch. Then fetch it and compare against the remote copy, never a local base branch that may be stale:

```bash
git fetch origin <base> --quiet
```

Getting the base right matters: a stacked branch compared against the default branch would inherit its parent branch's markers and issue references.

#### Source issues

The issues this branch addresses:

1. The PR's `closingIssuesReferences`, when a PR was found.
1. Otherwise, issue numbers in the branch name (`feature/42-login`, `fix/issue-42`) and `#N` references in the branch's commit messages:

   ```bash
   git log --no-merges --format=%B origin/<base>..HEAD
   ```

Confirm each number:

```bash
gh issue view <n> --repo <target> --json url,state,title,body
```

Drop any whose `url` contains `/pull/`, because `gh issue view` also resolves pull request numbers. Never search the tracker for source issues: a keyword match is not evidence that the branch addresses an issue.

#### Labels

For the default target now, and for any other target once a candidate names it:

```bash
gh label list --repo <target> --json name,description --limit 200
```

### 2. Collect Candidates

Read `./references/deferral-signals.md` before judging any candidate. It defines a deferral, lists the phrasings and source shapes that mark one, and lists what looks like a deferral but is not.

For each candidate, record the concern in one sentence, the source it came from, and a link or location.

#### Session

The conversation in context, from both sides: concerns the assistant named and set aside, and concerns the user parked. Work only from what is in context. If earlier turns were compacted into a summary, use what the summary retains and do not try to reconstruct the rest from transcript files.

#### Code markers the branch adds

```bash
git diff --unified=0 -G '(^|[^A-Za-z0-9_])(TODO|FIXME|XXX|HACK)([^A-Za-z0-9_]|$)' origin/<base>...HEAD
git diff --unified=0 -G '(^|[^A-Za-z0-9_])(TODO|FIXME|XXX|HACK)([^A-Za-z0-9_]|$)' HEAD
git ls-files --others --exclude-standard
```

The first covers the branch's commits, the second uncommitted changes, and the third lists untracked files, which neither diff shows. Read untracked files in full.

Three details in those commands are load-bearing:

- `-G` selects every file whose diff contains a matching line, then prints all of that file's changed lines. Re-apply the same pattern to each added (`+`) line and ignore everything else.
- The pattern spells out its word boundaries. `\b` matches nothing under the regular expression engine git uses on macOS, so a pattern written with it returns an empty, reassuring result.
- The same boundaries keep placeholder templates such as `mktemp`'s `XXXXXX` from matching.

#### Pull request

When a PR was found:

```bash
gh pr view <n> --repo <pr-repo> --json body,comments,reviews
gh api --paginate repos/<pr-repo>/pulls/<n>/comments --jq '.[] | {path, line, body, url: .html_url, author: .user.login}'
```

The first returns the body, the conversation comments, and the review bodies. The second returns the inline review comments as one object per line across every page. Look for replies that set a finding aside, and for review-feedback summaries, such as the one the `resolve-copilot-pr-feedback` skill posts, that carry a Deferred category.

#### Documents

- Plan files under `docs/plans/` and review documents under `docs/reviews/` that the branch changes or that are uncommitted or untracked:

  ```bash
  git diff --name-only origin/<base>...HEAD -- docs/plans docs/reviews
  git status --short -- docs/plans docs/reviews
  ```

  Read their out-of-scope sections. Review documents saved by the `review-branch` skill land in `docs/reviews/`.

- The body of each source issue, already fetched in step 1.

### 3. Filter and Deduplicate

Apply these in order.

1. **Drop what is not a deferral**, per the exclusions in `./references/deferral-signals.md`: concerns resolved later in the work, concerns the user declined, hedges with no concrete action, and the rest. When unsure whether something is a deferral at all, leave it out.
1. **Merge duplicates across sources.** A concern the session set aside and a `TODO` about the same thing become one candidate that carries both sources.
1. **Remove what is already tracked.** A candidate is tracked when any of these holds:
   - Its own text names an issue (`#N`, an issue URL, "tracked in", "filed as") other than the branch's source issues. Those close with this work, so naming them tracks nothing.
   - An issue was filed for it earlier in this session.
   - An issue that links back to the source covers the same concern. Read the cross-references of the PR and of each source issue once, then match candidates against the list:

     ```bash
     gh api --paginate repos/<target>/issues/<n>/timeline --jq '.[] | select(.event == "cross-referenced") | .source.issue | {number, title, state, url: .html_url}'
     ```

     The endpoint accepts a pull request number too. Every issue this skill files links its source, so this read finds an earlier run's filings whether or not that run posted a summary comment. The list also holds every other issue that merely mentions the source, such as a related proposal, so a listed issue tracks a candidate only when it passes the same distinctive-words test as a search hit below.

   - A review document on the branch records it as filed.
   - A tracker search finds it:

     ```bash
     gh issue list --repo <target> --search "<distinctive words>" --state all --limit 5 --json number,title,state,url
     ```

     Judge each hit on its distinctive words, the ones naming the specific subject, and not on generic tracker vocabulary such as `add`, `fix`, `update`, or `skill`. A clear match moves the candidate to **Already tracked**. An ambiguous one stays in the batch with a "possible duplicate of #N" note, and the user decides.

1. **Resolve each target.** Use the default target unless the deferral names another repository: an `owner/name`, a URL, or a repository the session already identified by name. Never guess from a vague description; propose the candidate with its target marked unresolved. Check each distinct target once:

   ```bash
   gh repo view <target> --json nameWithOwner,visibility,isArchived,hasIssuesEnabled
   ```

   An archived target, or one with issues disabled, moves the candidate to **Cannot file** with the reason. When origin is a fork whose issues are disabled, add that the user may retarget the item to the parent explicitly. Never retarget it yourself.

1. **Check visibility.** When a public target receives a candidate whose source is a private repository, its body must carry no link, path, permalink, or quotation from that repository. Say so on the item.

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
- **Apply drops and edits.** If the reply also approves, file. If it only edits, or is unclear about which items it means, present the revised batch and ask again.
- **`none`** files nothing. Report `none approved`.

**If `--dry-run` was specified**, stop after presenting the batch. Otherwise, stop and wait for the reply.

### 5. File the Approved Set

Read `./references/batch-filing.md`, then file each approved item in proposal order, one at a time, following its title, body, label, and per-issue sequence rules. Never file in parallel.

If an issue fails to file, continue with the rest and report it. Before retrying a failed item, confirm it did not land after all:

```bash
gh issue list --repo <target> --state all --limit 20 --json number,title,createdAt
```

This lists the newest issues directly rather than through the search index, which can lag behind an issue created moments earlier.

### 6. Cross-Reference

Every body links its source, which puts the new issue on the source's timeline. Then post one summary comment, as described in `./references/batch-filing.md`, on the first of these that exists:

1. The open PR, when it lives in the default target.
1. The first source issue in the default target.

If neither exists, post nothing and say so in the report. Never comment on a third-party repository. Skip this step under `--no-comment`, or when nothing was filed.

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

Then suggest the next step. When no PR exists yet, suggest `/pr`, which lists the filed issues under a Follow-ups section of the PR body and keeps them out of its closing references. With a parent continuation block, give the parent output instead and continue per the block.

## Error Handling

- **`gh` missing or unauthenticated**: Instruct the user to install it from https://cli.github.com/ and run `gh auth login`, then stop.
- **No `origin`, or not a git repository**: Scan only the session. Every target is unresolved, and the user must supply one in an `edit` before that item can be filed.
- **A duplicate search or timeline read fails**: Propose the affected candidates with a "not checked for duplicates" note.
- **The label list fails**: File without labels and report that labels were skipped.
- **An issue fails to file**: Continue with the rest, and check the newest-issues listing before any retry so a retry cannot duplicate an issue that did land.
- **The summary comment fails**: The issues stay filed. Report the failure and the list the comment would have carried.
- **A third-party target**: Never filed without approval by number, and never commented on.
