# Backlog gather

Tests for the `backlog-gather` script that `publish-report-board` bundles. It
reads a repository's open issues and pull requests from GitHub and its branches
and recent commits from the local checkout, works out each issue's progress
stage and affinity signals, and, once the analysis has written the board, adds
the derived fields with `finish`.

Every GitHub call goes through `tests/fixtures/backlog-gather-gh-stub`, which
answers from `tests/data/backlog-gather/github/`. The fixtures describe
`acme/widgets`, read by `ana`, with 22 open issues built so that between them
they reach every stage, flag, and affinity tier. The checkout is a throwaway
clone of a bare repository made below, whose origin reads as
`github.com/acme/widgets` while pushes go to the bare repository, with commits
at fixed dates, a branch that was never pushed, and a worktree. `backlog` takes
settings (`NAME=value`) first, then the command. The gather time is fixed at
2026-10-15T16:00:00Z and the host at `devbox`.

```scrut
$ function backlog() {
>   local -a settings=()
>   while [[ "${1:-}" == *=* ]]; do
>     settings+=("${1}")
>     shift
>   done
>   env PATH="${stub_dir}:${PATH}" STUB_GH_DIR="${BACKLOG_GATHER_DATA_DIR}/github" \
>     BACKLOG_GATHER_NOW=2026-10-15T16:00:00Z BACKLOG_GATHER_HOST=devbox XDG_CONFIG_HOME="${work}/config" \
>     ${settings[@]+"${settings[@]}"} "${BACKLOG_GATHER_BIN}" "${@}"
> }
> function commit_at() {
>   mkdir -p "$(dirname "${3}")"
>   printf '%s\n' "${1}" > "${3}"
>   git add "${3}"
>   GIT_AUTHOR_DATE="${1}" GIT_COMMITTER_DATE="${1}" GIT_AUTHOR_NAME=Someone GIT_COMMITTER_NAME=Someone \
>     GIT_AUTHOR_EMAIL="${2}" GIT_COMMITTER_EMAIL="${2}" git commit -q -m "Change ${3}"
> }
> function config_with() {
>   mkdir -p "${work}/config/report-boards/backlog-triage/github.com/acme"
>   jq "${1:-.}" "${BACKLOG_GATHER_DATA_DIR}/config.json" > "${work}/config/report-boards/backlog-triage/github.com/acme/widgets.json"
> }
> function stages() {
>   jq -r '.issues[] | select(.progress != null) | .progress as $p | "#\(.number) \($p.stage) \($p.nextMove) \"\($p.nextAction)\" [\($p.flags | join(","))]\(if $p.host != null then " on \($p.host)" else "" end)"' "${1}"
> }
> function owners() {
>   jq -r '.issues[] | .affinity as $a | select($a.owner != null) | "#\(.number) \($a.owner) \($a.kind)\(if $a.tier != null then " \($a.tier)" else "" end): \($a.reasons | join("; "))"' "${1}"
> }
> set -o pipefail
> stub_dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
> cp "${BACKLOG_GATHER_GH_STUB_BIN}" "${stub_dir}/gh"
> chmod +x "${stub_dir}/gh"
> work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
> config_with
> git init -q --bare "${work}/remote/acme/widgets.git"
> git clone -q "${work}/remote/acme/widgets.git" "${work}/widgets" 2> /dev/null
> cd "${work}/widgets"
> git remote set-url origin https://github.com/acme/widgets.git
> git remote set-url --push origin "${work}/remote/acme/widgets.git"
> git symbolic-ref HEAD refs/heads/main
> git config user.email ana@example.com
> commit_at 2026-08-01T10:00:00Z ana@example.com old/notes.txt
> commit_at 2026-09-20T10:00:00Z ben@example.com base.txt
> git push -q origin main
> git switch -q -c feature/13-behind && commit_at 2026-10-12T10:00:00Z ben@example.com src/thirteen.c && git push -q origin feature/13-behind
> git switch -q main && git switch -q -c fix/12-old && commit_at 2026-09-01T10:00:00Z ben@example.com fix/old.c && git push -q origin fix/12-old
> git switch -q main && git switch -q -c feature/12-again && commit_at 2026-09-05T10:00:00Z ben@example.com fix/again.c && git push -q origin feature/12-again
> git switch -q main && git branch -q -D feature/13-behind fix/12-old feature/12-again
> commit_at 2026-10-10T10:00:00Z ana@example.com lib/cache.c
> git push -q origin main
> git switch -q -c feature/3-pushed && commit_at 2026-10-01T10:00:00Z ana@example.com src/ui/button.c && git push -q origin feature/3-pushed
> git switch -q main && git switch -q -c chore/412-cleanup && commit_at 2026-10-13T10:00:00Z ben@example.com chore.txt && git push -q origin chore/412-cleanup
> git switch -q main && git branch -q -D chore/412-cleanup
> git switch -q -c feature/2-local && commit_at 2026-10-14T10:00:00Z ana@example.com src/parser/lexer.c
> git switch -q main
> git worktree add -q -b feature/20-fresh "${work}/fresh" main
> backlog gather acme/widgets "${work}/gather.json" > "${work}/gather.out"
> backlog finish "${work}/gather.json" "${BACKLOG_GATHER_DATA_DIR}/analysis.json" "${work}/board.json" > "${work}/finish.out"
```

