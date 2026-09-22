# Repository tooling

Tests for the `bin/` scripts that gate generated output and catalog releases.

## Marketplace entries do not duplicate plugin versions

Each plugin manifest remains the SemVer source. Both marketplace files omit
entry and aggregate versions, so a plugin bump leaves catalog registration
metadata unchanged.

```scrut
$ cd "${REPO_ROOT}" && jq -e 'all(.plugins[]; has("version") | not) and (.metadata | has("version") | not)' .claude-plugin/marketplace.json > /dev/null && jq -e 'all(.plugins[]; has("version") | not) and (.metadata | has("version") | not)' .agents/plugins/marketplace.json > /dev/null && for manifest in plugins/*/.claude-plugin/plugin.json; do jq -e '.version | strings | test("^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$")' "${manifest}" > /dev/null || exit 1; done && bin/validate-plugins && echo version-state-clean
Codex skill inventory: * (glob)
All plugin validations passed.
version-state-clean
```

## Validator rejects forbidden version state

Each case starts from a generated copy of the repository, then mutates one
surface. This exercises the validator itself instead of duplicating its rules
with a separate `jq` check. Every run also reports the Codex skill inventory,
which the next section covers, and a valid run warns about nothing.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" valid
Codex skill inventory: * (glob)
All plugin validations passed.
```

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" leading-zero 2>&1
::error::Plugin 'release': plugin.json version '01.2.3' must be MAJOR.MINOR.PATCH
Codex skill inventory: * (glob)
1 plugin validation error(s) found.
[1]
```

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" metadata-version 2>&1
::error::Marketplace metadata must not contain a version
Codex skill inventory: * (glob)
1 plugin validation error(s) found.
[1]
```

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" entry-version 2>&1
::error::Marketplace entry 'add-cobra-version' must not contain a version
Codex skill inventory: * (glob)
1 plugin validation error(s) found.
[1]
```

## The Codex skill inventory fits Codex's discovery budget

Rule 17 renders each generated skill as the line Codex puts in its initial skill
list, name and installed path included, and budgets the whole list at 2 percent
of the reference model's context window, less a reserve for Codex's own system
skills. Every normal run reports the cost against that budget and against the
8,000-character fallback Codex uses when the context window is unknown.

The limits below are exercised through overrides; the recorded budget is never
raised to fit content.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" valid 2>&1 | grep '^Codex skill inventory:'
Codex skill inventory: * skills cost * of 4840 tokens available under the 5440-token budget for gpt-6-astra, and * of 5600 characters available under the 8000-character fallback. (glob)
```

A single description over Codex's 1,024-character limit is an error however
much room the budget has left; the scenario widens the context window so the
length is the only fault.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" oversized-description 2>&1
::error::Skill 'plugins/release/skills/release/SKILL.md' description is 1100 characters, exceeding the 1024-character limit
Codex skill inventory: * (glob)
1 plugin validation error(s) found.
[1]
```

A routing description over 150 characters, its average share of the primary
budget, draws a warning but does not fail the run.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" long-description 2>&1
::warning::Skill 'plugins/release/skills/release/SKILL.md' routing description is 200 characters; keep it within 150, its average share of the Codex discovery budget
Codex skill inventory: * (glob)
All plugin validations passed.
```

A skill with no name has nothing for Codex to list it under, so an empty `name`
is an error.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" empty-name 2>&1
::error::Skill 'plugins/release/skills/release/SKILL.md' has an empty name
Codex skill inventory: * (glob)
1 plugin validation error(s) found.
[1]
```

A catalog over the primary budget fails with its total, the budget and reserve,
the largest entries, and what to do about it.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" aggregate-overflow 2>&1
Codex skill inventory: * skills cost * of 1400 tokens available under the 2000-token budget for gpt-6-astra, and * (glob)
::error::Codex skill inventory costs * tokens, over the 1400 available (2000-token budget for gpt-6-astra less a 600-token system-skill reserve). Descriptions are * of its * bytes; names, paths and line syntax are the rest. Largest entries in tokens: *. Tighten the largest routing descriptions rather than raising the budget. (glob)
1 plugin validation error(s) found.
[1]
```

Names and paths count. Here the descriptions alone fit the budget, as the
previous description-only check would have measured them, but the full lines do
not.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" path-overhead 2>&1 | sed -nE 's/^::error::Codex skill inventory costs ([0-9]+) tokens, over the ([0-9]+) available.* Descriptions are ([0-9]+) of .*/\1 \2 \3/p' | awk '{ print (($3 + 3) / 4 <= $2 && $2 < $1) ? "descriptions fit; names and paths exceed the budget" : "premise not met: " $0 }'
descriptions fit; names and paths exceed the budget
```

An empty context window models Codex not knowing it, which selects the
8,000-character fallback.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" fallback 2>&1
Codex skill inventory: * skills cost * of 5600 characters available under the 8000-character fallback; no reference context window is set. (glob)
::error::Codex skill inventory is * characters, over the 5600 available (8000-character fallback budget less a 2400-character system-skill reserve). Descriptions are * (glob)
1 plugin validation error(s) found.
[1]
```

## Generated Codex skills match their canonical sources

Rule 16 accepts whatever the generator produces, so a generator that rewrote
routing descriptions, as `bin/build-codex-marketplace` once did for every
skill, would pass it. Rule 16b compares each generated `SKILL.md` with its
canonical source directly.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" rewriting-generator 2>&1
::error::Generated Codex skill 'dist/codex/plugins/release/skills/release/SKILL.md' differs from its canonical source 'plugins/release/skills/release/SKILL.md'; the generator copies SKILL.md files unchanged unless disable-model-invocation is translated
Codex skill inventory: * (glob)
1 plugin validation error(s) found.
[1]
```

