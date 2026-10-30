# Review scope

Tests for the `review-until-clean` helper that reports the local review scope
and a content snapshot of it.

Cases that need a repository build their own in a temporary directory; the
help, schema and argument-parsing cases need none.

Before Scrut starts, `bin/run-scrut` clears inherited Git inputs and points
`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` at `/dev/null`, preventing developer
Git configuration from changing results. A global `core.excludesFile` would
remove files from the untracked bucket; `diff.relative` would make every reported
path relative to the current directory.

Each fixture also passes `--template=`, `-c commit.gpgsign=false` and an
explicit `user.name` and `user.email`, and creates its base branch with `git
checkout -b` rather than `git init --initial-branch`. The first three are
belt and braces once the global config is neutralized; the identity is not,
since a commit still needs one.

## Help

```scrut
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" \
>   && source "${REPO_ROOT}/tests/fixtures/review-fixture-paths.bash" \
>   && "${REVIEW_SCOPE_BIN}" --help
Usage: review-scope [--base <ref>]
       review-scope --schema
       review-scope --membership <scope.json>
       review-scope --symlinks <scope.json>

Print one JSON object describing every local change and a snapshot identifier
bound to their content: committed branch changes, staged changes, unstaged
changes, and untracked files.

The snapshot covers HEAD, the base tip and merge base, raw disk bytes, index
content and bucket membership. Staging, unstaging and intent-to-add move it.
The separate tree identifier measures content as Git would store it; byte
changes removed by Git's normalization do not move it.

Options:
  --base <ref>  Take the merge base with this ref instead of with the default
                branch; committed changes are those from the merge base to HEAD
  --schema      Print review-until-clean's findings schema and exit
  --membership <file>  Print the captured canonical path records
  --symlinks <file>    Describe links from canonical membership without following targets
  -h, --help    Show this help
```

## Findings schema is valid JSON

```scrut
$ "${REVIEW_SCOPE_BIN}" --schema | jq -r '[.required[], (.properties.findings.items.required | join(","))] | join(" ")'
findings reviewed detail,evidence,file,line,severity,title
```

## Findings schema constrains severity to the three levels the ledger uses

```scrut
$ "${REVIEW_SCOPE_BIN}" --schema | jq -c '.properties.findings.items.properties.severity.enum'
["critical","important","nit"]
```

## Shared helper copies stay byte-identical

```scrut
$ cmp "${REVIEW_SCOPE_BIN}" "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}" && echo "shared helper copies match"
shared helper copies match
```

## Findings schema rejects a line number that anchors nothing

```scrut
$ "${REVIEW_SCOPE_BIN}" --schema | jq -c '.properties.findings.items.properties.line | {type, minimum}'
{"type":["integer","null"],"minimum":1}
```

## Findings schema confines a finding's path to the repository

`file` names a path the fixer will edit, so reviewer output that escapes the
repository must not validate. The pattern is applied here with `test`, which
uses the same Oniguruma-compatible syntax a JSON Schema validator does, and it
carries no lookaround because Codex rejects a schema that contains one.

```scrut
$ pattern="$("${REVIEW_SCOPE_BIN}" --schema | jq -r '.properties.findings.items.properties.file.pattern')" \
>   && printf '%s\n' README.md .gitignore docs/plans/todo/notes.md ... dir/.hidden \
>        /etc/passwd ../outside.txt .. . a/../../etc/passwd '~/.ssh/id_ed25519' 'a\b' \
>   | jq -Rr --arg p "${pattern}" 'if test($p) then "accept \(.)" else "reject \(.)" end'
accept README.md
accept .gitignore
accept docs/plans/todo/notes.md
accept ...
accept dir/.hidden
reject /etc/passwd
reject ../outside.txt
reject ..
reject .
reject a/../../etc/passwd
reject ~/.ssh/id_ed25519
reject a\b
```

## Unknown flag

The exit status is captured rather than piped, because a pipeline reports
`tail`'s status and would pass whether or not the script rejected the flag.

