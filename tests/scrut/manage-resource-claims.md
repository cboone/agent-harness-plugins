# Manage resource claims

Tests for recording and reporting the exclusive resources held by git worktrees.

Staleness is derived from `git worktree list --porcelain`, so every testcase drives that through `tests/fixtures/git-worktree-stub` rather than the ambient repository. `/repo/wt-live` is a worktree git reports; `/repo/wt-gone` is not; and `/repo/wt-prunable` is one git still lists but marks `prunable`. Either of the latter two makes a claim on it stale, and the `prunable` case is the one a bare `rm -rf` of a worktree produces.

## Test helpers

`claims_tail` and `claims_check_report` exist because a pipeline reports the exit code of its last command. Piping straight into `tail` or `sed` would replace the script's status with the filter's, and every error case here asserts a status.

```scrut
$ function setup_claims() {
>   claim_file="$(mktemp -d)/.claude/worktree-resources.local.json"
>   stub_dir="$(mktemp -d)"
>   cp "${GIT_WORKTREE_STUB_BIN}" "${stub_dir}/git"
>   chmod +x "${stub_dir}/git"
>   live_porcelain="$(printf 'worktree /repo/main\nHEAD aaa\nbranch refs/heads/main\n\nworktree /repo/wt-live\nHEAD bbb\nbranch refs/heads/feature/live\n\nworktree /repo/wt-prunable\nHEAD ccc\nbranch refs/heads/feature/prunable\nprunable gitdir file points to non-existent location\n')"
> }
> function claims() {
>   env PATH="${stub_dir}:${PATH}" STUB_GIT_WORKTREE_PORCELAIN="${live_porcelain}" WORKTREE_RESOURCES_FILE="${claim_file}" bash "${MANAGE_RESOURCE_CLAIMS_BIN}" "$@"
> }
> function claims_list() {
>   claims list | sed 's/claimed=[^ ]*/claimed=TIMESTAMP/'
> }
> function claims_tail() {
>   local output status=0
>   output="$(claims "$@" 2>&1)" || status=$?
>   printf '%s\n' "${output}" | tail -1
>   return "${status}"
> }
> function claims_check_report() {
>   local output status=0
>   output="$(claims check "$@" 2>&1)" || status=$?
>   printf '%s\n' "${output}" | sed 's/claimed [0-9TZ:-]*/claimed TIMESTAMP/'
>   return "${status}"
> }
> function claims_shared() {
>   env -u WORKTREE_RESOURCES_FILE PATH="${stub_dir}:${PATH}" STUB_GIT_WORKTREE_PORCELAIN="${shared_porcelain}" bash "${MANAGE_RESOURCE_CLAIMS_BIN}" "$@"
> }
> function setup_shared() {
>   setup_claims
>   main_worktree="$(mktemp -d)"
>   linked_worktree="$(mktemp -d)"
>   shared_porcelain="$(printf 'worktree %s\nHEAD aaa\nbranch refs/heads/main\n\nworktree %s\nHEAD bbb\nbranch refs/heads/feature/live\n' "${main_worktree}" "${linked_worktree}")"
> }
> function claims_no_identity() {
>   local blind
>   blind="$(mktemp -d)"
>   printf '#!/usr/bin/env bash\nif [[ "${3:-}" == "rev-parse" ]]; then exit 128; fi\nexec "%s" "$@"\n' "${GIT_WORKTREE_STUB_BIN}" > "${blind}/git"
>   chmod +x "${blind}/git"
>   env PATH="${blind}:${PATH}" STUB_GIT_WORKTREE_PORCELAIN="${live_porcelain}" WORKTREE_RESOURCES_FILE="${claim_file}" bash "${MANAGE_RESOURCE_CLAIMS_BIN}" "$@"
> }
> function without_jq() {
>   local minimal
>   minimal="$(mktemp -d)"
>   ln -s "$(command -v basename)" "${minimal}/basename"
>   ln -s "$(command -v cat)" "${minimal}/cat"
>   env PATH="${minimal}" "$(command -v bash)" "${MANAGE_RESOURCE_CLAIMS_BIN}" "$@"
> }
```

## A claim is recorded and listed

The claim file is created along with its parent directory, so a project that has no `.claude/` yet does not have to make one first.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live --issue 128 \
>   && claims_list
claimed "logic" for feature/live
resource=logic state=held id=* branch=feature/live issue=128 claimed=TIMESTAMP worktree=/repo/wt-live (glob)
```

## The stored record carries the issue's fields

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live --issue 128 > /dev/null \
>   && jq -c '{version: .version, claim: (.claims[0] | del(.claimed_at, .id))}' "${claim_file}"
{"version":1,"claim":{"resource":"logic","worktree":"/repo/wt-live","branch":"feature/live","gitdir":"/admin/wt-live","issue":128}}
```

