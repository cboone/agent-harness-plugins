# Repository tooling

Tests for the `bin/` scripts that gate generated output and catalog releases.

## Marketplace entries do not duplicate plugin versions

Each plugin manifest remains the SemVer source. Both marketplace files omit
entry and aggregate versions, so a plugin bump leaves catalog registration
metadata unchanged.

```scrut
$ cd "${REPO_ROOT}" && jq -e 'all(.plugins[]; has("version") | not) and (.metadata | has("version") | not)' .claude-plugin/marketplace.json > /dev/null && jq -e 'all(.plugins[]; has("version") | not) and (.metadata | has("version") | not)' .agents/plugins/marketplace.json > /dev/null && for manifest in plugins/*/.claude-plugin/plugin.json; do jq -e '.version | strings | test("^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$")' "${manifest}" > /dev/null || exit 1; done && bin/validate-plugins && echo version-state-clean
All plugin validations passed.
version-state-clean
```

## Validator rejects forbidden version state

Each case starts from a generated copy of the repository, then mutates one
surface. This exercises the validator itself instead of duplicating its rules
with a separate `jq` check.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" valid
All plugin validations passed.
```

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" leading-zero 2>&1
::error::Plugin 'release': plugin.json version '01.2.3' must be MAJOR.MINOR.PATCH
1 plugin validation error(s) found.
[1]
```

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" metadata-version 2>&1
::error::Marketplace metadata must not contain a version
1 plugin validation error(s) found.
[1]
```

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" entry-version 2>&1
::error::Marketplace entry 'add-cobra-version' must not contain a version
1 plugin validation error(s) found.
[1]
```

## Release automation uses immutable tags and ignores documentation-only changes

The fixture executes the workflow's actual shell steps against isolated Git
history, with custom local source directories and remote registrations. It also
interprets the check and publication step conditions, so an incorrect condition
cannot hide a missing recovery attempt.

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" first-release
changed=true target=current
release-created-for-target=true
```

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" plugin-change
changed=true target=current
release-created-for-target=true
```

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" unchanged
changed=false target=previous
```

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" root-docs
changed=false target=previous
```

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" catalog-only
changed=true target=current
```

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" deleted-plugin
changed=true target=current
```

## Version comparison accepts unbounded numeric components

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" large-version
changed=true target=current
```

## Publication recovers an earlier tag after a documentation commit

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" tag-recovery
changed=false target=previous
release-created-for-target=true
```

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" same-head-recovery
changed=true target=current
release-created-for-target=true
```

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" existing-release
changed=false target=previous
release-created-for-target=false
```

