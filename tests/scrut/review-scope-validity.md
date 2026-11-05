# Review round validity

Real Git histories distinguish review inputs from informational base-tip movement.

## An unrelated base advance preserves the round

```scrut
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" \
>   && "${REVIEW_SCOPE_VALIDITY_BIN}" base
PASS: base round validity
```

## A new HEAD commit invalidates the round

```scrut
$ "${REVIEW_SCOPE_VALIDITY_BIN}" head
PASS: head round validity
```

## A rebase changes the merge base and invalidates the round

```scrut
$ "${REVIEW_SCOPE_VALIDITY_BIN}" rebase
PASS: rebase round validity
```

## A merge-base change alone invalidates the round

```scrut
$ "${REVIEW_SCOPE_VALIDITY_BIN}" merge-base
PASS: merge-base round validity
```

## Staging changes membership with identical disk content

```scrut
$ "${REVIEW_SCOPE_VALIDITY_BIN}" membership
PASS: membership round validity
```

## An unrelated base advance during collection preserves the round

```scrut
$ "${REVIEW_SCOPE_VALIDITY_BIN}" base-collection
PASS: base-collection round validity
```

## A merge-base change during collection refuses an inconsistent scope

```scrut
$ "${REVIEW_SCOPE_VALIDITY_BIN}" merge-base-collection
review-scope: the index, HEAD or merge base changed while the scope was being read; rerun once it has settled
PASS: merge-base-collection round validity
```

## A symbolic origin/HEAD alias preserves the round on an unrelated advance

```scrut
$ "${REVIEW_SCOPE_VALIDITY_BIN}" alias
PASS: alias round validity
```

## Plugin prose and helpers preserve the shared validity policy

```scrut
$ uv run --script "${REVIEW_VALIDITY_POLICY_BIN}"
Review validity policy passed.
```

## An unreadable policy subtree refuses a successful scan

```scrut
$ "${REVIEW_VALIDITY_UNREADABLE_BIN}"
review validity policy: check failed: *Permission denied* (glob)
PASS: unreadable policy subtree rejected
```

## Invalid UTF-8 in an active policy file refuses a successful scan

```scrut
$ "${REVIEW_VALIDITY_UNREADABLE_BIN}" encoding
review validity policy: check failed: *fixture.md: invalid UTF-8 policy source* (glob)
PASS: invalid UTF-8 policy input rejected
```
