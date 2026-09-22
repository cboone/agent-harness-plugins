# Review scope

Tests for the `review-until-clean` helper that reports the local review scope
and a content snapshot of it.

Cases that need a repository build their own in a temporary directory; the
help, schema and argument-parsing cases need none.

The suite runs with `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` pointed at
`/dev/null`, registered in the `Makefile` and in CI, so the developer's own git
configuration cannot change the result. That matters here beyond the usual
flakiness: a global `core.excludesFile` would remove files from the untracked
bucket, and `diff.relative` would make every reported path relative to the
current directory.

Each fixture also passes `--template=`, `-c commit.gpgsign=false` and an
explicit `user.name` and `user.email`, and creates its base branch with `git
checkout -b` rather than `git init --initial-branch`. The first three are
belt and braces once the global config is neutralized; the identity is not,
since a commit still needs one.

## Help

```scrut
$ "${REVIEW_SCOPE_BIN}" --help
Usage: review-scope [--base <ref>]
       review-scope --schema

Print one JSON object describing every local change and a snapshot identifier
bound to their content: committed branch changes, staged changes, unstaged
changes, and untracked files.

The snapshot is content-addressed, so it does not move when a file changes
which bucket it is in: staging a file, unstaging it, or recording an intent to
add it with `git add -N` all leave it alone, while changing a byte moves it.

Options:
  --base <ref>  Take the merge base with this ref instead of with the default
                branch; committed changes are those from the merge base to HEAD
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

The exit status is captured rather than piped, because a pipeline reports
`tail`'s status and would pass whether or not the script rejected the flag.

```scrut
$ out="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && exit_code=0 \
>   && "${REVIEW_SCOPE_BIN}" --nope > "${out}" 2>&1 || exit_code=$? \
>   && tail -1 "${out}" \
>   && exit "${exit_code}"
review-scope: unexpected argument: --nope
[1]
```

## Unknown flag prints the usage text

```scrut
$ "${REVIEW_SCOPE_BIN}" --nope 2>&1 | head -1
Usage: review-scope [--base <ref>]
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
>   && [[ -n "${before}" && "${before}" == "${after}" ]] && printf 'snapshot held: %s\n' "${before}"
snapshot held: * (glob)
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
>   && [[ -n "${before}" && "${before}" == "${after}" ]] && printf 'snapshot held: %s\n' "${before}"
snapshot held: * (glob)
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
>   && [[ -n "${before}" && -n "${after}" && "${before}" != "${after}" ]] && echo "snapshot moved: yes"
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
>   && [[ -n "${before}" && -n "${after}" && "${before}" != "${after}" ]] && echo "snapshot moved: yes"
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
>   && [[ -n "${before}" && -n "${after}" && "${before}" != "${after}" ]] && echo "snapshot moved: yes"
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

## The scope is the same from a subdirectory

`git ls-files` is scoped to the current directory while `git diff` is
whole-tree, so a run from a subdirectory once dropped every untracked file
above it while the whole-tree snapshot still covered them. The loop would then
bank a clean result over code no reviewer was shown.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && mkdir -p sub \
>   && printf 'x\n' > top-untracked.txt \
>   && printf 'y\n' > sub/sub-untracked.txt \
>   && from_root="$("${REVIEW_SCOPE_BIN}" --base base | jq -c '.untracked')" \
>   && cd sub \
>   && from_sub="$("${REVIEW_SCOPE_BIN}" --base base | jq -c '.untracked')" \
>   && printf '%s\n%s\n' "${from_root}" "${from_sub}"
["sub/sub-untracked.txt","top-untracked.txt"]
["sub/sub-untracked.txt","top-untracked.txt"]
```

## A force-added ignored file is inside the snapshot

A path matched by `.gitignore` but added with `git add -f` is tracked and is
reported in the staged bucket. A digest seeded from HEAD would skip it, so
rewriting it would not move the snapshot and a stale clean result would stand.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'secret.env\n' > .gitignore \
>   && git add .gitignore \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'AAAA\n' > secret.env \
>   && git add -f secret.env \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && printf 'BBBB-different\n' > secret.env \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && [[ -n "${before}" && -n "${after}" && "${before}" != "${after}" ]] && echo "snapshot moved: yes"
snapshot moved: yes
```

## A base that shares no history fails loudly

Swallowing the missing merge base left the committed bucket empty, which reads
as "no committed changes" and can report a branch full of unreviewed commits as
having nothing to review.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && git checkout -q --orphan other \
>   && git rm -q -rf . \
>   && printf 'z\n' > other.txt \
>   && git add other.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm orphan \
>   && git checkout -q base \
>   && "${REVIEW_SCOPE_BIN}" --base other 2>&1
review-scope: base ref 'other' shares no history with HEAD, so the committed part of the scope cannot be computed
[1]
```

## A working tree the digest cannot read fails loudly

`git add --all` fails on an unreadable file. Bash does not apply `set -e`
inside a command substitution, so the digest once fell through to `write-tree`
and returned HEAD's tree: the snapshot froze at a constant and the loop would
report clean for code that changed.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'secret\n' > unreadable.txt \
>   && chmod 000 unreadable.txt \
>   && exit_code=0 \
>   && "${REVIEW_SCOPE_BIN}" --base base > /dev/null 2>&1 || exit_code=$? \
>   && chmod 644 unreadable.txt \
>   && printf 'exit=%s\n' "${exit_code}"
exit=1
```

## Unstaging does not move the snapshot

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'two\n' >> tracked.txt \
>   && git add tracked.txt \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && git reset -q -- tracked.txt \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && [[ -n "${before}" && "${before}" == "${after}" ]] && printf 'snapshot held: %s\n' "${before}"
snapshot held: * (glob)
```

## A repository with no commits reports it

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . \
>   && "${REVIEW_SCOPE_BIN}" 2>&1
review-scope: HEAD does not resolve to a commit; the repository has no commits yet
[1]
```