One difference is sanctioned. Codex ignores `disable-model-invocation`, so the
generator drops the line and writes `agents/openai.yaml` instead, and rule 16b
accepts that exact pair of edits.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" translated-frontmatter 2>&1
Codex skill inventory: * (glob)
All plugin validations passed.
```

A generator that left the line in the Codex copy would ship a policy Codex
ignores.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" untranslated-frontmatter 2>&1
::error::Generated Codex skill 'dist/codex/plugins/release/skills/release/SKILL.md' differs from its canonical source 'plugins/release/skills/release/SKILL.md' by more than the translated disable-model-invocation line
Codex skill inventory: * (glob)
1 plugin validation error(s) found.
[1]
```

A generator that dropped the line without writing the manifest would lose the
policy altogether, which is the quieter of the two failures.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" missing-openai-yaml 2>&1
::error::Generated Codex skill 'dist/codex/plugins/release/skills/release/SKILL.md' drops disable-model-invocation without writing 'dist/codex/plugins/release/skills/release/agents/openai.yaml'
Codex skill inventory: * (glob)
1 plugin validation error(s) found.
[1]
```

## Skill frontmatter fields are on the allowlist

Claude Code accepts around twenty `SKILL.md` frontmatter fields, OpenCode
documents five and Codex CLI two, and all three tolerate what they do not
recognize. A misspelled field therefore changes nothing in any harness and
reports nothing, so rule 21 names the fields this repository ships.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" unknown-frontmatter-field 2>&1
Codex skill inventory: * (glob)
::error::Skill 'plugins/release/skills/release/SKILL.md' declares frontmatter field 'disable-model-invokation', which is not on the allowlist; see the skill frontmatter section of docs/plugin-development.md
1 plugin validation error(s) found.
[1]
```

A field on the allowlist passes, and reaches Codex and OpenCode unchanged
because both ignore what they do not recognize.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" permitted-frontmatter-field 2>&1
Codex skill inventory: * (glob)
All plugin validations passed.
```

Neither the generator nor rule 16b reads a quoted value, so a quoted
`disable-model-invocation` would translate to nothing and leave the skill
implicitly invocable everywhere.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" quoted-invocation-value 2>&1
Codex skill inventory: * (glob)
::error::Skill 'plugins/release/skills/release/SKILL.md' must write disable-model-invocation as an unquoted true or false
1 plugin validation error(s) found.
[1]
```

## Cross-reference warnings reach a passing run

Rule 19 relays `bin/check-cross-references` output. A run that passes still
shows its warnings, such as a skill that says "invoke `commit`" without
declaring it.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" near-miss-invocation 2>&1
Codex skill inventory: * (glob)
::warning::plugins/release/skills/release/SKILL.md says "invoke `commit`"; if that step runs the commit skill, write "Invoke the `commit` skill" and declare it under ## Skill dependencies
All plugin validations passed.
```

## Validator rejects stale review checklist copies

`set-up-review-config` ships byte-identical copies of each style guide's review
checklist. Rule 20 regenerates them and compares, so a source edited without
`make build`, a copy left behind, or a copy with no detection rules fails. The
fixture never runs the generator, since a rebuild would repair the first two;
the unlisted case removes the Go checklist's entry from `guides.md` instead.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" stale-review-checklist 2>&1
Codex skill inventory: * (glob)
::error::Review checklist copy 'plugins/set-up-review-config/skills/set-up-review-config/references/checklists/write-go-code.md' does not match its source; edit the style guide's references/review-checklist.md, not the copy, and run make build
1 plugin validation error(s) found.
[1]
```

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" orphan-review-checklist 2>&1
Codex skill inventory: * (glob)
::error::Review checklist copy 'plugins/set-up-review-config/skills/set-up-review-config/references/checklists/write-orphan.md' has no source checklist; run make build
1 plugin validation error(s) found.
[1]
```

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" unlisted-review-checklist 2>&1
Codex skill inventory: * (glob)
::error::'plugins/set-up-review-config/skills/set-up-review-config/references/guides.md' does not name ./references/checklists/write-go-code.md; add detection and routing rules for it
1 plugin validation error(s) found.
[1]
```

A source that fails the generator's own checks is relayed rather than
reported as a generic failure.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" invalid-review-checklist 2>&1
Codex skill inventory: * (glob)
::error::plugins/write-go-code/skills/write-go-code/references/review-checklist.md has a list item without a bold rule name, which reviewers cite: - plain item
1 review checklist error(s) found; no copies were written.
1 plugin validation error(s) found.
[1]
```

## Release automation uses immutable tags and ignores documentation-only changes

The fixture executes the workflow's catalog-change, tag/release-check, tag, and
publication shell steps against isolated Git history with custom local source
directories. It also interprets the check and publication step conditions, so an
incorrect condition cannot hide a missing recovery attempt.

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