## Gather reports the stages, flags, and ignored signals

```scrut
$ cat "${work}/gather.out"
acme/widgets at main * (glob)
Flags: 3 behind, 1 conflict, 1 leftover-label, 2 local, 1 multiple, 2 quiet, 1 stale
Affinity signals ignored for uniformity: none
```

```scrut
$ head -1 "${work}/gather.out" | cut -d: -f2
 22 open issues; 1 started, 5 branch, 1 draft, 3 awaiting-review, 2 needs-author, 1 ready-to-merge, 1 close-out
```

## Each issue reaches the stage its furthest signal does

A label alone is `started`. A branch is `branch`, and one only on this
machine names the host and asks to be pushed. A fresh branch in a worktree
counts though it has no commits yet. `chore/412-cleanup` names #412, not #41,
so #41 has no stage.

```scrut
$ stages "${work}/gather.json"
#1 started author "open a branch" []
#2 branch author "push it" [local] on devbox
#3 branch author "open a pull request" [quiet]
#4 draft author "mark it ready for review" []
#5 awaiting-review nobody "request a review" []
#6 awaiting-review reviewer "wait for review" []
#7 awaiting-review ci "wait for checks" []
#8 needs-author author "resolve the conflict" [conflict]
#9 needs-author author "answer the review" []
#10 ready-to-merge author "merge it" [behind]
#11 close-out author "close or split" [quiet,leftover-label]
#12 branch author "resume or drop" [stale,behind,multiple]
#13 branch author "open a pull request" [behind]
#20 branch author "push it" [local] on devbox
```

## Signals say what was gathered

GitHub reporting mergeability as unknown counts as no conflict, and the signal
says so.

```scrut
$ jq -r '.issues[] | select(.progress != null) | "#\(.number) \(.progress.signal)"' "${work}/gather.json"
#1 the in progress label
#2 branch feature/2-local, 1 commit ahead, local
#3 branch feature/3-pushed, 1 commit ahead
#4 pull request #40, draft
#5 pull request #50, review required, no review requested, checks passing
#6 pull request #60, review required, 1 review requested, checks running
#7 pull request #70, no review required, checks running
#8 pull request #80, approved, merge conflict, checks passing
#9 pull request #90, changes requested, checks failing
#10 pull request #100, approved, mergeability unknown, checks passing
#11 pull request #110 merged 2026-10-05
#12 branch feature/12-again, 1 commit ahead, 1 behind
#13 branch feature/13-behind, 1 commit ahead, 1 behind
#20 branch feature/20-fresh, 0 commits ahead, local
```

## A progress label beside a pull request does not decide the stage

Issue #10 carries `In Progress`, matched without regard to case, and its pull
request names it only through its head branch.

```scrut
$ jq -c '.issues[] | select(.number == 10) | .progress | {carrier, extraCarriers, since, lastActivity}' "${work}/gather.json"
{"carrier":{"pr":100},"extraCarriers":[{"label":"In Progress"}],"since":"2026-10-10T09:00:00Z","lastActivity":"2026-10-14T09:00:00Z"}
```

## A merged pull request that only mentions an issue makes it close-out

A merged pull request in another repository does not count.

```scrut
$ jq -c '.issues[] | select(.number == 11) | {carrier: .progress.carrier, mergedLinks}' "${work}/gather.json"
{"carrier":{"pr":110},"mergedLinks":[{"number":110,"mergedAt":"2026-10-05T10:00:00Z","closes":false}]}
```

