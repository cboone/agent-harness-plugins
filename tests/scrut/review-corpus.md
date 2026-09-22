# Review case corpus

Tests for `bin/materialize-case` and `bin/validate-corpus`, the two tools that
read the frozen review corpus described in
[review case corpus](../../docs/review-case-corpus.md).

Every testcase builds a throwaway corpus with
`tests/fixtures/review-corpus-fixture`, which stands up a real git repository
because both tools need real objects: the validator compares recorded line
ranges against blobs at a commit, and the materializer adds a worktree. Each
scenario asks the fixture for one mutation, so the checks exercise the tool
rather than restating its rules beside it.

## A clean corpus validates, and says how much it checked

The counts travel with the verdict. A corpus that matched nothing would read as
a zero rather than as a pass, which the next testcase relies on.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus"
Review corpus: 2 case(s), 2 defect(s) checked.
All review corpus cases are valid.
```

## An empty corpus is visibly empty rather than valid

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && rm -rf "${root}/corpus/cases" && mkdir "${root}/corpus/cases" && "${VALIDATE_CORPUS_BIN}" --corpus "${root}/corpus"
Review corpus: 0 case(s), 0 defect(s) checked.
All review corpus cases are valid.
```

## Materializing a case reports what the harness needs

The SHAs and the path vary per run, so their shape is pinned rather than their
value. Matching `[0-9a-f]{40}` is itself the assertion that a full SHA was
reported and not an abbreviation.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && target="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${target}" | sed -E 's/^(BASE|HEAD)=[0-9a-f]{40}$/\1=<sha>/; s|^WORKTREE=/.*|WORKTREE=<path>|'
CASE=001-demo-tally-sign
WORKTREE=<path>
BASE=<sha>
HEAD=<sha>
```

## The worktree is checked out at the recorded head

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && target="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${target}" > /dev/null && [ "$(git -C "${target}" rev-parse HEAD)" = "$(cat "${root}/corpus/cases/001-demo-tally-sign/HEAD")" ] && echo "head matches"
head matches
```

## The reviewer cannot reach the answer key

The defining property of the corpus. The same `git show` runs against the
corpus and against the materialized worktree: it succeeds in the first and
fails in the second, so the absence is the isolation working rather than a
command that reads nothing anywhere.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && target="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${target}" > /dev/null && printf 'corpus=%s\nworktree=%s\n' "$(git -C "${root}/corpus" show main:cases/001-demo-tally-sign/defects.yaml | head -1)" "$(git -C "${target}" show main:cases/001-demo-tally-sign/defects.yaml 2>&1 | head -1)"
corpus=case: 001-demo-tally-sign
worktree=fatal: invalid object name 'main'.
```

## The worktree holds only the two frozen commits

Sorted, because the fixture's two commits carry the same timestamp and `git log`
does not order them predictably when it has no other tiebreak.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && target="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${target}" > /dev/null && git -C "${target}" log --all --format='%s' | sort
case 001-demo-tally-sign: base
case 001-demo-tally-sign: head
```

## Materializing the same case twice gives the same tree

The reproducibility the corpus promises: two reviewers given the same case ID
are given the same code.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${scratch}/a" > /dev/null && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${scratch}/b" > /dev/null && diff -r --exclude=.git "${scratch}/a" "${scratch}/b" && echo "identical"
identical
```

## A case frozen with its own metadata is refused

If the answer key were committed into the case's head tree, no amount of ref
isolation would keep it from the reviewer, so the materializer checks the tree
it just wrote.

```scrut
$ "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" metadata-in-tree)/corpus" 001-demo-tally-sign "$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" 2>&1
Error: the frozen tree carries corpus metadata (defects.yaml); the case is mis-frozen
[1]
```

## A defect class outside the closed set is reported

Recall is scored per class, so an unrecognized class would silently drop its
defect out of every per-class figure.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" unknown-class)/corpus"
::error::001-demo-tally-sign: defects[0].class perfomance is not one of logic, error-handling, concurrency, input-handling
Review corpus: 2 case(s), 1 defect(s) checked.
1 corpus validation error(s) found.
[1]
```

