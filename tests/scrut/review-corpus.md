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

Where a block pipes the tool's output, it runs in a `set -o pipefail` subshell
so the tool's own status survives and can be asserted. Without that the block
takes the last stage's status, and a tool that exited 0, 2 or 128 would pass so
long as the text matched.

## A clean corpus validates, and says how much it checked

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus"
Review corpus: 2 case(s), 2 defect(s), 0 warning(s).
All review corpus cases are valid.
```

## A corpus with no cases is refused, not passed

Validating nothing is not a result. A wrong `--corpus`, or a clone that never
fetched the case content, would otherwise report a clean pass with the counts
as the only dissenting signal, and nothing consuming them.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && rm -rf "${root}/corpus/cases" && mkdir "${root}/corpus/cases" && (set -o pipefail; "${VALIDATE_CORPUS_BIN}" --corpus "${root}/corpus" 2>&1 | sed "s|${root}|<root>|")
Error: no cases found under <root>/corpus/cases; nothing was validated
[2]
```

## The materialized worktree can reach no branches at all

The tool-side form of the custom-ref rule: the cache is fed exactly two
refspecs, so a widened fetch would bring `refs/heads/*` along and show up here.
The count is reported beside it so a cache with no refs cannot pass as a zero.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && target="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${target}" > /dev/null && (set -o pipefail; git -C "${root}/corpus/.cache/cases.git" for-each-ref --format='%(refname)' | awk 'BEGIN { c = 0; h = 0 } /^refs\/cases\// { c++ } /^refs\/heads\// { h++ } END { print "cases=" c, "heads=" h }')
cases=2 heads=0
```

## Materializing a case reports what the harness needs

The SHAs and the path vary per run, so their shape is pinned rather than their
value. Matching `[0-9a-f]{40}` is itself the assertion that a full SHA was
reported and not an abbreviation.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && target="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" && (set -o pipefail; "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${target}" | sed -E 's/^(BASE|HEAD)=[0-9a-f]{40}$/\1=<sha>/; s|^WORKTREE=/.*|WORKTREE=<path>|')
CASE=001-demo-tally-sign
WORKTREE=<path>
BASE=<sha>
HEAD=<sha>
```

## A relative target lands beside the caller, not inside the cache

Every git call runs under `git -C "${cache}"`, so the target is made absolute
first. Without that a relative path would resolve against the cache directory.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${scratch}" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign relative-wt > /dev/null && test -d "${scratch}/relative-wt" && echo "beside the caller"
beside the caller
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
command that reads nothing anywhere. The failure is asserted rather than its
text, which is git's wording and not ours to pin.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && target="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${target}" > /dev/null && git -C "${root}/corpus" show main:cases/001-demo-tally-sign/defects.yaml | head -1 && ! git -C "${target}" rev-parse --verify --quiet main > /dev/null && echo "unreachable from the worktree"
case: 001-demo-tally-sign
unreachable from the worktree
```

## The worktree holds only the two frozen commits

Sorted, because the fixture's two commits carry the same timestamp and `git log`
does not order them predictably when it has no other tiebreak.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && target="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${target}" > /dev/null && (set -o pipefail; git -C "${target}" log --all --format='%s' | sort)
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

## The refused worktree is removed, so the answer key is not left behind

Asserting the consequence, not just the message. The check exists to keep the
metadata away from a reviewer, so refusing while leaving the tree at the path
the caller was told to use would defeat it. Removing it also keeps the failure
idempotent: the retry reports the real reason instead of "not empty".

```scrut
$ scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && root="$("${REVIEW_CORPUS_FIXTURE_BIN}" metadata-in-tree)" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${scratch}/wt" > /dev/null 2>&1; test ! -e "${scratch}/wt" && echo "worktree removed" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${scratch}/wt" 2>&1
worktree removed
Error: the frozen tree carries corpus metadata (defects.yaml); the case is mis-frozen
[1]
```

## A recorded SHA that has drifted from its case ref is refused

The materializer's own drift check. Without it a reviewer would be handed
whatever the ref now points at while the harness scored against the SHA the
case records.

```scrut
$ (set -o pipefail; "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" head-mismatch)/corpus" 001-demo-tally-sign "$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" 2>&1 | sed -E 's/[0-9a-f]{40}/<sha>/g')
Error: HEAD records <sha> but refs/cases/001-demo-tally-sign/head points at <sha>
[1]
```

## A base that is not an ancestor of the head is refused

Both ends move together in this scenario, so the recorded SHAs and the refs
agree and the ancestry is the only thing left to refuse it.

```scrut
$ (set -o pipefail; "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" base-unrelated)/corpus" 001-demo-tally-sign "$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" 2>&1 | sed -E 's/[0-9a-f]{40}/<sha>/g')
Error: BASE <sha> is not an ancestor of HEAD <sha>; three-dot diffs would be wrong
[1]
```

## --cache puts the objects where it says

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" --cache "${scratch}/own.git" 001-demo-tally-sign "${scratch}/wt" > /dev/null && git -C "${scratch}/own.git" rev-parse --verify --quiet "refs/cases/001-demo-tally-sign/head" > /dev/null && test ! -e "${root}/corpus/.cache" && echo "used the named cache, left the default alone"
used the named cache, left the default alone
```