## Changed plugin content requires a forward version bump

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" new-plugin-version 2>&1
::error::./plugins/new-plugin is newly registered and must start at manifest version 1.0.0 (found 0.1.0).
[1]
```

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" missing-bump 2>&1
::error::./custom/sample changed without a forward manifest version bump (1.0.0 -> 1.0.0).
[1]
```

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" regression 2>&1
::error::./custom/sample changed without a forward manifest version bump (1.0.0 -> 0.9.0).
[1]
```

## Recovery errors do not silently create another release

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" api-error 2>&1
changed=false target=previous
::error::Failed to determine whether GitHub Release catalog-* exists. (glob)
HTTP 403
[2]
```

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" tag-collision 2>&1
changed=false target=previous
::error::Catalog tag catalog-* exists at *, not *. (glob)
[1]
```

```scrut
$ "${CATALOG_RELEASE_FIXTURE_BIN}" missing-remote-tag 2>&1
changed=false target=previous
::error::Recovery tag catalog-* is missing on origin. (glob)
[1]
```

## The shell script list excludes generated mirrors

`dist/` holds byte-identical copies of scripts already listed from `plugins/`,
so linting them would report every finding twice.

Reported alongside the total so a run that lists nothing at all cannot pass this
as a vacuous zero.

```scrut
$ "${LIST_SHELL_SCRIPTS_BIN}" | awk 'BEGIN {d=0} /^dist\// {d++} END {print "dist=" d, "total>10=" (NR>10 ? "yes" : "no")}'
dist=0 total>10=yes
```

## The shell script list reaches scripts under skill references

The previous `plugins/*/scripts/*` lint glob never reached this 33 KB script,
and widening it by hand would have swept in a sibling `.yml`.

```scrut
$ "${LIST_SHELL_SCRIPTS_BIN}" | grep -q 'pin-everything/skills/pin-everything/references/scripts/version-audit-template' && echo found
found
```

## The shell script list contains only Bash scripts

```scrut
$ cd "${REPO_ROOT}" && "${LIST_SHELL_SCRIPTS_BIN}" | while IFS= read -r f; do head -n 1 "${f}" | grep -q bash || echo "not bash: ${f}"; done; echo done
done
```

## No angle-bracket placeholder is padded into a shell redirect

Prettier once rewrote `git diff <base-branch>...HEAD` into
`git diff < base-branch > ...HEAD` inside fenced blocks, which reads a file
named `base-branch` and truncates the commit range. `embeddedLanguageFormatting`
is off now; this guards the seven sites that were repaired.

Checks every prose surface, not just `plugins/`: the repo-local `check-versions`
skill carried two of these too, and a guard scoped to `plugins/` missed them.
`docs/plans/done/` is excluded as a historical archive.

The scanned count is reported as a yes/no so an empty scan, which would make the
zero meaningless, fails the test instead of passing it.

```scrut
$ cd "${REPO_ROOT}" && corrupted="$(grep -rlE '< [a-z][a-z0-9-]+ >' plugins/ .claude/ .github/ README.md AGENTS.md 2>/dev/null | wc -l)" && scanned="$(grep -rl 'git ' plugins/ .claude/ 2>/dev/null | wc -l)" && printf 'corrupted=%d scanned_enough=%s\n' "${corrupted}" "$([ "${scanned}" -gt 20 ] && echo yes || echo no)"
corrupted=0 scanned_enough=yes
```

## The duplicated worktree scripts stay byte-identical

`create-worktree` and `address-issue-in-worktree` ship the same
`compose-issue-prompt`, `launch-workmux` and `manage-resource-claims`. Rule 18
of `bin/validate-plugins` requires every `${CLAUDE_PLUGIN_ROOT}/scripts/NAME`
reference to resolve inside its own plugin, so the two plugins cannot share one
copy.

The copies drifted once before: one grew `--base` support while the other grew
Codex-pane prompt resending, and neither gained the other's feature. These
guards fail the build instead of letting that happen again.

```scrut
$ cd "${REPO_ROOT}" && cmp plugins/create-worktree/scripts/compose-issue-prompt plugins/address-issue-in-worktree/scripts/compose-issue-prompt && echo identical
identical
```

```scrut
$ cd "${REPO_ROOT}" && cmp plugins/create-worktree/scripts/launch-workmux plugins/address-issue-in-worktree/scripts/launch-workmux && echo identical
identical
```

```scrut
$ cd "${REPO_ROOT}" && cmp plugins/create-worktree/scripts/manage-resource-claims plugins/address-issue-in-worktree/scripts/manage-resource-claims && echo identical
identical
```

## Every `$(< path)` read in the bundled scripts is guarded for the same path

A `"$(< path)"` expansion that fails does so _during expansion_, not as a command, so neither a redirection on the assignment nor a trailing `||` catches it: Bash exits with its own unprefixed diagnostic and the script's error handling never runs. The path must therefore be tested before it is read, with `-f` as well as `-r`, because `-r` is true for a readable directory. The matcher allows the optional whitespace Bash permits after `<`, so a read written `$(<"${path}")` is counted rather than skipped.

This shipped broken three times on one branch: the lock owner read, the claim file read, and the lock owner read again after the claim file was fixed. Writing the rule into `.github/instructions/shell.instructions.md` did not stop the third. This does.

The check extracts the path from the read and requires a preceding guard naming that exact path under both predicates, so removing the readability test, or satisfying the check with an unrelated `-f` on some other path, fails it.

```scrut
$ cd "${REPO_ROOT}" && for f in plugins/create-worktree/scripts/manage-resource-claims plugins/address-issue-in-worktree/scripts/manage-resource-claims; do awk '/^[[:space:]]*#/ { next } { line[NR] = $0 } /\$\([[:space:]]*<[[:space:]]*"/ { read_line = $0; sub(/.*\$\([[:space:]]*<[[:space:]]*"/, "", read_line); sub(/".*/, "", read_line); ok = 0; for (i = NR - 12; i < NR; i++) { if (index(line[i], "-f \"" read_line "\"") && index(line[i], "-r \"" read_line "\"")) ok = 1; if (index(line[i], "-f \"" read_line "\"")) f_seen = i; if (index(line[i], "-r \"" read_line "\"")) r_seen = i } if (!ok && f_seen && r_seen) ok = 1; if (ok) guarded++; else { print FILENAME ": unguarded read at line " NR; bad++ } f_seen = 0; r_seen = 0 } END { printf "%s: guarded=%d unguarded=%d\n", FILENAME, guarded+0, bad+0 }' "$f"; done
plugins/create-worktree/scripts/manage-resource-claims: guarded=1 unguarded=0
plugins/address-issue-in-worktree/scripts/manage-resource-claims: guarded=1 unguarded=0
```
