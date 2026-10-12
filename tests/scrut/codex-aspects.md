# Codex aspects

Tests for the `review-pr-with-codex` helper that renders, runs and validates the
review aspects.

`codex` is replaced by `tests/fixtures/codex-stub`, linked into a private `bin`
directory at the front of `PATH`. The stub reads the aspect and snapshot from
the prompt and behaves as `CODEX_STUB_MODES` says for each aspect, so every
failure a real run can have is reproducible without a model.

One fixture repository serves the whole document: a base branch, a feature
branch with one committed change, one unstaged change, an untracked file and an
untracked symlink. Cases that change the tree run in a copy of it.

## Setup

```scrut
$ fixture="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
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

## Help

```scrut
$ "${CODEX_ASPECTS_BIN}" --help | head -6
Usage: codex-aspects schema
       codex-aspects prompt --aspect <name> --scope <file>
       codex-aspects run --aspect <name> [--aspect <name>...] --scope <file>
                         --out-dir <dir> [--model <model>] [--effort <level>]
       codex-aspects validate --aspect <name> --scope <file> <output-file>
       codex-aspects changes --before <file> --after <file>
```

## No command prints the usage and fails

```scrut
$ "${CODEX_ASPECTS_BIN}" 2>&1 | head -1
Usage: codex-aspects schema
```

```scrut
$ "${CODEX_ASPECTS_BIN}" > /dev/null 2>&1
[1]
```

## Unknown command

```scrut
$ "${CODEX_ASPECTS_BIN}" review > "${FIXTURE}/unknown.err" 2>&1; echo "exit=$?" \
>   && tail -1 "${FIXTURE}/unknown.err"
exit=1
codex-aspects: unknown command: review
```

## Schema requires every field and lists the three severities

```scrut
$ "${CODEX_ASPECTS_BIN}" schema | jq -c '[.required, .properties.findings.items.required, .properties.findings.items.properties.severity.enum]'
[["aspect","findings","reviewed","strengths","summary"],["confidence","detail","file","fix","line","severity","title"],["critical","important","suggestion"]]
```

## Schema has no lookaround, which Codex rejects

```scrut
$ "${CODEX_ASPECTS_BIN}" schema | grep -c '(?[=!<]'
0
[1]
```

## Unknown aspect

```scrut
$ "${CODEX_ASPECTS_BIN}" prompt --aspect style --scope "${FIXTURE}/scope.json" 2>&1
codex-aspects: unknown aspect 'style'; expected one of: code errors tests comments types simplify
[1]
```

## A scope file that is not review-scope output

```scrut
$ printf '{}' > "${FIXTURE}/bad-scope.json" \
>   && { "${CODEX_ASPECTS_BIN}" prompt --aspect code --scope "${FIXTURE}/bad-scope.json" > "${FIXTURE}/bad-scope.err" 2>&1; echo "exit=$?"; } \
>   && sed "s|${FIXTURE}|FIXTURE|" "${FIXTURE}/bad-scope.err"
exit=1
codex-aspects: scope file 'FIXTURE/bad-scope.json' is not review-scope output
```

## A scope file missing a bucket

Without this check the untracked files would drop out of the prompt with no
error, and the review would cover less than it claimed.

```scrut
$ jq 'del(.untracked)' "${FIXTURE}/scope.json" > "${FIXTURE}/no-untracked.json" \
>   && { "${CODEX_ASPECTS_BIN}" prompt --aspect code --scope "${FIXTURE}/no-untracked.json" > "${FIXTURE}/no-untracked.err" 2>&1; echo "exit=$?"; } \
>   && sed "s|${FIXTURE}|FIXTURE|" "${FIXTURE}/no-untracked.err"
exit=1
codex-aspects: scope file 'FIXTURE/no-untracked.json' is not review-scope output
```

## A scope with committed changes and no base

Without a base the committed diff cannot be named, and the prompt would leave
the committed changes out with no error.

```scrut
$ jq '.base = null' "${FIXTURE}/scope.json" > "${FIXTURE}/no-base.json" \
>   && { "${CODEX_ASPECTS_BIN}" prompt --aspect code --scope "${FIXTURE}/no-base.json" > "${FIXTURE}/no-base.err" 2>&1; echo "exit=$?"; } \
>   && sed "s|${FIXTURE}|FIXTURE|" "${FIXTURE}/no-base.err"
exit=1
codex-aspects: scope file 'FIXTURE/no-base.json' is not review-scope output
```

## A scope path that leaves the repository

The prompt tells the reviewer to read each untracked path by name, so a `..`
segment would send it outside the repository.

```scrut
$ jq '.untracked = ["../outside.txt"]' "${FIXTURE}/scope.json" > "${FIXTURE}/escape-scope.json" \
>   && { "${CODEX_ASPECTS_BIN}" prompt --aspect code --scope "${FIXTURE}/escape-scope.json" > "${FIXTURE}/escape-scope.err" 2>&1; echo "exit=$?"; } \
>   && sed "s|${FIXTURE}|FIXTURE|" "${FIXTURE}/escape-scope.err"
exit=1
codex-aspects: scope file 'FIXTURE/escape-scope.json' is not review-scope output
```

## An aspect file that cannot be read stops the run before Codex starts

macOS ships Bash 3.2, where `set -e` does not reach into the command
substitution that renders each prompt, so the read is checked explicitly.
Without that, the run would go ahead with a prompt that has no instructions.

```scrut
$ mkdir "${FIXTURE}/aspects" "${FIXTURE}/unreadable-out" \
>   && cp "$(dirname "${CODEX_ASPECTS_BIN}")/../skills/review-pr-with-codex/references/aspects/"*.md "${FIXTURE}/aspects/" \
>   && chmod 000 "${FIXTURE}/aspects/code.md" \
>   && { CODEX_ASPECTS_DIR="${FIXTURE}/aspects" "${CODEX_ASPECTS_BIN}" run --aspect code \
>        --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/unreadable-out" > "${FIXTURE}/unreadable.err" 2>&1; echo "exit=$?"; } \
>   && chmod 644 "${FIXTURE}/aspects/code.md" \
>   && tail -1 "${FIXTURE}/unreadable.err" | sed "s|${FIXTURE}|FIXTURE|" \
>   && ls "${FIXTURE}/unreadable-out"
exit=1
codex-aspects: could not read the aspect instructions at FIXTURE/aspects/code.md
schema.json
```

## A review prompt is read-only and carries the aspect and snapshot

```scrut
$ "${CODEX_ASPECTS_BIN}" prompt --aspect errors --scope "${FIXTURE}/scope.json" > "${FIXTURE}/errors.prompt" \
>   && head -2 "${FIXTURE}/errors.prompt" \
>   && grep -c '^# Aspect: errors$' "${FIXTURE}/errors.prompt" \
>   && grep -c "^- Set \"reviewed\" to exactly: $(jq -r .snapshot "${FIXTURE}/scope.json")$" "${FIXTURE}/errors.prompt"
You are reviewing this repository's local changes. This review is read-only:
do not create, edit, delete or move any file, do not run commands that write
1
1
```

## The prompt drops the attribution comment

```scrut
$ grep -c '<!--' "${FIXTURE}/errors.prompt"
0
[1]
```

## The scope lists each non-empty bucket and gives a symlink as its link text

```scrut
$ sed -n '/^## Scope$/,/^Read the surrounding/p' "${FIXTURE}/errors.prompt" | sed "s/[0-9a-f]\{40\}/SHA/g"
## Scope

The scope is all of the following, and you must read all of it:

- Committed changes: git diff SHA SHA
- Unstaged changes: git diff
- Untracked files, which are in no diff; read each one:
  - fresh.txt
  - link -> /etc/hosts (a symlink; review the link text only and do not open its target)

Read the surrounding code, not only the diff. Before reviewing, read the
```

## The simplify prompt allows edits only in scope

```scrut
$ "${CODEX_ASPECTS_BIN}" prompt --aspect simplify --scope "${FIXTURE}/scope.json" | head -2
You are refining this repository's local changes. You may edit files, but
only files in the scope below, and only to make them clearer without changing
```

## Every aspect has instructions

```scrut
$ for aspect in code errors tests comments types simplify; do "${CODEX_ASPECTS_BIN}" prompt --aspect "${aspect}" --scope "${FIXTURE}/scope.json" | grep -c "^# Aspect: ${aspect}$"; done | sort | uniq -c | tr -s ' '
 6 1
```

## A run reports each aspect, and every failure class is a failure

```scrut
$ CODEX_STUB_MODES="errors=exit tests=none comments=empty types=malformed" \
>   "${CODEX_ASPECTS_BIN}" run --aspect code --aspect errors --aspect tests --aspect comments --aspect types \
>   --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" > "${FIXTURE}/run.json"; echo "exit=$?" \
>   && jq -r '.[] | [.aspect, .status, (.reason // "-"), (.exit_code | tostring)] | join(" | ")' "${FIXTURE}/run.json"
exit=3
code | ok | - | 0
errors | failed | codex exited with status 1 | 1
tests | failed | no output file was written | 0
comments | failed | the output file is empty | 0
types | failed | the output is not JSON | 0
```

## A non-zero exit fails the aspect even when its output is valid

A run can write a complete, matching result and then fail. The exit status is
checked first, so that result is never reported as a finished review.

```scrut
$ CODEX_STUB_MODES="code=exit-after-output" \
>   "${CODEX_ASPECTS_BIN}" run --aspect code \
>   --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" > "${FIXTURE}/exit-after.json"; echo "exit=$?" \
>   && jq -r '.[] | "\(.aspect): \(.status), \(.reason)"' "${FIXTURE}/exit-after.json" \
>   && "${CODEX_ASPECTS_BIN}" validate --aspect code --scope "${FIXTURE}/scope.json" "${FIXTURE}/out/code.json" | jq -r .status
exit=3
code: failed, codex exited with status 1
ok
```

## Output that misses the schema, or names another aspect or snapshot, fails

```scrut
$ CODEX_STUB_MODES="code=schema errors=wrong-aspect tests=wrong-snapshot" \
>   "${CODEX_ASPECTS_BIN}" run --aspect code --aspect errors --aspect tests \
>   --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" > "${FIXTURE}/mismatch.json"; echo "exit=$?" \
>   && jq -r '.[] | "\(.aspect): \(.reason)"' "${FIXTURE}/mismatch.json"
exit=3
code: the output does not match the schema
errors: the output names a different aspect
tests: the output reviewed a different snapshot
```

## Output holding an invalid object before a valid one fails

jq reads a file as a stream of values and `jq -e` reports on the last one, so
without a count every later check would see only the valid object.

```scrut
$ CODEX_STUB_MODES="code=multiple" \
>   "${CODEX_ASPECTS_BIN}" run --aspect code \
>   --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" > "${FIXTURE}/multiple.json"; echo "exit=$?" \
>   && jq -r '.[] | "\(.aspect): \(.reason)"' "${FIXTURE}/multiple.json"
exit=3
code: the output holds 2 JSON values, not one
```

## A rerun never reports an earlier run's output

The first run leaves a valid output file behind; the second writes none. If
the helper did not remove the old file before starting, the second run would
read it and report success for a review that never happened.

```scrut
$ "${CODEX_ASPECTS_BIN}" run --aspect code --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" | jq -r '.[0].status' \
>   && { CODEX_STUB_MODES="code=none" "${CODEX_ASPECTS_BIN}" run --aspect code \
>        --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" > "${FIXTURE}/rerun.json"; echo "exit=$?"; } \
>   && jq -r '.[] | "\(.aspect): \(.reason)"' "${FIXTURE}/rerun.json"
ok
exit=3
code: no output file was written
```

## A clean run exits zero, and a critical finding is still a successful run

```scrut
$ CODEX_STUB_MODES="types=critical" \
>   "${CODEX_ASPECTS_BIN}" run --aspect code --aspect types \
>   --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" > "${FIXTURE}/clean.json"; echo "exit=$?" \
>   && jq -c 'map(.status)' "${FIXTURE}/clean.json" \
>   && jq -r '.findings[0].severity' "${FIXTURE}/out/types.json"
exit=0
["ok","ok"]
critical
```

## Aspects run concurrently, and each result stays with its aspect

In barrier mode no stub run writes its output until all three have started,
so a runner that waited for one before starting the next would fail here. The
first aspect also finishes last, which checks that a late result is still
matched to the aspect that produced it.

```scrut
$ mkdir "${FIXTURE}/barrier" \
>   && CODEX_STUB_MODES="code=barrier-slow errors=barrier tests=barrier" \
>      CODEX_STUB_BARRIER_DIR="${FIXTURE}/barrier" CODEX_STUB_BARRIER_COUNT=3 \
>      "${CODEX_ASPECTS_BIN}" run --aspect code --aspect errors --aspect tests \
>      --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" > "${FIXTURE}/barrier.json"; echo "exit=$?" \
>   && jq -r '.[] | "\(.aspect): \(.status)"' "${FIXTURE}/barrier.json" \
>   && for aspect in code errors tests; do jq -r .aspect "${FIXTURE}/out/${aspect}.json"; done
exit=0
code: ok
errors: ok
tests: ok
code
errors
tests
```

## Stopping the helper stops its Codex runs

A `simplify` run has write access, so a run left going after the helper stops
could keep editing after its changes were measured. The stub here starts a
long-running child, standing in for a process Codex starts, and waits until
stopped. Once the helper receives TERM, the stub and its child must both be
gone.

```scrut
$ mkdir "${FIXTURE}/pids" "${FIXTURE}/cancel-out" \
>   && { CODEX_STUB_MODES="simplify=hang" CODEX_STUB_PID_DIR="${FIXTURE}/pids" \
>        "${CODEX_ASPECTS_BIN}" run --aspect simplify --scope "${FIXTURE}/scope.json" \
>        --out-dir "${FIXTURE}/cancel-out" > /dev/null 2>&1 & } \
>   && helper=$! \
>   && for attempt in $(seq 50); do [ -s "${FIXTURE}/pids/simplify.pid" ] && break; sleep 0.1; done \
>   && stub="$(cat "${FIXTURE}/pids/simplify.pid")" \
>   && child="$(cat "${FIXTURE}/pids/simplify.child.pid")" \
>   && kill -TERM "${helper}" \
>   && { wait "${helper}"; echo "helper exit=$?"; } \
>   && sleep 0.2 \
>   && for entry in "stub:${stub}" "child:${child}"; do \
>        if kill -0 "${entry#*:}" 2> /dev/null; then echo "${entry%%:*} still running"; kill "${entry#*:}"; else echo "${entry%%:*} stopped"; fi; \
>      done
helper exit=143
stub stopped
child stopped
```

## A prompt too large for one argument stops the run before Codex starts

The prompt is passed as one argument, which Linux caps at 128 KiB. Thousands of
untracked paths can exceed that, and the helper must refuse before any run
starts rather than fail partway with a raw shell error.

```scrut
$ jq '.untracked = [range(0; 3000) | "generated/untracked-path-number-\(.)-with-some-padding.txt"]' \
>      "${FIXTURE}/scope.json" > "${FIXTURE}/large-scope.json" \
>   && mkdir "${FIXTURE}/large-out" \
>   && { "${CODEX_ASPECTS_BIN}" run --aspect code --scope "${FIXTURE}/large-scope.json" \
>        --out-dir "${FIXTURE}/large-out" > "${FIXTURE}/large.err" 2>&1; echo "exit=$?"; } \
>   && sed 's/is [0-9]* bytes/is N bytes/' "${FIXTURE}/large.err" \
>   && ls "${FIXTURE}/large-out"
exit=1
codex-aspects: the code prompt is N bytes, above the 120000-byte limit for one argument; narrow the scope
schema.json
```

## Review aspects run read-only, with the model, effort and stdin set per run

The helper is given a pipe on stdin, as an agent harness gives it, and each
run must still see `/dev/null`, never the caller's pipe. Bash already starts a
background job on `/dev/null` when job control is off; the helper redirects
explicitly as well, so the guarantee does not rest on that default alone.

```scrut
$ printf "" | "${CODEX_ASPECTS_BIN}" run --aspect code --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" \
>   --model test-model --effort high > /dev/null && cat "${FIXTURE}/log/code.args"
--cd
<path>
--sandbox
read-only
--ephemeral
--model
test-model
--config
model_reasoning_effort="high"
--output-schema
<path>
--output-last-message
<output>
stdin: character-device
```

## The default model and effort

```scrut
$ "${CODEX_ASPECTS_BIN}" run --aspect code --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" > /dev/null \
>   && grep -A1 -e '^--model$' -e '^--config$' "${FIXTURE}/log/code.args" | grep -v -e '^--' -e '^--$'
gpt-6.1-sol
model_reasoning_effort="medium"
```

## Simplify runs alone

```scrut
$ "${CODEX_ASPECTS_BIN}" run --aspect code --aspect simplify --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" 2>&1
codex-aspects: simplify runs alone, after the review aspects
[1]
```

## An aspect named twice

```scrut
$ "${CODEX_ASPECTS_BIN}" run --aspect code --aspect code --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/out" 2>&1
codex-aspects: aspect 'code' is listed twice
[1]
```

## The output directory must be outside the working tree

```scrut
$ mkdir -p inside && "${CODEX_ASPECTS_BIN}" run --aspect code --scope "${FIXTURE}/scope.json" --out-dir inside 2>&1; echo "exit=$?"; rmdir inside
codex-aspects: --out-dir must be outside the working tree
exit=1
```

## An output directory reached through a symlink is judged by its target

The check resolves the physical path, so a link that looks external but points
into the repository is refused before any run starts, and nothing is written
through it.

```scrut
$ mkdir inside-target && ln -s "${PWD}/inside-target" "${FIXTURE}/link-into-repo" \
>   && { "${CODEX_ASPECTS_BIN}" run --aspect code --scope "${FIXTURE}/scope.json" \
>        --out-dir "${FIXTURE}/link-into-repo" 2>&1; echo "exit=$?"; } \
>   && ls -A inside-target | wc -l | tr -d ' ' \
>   && rmdir inside-target
codex-aspects: --out-dir must be outside the working tree
exit=1
0
```

A link that points outside the repository is accepted.

```scrut
$ mkdir "${FIXTURE}/external-target" && ln -s "${FIXTURE}/external-target" "${FIXTURE}/link-outside" \
>   && "${CODEX_ASPECTS_BIN}" run --aspect code --scope "${FIXTURE}/scope.json" \
>      --out-dir "${FIXTURE}/link-outside" | jq -r '.[0].status' \
>   && ls "${FIXTURE}/external-target" | grep -c '^code\.json$'
ok
1
```

## The output directory must exist

```scrut
$ "${CODEX_ASPECTS_BIN}" run --aspect code --scope "${FIXTURE}/scope.json" --out-dir "${FIXTURE}/missing" > "${FIXTURE}/missing.err" 2>&1; echo "exit=$?" \
>   && sed "s|${FIXTURE}|FIXTURE|" "${FIXTURE}/missing.err"
exit=1
codex-aspects: --out-dir 'FIXTURE/missing' is not an existing directory
```

## Validate accepts a well-formed subagent reply

```scrut
$ "${CODEX_ASPECTS_BIN}" validate --aspect types --scope "${FIXTURE}/scope.json" "${FIXTURE}/out/types.json" | jq -c '{aspect, status, exit_code}'
{"aspect":"types","status":"ok","exit_code":null}
```

## Validate rejects a reply that is prose

```scrut
$ printf 'Looks good to me.\n' > "${FIXTURE}/prose.json" \
>   && { "${CODEX_ASPECTS_BIN}" validate --aspect code --scope "${FIXTURE}/scope.json" "${FIXTURE}/prose.json" > "${FIXTURE}/prose.status"; echo "exit=$?"; } \
>   && jq -r .reason "${FIXTURE}/prose.status"
exit=3
the output is not JSON
```

## Validate accepts each of the three severities

```scrut
$ for severity in critical important suggestion; do jq --arg severity "${severity}" '.findings[0].severity = $severity' "${FIXTURE}/out/types.json" > "${FIXTURE}/severity.json" && "${CODEX_ASPECTS_BIN}" validate --aspect types --scope "${FIXTURE}/scope.json" "${FIXTURE}/severity.json" | jq -r '"\($severity): \(.status)"' --arg severity "${severity}"; done
critical: ok
important: ok
suggestion: ok
```

## Validate rejects a severity outside the three

The `simplify` gate looks for `critical` exactly, so a reply saying `Critical`
must fail rather than slip past it.

```scrut
$ jq '.findings[0].severity = "Critical"' "${FIXTURE}/out/types.json" > "${FIXTURE}/bad-severity.json" \
>   && { "${CODEX_ASPECTS_BIN}" validate --aspect types --scope "${FIXTURE}/scope.json" "${FIXTURE}/bad-severity.json" > "${FIXTURE}/bad-severity.status"; echo "exit=$?"; } \
>   && jq -r .reason "${FIXTURE}/bad-severity.status"
exit=3
the output does not match the schema
```

## Validate rejects a finding whose path escapes the repository

```scrut
$ jq '.findings[0].file = "../outside.sh"' "${FIXTURE}/out/types.json" > "${FIXTURE}/escape.json" \
>   && { "${CODEX_ASPECTS_BIN}" validate --aspect types --scope "${FIXTURE}/scope.json" "${FIXTURE}/escape.json" > "${FIXTURE}/escape.status"; echo "exit=$?"; } \
>   && jq -r .reason "${FIXTURE}/escape.status"
exit=3
the output does not match the schema
```

## Changes fails when the trees cannot be compared

A tree object that is missing, for example after `git gc` collected it, makes
`git diff` fail. That must stop the command, never print an empty change
list, which would read as a clean read-only check.

```scrut
$ jq '.tree = "0000000000000000000000000000000000000001"' "${FIXTURE}/scope.json" > "${FIXTURE}/missing-tree.json" \
>   && { "${CODEX_ASPECTS_BIN}" changes --before "${FIXTURE}/missing-tree.json" --after "${FIXTURE}/scope.json" \
>        > "${FIXTURE}/missing-tree.out" 2> "${FIXTURE}/missing-tree.err"; echo "exit=$?"; } \
>   && tail -1 "${FIXTURE}/missing-tree.err" | sed "s/[0-9a-f]\{40\}/SHA/g" \
>   && wc -c < "${FIXTURE}/missing-tree.out" | tr -d ' '
exit=1
codex-aspects: could not compare tree SHA with SHA
0
```

## Changes is empty when nothing changed

```scrut
$ "${CODEX_ASPECTS_BIN}" changes --before "${FIXTURE}/scope.json" --after "${FIXTURE}/scope.json" | jq -c '{changed, outside_scope}'
{"changed":[],"outside_scope":[]}
```

## Simplify writes, and changes reports exactly what it touched

```scrut
$ cp -R "${FIXTURE}/repo" "${FIXTURE}/simplify" && cd "${FIXTURE}/simplify" \
>   && "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}" --base base > "${FIXTURE}/before.json" \
>   && CODEX_STUB_MODES="simplify=write" CODEX_STUB_WRITE="${FIXTURE}/simplify/lib.sh" \
>      "${CODEX_ASPECTS_BIN}" run --aspect simplify --scope "${FIXTURE}/before.json" --out-dir "${FIXTURE}/out" | jq -r '.[0].status' \
>   && grep -A1 '^--sandbox$' "${FIXTURE}/log/simplify.args" | tail -1 \
>   && "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}" --base base > "${FIXTURE}/after.json" \
>   && "${CODEX_ASPECTS_BIN}" changes --before "${FIXTURE}/before.json" --after "${FIXTURE}/after.json" | jq -c '{changed, outside_scope}'
ok
workspace-write
{"changed":["lib.sh"],"outside_scope":[]}
```

## Changes marks a path outside the original scope

```scrut
$ cd "${FIXTURE}/simplify" && printf 'edited\n' >> other.sh \
>   && "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}" --base base > "${FIXTURE}/after-other.json" \
>   && "${CODEX_ASPECTS_BIN}" changes --before "${FIXTURE}/before.json" --after "${FIXTURE}/after-other.json" | jq -c '{changed, outside_scope}'
{"changed":["lib.sh","other.sh"],"outside_scope":["other.sh"]}
```

## Changes lists both paths of a rename

With rename detection on, git names only a renamed file's new path, so a file
moved out of the scope's reach would leave its old path in neither list.

```scrut
$ cp -R "${FIXTURE}/repo" "${FIXTURE}/rename" && cd "${FIXTURE}/rename" \
>   && "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}" --base base > "${FIXTURE}/rename-before.json" \
>   && mv other.sh renamed.sh \
>   && "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}" --base base > "${FIXTURE}/rename-after.json" \
>   && "${CODEX_ASPECTS_BIN}" changes --before "${FIXTURE}/rename-before.json" --after "${FIXTURE}/rename-after.json" | jq -c '{changed, outside_scope}'
{"changed":["other.sh","renamed.sh"],"outside_scope":["other.sh","renamed.sh"]}
```

## A staged change is in the prompt, and an empty unstaged bucket is not

The shared fixture has nothing staged, so this case stages its unstaged change
in a copy of it.

```scrut
$ cp -R "${FIXTURE}/repo" "${FIXTURE}/staged" && cd "${FIXTURE}/staged" \
>   && git add lib.sh \
>   && "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}" --base base > "${FIXTURE}/staged-scope.json" \
>   && "${CODEX_ASPECTS_BIN}" prompt --aspect code --scope "${FIXTURE}/staged-scope.json" \
>   | grep -e '^- Staged changes' -e '^- Unstaged changes'
- Staged changes: git diff --cached
```

## Changes covers the whole tree with diff.relative on, from a subdirectory

`diff.relative` limits `git diff` to the current subdirectory, so without
`--no-relative` a change outside it would leave `changed` empty and the
read-only check would pass.

```scrut
$ cp -R "${FIXTURE}/repo" "${FIXTURE}/relative" && cd "${FIXTURE}/relative" \
>   && git config diff.relative true \
>   && "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}" --base base > "${FIXTURE}/relative-before.json" \
>   && printf 'edited\n' >> other.sh \
>   && "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}" --base base > "${FIXTURE}/relative-after.json" \
>   && mkdir sub && cd sub \
>   && "${CODEX_ASPECTS_BIN}" changes --before "${FIXTURE}/relative-before.json" --after "${FIXTURE}/relative-after.json" | jq -c '{changed, outside_scope}'
{"changed":["other.sh"],"outside_scope":["other.sh"]}
```
