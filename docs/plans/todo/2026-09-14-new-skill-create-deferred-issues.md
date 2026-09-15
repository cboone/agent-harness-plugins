# New skill: create-deferred-issues

Issue: [#350](https://github.com/cboone/agent-harness-plugins/issues/350)

## Context

The most frequent explicit instruction in the fosforo transcripts is the user telling the agent to file something the agent had already named in prose: "Create an issue to take care of shfmt", "Create an issue for that last concern regarding fosforo_all. Then /pr". The agent surfaces a concern, sets it aside as out of scope, and the user has to ask for each one separately, usually bundled with `/pr` as end-of-work cleanup.

The outcome is a plugin, `create-deferred-issues`, in the `issues-and-worktrees` category: one pass that collects every concern raised and set aside during a unit of work, proposes them as a single batch the user trims and edits, files the approved set, and links each back to where it came from. Two skills in flight already plan to hand off to it (#371 `final-review-pass`, and the deferred-items output in `docs/plans/todo/2026-09-14-new-skill-review-in-depth.md`).

## Design decisions

Settled with the user during planning.

| Decision               | Choice                                                                                                                                                                                                                              |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Filing mechanics       | Self-contained in `references/batch-filing.md`, mirroring the `create-issue` tmpfile pattern and naming it as the source. `create-issue` has no parent continuation contract and may ask per issue, which fights one batch approval |
| Composition with `pr`  | A small `pr` change in the same PR: a `## Follow-ups` section (no closing keyword) listing issues filed earlier in the session for this branch, and those numbers excluded from issue detection. `pr` goes 1.8.4 to 1.9.0           |
| Proposal gate          | Never skipped: not by a parent continuation block, not by "file them all" said before the batch was shown                                                                                                                           |
| Posture                | Under-propose. A missed deferral costs one manual `/create-issue`; a wrong one costs triage                                                                                                                                         |
| Session source         | The conversation in context only. No harness transcript files: they are Claude Code specific, and what compaction dropped is not reconstructed                                                                                      |
| Labels                 | Chosen only from labels that already exist in the target repository, excluding status and automation labels. Never created                                                                                                          |
| Default target         | The repository `origin` points at, passed as an explicit `--repo` on every `gh` call, because `gh` otherwise prefers an `upstream` remote                                                                                           |
| Third-party targets    | A fork's parent or an `upstream` remote is never a default. It is filed to only when an item names it or the user retargets an item, and only on approval by item number                                                            |
| Summary comment target | The branch's open PR if it lives in the default target repository, else the issue the branch addresses there, else none. Never on a third-party repository                                                                          |

## Files

### `plugins/create-deferred-issues/.claude-plugin/plugin.json`

Alphabetized fields matching siblings, `"version": "1.0.0"`, `"skills": "./skills"`. Keywords `["deferrals", "follow-ups", "gh", "github", "issues"]`.

Canonical description, 154 characters, used verbatim as the marketplace `description`, the plugin README's first paragraph, and the root README cell:

> Scan the session, branch, and pull request for concerns set aside as out of scope, propose them as one batch, and file the approved ones as GitHub issues.

### `plugins/create-deferred-issues/skills/create-deferred-issues/SKILL.md`

Frontmatter `name` and a `>-` description that fires on batch phrasings ("create deferred issues", "file the deferred issues", "file issues for the follow-ups", "file everything we set aside", "what did we defer") and deliberately not on single-issue phrasings like "file an issue for X", which stay with `create-issue`. Ends "Requires the gh CLI to be installed and authenticated."

Body sections:

- **Options**: `--dry-run` (propose, then stop; file and post nothing), `--no-comment` (skip the summary comment).
- **Parent Continuation Contract**, shaped like `lint-and-fix`'s, with keys `Caller`, `Resume target`, `On completion` (filed, none found, none approved, or dry run), and `On filing failure`. The proposal still stops for the user. Final output: `Deferred issues: <filed|none found|none approved|dry run|failure>`, `Filed: <none|#N title (owner/name), ...>`, `Summary comment: <none|URL>`, `Caller resume target:`. A user's own "then /pr" is honored the same way: report, then continue to `pr`.

#### Workflow

1. **Establish context** (read-only).
   - **Repository.** `git remote get-url origin`, then `gh repo view <url> --json nameWithOwner,visibility,isArchived,isFork,parent,hasIssuesEnabled,defaultBranchRef`. If `gh` cannot resolve the URL (an SSH host alias, for example), parse `owner/name` from the URL path and retry; on a host other than github.com use `HOST/OWNER/NAME` for `--repo` and `--hostname` for `gh api`. `parent` carries no `nameWithOwner`; build it from `.parent.owner.login` and `.parent.name`. `git remote -v` for an `upstream` remote. With no `origin`, every item's target starts unresolved.
   - **Branch and base.** `git branch --show-current`. Detached HEAD, or the default branch itself: scan the session only and say so. Otherwise detect the base the way the `pr` skill's step 1 does (reflog creation point, validated), `git fetch origin <base> --quiet`, and diff against `origin/<base>`, so a stacked branch does not inherit its parent's markers.
   - **PR.** `gh pr list --repo <target> --head <branch> --state open --json number,url,title,body,baseRefName,headRepositoryOwner,closingIssuesReferences`, keeping only a PR whose head owner is origin's owner. Empty output means no PR; `gh pr view <branch>` is not used because it returns merged PRs that reused the branch name. When origin is a fork and no PR is found, run the same query against the parent as a read-only source. A PR found there yields candidates but no summary comment.
   - **Source issues.** The PR's closing references; otherwise issue numbers in the branch name and in `git log --no-merges origin/<base>..HEAD`, each confirmed with `gh issue view <n> --repo <target> --json url,state,title,body`, dropping any whose URL contains `/pull/`.
   - **Labels** per target repository: `gh label list --repo <target> --json name,description --limit 200`.
1. **Collect candidates** using `./references/deferral-signals.md`:
   - **Session**: assistant and user turns in context.
   - **Code markers**: `git diff --unified=0 -G '(^|[^A-Za-z0-9_])(TODO|FIXME|XXX|HACK)([^A-Za-z0-9_]|$)' origin/<base>...HEAD`, the same against `HEAD` for uncommitted changes, and every line of untracked files from `git ls-files --others --exclude-standard`. `-G` selects whole files, so re-apply the same pattern to each added line. Written without `\b`, which matches nothing in macOS git's regex engine; the delimiters also keep `mktemp` templates like `XXXXXX` from matching.
   - **PR**: its body; conversation comments and review bodies from `gh pr view <n> --repo <target> --json comments,reviews`; inline review comments from `gh api --paginate repos/<target>/pulls/<n>/comments --jq '.[] | {path, line, body, url: .html_url, author: .user.login}'`.
   - **Documents**: out-of-scope sections of plan files under `docs/plans/` and review documents under `docs/reviews/` that are changed, uncommitted, or untracked on the branch, plus source issue bodies.
1. **Filter and deduplicate.**
   - Drop what was resolved later in the work, what the user declined, and hedges with no concrete action. Merge the same concern arriving from two sources.
   - **Already tracked**: anything whose text names an issue other than the branch's own source issues (those close with this work, so naming them tracks nothing); anything filed earlier in the session; anything in the source PR or issues' cross-reference timeline, `gh api --paginate repos/<target>/issues/<n>/timeline --jq '.[] | select(.event == "cross-referenced") | .source.issue | {number, title, state, url: .html_url}'`, which lists every issue whose body links back, whether or not a summary comment was posted; anything a review document records as filed; and anything a `gh issue list --repo <target> --search "<distinctive words>" --state all --limit 5 --json number,title,state,url` hit matches on distinctive words, using the `pr` skill's strategy 3 test. A clear match goes to "Already tracked"; an ambiguous one is proposed with a "possible duplicate of #N" note.
   - **Targets**: the default, or another repository only where the deferral names it; an unresolvable name is proposed as unresolved rather than guessed. Check each distinct target with `gh repo view <target> --json visibility,isArchived,hasIssuesEnabled`. Archived or issues disabled moves the item to "Cannot file", naming the reason; when origin is a fork with issues disabled, the note says the user may retarget an item to the parent explicitly.
   - **Visibility**: a public target receiving an item from a private origin gets no links, paths, or permalinks into the private repository, and the proposal says so.
1. **Propose the batch.**
   - Numbered items, each with title, target repository, labels, source (with link where one exists), and a two-line body sketch; then "Already tracked" and "Cannot file" lists, so the user can pull an item back.
   - A third-party target is marked as such and needs approval by its number.
   - Ask for a reply in plain text, not a structured question, since a batch can exceed four items and edits need free text: `file all`, `file 1 3`, `drop 2`, `edit 2: ...`, `none`. Numbers are fixed for the whole exchange and never renumbered after a drop.
   - An unambiguous approval of the whole batch ("yes", "file them") counts as `file all`, which never covers a third-party target. A reply that edits without approving, or is unclear about which items, gets the revised batch re-presented. Stop and wait.
   - With nothing found, report which sources were scanned and stop. `--dry-run` stops after the proposal.
1. **File the approved set** per `./references/batch-filing.md`, sequentially, in proposal order.
1. **Cross-reference.** Each body already links its source. Post one summary comment on the source per the decision table, unless `--no-comment` or nothing was filed.
1. **Report**: filed (number, title, repository), dropped, failed, already tracked, cannot file, summary comment URL; next step `/pr` when no PR exists yet, noting that `pr` lists these under Follow-ups.

#### Error Handling

`gh` missing or unauthenticated; no `origin`; not a git repository (session only, targets unresolved); duplicate search or timeline failing (propose with a "not checked for duplicates" note); label list failing (file without labels); a create failing mid-batch (continue with the rest, and before any retry list the target's newest issues with `gh issue list --repo <target> --state all --limit 20 --json number,title,createdAt`, which does not depend on the search index lagging behind a just-created issue); summary comment failing (the issues stay filed; report).

### `./references/deferral-signals.md`

- **Definition**: a deferral needs both a concrete concern and an explicit decision not to address it in this work. Either half alone is not one.
- **Phrasings** from the issue ("out of scope", "worth filing", "follow-up", "should be tracked separately", "left open", "not addressed here", "a separate concern", "deferred to") plus close relatives ("beyond this PR", "a separate PR", "pre-existing and unrelated", "known limitation, not fixed here"), and the user-side forms ("not now", "leave that for later", "park that").
- **Source shapes**: code markers that open a comment or are followed by `:` or `(`, rather than a prose mention of the word; review replies that set a finding aside; review-feedback summaries with a Deferred category; plan, review, and issue headings (`Out of scope`, `Non-goals`, `What this does not close`, `Follow-ups`, `Future work`, `Deferred`).
- **Not deferrals**: hedges and speculation; alternatives considered and rejected; concerns fixed later in the same work; concerns the user declined outright (declined is not deferred); generic caveats with no action; template placeholders such as a PR body's `TODO:` line; markers in generated, vendored, fixture, or snapshot files, or in documentation that teaches marker syntax; unchecked items of the issue being worked on, which are this branch's remaining work, not a new issue.
- **Worked examples** in neutral form, including one per exclusion. No invented backticked names beside the word "skill", and no example paths beginning `plugins/`.
- **Target repository signals**: an `owner/name`, a URL, or a repository the session already identified by name.

### `./references/batch-filing.md`

- **Title**: imperative, under 70 characters, no trailing period, and no backticks, since titles do not render Markdown and a backtick inside a double-quoted shell argument is command substitution. Pass it single-quoted; rephrase a title that needs an apostrophe.
- **Body** written for a reader who never saw the session: `## Summary` (the concern, why it was set aside, what done looks like) and `## Context` (`Deferred from #<pr>` or `Raised while working on #<issue>`, using `owner/name#N` across repositories, plus a link to the review comment, a blob permalink at a pushed commit for a code marker or `path:line` text when unpushed, or the plan path). The source link is what puts the issue on the source's timeline, which later runs read for duplicates. Summarize; never paste session text wholesale, secrets, or local absolute paths, and apply the visibility rule.
- **Labels**: existing labels only, per target repository. Prefer a type label (bug, enhancement, documentation, maintenance, or the repository's equivalent) and an obviously matching topical label. Never apply status, triage-outcome, or automation-owned labels (`in progress`, `duplicate`, `wontfix`, `dependencies`, a label a workflow manages). Single-quote each name, since labels may contain spaces.
- **Per-issue sequence**, mirroring `create-issue`: `mktemp -u /tmp/gh-issue-body-XXXXXX`; Write the body; a separate `gh issue create --repo <target> --title '<title>' --body-file <path> --label '<name>'` call, never batched with the Write; `gh issue view <url> --json body --jq '.body | length'`, with `gh issue edit <url> --body-file <path>` recovery on zero; `rm -f <path>` in its own call. Record each URL. On a label error, re-run without labels and report which were skipped.
- **Summary comment**: body opens with `<!-- create-deferred-issues -->`, then one line per filed issue. Same tmpfile sequence (`/tmp/gh-comment-body-XXXXXX`) with `gh pr comment <n> --repo <target> --body-file <path>` or `gh issue comment <n> --repo <target> --body-file <path>`. A re-run posts a new comment listing only what it filed.

### `plugins/create-deferred-issues/README.md`

House template: title, description paragraph verbatim, `**Type:** Skill`, `**Trigger:** /create-deferred-issues`, `**Requires:** gh (authenticated)`; Installation; What It Does (sources, the mandatory proposal, filing, cross-referencing, running before `/pr`); Usage with an options table; Recommended Permissions JSON covering every command the skill runs: `git remote`, `git branch`, `git reflog show`, `git ls-remote --heads`, `git fetch`, `git merge-base`, `git diff`, `git log`, `git status`, `git ls-files`, `gh repo view`, `gh pr list`, `gh pr view`, `gh issue view`, `gh issue list`, `gh label list`, `gh api --paginate repos/*/pulls/*/comments*`, `gh api --paginate repos/*/issues/*/timeline*`, `gh issue create`, `gh issue edit`, `gh pr comment`, `gh issue comment`, and the two `mktemp -u` and `rm -f` pairs; Examples; See Also linking `create-issue`, `pr`, `review-branch`, `resolve-copilot-pr-feedback`, `address-issue`, and all plugins.

### `plugins/pr/` (1.8.4 to 1.9.0)

- `skills/pr/SKILL.md`:
  - Step 2 "Combine results": remove any issue filed earlier in this session as a follow-up to this branch's work (for example by the `create-deferred-issues` skill), whichever strategy found it. Strategy 2 picks up any `#N` in a commit message, and strategy 3 can match a just-filed follow-up that shares words with the branch slug; either would close it at merge. Step 4's commit messages inherit the exclusion.
  - Step 7 body: a `## Follow-ups` section after `## Closes` (after `## Test plan` when there is no Closes section), listing `- #N` or `- owner/name#N` for those issues, never with a closing keyword, taken from the session only, omitted when there are none.
  - Step 9: report the follow-ups listed.
- `README.md` "What It Does": one sentence on the Follow-ups section.
- `.claude-plugin/plugin.json` version.

### Catalog registration

- `.claude-plugin/marketplace.json`: the new entry between `commit` and `create-issue`, `"category": "issues-and-worktrees"`, `"source": "./plugins/create-deferred-issues"`. `metadata.version` from `bin/compute-catalog-state` at each commit: `catalog-M71-m103-p156-n58` after registration, `catalog-M71-m104-p152-n58` after the `pr` bump, each confirmed from the script rather than assumed.
- Root `README.md`: a `Create Deferred Issues` row between `Address Issue in Worktree` and `Create Issue`; the `gh` bullet becomes `_Address Issue, Create Deferred Issues, Create Issue, Suggest Next Issue:_`. `## Contents` untouched.
- `bin/build-codex-marketplace` and `bin/build-opencode-mirror` at each commit that changes plugin content or the catalog, results committed.

## Cross-reference hazards

- No `repository-paths` comment: the `docs/plans/` and `docs/reviews/` paths in the skill name files in the project it runs against.
- Name only existing plugins beside the word "skill": `create-issue`, `pr`, `review-branch`, `resolve-copilot-pr-feedback`, `lint-and-fix`. `final-review-pass` and `review-in-depth` do not exist yet and are not named in `SKILL.md` or references.
- `pr`'s new mention of the `create-deferred-issues` skill resolves only once the plugin directory exists, which the commit order guarantees.
- No backticked lowercase single-segment absolute paths, and no example paths beginning `plugins/`.
- No em dashes, no time or effort estimates, neutral terminology.

## Verification

```bash
yarn install --immutable
bin/check-cross-references plugins/create-deferred-issues/skills/create-deferred-issues/SKILL.md
bin/check-cross-references plugins/pr/skills/pr/SKILL.md
make format
make build
make validate
make test-all
git status --porcelain dist/ .agents/
```

Then the `check-versions` skill. Finally a read-only walk-through: follow the new `SKILL.md` against this branch and session in `--dry-run` form, running its read-only commands for real (PR lookup, marker scan, timeline, label list) and confirming the proposal is sensible and nothing is filed.

## Commits

1. `docs: add plan for the create-deferred-issues skill (#350)`
1. `feat: add create-deferred-issues skill plugin (#350)`: the plugin directory
1. `feat: register create-deferred-issues in the marketplace catalog (#350)`: marketplace entry, root README row, catalog state, generated trees
1. `feat: keep follow-up issues out of pr closing references (#350)`: `pr` skill, README, version, catalog state, generated trees
