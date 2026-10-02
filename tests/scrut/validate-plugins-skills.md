# Plugin validator: skills

Tests for the `bin/validate-plugins` rules over skill bodies: the generated
Codex copies, frontmatter, cross-references and bundled review checklists.
Every case runs it through `tests/fixtures/validate-plugin-fixture`, which
validates a disposable copy of the repository after one targeted mutation, so
each case pays for a full validator run. `validate-plugins-catalog.md` covers
the catalog rules; the two are separate documents so CI runs them in parallel.

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

Asking only whether the policy is present would let a generator add anything
beside it, and Codex reads the whole manifest. `interface.short_description` is
the sharp case: Codex prints it in place of the skill's description, so a
generator that wrote one would replace every routing description in the Codex
catalog with the policy still correct.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" extra-manifest-key 2>&1
::error::Generated Codex manifest 'dist/codex/plugins/release/skills/release/agents/openai.yaml' must state policy.allow_implicit_invocation false and nothing else
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

Claude Code shows `argument-hint` after a typed slash command, so a skill that
documents an `## Options` section must declare one, or its options stay
hidden at the prompt.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" missing-argument-hint 2>&1
Codex skill inventory: * (glob)
::error::Skill 'plugins/release/skills/release/SKILL.md' has an ## Options section but no argument-hint; see the skill frontmatter section of docs/plugin-development.md
1 plugin validation error(s) found.
[1]
```

Only a non-empty double-quoted string counts. A block scalar would pass a
presence check while the validator, which reads one line per field, sees only
its indicator.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" block-scalar-argument-hint 2>&1
Codex skill inventory: * (glob)
::error::Skill 'plugins/release/skills/release/SKILL.md' must write argument-hint as a non-empty double-quoted string
::error::Skill 'plugins/release/skills/release/SKILL.md' has an ## Options section but no argument-hint; see the skill frontmatter section of docs/plugin-development.md
2 plugin validation error(s) found.
[1]
```

An `## Options` heading inside a fenced example is not the skill's own
section, so it demands no hint.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" fenced-options-heading 2>&1
Codex skill inventory: * (glob)
All plugin validations passed.
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
