# Skill cross-references

Tests for `bin/check-cross-references`, which resolves the paths and skill names
a skill body points at. Every testcase writes one skill body into the fixture
tree from `tests/fixtures/cross-reference-fixture` and checks that file alone.

## A path into this repository that does not resolve is reported

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Read `plugins/other/missing.md` first.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1 | head -1
::error::plugins/demo/skills/demo/SKILL.md references plugins/other/missing.md but no such path exists in this repository
```

## A path into this repository that resolves is accepted

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Read `plugins/other/README.md` first.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

## The regression from issue #356

`bootstrap-project` sent agents to a `commands/` directory that no longer
existed, naming a plugin that had been renamed. Both halves are reported.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '- `setup-ci` (read `plugins/setup-ci/commands/setup-ci.md`)' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1 | grep -c '^::error::'
1
```

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Invoke `/setup-ci` to configure CI.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1 | head -1
::error::plugins/demo/skills/demo/SKILL.md references the skill /setup-ci but plugins/setup-ci does not exist
```

## A stand-in is not a reference

`PLUGIN-NAME` and `<name>` name a plugin being written, not one that exists.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Create `plugins/PLUGIN-NAME/README.md` and `plugins/<name>/README.md`.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

## A sibling reference resolves against the skill directory

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'See `./references/real.md` and `./references/gone.md`.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1 | head -1
::error::plugins/demo/skills/demo/SKILL.md references ./references/gone.md but plugins/demo/skills/demo/references/gone.md does not exist
```

## A plugin-root reference resolves against the owning plugin

`scripts/` is left to rule 18 of `bin/validate-plugins`, which also checks the
executable bit, so only the rest of the subtree is resolved here.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Load ${CLAUDE_PLUGIN_ROOT}/references/gone.md at startup.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1 | head -1
::error::plugins/demo/skills/demo/SKILL.md references ${CLAUDE_PLUGIN_ROOT}/references/gone.md but plugins/demo/references/gone.md does not exist
```

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Run bash ${CLAUDE_PLUGIN_ROOT}/scripts/anything-at-all now.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

## An ambiguous prefix is checked only where the file declares its frame

Most `bin/` and `docs/` mentions name a file the skill creates in the project it
is run against, so they are skipped unless the file says otherwise.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Run `bin/nonexistent-tool` first.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '<!-- validate-plugins: repository-paths -->' 'Run `bin/real-tool`, then `bin/nonexistent-tool`.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1 | head -1
::error::plugins/demo/skills/demo/SKILL.md references bin/nonexistent-tool but no such path exists in this repository
```

A shebang is not a path into this repository, and does not become one when the
file declares its frame.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '<!-- validate-plugins: repository-paths -->' 'Start the script with `#!/usr/bin/env bash`.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

## An ignore entry exempts one reference

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '<!-- validate-plugins: ignore plugins/other/missing.md -->' 'Read `plugins/other/missing.md` first.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

An entry that matches nothing is itself reported, so an exemption cannot outlive
the reference it was written for and quietly hollow out the check.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '<!-- validate-plugins: ignore plugins/other/missing.md -->' 'Nothing references that path any more.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1 | head -1
::error::plugins/demo/skills/demo/SKILL.md ignores plugins/other/missing.md but no reference by that name was found; drop the stale ignore entry
```

## A skill name beside the word "skill" must name a plugin

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'The `setup-linters` skill runs after the `demo` skill.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1 | head -1
::error::plugins/demo/skills/demo/SKILL.md references the skill setup-linters but plugins/setup-linters does not exist
```

A bare backticked name is not a skill reference: nothing distinguishes
`set-up-ci` from `lean-toolchain` without reading the sentence around it.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Create `lean-toolchain` and `rustfmt.toml` in the project root.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

## A findings run exits non-zero

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Read `plugins/other/missing.md` first.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md > /dev/null 2>&1
[1]
```

## A run outside a plugin tree fails loudly

```scrut
$ cd "$(mktemp -d)" && "${CHECK_CROSS_REFERENCES_BIN}" 2>&1
check-cross-references: no plugins/ directory in /* (glob)
[2]
```
