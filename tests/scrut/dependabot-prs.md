# Dependabot PR summaries

Tests for the `dependabot-prs` script that `triage-dependabot-prs` bundles. `summarize` reduces a fetched bundle of open Dependabot PRs, other open PRs, comparisons of each head against its base branch, and Dependabot alerts to the evidence a triage needs.

`fetch` is not exercised past its argument checks: it requires an authenticated `gh`, which the test environment does not have. `summarize` is the seam that makes the parsing testable without one. The fixtures are synthetic bundles modeled on real Dependabot PRs, including the layouts that break naive parsing: grouped bodies repeated per directory, bodies truncated at the size limit, footers removed by a rebase, and titles updated in place.

## Help

```scrut
$ "${DEPENDABOT_PRS_BIN}" --help | head -n 1
Usage: dependabot-prs <command> [options]
```

## A single-dependency action bump

The ecosystem comes from the branch, the versions from the title, and the kind from the commands footer.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 101) | {ecosystem, kind, shape, group, updates, branchAgrees}'
{"ecosystem":"github_actions","kind":"version","shape":"single","group":null,"updates":[{"name":"actions/setup-go","from":"6.4.0","to":"7.0.0","type":"major","semverBreaking":true}],"branchAgrees":true}
```

## Ages are measured from the bundle's fetch time

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 101) | {ageDays, updatedDaysAgo}'
{"ageDays":3,"updatedDaysAgo":1}
```

`--now` overrides the fetch time, so a saved bundle can be re-read later.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize --now 2026-09-20T12:00:00Z < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 101) | {ageDays, updatedDaysAgo}'
{"ageDays":10,"updatedDaysAgo":8}
```

## Check runs are counted by state

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 101) | .checks'
{"total":3,"success":2,"failure":0,"pending":0,"skipped":1,"neutral":0,"failing":[],"newestCompletedAt":"2026-09-12T10:05:00Z"}
```

Commit statuses count too. A queued check run is pending, and a status context has no completion time.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 104) | .checks | {total, success, pending, newestCompletedAt}'
{"total":2,"success":1,"pending":1,"newestCompletedAt":null}
```

Failing check runs and failing statuses are both named.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 105) | .checks | {failure, failing}'
{"failure":2,"failing":["build","netlify/example/deploy-preview"]}
```

## A grouped PR across directories

A grouped body repeats the Updates line for each directory a dependency appears in. The repeats collapse, and the count agrees with the title.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 102) | {shape, group, updatesExpected, updates: [.updates[] | "\(.name) \(.from) \(.to) \(.type)"]}'
{"shape":"group","group":"github-actions-minor-patch","updatesExpected":2,"updates":["actions/checkout 7.0.0 7.0.1 patch","actions/cache 5.0.5 5.1.0 minor"]}
```

## A security update is matched to its alerts

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 103) | {kind, group, alerts: [.alerts[] | "\(.number) \(.package) \(.severity) \(.patched)"]}'
{"kind":"security","group":"go_modules","alerts":["21 golang.org/x/crypto critical 0.52.0","22 golang.org/x/crypto medium 0.52.0"]}
```

## A 0.x minor bump is a SemVer break

`type` names the position that changed. `semverBreaking` records that SemVer promises nothing below 1.0.0.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 109) | .updates'
[{"name":"markdownlint-cli2","from":"0.21.0","to":"0.23.2","type":"minor","semverBreaking":true}]
```

A patch bump inside 1.x is not.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/limited.json" | jq -c '.prs[0].updates'
[{"name":"left-pad","from":"1.3.0","to":"1.3.1","type":"patch","semverBreaking":false}]
```

## Draft and auto-merge state

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 109) | {draft, autoMerge, reviewDecision}'
{"draft":true,"autoMerge":true,"reviewDecision":"REVIEW_REQUIRED"}
```

## A commit-pinned action is a digest update

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 104) | .updates[] | {type, semverBreaking}'
{"type":"digest","semverBreaking":null}
```

