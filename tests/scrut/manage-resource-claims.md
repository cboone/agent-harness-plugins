# Manage resource claims

Tests for recording and reporting the exclusive resources held by git worktrees.

Staleness is derived from `git worktree list --porcelain`, so every testcase drives that through `tests/fixtures/git-worktree-stub` rather than the ambient repository. `/repo/wt-live` is a worktree git reports; `/repo/wt-gone` is not, which is what makes a claim on it stale.

## Test helpers

`claims_tail` and `claims_check_report` exist because a pipeline reports the exit code of its last command. Piping straight into `tail` or `sed` would replace the script's status with the filter's, and every error case here asserts a status.

```scrut
$ function setup_claims() {
>   claim_file="$(mktemp -d)/.claude/worktree-resources.local.json"
>   stub_dir="$(mktemp -d)"
>   cp "${GIT_WORKTREE_STUB_BIN}" "${stub_dir}/git"
>   chmod +x "${stub_dir}/git"
>   live_porcelain="$(printf 'worktree /repo/main\nHEAD aaa\nbranch refs/heads/main\n\nworktree /repo/wt-live\nHEAD bbb\nbranch refs/heads/feature/live\n')"
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

## Claiming a held resource takes it over and says so

The gate lives in `check` and in the skill that asks the user, so a claim is never refused here. A user who has decided to override needs a way to say so.

```scrut
$ setup_claims \
>   && claims claim logic --worktree /repo/wt-live --branch feature/live > /dev/null \
>   && claims claim logic --worktree /repo/main --branch main \
>   && claims list | wc -l | tr -d ' '
claimed "logic" for main, taking it over from feature/live
1
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
manage-resource-claims: */.claude/worktree-resources.local.json is not a claim file; expected an object with a numeric "version" and a "claims" array (glob)
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
manage-resource-claims: */.claude/worktree-resources.local.json declares version 999, newer than this script understands (1); upgrade the script rather than letting it overwrite the file (glob)
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
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; each needs a non-empty resource, worktree and branch, a claimed_at string, and a numeric issue when present (glob)
[1]
```

## A stored claim with a non-numeric issue is refused

```scrut
$ setup_claims \
>   && mkdir -p "$(dirname "${claim_file}")" \
>   && printf '{"version": 1, "claims": [{"resource":"a","worktree":"/repo/wt-live","branch":"b","claimed_at":"t","issue":"x"}]}' > "${claim_file}" \
>   && claims list 2>&1 | tail -1
manage-resource-claims: */.claude/worktree-resources.local.json holds a malformed claim; each needs a non-empty resource, worktree and branch, a claimed_at string, and a numeric issue when present (glob)
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

## An abandoned lock is broken rather than waited on forever

A process terminated mid-write leaves its lock directory behind. Honoring it indefinitely would block every later claim, which is the same failure a stale claim would cause and is ruled out for the same reason.

```scrut
$ setup_claims \
>   && mkdir -p "${claim_file}.lock" \
>   && touch -t 200001010000 "${claim_file}.lock" \
>   && claims claim logic --worktree /repo/wt-live --branch feature/a
claimed "logic" for feature/a
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
manage-resource-claims: check requires a resource name
[1]
```

## claim without a resource name

```scrut
$ setup_claims && claims_tail claim --worktree /repo/wt-live
manage-resource-claims: claim requires a resource name
[1]
```

## check refuses an option in place of a resource name

Without this guard a mistyped flag is read as a resource nobody has claimed, so `check` reports it free and exits 0. A caller branching on that exit code would then proceed as though the resource were available.

```scrut
$ setup_claims && claims_tail check --json
manage-resource-claims: check requires a resource name
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
