# Merge flow

Tests for the `merge-flow` script that `monitor-pr` bundles for its merge step. `policy` and `watch` run against `tests/fixtures/gh-stub`, answering from `tests/data/merge-flow/`. `sync` runs against real repositories built in a temporary directory, and `panes` against a `tmux` shim that prints a fixed pane list.

## Setup

`flow` runs the script with the stub `gh` first on `PATH`. `watch` takes a response sequence name and polls with no delay. `clone` builds a fresh local clone of a bare `acme/widgets` remote, set back one commit so that the remote's newest commit stands for a merge the clone has not fetched yet, and prints its path.

```scrut {fail_fast: true}
$ work="$(cd -P "$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && pwd)" \
>   && mkdir "${work}/bin" && ln -s "${GH_STUB_BIN}" "${work}/bin/gh" \
>   && function flow() { PATH="${work}/bin:${PATH}" STUB_GH_DIR="${MERGE_FLOW_DATA_DIR}" "${MERGE_FLOW_BIN}" "$@"; } \
>   && function watch() { local sequence="${1}"; shift; STUB_GH_PR_VIEW="pr-view/${sequence}.txt" STUB_GH_PR_VIEW_STATE="$(mktemp "${work}/state.XXXXXX")" MERGE_FLOW_INTERVAL=0 flow watch acme widgets 7 1111111111111111111111111111111111111111 "$@"; } \
>   && function git_quiet() { git -c init.defaultBranch=main -c user.name=Test -c user.email=test@example.com "$@" > /dev/null 2>&1; } \
>   && mkdir -p "${work}/remote/acme" && git_quiet init --bare "${work}/remote/acme/widgets.git" \
>   && git_quiet clone "${work}/remote/acme/widgets.git" "${work}/seed" \
>   && git_quiet -C "${work}/seed" commit --allow-empty -m base && git_quiet -C "${work}/seed" push origin main \
>   && function clone() { local dir; dir="$(mktemp -d "${work}/clone.XXXXXX")"; git_quiet clone "${work}/remote/acme/widgets.git" "${dir}" && git_quiet -C "${dir}" reset --hard HEAD~1 && git -C "${dir}" update-ref refs/remotes/origin/main HEAD && printf '%s\n' "${dir}"; } \
>   && git_quiet -C "${work}/seed" commit --allow-empty -m merged && git_quiet -C "${work}/seed" push origin main \
>   && merge_sha="$(git -C "${work}/seed" rev-parse HEAD)" \
>   && function sync() { local dir="${1}"; shift; (cd "${dir}" && "${MERGE_FLOW_BIN}" sync "$@"); } \
>   && echo ready
ready
```

## Help

```scrut
$ "${MERGE_FLOW_BIN}" --help | head -n 1
Usage: merge-flow <command> [arguments]
```

An unknown command is a usage error.

```scrut
$ "${MERGE_FLOW_BIN}" unmerge 2>&1
merge-flow: unknown command unmerge
Run 'merge-flow --help' for usage.
[2]
```

## Policy: a ruleset narrows the repository settings

The settings allow merge commits and squash, but the base branch's ruleset allows only squash and requires an approval.

```scrut
$ flow policy acme widgets main | jq -c '{allowed, approvals, settings, rules}'
{"allowed":["squash"],"approvals":1,"settings":["merge","squash"],"rules":[["squash"]]}
```

With no rules on the base branch, the settings decide alone.

```scrut
$ flow policy acme widgets dev | jq -c '{allowed, approvals}'
{"allowed":["merge","squash"],"approvals":0}
```

## Policy: hidden settings are unknown, not empty

Without admin access, GitHub reports every merge setting as null. That reads as unknown, so the rules decide alone.

```scrut
$ flow policy acme hidden main | jq -c '{allowed, settings, settingsNote}'
{"allowed":["squash"],"settings":null,"settingsNote":"the repository merge settings are not visible to this account, which usually means it lacks admin access"}
```

With no rules either, nothing is known about the methods.

```scrut
$ flow policy acme hidden dev | jq -c '{allowed, approvals}'
{"allowed":null,"approvals":0}
```

## Policy: failed reads are reported, not read as empty

A failed rules read leaves both the rules and the approval requirement unknown.

```scrut
$ STUB_GH_API_FAIL=rules_branches_main flow policy acme widgets main | jq -c '{allowed, approvals, rulesNote}'
{"allowed":["merge","squash"],"approvals":null,"rulesNote":"reading the base branch rules failed: gh: Resource not accessible by integration (HTTP 403)"}
```

A base branch that does not exist is not a branch without rules.

```scrut
$ flow policy acme widgets gone | jq -c '{approvals, rulesNote}'
{"approvals":null,"rulesNote":"reading base branch gone failed, so its rules were not read: gh: Not Found (HTTP 404)"}
```

A failed settings read is reported beside the rules that were read.

```scrut
$ STUB_GH_API_FAIL=repos_acme_widgets flow policy acme widgets main | jq -c '{allowed, settingsNote}'
{"allowed":["squash"],"settingsNote":"reading the repository settings failed: gh: Resource not accessible by integration (HTTP 403)"}
```

## Watch: a merge ends the watch only once it has a merge commit

The third response reports `MERGED` with no merge commit yet, so the watch keeps polling until the fourth names one.

```scrut
$ watch merged
{"event":"merged","state":"MERGED","reviewDecision":"NONE","headRefOid":"1111111111111111111111111111111111111111","mergeCommit":"2222222222222222222222222222222222222222"}
```