## The timestamp is recorded as UTC ISO 8601

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && jq -r '.claims[0].claimed_at' "${claim_file}"
????-??-??T??:??:??Z (glob)
```

## An issue number is omitted rather than stored as null

```scrut
$ setup_claims \
>   && claims claim simulator --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && jq -c '.claims[0] | has("issue")' "${claim_file}" \
>   && claims_list
false
resource=simulator state=held id=* branch=feature/live claimed=TIMESTAMP worktree=/repo/wt-live (glob)
```

## A held resource exits 3 and names its holder

The distinct exit code is what lets a caller branch on the outcome without parsing the message.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live --issue 128 > /dev/null \
>   && claims_check_report logic
resource "logic" is held by feature/live (issue 128) at /repo/wt-live, claimed TIMESTAMP, id * (glob)
[3]
```

## A free resource is silent and exits 0

```scrut
$ setup_claims && claims check logic
```

## Claims are listed in resource order

```scrut
$ setup_claims \
>   && claims claim simulator --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims claim disk --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims_list | cut -d' ' -f1
resource=disk
resource=logic
resource=simulator
```

## A claim whose worktree is gone is flagged stale

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-gone --branch feature/gone > /dev/null \
>   && claims_list
resource=logic state=stale id=* branch=feature/gone claimed=TIMESTAMP worktree=/repo/wt-gone (glob)
```

## check reports a stale claim rather than blocking on it

A worktree that has been removed must not hold a resource forever, so `check` reports the stale claim and still exits 0.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-gone --branch feature/gone > /dev/null \
>   && claims_check_report logic
resource "logic" has a stale claim from feature/gone at /repo/wt-gone, claimed TIMESTAMP; that claim no longer matches a live worktree
```

## list --json carries the derived stale flag

Staleness is never stored, so a reader that wants it has to be handed it.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-gone --branch feature/gone > /dev/null \
>   && claims claim disk --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims list --json | jq -c '[.[] | {resource, stale}]' \
>   && jq -c '[.claims[] | has("stale")]' "${claim_file}"
[{"resource":"disk","stale":false},{"resource":"logic","stale":true}]
[false,false]
```

## Claiming over a stale claim clears it

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-gone --branch feature/gone > /dev/null \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live \
>   && claims_list
claimed "logic" for feature/live, clearing a stale claim from feature/gone
resource=logic state=held id=* branch=feature/live claimed=TIMESTAMP worktree=/repo/wt-live (glob)
```

## Reclaiming from the same worktree refreshes rather than takes over

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live
refreshed the claim on "logic" for feature/live
```

## Claiming a resource another worktree holds is refused

`check` and `claim` are separate operations, so a resource that was free at the check can be held by the time the claim is written. Refusing here, under the lock, is what keeps a takeover from happening that nobody was asked about.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims_tail claim logic --worktree /repo/main --branch main
resource "logic" is held by feature/live at /repo/wt-live, claimed *, id *; pass --take-over * to claim it anyway (glob)
[3]
```

## --take-over claims it anyway and says so

The claim stays advisory: a user who has been asked and said yes needs a way through.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && token="$(claims list --json | jq -r '.[0].id')" \
>   && claims claim logic --worktree /repo/main --branch main --take-over "${token}" \
>   && claims list | wc -l | tr -d ' '
claimed "logic" for main, taking it over from feature/live
1
```

## A stale holder is replaced without --take-over

A stale claim is free by definition, so nothing is being taken from anyone.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-gone --branch feature/gone > /dev/null \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live
claimed "logic" for feature/live, clearing a stale claim from feature/gone
```

## release by resource removes one claim

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims claim disk --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims release logic \
>   && claims_list
released "logic" held by feature/live
resource=disk state=held id=* branch=feature/live claimed=TIMESTAMP worktree=/repo/wt-live (glob)
```

## release by worktree removes every claim that worktree holds

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims claim disk --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims claim simulator --worktree /repo/main --branch main > /dev/null \
>   && claims release --worktree /repo/wt-live \
>   && claims_list
released "disk" held by feature/live
released "logic" held by feature/live
resource=simulator state=held id=* branch=main claimed=TIMESTAMP worktree=/repo/main (glob)
```

## Releasing a resource nobody holds is reported, not an error

```scrut
$ setup_claims && claims release logic
no claim to release
```