```scrut
$ out="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && exit_code=0 \
>   && "${REVIEW_SCOPE_BIN}" --nope > "${out}" 2>&1 || exit_code=$? \
>   && tail -1 "${out}" \
>   && exit "${exit_code}" # error-output-allow: testcase asserts retained diagnostics: Unknown flag
review-scope: unexpected argument: --nope
[1]
```

## Unknown flag prints the usage text

```scrut
$ "${REVIEW_SCOPE_BIN}" --nope 2>&1 | head -1 # error-output-allow: testcase asserts retained diagnostics: Unknown flag prints the usage text
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
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && "${REVIEW_SCOPE_BIN}" --base no-such-ref 2>&1
fatal: Needed a single revision
review-scope: could not resolve base (exit 128)
[128]
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
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -c '{empty, committed, staged, unstaged, untracked}'
{"empty":true,"committed":[],"staged":[],"unstaged":[],"untracked":[]}
```

## Every bucket of the scope is reported separately

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && printf 'one\n' > staged.txt \
>   && printf 'one\n' > gone.txt \
>   && git add -- . \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && git checkout -q -b feature \
>   && printf 'two\n' >> tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qam committed \
>   && printf 'three\n' >> staged.txt && git add -- staged.txt \
>   && printf 'four\n' >> tracked.txt \
>   && rm -- gone.txt \
>   && printf 'new\n' > fresh.txt \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -c '{empty, committed, staged, unstaged, untracked}'
{"empty":false,"committed":["tracked.txt"],"staged":["staged.txt"],"unstaged":["gone.txt","tracked.txt"],"untracked":["fresh.txt"]}
```

## An ignored file is not in scope

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'ignored.txt\n' > .gitignore \
>   && git add -- .gitignore \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'noise\n' > ignored.txt \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -c '{empty, untracked}'
{"empty":true,"untracked":[]}
```

## A file name holding a newline survives intact

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'odd\n' > "$(printf 'we\nird.txt')" \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -c '.untracked'
["we\nird.txt"]
```

## The snapshot moves when a file is staged

Staging changes bucket membership and the reviewed diffs, invalidating review
without changing disk content.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'two\n' >> tracked.txt \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && git add -- tracked.txt \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && [[ -n "${before}" && "${before}" != "${after}" ]] && printf 'snapshot moved: %s\n' "${before}"
snapshot moved: * (glob)
```

## The snapshot moves when an untracked file gets an intent to add

`git add -N` changes bucket membership without changing disk content. Prepare
it before capturing the round snapshot.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'new\n' > fresh.txt \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && git add -N -- fresh.txt \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && [[ -n "${before}" && "${before}" != "${after}" ]] && printf 'snapshot moved: %s\n' "${before}"
snapshot moved: * (glob)
```

## The snapshot moves when one byte changes

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
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
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
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
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && rm -- tracked.txt \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && [[ -n "${before}" && -n "${after}" && "${before}" != "${after}" ]] && echo "snapshot moved: yes"
snapshot moved: yes
```

## The real index is left exactly as it was found

The snapshot is built in a temporary index. A run that disturbed the caller's
staged work would make the loop unsafe to run on a partly staged tree.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && printf 'one\n' > staged.txt \
>   && git add -- . \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'two\n' >> staged.txt && git add -- staged.txt \
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
>   && git init -q --template= -- . \
>   && git checkout -q -b solo \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'new\n' > fresh.txt \
>   && "${REVIEW_SCOPE_BIN}" | jq -c '{base, base_ref, committed, untracked, empty}'
{"base":null,"base_ref":null,"committed":[],"untracked":["fresh.txt"],"empty":false}
```

## The default base uses the remote-tracking branch despite a stale local main

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b main \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && git update-ref refs/remotes/origin/main HEAD \
>   && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main \
>   && git checkout -q -b feature \
>   && printf 'two\n' >> tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qam committed \
>   && git update-ref refs/heads/main HEAD \
>   && "${REVIEW_SCOPE_BIN}" | jq -c '{base_ref, committed}'
{"base_ref":"origin/main","committed":["tracked.txt"]}
```