## --offline succeeds against a cache that already holds the case

The refusal below covers a cold cache. This covers the other direction, so an
`--offline` that always refused would not pass.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${scratch}/warm" > /dev/null && (set -o pipefail; "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" --offline 001-demo-tally-sign "${scratch}/again" | sed -n '1p')
CASE=001-demo-tally-sign
```

## Offline refuses rather than reaching the network

```scrut
$ scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" --cache "${scratch}/cache.git" --offline 001-demo-tally-sign "${scratch}/wt" 2>&1
Error: refs/cases/001-demo-tally-sign/base is missing from the cache; re-run without --offline
[1]
```

## --prune forgets a worktree whose directory is gone

The first block shows the failure it remedies: git keeps the registration, so
re-using the freed path is refused until the registration is dropped.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${scratch}/a" > /dev/null && rm -rf "${scratch}/a" && (set -o pipefail; "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${scratch}/a" 2>&1 | tail -1)
Error: could not add a worktree for 001-demo-tally-sign at */a (glob)
[1]
```

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${scratch}/a" > /dev/null && rm -rf "${scratch}/a" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" --prune && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 001-demo-tally-sign "${scratch}/a" > /dev/null && echo "the freed path is usable again"
the freed path is usable again
```

## --prune takes no case or target

```scrut
$ "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" --prune 001-demo-tally-sign 2>&1
Error: --prune takes no case or target
[2]
```

## A defects.yaml that is not a mapping is reported

The likeliest hand edit there is, a leading hyphen and space on the first
line, and the one
this check most exists for. Every field lookup in the schema filter uses jq's
optional operator, and on a non-object document those yield nothing rather than
null, so without an explicit shape assertion the case would produce no problems
at all and pass as valid.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" non-mapping-yaml)/corpus"
::error::001-demo-tally-sign: defects.yaml must be a mapping at the top level, got array
Review corpus: 2 case(s), 1 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## A defect entry that is not a mapping is reported

Reported as a finding rather than becoming the script's exit status. Reading a
field off a scalar is a jq runtime error, and under `set -e` that would end the
run with jq's own code, no annotation, no summary, and every later case
unchecked.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" scalar-defect)/corpus"
::error::001-demo-tally-sign: defects[0] must be a mapping, got string
Review corpus: 2 case(s), 1 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## A line number written as a float is reported

`9.0` equals its own floor, so a value-only integer test accepts it, and yq and
`@tsv` both preserve the `9.0` text. It then reaches a shell arithmetic
comparison that cannot parse it, and because that comparison is an `if`
condition the error reads as false, which would skip the range check in
silence: a range of 400 in a 12-line file would pass.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" float-lines)/corpus"
::error::001-demo-tally-sign: defects[0].lines must hold integers
Review corpus: 2 case(s), 1 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## A defect recorded against a directory is reported

`git cat-file -e` is true for a tree as well as a blob, and `git show` on a
tree prints its listing, so a bare existence check would let a directory
through and the range would be compared against the length of that listing.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" directory-as-file)/corpus"
::error::001-demo-tally-sign/D1: src is not a file at HEAD
Review corpus: 2 case(s), 2 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## A defect class outside the closed set is reported

Recall is scored per class, so an unrecognized class would silently drop its
defect out of every per-class figure.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" unknown-class)/corpus"
::error::001-demo-tally-sign: defects[0].class perfomance is not one of logic, error-handling, concurrency, input-handling
Review corpus: 2 case(s), 1 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## A line range past the end of its file is reported

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" line-out-of-range)/corpus"
::error::001-demo-tally-sign/D1: lines 9 to 400 fall outside src/tally, which has 12 lines at HEAD
Review corpus: 2 case(s), 2 defect(s), 0 warning(s).
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
Review corpus: 2 case(s), 2 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## A case ID that disagrees with its directory is reported

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" case-mismatch)/corpus"
::error::001-demo-tally-sign: case is 007-demo-elsewhere but the directory is 001-demo-tally-sign
Review corpus: 2 case(s), 1 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## A base from an unrelated history is reported

The two case histories are orphans, so a base taken from the other one shares
no ancestor with this head. `git diff BASE...HEAD` does not show the wrong
change in that situation, it refuses outright with `no merge base`. The quieter
failure the same check guards is a base that shares history but is a sibling
rather than an ancestor, where the three-dot diff succeeds and shows something
other than the case.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" base-unrelated)/corpus"
::error::001-demo-tally-sign: BASE is not an ancestor of HEAD, so a three-dot diff would be wrong
Review corpus: 2 case(s), 1 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## A recorded SHA that has drifted from its case ref is reported

Pinned as one error, not a count. The mutation adds a descendant commit rather
than reusing the base, so the BASE..HEAD diff stays non-empty and the
diff-membership rule does not fire alongside this one.

```scrut
$ (set -o pipefail; "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" head-mismatch)/corpus" 2>&1 | sed -E 's/[0-9a-f]{40}/<sha>/g')
::error::001-demo-tally-sign: head ref points at <sha> but the file records <sha>
Review corpus: 2 case(s), 2 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## An abbreviated ground-truth SHA is reported