## prune drops stale claims and leaves the rest

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-gone --branch feature/gone > /dev/null \
>   && claims claim disk --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims prune \
>   && claims_list
pruned "logic" from feature/gone at /repo/wt-gone
resource=disk state=held id=* branch=feature/live claimed=TIMESTAMP worktree=/repo/wt-live (glob)
```

## prune reports when there is nothing stale

```scrut
$ setup_claims \
>   && claims claim disk --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims prune
no stale claims
```

## A missing claim file lists nothing

```scrut
$ setup_claims && claims list && echo "exit ok"
exit ok
```

## An empty claim file lists nothing

A file trimmed to nothing is the ordinary result of a user clearing it by hand, so it reads as no claims rather than as corruption.

```scrut
$ setup_claims && mkdir -p "$(dirname "${claim_file}")" && : > "${claim_file}" && claims list && echo "exit ok"
exit ok
```

## Invalid JSON is refused rather than overwritten

```scrut
$ setup_claims && mkdir -p "$(dirname "${claim_file}")" && printf '{' > "${claim_file}" && claims list 2>&1
manage-resource-claims: */.claude/worktree-resources.local.json is not valid JSON; fix or remove it (glob)
[1]
```

## A JSON document of the wrong shape is refused

```scrut
$ setup_claims && mkdir -p "$(dirname "${claim_file}")" && printf '{"hello": 1}' > "${claim_file}" && claims list 2>&1
manage-resource-claims: */.claude/worktree-resources.local.json is not a claim file; expected an object with an integer "version" and a "claims" array (glob)
[1]
```

## A file from a newer schema version is refused rather than downgraded

The `version` field exists so a later format change has something to branch on. Accepting any value and rewriting it as version 1 would make an older copy of this script silently destroy a newer file it did not understand.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 999, "claims": []}' > "${claim_file}" \
>   && { claims list 2>&1; echo "exit=$?"; } \
>   && jq -r '.version' "${claim_file}"
manage-resource-claims: */.claude/worktree-resources.local.json declares version 999; this script supports version 1 only, so it will not read or rewrite the file (glob)
exit=1
999
```

## A malformed claim record is refused

The skill promises not to rewrite a file it cannot read. Validating only the envelope broke that promise for records inside it: a claim missing `worktree` passed, and the next mutation rewrote the file around it.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 1, "claims": [{"id":"aaaaaaaaaaaa","resource": "logic"}]}' > "${claim_file}" \
>   && claims list 2>&1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; id must be lowercase hex, resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, gitdir must be non-empty and free of control characters when present, and issue must be a non-negative integer when present (glob)
[1]
```

## A stored claim with a non-numeric issue is refused

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 1, "claims": [{"id":"aaaaaaaaaaaa","resource":"a","worktree":"/repo/wt-live","branch":"b","claimed_at":"t","issue":"x"}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; id must be lowercase hex, resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, gitdir must be non-empty and free of control characters when present, and issue must be a non-negative integer when present (glob)
```

## Concurrent claims on different resources both survive

Atomic replacement alone stops a reader seeing half a document, but not two worktrees reading the same snapshot and the later write discarding the earlier claim. Parallel worktrees are the case this feature exists for, so that sequence is likely rather than exotic.

```scrut
$ setup_claims \
>   && { claims claim logic --worktree /repo/wt-live --branch feature/a > /dev/null 2>&1 & } \
>   && { claims claim simulator --worktree /repo/wt-live --branch feature/b > /dev/null 2>&1 & } \
>   && wait \
>   && claims list | cut -d' ' -f1
resource=logic
resource=simulator
```

## The lock is released when the operation finishes

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/a > /dev/null \
>   && if [[ -d "${claim_file}.lock" ]]; then echo "lock leaked"; else echo "lock released"; fi
lock released
```

## A resource name carrying whitespace is refused

`resource` is free-form, and the output is space-delimited `key=value`. A name like `logic state=stale` would forge a field and one carrying a newline would fake an entire claim line. The names this is for never contain whitespace, so refusing it removes the ambiguity by construction rather than by escaping.

```scrut
$ setup_claims && claims_tail claim "logic state=stale" --worktree /repo/wt-live --branch feature/a
manage-resource-claims: claim requires a resource name that has no whitespace and does not start with a hyphen
[1]
```

## check and release refuse a whitespace name too

```scrut
$ setup_claims \
>   && { claims_tail check "logic state=stale"; claims_tail release "logic state=stale"; } 2>&1
manage-resource-claims: check requires a resource name that has no whitespace and does not start with a hyphen
manage-resource-claims: release requires a resource name that has no whitespace and does not start with a hyphen
[1]
```

## A stored resource name carrying whitespace is refused

Validation on write and on read agree, so a hand-edited file cannot reintroduce what the CLI rejects.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 1, "claims": [{"id":"aaaaaaaaaaaa","resource":"a b","worktree":"/repo/wt-live","branch":"b","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; id must be lowercase hex, resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, gitdir must be non-empty and free of control characters when present, and issue must be a non-negative integer when present (glob)
```

## Outside a git repository the claim file cannot be resolved

```scrut
$ cd "$(mktemp -d)" && env -u WORKTREE_RESOURCES_FILE bash "${MANAGE_RESOURCE_CLAIMS_BIN}" list 2>&1
manage-resource-claims: not inside a git repository; set WORKTREE_RESOURCES_FILE to override
[1]
```

## prune outside a git repository says why it cannot run

Staleness is undetermined when git cannot answer, and pruning every claim because git was unavailable would be worse than leaving them in place.