## Head, base and snapshot are reported as resolved object names

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
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
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && mkdir -p -- sub \
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
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'secret.env\n' > .gitignore \
>   && git add -- .gitignore \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'AAAA\n' > secret.env \
>   && git add -f -- secret.env \
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
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && git checkout -q --orphan other \
>   && git rm -q -rf -- . \
>   && printf 'z\n' > other.txt \
>   && git add -- other.txt \
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
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'secret\n' > unreadable.txt \
>   && chmod 000 unreadable.txt \
>   && exit_code=0 \
>   && "${REVIEW_SCOPE_BIN}" --base base > /dev/null || exit_code=$? \
>   && chmod 644 unreadable.txt \
>   && printf 'exit=%s\n' "${exit_code}"
exit=1
```

## Unstaging moves the snapshot

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'two\n' >> tracked.txt \
>   && git add -- tracked.txt \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && git reset -q -- tracked.txt \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r '.snapshot')" \
>   && [[ -n "${before}" && "${before}" != "${after}" ]] && printf 'snapshot moved: %s\n' "${before}"
snapshot moved: * (glob)
```

## A repository with no commits reports it

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && "${REVIEW_SCOPE_BIN}" 2>&1
review-scope: HEAD does not resolve to a commit; the repository has no commits yet
[1]
```

## Staging a change and editing it back is not a failure

Both the staged and unstaged buckets are non-empty here, yet the working tree
matches HEAD, so the tree digest legitimately equals HEAD's. A guard that
inferred a changed worktree from those buckets rejected this valid state.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > f.txt \
>   && git add -- f.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'two\n' > f.txt \
>   && git add -- f.txt \
>   && printf 'one\n' > f.txt \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -c '{staged, unstaged, empty}'
{"staged":["f.txt"],"unstaged":["f.txt"],"empty":false}
```

## The digest describes the working tree, never the staged blob

The same fixture, checking the value the previous case does not. `one` is on
disk and `two` is staged, and both are four bytes, so an index whose stat cache
is trusted reports the staged blob and the snapshot describes content no
reviewer was given. Seeding the temporary index from `HEAD` instead of from the
caller's index is what keeps these two trees equal.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > f.txt \
>   && git add -- f.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && printf 'two\n' > f.txt \
>   && git add -- f.txt \
>   && printf 'one\n' > f.txt \
>   && tree="$("${REVIEW_SCOPE_BIN}" --base base | jq -r .tree)" \
>   && [[ "${tree}" == "$(git rev-parse 'HEAD^{tree}')" ]] \
>   && git cat-file blob "${tree}:f.txt"
one
```

## Identical working trees digest identically whatever the index holds

Two repositories with the same commit and the same bytes on disk, one with a
same-size change staged and edited back. The digest is a function of the working
tree, so the staged state must not reach it.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && for r in clean staged; do \
>        git init -q --template= -- "${r}" \
>          && ( cd "${r}" \
>            && git checkout -q -b base \
>            && printf 'one\n' > f.txt \
>            && git add -- f.txt \
>            && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init ); \
>      done \
>   && ( cd staged && printf 'two\n' > f.txt && git add -- f.txt && printf 'one\n' > f.txt ) \
>   && a="$(cd clean && "${REVIEW_SCOPE_BIN}" --base base | jq -r .tree)" \
>   && b="$(cd staged && "${REVIEW_SCOPE_BIN}" --base base | jq -r .tree)" \
>   && [[ "${a}" == "${b}" ]] && echo "identical: ${a}"
identical: 7385b9ca65269b27de63aea3ddff716dd768c253
```

## An inferred base with no shared history is reported, not dropped

Clearing the ref would empty the committed bucket and let a branch's whole
history leave the scope while the run still looked complete.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b main \
>   && printf 'one\n' > a.txt \
>   && git add -- a.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && git update-ref refs/remotes/origin/main HEAD \
>   && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main \
>   && git checkout -q --orphan feature \
>   && git rm -q -rf -- . \
>   && printf 'work\n' > b.txt \
>   && git add -- b.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm orphan \
>   && "${REVIEW_SCOPE_BIN}" | jq -c '{base_ref, base, base_unrelated, committed}'
{"base_ref":"origin/main","base":null,"base_unrelated":true,"committed":[]}
```

## A base that shares history reports base_unrelated false

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -c '.base_unrelated'
false
```