The fix commit lives in the upstream repository, not here, so its existence
cannot be checked. Its shape can, which is what catches a SHA that was
abbreviated or written from memory and would no longer identify the commit.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" bad-ground-truth)/corpus"
::error::001-demo-tally-sign: origin.ground_truth must be a full 40-character hex SHA
Review corpus: 2 case(s), 1 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## A malformed SHA file is reported

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" bad-sha)/corpus"
::error::001-demo-tally-sign: BASE must hold exactly one 40-character hex SHA
Review corpus: 2 case(s), 1 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## A missing case file is reported

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" missing-defects)/corpus"
::error::001-demo-tally-sign: defects.yaml is missing
Review corpus: 2 case(s), 1 defect(s), 0 warning(s).
1 corpus validation error(s) found.
[1]
```

## Unparseable YAML carries yq's own diagnostic

yq names the line, and it is the only thing that does, so the message is kept
rather than replaced with a generic one. Reporting every failure as invalid
YAML would also blame the file for an unwritable scratch directory.

```scrut
$ (set -o pipefail; "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" invalid-yaml)/corpus" 2>&1 | sed -n '1p')
::error::001-demo-tally-sign: could not read defects.yaml: Error: bad file *did not find expected ',' or ']' (glob)
[1]
```

## An unexpected entry is a warning, and the count travels with the verdict

A stray note does not corrupt a case, so it is reported without failing the
run. The count appears in the summary so a warning cannot be lost above an
unqualified pass.

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}" stray-file)/corpus"
::warning::001-demo-tally-sign: unexpected entry NOTES.md
Review corpus: 2 case(s), 2 defect(s), 1 warning(s).
All review corpus cases are valid.
```

