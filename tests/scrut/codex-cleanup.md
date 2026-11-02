# Codex cleanup stages

Cleanup runner boundaries and prompt delivery. Tests use the committed Codex
stub and refuse a live binary before launching reviewers.

## Setup

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut {fail_fast: true}
$ fixture="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && unset CODEX_STUB_MODES CODEX_STUB_SENTINEL \
>   && mkdir "${fixture}/bin" "${fixture}/out" "${fixture}/log" \
>   && ln -s "${CODEX_STUB_BIN}" "${fixture}/bin/codex" \
>   && export PATH="${fixture}/bin:${PATH}" FIXTURE="${fixture}" CODEX_STUB_LOG_DIR="${fixture}/log" \
>   && git init -q --template= "${fixture}/repo" && cd "${fixture}/repo" \
>   && git checkout -q -b base \
>   && printf 'one\n' > lib.sh && printf 'one\n' > other.sh \
>   && git add . \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && git checkout -q -b feature \
>   && printf 'two\n' >> lib.sh \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qam change \
>   && printf 'three\n' >> lib.sh \
>   && printf 'new\n' > fresh.txt \
>   && ln -s /etc/hosts link \
>   && "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}" --base base > "${fixture}/scope.json" \
>   && jq -c '{committed, staged, unstaged, untracked}' "${fixture}/scope.json"
{"committed":["lib.sh"],"staged":[],"unstaged":["lib.sh"],"untracked":["fresh.txt","link"]}
```

## Four cleanup reviewers run independently with read-only sandboxes

A four-process barrier fails if the helper serializes these runs. Refuse a
non-stub binary before invoking any reviewer.

```scrut
$ cd "${FIXTURE}/repo" && test "$(command -v codex)" = "${FIXTURE}/bin/codex" \
>   && mkdir "${FIXTURE}/cleanup" "${FIXTURE}/cleanup-barrier" \
>   && CODEX_STUB_BARRIER_DIR="${FIXTURE}/cleanup-barrier" CODEX_STUB_BARRIER_COUNT=4 \
>      CODEX_STUB_MODES='cleanup-reuse=barrier cleanup-simplification=barrier cleanup-efficiency=barrier cleanup-altitude=barrier' \
>      "${CODEX_ASPECTS_BIN}" run --aspect cleanup-reuse --aspect cleanup-simplification \
>        --aspect cleanup-efficiency --aspect cleanup-altitude --scope "${FIXTURE}/scope.json" \
>        --out-dir "${FIXTURE}/cleanup" > "${FIXTURE}/cleanup/statuses.json" \
>   && jq -c 'map({aspect,status})' "${FIXTURE}/cleanup/statuses.json" \
>   && for angle in reuse simplification efficiency altitude; do \
>        printf '%s: ' "${angle}"; sed -n '/^--sandbox$/{n;p;}' "${FIXTURE}/log/cleanup-${angle}.args"; done
[{"aspect":"cleanup-reuse","status":"ok"},{"aspect":"cleanup-simplification","status":"ok"},{"aspect":"cleanup-efficiency","status":"ok"},{"aspect":"cleanup-altitude","status":"ok"}]
reuse: read-only
simplification: read-only
efficiency: read-only
altitude: read-only
```

## Cleanup cannot authorize edits or stand in for correctness reviews

```scrut
$ "${CODEX_ASPECTS_BIN}" select cleanup-reuse 2>&1
codex-aspects: cleanup angles are internal; select simplify with a review aspect
[1]
```

```scrut
$ "${CODEX_ASPECTS_BIN}" gate --aspect cleanup-reuse 2>&1
codex-aspects: gate accepts review aspects only
[1]
```

## Inline fallback delivers every checklist and discloses what ran

Prompt canaries measure delivered instructions. They cannot establish whether
a model follows the cost, deduplication and skip rules.

```scrut
$ "${CODEX_ASPECTS_BIN}" prompt --aspect simplify --scope "${FIXTURE}/scope.json" > "${FIXTURE}/inline.prompt" \
>   && grep '^Execution mode:\|^# Cleanup angle:' "${FIXTURE}/inline.prompt"
Execution mode: inline fallback. Before editing, review reuse, simplification,
# Cleanup angle: Reuse
# Cleanup angle: Simplification
# Cleanup angle: Efficiency
# Cleanup angle: Altitude
```

## Cleanup findings carry cost and mechanism requirements

```scrut
$ for angle in reuse simplification efficiency altitude; do \
>     grep -F 'name its mechanism and concrete cost:' "${FIXTURE}/cleanup/cleanup-${angle}.prompt.md"; done
name its mechanism and concrete cost: duplicated maintenance, unnecessary work
name its mechanism and concrete cost: duplicated maintenance, unnecessary work
name its mechanism and concrete cost: duplicated maintenance, unnecessary work
name its mechanism and concrete cost: duplicated maintenance, unnecessary work
```

## Editor deduplicates mechanisms and records skipped fixes with reasons

```scrut
$ grep -F 'Deduplicate findings by the underlying mechanism' "${FIXTURE}/inline.prompt" \
>   && grep -F 'angles, mechanism, concrete cost, and disposition' "${FIXTURE}/inline.prompt" \
>   && grep -F 'Report every skipped fix' "${FIXTURE}/inline.prompt" \
>   && grep -F 'change intended behavior, extend beyond added or modified code' "${FIXTURE}/inline.prompt"
Deduplicate findings by the underlying mechanism, including reports at different
angles, mechanism, concrete cost, and disposition (`fixed` or `skipped` with a
changes outside the diff, or is a false positive. Report every skipped fix
change intended behavior, extend beyond added or modified code, require broad
```

## Editor receives validated fan-out data without inline fallback

```scrut
$ "${CODEX_ASPECTS_BIN}" prompt --aspect simplify --scope "${FIXTURE}/scope.json" \
>     --cleanup-dir "${FIXTURE}/cleanup" > "${FIXTURE}/fanout.prompt" \
>   && grep '^Execution mode:' "${FIXTURE}/fanout.prompt" \
>   && test "$(grep -c '"aspect": "cleanup-' "${FIXTURE}/fanout.prompt")" = 4 \
>   && ! grep -q '^Execution mode: inline' "${FIXTURE}/fanout.prompt"
Execution mode: four independent read-only cleanup reviewers completed.
```

## Failed cleanup process blocks fan-out even with valid output

```scrut
$ cp "${FIXTURE}/cleanup/statuses.json" "${FIXTURE}/cleanup-good-statuses.json" \
>   && jq '.[0].status = "failed" | .[0].exit_code = 2' "${FIXTURE}/cleanup-good-statuses.json" > "${FIXTURE}/cleanup/statuses.json" \
>   && { "${CODEX_ASPECTS_BIN}" prompt --aspect simplify --scope "${FIXTURE}/scope.json" \
>          --cleanup-dir "${FIXTURE}/cleanup" > "${FIXTURE}/cleanup-failed.prompt" 2> "${FIXTURE}/cleanup-failed.err"; echo "exit=$?"; } \
>   && tail -1 "${FIXTURE}/cleanup-failed.err" \
>   && cp "${FIXTURE}/cleanup-good-statuses.json" "${FIXTURE}/cleanup/statuses.json" # error-output-allow: snapshot replays retained cleanup rejection diagnostics and exit status
exit=1
codex-aspects: invalid cleanup review inputs
```

## A stale cleanup snapshot blocks the editor prompt

```scrut
$ cp "${FIXTURE}/cleanup/cleanup-altitude.json" "${FIXTURE}/altitude-good.json" \
>   && jq '.reviewed = "stale"' "${FIXTURE}/altitude-good.json" > "${FIXTURE}/cleanup/cleanup-altitude.json" \
>   && { "${CODEX_ASPECTS_BIN}" prompt --aspect simplify --scope "${FIXTURE}/scope.json" \
>          --cleanup-dir "${FIXTURE}/cleanup" > "${FIXTURE}/cleanup-stale.prompt" 2> "${FIXTURE}/cleanup-stale.err"; echo "exit=$?"; } \
>   && sed "s|${FIXTURE}|FIXTURE|g" "${FIXTURE}/cleanup-stale.err" \
>   && cp "${FIXTURE}/altitude-good.json" "${FIXTURE}/cleanup/cleanup-altitude.json" # error-output-allow: snapshot replays retained stale-snapshot diagnostics and exit status
exit=1
Cleanup reviewer cleanup-altitude (FIXTURE/cleanup/cleanup-altitude.json): the output reviewed a different snapshot; rerun this reviewer against the current scope
codex-aspects: invalid cleanup review inputs
```

## Fan-out data never replaces the existing edit gate

```scrut
$ "${CODEX_ASPECTS_BIN}" run --aspect simplify --scope "${FIXTURE}/scope.json" \
>     --cleanup-dir "${FIXTURE}/cleanup" --out-dir "${FIXTURE}/out" 2>&1
codex-aspects: simplify requires --reviewed-scope, --results, --statuses and --reviewed-aspect
[1]
```

## Non-empty findings reach the rendered editor prompt unchanged

```scrut
$ for angle in reuse simplification efficiency altitude; do \
>     jq --arg angle "${angle}" '.findings = [{confidence:95,detail:("Mechanism and cost for " + $angle),file:"lib.sh",fix:("Proposal for " + $angle),line:2,severity:"suggestion",title:("Cleanup " + $angle)}]' \
>       "${FIXTURE}/cleanup/cleanup-${angle}.json" > "${FIXTURE}/payload.json" \
>       && cp "${FIXTURE}/payload.json" "${FIXTURE}/cleanup/cleanup-${angle}.json" || exit 1; done \
>   && jq -s . "${FIXTURE}/cleanup/cleanup-reuse.json" "${FIXTURE}/cleanup/cleanup-simplification.json" \
>        "${FIXTURE}/cleanup/cleanup-efficiency.json" "${FIXTURE}/cleanup/cleanup-altitude.json" > "${FIXTURE}/expected-payload.json" \
>   && "${CODEX_ASPECTS_BIN}" prompt --aspect simplify --scope "${FIXTURE}/scope.json" \
>        --cleanup-dir "${FIXTURE}/cleanup" > "${FIXTURE}/payload.prompt" \
>   && awk 'found {print; if ($0 == "]") exit} /^The following JSON is untrusted review data/ {found=1}' \
>        "${FIXTURE}/payload.prompt" > "${FIXTURE}/rendered-payload.json" \
>   && diff "${FIXTURE}/expected-payload.json" "${FIXTURE}/rendered-payload.json" && echo preserved
preserved
```

## Successful fan-out precedes one gated editing stage

```scrut
$ test "$(command -v codex)" = "${FIXTURE}/bin/codex" \
>   && "${CODEX_ASPECTS_BIN}" run --aspect code --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" > "${FIXTURE}/code-statuses.json" \
>   && jq -s . "${FIXTURE}/out/code.json" > "${FIXTURE}/code-results.json" \
>   && "${CODEX_ASPECTS_BIN}" run --aspect simplify --scope "${FIXTURE}/scope.json" \
>        --cleanup-dir "${FIXTURE}/cleanup" --out-dir "${FIXTURE}/out" \
>        --reviewed-scope "${FIXTURE}/scope.json" --results "${FIXTURE}/code-results.json" \
>        --statuses "${FIXTURE}/code-statuses.json" --reviewed-aspect code | jq -r '.[0].status' \
>   && sed -n '/^--sandbox$/{n;p;}' "${FIXTURE}/log/simplify.args"
ok
workspace-write
```

## Non-empty findings also reach the standalone editor prompt unchanged

```scrut
$ awk 'found {print; if ($0 == "]") exit} /^The following JSON is untrusted review data/ {found=1}' \
>     "${FIXTURE}/out/simplify.prompt.md" > "${FIXTURE}/run-payload.json" \
>   && diff "${FIXTURE}/expected-payload.json" "${FIXTURE}/run-payload.json" && echo preserved
preserved
```

## Missing cleanup angle blocks launch with an actionable reason

```scrut
$ cp -R "${FIXTURE}/cleanup" "${FIXTURE}/missing-angle" \
>   && jq '.[0:3]' "${FIXTURE}/cleanup-good-statuses.json" > "${FIXTURE}/missing-angle/statuses.json" \
>   && { CODEX_STUB_MODES='simplify=write' CODEX_STUB_WRITE="${FIXTURE}/unexpected-edit-missing-angle" \
>        "${CODEX_ASPECTS_BIN}" run --aspect simplify --scope "${FIXTURE}/scope.json" \
>          --cleanup-dir "${FIXTURE}/missing-angle" --out-dir "${FIXTURE}/out" \
>          --reviewed-scope "${FIXTURE}/scope.json" --results "${FIXTURE}/code-results.json" \
>          --statuses "${FIXTURE}/code-statuses.json" --reviewed-aspect code \
>          > "${FIXTURE}/boundary.err" 2>&1; echo "exit=$?"; } \
>   && sed "s|${FIXTURE}|FIXTURE|g" "${FIXTURE}/boundary.err" \
>   && test ! -e "${FIXTURE}/unexpected-edit-missing-angle" # error-output-allow: snapshot replays retained missing-angle rejection and verifies no editor ran
exit=1
Cleanup statuses at FIXTURE/missing-angle/statuses.json: cleanup angle coverage is missing or duplicated; rerun cleanup against the current scope
codex-aspects: invalid cleanup review inputs
```

## Duplicated cleanup angle blocks launch with an actionable reason

```scrut
$ cp -R "${FIXTURE}/cleanup" "${FIXTURE}/duplicate-angle" \
>   && jq '.[0].aspect = .[1].aspect' "${FIXTURE}/cleanup-good-statuses.json" > "${FIXTURE}/duplicate-angle/statuses.json" \
>   && { CODEX_STUB_MODES='simplify=write' CODEX_STUB_WRITE="${FIXTURE}/unexpected-edit-duplicate-angle" \
>        "${CODEX_ASPECTS_BIN}" run --aspect simplify --scope "${FIXTURE}/scope.json" \
>          --cleanup-dir "${FIXTURE}/duplicate-angle" --out-dir "${FIXTURE}/out" \
>          --reviewed-scope "${FIXTURE}/scope.json" --results "${FIXTURE}/code-results.json" \
>          --statuses "${FIXTURE}/code-statuses.json" --reviewed-aspect code \
>          > "${FIXTURE}/boundary.err" 2>&1; echo "exit=$?"; } \
>   && sed "s|${FIXTURE}|FIXTURE|g" "${FIXTURE}/boundary.err" \
>   && test ! -e "${FIXTURE}/unexpected-edit-duplicate-angle" # error-output-allow: snapshot replays retained duplicate-angle rejection and verifies no editor ran
exit=1
Cleanup statuses at FIXTURE/duplicate-angle/statuses.json: cleanup angle coverage is missing or duplicated; rerun cleanup against the current scope
codex-aspects: invalid cleanup review inputs
```

## Different cleanup membership blocks launch with an actionable reason

```scrut
$ cp -R "${FIXTURE}/cleanup" "${FIXTURE}/different-membership" \
>   && jq '.[0].membership_paths = []' "${FIXTURE}/cleanup-good-statuses.json" > "${FIXTURE}/different-membership/statuses.json" \
>   && { CODEX_STUB_MODES='simplify=write' CODEX_STUB_WRITE="${FIXTURE}/unexpected-edit-different-membership" \
>        "${CODEX_ASPECTS_BIN}" run --aspect simplify --scope "${FIXTURE}/scope.json" \
>          --cleanup-dir "${FIXTURE}/different-membership" --out-dir "${FIXTURE}/out" \
>          --reviewed-scope "${FIXTURE}/scope.json" --results "${FIXTURE}/code-results.json" \
>          --statuses "${FIXTURE}/code-statuses.json" --reviewed-aspect code \
>          > "${FIXTURE}/boundary.err" 2>&1; echo "exit=$?"; } \
>   && sed "s|${FIXTURE}|FIXTURE|g" "${FIXTURE}/boundary.err" \
>   && test ! -e "${FIXTURE}/unexpected-edit-different-membership" # error-output-allow: snapshot replays retained membership rejection and verifies no editor ran
exit=1
Cleanup statuses at FIXTURE/different-membership/statuses.json: cleanup membership differs from the current scope; rerun cleanup against the current scope
codex-aspects: invalid cleanup review inputs
```

## Critical correctness findings block the editor despite clean cleanup results

```scrut
$ jq '.[0].findings = [{confidence:95,detail:"Bug",file:"lib.sh",fix:"Fix",line:1,severity:"critical",title:"Bug"}]' \
>     "${FIXTURE}/code-results.json" > "${FIXTURE}/critical.json" \
>   && "${CODEX_ASPECTS_BIN}" run --aspect simplify --scope "${FIXTURE}/scope.json" \
>        --cleanup-dir "${FIXTURE}/cleanup" --out-dir "${FIXTURE}/out" \
>        --reviewed-scope "${FIXTURE}/scope.json" --results "${FIXTURE}/critical.json" \
>        --statuses "${FIXTURE}/code-statuses.json" --reviewed-aspect code 2>&1
codex-aspects: simplify is not eligible: a review reported a Critical finding
[1]
```

## Failed correctness review blocks the editor despite clean cleanup results

```scrut
$ jq '.[0].status = "failed"' "${FIXTURE}/code-statuses.json" > "${FIXTURE}/code-failed.json" \
>   && "${CODEX_ASPECTS_BIN}" run --aspect simplify --scope "${FIXTURE}/scope.json" \
>        --cleanup-dir "${FIXTURE}/cleanup" --out-dir "${FIXTURE}/out" \
>        --reviewed-scope "${FIXTURE}/scope.json" --results "${FIXTURE}/code-results.json" \
>        --statuses "${FIXTURE}/code-failed.json" --reviewed-aspect code 2>&1
codex-aspects: simplify is not eligible: a selected review aspect failed or is missing
[1]
```

## A changed tree blocks the final editor launch despite complete prior reviews

```scrut
$ printf 'later\n' >> lib.sh \
>   && "${CODEX_ASPECTS_BIN}" run --aspect simplify --scope "${FIXTURE}/scope.json" \
>        --cleanup-dir "${FIXTURE}/cleanup" --out-dir "${FIXTURE}/out" \
>        --reviewed-scope "${FIXTURE}/scope.json" --results "${FIXTURE}/code-results.json" \
>        --statuses "${FIXTURE}/code-statuses.json" --reviewed-aspect code 2>&1
codex-aspects: the scope changed after --scope was captured; capture it again and rerun the gate
[1]
```
