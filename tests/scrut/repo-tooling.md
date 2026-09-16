# Repository tooling

Tests for the `bin/` scripts that gate generated output and catalog releases.

## Marketplace entries do not duplicate plugin versions

Each plugin manifest remains the SemVer source. Both marketplace files omit
entry and aggregate versions, so a plugin bump leaves catalog registration
metadata unchanged.

```scrut
$ cd "${REPO_ROOT}" && jq -e 'all(.plugins[]; has("version") | not) and (.metadata | has("version") | not)' .claude-plugin/marketplace.json > /dev/null && jq -e 'all(.plugins[]; has("version") | not) and (.metadata | has("version") | not)' .agents/plugins/marketplace.json > /dev/null && find plugins -path '*/.claude-plugin/plugin.json' -exec jq -e '.version | strings | test("^[0-9]+\\.[0-9]+\\.[0-9]+$")' {} \; > /dev/null && echo version-state-clean
version-state-clean
```

## Release automation uses immutable tags and ignores documentation-only changes

The workflow compares only plugin sources and canonical marketplace metadata
with the latest catalog tag. A changed catalog release uses the landing commit's
full SHA, so aggregate-version collisions cannot occur.

```scrut
$ cd "${REPO_ROOT}" && grep -q "git diff --quiet.*plugins/ .claude-plugin/marketplace.json" .github/workflows/release.yml && grep -q 'tag="catalog-${GITHUB_SHA}"' .github/workflows/release.yml && echo catalog-release-inputs-checked
catalog-release-inputs-checked
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