## A mention alone is not progress

Without its progress label, `#11`'s merged pull request is likely a follow-up
that left it open, so the issue has no stage.

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp -R "${BACKLOG_GATHER_DATA_DIR}/github/." "${dir}/" && jq '(.. | objects | select(.number? == 11 and has("labels")) | .labels.nodes) |= map(select(.name != "in progress"))' "${BACKLOG_GATHER_DATA_DIR}/github/graphql/issues.json" > "${dir}/graphql/issues.json" && backlog STUB_GH_DIR="${dir}" gather acme/widgets "${work}/mention.json" > /dev/null && jq -c '.issues[] | select(.number == 11) | .progress' "${work}/mention.json"
null
```

## The most recent of several branches carries the issue

```scrut
$ jq -c '.issues[] | select(.number == 12) | .progress | {carrier, extraCarriers, lastActivity}' "${work}/gather.json"
{"carrier":{"branch":"feature/12-again"},"extraCarriers":[{"branch":"fix/12-old"}],"lastActivity":"2026-09-05T10:00:00Z"}
```

## The latest review counts as activity

```scrut
$ jq -r '.issues[] | select(.number == 8) | .progress.lastActivity' "${work}/gather.json"
2026-10-15T08:00:00Z
```

## The viewer's files come from open branches, open and merged pull requests, and recent commits

Files on another person's pushed branches do not count, and neither does a
commit older than the work window.

```scrut
$ jq -r '.viewerFiles.active[] | "\(.path) on \(.via)"' "${work}/gather.json"
docs/guide.md on pull request #50
src/parser/lexer.c on branch feature/2-local
src/ui/button.c on branch feature/3-pushed
```

```scrut
$ jq -r '.viewerFiles.recent[] | "\(.path) in \(.via | sub("commit [0-9a-f]+"; "commit SHA")) at \(.at)"' "${work}/gather.json"
lib/cache.c in commit SHA at 2026-10-10T10:00:00Z
src/net/http.c in pull request #110 at 2026-10-05T10:00:00Z
src/parser/lexer.c in commit SHA at 2026-10-14T10:00:00Z
src/ui/button.c in commit SHA at 2026-10-01T10:00:00Z
```

## The gather searches for the viewer's merged pull requests in the work window

```scrut
$ log="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && backlog STUB_GH_LOG="${log}" gather acme/widgets "${work}/logged.json" > /dev/null && sort "${log}"
gh api graphql issues owner=acme name=widgets
gh api graphql merged q=repo:acme/widgets is:pr is:merged author:ana merged:>=2026-09-15
gh api graphql pulls owner=acme name=widgets
gh api graphql repository owner=acme name=widgets
```

## Finish writes progress, affinity, and the claims derived from areas

```scrut
$ cat "${work}/finish.out"
22 issues: 15 yours, 1 owned by others, 1 claimed by no one known; 1 claim derived from areas
```

```scrut
$ jq -c '{schemaVersion, affinityIgnored, contention}' "${work}/board.json"
{"schemaVersion":2,"affinityIgnored":[],"contention":{"rowLabel":"Area","claims":[{"name":"parser","issues":[2,16]}]}}
```

```scrut
$ jq -c '.issues[] | select(.number == 2) | {progress: .progress.stage, areas}' "${work}/board.json"
{"progress":"branch","areas":["parser"]}
```

## Affinity follows assignment, then implicit tiers, then a claim with no owner

An assignee outranks implicit affinity. Open work in an issue's area is tier
1, recent commits or merged pull requests tier 2, and filing or commenting
tier 3. A comment older than the comment window does not count, and neither
does an issue with no areas.

```scrut
$ owners "${work}/board.json"
#1 you explicit: assigned
#2 you explicit: assigned
#3 you explicit: assigned
#4 you explicit: assigned
#5 you explicit: assigned
#6 you explicit: assigned
#7 you explicit: assigned
#8 you explicit: assigned
#9 you explicit: assigned
#10 you explicit: assigned
#14 ben explicit: assigned to @ben
#15 you implicit 3: filed it
#16 you implicit 1: parser changed on branch feature/2-local; parser changed in commit * within 30 days (glob)
#17 you implicit 2: cache changed in commit * within 30 days (glob)
#18 unknown explicit: claimed with the claimed label
#19 you implicit 2: net changed in pull request #110 within 30 days
#21 you implicit 3: commented within 90 days
```

## A signal one owner holds on most issues is ignored

With the share lowered to 40%, `ana` holds assignment on 10 of the 22 issues
and `ben` filed 12, so both kinds drop and the assigned issues lose their
explicit owner, `ben`'s `#14` among them.

