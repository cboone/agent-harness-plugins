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
resource=logic state=held branch=feature/live issue=128 claimed=TIMESTAMP worktree=/repo/wt-live
```

## The stored record carries the issue's fields

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live --issue 128 > /dev/null \
>   && jq -c '{version: .version, claim: (.claims[0] | del(.claimed_at))}' "${claim_file}"
{"version":1,"claim":{"resource":"logic","worktree":"/repo/wt-live","branch":"feature/live","issue":128}}
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
resource=simulator state=held branch=feature/live claimed=TIMESTAMP worktree=/repo/wt-live
```

## A held resource exits 3 and names its holder

The distinct exit code is what lets a caller branch on the outcome without parsing the message.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live --issue 128 > /dev/null \
>   && claims_check_report logic
resource "logic" is held by feature/live (issue 128) at /repo/wt-live, claimed TIMESTAMP
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
resource=logic state=stale branch=feature/gone claimed=TIMESTAMP worktree=/repo/wt-gone
```

## check reports a stale claim rather than blocking on it

A worktree that has been removed must not hold a resource forever, so `check` reports the stale claim and still exits 0.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-gone --branch feature/gone > /dev/null \
>   && claims_check_report logic
resource "logic" has a stale claim from feature/gone at /repo/wt-gone, claimed TIMESTAMP; that worktree no longer exists
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
resource=logic state=held branch=feature/live claimed=TIMESTAMP worktree=/repo/wt-live
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
resource "logic" is held by feature/live at /repo/wt-live, claimed *; pass --take-over /repo/wt-live to claim it anyway (glob)
[3]
```

## --take-over claims it anyway and says so

The claim stays advisory: a user who has been asked and said yes needs a way through.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims claim logic --worktree /repo/main --branch main --take-over /repo/wt-live \
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
resource=disk state=held branch=feature/live claimed=TIMESTAMP worktree=/repo/wt-live
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
resource=simulator state=held branch=main claimed=TIMESTAMP worktree=/repo/main
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
resource=disk state=held branch=feature/live claimed=TIMESTAMP worktree=/repo/wt-live
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
>   && printf '{"version": 1, "claims": [{"resource": "logic"}]}' > "${claim_file}" \
>   && claims list 2>&1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, and issue must be a non-negative integer when present (glob)
[1]
```

## A stored claim with a non-numeric issue is refused

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 1, "claims": [{"resource":"a","worktree":"/repo/wt-live","branch":"b","claimed_at":"t","issue":"x"}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, and issue must be a non-negative integer when present (glob)
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
>   && printf '{"version": 1, "claims": [{"resource":"a b","worktree":"/repo/wt-live","branch":"b","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, and issue must be a non-negative integer when present (glob)
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
resource=logic state=held branch=feature/live claimed=TIMESTAMP worktree=/repo/wt-live
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

The declared version is compared with Bash arithmetic, so a JSON `1.5` that passed a bare number check would fail as an arithmetic syntax error rather than the schema error this is meant to report.

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
>   && printf '{"version": 1, "claims": [{"resource":"-logic","worktree":"/repo/wt-live","branch":"b","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, and issue must be a non-negative integer when present (glob)
```

## A stored branch carrying whitespace is refused

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 1, "claims": [{"resource":"a","worktree":"/repo/wt-live","branch":"b c","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, and issue must be a non-negative integer when present (glob)
```

## A worktree path containing spaces is still accepted

A path legitimately may contain spaces, which is why `list` emits `worktree=` last.

```scrut
$ setup_claims \
>   && claims claim logic --worktree "/repo/with space" --branch feature/live > /dev/null \
>   && claims_list
resource=logic state=stale branch=feature/live claimed=TIMESTAMP worktree=/repo/with space
```

## Two claims on one resource are refused

One claim per resource is the invariant every lookup assumes. `claim_for_resource` answers with the first match, so a duplicate would let a stale record hide a live holder behind it and slip a takeover past the guard in `claim`.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"resource":"logic","worktree":"/repo/wt-gone","branch":"a","claimed_at":"t"},{"resource":"logic","worktree":"/repo/wt-live","branch":"b","claimed_at":"t"}]}' > "${claim_file}" \
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
>   && printf '{"version":1,"claims":[{"resource":"a","worktree":"/a\\n/b","branch":"b","claimed_at":"t"}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, and issue must be a non-negative integer when present (glob)
```

## --take-over naming a holder that no longer holds it is refused

Approval is about a particular holder. If a third worktree takes the resource between the check and the write, consent to displace the first says nothing about displacing it, and a boolean flag could not tell the two apart.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims_tail claim logic --worktree /repo/main --branch main --take-over /repo/somewhere-else
resource "logic" is held by feature/live at /repo/wt-live, claimed *; --take-over named /repo/somewhere-else, which no longer holds it, so nothing was changed (glob)
[3]
```

## --take-over requires the holder path

```scrut
$ setup_claims && claims_tail claim logic --worktree /repo/main --branch main --take-over
manage-resource-claims: --take-over requires the worktree path of the holder being displaced
[1]
```

## A stored issue must be a non-negative integer

The CLI accepts only digit strings for `--issue`, so the read contract has to match: a hand-edited `1.5` or `-3` would otherwise survive every later rewrite and surface as an impossible issue number.

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"resource":"a","worktree":"/repo/wt-live","branch":"b","claimed_at":"t","issue":1.5}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, and issue must be a non-negative integer when present (glob)
```

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version":1,"claims":[{"resource":"a","worktree":"/repo/wt-live","branch":"b","claimed_at":"t","issue":-3}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; resource, branch and claimed_at must be non-empty and whitespace-free, resource must not start with a hyphen, worktree must be non-empty and free of control characters, and issue must be a non-negative integer when present (glob)
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
resource=logic state=stale branch=feature/prunable claimed=TIMESTAMP worktree=/repo/wt-prunable
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