## Committed work with no base ref reports the bucket as uncovered

With no valid `origin/HEAD` and no explicit base, there is nothing to measure commits
from. An empty `committed` list alone would read as "nothing committed", so the
branch's history could leave the scope while the run still looked complete.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b solo \
>   && printf 'one\n' > a.txt \
>   && git add -- a.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm first \
>   && printf 'two\n' >> a.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qam second \
>   && "${REVIEW_SCOPE_BIN}" | jq -c '{base_ref, base_unrelated, committed_covered, committed, empty}'
{"base_ref":null,"base_unrelated":false,"committed_covered":false,"committed":[],"empty":true}
```

## An unrelated base reports uncovered and says why

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b main \
>   && printf 'one\n' > a.txt \
>   && git add -- a.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && git update-ref refs/remotes/origin/main HEAD \
>   && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main \
>   && git checkout -q --orphan feature \
>   && git rm -q -rf -- . \
>   && printf 'work\n' > b.txt \
>   && git add -- b.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm orphan \
>   && "${REVIEW_SCOPE_BIN}" | jq -c '{base_ref, base_unrelated, committed_covered}'
{"base_ref":"origin/main","base_unrelated":true,"committed_covered":false}
```

## A resolved base reports the committed bucket as covered

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b base \
>   && printf 'one\n' > tracked.txt \
>   && git add -- tracked.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && "${REVIEW_SCOPE_BIN}" --base base | jq -c '{base_unrelated, committed_covered}'
{"base_unrelated":false,"committed_covered":true}
```

## Index-only content invalidates review while the disk tree holds

```scrut
$ cd "${work}" && "${REVIEW_SCOPE_BIN}" --base base > "${work}/../scope-before.json" \
>   && blob="$(printf 'indexed-only\n' | git hash-object -w --stdin)" \
>   && git update-index --cacheinfo "100644,${blob},tracked.txt" \
>   && "${REVIEW_SCOPE_BIN}" --base base > "${work}/../scope-after.json" \
>   && jq -cn --slurpfile a "${work}/../scope-before.json" --slurpfile b "${work}/../scope-after.json" \
>     '{tree_held: ($a[0].tree == $b[0].tree), snapshot_moved: ($a[0].snapshot != $b[0].snapshot)}'
{"tree_held":true,"snapshot_moved":true}
```

## Prepared coverage survives confirmation and restores only its own entries

```scrut
$ cd "${work}" && saved="$(git ls-files --stage -z | git hash-object --stdin)" \
>   && printf 'new\n' > coverage.txt && git add -N -- coverage.txt \
>   && round="$("${REVIEW_SCOPE_BIN}" --base base | jq -r .snapshot)" \
>   && confirm="$("${REVIEW_SCOPE_BIN}" --base base | jq -r .snapshot)" \
>   && test "${round}" = "${confirm}" && echo "confirming snapshot held" \
>   && git reset -q -- coverage.txt \
>   && test "${saved}" = "$(git ls-files --stage -z | git hash-object --stdin)" && echo "pre-existing index preserved"
confirming snapshot held
pre-existing index preserved
```

## An unrelated index edit invalidates a prepared round

```scrut
$ cd "${work}" && git add -N -- coverage.txt \
>   && before="$("${REVIEW_SCOPE_BIN}" --base base | jq -r .snapshot)" \
>   && blob="$(printf 'another indexed version\n' | git hash-object -w --stdin)" \
>   && git update-index --cacheinfo "100644,${blob},tracked.txt" \
>   && after="$("${REVIEW_SCOPE_BIN}" --base base | jq -r .snapshot)" \
>   && test "${before}" != "${after}" && echo "prepared round invalidated" \
>   && git reset -q -- coverage.txt
prepared round invalidated
```

## An index edit during collection refuses an inconsistent scope

```scrut
$ cd "${work}" \
>   && ( function git() { \
>          if [[ " $* " == *" diff "* && " $* " == *" HEAD "* ]]; then \
>            local blob; blob="$(printf 'during scan\n' | command git hash-object -w --stdin)" || return; \
>            command git update-index --cacheinfo "100644,${blob},tracked.txt" || return; \
>          fi; \
>          command git "$@"; \
>        }; export -f git; "${REVIEW_SCOPE_BIN}" --base base ) 2>&1
review-scope: the index, HEAD or base changed while the scope was being read; rerun once it has settled
[1]
```

## Temporary index files must remain outside the scope

```scrut
$ cd "${work}" && mkdir -- internal-tmp \
>   && TMPDIR="${work}/internal-tmp" "${REVIEW_SCOPE_BIN}" --base base 2>&1
review-scope: TMPDIR must point outside the working tree
[1]
```

## Fatal merge-base errors retain Git's diagnostic for either base source

The committed function stub passes every other Git operation through and is
exported only inside this subshell. Each invocation verifies its resolution.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . && git checkout -q -b main \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init --allow-empty \
>   && git update-ref refs/remotes/origin/main HEAD \
>   && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main \
>   && ( function git() { \
>          if [[ "${1:-}" == merge-base ]]; then echo 'fatal: sample object read failure' >&2; return 128; fi; \
>          command git "$@"; \
>        }; export -f git; \
>        for mode in inferred explicit; do \
>          [[ "$(type -t git)" == function ]] || exit 1; \
>          args=(); [[ "${mode}" == explicit ]] && args=(--base main); \
>          code=0; "${REVIEW_SCOPE_BIN}" ${args[@]+"${args[@]}"} > out 2> err || code=$?; \
>          test ! -s out || exit 1; \
>          printf '%s exit=%s\n' "${mode}" "${code}"; cat err; \
>        done ) # error-output-allow: testcase asserts retained diagnostics: Fatal merge-base errors retain Git's diagnostic for either base source
inferred exit=128
fatal: sample object read failure
review-scope: git merge-base '*' '*' failed (exit 128) (glob)
explicit exit=128
fatal: sample object read failure
review-scope: git merge-base '*' '*' failed (exit 128) (glob)
```