## A stray dotfile is reported too

The sweep uses `find` rather than a glob, which skips dotfiles, so a leftover
`.DS_Store` or `.defects.json` would otherwise pass in silence.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && printf 'x\n' > "${root}/corpus/cases/001-demo-tally-sign/.hidden" && (set -o pipefail; "${VALIDATE_CORPUS_BIN}" --corpus "${root}/corpus" | sed -n '1p')
::warning::001-demo-tally-sign: unexpected entry .hidden
```

## Two problems in one case are both reported

The loop reports every problem rather than stopping at the first, so one edit
does not mask another.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && sed -i.bak -e 's/^source: planted$/source: invented/' -e 's/^    severity: p1$/    severity: urgent/' "${root}/corpus/cases/001-demo-tally-sign/defects.yaml" && rm -f "${root}/corpus/cases/001-demo-tally-sign/defects.yaml.bak" && (set -o pipefail; "${VALIDATE_CORPUS_BIN}" --corpus "${root}/corpus" 2>&1 | grep -c '^::error::')
2
[1]
```

## Duplicate defect ids are reported

Two defects sharing an id would make per-defect scoring ambiguous.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && python3 -c "import sys; p=sys.argv[1]; s=open(p).read(); open(p,'w').write(s + s.split('defects:')[1])" "${root}/corpus/cases/001-demo-tally-sign/defects.yaml" 2>/dev/null; (set -o pipefail; "${VALIDATE_CORPUS_BIN}" --corpus "${root}/corpus" 2>&1 | grep -c 'not unique')
1
[1]
```

## A defect naming a file absent from HEAD is reported

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && sed -i.bak 's|^    file: src/tally$|    file: src/gone|' "${root}/corpus/cases/001-demo-tally-sign/defects.yaml" && rm -f "${root}/corpus/cases/001-demo-tally-sign/defects.yaml.bak" && (set -o pipefail; "${VALIDATE_CORPUS_BIN}" --corpus "${root}/corpus" 2>&1 | sed -n '1p')
::error::001-demo-tally-sign/D1: src/gone is not a file at HEAD
[1]
```

