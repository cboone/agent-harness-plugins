# Plan and branch subject matching

The skill uses this read-only helper for each eligible candidate before counting unique matches. Both results exit 0; command failures remain distinct from a nonmatching candidate.

## Trailing issue number

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'feat/4344-auto-promote-production-deploys' '2026-09-08-auto-promote-production-deploys-4344.md'
match
```

## Leading issue number

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'feature/493-add-search' '2026-10-30-493-add-search.md'
match
```

## Leading issue word

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/issue-493-add-search' '2026-10-30-issue-493-add-search.md'
match
```

## Absent plan issue number

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-add-search' '2026-10-30-add-search.md'
match
```

## Absent branch issue number

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'feat/add-search' '2026-10-30-add-search.md'
match
```

## Both plan issue forms

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-add-search' '2026-10-30-493-add-search-493.md'
match
```

## Both forms with issue word

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/issue-493-add-search' '2026-10-30-issue-493-add-search-493.md'
match
```

## Numeric subject without branch issue

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'feat/upgrade-to-postgres-16' '2026-01-01-upgrade-to-postgres-16.md'
match
```

## Numeric subject with branch issue

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'feat/493-upgrade-to-postgres-16' '2026-01-01-upgrade-to-postgres-16.md'
match
```

## Numeric subject followed by issue

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'feat/493-upgrade-to-postgres-16' '2026-01-01-upgrade-to-postgres-16-493.md'
match
```

## Near miss with extra subject word

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-add-search' '2026-10-30-add-search-results-493.md'
no-match
```

## Near miss with missing subject word

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-add-search-results' '2026-10-30-add-search-493.md'
no-match
```

## Wrong trailing issue

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-add-search' '2026-10-30-add-search-494.md'
no-match
```

## No suffix tolerance without branch issue

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'feat/add-search' '2026-10-30-add-search-493.md'
no-match
```

## At most one trailing suffix

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-add-search' '2026-10-30-add-search-493-493.md'
no-match
```

## Wrong trailing issue with both forms

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-add-search' '2026-10-30-493-add-search-494.md'
no-match
```

## One leading prefix with trailing issue

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-add-search' '2026-10-30-493-493-add-search-493.md'
no-match
```

## At most one branch issue prefix

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-493-add-search' '2026-10-30-add-search-493.md'
no-match
```

## At most one datestamp

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-add-search' '2026-10-30-2026-10-29-add-search-493.md'
no-match
```

## Unlisted category retained

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'hotfix/493-add-search' '2026-10-30-add-search-493.md'
no-match
```

## Category is case sensitive

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'Fix/493-add-search' '2026-10-30-add-search-493.md'
no-match
```

## Issue prefix is case sensitive

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/Issue-493-add-search' '2026-10-30-add-search-493.md'
no-match
```

## ASCII case and punctuation

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-Add_Search' '2026-10-30-ADD...SEARCH-493.md'
match
```

## Leading zeroes retained

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/0493-add-search' '2026-10-30-add-search-0493.md'
match
```

## Different leading zeroes

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/0493-add-search' '2026-10-30-add-search-493.md'
no-match
```

## Undated plan

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-add-search' 'add-search-493.md'
match
```

## Newline punctuation collapses with adjacent punctuation

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 'fix/493-add-search' $'2026-10-30-add.\n.search-493.md'
match
```

## Missing arguments

```scrut
$ "${PLAN_MATCHES_BRANCH_BIN}" 2>&1
Usage: plan-matches-branch <branch> <plan-basename.md>
[2]
```