```scrut
$ config_with '.uniformityShare = 0.4' && backlog gather acme/widgets "${work}/uniform.json" | tail -1 && backlog finish "${work}/uniform.json" "${BACKLOG_GATHER_DATA_DIR}/analysis.json" "${work}/uniform-board.json" > /dev/null && jq -c '.affinityIgnored' "${work}/uniform-board.json" && owners "${work}/uniform-board.json" | grep -E '^#(1|2|3|5|14|15) '; jq -r '.issues[] | select(.number == 14) | "#14 owner \(.affinity.owner)"' "${work}/uniform-board.json"
Affinity signals ignored for uniformity: assigned, filed
["assigned","filed"]
#2 you implicit 1: parser changed on branch feature/2-local; parser changed in commit * within 30 days (glob)
#3 you implicit 1: ui changed on branch feature/3-pushed; ui changed in commit * within 30 days (glob)
#5 you implicit 1: docs changed on pull request #50
#14 owner null
```

## Uniformity needs enough issues to judge

```scrut
$ config_with '.uniformityShare = 0.4 | .uniformityMinimum = 23' && backlog gather acme/widgets "${work}/few.json" | tail -1
Affinity signals ignored for uniformity: none
```

## Finish refuses analysis data that does not fit the gather

```scrut
$ config_with && jq '.issues[1].areas = ["lexer"] | .issues[0].progress = null | .schemaVersion = 2 | .contention.claims = [] | .issues += [{number: 99, title: "Gone", milestone: null}] | .issues |= map(select(.number != 41)) | .areas += [{name: "empty", paths: []}]' "${BACKLOG_GATHER_DATA_DIR}/analysis.json" > "${work}/bad.json" && backlog finish "${work}/gather.json" "${work}/bad.json" "${work}/out.json" 2>&1 | sed "s|${work}|WORK|g"
backlog-gather: WORK/bad.json does not fit the gather:
  - schemaVersion: derived by backlog-gather finish; leave it out of the analysis data
  - contention.claims: derived from the areas the issues list; leave it out of the analysis data
  - #1: progress is derived by backlog-gather finish; leave it out of the analysis data
  - #2 lists the area lexer, which is not in areas
  - area empty: paths must be a non-empty list of path patterns
  - #41 is open but missing from the board data
  - #99 is in the board data but is not an open issue in the gather
[1]
```

```scrut
$ backlog finish "${work}/gather.json" "${work}/missing.json" "${work}/out.json" 2>&1 | sed "s|${work}|WORK|g"
backlog-gather: cannot read WORK/missing.json
[1]
```

## A config that marks a label both progress and claim is refused

```scrut
$ config_with '.claimLabels = ["In Progress"] | .quietDays = 40 | .colour = "red"' && backlog gather acme/widgets "${work}/x.json" 2>&1 | sed "s|${work}|WORK|g"
backlog-gather: WORK/config/report-boards/backlog-triage/github.com/acme/widgets.json is not a valid backlog config:
  - colour: not a config key; expected one of progressLabels, claimLabels, quietDays, staleDays, affinityWorkDays, affinityCommentDays, uniformityShare, uniformityMinimum
[1]
```

```scrut
$ config_with '.claimLabels = ["In Progress"] | .quietDays = 40' && backlog gather acme/widgets "${work}/x.json" 2>&1 | sed "s|${work}|WORK|g"
backlog-gather: WORK/config/report-boards/backlog-triage/github.com/acme/widgets.json is not a valid backlog config:
  - claimLabels: In Progress is also a progress label; a label marks work started or claims an issue, not both
  - quietDays: expected fewer days than staleDays, 30
[1]
```

## A pull request and its own head branch carry the issue once

Pushing `fix/10-ready`, the head of pull request `#100`, adds no carrier and
no `multiple` flag, and its newer commit becomes the issue's last activity.

