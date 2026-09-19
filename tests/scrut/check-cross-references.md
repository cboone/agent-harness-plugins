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

## A declared composition is accepted

A workflow that invokes another skill declares it under `## Skill dependencies`,
and the declaration resolves to a canonical skill.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Skill dependencies' '' '- **Required:** `other`' '- **Optional:** None' '' '## Workflow' '' 'Invoke the `other` skill with `--no-push`.' > plugins/demo/skills/demo/SKILL.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

## An undeclared composition is reported

The name may carry the slash of the Claude Code command form.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Invoke the `/other` skill, then continue.' > plugins/demo/skills/demo/SKILL.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1
::error::plugins/demo/skills/demo/SKILL.md invokes the other skill, but plugins/demo/skills/demo/SKILL.md does not declare it under ## Skill dependencies
[1]
```

A composition in reference material belongs to the workflow that loads it, so it
is checked against the owning `SKILL.md`.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Invoke the `other` skill for each tracked item.' > plugins/demo/skills/demo/references/real.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/references/real.md 2>&1
::error::plugins/demo/skills/demo/references/real.md invokes the other skill, but plugins/demo/skills/demo/SKILL.md does not declare it under ## Skill dependencies
[1]
```

## A mention that is not composition needs no declaration

Suggestions to the user, redirects to an adjacent skill, and "Pairs with" text
are worded differently from composition on purpose.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Pairs with the `other` skill.' 'For a review, use the `other` skill instead.' 'Suggest next steps: run `/other`.' > plugins/demo/skills/demo/SKILL.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

## A selection-driven candidate is declared optional

A workflow that runs the skills a user picks from a list names each candidate
bare, which counts as using its declaration.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Skill dependencies' '' '- **Required:** None' '- **Optional:** `other`' '' '## Workflow' '' 'Invoke the skill for each selected item:' '' '- `other`' > plugins/demo/skills/demo/SKILL.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

## A declaration the workflow never uses is reported

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Skill dependencies' '' '- **Required:** None' '- **Optional:** `other`' '' '## Workflow' '' 'Nothing here names it.' > plugins/demo/skills/demo/SKILL.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1
::error::plugins/demo/skills/demo/SKILL.md declares the dependency other but never names it outside ## Skill dependencies
[1]
```

## A declaration that names no canonical skill is reported

The dependency block is the file's only candidate here, so this also checks
that the prefilter admits it.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Skill dependencies' '' '- **Required:** `absent`' '- **Optional:** None' > plugins/demo/skills/demo/SKILL.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1
::error::plugins/demo/skills/demo/SKILL.md declares the dependency absent, but no plugins/*/skills/absent/SKILL.md exists
::error::plugins/demo/skills/demo/SKILL.md declares the dependency absent but never names it outside ## Skill dependencies
[1]
```

## A repeated dependency is reported

A skill is required or optional, never both, and is listed once.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Skill dependencies' '' '- **Required:** `other`' '- **Optional:** `other`' '' '## Workflow' '' 'Invoke the `other` skill.' > plugins/demo/skills/demo/SKILL.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1
::error::plugins/demo/skills/demo/SKILL.md declares other as both required and optional
[1]
```

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Skill dependencies' '' '- **Required:** `other`, `other`' '- **Optional:** None' '' '## Workflow' '' 'Invoke the `other` skill.' > plugins/demo/skills/demo/SKILL.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1
::error::plugins/demo/skills/demo/SKILL.md declares other more than once in one ## Skill dependencies category
[1]
```

## A malformed declaration is reported

A name must be backticked.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Skill dependencies' '' '- **Required:** other' '- **Optional:** None' > plugins/demo/skills/demo/SKILL.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1
::error::plugins/demo/skills/demo/SKILL.md has a malformed ## Skill dependencies line '- **Required:** other'; write '- **Required:**' or '- **Optional:**' followed by None or backticked skill names separated by commas
[1]
```

An empty category is written `None`, not left out.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Skill dependencies' '' '- **Required:** `other`' '' '## Workflow' '' 'Invoke the `other` skill.' > plugins/demo/skills/demo/SKILL.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1
::error::plugins/demo/skills/demo/SKILL.md ## Skill dependencies has no '- **Optional:**' line; write None for an empty category
[1]
```

A skill declares its dependencies in one section, so a second is reported even
when both are well formed.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Skill dependencies' '' '- **Required:** `other`' '- **Optional:** None' '' '## Skill dependencies' '' '- **Required:** None' '- **Optional:** None' '' '## Workflow' '' 'Invoke the `other` skill.' > plugins/demo/skills/demo/SKILL.md \
> && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md 2>&1
::error::plugins/demo/skills/demo/SKILL.md has more than one ## Skill dependencies section
[1]
```

## The default scan discovers the files itself

Every case above names the file to check, but `bin/validate-plugins` passes no
arguments at all, so `find` decides what gets looked at. A discovery bug there
reports success having scanned nothing, which is the exact shape of failure this
check exists to catch, so the default path is exercised on its own.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Read `plugins/other/missing.md` first.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" 2>&1 | head -1
::error::plugins/demo/skills/demo/SKILL.md references plugins/other/missing.md but no such path exists in this repository
```

Reference material nested under a topic directory is reached too, which the
`write-*` skills and `set-up-linters` rely on.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && mkdir -p plugins/demo/skills/demo/references/tools && printf '%s\n' 'See `plugins/other/gone.md`.' > plugins/demo/skills/demo/references/tools/nested.md && "${CHECK_CROSS_REFERENCES_BIN}" 2>&1 | head -1
::error::plugins/demo/skills/demo/references/tools/nested.md references plugins/other/gone.md but no such path exists in this repository
```

## A findings run exits non-zero

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' 'Read `plugins/other/missing.md` first.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" > /dev/null 2>&1
[1]
```

## A run outside a plugin tree fails loudly

```scrut
$ cd "$(mktemp -d)" && "${CHECK_CROSS_REFERENCES_BIN}" 2>&1
check-cross-references: no plugins/ directory in /* (glob)
[2]
```