```scrut
$ cd "$(mktemp -d)" && env WORKTREE_RESOURCES_FILE="${PWD}/claims.json" bash "${MANAGE_RESOURCE_CLAIMS_BIN}" prune 2>&1
manage-resource-claims: cannot list worktrees; run prune inside a git repository
[1]
```

## The create-worktree copy is wired and runnable

`bin/validate-plugins` rule 18 requires each plugin to ship its own copy, and `tests/scrut/repo-tooling.md` keeps the two byte-identical. This confirms the second copy is reachable through its own variable.

```scrut
$ setup_claims \
>   && env PATH="${stub_dir}:${PATH}" STUB_GIT_WORKTREE_PORCELAIN="${live_porcelain}" WORKTREE_RESOURCES_FILE="${claim_file}" bash "${CREATE_WORKTREE_MANAGE_RESOURCE_CLAIMS_BIN}" claim logic --worktree /repo/wt-live --branch feature/live \
>   && claims_list
claimed "logic" for feature/live
resource=logic state=held id=* branch=feature/live claimed=TIMESTAMP worktree=/repo/wt-live (glob)
```

## Help is available before jq is required

`--help` has to work on a machine that has not installed jq yet, which is exactly when someone reads it.

```scrut
$ without_jq --help | head -1
Usage: manage-resource-claims <subcommand> [options]
```

## Every other subcommand requires jq

```scrut
$ without_jq list 2>&1
manage-resource-claims: jq is required
[1]
```

## No subcommand

```scrut
$ setup_claims && claims_tail
manage-resource-claims: expected a subcommand
[1]
```

## Unknown subcommand

```scrut
$ setup_claims && claims_tail bogus
manage-resource-claims: unknown subcommand: bogus
[1]
```

## check without a resource name

```scrut
$ setup_claims && claims_tail check
manage-resource-claims: check requires a resource name that has no whitespace and does not start with a hyphen
[1]
```

## claim without a resource name

```scrut
$ setup_claims && claims_tail claim --worktree /repo/wt-live
manage-resource-claims: claim requires a resource name that has no whitespace and does not start with a hyphen
[1]
```

## check refuses an option in place of a resource name

Without this guard a mistyped flag is read as a resource nobody has claimed, so `check` reports it free and exits 0. A caller branching on that exit code would then proceed as though the resource were available.

```scrut
$ setup_claims && claims_tail check --json
manage-resource-claims: check requires a resource name that has no whitespace and does not start with a hyphen
[1]
```

## claim without --worktree

```scrut
$ setup_claims && claims claim logic --branch feature/live 2>&1
manage-resource-claims: claim requires --worktree
[1]
```

## claim without --branch

```scrut
$ setup_claims && claims claim logic --worktree /repo/wt-live 2>&1
manage-resource-claims: claim requires --branch
[1]
```

## A non-numeric issue is refused

```scrut
$ setup_claims && claims claim logic --worktree /repo/wt-live --branch feature/live --issue abc 2>&1
manage-resource-claims: --issue must be a number, got: abc
[1]
```

## An option with no value

```scrut
$ setup_claims && claims claim logic --worktree 2>&1
manage-resource-claims: --worktree requires a path
[1]
```

## release accepts a resource or --worktree, not both

```scrut
$ setup_claims && claims_tail release logic --worktree /repo/wt-live
manage-resource-claims: release takes a resource name or --worktree, not both
[1]
```

## release with neither a resource nor --worktree

```scrut
$ setup_claims && claims_tail release
manage-resource-claims: release requires a resource name or --worktree
[1]
```

## Unexpected arguments are refused

```scrut
$ setup_claims && claims_tail prune extra
manage-resource-claims: unexpected argument: extra
[1]
```

## Unknown options are refused

```scrut
$ setup_claims && claims_tail list --bogus
manage-resource-claims: unexpected argument: --bogus
[1]
```

## A whitespace branch is refused

git refuses whitespace in a branch name, so accepting it here would only let `claim` write a record that the read contract then refuses, leaving the file unusable by the next command.

```scrut
$ setup_claims && claims_tail claim logic --worktree /repo/wt-live --branch "a b"
manage-resource-claims: --branch must not contain whitespace
[1]
```

## A non-integer version reports the schema error, not an arithmetic one

A `1.5` is refused as a malformed envelope rather than reported as an unsupported version it was never going to be, which keeps the two diagnostics distinct.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 1.5, "claims": []}' > "${claim_file}" \
>   && claims list 2>&1
manage-resource-claims: */.claude/worktree-resources.local.json is not a claim file; expected an object with an integer "version" and a "claims" array (glob)
[1]
```

## The stored record contract matches what the CLI accepts

A looser read contract would let a hand-edited file hold a claim no command can name, or one that forges columns in the space-delimited list output.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 1, "claims": [{"id":"aaaaaaaaaaaa","resource":"-logic","worktree":"/repo/wt-live","branch":"b","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; id must be lowercase hex, resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, gitdir must be non-empty and free of control characters when present, and issue must be a non-negative integer when present (glob)
```