## Watch: a close ends the watch

```scrut
$ watch closed | jq -c '{event, mergeCommit}'
{"event":"closed","mergeCommit":null}
```

## Watch: a push ends the watch

A head that differs from the one readiness was declared on ends the watch, so a merge offer is never accepted for commits that were not checked.

```scrut
$ watch pushed | jq -c '{event, headRefOid}'
{"event":"head","headRefOid":"3333333333333333333333333333333333333333"}
```

## Watch: a changed review decision ends an approval wait

```scrut
$ watch approved --awaited REVIEW_REQUIRED | jq -c '{event, reviewDecision}'
{"event":"decision","reviewDecision":"APPROVED"}
```

An empty decision reads as `NONE`, so an approval wait from no decision does not end on it.

```scrut
$ watch closed --awaited NONE | jq -c '{event, reviewDecision}'
{"event":"closed","reviewDecision":"NONE"}
```

## Watch: read failures

A successful read resets the failure count, so isolated failures do not end the watch.

```scrut
$ MERGE_FLOW_MAX_FAILURES=2 watch flaky | jq -c '{event, mergeCommit}'
{"event":"merged","mergeCommit":"2222222222222222222222222222222222222222"}
```

Consecutive failures end it with the last error.

```scrut
$ MERGE_FLOW_MAX_FAILURES=2 watch offline
{"event":"failed","error":"2 consecutive reads failed; last error: error connecting to api.github.com"}
```

A watch that outlives its lifetime ends too.

```scrut
$ MERGE_FLOW_LIFETIME=0 watch merged
{"event":"expired","error":"no merge within 0 seconds"}
```

## Sync: the base branch checked out in the main worktree

```scrut
$ dir="$(clone)" && sync "${dir}" acme widgets main "${merge_sha}" | jq -c --arg dir "${dir}" '{synced, remote, here: (.worktree == $dir), moved: (.before != .after), reason}'
{"synced":true,"remote":"origin","here":true,"moved":true,"reason":null}
```

## Sync: the base branch checked out in another worktree

The fast-forward runs where the branch is checked out, since a branch checked out elsewhere cannot be updated by ref.

```scrut
$ dir="$(clone)" && git_quiet -C "${dir}" switch -c feature && git_quiet -C "${dir}" worktree add "${dir}.main" main \
>   && sync "${dir}" acme widgets main "${merge_sha}" | jq -c --arg wt "${dir}.main" '{synced, there: (.worktree == $wt)}'
{"synced":true,"there":true}
```

## Sync: the base branch not checked out anywhere

```scrut
$ dir="$(clone)" && git_quiet -C "${dir}" switch -c feature && sync "${dir}" acme widgets main "${merge_sha}" | jq -c '{synced, worktree}'
{"synced":true,"worktree":null}
```

## Sync: the remote is found by URL, not by name

A fork layout names the upstream something other than `origin`.

```scrut
$ dir="$(clone)" && git_quiet -C "${dir}" remote rename origin upstream && git_quiet -C "${dir}" remote add origin "${work}/remote/someone/widgets.git" \
>   && sync "${dir}" acme widgets main "${merge_sha}" | jq -c '{synced, remote}'
{"synced":true,"remote":"upstream"}
```

No remote naming the repository is reported.

```scrut
$ dir="$(clone)" && sync "${dir}" acme gadgets main "${merge_sha}" | jq -c '{synced, reason}'
{"synced":false,"reason":"no remote points at acme/gadgets"}
```

## Sync: a fetched base without the merge is not synced

```scrut
$ dir="$(clone)" && sync "${dir}" acme widgets main 4444444444444444444444444444444444444444 | jq -c '{synced, reason}'
{"synced":false,"reason":"origin/main does not contain 4444444444444444444444444444444444444444"}
```

## Sync: a refused fast-forward leaves the worktree alone

A local commit on the base branch makes it diverge, and the refusal is reported with git's own message.

```scrut
$ dir="$(clone)" && git_quiet -C "${dir}" commit --allow-empty -m local && before="$(git -C "${dir}" rev-parse HEAD)" \
>   && sync "${dir}" acme widgets main "${merge_sha}" | jq -c --arg before "${before}" '{synced, kept: (.after == $before), reason: (.reason | test("^fast-forwarding main in .* failed: "))}'
{"synced":false,"kept":true,"reason":true}
```

## Panes: matched by whole path component

Panes in a worktree or below one match, and the deepest worktree wins. A sibling directory whose name only starts with the repository's name does not match.

```scrut
$ repo="${work}/panes/repo" && mkdir -p "${repo}" && git_quiet -C "${repo}" init && git_quiet -C "${repo}" commit --allow-empty -m base \
>   && git_quiet -C "${repo}" worktree add "${work}/panes/repo__worktrees/topic" -b topic \
>   && printf '#!/bin/sh\nprintf "%%s\\n" "%%1 %s" "%%2 %s/src" "%%3 %s" "%%4 %s" "%%5 %s"\n' "${repo}" "${repo}" "${work}/panes/repo__worktrees/topic" "${work}/panes/repo-old" "${work}" > "${work}/bin/tmux" && chmod +x "${work}/bin/tmux" \
>   && (cd "${repo}" && PATH="${work}/bin:${PATH}" "${MERGE_FLOW_BIN}" panes) | jq -c --arg root "${work}/panes/" '[.[] | [.pane, (.worktree | ltrimstr($root))]]'
[["%1","repo"],["%2","repo"],["%3","repo__worktrees/topic"]]
```