```scrut
$ config_with && git switch -q -c fix/10-ready main && commit_at 2026-10-14T12:00:00Z ben@example.com fix/ready.c && git push -q origin fix/10-ready && git switch -q main && backlog gather acme/widgets "${work}/head.json" > /dev/null && jq -c '.issues[] | select(.number == 10) | .progress | {carrier, extraCarriers, flags, lastActivity}' "${work}/head.json"; git push -q origin --delete fix/10-ready && git branch -q -D fix/10-ready
{"carrier":{"pr":100},"extraCarriers":[{"label":"In Progress"}],"flags":["behind"],"lastActivity":"2026-10-14T12:00:00Z"}
```

## Lists GitHub cut short are named, and the gather goes on

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp -R "${BACKLOG_GATHER_DATA_DIR}/github/." "${dir}/" && jq '(.. | objects | select(.number? == 11 and has("assignees")) | .assignees.pageInfo) = {hasNextPage: true}' "${BACKLOG_GATHER_DATA_DIR}/github/graphql/issues.json" > "${dir}/graphql/issues.json" && backlog STUB_GH_DIR="${dir}" gather acme/widgets "${work}/cut.json" 2>&1 > /dev/null; echo "exit ${?}"
backlog-gather: GitHub cut these lists short, so an item past the cut is missing:
  - #11: assignees
exit 0
```

## Progress lists cut short stop the gather

A progress label, linked pull request or cross-reference past the cut would read as no progress.

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp -R "${BACKLOG_GATHER_DATA_DIR}/github/." "${dir}/" && jq '(.. | objects | select(.number? == 1 and has("labels")) | .labels.pageInfo) = {hasNextPage: true} | (.. | objects | select(.number? == 11 and has("timelineItems")) | .timelineItems.pageInfo) = {hasPreviousPage: true}' "${BACKLOG_GATHER_DATA_DIR}/github/graphql/issues.json" > "${dir}/graphql/issues.json" && backlog STUB_GH_DIR="${dir}" gather acme/widgets "${work}/x.json" 2>&1
backlog-gather: GitHub cut short the lists of #1 (labels), #11 (cross-references), so progress could be missing; the board cannot be trusted
[1]
```

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cp -R "${BACKLOG_GATHER_DATA_DIR}/github/." "${dir}/" && jq '(.. | objects | select(.number? == 40 and has("closingIssuesReferences")) | .closingIssuesReferences.pageInfo) = {hasNextPage: true}' "${BACKLOG_GATHER_DATA_DIR}/github/graphql/pulls.json" > "${dir}/graphql/pulls.json" && backlog STUB_GH_DIR="${dir}" gather acme/widgets "${work}/x.json" 2>&1
backlog-gather: pull requests #40 close more than 100 issues, so an issue past the cut would read as unstarted; the board cannot be trusted
[1]
```

## Gather stops when it cannot trust what it read

```scrut
$ config_with && backlog STUB_GH_GRAPHQL_FAIL=issues gather acme/widgets "${work}/x.json" 2>&1
backlog-gather: issues failed:
  gh: HTTP 502: Bad Gateway (https://api.github.com/graphql)
[1]
```

```scrut
$ backlog gather acme/other "${work}/x.json" 2>&1
backlog-gather: the origin of this checkout is not acme/other on github.com
[1]
```

A lookalike host is not GitHub, so its checkout supplies no branches.

```scrut
$ git remote set-url origin https://evilgithub.com/acme/widgets.git && backlog gather acme/widgets "${work}/x.json" 2>&1; code=$?; git remote set-url origin https://github.com/acme/widgets.git; echo "exit ${code}"
backlog-gather: the origin of this checkout is not acme/widgets on github.com
exit 1
```

```scrut
$ (cd "${work}" && backlog gather acme/widgets "${work}/x.json") 2>&1
backlog-gather: run gather inside a checkout of acme/widgets
[1]
```

## Usage errors

```scrut
$ backlog finish "${work}/gather.json" 2>&1 | sed -n 1p
backlog-gather: finish takes a gather file, the analysis data, and an output path
[2]
```

```scrut
$ backlog frobnicate 2>&1 | sed -n 1p
backlog-gather: unknown command: frobnicate
[2]
```

```scrut
$ backlog gather not-a-repo "${work}/x.json" 2>&1
backlog-gather: expected OWNER/NAME, not not-a-repo
[1]
```