## A stored branch carrying whitespace is refused

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 1, "claims": [{"id":"aaaaaaaaaaaa","resource":"a","worktree":"/repo/wt-live","branch":"b c","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; id must be lowercase hex, resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, gitdir must be non-empty and free of control characters when present, and issue must be a non-negative integer when present (glob)
```

## A worktree path containing spaces is still accepted

A path legitimately may contain spaces, which is why `list` emits `worktree=` last.

```scrut
$ setup_claims \
>   && claims claim logic --worktree "/repo/with space" --branch feature/live > /dev/null \
>   && claims_list
resource=logic state=held id=* branch=feature/live claimed=TIMESTAMP worktree=/repo/with space (glob)
```

## Two claims on one resource are refused

One claim per resource is the invariant every lookup assumes. `claim_for_resource` answers with the first match, so a duplicate would let a stale record hide a live holder behind it and slip a takeover past the guard in `claim`.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"id":"aaaaaaaaaaaa","resource":"logic","worktree":"/repo/wt-gone","branch":"a","claimed_at":"t"},{"id":"bbbbbbbbbbbb","resource":"logic","worktree":"/repo/wt-live","branch":"b","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims list 2>&1
manage-resource-claims: */.claude/worktree-resources.local.json holds more than one claim on the same resource; remove the duplicates (glob)
[1]
```

## A control character in the worktree path is refused on write

`list` prints one claim per line, so a newline inside a path would let one record print as several and forge claims that are not in the file. Spaces stay legal, since a path may legitimately contain them.

```scrut
$ setup_claims && claims_tail claim logic --worktree "$(printf '/a\n/b')" --branch feature/live
manage-resource-claims: --worktree must not contain control characters
[1]
```

## A control character in a stored worktree path is refused on read

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"id":"aaaaaaaaaaaa","resource":"a","worktree":"/a\\n/b","branch":"b","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; id must be lowercase hex, resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, gitdir must be non-empty and free of control characters when present, and issue must be a non-negative integer when present (glob)
```

## --take-over naming a holder that no longer holds it is refused

Approval is about a particular holder. If a third worktree takes the resource between the check and the write, consent to displace the first says nothing about displacing it, and a boolean flag could not tell the two apart.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims_tail claim logic --worktree /repo/main --branch main --take-over deadbeef
resource "logic" is held by feature/live at /repo/wt-live, claimed *, id *; --take-over named claim deadbeef, which is not the one held now, so nothing was changed (glob)
[3]
```

## --take-over requires the holder's id

```scrut
$ setup_claims && claims_tail claim logic --worktree /repo/main --branch main --take-over
manage-resource-claims: --take-over requires the id of the holder being displaced
[1]
```

## A stored issue must be a non-negative integer

The CLI accepts only digit strings for `--issue`, so the read contract has to match: a hand-edited `1.5` or `-3` would otherwise survive every later rewrite and surface as an impossible issue number.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"id":"aaaaaaaaaaaa","resource":"a","worktree":"/repo/wt-live","branch":"b","claimed_at":"t","issue":1.5}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; id must be lowercase hex, resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, gitdir must be non-empty and free of control characters when present, and issue must be a non-negative integer when present (glob)
```

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"id":"aaaaaaaaaaaa","resource":"a","worktree":"/repo/wt-live","branch":"b","claimed_at":"t","issue":-3}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; id must be lowercase hex, resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, gitdir must be non-empty and free of control characters when present, and issue must be a non-negative integer when present (glob)
```

## A lock held past the wait is reported, never broken

Deciding that another process has abandoned a lock cannot be made safe with these primitives: the check and the removal are separate steps, so two waiters can both decide to break the same lock and the second deletes the fresh one the first just took. A held lock is therefore reported and the user removes it.

When the owner has exited, the message says so, which is what makes it actionable.

```scrut
$ setup_claims \
>   && mkdir -p "${claim_file}.lock" \
>   && sh -c 'echo $$' > "${claim_file}.lock/owner" \
>   && claims_tail claim logic --worktree /repo/wt-live --branch feature/live
manage-resource-claims: */.claude/worktree-resources.local.json.lock is held by process *, which has exited; remove that directory (glob)
[1]
```

## A lock whose owner is still running says to wait

```scrut
$ setup_claims \
>   && mkdir -p "${claim_file}.lock" \
>   && printf '%s' "$$" > "${claim_file}.lock/owner" \
>   && claims_tail claim logic --worktree /repo/wt-live --branch feature/live
manage-resource-claims: */.claude/worktree-resources.local.json.lock is held by process *, which is still running; wait for it to finish (glob)
[1]
```

## A lock with no recorded owner is reported as unrecorded

```scrut
$ setup_claims \
>   && mkdir -p "${claim_file}.lock" \
>   && claims_tail claim logic --worktree /repo/wt-live --branch feature/live
manage-resource-claims: */.claude/worktree-resources.local.json.lock is held by an unrecorded process; remove that directory if no claim is in progress (glob)
[1]
```

## A claim on a prunable worktree is stale

Git keeps listing a worktree whose directory has been deleted and marks the record `prunable` rather than dropping it. Reading only the `worktree` lines would count that as live and hold its resource forever, which is the case this feature exists to clear. Deleting the directory outright is the ordinary way to reach that state; `git worktree remove` and `workmux remove` drop the record instead.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-prunable --branch feature/prunable > /dev/null \
>   && claims_list
resource=logic state=stale id=* branch=feature/prunable claimed=TIMESTAMP worktree=/repo/wt-prunable (glob)
```

## A version in scientific notation reports the version, not a syntax error

`1e100` satisfies the integer check, so comparing it in Bash arithmetic would fail as a syntax error rather than naming the unsupported version. The comparison happens in jq for that reason.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 1e100, "claims": []}' > "${claim_file}" \
>   && claims list 2>&1
manage-resource-claims: */.claude/worktree-resources.local.json declares version 1E+100; this script supports version 1 only, so it will not read or rewrite the file (glob)
[1]
```

## Version zero is refused rather than rewritten

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 0, "claims": []}' > "${claim_file}" \
>   && claims list 2>&1
manage-resource-claims: */.claude/worktree-resources.local.json declares version 0; this script supports version 1 only, so it will not read or rewrite the file (glob)
[1]
```

## A claim survives its worktree being moved

`git worktree move` changes the path and keeps the branch, so matching on the path alone would read a live holder as stale and let another worktree take the resource without anyone being asked. `/repo/moved-away` is a path git no longer lists, but `feature/live` is a branch it does.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/moved-away --branch feature/live > /dev/null \
>   && claims_list
resource=logic state=held id=* branch=feature/live claimed=TIMESTAMP worktree=/repo/moved-away (glob)
```