## A body without the commands footer is unknown, not a version update

A rebase can rewrite the body without the footer, and the security line lives in that footer.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 104) | {kind, commandsFooter}'
{"kind":"unknown","commandsFooter":false}
```

## A stale PR against a non-default base

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 105) | {base, baseIsDefault, rebasesDisabled, mergeStateStatus, compare}'
{"base":"staging","baseIsDefault":false,"rebasesDisabled":true,"mergeStateStatus":"DIRTY","compare":{"status":"diverged","aheadBy":2,"behindBy":62,"nonDependabotCommits":1}}
```

A failed comparison is reported as null rather than guessed at.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 104) | .compare'
null
```

## Overlapping files are reported against every open PR

Another Dependabot PR bumping the same dependency to a newer version:

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 105) | .overlaps'
[{"number":106,"author":"app/dependabot","sharedFiles":["web/package-lock.json","web/package.json"]}]
```

A human PR touching the same manifest:

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 103) | .overlaps'
[{"number":90,"author":"octocat","sharedFiles":["go.mod"]}]
```

## A body truncated at the size limit

The title announces three updates, but only two Updates lines survived the truncation, and the footer went with them.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 107) | {bodyTruncated, commandsFooter, kind, updatesExpected, parsed: (.updates | length)}'
{"bodyTruncated":true,"commandsFooter":false,"kind":"unknown","updatesExpected":3,"parsed":2}
```

## A title updated in place disagrees with its branch

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 108) | {branch, to: .updates[0].to, branchAgrees}'
{"branch":"dependabot/npm_and_yarn/sinon-21.1.2","to":"22.0.0","branchAgrees":false}
```

## A multi-dependency update

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 110) | {shape, kind, names: [.updates[].name], alerts: [.alerts[].number]}'
{"shape":"multi","kind":"security","names":["markdown-it","markdownlint-cli2"],"alerts":[23]}
```

## Versions that do not parse are unknown

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.prs[] | select(.number == 111) | {ecosystem, updates}'
{"ecosystem":"docker","updates":[{"name":"ubuntu","from":"jammy-20240101","to":"noble-20240601","type":"unknown","semverBreaking":null}]}
```

## Alerts no PR addresses are grouped by package

Highest severity first. These are alerts with no fix path through Dependabot.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '.unmatchedAlerts[]'
{"package":"minimist","manifest":"web/package-lock.json","count":1,"highestSeverity":"critical","patched":["1.2.6"],"numbers":[26]}
{"package":"lodash","manifest":"yarn.lock","count":2,"highestSeverity":"high","patched":["4.17.21"],"numbers":[24,25]}
```

## Top-level counts

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/mixed.json" | jq -c '{repo, defaultBranch, isArchived, count, limitReached, alertsAvailable}'
{"repo":"example-org/example-repo","defaultBranch":"main","isArchived":false,"count":11,"limitReached":false,"alertsAvailable":true}
```

## A list cut off at the limit, alerts refused, and an archived repository

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/limited.json" | jq -c '{isArchived, limit, limitReached, alertsAvailable, alertsReason}'
{"isArchived":true,"limit":1,"limitReached":true,"alertsAvailable":false,"alertsReason":"gh: Resource not accessible by integration (HTTP 403)"}
```

A bundle with no other open PRs and no comparisons still summarizes.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/limited.json" | jq -c '.prs[0] | {kind, overlaps, compare, alerts}'
{"kind":"unknown","overlaps":[],"compare":null,"alerts":[]}
```

## No open Dependabot PRs

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/empty.json" | jq -c '{count, unmatchedAlerts, prs}'
{"count":0,"unmatchedAlerts":[],"prs":[]}
```

## A short digest in backticks is a digest

