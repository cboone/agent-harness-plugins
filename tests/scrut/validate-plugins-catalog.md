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
list, name and aliased installed path included. It charges the most expensive
75 percent of those lines, the share of the catalog the maintainer enables,
against 2 percent of the reference model's context window, less a reserve for
skills from other sources. Every normal run reports the cost against that
budget.

The limits below are exercised through overrides; the recorded budget is never
raised to fit content.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" valid 2>&1 | grep '^Codex skill inventory:'
Codex skill inventory: the * most expensive of * skills (75 percent) cost * of 4290 tokens available under the 5440-token budget for gpt-6.1-sol. Withheld from implicit invocation and not charged: *. (glob)
```

A single description over Codex's 1,024-character limit is an error however
much room the budget has left; the scenario widens the context window so the
length is the only fault. Its description, cut to 1,024 characters, makes its
line the most expensive in the catalog by far, so charging 1 percent of the
catalog shows both that the share rounds up, a fraction of a skill counting as
a whole one, and that the counted skill is the most expensive one: no other
line, even with the 18-token roots table row, reaches 256 tokens.

```scrut
$ { CODEX_ENABLED_SKILL_PERCENT=1 "${VALIDATE_PLUGIN_FIXTURE_BIN}" oversized-description 2>&1; echo "exit ${?}"; } | awk '{ print } /^Codex skill inventory:/ { verdict = ($5 == 1 && $14 >= 256) ? "the most expensive skill is counted" : "unexpected selection: " $5 " costing " $14 } END { print verdict }'
::error::Skill 'plugins/release/skills/release/SKILL.md' description is 1100 characters, exceeding the 1024-character limit
Codex skill inventory: the 1 most expensive of * skills (1 percent) cost * (glob)
1 plugin validation error(s) found.
exit 1
the most expensive skill is counted
```

A routing description over 240 characters, its average share of the budget,
draws a warning but does not fail the run. Like the previous scenario, it widens
the context window so catalog headroom cannot decide the outcome.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" long-description 2>&1
::warning::Skill 'plugins/release/skills/release/SKILL.md' routing description is 250 characters; keep it within 240, its average share of the Codex discovery budget
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
Codex skill inventory: the * most expensive of * skills (75 percent) cost * of 850 tokens available under the 2000-token budget for gpt-6.1-sol.* (glob)
::error::Codex skill inventory costs * tokens, over the 850 available (2000-token budget for gpt-6.1-sol less a 1150-token reserve for skills from other sources). Descriptions are * of its * bytes; names, paths, the roots table row and line syntax are the rest. Largest entries in tokens: *. Tighten the largest routing descriptions rather than raising the budget. (glob)
1 plugin validation error(s) found.
[1]
```

Names and paths count. Here the counted descriptions alone fit the budget, as a
description-only check would measure them, but their full lines do not.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" path-overhead 2>&1 | sed -nE 's/^::error::Codex skill inventory costs ([0-9]+) tokens, over the ([0-9]+) available.* Descriptions are ([0-9]+) of .*/\1 \2 \3/p' | awk '{ print (($3 + 3) / 4 <= $2 && $2 < $1) ? "descriptions fit; names and paths exceed the budget" : "premise not met: " $0 }'
descriptions fit; names and paths exceed the budget
```

The budget is always the reference model's, so an empty context window is an
error rather than a request for Codex's character budget for unknown models.
The other overrides are held to plain decimal of bounded length, because Bash
arithmetic reads a leading zero as octal and wraps a value past 64 bits: this
enabled share wraps to 10 percent, and this reserve is not valid octal. Each
invalid override is an error, and none reaches the budget check.

```scrut
$ CODEX_ENABLED_SKILL_PERCENT=18446744073709551626 CODEX_OTHER_SKILL_RESERVE_TOKENS=0900 "${VALIDATE_PLUGIN_FIXTURE_BIN}" empty-context-window 2>&1
::error::CODEX_REFERENCE_CONTEXT_WINDOW must be a positive decimal integer below 1000000000
::error::CODEX_ENABLED_SKILL_PERCENT must be a decimal integer from 1 to 100
::error::CODEX_OTHER_SKILL_RESERVE_TOKENS must be a non-negative decimal integer below 1000000000
3 plugin validation error(s) found.
[1]
```

A skill whose generated manifest sets `policy.allow_implicit_invocation: false`
is withheld from Codex's list, so it costs nothing. Withholding `release`
drops it from the skill count and the token total, and the run reports it among
the withheld skills. Charging the whole catalog keeps another skill from taking
its place among the counted share.

```scrut
$ charged() { CODEX_ENABLED_SKILL_PERCENT=100 "${VALIDATE_PLUGIN_FIXTURE_BIN}" "${1}" 2>&1 | awk '/^Codex skill inventory:/ { withheld = 0; if (match($0, /not charged: [0-9]+/)) withheld = substr($0, RSTART + 13, RLENGTH - 13); print $9, $14, withheld }'; }
> read -r count tokens withheld <<< "$(charged valid)"
> read -r count_after tokens_after withheld_after <<< "$(charged translated-frontmatter)"
> [[ ${count_after} -eq $((count - 1)) && ${tokens_after} -lt ${tokens} && ${withheld_after} -eq $((withheld + 1)) ]] && echo "withheld skill is not charged"
withheld skill is not charged
```