## A claim survives its worktree switching branch

The mirror case: `git switch` changes the branch and keeps the path.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/since-switched > /dev/null \
>   && claims_list
resource=logic state=held id=* branch=feature/since-switched claimed=TIMESTAMP worktree=/repo/wt-live (glob)
```

## A claim is stale only when neither path nor branch matches

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-gone --branch feature/gone > /dev/null \
>   && claims_list
resource=logic state=stale id=* branch=feature/gone claimed=TIMESTAMP worktree=/repo/wt-gone (glob)
```

## Only an exact path and branch match counts as the same worktree

Same worktree means both fields match, which is deliberately stricter than the staleness rule that accepts either. Matching either here would be unsafe: if worktree A claims on a branch, switches away, and worktree B checks out that branch, B would match A's claim by branch and silently take a resource nobody agreed to hand over.

The cost is that a worktree refreshing its own claim after `git worktree move` or `git switch` is asked to confirm a takeover of itself, which is visible and answerable rather than silent and wrong. Both rules point the same way: when the evidence is ambiguous, keep the claim and ask.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims_tail claim logic --worktree /repo/moved-away --branch feature/live
resource "logic" is held by feature/live at /repo/wt-live, claimed *, id *; pass --take-over * to claim it anyway (glob)
[3]
```

## An exact match is a refresh

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live
refreshed the claim on "logic" for feature/live
```

## A genuinely different worktree is still refused

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims_tail claim logic --worktree /repo/main --branch main
resource "logic" is held by feature/live at /repo/wt-live, claimed *, id *; pass --take-over * to claim it anyway (glob)
[3]
```

## An unreadable claim file reports which file and why

An existing but unreadable file is a real case: a permissions mistake, or a directory in the file's place. The `"$(< path)"` expansion would fail during expansion rather than as a command, bypassing the error message and exiting with Bash's own unprefixed diagnostic.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[]}' > "${claim_file}" \
>   && chmod 000 "${claim_file}" \
>   && claims_tail list
manage-resource-claims: */.claude/worktree-resources.local.json exists but cannot be read (glob)
[1]
```

## A file holding two JSON documents is refused

`jq empty` accepts a stream of several top-level values, so two concatenated documents pass it and every envelope check, since `-e` reports only the last result. The reads would then see both.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[]} {"version":1,"claims":[]}' > "${claim_file}" \
>   && claims_tail list
manage-resource-claims: */.claude/worktree-resources.local.json holds more than one JSON document; it must hold exactly one object (glob)
[1]
```

## A directory in the claim file's place is refused

`-r` is true for a readable directory, so a file-type check has to come first or the `"$(< path)"` expansion fails with Bash's own unprefixed diagnostic.

```scrut
$ setup_claims \
>   && mkdir -p "${claim_file}" \
>   && claims_tail list
manage-resource-claims: */.claude/worktree-resources.local.json exists but is not a regular file (glob)
[1]
```

## A file whose first non-whitespace byte is NUL is refused, not read as empty

An emptiness probe that routes the file through a shell variable reintroduces the truncation the by-path reads exist to avoid: command substitution stops at a NUL, so such a file would look empty, return no claims, and be replaced by the next mutation. Counting the values jq yields separates empty from malformed without ever reading the bytes into the shell.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '   \000{"version":1,"claims":[]}' > "${claim_file}" \
>   && claims_tail list
manage-resource-claims: */.claude/worktree-resources.local.json is not valid JSON; fix or remove it (glob)
[1]
```

