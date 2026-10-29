# Progress model

Tests for `progress.jq`, the jq definitions `backlog-gather` and `bugs-gather`
share, so both boards derive progress and affinity by the same rules. The
gather documents cover how each script reads GitHub and git into these shapes;
this one covers the rules themselves, case by case, including the ones where
signals compete.

`model` runs a jq expression with the definitions loaded and helpers that build
an issue for `#12`, its pull requests, and its branches. The gather time is
2026-10-15T12:00:00Z.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
$ function model() {
>   jq -n -r -L "$(dirname "${BACKLOG_GATHER_BIN}")" 'include "progress";
>     def c: {progressLabels: ["in progress"], progressPipelines: ["In Progress"], quietDays: 7, staleDays: 30,
>             affinityCommentDays: 90, uniformityShare: 0.5, uniformityMinimum: 4};
>     def now: "2026-10-15T12:00:00Z" | epoch;
>     def item(f): {number: 12, labels: [], updatedAt: "2026-10-14T12:00:00Z", pipeline: null, pipelineSince: null, prs: [], merged: []} | f;
>     def pr($n; f): {number: $n, headRefName: "fix/12-pr\($n)", isDraft: false, mergeable: "MERGEABLE", mergeStateStatus: "CLEAN",
>                     reviewDecision: "APPROVED", checks: "SUCCESS", reviewRequests: 0,
>                     createdAt: "2026-10-10T12:00:00Z", updatedAt: "2026-10-14T12:00:00Z", lastReview: null} | f;
>     def branch($name; f): {name: $name, local: false, remote: true, worktree: false, at: "2026-10-14T12:00:00Z", ahead: 1, behind: 0} | f;
>     def carrier: to_entries[0] | "\(.key) \(.value)";
>     def show: if . == null then "none"
>       else "\(.stage) on \(.carrier | carrier) [\(.flags | join(","))] \(.nextAction)"
>            + (if (.extraCarriers | length) > 0 then "; also \(.extraCarriers | map(carrier) | join(", "))" else "" end) end;
>     def run($branches): progress_of(.; $branches; c; now; "devbox") | show;
>     def held(f): {assignees: [], claims: [], author: "someone", commented: false, active: [], recent: []} | f;
>     '"${1}"
> }
```

## A branch names an issue from the start of a path segment

A version number in a branch name, or a dependency bot's branch, names no
issue.

```scrut
$ model '["feature/412-tags", "412", "issue412", "fix-412", "GH-412", "cboone/412-x", "chore/4120", "release/412.1", "update-to-v412", "dependabot/npm/lib-412", "renovate/412-x"][] | "\(.) \(names_issue(412))"'
feature/412-tags true
412 true
issue412 true
fix-412 true
GH-412 true
cboone/412-x true
chore/4120 false
release/412.1 false
update-to-v412 false
dependabot/npm/lib-412 false
renovate/412-x false
```

## Area patterns cross segments with \*\*, and \*\*/ matches none

```scrut
$ model '[["docs/**/README.md", "docs/README.md"], ["docs/**/README.md", "docs/a/b/README.md"], ["**/x.c", "x.c"], ["src/*.c", "src/a/b.c"], ["src/?.c", "src/a.c"], ["src/parser/", "src/parser/deep/lexer.c"], ["a+b.md", "aab.md"]][] | .[0] as $glob | .[1] as $path | "\($glob) \($path) \($path | test($glob | glob_regex))"'
docs/**/README.md docs/README.md true
docs/**/README.md docs/a/b/README.md true
**/x.c x.c true
src/*.c src/a/b.c false
src/?.c src/a.c true
src/parser/ src/parser/deep/lexer.c true
a+b.md aab.md false
```

## A pull request's state decides its stage, in the model's order

A draft stays a draft through a conflict; a conflict comes before changes
requested; a check rollup of `ERROR` fails and one of `EXPECTED` is still
running.

```scrut
$ model '[pr(1; .isDraft = true | .mergeable = "CONFLICTING"), pr(2; .mergeable = "CONFLICTING" | .reviewDecision = "CHANGES_REQUESTED"), pr(3; .checks = "ERROR"), pr(4; .reviewDecision = null | .checks = "EXPECTED"), pr(5; .reviewDecision = "REVIEW_REQUIRED"), pr(6; .mergeable = "UNKNOWN")][] | "\(.number) \(pr_stage) \(pr_next.nextMove): \(pr_next.nextAction) (\(pr_signal))"'
1 draft author: mark it ready for review (pull request #1, draft)
2 needs-author author: resolve the conflict (pull request #2, changes requested, merge conflict, checks passing)
3 needs-author author: fix the checks (pull request #3, approved, checks failing)
4 awaiting-review ci: wait for checks (pull request #4, no review required, checks running)
5 awaiting-review nobody: request a review (pull request #5, review required, no review requested, checks passing)
6 ready-to-merge author: merge it (pull request #6, approved, mergeability unknown, checks passing)
```

## Close-out outranks an open pull request, a branch, and a label

The others stay as extra carriers, and only the label raises a flag.

```scrut
$ model 'item(.labels = ["in progress"] | .prs = [pr(40; .)] | .merged = [{number: 38, mergedAt: "2026-10-13T12:00:00Z", closes: true}]) | run([branch("fix/12-x"; .)])'
close-out on pr 38 [leftover-label] close or split; also pr 40, branch fix/12-x, label in progress
```

## A stale close-out still asks to close or split

```scrut
$ model 'item(.merged = [{number: 38, mergedAt: "2026-08-01T12:00:00Z", closes: true}]) | run([])'
close-out on pr 38 [stale] close or split
```

## A merged pull request that only mentions an issue needs a mark of work

Without a progress label or pipeline it is not progress. A pipeline marks the
work but, not being a label, raises no `leftover-label`.

```scrut
$ model '{number: 38, mergedAt: "2026-10-13T12:00:00Z", closes: false} as $m | (item(.merged = [$m]), item(.merged = [$m] | .pipeline = "In Progress")) | run([])'
none
close-out on pr 38 [] close or split; also pipeline In Progress
```

## Among open pull requests the furthest stage carries the issue

```scrut
$ model 'item(.prs = [pr(41; .isDraft = true), pr(42; .reviewDecision = "CHANGES_REQUESTED")]) | run([])'
needs-author on pr 42 [multiple] answer the review; also pr 41
```

## A pull request and its own head branch count once

The head branch still says the work is behind, and its last commit counts as
activity, which here keeps the work from going quiet.

```scrut
$ model 'item(.prs = [pr(40; .updatedAt = "2026-09-01T12:00:00Z")]) | run([branch("fix/12-pr40"; .behind = 2)])'
ready-to-merge on pr 40 [behind] merge it
```

## A branch carries work with commits ahead or a worktree

A branch with nothing beyond the default branch is not progress unless a
worktree has it checked out. One whose commits the gather could not count
still is, and its signal says so.

```scrut
$ model '(branch("fix/12-a"; .ahead = 0), branch("fix/12-a"; .ahead = 0 | .local = true | .remote = false | .worktree = true), branch("fix/12-a"; .ahead = null | .behind = null)) as $b | item(.) | progress_of(.; [$b]; c; now; "devbox") | if . == null then "none" else "\(.signal) [\(.flags | join(","))] \(.nextAction)\(if .host then " on \(.host)" else "" end)" end'
none
branch fix/12-a, 0 commits ahead, local [local] push it on devbox
branch fix/12-a, commits ahead unknown [] open a pull request
```

## A branch only on the gathering machine is marked local, even as an extra carrier

```scrut
$ model 'item(.prs = [pr(40; .)]) | progress_of(.; [branch("fix/12-y"; .local = true | .remote = false)]; c; now; "devbox") | .extraCarriers | tojson'
[{"branch":"fix/12-y","local":true}]
```

## Local and remote copies of a branch join, counting from the one further ahead

```scrut
$ model '[{name: "fix/12-a", local: true, remote: false, worktree: false, at: "2026-10-01T12:00:00Z", ahead: 0, behind: 0}, {name: "fix/12-a", local: false, remote: true, worktree: false, at: "2026-10-05T12:00:00Z", ahead: 3, behind: 1}, {name: "main", local: true, remote: false, worktree: false, at: null, ahead: 0, behind: 0}] | join_branches("main") | .[] | "\(.name) local \(.local) remote \(.remote) ahead \(.ahead) behind \(.behind) at \(.at)"'
fix/12-a local true remote true ahead 3 behind 1 at 2026-10-05T12:00:00Z
```

## An uncounted remote copy stays uncounted beside a copy with nothing ahead

```scrut
$ model '[{name: "fix/12-a", local: true, remote: false, worktree: false, at: "2026-10-01T12:00:00Z", ahead: 0, behind: 2}, {name: "fix/12-a", local: false, remote: true, worktree: false, at: "2026-10-05T12:00:00Z", ahead: null, behind: null}] | join_branches("main") | .[] | "\(.name) ahead \(.ahead) behind \(.behind) carries work \(carries_work)"'
fix/12-a ahead null behind null carries work true
```

## A pipeline alone is started, from when the issue entered it

```scrut
$ model 'item(.pipeline = "In Progress" | .pipelineSince = "2026-10-01T12:00:00Z") | progress_of(.; []; c; now; null) | "\(.stage) on \(.carrier.pipeline), last activity \(.lastActivity) [\(.flags | join(","))]"'
started on In Progress, last activity 2026-10-01T12:00:00Z [quiet]
```

## Quiet and stale start strictly after their day counts

```scrut
$ model '("2026-10-08T12:00:00Z", "2026-10-08T11:59:59Z", "2026-09-15T12:00:00Z", "2026-09-15T11:59:59Z") as $at | item(.labels = ["in progress"] | .updatedAt = $at) | progress_of(.; []; c; now; null) | "\($at) [\(.flags | join(","))] \(.nextAction)"'
2026-10-08T12:00:00Z [] open a branch
2026-10-08T11:59:59Z [quiet] open a branch
2026-09-15T12:00:00Z [quiet] open a branch
2026-09-15T11:59:59Z [stale] resume or drop
```

## Merged links count closing references and closing keywords in the repository

A merged pull request in another repository, an unmerged one, and an issue
that cross-references this one do not count.

```scrut
$ model '{closedByPullRequestsReferences: {nodes: [{number: 1, mergedAt: "2026-10-01T12:00:00Z", repository: {nameWithOwner: "acme/widgets"}}, {number: 2, mergedAt: "2026-10-01T12:00:00Z", repository: {nameWithOwner: "acme/gadgets"}}, {number: 3, mergedAt: null, repository: {nameWithOwner: "acme/widgets"}}]}, timelineItems: {nodes: [{__typename: "CrossReferencedEvent", willCloseTarget: true, source: {__typename: "PullRequest", number: 4, mergedAt: "2026-10-02T12:00:00Z", repository: {nameWithOwner: "ACME/Widgets"}}}, {__typename: "CrossReferencedEvent", willCloseTarget: false, source: {__typename: "PullRequest", number: 5, mergedAt: "2026-10-03T12:00:00Z", repository: {nameWithOwner: "acme/widgets"}}}, {__typename: "CrossReferencedEvent", willCloseTarget: false, source: {__typename: "Issue"}}]}} | merged_links("acme/widgets")[] | "#\(.number) closes \(.closes)"'
#1 closes true
#4 closes true
#5 closes false
```

## Times convert to UTC from any offset

A malformed time is an error rather than no value.

```scrut
$ model '["2026-10-15T05:00:00-07:00", "2026-10-15T12:00:00.5Z", "2026-10-15T12:00+00:00", "2026-10-15T17:30:00+05:30"][] | utc' && model '"2026-10-15 12:00" | utc' 2>&1; echo "exit ${?}"
2026-10-15T12:00:00Z
2026-10-15T12:00:00Z
2026-10-15T12:00:00Z
2026-10-15T12:00:00Z
jq: error (at <unknown>): not an ISO 8601 time
exit 5
```

## A pull request linked twice is one merged link

A closing reference and a mention of the same pull request make one link that
closes the issue.

```scrut
$ model '{closedByPullRequestsReferences: {nodes: [{number: 1, mergedAt: "2026-10-01T12:00:00Z", repository: {nameWithOwner: "acme/widgets"}}]}, timelineItems: {nodes: [{__typename: "CrossReferencedEvent", willCloseTarget: false, source: {__typename: "PullRequest", number: 1, mergedAt: "2026-10-01T12:00:00Z", repository: {nameWithOwner: "acme/widgets"}}}]}} | merged_links("acme/widgets") | map("#\(.number) closes \(.closes)") | join(", ")'
#1 closes true
```

## The owner follows assignment, then a claim's assignees, then implicit tiers

An issue assigned to someone else stays theirs despite implicit affinity. With
assignment ignored, a claim belongs to its assignees, the current user first,
ahead of implicit affinity; with no assignee it has no known owner.

```scrut
$ model '[[held(.assignees = ["ana", "ben"]), []], [held(.assignees = ["ben"] | .active = ["parser changed on branch x"]), []], [held(.assignees = ["ben", "ana"] | .claims = ["claimed with the mine label"]), ["assigned"]], [held(.assignees = ["ben"] | .claims = ["claimed with the mine label"] | .active = ["parser changed on branch x"]), ["assigned"]], [held(.author = "ana" | .commented = true | .recent = ["cache changed in commit abc within 30 days"]), []], [held(.claims = ["claimed in the Mine pipeline"]), []], [held(.author = "ana"), ["filed"]]][] | affinity_of(.[0]; .[1]; "ana"; c) | if .owner == null then "no owner" else "\(.owner) \(.kind)\(if .tier then " \(.tier)" else "" end): \(.reasons | join("; "))" end'
you explicit: assigned
ben explicit: assigned to @ben
you explicit: claimed with the mine label
ben explicit: claimed with the mine label; assigned to @ben
you implicit 2: cache changed in commit abc within 30 days; filed it; commented within 90 days
unknown explicit: claimed in the Mine pipeline
no owner
```

## Uniformity ignores a kind one owner holds on the uniformity share or more

With a share of 0.5 and four issues, a kind held on two is ignored and one
held on one is not. Filing counts any one author.

```scrut
$ model '[held(.assignees = ["ana"] | .claims = ["c"] | .author = "bot" | .commented = true | .active = ["a"] | .recent = ["r"]), held(.assignees = ["ana"] | .claims = ["c"] | .author = "bot" | .commented = true | .active = ["a"] | .recent = ["r"]), held(.assignees = ["ben"]), held(.author = "ana")] | uniformity_ignored(.; c) | join(", ")'
assigned, claimed, filed, commented, active, recent
```

```scrut
$ model '[held(.assignees = ["ana"] | .claims = ["c"] | .author = "bot" | .commented = true | .active = ["a"] | .recent = ["r"]), held(.assignees = ["ben"] | .author = "cat"), held(.author = "dan"), held(.author = "eve")] | uniformity_ignored(.; c) | if length == 0 then "none" else join(", ") end'
none
```

## Uniformity needs the minimum number of issues

```scrut
$ model '[held(.author = "bot"), held(.author = "bot"), held(.author = "bot")] | uniformity_ignored(.; c) | if length == 0 then "none" else join(", ") end'
none
```

## Both gather scripts refuse to run without the shared definitions

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp "${BACKLOG_GATHER_BIN}" "${BUGS_GATHER_BIN}" "${dir}/" && { "${dir}/backlog-gather" --help 2>&1; echo "exit ${?}"; "${dir}/bugs-gather" --help 2>&1; echo "exit ${?}"; }
backlog-gather: */progress.jq is missing; reinstall publish-report-board (glob)
exit 2
bugs-gather: */progress.jq is missing; reinstall publish-report-board (glob)
exit 2
```