## A line range past the end of its file is reported

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" line-out-of-range)/corpus"
::error::001-demo-tally-sign/D1: lines 9 to 400 fall outside src/tally, which has 12 lines at HEAD
Review corpus: 2 case(s), 2 defect(s) checked.
1 corpus validation error(s) found.
[1]
```

## A defect outside the case's own diff is reported

The file exists at HEAD and the line range fits, so only the diff check can
catch it. A defect the diff never touches is one no reviewer could have been
expected to find.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" file-not-in-diff)/corpus"
::error::001-demo-tally-sign/D1: README.md is not in the BASE..HEAD diff
Review corpus: 2 case(s), 2 defect(s) checked.
1 corpus validation error(s) found.
[1]
```

## A case ID that disagrees with its directory is reported

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" case-mismatch)/corpus"
::error::001-demo-tally-sign: case is 007-demo-elsewhere but the directory is 001-demo-tally-sign
Review corpus: 2 case(s), 1 defect(s) checked.
1 corpus validation error(s) found.
[1]
```

## A base that is not an ancestor of its head is reported

`git diff BASE...HEAD` against an unrelated base compares from a merge base
that does not exist, so the reviewer would be shown the wrong change entirely.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" base-not-ancestor)/corpus"
::error::001-demo-tally-sign: BASE is not an ancestor of HEAD, so a three-dot diff would be wrong
Review corpus: 2 case(s), 1 defect(s) checked.
1 corpus validation error(s) found.
[1]
```

## A recorded SHA that has drifted from its case branch is reported

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" head-mismatch)/corpus" 2>&1 | grep -c '^::error::'
2
```

## An abbreviated ground-truth SHA is reported

The fix commit lives in the upstream repository, not here, so its existence
cannot be checked. Its shape can, which is what catches a SHA that was
abbreviated or written from memory and would no longer identify the commit.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" bad-ground-truth)/corpus"
::error::001-demo-tally-sign: origin.ground_truth must be a full 40-character hex SHA
Review corpus: 2 case(s), 1 defect(s) checked.
1 corpus validation error(s) found.
[1]
```

## A malformed SHA file is reported

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" bad-sha)/corpus"
::error::001-demo-tally-sign: BASE must hold exactly one 40-character hex SHA
Review corpus: 2 case(s), 1 defect(s) checked.
1 corpus validation error(s) found.
[1]
```

## A missing case file is reported

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" missing-defects)/corpus"
::error::001-demo-tally-sign: defects.yaml is missing
Review corpus: 2 case(s), 1 defect(s) checked.
1 corpus validation error(s) found.
[1]
```

## Unparseable YAML is reported as such

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" invalid-yaml)/corpus"
::error::001-demo-tally-sign: defects.yaml is not valid YAML
Review corpus: 2 case(s), 1 defect(s) checked.
1 corpus validation error(s) found.
[1]
```

## An unexpected file is a warning, not a finding

A stray note does not corrupt a case, so it is reported without failing the
run.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" stray-file)/corpus"
::warning::001-demo-tally-sign: unexpected file NOTES.md
Review corpus: 2 case(s), 2 defect(s) checked.
All review corpus cases are valid.
```

## A non-empty target is refused

Writing a case over an existing tree would leave the reviewer with a mixture of
two, and nothing downstream could tell.

```scrut
$ scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && mkdir "${scratch}/wt" && touch "${scratch}/wt/leftover" && "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" 001-demo-tally-sign "${scratch}/wt" 2>&1 | sed "s|${scratch}|<scratch>|"
Error: target <scratch>/wt is not empty
```

## A case ID that is not of the corpus form is a usage error

```scrut
$ "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" BadCase "$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" 2>&1
Error: case ID BadCase is not of the form NNN-repo-slug
[2]
```

## A missing corpus is a usage error rather than a finding

Exit 2 keeps a misconfigured run distinguishable from a corpus that really has
a problem, which matters when a harness reads the code to decide whether to
record a result.

```scrut
$ "${MATERIALIZE_CASE_BIN}" 001-demo-tally-sign "$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" 2>&1
Error: no corpus given; pass --corpus DIR or set REVIEW_CASE_CORPUS_DIR
[2]
```

## Offline refuses rather than reaching the network

```scrut
$ scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" --cache "${scratch}/cache.git" --offline 001-demo-tally-sign "${scratch}/wt" 2>&1
Error: refs/cases/001-demo-tally-sign/base is missing from the cache; re-run without --offline
[1]
```

## Validating one named case checks only that case

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" 002-demo-report-error
Review corpus: 1 case(s), 1 defect(s) checked.
All review corpus cases are valid.
```