## A reversed line range is reported

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && sed -i.bak 's/^    lines: \[9, 9\]$/    lines: [9, 4]/' "${root}/corpus/cases/001-demo-tally-sign/defects.yaml" && rm -f "${root}/corpus/cases/001-demo-tally-sign/defects.yaml.bak" && (set -o pipefail; "${VALIDATE_CORPUS_BIN}" --corpus "${root}/corpus" 2>&1 | sed -n '1p')
::error::001-demo-tally-sign: defects[0].lines start 9 is after end 4
[1]
```

## A non-empty target is refused

Writing a case over an existing tree would leave the reviewer with a mixture of
two, and nothing downstream could tell.

```scrut
$ scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && mkdir "${scratch}/wt" && touch "${scratch}/wt/leftover" && (set -o pipefail; "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" 001-demo-tally-sign "${scratch}/wt" 2>&1 | sed "s|${scratch}|<scratch>|")
Error: target <scratch>/wt is not empty
[1]
```

## An existing empty target is accepted

```scrut
$ scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && mkdir "${scratch}/wt" && (set -o pipefail; "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" 001-demo-tally-sign "${scratch}/wt" | sed -n '1p')
CASE=001-demo-tally-sign
```

## A case ID that is not of the corpus form is a usage error

```scrut
$ "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" BadCase "$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" 2>&1
Error: case ID BadCase is not of the form NNN-repo-slug
[2]
```

## Both tools give the same exit code for a case that does not exist

The same user error, so the same code. Exit 2 keeps a misconfigured run
distinguishable from a corpus that really has a problem.

```scrut
$ root="$("${REVIEW_CORPUS_FIXTURE_BIN}")" && "${MATERIALIZE_CASE_BIN}" --corpus "${root}/corpus" 099-demo-absent "$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" > /dev/null 2>&1; m=$?; "${VALIDATE_CORPUS_BIN}" --corpus "${root}/corpus" 099-demo-absent > /dev/null 2>&1; v=$?; printf 'materialize=%d validate=%d\n' "${m}" "${v}"
materialize=2 validate=2
```

## A missing corpus is a usage error rather than a finding

```scrut
$ "${MATERIALIZE_CASE_BIN}" 001-demo-tally-sign "$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")/wt" 2>&1
Error: no corpus given; pass --corpus DIR or set REVIEW_CASE_CORPUS_DIR
[2]
```

## A corpus that is not a git repository is a usage error

```scrut
$ scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && (set -o pipefail; "${MATERIALIZE_CASE_BIN}" --corpus "${scratch}" 001-demo-tally-sign "${scratch}/wt" 2>&1 | sed "s|${scratch}|<scratch>|")
Error: corpus <scratch> is not a git repository
[2]
```

## A cache that is not a git repository is a usage error

Rather than git's own `fatal:` and exit 128, which is outside the documented
contract and says nothing about which option was wrong.

```scrut
$ scratch="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && mkdir "${scratch}/notgit" && (set -o pipefail; "${MATERIALIZE_CASE_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" --cache "${scratch}/notgit" --prune 2>&1 | sed "s|${scratch}|<scratch>|")
Error: cache <scratch>/notgit is not a git repository
[2]
```

## An unknown option is a usage error in both tools

```scrut
$ "${MATERIALIZE_CASE_BIN}" --nope 2>&1
Error: unknown option --nope
[2]
```

```scrut
$ "${VALIDATE_CORPUS_BIN}" --nope 2>&1
Error: unknown option --nope
[2]
```

## An option missing its value is a usage error

```scrut
$ "${MATERIALIZE_CASE_BIN}" --corpus 2>&1
Error: --corpus needs a directory
[2]
```

## REVIEW_CASE_CORPUS_DIR is honored when no --corpus is given

It is the only input `make validate-corpus` uses, and the suite unsets it, so
nothing else would notice if it stopped being read.

```scrut
$ REVIEW_CASE_CORPUS_DIR="$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" "${VALIDATE_CORPUS_BIN}"
Review corpus: 2 case(s), 2 defect(s), 0 warning(s).
All review corpus cases are valid.
```

## Validating one named case checks only that case

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" 002-demo-report-error
Review corpus: 1 case(s), 1 defect(s), 0 warning(s).
All review corpus cases are valid.
```

## Validating two named cases checks both

```scrut
$ "${VALIDATE_CORPUS_BIN}" --corpus "$("${REVIEW_CORPUS_FIXTURE_BIN}")/corpus" 001-demo-tally-sign 002-demo-report-error
Review corpus: 2 case(s), 2 defect(s), 0 warning(s).
All review corpus cases are valid.
```

## Each tool's help text

```scrut
$ "${MATERIALIZE_CASE_BIN}" --help | head -2
Usage: materialize-case [--corpus DIR] [--cache DIR] [--offline] CASE TARGET
       materialize-case [--corpus DIR] [--cache DIR] --prune
```

```scrut
$ "${VALIDATE_CORPUS_BIN}" --help | head -1
Usage: validate-corpus [--corpus DIR] [CASE...]
```

## An unknown fixture mutation is refused without leaving a directory behind

The fixture's contract is that the caller owns the printed directory, so a
failure that prints nothing must not leave one. The name is checked before
`mktemp` runs.

```scrut
$ "${REVIEW_CORPUS_FIXTURE_BIN}" no-such-mutation 2>&1
Error: unknown mutation no-such-mutation
[2]
```
