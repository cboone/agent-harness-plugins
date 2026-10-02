# Plugin validator: catalog and Codex budget

Tests for the `bin/validate-plugins` rules over plugin manifests, catalog
version state and the Codex skill inventory budget. Most cases run it through
`tests/fixtures/validate-plugin-fixture`, which validates a disposable copy of
the repository after one targeted mutation, so each case pays for a full
validator run. `validate-plugins-skills.md` covers the rules over skill bodies;
the two are separate documents so CI runs them in parallel.

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
Codex skill inventory: * skills cost * of 4840 tokens available under the 5440-token budget for gpt-6-astra, and * of 5600 characters available under the 8000-character fallback. Withheld from implicit invocation and not charged: *. (glob)
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
budget, draws a warning but does not fail the run. Like the previous scenario, it
widens the context window so catalog headroom cannot decide the outcome.

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
Codex skill inventory: * skills cost * of 5600 characters available under the 8000-character fallback; no reference context window is set. Withheld from implicit invocation and not charged: *. (glob)
::error::Codex skill inventory is * characters, over the 5600 available (8000-character fallback budget less a 2400-character system-skill reserve). Descriptions are * (glob)
1 plugin validation error(s) found.
[1]
```

A skill whose generated manifest sets `policy.allow_implicit_invocation: false`
is withheld from Codex's list, so it costs nothing. Withholding `release`
drops it from the charged count and the token total, and the run reports it
among the withheld skills.

```scrut
$ charged() { "${VALIDATE_PLUGIN_FIXTURE_BIN}" "${1}" 2>&1 | awk '/^Codex skill inventory:/ { withheld = 0; if (match($0, /not charged: [0-9]+/)) withheld = substr($0, RSTART + 13, RLENGTH - 13); print $4, $7, withheld }'; }
> read -r count tokens withheld <<< "$(charged valid)"
> read -r count_after tokens_after withheld_after <<< "$(charged translated-frontmatter)"
> [[ ${count_after} -eq $((count - 1)) && ${tokens_after} -lt ${tokens} && ${withheld_after} -eq $((withheld + 1)) ]] && echo "withheld skill is not charged"
withheld skill is not charged
```
