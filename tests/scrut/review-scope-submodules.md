# Review scope submodules

Local repositories and an isolated fixture config provide every submodule.
The fixture allows file transport only in that config and checks that the
helper preserves the child index. Each case checks snapshot movement and the
reported path; the staged-only case also checks that disk content stays equal.

## Setup

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" \
>   && source "${REPO_ROOT}/tests/fixtures/review-fixture-paths.bash"
```

## Unchanged recursive scans are stable

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" stable
true
```

## Working-tree edits invalidate consecutive dirty snapshots

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" edit
true
true
```

## Staged content moves the snapshot even when disk content is restored

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" staged
true
```

## Untracked submodule files enter the scope

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" untracked
true
```

## Moving submodule HEAD moves the snapshot

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" head
true
```

## Nested submodule edits invalidate consecutive dirty snapshots

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" nested
true
true
```

## Uninitialized submodules record only their gitlink

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" uninitialized
true
```

## Submodule ignore configuration cannot hide internal changes

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" ignored
true
```

## Mutation reporting includes nested internal paths

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" changes
true
```

## Unreadable child metadata retains Git diagnostics

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" failure 2>&1
fatal: invalid gitfile format: module/.git
review-scope: could not stage the working tree into the temporary index; the snapshot would describe HEAD instead of what is on disk
[1]
```

## Review prompts include nested tracked changes

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" prompt
nested diff command present
```

## Committed gitlink changes override diff ignore settings

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" committed
true
```

## Retained checkouts staged for deletion still have recursive scope

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" deleted
true
true
```

## Uninitialized checkouts with files fail instead of excluding their contents

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" populated 2>&1
review-scope: uninitialized submodule contains files: module
[1]
```

## Deleting the last submodule remains visible in rendered committed diffs

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" removed
true
module
```

## A child index mutation during collection refuses inconsistent output

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" mutation
review-scope: submodules changed while the scope was being read; rerun once settled
```