## Missing remote HEAD never guesses an existing local main

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= -- . \
>   && git checkout -q -b main \
>   && printf 'one\n' > a.txt && git add -- a.txt \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init \
>   && git remote add origin https://example.invalid/repo.git \
>   && "${REVIEW_SCOPE_BIN}" | jq -c '{base_ref, committed_covered}'
{"base_ref":null,"committed_covered":false}
```

## A dangling remote HEAD is not a base

```scrut
$ cd "${work}" \
>   && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/missing \
>   && "${REVIEW_SCOPE_BIN}" | jq -c '{base_ref, committed_covered}'
{"base_ref":null,"committed_covered":false}
```

## A valid nonstandard remote default is a base

```scrut
$ cd "${work}" \
>   && git update-ref refs/remotes/origin/integration HEAD \
>   && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/integration \
>   && "${REVIEW_SCOPE_BIN}" | jq -c '{base_ref, committed_covered}'
{"base_ref":"origin/integration","committed_covered":true}
```

## Unexpected inferred-base validation errors stop collection

The committed function stub rejects only the inferred base's commit lookup.
It passes other operations through and verifies its resolution before use.

```scrut
$ cd "${work}" \
>   && ( function git() { \
>          if [[ "${1:-}" == rev-parse && "${3:-}" == 'refs/remotes/origin/integration^{commit}' ]]; then \
>            echo 'fatal: sample object read failure' >&2; return 128; \
>          fi; \
>          command git "$@"; \
>        }; export -f git; \
>        [[ "$(type -t git)" == function ]] || exit 1; \
>        code=0; "${REVIEW_SCOPE_BIN}" > out 2> err || code=$?; \
>        test ! -s out || exit 1; \
>        printf 'exit=%s\n' "${code}"; cat err ) # error-output-allow: testcase asserts retained diagnostics: Unexpected inferred-base validation errors stop collection
exit=128
fatal: sample object read failure
review-scope: could not resolve base (exit 128)
```