## A whitespace-only file is still no claims

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '  \n\t\n ' > "${claim_file}" \
>   && claims list \
>   && echo "no claims"
no claims
```

## A lock path occupied by a regular file fails at once

Treating every `mkdir` failure as contention costs the full timeout and then reports a held lock, telling the user to remove a directory that does not exist. Contention is specifically the case where the lock directory is there.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && touch "${claim_file}.lock" \
>   && claims_tail claim logic --worktree /repo/wt-live --branch feature/live
manage-resource-claims: cannot create */.claude/worktree-resources.local.json.lock; check that */.claude is writable and that nothing else occupies that path (glob)
[1]
```

## An unwritable parent fails at once

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && chmod 500 "$(dirname "${claim_file}")" \
>   && claims_tail claim logic --worktree /repo/wt-live --branch feature/live
manage-resource-claims: cannot create */.claude/worktree-resources.local.json.lock; check that */.claude is writable and that nothing else occupies that path (glob)
[1]
```

## A claim survives its worktree being moved and switched

`git worktree move` changes the path and `git switch` changes the branch, so a worktree that has had both done matches neither stored field. The claim records the worktree's git admin directory, which survives both, and that is what keeps it live. Without it the claim reads stale and another worktree takes the resource with nobody asked.

The stored path and branch are rewritten here to values git does not list, which is the state those two operations leave behind.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && jq '.claims[0].worktree="/gone" | .claims[0].branch="gone"' "${claim_file}" > "${claim_file}.new" \
>   && mv "${claim_file}.new" "${claim_file}" \
>   && claims_list
resource=logic state=held id=* branch=gone claimed=TIMESTAMP worktree=/gone (glob)
```

## The identity is what keeps it live, not the path or the branch

The same record with its `gitdir` removed is stale, which is what makes the case above a test of the identity rather than of the fallback.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && jq '.claims[0].worktree="/gone" | .claims[0].branch="gone" | .claims[0] |= del(.gitdir)' "${claim_file}" > "${claim_file}.new" \
>   && mv "${claim_file}.new" "${claim_file}" \
>   && claims_list
resource=logic state=stale id=* branch=gone claimed=TIMESTAMP worktree=/gone (glob)
```

## A worktree the identity cannot be resolved for still records a claim

`rev-parse` fails for a path that is not a worktree, and the claim falls back to the path and branch rather than being refused.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/not-a-worktree --branch feature/live > /dev/null \
>   && jq -r '.claims[0] | has("gitdir")' "${claim_file}"
false
```

## A path reused by an unrelated worktree does not keep an obsolete claim held

An identity settles staleness in both directions. Judging a claim that has one by the path or branch as well would let a path since reused by a different worktree hold the obsolete claim forever, and no later `check` or `prune` could clear it: the path keeps matching.

Here the stored path and branch still match a live record, and only the admin directory differs.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && jq '.claims[0].gitdir="/admin/somewhere-else"' "${claim_file}" > "${claim_file}.new" \
>   && mv "${claim_file}.new" "${claim_file}" \
>   && claims_list
resource=logic state=stale id=* branch=feature/live claimed=TIMESTAMP worktree=/repo/wt-live (glob)
```

## prune clears a claim whose path was reused

The consequence of getting the rule above wrong is a claim no command can remove, so this checks the remedy actually reaches it.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && jq '.claims[0].gitdir="/admin/somewhere-else"' "${claim_file}" > "${claim_file}.new" \
>   && mv "${claim_file}.new" "${claim_file}" \
>   && claims prune \
>   && claims list \
>   && echo "none left"
pruned "logic" from feature/live at /repo/wt-live
none left
```

## A claim from a linked worktree is written under the main worktree

This is the mechanism the whole feature rests on: worktrees share a repository but not a working tree, so one shared file has to be reachable from every one of them. `claim_file_path` resolves it from the first record of `git worktree list --porcelain -z`, which is always the main worktree.

Every other case here sets `WORKTREE_RESOURCES_FILE`, which bypasses that resolution entirely, so this is the only case that exercises it succeeding. It runs with the override unset and asserts the file lands under the main worktree rather than the linked one it was invoked from.

