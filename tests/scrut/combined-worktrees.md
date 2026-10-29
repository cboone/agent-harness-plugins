# Combined issue worktrees

The fixture refuses to proceed unless gh, git, workmux and tmux resolve to
committed stubs. Workmux refuses a second launch. No real worktree or window
is created. Repeated issue flags preserve every distinct issue number in input order.

The ref namespace case uses a private bare repository and existing commit
objects. It creates no worktrees or windows and changes no source-repository refs.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

## One launch carries both issue identities and one footer

```scrut
$ "${COMBINED_WORKTREES_CASE_BIN}" launch
Generated branch name: fix/4523-4503-verify-email
Work on issue #4523: Issue 4523
(Issue body truncated. Run `gh issue view 4523` for full details.)
Work on issue #4503: Issue 4503
(Issue body truncated. Run `gh issue view 4503` for full details.)
/address-issue 4523 4503
worktrees: 1
```

## Each issue has its own body budget

```scrut
$ "${COMBINED_WORKTREES_CASE_BIN}" budgets
body characters: 2000
body characters: 2000
```

## Rerun finds the combined branch in either issue order

```scrut
$ "${COMBINED_WORKTREES_CASE_BIN}" lookup
fix/4523-4503-verify-email
```

## Rerun reuses the combined branch rather than a primary-only branch

```scrut
$ "${COMBINED_WORKTREES_CASE_BIN}" reuse
Reusing branch fix/4523-4503-verify-email for issue 4503/4523
branch: fix/4523-4503-verify-email
```

## Bare combined names preserve issue order and remove duplicates

```scrut
$ "${COMBINED_WORKTREES_CASE_BIN}" bare
Generated branch name: 4523-4503-verify-email
```

## A branch matching only the first requested issue is not reused

The only existing branch carries 4503. Combined lookup must return no match,
and launch must generate a name carrying both requested issues.

```scrut
$ "${COMBINED_WORKTREES_CASE_BIN}" partial-match
combined lookup: none
Generated branch name: fix/4503-4523-verify-email
```

## PR branch detection preserves every closing identity

```scrut
$ "${COMBINED_WORKTREES_CASE_BIN}" links
Closes #4523
Closes #4503
```

## Fan-out stops before launching the same combined branch twice

Both singleton lookups resolve to the combined branch. The preflight message
names the issues and shared branch, asks for explicit choices, and launches nothing.

```scrut
$ "${COMBINED_WORKTREES_CASE_BIN}" fan-out
launch-workmux: issues 4523 and 4503 resolve to the same branch: fix/4523-4503-verify-email
launch-workmux: stop fan-out; choose distinct explicit branches for these issues
preflight exit: 1
launches: 0
```

## Fan-out accepts distinct explicit branches and unmatched issues

```scrut
$ "${COMBINED_WORKTREES_CASE_BIN}" fan-out-clear
distinct or missing branches: accepted
```

## Fan-out preflight rejects incomplete pairs

```scrut
$ bash "${LAUNCH_WORKMUX_BIN}" --check-fan-out-branches 4523 2>&1
launch-workmux: --check-fan-out-branches requires issue/branch pairs
[1]
```

## Numeric path segments support prefixes and single issues

Duplicates are removed; version numbers and leading zeroes are excluded.

```scrut
$ "${COMBINED_WORKTREES_CASE_BIN}" parser
4523
4503
4523
4503
4523
4523
```

## Numeric path segments conflict with an existing parent branch

This regression documents the slash format's namespace limitation in both
directions. A hyphen-separated branch occupies a separate ref name.

```scrut
$ "${COMBINED_REF_COLLISION_BIN}"
parent branch blocks combined child: yes
combined child blocks parent branch: yes
hyphen-separated combined branch coexists: yes
```

## Ref collisions are checked from shallow source checkouts

The fixture copies the existing commit object rather than fetching history.
The source repository in this case explicitly marks that commit as a shallow root.

```scrut
$ "${COMBINED_REF_COLLISION_BIN}" --shallow-source
shallow source: true
parent branch blocks combined child: yes
combined child blocks parent branch: yes
hyphen-separated combined branch coexists: yes
```
