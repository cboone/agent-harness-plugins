# Review scope

Tests for the `review-until-clean` helper that reports the local review scope
and a content snapshot of it.

Each case builds its own repository in a temporary directory. `-c
commit.gpgsign=false` keeps the fixture off the developer's signing key, which
CI does not have, and `--template=` keeps it off a template directory
that would otherwise decide the first branch's name. The base branch is created
with `git checkout -b` rather than `git init --initial-branch`, so the fixture
does not depend on `init.defaultBranch` either.

## Help

```scrut
$ "${REVIEW_SCOPE_BIN}" --help
Usage: review-scope [--base <ref>]
       review-scope --schema

Print one JSON object describing every local change and a snapshot identifier
bound to their content: committed branch changes, staged changes, unstaged
changes, and untracked files.

The snapshot is content-addressed, so it does not move when a file changes
which bucket it is in. Staging a file, unstaging it, or recording an intent to
add it with `git add -N` all leave the snapshot alone; changing a byte of it
does not.

Options:
  --base <ref>  Compare committed changes against this ref instead of the
                merge base with the default branch
  --schema      Print the JSON Schema for reviewer findings and exit
  -h, --help    Show this help
```

## Findings schema is valid JSON

```scrut
$ "${REVIEW_SCOPE_BIN}" --schema | jq -r '[.required[], (.properties.findings.items.required | join(","))] | join(" ")'
findings reviewed detail,evidence,file,line,severity,title
```

## Findings schema constrains severity to the two levels the ledger uses

```scrut
$ "${REVIEW_SCOPE_BIN}" --schema | jq -c '.properties.findings.items.properties.severity.enum'
["important","nit"]
```

## Unknown flag

```scrut
$ "${REVIEW_SCOPE_BIN}" --nope 2>&1 | tail -1
review-scope: unexpected argument: --nope
```

## Missing base ref value

```scrut
$ "${REVIEW_SCOPE_BIN}" --base 2>&1
review-scope: --base requires a ref
[1]
```

## Base ref that does not resolve

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && "${REVIEW_SCOPE_BIN}" --base no-such-ref 2>&1
review-scope: base ref 'no-such-ref' does not resolve to a commit
[1]
```

## Outside a git work tree

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" && "${REVIEW_SCOPE_BIN}" 2>&1
review-scope: not inside a git work tree
[1]
```

## A branch with no local changes reports an empty scope

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -c '{empty, committed, staged, unstaged, untracked}'
{"empty":true,"committed":[],"staged":[],"unstaged":[],"untracked":[]}
```

## Every bucket of the scope is reported separately

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && printf 'one\n' > staged.txt \
>   && printf 'one\n' > gone.txt \
>   && git add . \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && git checkout -q -b feature \
>   && printf 'two\n' >> tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qam committed \
>   && printf 'three\n' >> staged.txt && git add staged.txt \
>   && printf 'four\n' >> tracked.txt \
>   && rm gone.txt \
>   && printf 'new\n' > fresh.txt \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -c '{empty, committed, staged, unstaged, untracked}'
{"empty":false,"committed":["tracked.txt"],"staged":["staged.txt"],"unstaged":["gone.txt","tracked.txt"],"untracked":["fresh.txt"]}
```

## An ignored file is not in scope

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'ignored.txt\n' > .gitignore \
>   && git add .gitignore \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'noise\n' > ignored.txt \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -c '{empty, untracked}'
{"empty":true,"untracked":[]}
```

## A file name holding a newline survives intact

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'odd\n' > "$(printf 'we\nird.txt')" \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -c '.untracked'
["we\nird.txt"]
```

## The snapshot does not move when a file is staged

Staging changes which bucket a path is reported in and changes nothing about
its content, so a clean result bound to the snapshot stays valid.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'two\n' >> tracked.txt \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && git add tracked.txt \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && [[ "${before}" == "${after}" ]] && echo "snapshot held: yes"
snapshot held: yes
```

## The snapshot does not move when an untracked file gets an intent to add

`git add -N` moves a path from untracked to tracked without changing a byte of
it. A snapshot that hashed `git status` or `git diff HEAD` would move here, and
the loop would discard a clean result that is still good.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'new\n' > fresh.txt \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && git add -N fresh.txt \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && [[ "${before}" == "${after}" ]] && echo "snapshot held: yes"
snapshot held: yes
```

## The snapshot moves when one byte changes

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'new\n' > fresh.txt \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && printf 'x' >> fresh.txt \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && [[ "${before}" != "${after}" ]] && echo "snapshot moved: yes"
snapshot moved: yes
```

## The snapshot moves when the working tree is committed

Committing changes the head the scope is measured from, so a clean result
bound to the earlier snapshot no longer applies.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'new\n' > fresh.txt \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && git add -A \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm second \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && [[ "${before}" != "${after}" ]] && echo "snapshot moved: yes"
snapshot moved: yes
```

## A deletion is content, so it moves the snapshot too

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && rm tracked.txt \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && [[ "${before}" != "${after}" ]] && echo "snapshot moved: yes"
snapshot moved: yes
```

## The real index is left exactly as it was found

The snapshot is built in a temporary index. A run that disturbed the caller's
staged work would make the loop unsafe to run on a partly staged tree.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && printf 'one\n' > staged.txt \
>   && git add . \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'two\n' >> staged.txt && git add staged.txt \
>   && printf 'two\n' >> tracked.txt \
>   && printf 'new\n' > fresh.txt \
>   && before="$(git status --porcelain=v1 --untracked-files=all)" \
>   && "${REVIEW_SCOPE_BIN}" --base base > /dev/null \
>   && after="$(git status --porcelain=v1 --untracked-files=all)" \
>   && [[ "${before}" == "${after}" ]] && echo "index untouched: yes" && printf '%s\n' "${after}"
index untouched: yes
M  staged.txt
 M tracked.txt
?? fresh.txt
```

## Without a resolvable base, the working tree is still the scope

A repository with no `main`, no `master`, and no `origin` reports a null base
rather than failing, so the loop still reviews uncommitted work.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b solo \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'new\n' > fresh.txt \
>   && "${REVIEW_SCOPE_BIN}" | jq -c '{base, base_ref, committed, untracked, empty}'
{"base":null,"base_ref":null,"committed":[],"untracked":["fresh.txt"],"empty":false}
```

## The default base follows the conventional branch name

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b main \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && git checkout -q -b feature \
>   && printf 'two\n' >> tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qam committed \
>   && "${REVIEW_SCOPE_BIN}" | jq -c '{base_ref, committed}'
{"base_ref":"main","committed":["tracked.txt"]}
```

## Head, base and snapshot are reported as resolved object names

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -r '[.head, .base, .tree, .snapshot] | map(test("^[0-9a-f]{40}$")) | join(" ")'
true true true true
```