```scrut
$ setup_shared \
>   && ( cd "${linked_worktree}" && claims_shared claim logic --worktree "${linked_worktree}" --branch feature/live ) \
>   && test -f "${main_worktree}/.claude/worktree-resources.local.json" && echo "written under the main worktree" \
>   && test ! -e "${linked_worktree}/.claude/worktree-resources.local.json" && echo "not under the linked worktree"
claimed "logic" for feature/live
written under the main worktree
not under the linked worktree
```

## A claim made in one worktree is visible from another

The point of resolving one shared path: a second worktree reading with the override unset sees the first worktree's claim.

```scrut
$ setup_shared \
>   && ( cd "${linked_worktree}" && claims_shared claim logic --worktree "${linked_worktree}" --branch feature/live > /dev/null ) \
>   && ( cd "${main_worktree}" && claims_shared list | sed 's/claimed=[^ ]*/claimed=TIMESTAMP/' | sed 's/id=[^ ]*/id=ID/' )
resource=logic state=held id=ID branch=feature/live claimed=TIMESTAMP worktree=* (glob)
```

## A live record whose identity cannot be resolved falls back rather than going stale

`rev-parse` can fail for a worktree git still lists. Judging a claim that carries a `gitdir` on that alone would then read it as stale, and `claim` would replace a live holder with nobody asked, which is the outcome the identity was added to prevent.

An identity decides a match only where both the claim and the record have one. Here the record has none, so the path and branch decide, and the claim stays held.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"id":"aaaaaaaaaaaa","resource":"logic","worktree":"/repo/wt-live","branch":"feature/live","gitdir":"/admin/wt-live","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims_no_identity list
resource=logic state=held id=aaaaaaaaaaaa branch=feature/live claimed=t worktree=/repo/wt-live
```

## A record that does resolve an identity still overrides a reused path

The other half of the same rule: where both sides have an identity, a mismatch wins even though the path matches.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"id":"aaaaaaaaaaaa","resource":"logic","worktree":"/repo/wt-live","branch":"feature/live","gitdir":"/admin/somewhere-else","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims list
resource=logic state=stale id=aaaaaaaaaaaa branch=feature/live claimed=t worktree=/repo/wt-live
```

## Releasing by path releases a claim whose worktree has moved

`git worktree move` changes the path but not the admin directory, and a claim deliberately holds across it. Releasing by the worktree's current path would otherwise report `no claim to release` and leave the claim behind, which is the failure the identity was supposed to rule out rather than introduce.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"id":"aaaaaaaaaaaa","resource":"logic","worktree":"/repo/wt-old","branch":"feature/live","gitdir":"/admin/wt-live","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims release --worktree /repo/wt-live \
>   && jq -c '.claims' "${claim_file}"
released "logic" held by feature/live
[]
```

## Releasing by a reused path leaves another worktree's claim alone

The same rule in the other direction. The path matches, but it is a different worktree's now, and releasing on the path alone would drop a claim its holder still has.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"id":"aaaaaaaaaaaa","resource":"logic","worktree":"/repo/wt-live","branch":"feature/live","gitdir":"/admin/somewhere-else","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims release --worktree /repo/wt-live \
>   && jq -c '[.claims[].resource]' "${claim_file}"
no claim to release
["logic"]
```

## Releasing by path still matches a claim that has no identity

A claim recorded before the worktree existed carries no `gitdir`, so the path is all there is to match on.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"id":"aaaaaaaaaaaa","resource":"logic","worktree":"/repo/wt-live","branch":"feature/live","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims release --worktree /repo/wt-live \
>   && jq -c '.claims' "${claim_file}"
released "logic" held by feature/live
[]
```

## A recycled admin directory keeps an obsolete claim held

git names a worktree's admin directory after its basename and gives that name to the next worktree with the same basename once the first is removed, so the identity names a worktree rather than an instance of one. A claim whose worktree is gone then reports held, naming a holder that no longer exists, and `prune` does not clear it because it does not read as stale.

This pins the behavior the documentation describes. Changing the matching rule fails this case, which is the point: the fix and the prose have to move together. The options and the decision to ship this one are recorded in issue 424.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"id":"aaaaaaaaaaaa","resource":"logic","worktree":"/repo/wt-removed","branch":"feature/removed","gitdir":"/admin/wt-live","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims list \
>   && claims prune
resource=logic state=held id=aaaaaaaaaaaa branch=feature/removed claimed=t worktree=/repo/wt-removed
no stale claims
```

## check describes a stale claim without claiming the worktree is gone

A claim goes stale when it no longer matches a live worktree, which is not the same as its worktree having been removed. A path reused by a different worktree is stale while the path itself still exists, so wording the report as "that worktree no longer exists" would describe a directory the user can see is there.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && jq '.claims[0].gitdir="/admin/somewhere-else"' "${claim_file}" > "${claim_file}.new" \
>   && mv "${claim_file}.new" "${claim_file}" \
>   && claims_check_report logic
resource "logic" has a stale claim from feature/live at /repo/wt-live, claimed TIMESTAMP; that claim no longer matches a live worktree
```