Container digest titles wrap short SHAs in backticks. The backticks are stripped before comparing with the branch.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 201) | {updates, branchAgrees}'
{"updates":[{"name":"node","from":"6f7ab5c","to":"0e9c10a","type":"digest","semverBreaking":null}],"branchAgrees":true}
```

## A title without versions falls back to the body lead

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 202) | {updates, branchAgrees}'
{"updates":[{"name":"vendor/lib","from":"08c6903","to":"11bd719","type":"digest","semverBreaking":null}],"branchAgrees":null}
```

## A requirement update keeps its range, and its branch is not compared

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 203) | {updates, branchAgrees}'
{"updates":[{"name":"rake","from":"~> 12.3","to":"~> 13.0","type":"major","semverBreaking":true}],"branchAgrees":null}
```

## Updates lines outrank a stale title

The body was regenerated with the newer version, trailing whitespace and all, while the title still names the old one.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 204) | {to: .updates[0].to, branchAgrees}'
{"to":"1.2.0","branchAgrees":false}
```

## A 0.0.x patch bump is a SemVer break

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 205) | .updates[0] | {type, semverBreaking}'
{"type":"patch","semverBreaking":true}
```

## Every check state is counted, and a zero completion time is ignored

Neutral is its own count. Cancelled, stale, and errored count as failures. In progress and expected are pending, and an unfinished run's zero timestamp does not become the newest completion.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 205) | .checks'
{"total":6,"success":0,"failure":3,"pending":2,"skipped":0,"neutral":1,"failing":["cancelled","stale","errored"],"newestCompletedAt":"2026-09-12T02:00:00Z"}
```

## Alerts match on package, ecosystem, and a dependency file in the same directory

The lockfile the PR touches sits beside the alert's `web/package.json`, so alert 31 matches. Alert 32 names the same package in another directory, and alert 33 names it in another ecosystem.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 206) | {alerts: [.alerts[].number]}'
{"alerts":[31]}
```

A file that is not a dependency file does not make a match, even in the manifest's directory.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 207) | {alerts: [.alerts[].number]}'
{"alerts":[]}
```

## A matched alert says whether the PR clears it

A PR can update a vulnerable package and still stop short of the first patched version. Here tiny moves to 0.0.4, and the advisory is fixed in 0.1.0.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '[.prs[] | select(.number == 205 or .number == 206) | {number, alerts: [.alerts[] | {number, cleared}]}]'
[{"number":205,"alerts":[{"number":37,"cleared":false}]},{"number":206,"alerts":[{"number":31,"cleared":true}]}]
```

A grouped PR that moves one package to different versions in different directories cannot say which target applies to an alert's manifest, so `cleared` is null.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 208) | {alerts: [.alerts[] | {number, cleared}]}'
{"alerts":[{"number":38,"cleared":null}]}
```

A pre-release target is not compared at all. Reading `2.0.0-rc.1` as `2.0.0` would call an alert patched in `2.0.0` cleared when it is not.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 209) | {alerts: [.alerts[] | {number, cleared}]}'
{"alerts":[{"number":39,"cleared":null}]}
```

## A group across directories ties each package to its directory

A grouped body names the dependencies it updates in each directory on its `Bumps` lines. The `Updates` lines carry no directory, so those lines are the only record of which package moves where.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 210) | .directories'
[{"directory":"web","names":["lodash"]},{"directory":"api","names":["qs"]}]
```

This group updates lodash in `/web` and qs in `/api`, touching both lockfiles. The lodash alert in `/api` stays unmatched, because the `/api` line names only qs.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 210) | {alerts: [.alerts[] | {number, directoryConfirmed, cleared}]}'
{"alerts":[{"number":31,"directoryConfirmed":true,"cleared":true},{"number":40,"directoryConfirmed":true,"cleared":true}]}
```

A `Bumps` line with a long list leaves the names off. An alert in that directory is attached but unconfirmed, with `cleared` null, while an alert in a directory whose line names other packages is not attached.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 211) | {directories, alerts: [.alerts[] | {number, directoryConfirmed, cleared}]}'
{"directories":[{"directory":"mjx","names":["pip","setuptools"]},{"directory":"python","names":[]}],"alerts":[{"number":41,"directoryConfirmed":false,"cleared":null}]}
```

For GitHub Actions, the `/` directory covers `.github/workflows`, so a workflow alert matches the `/` line and a composite action alert matches its own.

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.prs[] | select(.number == 212) | {alerts: [.alerts[] | {number, directoryConfirmed, cleared}]}'
{"alerts":[{"number":43,"directoryConfirmed":true,"cleared":true}]}
```

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '[.unmatchedAlerts[] | select(.package == "lodash" or .package == "pillow" or .package == "actions/checkout") | {package, manifest}]'
[{"package":"lodash","manifest":"api/package-lock.json"},{"package":"pillow","manifest":"mjx/requirements.txt"},{"package":"actions/checkout","manifest":".github/actions/setup/action.yml"},{"package":"lodash","manifest":"web/requirements.txt"}]
```

## Patched versions sort by version, not as strings

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < "${DEPENDABOT_PRS_DATA_DIR}/edge-cases.json" | jq -c '.unmatchedAlerts[] | select(.package == "qs") | .patched'
["6.2.4","6.10.0"]
```

## Malformed input is rejected with a reason

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize < /dev/null 2>&1
Error: Invalid bundle: input is empty.
[1]
```

```scrut
$ echo 'not json' | "${DEPENDABOT_PRS_BIN}" summarize 2>&1
Error: Invalid bundle: could not parse input as JSON.
[1]
```

```scrut
$ echo '[]' | "${DEPENDABOT_PRS_BIN}" summarize 2>&1
Error: Invalid bundle: expected an object, got array. Pass the output of: dependabot-prs fetch --repo OWNER/REPO --raw
[1]
```

```scrut
$ echo '{"repo":"a/b"}' | "${DEPENDABOT_PRS_BIN}" summarize 2>&1
Error: Invalid bundle: missing required field(s): defaultBranch, dependabot.
[1]
```

```scrut
$ echo '{"repo":"a/b","defaultBranch":"main","dependabot":{}}' | "${DEPENDABOT_PRS_BIN}" summarize 2>&1
Error: Invalid bundle: dependabot must be an array of PR objects.
[1]
```

## A reference time is required

```scrut
$ echo '{"repo":"a/b","defaultBranch":"main","dependabot":[]}' | "${DEPENDABOT_PRS_BIN}" summarize 2>&1
Error: summarize needs --now, or a fetchedAt field in the bundle.
[1]
```

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize --now yesterday < "${DEPENDABOT_PRS_DATA_DIR}/empty.json" 2>&1
Error: Invalid timestamp 'yesterday'. Expected YYYY-MM-DDTHH:MM:SSZ.
[1]
```

## Argument errors

```scrut
$ "${DEPENDABOT_PRS_BIN}" 2>&1 | head -n 1
Usage: dependabot-prs <command> [options]
```

```scrut
$ "${DEPENDABOT_PRS_BIN}" triage 2>&1
Error: Unknown command: triage. Use 'dependabot-prs --help' for usage.
[1]
```

```scrut
$ "${DEPENDABOT_PRS_BIN}" summarize --since 2026-01-01 2>&1
Error: Unknown summarize option: --since. Use 'dependabot-prs --help' for usage.
[1]
```

`fetch` validates its arguments before it checks for `gh`, so these fail the same way with or without credentials.

```scrut
$ "${DEPENDABOT_PRS_BIN}" fetch 2>&1
Error: fetch requires --repo OWNER/REPO
[1]
```

```scrut
$ "${DEPENDABOT_PRS_BIN}" fetch --repo example-repo 2>&1
Error: Invalid --repo 'example-repo'. Expected OWNER/REPO.
[1]
```

```scrut
$ "${DEPENDABOT_PRS_BIN}" fetch --repo example-org/example-repo --limit 0 2>&1
Error: Invalid --limit '0'. Expected a positive integer.
[1]
```
